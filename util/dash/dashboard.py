from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from ...task_data import queries
from ...util import db


load_dotenv()


# function to load data from all table
def load_data():

    conn = db.engine()
    query = queries.load_data_query
    df = pd.read_sql(query, conn)

    return df


""" 
Here, data cleaning should ideally be performed before starting the analysis. 
However, for this particular analysis, the related data entries appear to be in good condition.
In cases where handling missing values is necessary for time-sensitive analysis, 
I would drop rows with null values in the 'OTR_Points_Actual_Time' column to ensure the accuracy of the results.
"""


# helper function: calculate overall on-time rate
def cal_overall_ontime(df):

    status_counts = df['Status'].value_counts()
    on_time_count = status_counts.get('On Time', 0)
    total_tracked = df[df['Status'] != 'Untracked'].shape[0]
    on_time_rate = (on_time_count / total_tracked * 100) if total_tracked > 0 else 0

    return on_time_rate

# helper function: calculate total trips
def cal_total_trips(df):
    total_trips = df.groupby(['Trip_Start_Date', 'Trip_ID']).size().reset_index().shape[0]

    return total_trips

# helper function: calculate average delay
def cal_avg_delay(df):
    avg_delay = df[df['Status'] != 'Untracked']['Var_(Sec)'].mean()

    return avg_delay

# pre-calculated overall metrics
df = load_data()
overall_on_time = cal_overall_ontime(df)
total_trips = cal_total_trips(df)
avg_delay = cal_avg_delay(df)


"""
Below is the dashboard frontend layout
"""
# function to create dash app
def create_dash(flask_server):
    external_stylesheets = ["style.css", dbc.themes.FLATLY]
    dash_app = Dash(server= flask_server, name="Dashboard", url_base_pathname="/dash/", external_stylesheets=external_stylesheets)

    dash_app.layout = dbc.Container([
        dbc.Row([
            html.H1("Bus Operation Perfomance Metrics", className="text-center text-success mb-4")
        ], style={"margin-top":"60px", "text-color":"#303030"}),

        # Data Range Selector
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Select Date Range", className="card-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=df['Trip_Start_Date'].min(),
                            end_date=df['Trip_Start_Date'].max(),
                            display_format = "YYYY-MM-DD"
                        )
                    ])
                ])
            ], width=12, className="mb-4")
        ]),

        # Overall metric cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("On-Time Rate", className="card-title"),
                    html.H2(id="overall_on_time", className="text-success")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Average Delay (Min)", className="card-title"),
                    html.H2(id="avg_delay", className="delay-text")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Total Trips", className="card-title"),
                    html.H2(id="total_trips", className="text-success")
                ])
            ]), width=4),
        ], className="mb-4"),

        # Route Performance Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Route Performance Metrics"),
                    dbc.CardBody([
                        html.Div(id="route-perf-table")
                    ])
                ])
            ], width=12)
        ]),

        # store for processed data
        dcc.Store(id="processed-data")

    ], style={"background":"#EFF3EA", "margin-top":"60px"})

    @dash_app.callback(
    Output("processed-data", "data"),
    [Input("date-range", "start_date"),
     Input("date-range", "end_date")]
    )

    # helper function to update metric based on input
    def update_data(start_date, end_date):
        if start_date is None or end_date is None:
            return {}
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        #filter data based on input date range
        mask = (df["Trip_Start_Date"]>= start_date) & (df["Trip_Start_Date"]<= end_date)
        filter_df = df[mask].copy()

        # calculate the metrics
        metrics = {
            "on_time_rate": cal_overall_ontime(filter_df),
            "avg_delay": (cal_avg_delay(filter_df)/60),
            "total_trips": cal_total_trips(filter_df),

            #calculate route-level metrics
            "route_metrics":filter_df.groupby(["Route"]).apply(
                lambda x: {
                    "on_time_rate": cal_overall_ontime(x),
                    "avg_delay": (cal_avg_delay(x)/60),
                    "total_trip": cal_total_trips(x)
                }
            ).to_dict()
        }

        return metrics

    # Callback to update metric cards
    @dash_app.callback(
        [Output("overall_on_time", "children"),
         Output("avg_delay", "children"),
         Output("total_trips", "children")],
        [Input("processed-data", "data")]
    )
    def update_metrics(data):
        if not data:
            return "N/A", "N/A", "N/A"
        
        return (
            f"{data['on_time_rate']:.1f}%",
            f"{data['avg_delay']:.1f}",
            f"{data['total_trips']:,}"
        )


    # Callback to update route performance table
    @dash_app.callback(
        Output("route-perf-table", "children"),
        [Input("processed-data", "data")]
    )
    def update_route_table(data):
        if not data:
            return "No data available"
        
        # Create table data
        table_data = []
        for route_id, metrics in data['route_metrics'].items():
            table_data.append({
                'Route': route_id,
                'On-Time Rate': f"{metrics['on_time_rate']:.1f}%",
                'Avg Delay (min)': f"{metrics['avg_delay']:.1f}",
                'Total Trips': metrics['total_trip']
            })
        
        # Convert to DataFrame for easy table creation
        table_df = pd.DataFrame(table_data)
        
        return dbc.Table.from_dataframe(
            table_df,
            striped=True,
            bordered=True,
            hover=True,
            color="secondary",
            className="table-responsive"
        )

    return dash_app