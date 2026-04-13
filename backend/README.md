# Isuku Backend - Waste Management System

This folder contains the Django backend for the Isuku waste management system.

## Features

- Landing page with system information
- Household registration and login
- Collector registration and login
- Admin dashboard
- Waste pickup request workflow
- Pickup assignment and management
- Server-rendered templates with Jinja2

## Technology Stack

- Backend: Django 5.2+
- Templates: Jinja2
- Database: SQLite by default (PostgreSQL recommended for production)

## Setup Instructions

### 1. Virtual Environment Setup

If your virtual environment is in the repository root (`../venv`), activate it from this folder with:

Windows PowerShell:
```powershell
..\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
..\venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source ../venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Load Sample Data (Recommended)

```bash
python manage.py create_sample_data
```

This creates sample locations, waste categories, and test user accounts.

### 6. Run the Development Server

```bash
python manage.py runserver
```

Application URL: `http://127.0.0.1:8000/`

## Accessing the Application

1. Landing page: `http://127.0.0.1:8000/`
2. Household login: `http://127.0.0.1:8000/household/login/`
3. Collector login: `http://127.0.0.1:8000/collector/login/`
4. Admin login: `http://127.0.0.1:8000/admin/login/`
5. Admin dashboard: `http://127.0.0.1:8000/portal-admin/dashboard/`
6. Django admin: `http://127.0.0.1:8000/admin/`

## Project Structure

```
backend/
├── isuku_app/          # Project settings and URLs
├── registration/       # Core app models, views, routes
├── templates/          # Jinja2 templates
├── static/             # Static assets
├── manage.py
├── requirements.txt
├── render.yaml
├── build.sh
└── upload_model_to_render.sh
```

## Core Models

- Province, District, Sector, Cell, Village
- Household
- Collector
- Admin
- WasteCategory
- WastePickupRequest
- Notification

## Render Deployment

Use files in this folder:

- `render.yaml`
- `build.sh`

## Required Environment Variables

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=isuku-app.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://isuku-app.onrender.com`
- `CORS_ALLOWED_ORIGINS=https://isuku.netlify.app`

## API Used By Split Frontend

- POST `/api/analyze-waste-image/`
- GET `/api/districts/?province_id=<id>`
- GET `/api/sectors/?district_id=<id>`
- GET `/api/cells/?sector_id=<id>`
- GET `/api/villages/?cell_id=<id>`

## Development Notes

To add features:

1. Update models in `registration/models.py`
2. Run migrations
3. Add views in `registration/views.py`
4. Update routes in `registration/urls.py`
5. Add templates in `templates/registration/`
