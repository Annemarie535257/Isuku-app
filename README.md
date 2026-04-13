# Isuku App Monorepo

This repository is split into frontend and backend apps.

## Project Folders

- `frontend/`: React + Vite frontend (Netlify target)
- `backend/`: Django backend (Render target)
- `AI_Chatbot/`: model training assets and chatbot-related resources

## Where To Find Backend Details

All backend documentation and deployment files are in `backend/`:

- `backend/README.md`
- `backend/render.yaml`
- `backend/build.sh`
- `backend/upload_model_to_render.sh`

## Deployment Summary

- Frontend deploy config: `frontend/netlify.toml`
- Backend deploy config: `backend/render.yaml`

See `FRONTEND_BACKEND_SPLIT.md` for the split overview.
