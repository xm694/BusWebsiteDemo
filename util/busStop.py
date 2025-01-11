import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from .auth import login_required
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError


from .db import engine
from ..task_data import queries

#create blueprint for stop data manipulation
st_bp = Blueprint('stop', __name__, url_prefix='/stop')

#initiate database
sqlengine = engine()

# function to get stop information by user input
@st_bp.route('/', methods=('GET', 'POST'))
def search():
        stop_info=None
        error_message = None
        if request.method == 'GET':
            try:
                  stop = request.args.get('stop_name').strip().lower();
                  with sqlengine.connect() as db:
                        stop_info = db.execute(text(queries.stop_query),{"stop_name":stop}).fetchall()
            except OperationalError as e:
                  # Issues related to the database engine (e.g., timeout, unreachable server)
                  error_message = "Unable to connect to the database. Please try again later." + str(e)
            except SQLAlchemyError as e:
                  # Catch all other SQLAlchemy errors
                  error_message = "An error occurred while processing your request." + str(e)
            except Exception as e:
                  # For catching any other exceptions that are not database-related
                  error_message = "An unexpected error occurred. Please try again later." + str(e)

            return render_template('home.html', stop_info = stop_info, error_message=error_message)
        
        
