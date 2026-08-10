from datetime import datetime
from app.extensions import db

class TrekCertificate(db.Model):
    __tablename__ = 'trek_certificates'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    certificate_url = db.Column(db.String(250), nullable=True)  # Store generated HTML view or static PDF path
