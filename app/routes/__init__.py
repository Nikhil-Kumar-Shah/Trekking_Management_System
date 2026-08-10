from app.routes.auth_routes import auth_bp
from app.routes.admin_routes import admin_bp
from app.routes.staff_routes import staff_bp
from app.routes.user_routes import user_bp

__all__ = [
    'auth_bp',
    'admin_bp',
    'staff_bp',
    'user_bp'
]
