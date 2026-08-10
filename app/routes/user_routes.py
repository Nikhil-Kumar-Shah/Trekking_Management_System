from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.trek import Trek
from app.models.booking import Booking
from app.models.assignment import TrekStaffAssignment
from app.models.notification import Notification
from app.models.certificate import TrekCertificate
from app.services.booking_service import BookingService
from app.utils.decorators import role_required
from app.routes.forms import BookingForm
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
@role_required('user')
def dashboard():
    # Fetch recent unread notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Retrieve upcoming active bookings
    bookings = Booking.query.filter_by(
        user_id=current_user.id, 
        booking_status='Booked'
    ).all()
    
    # Filter bookings that are yet to start
    upcoming_bookings = []
    for booking in bookings:
        if booking.trek.start_date >= datetime.utcnow().date():
            upcoming_bookings.append(booking)
            
    return render_template(
        'user/dashboard.html', 
        notifications=notifications, 
        upcoming_bookings=upcoming_bookings
    )

@user_bp.route('/treks')
@login_required
@role_required('user')
def list_treks():
    # Base query filters treks that are Open for bookings
    query = Trek.query.filter_by(trek_status='Open')
    
    # Apply search filter
    search_q = request.args.get('q', '').strip()
    if search_q:
        query = query.filter(
            (Trek.title.ilike(f"%{search_q}%")) | 
            (Trek.location.ilike(f"%{search_q}%"))
        )
        
    # Apply difficulty filter
    difficulty = request.args.get('difficulty', '').strip()
    if difficulty:
        query = query.filter(Trek.difficulty_level == difficulty)
        
    treks = query.order_by(Trek.start_date.asc()).all()
    
    # Get all booking trek IDs for current user to show checkmark/disabled book state
    booked_trek_ids = {b.trek_id for b in Booking.query.filter_by(
        user_id=current_user.id,
        booking_status='Booked'
    ).all()}
    
    return render_template(
        'user/treks.html', 
        treks=treks, 
        search_q=search_q, 
        difficulty=difficulty,
        booked_trek_ids=booked_trek_ids
    )

@user_bp.route('/treks/<int:trek_id>')
@login_required
@role_required('user')
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    
    # Get staff assigned to this trek
    assignments = TrekStaffAssignment.query.filter_by(
        trek_id=trek.id, 
        assignment_status='Active'
    ).all()
    
    # Check if this user has already booked the trek
    already_booked = Booking.query.filter_by(
        user_id=current_user.id, 
        trek_id=trek.id, 
        booking_status='Booked'
    ).first()
    
    return render_template(
        'user/trek_detail.html', 
        trek=trek, 
        assignments=assignments,
        already_booked=already_booked
    )

@user_bp.route('/treks/<int:trek_id>/book', methods=['GET', 'POST'])
@login_required
@role_required('user')
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    
    # Business rule: Reject bookings for treks that are not Open
    if trek.trek_status != 'Open':
        flash("This trek is not open for bookings.", "danger")
        return redirect(url_for('user.trek_detail', trek_id=trek_id))
        
    # Business rule: Check slot availability
    if trek.available_slots <= 0:
        flash("This trek is fully booked.", "danger")
        return redirect(url_for('user.trek_detail', trek_id=trek_id))
        
    # Check if already booked
    existing = Booking.query.filter_by(
        user_id=current_user.id, 
        trek_id=trek.id, 
        booking_status='Booked'
    ).first()
    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for('user.my_bookings'))
        
    # Load and pre-fill form from user profile details
    form = BookingForm(
        blood_group=current_user.blood_group,
        medical_conditions=current_user.medical_conditions,
        emergency_contact_name=current_user.emergency_contact_name,
        emergency_contact_phone=current_user.emergency_contact_phone
    )
    
    if form.validate_on_submit():
        # Update emergency info in profile if not already set
        if not current_user.blood_group:
            current_user.blood_group = form.blood_group.data
        if not current_user.medical_conditions:
            current_user.medical_conditions = form.medical_conditions.data
        if not current_user.emergency_contact_name:
            current_user.emergency_contact_name = form.emergency_contact_name.data
        if not current_user.emergency_contact_phone:
            current_user.emergency_contact_phone = form.emergency_contact_phone.data
            
        # Create booking using the service layer
        success, result = BookingService.create_booking(
            user_id=current_user.id,
            trek_id=trek.id,
            special_requests=form.special_requests.data
        )
        
        if success:
            flash("Booking confirmed successfully!", "success")
            return redirect(url_for('user.my_bookings'))
        else:
            flash(f"Booking failed: {result}", "danger")
            
    return render_template('user/book.html', form=form, trek=trek)

@user_bp.route('/my-bookings')
@login_required
@role_required('user')
def my_bookings():
    # Retrieve all active bookings for this user
    bookings = Booking.query.filter_by(
        user_id=current_user.id, 
        booking_status='Booked'
    ).order_by(Booking.booking_date.desc()).all()
    
    return render_template('user/bookings.html', bookings=bookings)

@user_bp.route('/my-bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required('user')
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Security check: verify this booking belongs to current user
    if booking.user_id != current_user.id:
        abort(403)
        
    success, message = BookingService.cancel_booking(booking.id, current_user)
    
    if success:
        flash("Your booking has been cancelled successfully.", "success")
    else:
        flash(message, "danger")
        
    return redirect(url_for('user.my_bookings'))

@user_bp.route('/my-history')
@login_required
@role_required('user')
def my_history():
    # Historical bookings: completed treks or cancelled bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    historical_bookings = []
    for booking in bookings:
        # Include cancelled bookings or bookings of completed treks
        if booking.booking_status == 'Cancelled':
            historical_bookings.append(booking)
        elif booking.trek.trek_status == 'Completed':
            historical_bookings.append(booking)
            
    return render_template('user/history.html', bookings=historical_bookings)

@user_bp.route('/my-certificates')
@login_required
@role_required('user')
def my_certificates():
    # Retrieve certificates for user's checked-in bookings
    bookings = Booking.query.filter_by(
        user_id=current_user.id, 
        booking_status='Booked', 
        checked_in=True
    ).all()
    
    certificates = []
    for booking in bookings:
        if booking.trek.trek_status == 'Completed':
            cert = TrekCertificate.query.filter_by(booking_id=booking.id).first()
            if cert:
                certificates.append(cert)
            
    return render_template('user/certificates.html', certificates=certificates)

@user_bp.route('/my-certificates/<string:certificate_number>/view')
@login_required
@role_required('user')
def view_certificate(certificate_number):
    certificate = TrekCertificate.query.filter_by(
        certificate_number=certificate_number
    ).first_or_404()
    
    booking = certificate.booking
    
    # Security check: verify the certificate belongs to the current user
    if booking.user_id != current_user.id:
        abort(403)
        
    return render_template('user/view_certificate.html', certificate=certificate, booking=booking)

@user_bp.route('/notifications')
@login_required
@role_required('user')
def list_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark read state
    for notif in notifications:
        notif.is_read = True
    db.session.commit()
    
    return render_template('user/notifications.html', notifications=notifications)
