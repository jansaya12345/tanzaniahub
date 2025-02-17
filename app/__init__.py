from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['WTF_CSRF_ENABLED'] = False  # 🚨 TEMPORARY for testing

# Database
db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 🟡 FIXED: Load User for Flask-Login
from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after app setup
from app import routes
