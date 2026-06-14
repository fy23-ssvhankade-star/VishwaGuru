# VishwaGuru

VishwaGuru is an open source platform empowering India's youth to engage with democracy. It uses AI to simplify contacting representatives, filing grievances, and organizing community action. Built for India's languages and governance, it turns selfies and videos into real civic impact.

## Features

- **AI-Powered Action Plans**: Generates WhatsApp messages, email drafts, and X.com posts for civic issues using Google's Gemini API.
- **Advanced AI Detection**:
    - **Local ML**: Uses lightweight YOLOv8 models for offline-capable detection of Potholes, Vandalism, Flooding, and more.
    - **Hybrid Architecture**: Automatically falls back to Hugging Face API if local models are unavailable.
- **Find My MLA**: Locate your constituency and representative details using pincode (Maharashtra focused MVP).
- **Issue Reporting**: Users can report issues via a web interface or a Telegram bot.
- **Modern Stack**: Built with React (Vite) and FastAPI.

## Architecture & Data Flow

VishwaGuru uses a unified backend architecture where a single FastAPI service powers the web frontend, AI services, database operations, and the Telegram bot.

### High-Level Flow

1. Users submit civic issues via Web UI or Telegram.
2. Requests reach the FastAPI backend.
3. Images are analyzed using **Local ML** (YOLOv8) or **Hugging Face** API for validation and categorization.
4. Data is validated and stored in the database.
5. Background tasks generate actionable drafts using **Google Gemini**.
6. AI-generated action plans are pushed to the user.

### Tech Stack

*   **Frontend**: React, Vite, Tailwind CSS
*   **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
*   **AI & ML**:
    *   Local: YOLOv8 (Ultralytics) for object detection.
    *   Cloud: Google Gemini (Generative AI), Hugging Face (Fallback).
*   **Database**: SQLite (Dev), PostgreSQL (Prod)
*   **Bot**: python-telegram-bot
*   **Deployment**: Render (Backend) + Netlify (Frontend)

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Git**

## Installation & Local Development

### 1. Clone the Repository

```bash
git clone <repository_url>
cd vishwaguru
```

### 2. Backend Setup

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file in the root directory:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    GEMINI_API_KEY=your_gemini_api_key
    HF_TOKEN=your_huggingface_token_optional
    DATABASE_URL=sqlite:///./data/issues.db
    FRONTEND_URL=http://localhost:5173
    ```

4.  Start the Backend:
    ```bash
    # From the root directory
    export PYTHONPATH=.
    python -m uvicorn backend.main:app --reload
    ```
    The API will be at `http://localhost:8000`.

### 3. Frontend Setup

1.  Navigate to frontend:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start Frontend:
    ```bash
    npm run dev
    ```
    The app will be at `http://localhost:5173`.

## Deployment Guide

VishwaGuru is designed for a split deployment: **Render** for the backend and **Netlify** for the frontend.

### Backend (Render)

1.  Create a new **Web Service** on Render connected to your repo.
2.  Settings:
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r backend/requirements.txt`
    *   **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3.  Environment Variables:
    *   `PYTHONPATH`: `backend`
    *   `GEMINI_API_KEY`: Your key.
    *   `DATABASE_URL`: Your PostgreSQL connection string (Render provides one if you add a Postgres database).
    *   `FRONTEND_URL`: Your Netlify URL (e.g., `https://my-app.netlify.app`).

### Frontend (Netlify)

1.  Create a new site from Git on Netlify.
2.  Settings:
    *   **Base directory**: `frontend`
    *   **Build command**: `npm run build`
    *   **Publish directory**: `frontend/dist`
3.  Environment Variables:
    *   `VITE_API_URL`: Your Render Backend URL (e.g., `https://my-app.onrender.com`).

## License

This project is licensed under the **AGPL-3.0** License.
