from datetime import datetime
from app.extensions import db
from app.models.attendance import TrekAttendance
from app.models.booking import Booking
from app.models.notification import Notification

class AttendanceService:
    @staticmethod
    def mark_attendance(booking_id, staff_id, attendance_status, notes=None):
        """
        Record or update attendance for a specific booking.
        Checks if booking is active, updates booking check_in status, and logs markings.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking record not found."
            
        # Ensure booking is not cancelled
        if booking.booking_status != 'Booked':
            return False, "Cannot record attendance for a cancelled booking."
            
        # Query for existing attendance log
        attendance_record = TrekAttendance.query.filter_by(booking_id=booking_id).first()
        
        if not attendance_record:
            # Insert new attendance log
            attendance_record = TrekAttendance(
                booking_id=booking_id,
                attendance_status=attendance_status,
                check_in_time=datetime.utcnow(),
                marked_by_staff_id=staff_id,
                notes=notes
            )
            db.session.add(attendance_record)
        else:
            # Modify existing attendance log
            attendance_record.attendance_status = attendance_status
            attendance_record.check_in_time = datetime.utcnow()
            attendance_record.marked_by_staff_id = staff_id
            attendance_record.notes = notes
            
        # Synchronize checked_in flag on the booking table
        if attendance_status == 'Present':
            booking.checked_in = True
            title = "Trek Attendance Verified"
            message = f"Your attendance for the expedition '{booking.trek.title}' has been marked as PRESENT. You are checked in!"
        else:
            booking.checked_in = False
            title = "Trek Attendance Updated"
            message = f"Your attendance for the expedition '{booking.trek.title}' has been marked as {attendance_status}."
            
        # Log real-time notification
        notification = Notification(
            user_id=booking.user_id,
            title=title,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
            
        db.session.commit()
        return True, attendance_record
