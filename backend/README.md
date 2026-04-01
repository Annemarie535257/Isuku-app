# Backend (Render)

This folder documents backend deployment for the Django API hosted on Render.

## Current backend source
The active Django backend source remains at repository root:
- isuku_app/
- registration/
- manage.py

## Render deployment
Use `render.yaml` and `build.sh` from repository root.

## Required environment variables
- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS=isuku-app.onrender.com
- CSRF_TRUSTED_ORIGINS=https://isuku-app.onrender.com
- CORS_ALLOWED_ORIGINS=https://isuku.netlify.app
- DATABASE_URL (recommended Postgres)

## API used by separated frontend
- POST /api/analyze-waste-image/
- GET /api/districts/?province_id=<id>
- GET /api/sectors/?district_id=<id>
- GET /api/cells/?sector_id=<id>
- GET /api/villages/?cell_id=<id>
