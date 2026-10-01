# MASTER PROMPT: CONNECT THE EXISTING STITCH FRONTEND TO A PYTHON BACKEND AND PREPARE FOR DEPLOYMENT

## PROJECT CONTEXT

I already have a complete frontend UI designed using Stitch. It contains multiple screens, navigation elements, dashboards, forms, buttons, tables, charts, filters, cards, menus, toggles, and other UI components.

- DO NOT rebuild the frontend from scratch.
- DO NOT replace the existing Stitch design.
- DO NOT change the UI/UX, layout, colors, typography, spacing, components, navigation, or screen structure unless it is required for backend integration.

Your job is to take the EXISTING STITCH FRONTEND and connect it to a PYTHON BACKEND so that the entire application works end-to-end and is ready for deployment. The application must work locally first, then be deployable to production.

**Deployment target (fill in before running):** Frontend: `[e.g. Vercel / Netlify]` | Backend: `[e.g. Render / Railway]` | Database: `[e.g. Railway MySQL / PlanetScale / local MySQL]`

**Working rules for this task:**

- Before changing anything, create a Git commit or backup of the current project so the original Stitch work can be restored.
- Do not delete existing files unless absolutely necessary. If you must, tell me which file and why.
- If something is unclear (for example, business logic that is not visible in the UI), make a reasonable assumption, write it down in `README.md` under "Assumptions", and continue. Do not stop to ask unless the project cannot proceed without my answer.

---

## 1. FIRST: INSPECT THE ENTIRE EXISTING PROJECT

Before making any changes:

1. Inspect the complete project folder.
2. Identify the technology the Stitch export uses. It may be a framework project (React/Vite/Next.js) or plain HTML + Tailwind + JavaScript files. Do not assume; check.
3. Identify:
   - `package.json` (if present)
   - frontend source files
   - components
   - pages/screens
   - routing
   - assets
   - CSS/Tailwind configuration
   - environment variables
   - existing API calls
   - existing mock data
   - existing JSON/CSV/Excel files
   - charts
   - forms
   - authentication-related components
   - navigation
   - dashboard components
4. Understand how every screen is connected to the others.
5. Identify buttons and UI controls that currently use static or mock data.
6. Identify all data that must come from the backend.
7. Identify all frontend actions that need backend APIs.

DO NOT start coding the backend until you understand the existing frontend structure. Write a short plan (screens found, data needed, APIs required) before you start.

---

## 2. PRESERVE THE EXISTING FRONTEND

The existing Stitch frontend is the primary UI. Keep:

- existing screens, navigation, sidebar, and header
- existing dashboard layout and responsive design
- existing cards, charts, tables, filters, forms, and buttons
- existing light/bright theme, and the dark theme if already implemented
- existing icons, animations, and styling

Only modify frontend code when necessary to:

- connect APIs, send data to the backend, and receive responses
- display real data
- handle loading states and errors
- validate forms
- implement authentication (only if it already exists in the UI)
- implement filters, search, and sorting
- implement CRUD operations
- connect charts and dashboard statistics to real backend data

Do not redesign the interface.

---

## 3. BACKEND TECHNOLOGY

Build the backend using Python, FastAPI, and Uvicorn, with a clean REST API architecture and a modular structure (not everything in one file):

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   └── utils/
├── requirements.txt
└── .env.example
```

---

## 4. DATABASE

If the project needs persistent data, use **MySQL** with **SQLAlchemy** and the **PyMySQL** driver (connection string format: `mysql+pymysql://user:password@host:port/dbname`).

Create proper:

- database connection
- tables and models
- relationships
- CRUD operations
- validation
- error handling

Do not hard-code database credentials. Use a single environment variable:

```
DATABASE_URL=
```

Create `.env.example` with placeholder values only. Never expose real credentials in the frontend or in the GitHub repository.

If the project only needs CSV/Excel analytics with no stored records, say so in the plan and do not add a database just for the sake of it.

---

## 5. DATA FILE SUPPORT

The project may use CSV/Excel datasets. Implement backend data processing using Pandas, NumPy, and openpyxl (for Excel).

The backend must be able to:

1. Read CSV files.
2. Read Excel files.
3. Validate uploaded datasets.
4. Clean the data.
5. Handle missing values.
6. Handle incorrect values.
7. Perform the required calculations.
8. Generate analytical results.
9. Return structured JSON responses to the frontend.

