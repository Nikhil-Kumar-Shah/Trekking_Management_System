from datetime import datetime
from app.extensions import db

class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    altitude = db.Column(db.Integer, nullable=False)  # in meters
    difficulty_level = db.Column(db.String(20), nullable=False)  # Easy, Moderate, Hard
    duration_days = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    max_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    meeting_point = db.Column(db.String(150), nullable=False)
    
    # Statuses: Open, Closed, In Progress, Completed, Cancelled
    trek_status = db.Column(db.String(30), default='Open', nullable=False)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade='all, delete-orphan')
    staff_assignments = db.relationship('TrekStaffAssignment', backref='trek', lazy=True, cascade='all, delete-orphan')
    status_logs = db.relationship('TrekStatusLog', backref='trek', lazy=True, cascade='all, delete-orphan')

    # Simple property to retrieve creator details
    @property
    def creator(self):
        from app.models.user import User
        return User.query.get(self.created_by)
