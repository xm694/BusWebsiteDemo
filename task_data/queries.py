# query to search stop information by user input stop name
# (user this syntax for mariadb)
stop_query = """
    SELECT
        route,
        route_type,
        start_stop,
        mid_stop,
        end_stop,
        earliest_start_time,
        latest_start_time,
        operator
    FROM busRoute
    WHERE (
        REPLACE(LOWER(start_stop), ' ', '') LIKE CONCAT('%', :stop_name, '%')
        OR REPLACE(LOWER(mid_stop), ' ', '') LIKE CONCAT('%', :stop_name, '%')
        OR REPLACE(LOWER(end_stop), ' ', '') LIKE CONCAT('%', :stop_name, '%')
        )
"""

# query to combine all available data for dashboard development
load_data_query = """
    SELECT * FROM (
        SELECT * FROM PremierDemo.rd_otr_at_nominated_first_stop
        UNION ALL
        SELECT * FROM PremierDemo.rd_otr_at_mid_stop
        UNION ALL
        SELECT * FROM PremierDemo.rd_otr_at_nominated_end_stop
    ) total
"""

