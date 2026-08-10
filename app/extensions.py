from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Instantiate SQLAlchemy ORM
db = SQLAlchemy()

# Instantiate LoginManager for session-based user authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
