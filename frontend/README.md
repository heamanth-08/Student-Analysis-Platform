# CampusIQ Frontend

This folder is the standalone HTML frontend package. It uses Vite to serve and build all screen pages.

## Run locally

```powershell
npm install
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

The FastAPI backend is a separate Python project in `../campusiq-backend`. Start it with `python main.py`; its local API origin is `http://localhost:8000`.

## API configuration

Copy `.env.example` to `.env.local` and set `VITE_API_BASE_URL` to the backend origin. Set the matching frontend origin in the backend's `FRONTEND_ORIGINS`. Vite injects the shared API integration script into every HTML screen during development and production builds.

The current backend has no internship endpoint or separate research-publications model. Research entries can only be displayed if stored as Research-category achievements.