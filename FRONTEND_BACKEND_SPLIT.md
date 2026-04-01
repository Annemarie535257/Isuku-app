# Frontend/Backend Split Plan

## Frontend folder
- Path: `frontend/`
- Hosting target: Netlify
- Base directory in Netlify: `frontend`
- Publish directory: `.`
- Build command: leave empty (static app)

## Backend folder
- Path: `backend/` (documentation)
- Hosting target: Render
- Backend source currently remains in repo root.

## API Base URL
In `frontend/index.html`:
`window.API_BASE_URL = "https://isuku-app.onrender.com";`

## Backend CORS
Django now allows cross-origin calls via `CORS_ALLOWED_ORIGINS` setting.

## Netlify settings
- Branch: `main`
- Base directory: `frontend`
- Build command: (empty)
- Publish directory: `.`
