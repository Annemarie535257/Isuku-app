# Isuku App - Waste Management System

A Django-based waste management system connecting households with waste collectors.

## Features

- **Landing Page** with information about the waste management system
- **Household Registration & Login** - For households to request waste pickup
- **Collector Registration & Login** - For waste collectors to manage pickups
- **Admin Dashboard** - For administrators to manage the system
- **Waste Pickup Requests** - Households can request waste collection
- **Pickup Management** - Collectors can view and assign pickups
- **Clean, modern UI** with Tailwind CSS

## Technology Stack

- **Backend**: Django 5.2+
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Templates**: Jinja2
- **Database**: SQLite (default, can be changed)

## Setup Instructions

### 1. Virtual Environment Setup

The virtual environment has already been created in the `venv` directory. To activate it:

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

Dependencies should already be installed. If you need to reinstall:

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 5. Load sample data (recommended for testing)

Create sample data including test user accounts:

```bash
python manage.py create_sample_data
```

This will create:
- Sample provinces, districts, sectors, cells, and villages
- Waste categories (Organic, Plastic, Paper, Glass, Metal, General)
- A test household user (username: `household@test.com`, password: `testpass123`)
- A test collector user (username: `collector@test.com`, password: `testpass123`)
- A test admin user (username: `admin@test.com`, password: `testpass123`)

### 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Accessing the Application

1. **Landing Page**: `http://127.0.0.1:8000/`
   - Contains information about the waste management system
   - Includes login forms for households and collectors
   - Links to registration pages

2. **Household Login**: `http://127.0.0.1:8000/household/login/`
   - Username: `household@test.com`
   - Password: `testpass123`

3. **Household Dashboard**: `http://127.0.0.1:8000/household/dashboard/`
   - View pickup requests
   - Create new pickup requests
   - View notifications

4. **Collector Login**: `http://127.0.0.1:8000/collector/login/`
   - Username: `collector@test.com`
   - Password: `testpass123`

5. **Collector Dashboard**: `http://127.0.0.1:8000/collector/dashboard/`
   - View available pickups
   - Assign pickups to yourself
   - Manage assigned pickups

6. **Admin Login**: `http://127.0.0.1:8000/admin/login/`
   - Username: `admin@test.com`
   - Password: `testpass123`

7. **Admin Dashboard**: `http://127.0.0.1:8000/portal-admin/dashboard/`
   - View system statistics
   - Manage households and collectors
   - View recent activity

8. **Django Admin**: `http://127.0.0.1:8000/admin/`
   - Full administrative interface
   - Manage all models and data

## Project Structure

```
isuku_app/
├── isuku_app/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── jinja2.py       # Jinja2 configuration
├── registration/       # Registration app
│   ├── models.py       # Household, Collector, Admin, WasteCategory, etc.
│   ├── views.py        # View functions
│   ├── urls.py         # URL routing
│   └── admin.py        # Admin configuration
├── templates/          # Jinja2 templates
│   ├── base.html
│   ├── landing.html
│   └── registration/
│       ├── household_login.html
│       ├── household_signup.html
│       ├── household_dashboard.html
│       ├── collector_login.html
│       ├── collector_signup.html
│       ├── collector_dashboard.html
│       ├── admin_login.html
│       └── admin_dashboard.html
├── static/             # Static files (CSS, JS, images)
│   ├── images/         # Logo and other images
│   ├── css/
│   └── js/
├── manage.py
└── requirements.txt
```

## Models

- **Province, District, Sector, Cell, Village**: Location hierarchy
- **Household**: Household user profiles with location information
- **Collector**: Waste collector profiles with license and vehicle information
- **Admin**: Admin user profiles with roles
- **WasteCategory**: Categories of waste (Organic, Plastic, Paper, etc.)
- **WastePickupRequest**: Pickup requests from households
- **Notification**: User notifications

## User Types

1. **Households**: Can create pickup requests, view their requests, and receive notifications
2. **Collectors**: Can view available pickups, assign pickups to themselves, and manage assigned pickups
3. **Admin**: Can view system statistics, manage users, and oversee the entire system

## Notes

- The application uses Jinja2 templates instead of Django templates
- Tailwind CSS is loaded via CDN for quick setup
- Font Awesome icons are used for UI elements
- For production, consider:
  - Setting up proper static file serving
  - Using Tailwind via npm/build process
  - Adding proper authentication middleware
  - Securing the SECRET_KEY
  - Setting DEBUG = False
  - Using a production database (PostgreSQL, MySQL)
  - Adding email functionality for notifications
  - Implementing AJAX for dynamic location dropdowns

## Development

To add new features:
1. Update models in `registration/models.py`
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Create views in `registration/views.py`
4. Add URL patterns in `registration/urls.py`
5. Create templates in `templates/registration/`
