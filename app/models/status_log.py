from datetime import datetime
from app.extensions import db

class TrekStatusLog(db.Model):
    __tablename__ = 'trek_status_logs'

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    old_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.Text, nullable=True)

    @property
    def editor(self):
        from app.models.user import User
        return User.query.get(self.changed_by)
