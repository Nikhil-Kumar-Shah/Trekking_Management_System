import os
from datetime import datetime, date, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.trek import Trek
from app.models.assignment import TrekStaffAssignment
from app.models.booking import Booking
from app.models.attendance import TrekAttendance
from app.models.certificate import TrekCertificate
from app.models.status_log import TrekStatusLog

# Create the application instance
app = create_app()

def seed_database():
    """
    Checks if database table content is seeded and creates default records:
    - 1 Admin: admin@trekking.com / admin123
    - 1 Staff: staff@trekking.com / staff123
    - 1 Trekker: trekker@trekking.com / trekker123
    - 3 sample Treks: Open, Closed, Completed
    - 1 Active Staff Assignment
    - 1 Checked-In Booking with completion certificate
    """
    # Verify if users are already registered
    admin_exists = User.query.filter_by(role='admin').first()
    if admin_exists:
        # Database already initialized and seeded
        print("Database already contains users. Skipping seed process.")
        return
        
    print("Seeding database with default demo records...")
    
    # 1. Create Admin
    admin_user = User(
        full_name="System Administrator",
        email="admin@trekking.com",
        phone="9876543210",
        role="admin",
        is_active=True,
        is_blacklisted=False
    )
    admin_user.set_password("admin123")
    db.session.add(admin_user)
    
    # 2. Create Staff
    staff_user = User(
        full_name="John Guide",
        email="staff@trekking.com",
        phone="9812345678",
        role="staff",
        is_active=True,
        is_blacklisted=False
    )
    staff_user.set_password("staff123")
    db.session.add(staff_user)
    
    # 3. Create Trekker / User
    trekker_user = User(
        full_name="Alice Trekker",
        email="trekker@trekking.com",
        phone="9801112222",
        role="user",
        blood_group="O+",
        medical_conditions="Mild seasonal asthma",
        emergency_contact_name="Bob Trekker (Father)",
        emergency_contact_phone="9803334444",
        is_active=True,
        is_blacklisted=False
    )
    trekker_user.set_password("trekker123")
    db.session.add(trekker_user)
    
    # Flush users to obtain primary keys
    db.session.flush()
    
    # 4. Create sample Treks
    # Trek A: Everest Base Camp (Open status)
    trek_ebc = Trek(
        title="Everest Base Camp Trek",
        location="Solukhumbu District, Nepal",
        altitude=5364,
        difficulty_level="Hard",
        duration_days=14,
        description="A challenging walk through the heart of the Sherpa culture to the base of the highest peak in the world. Features magnificent vistas of Everest, Lhotse, and Ama Dablam.",
        max_slots=15,
        available_slots=14,  # One slot taken by Alice
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=44),
        meeting_point="Tribhuvan International Airport Domestic Terminal, Kathmandu",
        trek_status="Open",
        created_by=admin_user.id
    )
    db.session.add(trek_ebc)
    
    # Trek B: Annapurna Circuit Trek (Closed status)
    trek_annapurna = Trek(
        title="Annapurna Circuit Expedition",
        location="Gandaki Province, Nepal",
        altitude=5416,
        difficulty_level="Moderate",
        duration_days=12,
        description="A classical circuit around the Annapurna massif. Crossing Thorong La Pass at 5416 meters is the highlight of this trek.",
        max_slots=20,
        available_slots=20,
        start_date=date.today() + timedelta(days=15),
        end_date=date.today() + timedelta(days=27),
        meeting_point="Lakeside Pokhara Information Center",
        trek_status="Closed",
        created_by=admin_user.id
    )
    db.session.add(trek_annapurna)
    
    # Trek C: Langtang Valley Trek (Completed status)
    trek_langtang = Trek(
        title="Langtang Valley Journey",
        location="Langtang National Park, Nepal",
        altitude=3870,
        difficulty_level="Easy",
        duration_days=8,
        description="A scenic trek through rhododendron and bamboo forests up to the alpine meadows of Kyanjin Gompa.",
        max_slots=10,
        available_slots=9,
        start_date=date.today() - timedelta(days=15),
        end_date=date.today() - timedelta(days=7),
        meeting_point="Machhapokhari Bus Park, Kathmandu",
        trek_status="Completed",
        created_by=admin_user.id
    )
    db.session.add(trek_langtang)
    
    db.session.flush()
    
    # 5. Create Staff Assignments
    assign_ebc = TrekStaffAssignment(
        trek_id=trek_ebc.id,
        staff_id=staff_user.id,
        assigned_role="Guide",
        assignment_status="Active"
    )
    db.session.add(assign_ebc)
    
    assign_langtang = TrekStaffAssignment(
        trek_id=trek_langtang.id,
        staff_id=staff_user.id,
        assigned_role="Guide",
        assignment_status="Active"
    )
    db.session.add(assign_langtang)
    
    # 6. Create Bookings & Attendance & Certificates for Completed Trek
    # Alice books Everest Base Camp
    booking_ebc = Booking(
        user_id=trekker_user.id,
        trek_id=trek_ebc.id,
        booking_status="Booked",
        payment_status="Paid",
        checked_in=False,
        special_requests="Requesting vegetarian meals during the trek."
    )
    db.session.add(booking_ebc)
    
    # Alice booked and completed Langtang Valley
    booking_langtang = Booking(
        user_id=trekker_user.id,
        trek_id=trek_langtang.id,
        booking_status="Booked",
        payment_status="Paid",
        checked_in=True,  # Attended
        special_requests=""
    )
    db.session.add(booking_langtang)
    db.session.flush()
    
    # Log attendance
    attendance_langtang = TrekAttendance(
        booking_id=booking_langtang.id,
        attendance_status="Present",
        check_in_time=datetime.utcnow() - timedelta(days=14),
        marked_by_staff_id=staff_user.id,
        notes="Alice was fully fit and completed the trek ahead of schedule."
    )
    db.session.add(attendance_langtang)
    
    # Generate certificate
    cert_langtang = TrekCertificate(
        booking_id=booking_langtang.id,
        certificate_number="TRK-0002-DEMO99",
        generated_at=datetime.utcnow() - timedelta(days=7),
        certificate_url="/my-certificates/TRK-0002-DEMO99/view"
    )
    db.session.add(cert_langtang)
    
    # 7. Create Trek Status Logs
    log_ebc = TrekStatusLog(
        trek_id=trek_ebc.id,
        old_status=None,
        new_status="Open",
        changed_by=admin_user.id,
        reason="Initial scheduling."
    )
    db.session.add(log_ebc)
    
    log_langtang_1 = TrekStatusLog(
        trek_id=trek_langtang.id,
        old_status="Open",
        new_status="In Progress",
        changed_by=staff_user.id,
        reason="Expedition team reached trailhead."
    )
    db.session.add(log_langtang_1)
    
    log_langtang_2 = TrekStatusLog(
        trek_id=trek_langtang.id,
        old_status="In Progress",
        new_status="Completed",
        changed_by=staff_user.id,
        reason="Trek concluded successfully. All members returned safely."
    )
    db.session.add(log_langtang_2)
    
    # Commit transaction
    db.session.commit()
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    # Initialize SQLite database file and tables if not existing
    with app.app_context():
        db.create_all()
        seed_database()
        
    # Start development server on port 5000
    app.run(debug=True, port=5000)
