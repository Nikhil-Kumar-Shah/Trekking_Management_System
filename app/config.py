import os

class Config:
    # Secret key for sessions and WTForms CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trekking-secret-key-for-college-viva'
    
    # Resolve the base directory of the project
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Store SQLite database in the project root for easy access
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'trekking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for trek certificates or user profile images
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    
    # Allow maximum file upload of 16 Megabytes
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
