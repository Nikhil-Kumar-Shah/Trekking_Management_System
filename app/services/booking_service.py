from datetime import datetime
from app.extensions import db
from app.models.booking import Booking
from app.models.trek import Trek
from app.models.user import User
from app.models.notification import Notification

class BookingService:
    @staticmethod
    def create_booking(user_id, trek_id, special_requests=None):
        """
        Creates a trek booking for a user after checking all business rules:
        1. User must not be blacklisted.
        2. Trek status must be 'Open'.
        3. Trek must have available slots.
        4. User must not have an active booking for this trek.
        """
        # Fetch user
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."
            
        # 1. Verify user is not blacklisted
        if user.is_blacklisted:
            return False, "Your account has been blacklisted. Booking is not permitted."
            
        # Fetch trek
        trek = Trek.query.get(trek_id)
        if not trek:
            return False, "Trek not found."
            
        # 2. Verify trek status is Open
        if trek.trek_status != 'Open':
            return False, f"Trek booking is closed. Current status: {trek.trek_status}."
            
        # 3. Verify available slots
        if trek.available_slots <= 0:
            return False, "No slots available for this trek."
            
        # 4. Check for existing active booking
        existing_booking = Booking.query.filter_by(
            user_id=user_id,
            trek_id=trek_id,
            booking_status='Booked'
        ).first()
        
        if existing_booking:
            return False, "You have already booked this trek."
            
        # Build booking instance
        booking = Booking(
            user_id=user_id,
            trek_id=trek_id,
            booking_status='Booked',
            payment_status='Pending',
            checked_in=False,
            special_requests=special_requests
        )
        
        # Add booking and decrement slots
        db.session.add(booking)
        trek.available_slots -= 1
        
        # Flush to get the booking id
        db.session.flush()
        
        # Create a notification for the user
        notification = Notification(
            user_id=user_id,
            title="Trek Booked Successfully",
            message=f"Your booking for '{trek.title}' has been recorded. Please complete payment if necessary.",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        
        # Commit transaction
        db.session.commit()
        
        return True, booking

    @staticmethod
    def cancel_booking(booking_id, changed_by_user):
        """
        Cancels a booking, updates available slots, and logs notification.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found."
            
        if booking.booking_status == 'Cancelled':
            return False, "Booking is already cancelled."
            
        # Prevent cancellation if the trek is already In Progress, Completed, or Cancelled
        if booking.trek.trek_status in ['In Progress', 'Completed', 'Cancelled']:
            return False, f"Cannot cancel booking because the trek is already {booking.trek.trek_status.lower()}."
            
        # Reset booking status
        booking.booking_status = 'Cancelled'
        booking.checked_in = False
        
        # Revoke certificates and remove attendance logs if any
        from app.models.certificate import TrekCertificate
        from app.models.attendance import TrekAttendance
        TrekCertificate.query.filter_by(booking_id=booking.id).delete()
        TrekAttendance.query.filter_by(booking_id=booking.id).delete()
        
        # Return slot back to the trek
        trek = Trek.query.get(booking.trek_id)
        if trek:
            trek.available_slots += 1
            
        # Create notification for cancellation
        notification = Notification(
            user_id=booking.user_id,
            title="Trek Booking Cancelled",
            message=f"Your booking for '{trek.title}' has been cancelled by {changed_by_user.full_name}.",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        
        db.session.commit()
        return True, "Booking cancelled successfully."
