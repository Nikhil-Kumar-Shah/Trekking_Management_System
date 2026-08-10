from datetime import datetime
from app.extensions import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Statuses: Booked, Cancelled
    booking_status = db.Column(db.String(20), default='Booked', nullable=False)
    
    # Statuses: Pending, Paid
    payment_status = db.Column(db.String(20), default='Pending', nullable=False)
    
    checked_in = db.Column(db.Boolean, default=False, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)

    # Relationships
    attendance_records = db.relationship('TrekAttendance', backref='booking', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('TrekCertificate', backref='booking', lazy=True, cascade='all, delete-orphan')
