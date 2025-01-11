import functools
from passlib.hash import pbkdf2_sha256
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from .db import engine

#create blueprint for authentication
au_bp = Blueprint('auth', __name__, url_prefix='/auth')

#initiate database
sqlengine = engine()

#create the login view for old user
@au_bp.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = sqlengine.connect()
        try: 
            user = db.execute(
                text('SELECT * FROM staff WHERE email = :email'), {"email":email}
            ).fetchone()

            print(" result is : ", user)
            if not user:
                error = 'Incorrect username.'
            else:
                user = dict(user._mapping) #convert result to dictionary
                if not pbkdf2_sha256.verify(password, user['password']):
                    # if not user['password'] == password:
                    error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('home'))
            
        except OperationalError as e:
                # Issues related to the database engine (e.g., timeout, unreachable server)
                error_message = "Internal error." 
        except SQLAlchemyError as e:
                # Catch all other SQLAlchemy errors
                error_message = "An error occurred while processing your request." 
        except Exception as e:
                # For catching any other exceptions that are not database-related
                error_message = "Credential is incorrect!" 

        
        #debug
        print(f"here is user info: {user}")
        # flash(error)

    return render_template('auth/login.html', error=error, error_message=error_message)

#function to keep user login info in session
@au_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        with sqlengine.connect() as db:
            result = db.execute(
                text('SELECT * FROM staff WHERE id = :user_id'), {"user_id":user_id}
            ).fetchone()
        g.user = dict(result._mapping) if result else None
        print("Logged in user: ",g.user)

#function to require authentication in other views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

#create user log out view
@au_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# # Create the register view for new user
# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = sqlengine.connect()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'

#         # toDo: need to fix the database connection code
#         if error is None:
#             try:
#                 db.execute(
#                     "INSERT INTO user (username, password) VALUES (?, ?)",
#                     (username, generate_password_hash(password)),
#                 )
#                 db.commit()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))

#         flash(error)

#     return render_template('auth/register.html')