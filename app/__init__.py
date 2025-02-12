from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'ffd26404c1d6e76efae9130b6f2ddcfb'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Fix user_loader placement AFTER importing models
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import User inside the function to prevent circular imports
    return User.query.get(int(user_id))
