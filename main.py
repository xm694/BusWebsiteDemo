import os
from flask import Flask, request, render_template
from flask_cors import CORS

from .util.dash import dashboard
from .util import auth, busStop

# flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','dev')
CORS(app)
dashboard.create_dash(app)
app.debug=True

# register blueprints
app.register_blueprint(auth.au_bp)
app.register_blueprint(busStop.st_bp)

# Routers for website 
@app.route("/")
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)