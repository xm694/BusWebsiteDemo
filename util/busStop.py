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
        if request.method == 'GET':
            stop = request.args.get('stop_name').strip().lower();
            with sqlengine.connect() as db:
                  stop_info = db.execute(text(queries.stop_query),{"stop_name":stop}).fetchall()

            return render_template('home.html', stop_info = stop_info)
        
        
# # function to generate analysis report
# @st_bp.route('/report', methods=('GET', 'POST'))
# def generate_report():
#       return "Here is report!"
