from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.trek import Trek
from app.models.booking import Booking
from app.models.assignment import TrekStaffAssignment
from app.models.status_log import TrekStatusLog
from app.models.certificate import TrekCertificate
from app.utils.decorators import role_required
from app.routes.forms import TrekForm, StaffForm, AssignmentForm
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Calculate statistics for the dashboard
    total_treks = Trek.query.count()
    open_treks = Trek.query.filter_by(trek_status='Open').count()
    total_bookings = Booking.query.filter_by(booking_status='Booked').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_users = User.query.filter_by(role='user').count()
    
    # Retrieve recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_treks=total_treks,
        open_treks=open_treks,
        total_bookings=total_bookings,
        total_staff=total_staff,
        total_users=total_users,
        recent_bookings=recent_bookings
    )

@admin_bp.route('/treks')
@login_required
@role_required('admin')
def list_treks():
    treks = Trek.query.order_by(Trek.start_date.desc()).all()
    return render_template('admin/treks.html', treks=treks)

@admin_bp.route('/treks/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_trek():
    form = TrekForm()
    # Remove trek_status field during creation, default to Open
    if 'trek_status' in form:
        del form.trek_status
        
    if form.validate_on_submit():
        new_trek = Trek(
            title=form.title.data,
            location=form.location.data,
            altitude=form.altitude.data,
            difficulty_level=form.difficulty_level.data,
            duration_days=form.duration_days.data,
            description=form.description.data,
            max_slots=form.max_slots.data,
            available_slots=form.max_slots.data,  # Matches max slots initially
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            meeting_point=form.meeting_point.data,
            trek_status='Open',
            created_by=current_user.id
        )
        
        db.session.add(new_trek)
        db.session.flush()  # Extract the trek ID for logging
        
        # Log initial trek state
        log = TrekStatusLog(
            trek_id=new_trek.id,
            old_status=None,
            new_status='Open',
            changed_by=current_user.id,
            reason="Initial trek creation."
        )
        db.session.add(log)
        db.session.commit()
        
        flash("Trek created successfully!", "success")
        return redirect(url_for('admin.list_treks'))
        
    return render_template('admin/create_trek.html', form=form)

@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    form = TrekForm(obj=trek)
    
    if form.validate_on_submit():
        # Count current bookings to prevent setting max_slots below active bookings
        active_bookings_count = Booking.query.filter_by(
            trek_id=trek.id, 
            booking_status='Booked'
        ).count()
        
        if form.max_slots.data < active_bookings_count:
            flash(f"Cannot reduce capacity below {active_bookings_count} (existing active bookings).", "danger")
            return render_template('admin/edit_trek.html', form=form, trek=trek)
            
        old_status = trek.trek_status
        new_status = form.trek_status.data
        
        # Check if status is transitioning
        if old_status != new_status:
            status_log = TrekStatusLog(
                trek_id=trek.id,
                old_status=old_status,
                new_status=new_status,
                changed_by=current_user.id,
                reason=f"Admin updated trek properties and status."
            )
            db.session.add(status_log)
            
            # If changed to Completed, automatically trigger certificate generation
            if new_status == 'Completed':
                from app.services.certificate_service import CertificateService
                issued = CertificateService.bulk_generate_for_trek(trek.id)
                flash(f"Trek completed! Generated {issued} certificates for attendees.", "info")
            elif old_status == 'Completed':
                from app.services.certificate_service import CertificateService
                CertificateService.delete_certificates_for_trek(trek.id)
                flash("Trek status reverted from Completed. Associated certificates have been revoked.", "warning")
        
        # Update trek details
        trek.title = form.title.data
        trek.location = form.location.data
        trek.altitude = form.altitude.data
        trek.difficulty_level = form.difficulty_level.data
        trek.duration_days = form.duration_days.data
        trek.description = form.description.data
        
        # Re-calculate available slots
        trek.max_slots = form.max_slots.data
        trek.available_slots = trek.max_slots - active_bookings_count
        
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data
        trek.meeting_point = form.meeting_point.data
        trek.trek_status = new_status
        
        db.session.commit()
        flash("Trek details updated successfully!", "success")
        return redirect(url_for('admin.list_treks'))
        
    return render_template('admin/edit_trek.html', form=form, trek=trek)

@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    
    # Check if trek has active bookings
    active_bookings = Booking.query.filter_by(trek_id=trek.id, booking_status='Booked').first()
    if active_bookings:
        flash("Cannot delete trek with active bookings. Cancel the bookings first.", "danger")
        return redirect(url_for('admin.list_treks'))
        
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted successfully.", "success")
    return redirect(url_for('admin.list_treks'))

@admin_bp.route('/staff')
@login_required
@role_required('admin')
def list_staff():
    staff_members = User.query.filter_by(role='staff').all()
    # Build a lookup of assignments per staff
    assignments = {}
    for staff in staff_members:
        assignments[staff.id] = TrekStaffAssignment.query.filter_by(staff_id=staff.id, assignment_status='Active').all()
    return render_template('admin/staff.html', staff_members=staff_members, assignments=assignments)

@admin_bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_staff():
    form = StaffForm()
    if form.validate_on_submit():
        # Prevent duplicate emails
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email address is already registered.", "danger")
            return render_template('admin/create_staff.html', form=form)
            
        new_staff = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            role='staff',
            is_active=True
        )
        new_staff.set_password(form.password.data)
        
        db.session.add(new_staff)
        db.session.commit()
        
        flash(f"Staff account for {new_staff.full_name} created successfully!", "success")
        return redirect(url_for('admin.list_staff'))
        
    return render_template('admin/create_staff.html', form=form)

