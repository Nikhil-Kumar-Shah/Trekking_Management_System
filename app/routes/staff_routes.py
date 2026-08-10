from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.trek import Trek
from app.models.booking import Booking
from app.models.assignment import TrekStaffAssignment
from app.models.status_log import TrekStatusLog
from app.services.attendance_service import AttendanceService
from app.services.certificate_service import CertificateService
from app.utils.decorators import role_required
from app.routes.forms import AttendanceForm, TrekStatusForm, TrekSlotsForm

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

def verify_staff_assignment(trek_id):
    """
    Business rule check: Staff can only manage treks they are assigned to.
    """
    assignment = TrekStaffAssignment.query.filter_by(
        trek_id=trek_id,
        staff_id=current_user.id,
        assignment_status='Active'
    ).first()
    
    if not assignment:
        # Prevent access to unassigned treks
        abort(403)

@staff_bp.route('/dashboard')
@login_required
@role_required('staff')
def dashboard():
    # Fetch active assignments for the current staff member
    assignments = TrekStaffAssignment.query.filter_by(
        staff_id=current_user.id,
        assignment_status='Active'
    ).all()
    
    assigned_trek_ids = [a.trek_id for a in assignments]
    
    total_assigned_count = len(assigned_trek_ids)
    in_progress_count = Trek.query.filter(Trek.id.in_(assigned_trek_ids), Trek.trek_status == 'In Progress').count() if assigned_trek_ids else 0
    open_treks_count = Trek.query.filter(Trek.id.in_(assigned_trek_ids), Trek.trek_status == 'Open').count() if assigned_trek_ids else 0
    completed_treks_count = Trek.query.filter(Trek.id.in_(assigned_trek_ids), Trek.trek_status == 'Completed').count() if assigned_trek_ids else 0
    
    total_participants = Booking.query.filter(Booking.trek_id.in_(assigned_trek_ids), Booking.booking_status == 'Booked').count() if assigned_trek_ids else 0
    checked_in_participants = Booking.query.filter(Booking.trek_id.in_(assigned_trek_ids), Booking.booking_status == 'Booked', Booking.checked_in == True).count() if assigned_trek_ids else 0
    
    recent_bookings = Booking.query.filter(Booking.trek_id.in_(assigned_trek_ids)).order_by(Booking.booking_date.desc()).limit(5).all() if assigned_trek_ids else []
    
    assigned_treks = [a.trek for a in assignments]
    
    return render_template(
        'staff/dashboard.html',
        treks=assigned_treks,
        total_assigned_count=total_assigned_count,
        in_progress_count=in_progress_count,
        open_treks_count=open_treks_count,
        completed_treks_count=completed_treks_count,
        total_participants=total_participants,
        checked_in_participants=checked_in_participants,
        recent_bookings=recent_bookings
    )

@staff_bp.route('/treks')
@login_required
@role_required('staff')
def list_treks():
    assignments = TrekStaffAssignment.query.filter_by(
        staff_id=current_user.id,
        assignment_status='Active'
    ).all()
    
    assigned_treks = []
    for assignment in assignments:
        assigned_treks.append(assignment.trek)
        
    return render_template('staff/treks.html', treks=assigned_treks)

@staff_bp.route('/treks/<int:trek_id>/participants')
@login_required
@role_required('staff')
def list_participants(trek_id):
    # Verify assignment first
    verify_staff_assignment(trek_id)
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Retrieve all active bookings for this trek
    bookings = Booking.query.filter_by(
        trek_id=trek.id, 
        booking_status='Booked'
    ).all()
    
    return render_template('staff/participants.html', trek=trek, bookings=bookings)

