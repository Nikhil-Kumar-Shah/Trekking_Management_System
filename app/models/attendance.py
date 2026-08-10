from datetime import datetime
from app.extensions import db

class TrekAttendance(db.Model):
    __tablename__ = 'trek_attendance'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    attendance_status = db.Column(db.String(20), default='Present', nullable=False)  # Present, Absent
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    marked_by_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    @property
    def staff_member(self):
        from app.models.user import User
        return User.query.get(self.marked_by_staff_id)
