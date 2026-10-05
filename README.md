# Student Analysis Platform

This repository contains the frontend and backend for the Student Analysis Platform.

## Project Structure

- `frontend/`: Contains the user interface built with Vite.
- `backend/`: Contains the REST API built with Python (FastAPI).

## Prerequisites

Before running the project, make sure you have the following installed:
- [Node.js](https://nodejs.org/) (for the frontend)
- [Python 3.8+](https://www.python.org/downloads/) (for the backend)

## How to Run Manually

### 1. Start the Backend

Open a terminal and navigate to the `backend` directory:

```bash
cd backend
```

Create a virtual environment and activate it:

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
uvicorn app.main:app --reload
```
The backend server will start at `http://127.0.0.1:8000`.


### 2. Start the Frontend

Open a **new** terminal window and navigate to the `frontend` directory:

```bash
cd frontend
```

Install the required Node packages:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will start locally. The terminal output will show you the exact local URL (typically `http://localhost:5173` or `http://localhost:3000`) where you can view the application in your browser.

## Deployment Instructions

### Deploying the Frontend

You can easily deploy the frontend to services like Vercel or Netlify.

**Using Vercel:**
1. Sign up on [Vercel](https://vercel.com/) with your GitHub account.
2. Add a new project and select the `Student-Analysis-Platform` repository.
3. In the project settings, set the **Root Directory** to `frontend`.
4. The Build Command (`npm run build`) and Output Directory (`dist`) should be auto-detected.
5. Click **Deploy**. Your frontend will be live in a few minutes.

### Deploying the Backend

You can deploy the Python FastAPI backend to services like Render or Railway.

**Using Render:**
1. Sign up on [Render](https://render.com/) with your GitHub account.
2. Click on **New** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the **Root Directory** to `backend`.
5. Set the **Environment** to `Python`.
6. Set the **Build Command** to `pip install -r requirements.txt`.
7. Set the **Start Command** to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
8. Click **Create Web Service**.

### Connecting Frontend to Backend
Once your backend is deployed, you will receive a public URL. Update the API base URL in your frontend code (or add it as an environment variable in your Vercel/Netlify dashboard) to point to the newly deployed backend URL.