@admin_bp.route('/staff/<int:staff_id>/assign', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def assign_staff(staff_id):
    staff_member = User.query.filter_by(id=staff_id, role='staff').first_or_404()
    
    # Retrieve all treks to present in the dropdown
    treks = Trek.query.order_by(Trek.start_date.desc()).all()
    
    form = AssignmentForm()
    # Override select choice dynamically
    form.staff_id.choices = [(staff_member.id, staff_member.full_name)]
    
    # Fetch active assignments for this staff
    active_assignments = TrekStaffAssignment.query.filter_by(
        staff_id=staff_member.id, 
        assignment_status='Active'
    ).all()
    
    if form.validate_on_submit():
        trek_id = int(request.form.get('trek_id'))
        
        # Check if already assigned to this trek
        existing = TrekStaffAssignment.query.filter_by(
            trek_id=trek_id, 
            staff_id=staff_member.id, 
            assignment_status='Active'
        ).first()
        
        if existing:
            flash("Staff is already assigned to this trek.", "warning")
        else:
            assignment = TrekStaffAssignment(
                trek_id=trek_id,
                staff_id=staff_member.id,
                assigned_role=form.assigned_role.data,
                assignment_status='Active'
            )
            db.session.add(assignment)
            db.session.commit()
            flash("Staff successfully assigned to trek.", "success")
            return redirect(url_for('admin.list_staff'))
            
    return render_template(
        'admin/assign_staff.html', 
        form=form, 
        staff=staff_member, 
        treks=treks,
        assignments=active_assignments
    )

@admin_bp.route('/staff/assignments/<int:assignment_id>/remove', methods=['POST'])
@login_required
@role_required('admin')
def remove_assignment(assignment_id):
    assignment = TrekStaffAssignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash("Staff assignment removed.", "info")
    return redirect(url_for('admin.list_staff'))

@admin_bp.route('/users')
@login_required
@role_required('admin')
def list_users():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
@login_required
@role_required('admin')
def toggle_blacklist(user_id):
    user = User.query.get_or_404(user_id)
    
    # Toggle blacklisted flag
    if user.is_blacklisted:
        user.is_blacklisted = False
        flash(f"User {user.full_name} has been unblacklisted.", "success")
    else:
        user.is_blacklisted = True
        # If user is blacklisted, cancel all their active bookings
        bookings = Booking.query.filter_by(user_id=user.id, booking_status='Booked').all()
        for booking in bookings:
            booking.booking_status = 'Cancelled'
            booking.checked_in = False
            # Revoke certificates and remove attendance logs if any
            from app.models.certificate import TrekCertificate
            from app.models.attendance import TrekAttendance
            TrekCertificate.query.filter_by(booking_id=booking.id).delete()
            TrekAttendance.query.filter_by(booking_id=booking.id).delete()
            # Give slot back
            trek = Trek.query.get(booking.trek_id)
            if trek:
                trek.available_slots += 1
                
        flash(f"User {user.full_name} has been blacklisted and their bookings were cancelled.", "warning")
        
    db.session.commit()
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/bookings')
@login_required
@role_required('admin')
def list_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/bookings/<int:booking_id>/toggle-payment', methods=['POST'])
@login_required
@role_required('admin')
def toggle_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.payment_status == 'Paid':
        booking.payment_status = 'Pending'
    else:
        booking.payment_status = 'Paid'
        
    # Notify trekker of the payment status update
    from app.models.notification import Notification
    from datetime import datetime
    title = "Payment Status Updated"
    if booking.payment_status == 'Paid':
        message = f"Your registration payment for the expedition '{booking.trek.title}' has been verified as PAID. Thank you!"
    else:
        message = f"Your registration payment for the expedition '{booking.trek.title}' is now marked as PENDING."
        
    notification = Notification(
        user_id=booking.user_id,
        title=title,
        message=message,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.session.add(notification)
        
    db.session.commit()
    flash(f"Booking #{booking.id} payment status updated to {booking.payment_status}.", "success")
    return redirect(url_for('admin.list_bookings'))

@admin_bp.route('/reports')
@login_required
@role_required('admin')
def view_reports():
    active_tab = request.args.get('tab', 'logs')
    if active_tab not in ['logs', 'certs', 'completed']:
        active_tab = 'logs'
    # Reports summary: finished treks, certificates generated, and status change logs
    completed_treks = Trek.query.filter_by(trek_status='Completed').all()
    certificates = TrekCertificate.query.order_by(TrekCertificate.generated_at.desc()).all()
    logs = TrekStatusLog.query.order_by(TrekStatusLog.changed_at.desc()).all()
    
    return render_template(
        'admin/reports.html', 
        completed_treks=completed_treks, 
        certificates=certificates, 
        logs=logs,
        active_tab=active_tab
    )
