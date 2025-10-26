# AI Fake News Detector - Frontend

This is the React + Vite frontend for the AI Fake News Detector project.

Features:
- Login / Signup (JWT)
- Analyze text or image via backend
- History, Profile, Settings
- Dark / Light theme

Setup

1. Install dependencies:

```powershell
cd frontend; npm install
```

2. Start dev server:

```powershell
npm run dev
```

Backend

Make sure the Flask backend is running on `http://localhost:5000` and supports the documented routes.

Environment

- Edit `.env` to change `VITE_API_BASE_URL` if needed.
