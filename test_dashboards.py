import sys
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

def test_routes():
    print("Beginning diagnostic routing tests...")
    
    # Run DB queries inside context and close it
    with app.app_context():
        admin_db = User.query.filter_by(email='admin@trekking.com').first()
        staff_db = User.query.filter_by(email='staff@trekking.com').first()
        user_db = User.query.filter_by(email='trekker@trekking.com').first()
        
        print(f"Admin DB: {admin_db.email if admin_db else 'None'} | Role: {admin_db.role if admin_db else 'None'}")
        print(f"Staff DB: {staff_db.email if staff_db else 'None'} | Role: {staff_db.role if staff_db else 'None'}")
        print(f"User DB: {user_db.email if user_db else 'None'} | Role: {user_db.role if user_db else 'None'}")

    # Set CSRF to false on app config directly
    app.config['WTF_CSRF_ENABLED'] = False
    
    # 1. Test unauthenticated root access
    with app.test_client() as client:
        res = client.get('/', follow_redirects=True)
        print(f"Unauthenticated '/' status code: {res.status_code}")
        
    # 2. Test Admin Login and Dashboard
    with app.test_client() as client:
        login_res = client.post('/login', data={
            'email': 'admin@trekking.com',
            'password': 'admin123'
        })
        print(f"Admin Login POST status: {login_res.status_code} | Redirect to: {login_res.location}")
        
        # Test all admin routes
        for path in ['/admin/dashboard', '/admin/treks', '/admin/bookings', '/admin/staff', '/admin/reports']:
            res = client.get(path)
            print(f"Admin GET '{path}' status code: {res.status_code}")
        
    # 3. Test Staff Login and Dashboard
    with app.test_client() as client:
        login_res = client.post('/login', data={
            'email': 'staff@trekking.com',
            'password': 'staff123'
        })
        print(f"Staff Login POST status: {login_res.status_code} | Redirect to: {login_res.location}")
        
        # Test all staff routes
        for path in ['/staff/dashboard', '/staff/treks']:
            res = client.get(path)
            print(f"Staff GET '{path}' status code: {res.status_code}")
            
    # 4. Test Trekker Login and Dashboard
    with app.test_client() as client:
        login_res = client.post('/login', data={
            'email': 'trekker@trekking.com',
            'password': 'trekker123'
        })
        print(f"Trekker Login POST status: {login_res.status_code} | Redirect to: {login_res.location}")
        
        # Test all user routes
        for path in ['/dashboard', '/treks', '/my-bookings', '/my-history', '/my-certificates', '/notifications']:
            res = client.get(path)
            print(f"Trekker GET '{path}' status code: {res.status_code}")
            
    # 5. Test Auto-Login and Switch-Role
    with app.test_client() as client:
        # Get auto-login admin
        res = client.get('/auto-login/admin', follow_redirects=False)
        print(f"Auto-login admin status: {res.status_code} | Redirect to: {res.location}")
        
        # Switch to staff
        res = client.get('/switch-role/staff', follow_redirects=False)
        print(f"Switch role staff status: {res.status_code} | Redirect to: {res.location}")
        
        # Switch to user
        res = client.get('/switch-role/user', follow_redirects=False)
        print(f"Switch role user status: {res.status_code} | Redirect to: {res.location}")

if __name__ == '__main__':
    test_routes()
