from app.extensions import db

class TrekStaffAssignment(db.Model):
    __tablename__ = 'trek_staff_assignments'

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_role = db.Column(db.String(30), nullable=False)  # Guide, Medic
    assignment_status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Inactive
