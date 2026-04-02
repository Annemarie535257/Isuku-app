# Frontend/Backend Split Plan

## Frontend folder
- Path: `frontend/`
- Hosting target: Netlify
- Base directory in Netlify: `frontend`
- Build command: `npm run build`
- Publish directory: `dist`

## Backend folder
- Path: `backend/`
- Hosting target: Render
- Django source now lives in this folder.

## API Base URL
In Netlify env vars:
`VITE_API_BASE_URL=https://isuku-app.onrender.com`

## Backend CORS
Django now allows cross-origin calls via `CORS_ALLOWED_ORIGINS` setting.

## Netlify settings
- Branch: `main`
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `dist`
