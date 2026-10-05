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
