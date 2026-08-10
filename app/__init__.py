import os
from flask import Flask, render_template, request, session
from datetime import datetime
from app.config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    # Initialize the Flask instance
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extension bindings
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure user session loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        # Fetch user by integer ID
        return User.query.get(int(user_id))
        
    # Register application blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.staff_routes import staff_bp
    from app.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    
    @app.before_request
    def auto_switch_user_by_route():
        endpoint = request.endpoint
        if not endpoint:
            return
            
        # Ignore static, media assets, and endpoints that log out or switch roles manually
        if endpoint.startswith('static') or endpoint in ['auth.login', 'auth.register', 'auth.logout', 'auth.switch_role', 'auth.index']:
            return
            
        from flask_login import current_user, login_user
        from app.models.user import User
        
        # If it's an admin endpoint and we have an admin session user, make sure they are active
        if endpoint.startswith('admin.'):
            admin_user_id = session.get('admin_user_id')
            if admin_user_id:
                if not current_user.is_authenticated or current_user.id != admin_user_id:
                    user = User.query.get(admin_user_id)
                    if user and user.role == 'admin':
                        login_user(user)
                        
        # If it's a staff endpoint and we have a staff session user, make sure they are active
        elif endpoint.startswith('staff.'):
            staff_user_id = session.get('staff_user_id')
            if staff_user_id:
                if not current_user.is_authenticated or current_user.id != staff_user_id:
                    user = User.query.get(staff_user_id)
                    if user and user.role == 'staff':
                        login_user(user)
                        
        # If it's a trekker / user endpoint and we have a trekker session user, make sure they are active
        elif endpoint.startswith('user.'):
            user_user_id = session.get('user_user_id')
            if user_user_id:
                if not current_user.is_authenticated or current_user.id != user_user_id:
                    user = User.query.get(user_user_id)
                    if user and user.role == 'user':
                        login_user(user)
    
    # Configure custom error page routing templates
    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Prevent database lockups during crashes
        return render_template('errors/500.html'), 500
        
    # Inject current year into Jinja templates for copyright footers
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.utcnow().year
        }
        
    # Ensure static directories and uploads directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
