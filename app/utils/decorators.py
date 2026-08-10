from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user, logout_user

def role_required(*roles):
    """
    Decorator to restrict access to specific roles (e.g. admin, staff, user).
    Ensures user is authenticated, active, and not blacklisted.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate authentication state
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            # Check if account status is active and not blacklisted
            if not current_user.is_active:
                logout_user()
                flash("Your account is currently disabled.", "danger")
                return redirect(url_for('auth.login'))
                
            if current_user.is_blacklisted:
                logout_user()
                flash("Access denied. Your account is blacklisted.", "danger")
                return redirect(url_for('auth.login'))
            
            # Match role with permissions
            if current_user.role not in roles:
                abort(403)  # Forbidden access
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
