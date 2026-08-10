from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Trek
from app.routes.forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    # Fetch a few featured open treks to display on the landing page
    featured_treks = Trek.query.filter_by(trek_status='Open').limit(3).all()
    return render_template('index.html', treks=featured_treks)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to respective dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
            
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Check user password
            if user.check_password(form.password.data):
                # Verify blacklist
                if user.is_blacklisted:
                    flash("Your account has been blacklisted. Access denied.", "danger")
                    return redirect(url_for('auth.login'))
                    
                # Verify activity status
                if not user.is_active:
                    flash("Your account is currently inactive.", "danger")
                    return redirect(url_for('auth.login'))
                
                # Perform login
                login_user(user, remember=form.remember_me.data)
                flash(f"Welcome back, {user.full_name}!", "success")
                
                # Store user identifiers in session for quick switcher access
                if user.role == 'admin':
                    session['admin_user_id'] = user.id
                elif user.role == 'staff':
                    session['staff_user_id'] = user.id
                else:
                    session['user_user_id'] = user.id
                
                # Role-based redirection
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'staff':
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                flash("Invalid email or password.", "danger")
        else:
            flash("Invalid email or password.", "danger")
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect away
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
            
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email is registered
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email address is already registered.", "danger")
            return render_template('auth/register.html', form=form)
            
        # Create new user
        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            role='user',  # Only user role can self-register
            blood_group=form.blood_group.data or None,
            medical_conditions=form.medical_conditions.data or None,
            emergency_contact_name=form.emergency_contact_name.data or None,
            emergency_contact_phone=form.emergency_contact_phone.data or None,
            is_blacklisted=False,
            is_active=True
        )
        new_user.set_password(form.password.data)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # Clear only the current user's role session key
    role = current_user.role
    if role == 'admin':
        session.pop('admin_user_id', None)
    elif role == 'staff':
        session.pop('staff_user_id', None)
    elif role == 'user':
        session.pop('user_user_id', None)
        
    logout_user()
    
    # Try to find another active session in session variables to switch into
    next_role_user = None
    from app.models.user import User
    for role_key, session_key in [('admin', 'admin_user_id'), ('staff', 'staff_user_id'), ('user', 'user_user_id')]:
        user_id = session.get(session_key)
        if user_id:
            user = User.query.get(user_id)
            if user:
                next_role_user = user
                break
                
    if next_role_user:
        login_user(next_role_user)
        flash(f"Logged out from previous role. Switched active role to {next_role_user.role}.", "info")
        if next_role_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif next_role_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
            
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/auto-login/<string:role>')
def auto_login(role):
    # Determine the seed email for the target role
    if role == 'admin':
        email = 'admin@trekking.com'
    elif role == 'staff':
        email = 'staff@trekking.com'
    elif role == 'user':
        email = 'trekker@trekking.com'
    else:
        flash("Invalid auto-login role specified.", "danger")
        return redirect(url_for('auth.index'))
        
    user = User.query.filter_by(email=email).first()
    if user:
        if current_user.is_authenticated:
            # Save the current user role's session key before switching
            curr_role = current_user.role
            if curr_role == 'admin':
                session['admin_user_id'] = current_user.id
            elif curr_role == 'staff':
                session['staff_user_id'] = current_user.id
            elif curr_role == 'user':
                session['user_user_id'] = current_user.id
            logout_user()
            
        login_user(user)
        session[f"{'user' if role == 'user' else role}_user_id"] = user.id
        flash(f"Logged in successfully as {user.full_name}.", "success")
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    else:
        flash("Seed account not found in the database.", "danger")
        return redirect(url_for('auth.index'))

@auth_bp.route('/switch-role/<string:role>')
@login_required
def switch_role(role):
    # Perform quick switching between stored sessions
    user = None
    session_key = 'admin_user_id' if role == 'admin' else ('staff_user_id' if role == 'staff' else 'user_user_id')
    user_id = session.get(session_key)
    
    if user_id:
        user = User.query.get(user_id)
        
    # Fallback to seed account if no session key exists yet
    if not user:
        if role == 'admin':
            user = User.query.filter_by(email='admin@trekking.com').first()
        elif role == 'staff':
            user = User.query.filter_by(email='staff@trekking.com').first()
        elif role == 'user':
            user = User.query.filter_by(email='trekker@trekking.com').first()
            
    if user:
        # Save the current user role's session key before switching
        current_role = current_user.role
        if current_role == 'admin':
            session['admin_user_id'] = current_user.id
        elif current_role == 'staff':
            session['staff_user_id'] = current_user.id
        elif current_role == 'user':
            session['user_user_id'] = current_user.id
            
        login_user(user)
        session[session_key] = user.id
        flash(f"Switched to {role.upper()} session successfully.", "success")
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
            
    flash("The selected role user account could not be found.", "warning")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Update user record
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        current_user.blood_group = form.blood_group.data
        current_user.medical_conditions = form.medical_conditions.data
        current_user.emergency_contact_name = form.emergency_contact_name.data
        current_user.emergency_contact_phone = form.emergency_contact_phone.data
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Verify old password
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Your password has been changed successfully!", "success")
            return redirect(url_for('auth.profile'))
        else:
            flash("Incorrect current password.", "danger")
            
    return render_template('auth/change_password.html', form=form)
