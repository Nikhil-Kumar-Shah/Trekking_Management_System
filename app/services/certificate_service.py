from datetime import datetime
from app.extensions import db
from app.models.certificate import TrekCertificate
from app.models.booking import Booking
from app.utils.helpers import generate_certificate_code

class CertificateService:
    @staticmethod
    def generate_certificate_for_booking(booking_id):
        """
        Generate a single certificate for a booking if the trek is completed
        and the participant was checked in.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found."
            
        # 1. Verify booking status is not cancelled
        if booking.booking_status != 'Booked':
            return False, "Cannot issue certificate for a cancelled booking."
            
        # 2. Verify trek status is completed
        if booking.trek.trek_status != 'Completed':
            return False, "Certificates are only issued for Completed treks."
            
        # 3. Verify attendance check-in status
        if not booking.checked_in:
            return False, "Trekker did not check-in/attend the trek."
            
        # 4. Prevent duplicate certificate generation
        existing_certificate = TrekCertificate.query.filter_by(booking_id=booking_id).first()
        if existing_certificate:
            return True, existing_certificate
            
        # Generate unique code
        certificate_number = generate_certificate_code(booking_id)
        
        # Relative link pointing to the certificate preview router
        certificate_url = f"/my-certificates/{certificate_number}/view"
        
        certificate = TrekCertificate(
            booking_id=booking_id,
            certificate_number=certificate_number,
            generated_at=datetime.utcnow(),
            certificate_url=certificate_url
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        return True, certificate

    @staticmethod
    def delete_certificates_for_trek(trek_id):
        """
        Delete all generated certificates for a trek if its status reverts from Completed.
        """
        booking_ids = [b.id for b in Booking.query.filter_by(trek_id=trek_id).all()]
        if booking_ids:
            TrekCertificate.query.filter(TrekCertificate.booking_id.in_(booking_ids)).delete(synchronize_session=False)
            db.session.commit()


    @staticmethod
    def bulk_generate_for_trek(trek_id):
        """
        Automatically run through all booked and checked-in attendees
        of a completed trek and issue certificates.
        """
        bookings = Booking.query.filter_by(
            trek_id=trek_id, 
            booking_status='Booked', 
            checked_in=True
        ).all()
        
        generated_count = 0
        
        for booking in bookings:
            success, _ = CertificateService.generate_certificate_for_booking(booking.id)
            if success:
                generated_count += 1
                
        return generated_count