Do not perform heavy data processing in the frontend.

---

## 6. API DESIGN

Create REST APIs based on the actual requirements of the existing frontend. Use appropriate HTTP methods: GET, POST, PUT, PATCH, DELETE.

Example structure (for illustration only):

```
GET    /api/dashboard
GET    /api/analytics
GET    /api/students
GET    /api/students/{id}
POST   /api/students
PUT    /api/students/{id}
DELETE /api/students/{id}
```

Do NOT blindly copy these endpoints. First inspect the frontend and determine the actual API structure. If the project has different entities, create endpoints for those.

---

## 7. CONNECT EVERY FRONTEND SCREEN

Go through every existing Stitch screen one by one. For each screen:

1. Identify what data it displays.
2. Identify whether that data is currently static or mock.
3. Identify which backend API it needs.
4. Create the API if it does not exist.
5. Connect the frontend to that API.
6. Display real backend data.
7. Add a loading state.
8. Add error handling.
9. Add empty-data handling.
10. Verify that the screen still works after a page refresh.

Do not leave any major screen using fake data unless it is intentionally static UI content.

---

## 8. CONNECT ALL BUTTONS

Audit every button in the application and determine its intended action. Examples: Add, Edit, Delete, Save, Submit, Upload, Download, Search, Filter, Reset, Refresh, View details, Generate report, Export, Login, Logout, navigation, theme toggle, Profile, Settings.

Every functional button must actually work. When a button needs the backend, the flow is:

```
Frontend → API request → FastAPI → Database / data processing → API response → Frontend state update → UI update
```

Do not leave buttons with placeholder `console.log()`, `alert()`, TODO comments, or fake success messages.

---

## 9. CONNECT FORMS

For every form:

1. Add proper frontend validation.
2. Send the data to the backend.
3. Validate the data again in FastAPI (never trust frontend validation alone).
4. Store or process the data.
5. Return a proper response.
6. Display success and error messages.
7. Update the UI without an unnecessary page refresh.

---

## 10. API CLIENT

