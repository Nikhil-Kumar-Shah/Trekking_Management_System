# 🏔️ Trekking Operations Management System (TOMS)

A clean, responsive, and role-based web application built with **Flask**, **Jinja2**, **SQLAlchemy**, and **Bootstrap 5** featuring a distinctive Brutalist/Bauhaus visual design language. 

TOMS simplifies mountain expedition logistics, crew assignments, participant bookings, attendance tracking, and automated completion certificate generation.

---

## ✨ Key Features

### 👑 Admin Portal
- **Dashboard Overview**: Real-time metrics for active treks, open bookings, staff counts, and trekker registrations.
- **Trek Management**: Full CRUD operations for creating, updating, and cancelling trekking expeditions.
- **Staff Assignment**: Assign guides and medical personnel to specific treks with defined operational roles.
- **User & Blacklist Management**: Monitor registered trekkers, inspect medical profiles, and manage blacklist flags.
- **Reports & Audit Trail**: Tabbed report engine tracking trek status transitions, payment status, and certificate issuance records.

### 🥾 Staff / Guide Portal
- **Assigned Expeditions**: Overview of assigned treks, date ranges, and booked capacity.
- **On-Field Attendance**: Log participant check-ins and record field notes (fitness, delays, gear checks).
- **Status & Slot Updates**: Dynamic status progression (Open → Closed → In Progress → Completed) with required change reason logging. Automated certificate generation triggers when marked *Completed*.

### 🎒 Trekker / User Portal
- **Expedition Discovery**: Search and filter open treks by location and difficulty level (Easy, Moderate, Hard).
- **Booking & Medical Verification**: Register for treks with pre-filled medical profiles, blood group info, emergency contact details, and special requests.
- **Trek History & Certificates**: View upcoming and past trips, cancel bookings, and download/print verified completion certificates.
- **In-App Notifications**: Real-time alerts for booking confirmations and expedition status changes.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy (SQLite ORM), Flask-WTForms, Flask-Login, Werkzeug
- **Frontend**: Jinja2 Templates, HTML5, Vanilla CSS (Modular CSS Tokens), Bootstrap 5, FontAwesome 6
- **Architecture**: Model-View-Controller (MVC) Pattern with Flask Blueprints and Services Layer

---

## 📁 Project Structure

```text
Trekking_app/
│
├── run.py                    # App entry point (creates DB, seeds accounts, starts server)
├── test_dashboards.py        # Automated routing & role-flow diagnostic test script
├── trekking.db               # SQLite database instance
│
└── app/
    ├── config.py             # Flask app configuration settings
    ├── extensions.py         # SQLAlchemy & Flask-Login instances
    │
    ├── models/               # SQLAlchemy ORM Database Schemas
    │   ├── user.py           # User model & password hashing logic
    │   ├── trek.py           # Trek event model & status logs
    │   ├── booking.py        # Booking registration model
    │   └── assignment.py     # Staff-to-trek assignment model
    │
    ├── routes/               # Flask Controller Blueprints
    │   ├── auth_routes.py    # Login, registration, profile, role switching
    │   ├── admin_routes.py   # Admin management & reports controllers
    │   ├── staff_routes.py   # Staff dashboard, attendance, status controllers
    │   ├── user_routes.py    # Trekker browsing, booking, certificate controllers
    │   └── forms.py          # WTForms field definitions & validation rules
    │
    ├── services/             # Core Business Logic Layer
    │   └── booking_service.py # Booking validation, capacity, and certificate generation
    │
    ├── static/
    │   └── css/              # Modular CSS Architecture
    │       ├── base.css      # Theme variables, colors, typography, resets
    │       ├── components.css# Brutalist cards, buttons, forms, tables, badges, navbar
    │       ├── pages.css     # Page layout overrides, print styles, media queries
    │       └── style.css     # Master stylesheet importer (@import)
    │
    └── templates/            # Jinja2 HTML Templates
        ├── base.html         # Base template skeleton
        ├── index.html        # Public landing page & demo switcher
        ├── admin/            # Admin portal templates
        ├── auth/             # Authentication & profile templates
        ├── errors/           # 401, 403, 404, 500 error pages
        ├── partials/         # Navbar, sidebar, footer, flash message partials
        ├── staff/            # Staff portal templates
        └── user/             # Trekker portal templates
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Set Up Virtual Environment
```bash
# Clone the repository (or navigate to project directory)
cd Trekking_app

# Create a virtual environment
python -m venv env

# Activate the virtual environment
# Windows (PowerShell):
.\env\Scripts\Activate.ps1
# macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-wtf flask-login werkzeug
```

### 4. Run the Application
```bash
python run.py
```
*`run.py` automatically initializes the SQLite database (`trekking.db`) and populates initial demo seed accounts.*

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials

For testing and demonstration, use the following pre-seeded accounts:

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@trekking.com` | `admin123` | Full administrative control |
| **Staff Guide** | `staff@trekking.com` | `staff123` | Expedition attendance & status management |
| **Trekker** | `trekker@trekking.com` | `trekker123` | Booking expeditions & printing certificates |

*Note: The landing page (`/`) includes an interactive **Developer Session Swapper** for quick one-click role switching.*

---

## 🧪 Testing & Verification

Run the automated routing test suite to verify route access control, authentication, and role flows:

```bash
python test_dashboards.py
```

---

## 🎨 Visual Identity

The project features a **Brutalist / Bauhaus-inspired** design system:
- **Palette**: Off-White Cream (`#f2f0e9`), Pure White (`#ffffff`), Warm Yellow (`#f4a261`), Teal (`#2a9d8f`), and Coral Accent (`#e63946`).
- **Typography**: Space Grotesk (Headings) & Space Mono (Data / Code elements).
- **Aesthetics**: High-contrast 4px borders, offset drop shadows, sharp edges, and zero unnecessary client-side dependencies.

---

## 📄 License
Academic & Portfolio Project. Built for Trekking Operations Management.
