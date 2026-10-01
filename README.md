# CampusIQ — Student & Campus Analytics Platform

A full-stack analytics platform for higher education institutions. Built with:

- **Frontend**: Vite + plain HTML + Tailwind CSS (CDN) — exported from Google Stitch
- **Backend**: Python 3.12+, FastAPI, Uvicorn
- **Database**: SQLite (local dev) / MySQL (production)
- **Data processing**: Pandas, NumPy, openpyxl

---

## Folder Structure

```
CA/
├── stitch_campusiq_analytics_platform_prototype/  ← Vite frontend
│   ├── campus_overview_dashboard/code.html
│   ├── students_directory/code.html
│   ├── academic_performance_analytics/code.html
│   ├── attendance_analytics/code.html
│   ├── placement_analytics/code.html
│   ├── department_performance/code.html
│   ├── stride_points_hub/code.html
│   ├── student_achievements/code.html
│   ├── certifications_internships/code.html
│   ├── research_publications/code.html
│   ├── data_upload_ingestion/code.html
│   ├── reports_export_studio/code.html
│   ├── settings/code.html
│   ├── student_profile_aarav_sharma/code.html
│   ├── src/screen-integration.js
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

---

## Frontend Setup

```bash
cd stitch_campusiq_analytics_platform_prototype
npm install
cp .env.example .env
# .env already points to http://localhost:8000 — no changes needed for local dev
npm run dev
```

Open: http://localhost:5173

---

## Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env if you want MySQL; leave as-is for SQLite (local dev)

# Start the backend
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs
Health check: http://localhost:8000/api/health

---

## Database Setup

### Local Development (SQLite — no setup needed)

Leave `DATABASE_URL` unset in `.env`. The backend automatically uses `campusiq.db`
in the `backend/` directory. The database and tables are created on first start,
and 200 sample students are seeded automatically.

### Production (MySQL)

```
DATABASE_URL=mysql+pymysql://user:password@host:3306/campusiq
```

Create the database first:
```sql
CREATE DATABASE campusiq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then start the backend — tables and seed data are created automatically.

---

## Environment Variables

### Frontend (`stitch_campusiq_analytics_platform_prototype/.env`)

| Variable | Example | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL |

### Backend (`backend/.env`)

| Variable | Example | Description |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://root:pw@localhost:3306/campusiq` | Leave blank for SQLite |
| `SECRET_KEY` | `change-me-long-random` | JWT / app secret |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |

---

## API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/dashboard` | GET | Dashboard stats + department performance |
| `/api/students` | GET | List students (search, filter, paginate) |
| `/api/students/{id}` | GET | Student profile |
| `/api/students` | POST | Create student |
| `/api/students/{id}` | PUT | Update student |
| `/api/students/{id}` | DELETE | Delete student |
| `/api/academics` | GET | Academic analytics |
| `/api/attendance` | GET | Attendance analytics |
| `/api/placements` | GET | Placement analytics |
| `/api/departments` | GET | Department list |
| `/api/achievements` | GET | Achievements (filter by category) |
| `/api/achievements` | POST | Add achievement |
| `/api/stride-points` | GET | Stride Points leaderboard |
| `/api/stride-points` | POST | Add stride point |
| `/api/upload/files` | POST | Upload CSV/Excel dataset |
| `/api/upload/files` | GET | List uploaded files |
| `/api/reports` | GET | List reports |
| `/api/reports/generate` | POST | Generate a report |
| `/api/reports/{id}/download` | GET | Download report as CSV |
| `/api/settings/profile` | GET | Admin profile |
| `/api/settings/profile` | PUT | Update admin profile |

Interactive docs: http://localhost:8000/docs

---

## Testing

1. Start backend (`uvicorn app.main:app --reload` in `backend/`)
2. Start frontend (`npm run dev` in `stitch_campusiq_analytics_platform_prototype/`)
3. Open http://localhost:5173 in the browser
4. Each screen shows a "Live backend data" panel that confirms the API connection
5. Navigate through all 14 screens and verify data loads

---

## Deployment

### Frontend (Vercel / Netlify)

1. Set environment variable: `VITE_API_BASE_URL=https://your-backend.onrender.com`
2. Build command: `npm run build`
3. Publish directory: `dist/`

### Backend (Render / Railway)

1. Set environment variables:
   - `DATABASE_URL=mysql+pymysql://...`
   - `SECRET_KEY=your-secret-key`
   - `CORS_ORIGINS=https://your-frontend.vercel.app`
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Assumptions

1. **No authentication**: The current Stitch UI has no login/signup screens. Authentication
   has not been implemented as per the master prompt instruction (only add auth if it
   already exists in the UI).

2. **Stride Points scoring**: Points are stored per activity (each row). Total per student
   is computed by summing all rows. Categories: Academic Excellence, Extracurricular,
   Research & Innovation, Community Service, Leadership, Sports.
   Point values range from 5 to 50 per activity (seeded). Admins can add points via the API.

3. **Research Publications**: The UI fetches from `/api/achievements` and filters client-side
   for rows where title/category contains "research/publication/journal/paper". A dedicated
   `/api/research` endpoint was not added since the existing screen-integration.js handles
   this filtering pattern.

4. **Certifications & Internships**: The backend serves certifications from `/api/achievements?category=Certifications`.
   A separate internships table was not created because the UI shows no internship-specific
   data entry form; only the certifications tab is connected to the backend.

5. **Student profiles**: The profile screen is for viewing only (no edit form in the current UI).
   URL format: `student_profile_aarav_sharma/code.html?student_id=CSE20241001`

6. **File upload**: Uploads are expected to have columns: `student_id, name, department, year`.
   Optional columns: `cgpa, attendance_percentage, email, phone, batch, section, gender,
   hostel, placed, company, package_lpa`. Duplicate student IDs are silently skipped.

7. **Reports**: Reports are generated from live database queries and downloaded as CSV files.
   No PDF generation is implemented (not specified in the UI).

8. **Sample data**: 200 students seeded on first startup across 5 departments with
   realistic but randomly generated values.