@staff_bp.route('/treks/<int:trek_id>/attendance/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def mark_attendance(trek_id, booking_id):
    # Verify assignment
    verify_staff_assignment(trek_id)
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.trek_id != trek_id:
        abort(400)  # Bad Request if booking doesn't match trek
        
    # Fetch existing attendance if any
    from app.models.attendance import TrekAttendance
    attendance = TrekAttendance.query.filter_by(booking_id=booking_id).first()
    
    form = AttendanceForm(obj=attendance)
    
    if form.validate_on_submit():
        success, result = AttendanceService.mark_attendance(
            booking_id=booking.id,
            staff_id=current_user.id,
            attendance_status=form.attendance_status.data,
            notes=form.notes.data
        )
        
        if success:
            flash(f"Attendance for {booking.trekker.full_name} marked as {form.attendance_status.data}.", "success")
            return redirect(url_for('staff.list_participants', trek_id=trek_id))
        else:
            flash(f"Error marking attendance: {result}", "danger")
            
    return render_template('staff/attendance.html', form=form, booking=booking)

@staff_bp.route('/treks/<int:trek_id>/update-status', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def update_status(trek_id):
    # Verify assignment
    verify_staff_assignment(trek_id)
    
    trek = Trek.query.get_or_404(trek_id)
    form = TrekStatusForm(obj=trek)
    
    if form.validate_on_submit():
        old_status = trek.trek_status
        new_status = form.trek_status.data
        
        if old_status == new_status:
            flash("The selected status is already active.", "info")
            return redirect(url_for('staff.list_treks'))
            
        # Update trek status
        trek.trek_status = new_status
        
        # Log status change in status logs
        log = TrekStatusLog(
            trek_id=trek.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=current_user.id,
            reason=form.reason.data
        )
        db.session.add(log)
        
        # If status changed to Completed, automatically trigger certificate generation
        if new_status == 'Completed':
            issued_count = CertificateService.bulk_generate_for_trek(trek.id)
            flash(f"Trek status set to Completed. Generated {issued_count} certificates for attendees.", "success")
        elif old_status == 'Completed':
            CertificateService.delete_certificates_for_trek(trek.id)
            flash("Trek status reverted from Completed. Associated certificates have been revoked.", "warning")
        else:
            flash(f"Trek status updated to {new_status}.", "success")
            
        # Notify all active trekkers of the status update
        from app.models.notification import Notification
        from datetime import datetime
        active_bookings = Booking.query.filter_by(trek_id=trek.id, booking_status='Booked').all()
        for b in active_bookings:
            title = f"Trek Expedition {new_status}"
            if new_status == 'In Progress':
                message = f"Your trek expedition '{trek.title}' is now IN PROGRESS! Follow safety instructions from your crew details."
            elif new_status == 'Completed':
                message = f"Congratulations! Your trek expedition '{trek.title}' has been marked as Completed. Your certificate has been issued."
            elif new_status == 'Cancelled':
                message = f"Notice: The trek expedition '{trek.title}' has been cancelled by the operation staff."
            else:
                message = f"The status of your trek expedition '{trek.title}' has been updated to: {new_status}."
                
            notification = Notification(
                user_id=b.user_id,
                title=title,
                message=message,
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
        db.session.commit()
        return redirect(url_for('staff.list_treks'))
        
    return render_template('staff/update_status.html', form=form, trek=trek)

@staff_bp.route('/treks/<int:trek_id>/update-slots', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def update_slots(trek_id):
    # Verify assignment
    verify_staff_assignment(trek_id)
    
    trek = Trek.query.get_or_404(trek_id)
    form = TrekSlotsForm(obj=trek)
    
    if form.validate_on_submit():
        new_available = form.available_slots.data
        
        # Validate that available slots do not exceed maximum capacity
        if new_available > trek.max_slots:
            flash(f"Available slots cannot exceed the maximum trek capacity ({trek.max_slots}).", "danger")
            return render_template('staff/update_slots.html', form=form, trek=trek)
            
        trek.available_slots = new_available
        db.session.commit()
        
        flash("Trek available slots updated successfully.", "success")
        return redirect(url_for('staff.list_treks'))
        
    return render_template('staff/update_slots.html', form=form, trek=trek)
