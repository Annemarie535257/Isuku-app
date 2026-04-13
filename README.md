# Isuku App

Isuku App is a full-stack waste management platform with:

- a Django backend for authentication, dashboards, workflows, and APIs
- a React + Vite frontend for split deployment
- optional AI modules for chatbot responses and image-based waste classification

The system supports households, collectors, and admins, with waste pickup workflows, geolocation features, OTP verification, and multilingual chatbot support (English, Kinyarwanda, French).

## Repository Structure

```
Isuku-app/
|- backend/          # Django application (main backend)
|- frontend/         # React + Vite app (split frontend)
|- AI_Chatbot/       # Notebook + dependencies for chatbot training
|- .venv/            # Local Python virtual environment (if created)
|- venv/             # Alternate local Python environment (if created)
```

## Core Features

- Role-based flows for Household, Collector, and Admin users
- Household and collector registration/login
- OTP request, verify, and resend flow
- Waste pickup request lifecycle: Pending, Scheduled, In Progress, Completed, Cancelled
- Location hierarchy support: Province, District, Sector, Cell, Village
- Geolocation APIs for nearby collectors and pickups
- Waste image analysis endpoint
- AI waste classification endpoint
- Chatbot endpoint with multilingual responses
- Server-rendered dashboards and pages using Django templates/Jinja2

## Technology Stack

### Backend

- Python
- Django
- Jinja2 templates
- WhiteNoise for static files
- django-cors-headers for cross-origin support
- dj-database-url for DB configuration
- SQLite by default, PostgreSQL-ready via DATABASE_URL
- Gunicorn for production serving

### Frontend

- React 18
- React DOM
- Vite 5
- @vitejs/plugin-react

### AI and ML (Backend Runtime + Training)

- PyTorch
- Transformers
- PEFT
- Accelerate
- Torchvision
- Pillow
- NumPy

### AI_Chatbot Training Assets

- Jupyter + IPython kernel
- pandas
- scikit-learn
- datasets
- bitsandbytes (optional/performance-oriented)

## Model Training Details

The chatbot model was trained/fine-tuned using the stack below:

- Base model: TinyLlama/TinyLlama-1.1B-Chat-v1.0
- Framework: PyTorch
- Transformer training/inference utilities: Hugging Face Transformers
- Fine-tuning approach: PEFT (LoRA adapters)
- Training orchestration: Accelerate
- Memory/performance optimization: bitsandbytes
- Dataset handling: datasets
- Training environment: Jupyter Notebook (train_llama_chatbot.ipynb)

Related files:

- AI_Chatbot/train_llama_chatbot.ipynb
- AI_Chatbot/requirements.txt
- backend/registration/chatbot_service.py

## Backend Dependencies

From backend/requirements.txt:

- Django
- Jinja2
- gunicorn
- whitenoise
- dj-database-url
- psycopg2-binary
- django-cors-headers
- torch
- transformers
- peft
- accelerate
- torchvision
- Pillow
- numpy

## Frontend Dependencies

From frontend/package.json:

- react
- react-dom
- vite
- @vitejs/plugin-react

## AI_Chatbot Dependencies

From AI_Chatbot/requirements.txt:

- torch
- transformers
- accelerate
- peft
- bitsandbytes
- pandas
- numpy
- openpyxl
- scikit-learn
- datasets
- jupyter
- ipykernel

## Main API Endpoints

### Utility and Data Endpoints

- GET /api/districts/?province_id=<id>
- GET /api/sectors/?district_id=<id>
- GET /api/cells/?sector_id=<id>
- GET /api/villages/?cell_id=<id>

### Waste and AI Endpoints

- POST /api/analyze-waste-image/
- POST /api/classify-waste/

### Chatbot Endpoint

- POST /api/chatbot/

Expected request payload example:

```
{
	"question": "How do I request pickup?",
	"language": "en"
}
```

Supported language values:

- en (English)
- rw (Kinyarwanda)
- fr (French)

### OTP Endpoints

- POST /api/send-otp/
- POST /api/request-otp/
- POST /api/verify-otp/
- POST /api/resend-otp/

### Geolocation Endpoints

- GET /api/nearby-collectors/
- GET /api/nearby-pickups/
- POST /api/update-location/

## Data Model Overview

Key models include:

- Province, District, Sector, Cell, Village
- Household
- Collector
- Admin
- WasteCategory
- WastePickupRequest
- Notification
- OTP

## Local Development Setup

### 1. Clone Repository

Use your normal git clone workflow, then move into the repository root.

### 2. Backend Setup

From the backend folder:

1. Create/activate a Python virtual environment
2. Install dependencies
3. Run migrations
4. Optionally create a superuser
5. Optionally seed sample data
6. Start Django

Commands:

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sample_data
python manage.py runserver 127.0.0.1:8000
```

### 3. Frontend Setup

From the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

Optional production-like local preview:

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

### 4. Frontend Environment Variable

Set the backend base URL used by React:

- VITE_API_BASE_URL

Example:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If not set, frontend currently defaults to the deployed backend URL.

### 5. AI_Chatbot Notebook Setup (Optional)

From AI_Chatbot:

```bash
cd AI_Chatbot
pip install -r requirements.txt
jupyter notebook
```

Use train_llama_chatbot.ipynb for model training experiments.

## Deployment

### Backend (Render)

Deployment configuration exists in backend/render.yaml with:

- buildCommand: install requirements, migrate, collectstatic
- startCommand: gunicorn isuku_app.wsgi:application
- health check path: /

### Frontend (Netlify)

Deployment configuration exists in frontend/netlify.toml with:

- build command: npm ci && npm run build
- publish directory: dist
- SPA redirect to /index.html

## Backend Environment Variables

Common variables used in backend settings/deployment:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- CSRF_TRUSTED_ORIGINS
- CORS_ALLOWED_ORIGINS
- DATABASE_URL (optional, for PostgreSQL)
- DATABASE_FILE (optional, for SQLite path override)

## Notes on AI Behavior

- Chatbot service attempts to load a local fine-tuned model from AI_Chatbot models path.
- If ML dependencies or model files are unavailable, it falls back to deterministic responses.
- Waste classification also includes fallback behavior when full ML inference is unavailable.

## Useful Paths

- backend/README.md
- backend/render.yaml
- backend/build.sh
- backend/manage.py
- backend/registration/models.py
- backend/registration/urls.py
- backend/registration/views.py
- backend/registration/chatbot_service.py
- backend/registration/waste_classifier.py
- frontend/package.json
- frontend/netlify.toml
- frontend/src/App.jsx
- AI_Chatbot/README.md
- AI_Chatbot/requirements.txt

## License

No explicit license file is currently present in the repository. Add one if you plan to distribute this project publicly.
