from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # roles: admin, staff, user
    
    # Emergency & Medical details
    blood_group = db.Column(db.String(5), nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    
    profile_image = db.Column(db.String(200), nullable=True)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='trekker', lazy=True, cascade='all, delete-orphan')
    staff_assignments = db.relationship('TrekStaffAssignment', backref='staff', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        # Generate secure hash from the password text
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Verify the entered password against stored password hash
        return check_password_hash(self.password_hash, password)

    # Override Flask-Login active state based on both activation and blacklist status
    @property
    def is_active_user(self):
        if self.is_active:
            if not self.is_blacklisted:
                return True
        return False