Create one centralized frontend API client (for example `src/services/api.js`, or the equivalent for this project's structure; for plain HTML projects use a shared `js/api.js` loaded by every page).

It should contain:

- the base URL
- GET, POST, PUT/PATCH, and DELETE helpers
- authentication handling (only if authentication exists)
- common error handling

Do not scatter hard-coded backend URLs across the frontend. Read the base URL from an environment variable:

- Vite: `VITE_API_URL`
- Next.js: `NEXT_PUBLIC_API_URL`
- Plain HTML: a single `config.js` file that defines the API base URL

All calls should use `${API_URL}/api/...` and not `http://localhost:8000/...`.

---

## 11. ENVIRONMENT CONFIGURATION

Frontend `.env.example`:

```
VITE_API_URL=http://localhost:8000
```

Backend `.env.example`:

```
DATABASE_URL=
SECRET_KEY=
CORS_ORIGINS=http://localhost:5173
```

Do not commit real `.env` files containing secrets. Update `.gitignore` to exclude `.env`, `venv/`, `node_modules/`, `__pycache__/`, and uploaded files.

---

## 12. CORS

Configure FastAPI CORS correctly.

- Development: allow the actual local frontend origin (for example `http://localhost:5173` or `http://localhost:3000`).
- Production: read allowed origins from the `CORS_ORIGINS` environment variable.
- Do NOT permanently use `allow_origins=["*"]`, especially when credentials or authentication are used.

---

## 13. AUTHENTICATION

If the existing frontend contains login, signup, or user authentication, implement proper backend authentication:

- password hashing (bcrypt or argon2)
- JWT or another appropriate token mechanism
- login endpoint
- protected API routes
- token validation
- logout handling
- user session handling

Never store plain-text passwords. Never expose secret keys in frontend code.

If authentication is NOT part of the current project, do not add it.

---

## 14. DASHBOARD AND ANALYTICS

The dashboard must use real backend data. Do not hard-code numbers, percentages, charts, statistics, tables, or analytics values. The backend calculates them:

```
Database / CSV / Excel → Python → Pandas / NumPy → calculations → FastAPI → JSON → Frontend → Charts / Cards / Tables
```

Create appropriate endpoints for dashboard statistics.

---

## 15. CHARTS

Inspect every chart in the Stitch frontend and replace mock chart data with backend data. The backend should return data in the format the existing chart library expects, for example:

```json
{ "labels": [], "values": [] }
```

Do not change the chart design unless required for functionality. Charts must update when the backend data changes.

---

## 16. FILTERS AND SEARCH

Connect all existing search, filter, sorting, date-range, category, dropdown, and pagination controls to the backend where appropriate, using query parameters:

```
GET /api/students?search=abc&page=1&limit=20
```

Do not download huge datasets to the browser when server-side filtering is more appropriate.

---

## 17. FILE UPLOAD

If the frontend contains CSV/Excel upload functionality:

```
File selection → multipart/form-data → FastAPI upload endpoint → validation → Pandas/openpyxl processing → Database/storage → analytics → JSON response → Frontend update
```

Validate:

- file type and file size (set a sensible maximum)
- required columns
- invalid data
- duplicate records
- missing values

Use safe filenames, never trust the original filename, and return clear error messages. Note that many hosting platforms have temporary file storage, so store processed data in the database rather than relying on saved files.

---

## 18. STRIDE POINT FEATURE

The project contains a feature called **STRIDE POINT**. Treat it as a real functional feature, not a visual placeholder.

1. Inspect the existing Stitch frontend to see exactly how Stride Point is represented (screens, cards, tables, charts, labels, scores).
2. Work out the data, calculations, scoring rules, and storage it requires from the UI.
3. Implement the backend logic, API endpoints, and frontend connections needed to make it work.
4. Write every assumption about the scoring logic in `README.md` under "Assumptions".

Do not invent functionality that is unrelated to the existing design. The UI is the source of truth.

---

## 19. ERROR HANDLING

Backend must return proper status codes: 400, 401, 403, 404, 422, and 500. Frontend must show user-friendly messages. Never show raw Python stack traces to users. Log technical errors on the backend.

---

## 20. LOADING STATES

Every API-driven screen must have a loading state (spinner, skeleton, disabled submit button, or progress indicator). Do not allow users to submit the same request repeatedly while an operation is running.

---

## 21. EMPTY STATES

Handle cases where there is no data, for example "No records found", "No analytics available", "No uploaded dataset", or "No results match your filter". The UI must not break when API responses contain empty arrays or null values.

---

## 22. SECURITY

Follow basic production security practices. Do not expose passwords, API secrets, or database credentials. Do not commit `.env` files. Do not hard-code production credentials. Do not trust frontend validation. Do not return sensitive database information unnecessarily.

Validate all backend inputs. Use the ORM or parameterized queries. Configure trusted CORS origins.

---

## 23. API DOCUMENTATION

FastAPI automatically provides `/docs` and `/redoc`. Make sure all major endpoints have clear names, request schemas, response schemas, useful descriptions, and validation.

---

## 24. PROJECT STRUCTURE

Adapt to the existing project, aiming for a clean separation like:

```
project/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── .gitignore
```

If the existing Stitch project already has a suitable structure, keep it instead of restructuring unnecessarily.

---

## 25. LOCAL DEVELOPMENT

The complete application must run locally.

Frontend:

```
npm install
npm run dev
```

Backend:

```
python -m venv venv
```

Activate the environment:

- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

Then:

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Verify that the frontend can communicate with the backend.

---

## 26. END-TO-END TESTING

After implementation, test the application as a real user by running it in the browser. Test:

1. Opening the application
2. Navigating through every screen
3. Sidebar and header
4. Every major button
5. Forms
6. Search, filters, and sorting
7. Tables and charts
8. Data upload
9. CRUD operations
10. Stride Point
11. Dashboard
12. Page refresh
13. Invalid input
14. Empty data
15. Backend failure (backend stopped)
16. API errors
17. Responsive layout
18. Browser console
19. Backend logs

Fix all errors found. In your final report, state honestly what you actually tested and what you could not test. Never claim something works if you did not verify it.

---

## 27. NO MOCK DATA IN THE FINAL VERSION

Search the project for: mock, dummy, sample, placeholder, fake data, hard-coded statistics, TODO, console.log, and temporary API responses.

Replace them with real functionality wherever they represent data that should come from the backend. Static UI labels and intentional demo content may remain.

---

## 28. PERFORMANCE

Avoid unnecessary API calls. Use efficient database queries, pagination, appropriate caching where useful, debounced search, optimized data processing, and lazy loading where appropriate. Do not over-engineer: keep the implementation suitable for a student project that needs reliable deployment.

---

## 29. DEPLOYMENT PREPARATION

Prepare both frontend and backend for deployment.

- The frontend must use environment-based API configuration.
- The backend must listen on the platform's `PORT`. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Do not hard-code `localhost`, `127.0.0.1`, or development-only paths.
- Production configuration must come from environment variables.

Create or update: `requirements.txt`, `package.json`, `.env.example`, `.gitignore`, and `README.md` (with deployment instructions for my chosen platforms).

---

## 30. HEALTH CHECK

Create `GET /api/health` returning:

```json
{ "status": "ok" }
```

---

## 31. README

Create or update `README.md` with:

1. Project description
2. Technologies
3. Folder structure
4. Frontend setup
5. Backend setup
6. Database setup
7. Environment variables
8. Local development
9. API documentation
10. Testing
11. Deployment instructions
12. Assumptions

Keep the instructions simple enough for a student to follow.

---

## 32. DO NOT BREAK EXISTING WORK

Understand the current implementation before modifying important files. Do not delete working components unless absolutely necessary. Do not replace the entire frontend. Do not recreate the Stitch UI. Do not remove existing features. Make the minimum frontend changes necessary for backend integration.

---

## 33. IMPLEMENTATION ORDER

Follow this sequence:

1. Inspect the entire existing Stitch project.
2. Identify all frontend data and API requirements.
3. Design the backend architecture.
4. Create the FastAPI backend.
5. Connect the database / CSV / Excel processing.
6. Create the API endpoints.
7. Create the centralized frontend API client.
8. Connect the dashboard.
9. Connect analytics.
10. Connect forms.
11. Connect tables.
12. Connect charts.
13. Connect search, filter, and sort.
14. Connect file upload.
15. Connect Stride Point.
16. Connect authentication (only if already present).
17. Implement error, loading, and empty states.
18. Run complete end-to-end testing.
19. Fix all errors.
20. Prepare the production environment.
21. Prepare deployment configuration.
22. Update the README.

---

## 34. IMPORTANT DEVELOPMENT RULE

DO NOT STOP after creating the backend. The task is NOT complete until this full chain works end-to-end:

```
Stitch frontend → API client → FastAPI → Database / CSV / Excel → Python processing → FastAPI response → Frontend state → Visible UI update
```

---

## 35. FINAL VERIFICATION CHECKLIST

Before declaring the project complete, verify each item:

- [ ] Frontend starts successfully
- [ ] Backend starts successfully
- [ ] Frontend communicates with the backend
- [ ] API URLs use environment variables
- [ ] Database connection works
- [ ] CSV/Excel processing works (if required)
- [ ] Dashboard, analytics, charts, and tables use real data
- [ ] Forms and CRUD operations work
- [ ] Search, filters, and sorting work
- [ ] File upload works (if present)
- [ ] Stride Point works
- [ ] Authentication works (if present)
- [ ] Loading, empty, and error states work
- [ ] No broken buttons
- [ ] No unnecessary mock data
- [ ] No hard-coded localhost URLs in production code
- [ ] No secrets in source code
- [ ] CORS is configured
- [ ] `/api/health` works
- [ ] `/docs` works
- [ ] Browser console has no critical errors
- [ ] Backend logs have no critical errors
- [ ] Application works after page refresh
- [ ] Responsive UI still works
- [ ] Production environment configuration is ready
- [ ] README is updated

---

## FINAL INSTRUCTION

Take the existing Stitch frontend as the source of truth for the user interface. Do not redesign it. Build and integrate the FastAPI backend around the actual requirements of that frontend.

Inspect first. Understand the architecture. Implement incrementally. Connect every required feature. Test everything. Fix errors. Then prepare the application for deployment.

The final result must be a REAL WORKING FULL-STACK APPLICATION, not a UI prototype. Do not just explain what needs to be done: inspect the project, modify the files, implement the backend, connect the frontend, test the integration, and leave the project deployment-ready.

**When finished, give me a short report:** files created and changed, how to run the project, what was tested, what could not be tested, and any assumptions made.
