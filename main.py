"""
CampusIQ Backend  –  main.py
Run:  python main.py
API:  http://localhost:8000
Docs: http://localhost:8000/docs
"""

# ─────────────────────────────────────────────
#  Standard-library & third-party imports
# ─────────────────────────────────────────────
import os
import hashlib
import hmac
import json
import re
import uuid
from datetime import datetime, date, timedelta
from typing import Any, Optional

from fastapi import (
    FastAPI, HTTPException, Depends, status,
    Query, Path, Body,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator, model_validator
import uvicorn

# ─────────────────────────────────────────────
#  Optional JWT support  (pip install pyjwt)
# ─────────────────────────────────────────────
try:
    import jwt as _jwt          # PyJWT
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("[WARN] PyJWT not installed – auth tokens will use a simple HMAC scheme.")

# ─────────────────────────────────────────────
#  Config / secrets  (override via env vars)
# ─────────────────────────────────────────────
SECRET_KEY      = os.getenv("SECRET_KEY",      "campusiq-super-secret-change-me")
TOKEN_EXPIRE_H  = int(os.getenv("TOKEN_EXPIRE_HOURS", "8"))
FRONTEND_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]

# ─────────────────────────────────────────────
#  In-memory "database"  (replace with a real
#  DB – SQLAlchemy / SQLite / Postgres – when
#  you move to production)
# ─────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(f"{password}{SECRET_KEY}".encode()).hexdigest()

# Seed data ──────────────────────────────────

_DEPARTMENTS: list[dict] = [
    {"id": "dept-cs",   "name": "Computer Science",       "hod": "Dr. Ramesh Kumar",  "student_count": 240},
    {"id": "dept-ec",   "name": "Electronics & Comms",    "hod": "Dr. Priya Nair",    "student_count": 190},
    {"id": "dept-me",   "name": "Mechanical Engineering", "hod": "Dr. Suresh Babu",   "student_count": 175},
    {"id": "dept-ce",   "name": "Civil Engineering",      "hod": "Dr. Anitha Raj",    "student_count": 160},
    {"id": "dept-it",   "name": "Information Technology", "hod": "Dr. Vijay Kumar",   "student_count": 210},
]

_STUDENTS: list[dict] = [
    # --- CS dept ---
    {"id":"stu-001","roll":"21CS001","name":"Arjun Venkatesh",    "email":"arjun@campus.edu",  "dept_id":"dept-cs","year":3,"cgpa":8.7,"attendance":91,"batch":"2021-25","phone":"9876543210","status":"active"},
    {"id":"stu-002","roll":"21CS002","name":"Meena Subramanian",  "email":"meena@campus.edu",  "dept_id":"dept-cs","year":3,"cgpa":9.1,"attendance":88,"batch":"2021-25","phone":"9876543211","status":"active"},
    {"id":"stu-003","roll":"22CS001","name":"Kiran Prasad",       "email":"kiran@campus.edu",  "dept_id":"dept-cs","year":2,"cgpa":7.4,"attendance":76,"batch":"2022-26","phone":"9876543212","status":"active"},
    {"id":"stu-004","roll":"22CS002","name":"Divya Lakshmi",      "email":"divya@campus.edu",  "dept_id":"dept-cs","year":2,"cgpa":8.2,"attendance":83,"batch":"2022-26","phone":"9876543213","status":"active"},
    {"id":"stu-005","roll":"21CS003","name":"Ravi Shankar",       "email":"ravi@campus.edu",   "dept_id":"dept-cs","year":3,"cgpa":6.8,"attendance":68,"batch":"2021-25","phone":"9876543214","status":"active"},
    # --- EC dept ---
    {"id":"stu-006","roll":"21EC001","name":"Ananya Krishnan",    "email":"ananya@campus.edu", "dept_id":"dept-ec","year":3,"cgpa":8.5,"attendance":90,"batch":"2021-25","phone":"9876543220","status":"active"},
    {"id":"stu-007","roll":"22EC001","name":"Suresh Pillai",      "email":"suresh@campus.edu", "dept_id":"dept-ec","year":2,"cgpa":7.9,"attendance":82,"batch":"2022-26","phone":"9876543221","status":"active"},
    # --- IT dept ---
    {"id":"stu-008","roll":"21IT001","name":"Preethi Sundaram",   "email":"preethi@campus.edu","dept_id":"dept-it","year":3,"cgpa":9.3,"attendance":95,"batch":"2021-25","phone":"9876543230","status":"active"},
    {"id":"stu-009","roll":"22IT001","name":"Vikram Natarajan",   "email":"vikram@campus.edu", "dept_id":"dept-it","year":2,"cgpa":7.1,"attendance":72,"batch":"2022-26","phone":"9876543231","status":"active"},
    {"id":"stu-010","roll":"21IT002","name":"Kavitha Ramesh",     "email":"kavitha@campus.edu","dept_id":"dept-it","year":3,"cgpa":8.9,"attendance":93,"batch":"2021-25","phone":"9876543232","status":"active"},
]

_ACHIEVEMENTS: list[dict] = [
    {"id":"ach-001","student_id":"stu-001","title":"Smart India Hackathon – Winner","category":"Hackathon","date":"2024-03-15","description":"National-level winner in SIH 2024.","verified":True},
    {"id":"ach-002","student_id":"stu-002","title":"IEEE Research Paper Published","category":"Research",  "date":"2024-02-10","description":"Published in IEEE Xplore, Jan 2024.","verified":True},
    {"id":"ach-003","student_id":"stu-003","title":"NPTEL Python Certification","category":"Certification","date":"2024-01-20","description":"Scored 85% in NPTEL Python.","verified":True},
    {"id":"ach-004","student_id":"stu-008","title":"Google Summer of Code 2024","category":"Internship",  "date":"2024-05-01","description":"Selected for GSoC 2024.","verified":True},
    {"id":"ach-005","student_id":"stu-010","title":"AWS Cloud Practitioner","category":"Certification","date":"2024-04-12","description":"Certified AWS Cloud Practitioner.","verified":True},
    {"id":"ach-006","student_id":"stu-006","title":"Best Paper – ICECS 2024","category":"Research",  "date":"2024-03-28","description":"Best paper award at ICECS 2024.","verified":False},
]

_PLACEMENTS: list[dict] = [
    {"id":"plc-001","student_id":"stu-001","company":"TCS",        "role":"Software Engineer","package_lpa":7.0, "offer_date":"2024-10-01","status":"accepted"},
    {"id":"plc-002","student_id":"stu-002","company":"Infosys",    "role":"Systems Engineer", "package_lpa":6.5, "offer_date":"2024-10-05","status":"accepted"},
    {"id":"plc-003","student_id":"stu-008","company":"Google",     "role":"SWE Intern",       "package_lpa":25.0,"offer_date":"2024-09-15","status":"accepted"},
    {"id":"plc-004","student_id":"stu-010","company":"Amazon",     "role":"SDE-I",            "package_lpa":22.0,"offer_date":"2024-10-10","status":"accepted"},
    {"id":"plc-005","student_id":"stu-006","company":"Intel",      "role":"VLSI Engineer",    "package_lpa":9.5, "offer_date":"2024-10-12","status":"pending"},
    {"id":"plc-006","student_id":"stu-004","company":"Wipro",      "role":"Project Engineer", "package_lpa":5.5, "offer_date":"2024-10-20","status":"accepted"},
]

_ATTENDANCE_RECORDS: list[dict] = [
    # student_id, subject, month, percentage
    {"id":"att-001","student_id":"stu-001","subject":"OS",          "month":"2024-10","percentage":92},
    {"id":"att-002","student_id":"stu-001","subject":"DBMS",        "month":"2024-10","percentage":88},
    {"id":"att-003","student_id":"stu-003","subject":"OS",          "month":"2024-10","percentage":70},
    {"id":"att-004","student_id":"stu-003","subject":"DBMS",        "month":"2024-10","percentage":65},
    {"id":"att-005","student_id":"stu-005","subject":"Algorithms",  "month":"2024-10","percentage":62},
    {"id":"att-006","student_id":"stu-009","subject":"Web Tech",    "month":"2024-10","percentage":68},
]

_EXAMS: list[dict] = [
    {"id":"exm-001","student_id":"stu-001","subject":"OS",         "exam_type":"Internal","marks":88,"max_marks":100,"date":"2024-09-20"},
    {"id":"exm-002","student_id":"stu-001","subject":"DBMS",       "exam_type":"Internal","marks":91,"max_marks":100,"date":"2024-09-22"},
    {"id":"exm-003","student_id":"stu-002","subject":"OS",         "exam_type":"Internal","marks":94,"max_marks":100,"date":"2024-09-20"},
    {"id":"exm-004","student_id":"stu-003","subject":"OS",         "exam_type":"Internal","marks":72,"max_marks":100,"date":"2024-09-20"},
    {"id":"exm-005","student_id":"stu-005","subject":"Algorithms", "exam_type":"Internal","marks":58,"max_marks":100,"date":"2024-09-25"},
    {"id":"exm-006","student_id":"stu-008","subject":"DSA",        "exam_type":"Internal","marks":97,"max_marks":100,"date":"2024-09-18"},
]

_FACULTY: list[dict] = [
    {"id":"fac-001","name":"Dr. Ramesh Kumar", "dept_id":"dept-cs","designation":"Professor & HoD",  "email":"ramesh@campus.edu","subjects":["OS","Compiler Design"]},
    {"id":"fac-002","name":"Mrs. Saranya Devi","dept_id":"dept-cs","designation":"Assistant Professor","email":"saranya@campus.edu","subjects":["DBMS","Data Mining"]},
    {"id":"fac-003","name":"Dr. Vijay Kumar",  "dept_id":"dept-it","designation":"Professor & HoD",  "email":"vijay@campus.edu", "subjects":["Web Tech","Cloud Computing"]},
]

_USERS: list[dict] = [
    {"id":"usr-001","username":"admin",   "password_hash":_hash("admin123"),  "role":"admin",   "name":"Admin User",    "dept_id":None},
    {"id":"usr-002","username":"hod_cs",  "password_hash":_hash("hod123"),    "role":"hod",     "name":"Dr. Ramesh Kumar","dept_id":"dept-cs"},
    {"id":"usr-003","username":"faculty1","password_hash":_hash("faculty123"),"role":"faculty", "name":"Mrs. Saranya Devi","dept_id":"dept-cs"},
    {"id":"usr-004","username":"student1","password_hash":_hash("student123"),"role":"student", "name":"Arjun Venkatesh","dept_id":"dept-cs"},
]

# ─────────────────────────────────────────────
#  Token helpers
# ─────────────────────────────────────────────

def _make_token(user: dict) -> str:
    payload = {
        "sub":  user["id"],
        "role": user["role"],
        "name": user["name"],
        "exp":  (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_H)).isoformat(),
    }
    if JWT_AVAILABLE:
        return _jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    raw = json.dumps(payload, separators=(",", ":"))
    sig = hmac.new(SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    import base64
    return base64.urlsafe_b64encode(f"{raw}.{sig}".encode()).decode()


def _decode_token(token: str) -> dict:
    if JWT_AVAILABLE:
        try:
            return _jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except _jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except _jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    # Simple HMAC path
    try:
        import base64
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        raw, sig = decoded.rsplit(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError
        payload = json.loads(raw)
        if datetime.fromisoformat(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─────────────────────────────────────────────
#  FastAPI app + CORS
# ─────────────────────────────────────────────
app = FastAPI(
    title="CampusIQ API",
    version="1.0.0",
    description="Student Analysis Platform backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer_scheme = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────
#  Auth dependency
# ─────────────────────────────────────────────

def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = _decode_token(creds.credentials)
    user = next((u for u in _USERS if u["id"] == payload["sub"]), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*roles: str):
    def _dep(current: dict = Depends(get_current_user)):
        if current["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current
    return _dep


# ─────────────────────────────────────────────
#  Pydantic schemas
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class StudentCreate(BaseModel):
    roll: str
    name: str
    email: str
    dept_id: str
    year: int
    cgpa: float
    attendance: float
    batch: str
    phone: Optional[str] = None

    @field_validator("cgpa")
    @classmethod
    def cgpa_range(cls, v):
        if not (0 <= v <= 10):
            raise ValueError("CGPA must be 0–10")
        return v

    @field_validator("attendance")
    @classmethod
    def att_range(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Attendance must be 0–100")
        return v

class StudentUpdate(BaseModel):
    name:       Optional[str]   = None
    email:      Optional[str]   = None
    year:       Optional[int]   = None
    cgpa:       Optional[float] = None
    attendance: Optional[float] = None
    phone:      Optional[str]   = None
    status:     Optional[str]   = None

class AchievementCreate(BaseModel):
    student_id:  str
    title:       str
    category:    str
    date:        str
    description: Optional[str] = None
    verified:    bool = False

class PlacementCreate(BaseModel):
    student_id:  str
    company:     str
    role:        str
    package_lpa: float
    offer_date:  str
    status:      str = "pending"

class AttendanceCreate(BaseModel):
    student_id:  str
    subject:     str
    month:       str   # YYYY-MM
    percentage:  float

class ExamCreate(BaseModel):
    student_id: str
    subject:    str
    exam_type:  str
    marks:      float
    max_marks:  float = 100
    date:       str


# ─────────────────────────────────────────────
#  Helper: paginate any list
# ─────────────────────────────────────────────

def paginate(items: list, page: int, size: int) -> dict:
    total = len(items)
    start = (page - 1) * size
    return {
        "total": total,
        "page":  page,
        "size":  size,
        "pages": max(1, -(-total // size)),  # ceil div
        "items": items[start: start + size],
    }


# ═══════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════

# ── Health ───────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ── Auth ─────────────────────────────────────────────

@app.post("/api/auth/login", tags=["Auth"])
def login(body: LoginRequest):
    user = next(
        (u for u in _USERS
         if u["username"] == body.username
         and u["password_hash"] == _hash(body.password)),
        None,
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _make_token(user)
    return {
        "access_token": token,
        "token_type":   "bearer",
        "expires_in":   TOKEN_EXPIRE_H * 3600,
        "user": {
            "id":      user["id"],
            "name":    user["name"],
            "role":    user["role"],
            "dept_id": user["dept_id"],
        },
    }


@app.get("/api/auth/me", tags=["Auth"])
def me(current: dict = Depends(get_current_user)):
    return {k: v for k, v in current.items() if k != "password_hash"}


# ── Dashboard / Overview ─────────────────────────────

@app.get("/api/dashboard/overview", tags=["Dashboard"])
def dashboard_overview(current: dict = Depends(get_current_user)):
    students = _STUDENTS
    if current["role"] in ("hod", "faculty") and current["dept_id"]:
        students = [s for s in _STUDENTS if s["dept_id"] == current["dept_id"]]

    total     = len(students)
    avg_cgpa  = round(sum(s["cgpa"] for s in students) / total, 2) if total else 0
    avg_att   = round(sum(s["attendance"] for s in students) / total, 2) if total else 0
    at_risk   = sum(1 for s in students if s["attendance"] < 75 or s["cgpa"] < 6.5)
    placed    = len({p["student_id"] for p in _PLACEMENTS if p["status"] == "accepted"})

    dept_stats = []
    for dept in _DEPARTMENTS:
        ds = [s for s in _STUDENTS if s["dept_id"] == dept["id"]]
        if ds:
            dept_stats.append({
                "dept_id":   dept["id"],
                "dept_name": dept["name"],
                "students":  len(ds),
                "avg_cgpa":  round(sum(s["cgpa"] for s in ds) / len(ds), 2),
                "avg_att":   round(sum(s["attendance"] for s in ds) / len(ds), 2),
            })

    return {
        "total_students":      total,
        "average_cgpa":        avg_cgpa,
        "average_attendance":  avg_att,
        "at_risk_students":    at_risk,
        "placed_students":     placed,
        "total_achievements":  len(_ACHIEVEMENTS),
        "department_stats":    dept_stats,
    }


@app.get("/api/dashboard/trends", tags=["Dashboard"])
def dashboard_trends(current: dict = Depends(get_current_user)):
    """Monthly trend data for charts (mocked for the last 6 months)."""
    base = date.today().replace(day=1)
    months, cgpa_trend, att_trend, ach_trend = [], [], [], []
    for i in range(5, -1, -1):
        m = (base - timedelta(days=30 * i))
        label = m.strftime("%b %Y")
        months.append(label)
        cgpa_trend.append(round(7.8 + (5 - i) * 0.05 + (i % 2) * 0.1, 2))
        att_trend.append(round(82 + (5 - i) * 0.3 - (i % 3) * 0.4, 1))
        ach_trend.append(2 + i % 3)
    return {
        "labels":      months,
        "cgpa":        cgpa_trend,
        "attendance":  att_trend,
        "achievements": ach_trend,
    }


# ── Departments ───────────────────────────────────────

@app.get("/api/departments", tags=["Departments"])
def list_departments(current: dict = Depends(get_current_user)):
    return _DEPARTMENTS


@app.get("/api/departments/{dept_id}", tags=["Departments"])
def get_department(dept_id: str, current: dict = Depends(get_current_user)):
    dept = next((d for d in _DEPARTMENTS if d["id"] == dept_id), None)
    if not dept:
        raise HTTPException(404, "Department not found")
    students = [s for s in _STUDENTS if s["dept_id"] == dept_id]
    return {
        **dept,
        "students": len(students),
        "avg_cgpa": round(sum(s["cgpa"] for s in students) / len(students), 2) if students else 0,
        "avg_attendance": round(sum(s["attendance"] for s in students) / len(students), 2) if students else 0,
    }


# ── Students ─────────────────────────────────────────

@app.get("/api/students", tags=["Students"])
def list_students(
    dept_id:    Optional[str]   = Query(None),
    year:       Optional[int]   = Query(None),
    batch:      Optional[str]   = Query(None),
    search:     Optional[str]   = Query(None),
    cgpa_min:   Optional[float] = Query(None),
    cgpa_max:   Optional[float] = Query(None),
    att_min:    Optional[float] = Query(None),
    at_risk:    Optional[bool]  = Query(None),
    page:       int             = Query(1, ge=1),
    size:       int             = Query(20, ge=1, le=100),
    current:    dict            = Depends(get_current_user),
):
    items = list(_STUDENTS)

    # Scope HoD/faculty to their own dept
    if current["role"] in ("hod", "faculty") and current["dept_id"]:
        items = [s for s in items if s["dept_id"] == current["dept_id"]]

    if dept_id:
        items = [s for s in items if s["dept_id"] == dept_id]
    if year:
        items = [s for s in items if s["year"] == year]
    if batch:
        items = [s for s in items if s["batch"] == batch]
    if search:
        q = search.lower()
        items = [s for s in items if q in s["name"].lower() or q in s["roll"].lower() or q in s["email"].lower()]
    if cgpa_min is not None:
        items = [s for s in items if s["cgpa"] >= cgpa_min]
    if cgpa_max is not None:
        items = [s for s in items if s["cgpa"] <= cgpa_max]
    if att_min is not None:
        items = [s for s in items if s["attendance"] >= att_min]
    if at_risk:
        items = [s for s in items if s["attendance"] < 75 or s["cgpa"] < 6.5]

    return paginate(items, page, size)


@app.get("/api/students/{student_id}", tags=["Students"])
def get_student(student_id: str, current: dict = Depends(get_current_user)):
    stu = next((s for s in _STUDENTS if s["id"] == student_id), None)
    if not stu:
        raise HTTPException(404, "Student not found")
    return {
        **stu,
        "achievements": [a for a in _ACHIEVEMENTS if a["student_id"] == student_id],
        "placements":   [p for p in _PLACEMENTS   if p["student_id"] == student_id],
        "attendance":   [a for a in _ATTENDANCE_RECORDS if a["student_id"] == student_id],
        "exams":        [e for e in _EXAMS         if e["student_id"] == student_id],
    }


@app.post("/api/students", tags=["Students"], status_code=201)
def create_student(
    body: StudentCreate,
    current: dict = Depends(require_roles("admin", "hod")),
):
    if any(s["roll"] == body.roll for s in _STUDENTS):
        raise HTTPException(409, "Roll number already exists")
    new_id = f"stu-{str(uuid.uuid4())[:8]}"
    student = {"id": new_id, "status": "active", **body.model_dump()}
    _STUDENTS.append(student)
    return student


@app.put("/api/students/{student_id}", tags=["Students"])
def update_student(
    student_id: str,
    body: StudentUpdate,
    current: dict = Depends(require_roles("admin", "hod", "faculty")),
):
    stu = next((s for s in _STUDENTS if s["id"] == student_id), None)
    if not stu:
        raise HTTPException(404, "Student not found")
    for k, v in body.model_dump(exclude_none=True).items():
        stu[k] = v
    return stu


@app.delete("/api/students/{student_id}", tags=["Students"])
def delete_student(
    student_id: str,
    current: dict = Depends(require_roles("admin")),
):
    global _STUDENTS
    before = len(_STUDENTS)
    _STUDENTS = [s for s in _STUDENTS if s["id"] != student_id]
    if len(_STUDENTS) == before:
        raise HTTPException(404, "Student not found")
    return {"detail": "Deleted"}


# ── Achievements ─────────────────────────────────────

@app.get("/api/achievements", tags=["Achievements"])
def list_achievements(
    student_id: Optional[str] = Query(None),
    category:   Optional[str] = Query(None),
    verified:   Optional[bool]= Query(None),
    page:       int           = Query(1, ge=1),
    size:       int           = Query(20, ge=1, le=100),
    current:    dict          = Depends(get_current_user),
):
    items = list(_ACHIEVEMENTS)
    if student_id: items = [a for a in items if a["student_id"] == student_id]
    if category:   items = [a for a in items if a["category"] == category]
    if verified is not None: items = [a for a in items if a["verified"] == verified]
    return paginate(items, page, size)


@app.post("/api/achievements", tags=["Achievements"], status_code=201)
def create_achievement(
    body: AchievementCreate,
    current: dict = Depends(require_roles("admin", "hod", "faculty")),
):
    ach = {"id": f"ach-{str(uuid.uuid4())[:8]}", **body.model_dump()}
    _ACHIEVEMENTS.append(ach)
    return ach


@app.patch("/api/achievements/{ach_id}/verify", tags=["Achievements"])
def verify_achievement(
    ach_id: str,
    current: dict = Depends(require_roles("admin", "hod")),
):
    ach = next((a for a in _ACHIEVEMENTS if a["id"] == ach_id), None)
    if not ach:
        raise HTTPException(404, "Achievement not found")
    ach["verified"] = True
    return ach


@app.delete("/api/achievements/{ach_id}", tags=["Achievements"])
def delete_achievement(
    ach_id: str,
    current: dict = Depends(require_roles("admin", "hod")),
):
    global _ACHIEVEMENTS
    before = len(_ACHIEVEMENTS)
    _ACHIEVEMENTS = [a for a in _ACHIEVEMENTS if a["id"] != ach_id]
    if len(_ACHIEVEMENTS) == before:
        raise HTTPException(404, "Achievement not found")
    return {"detail": "Deleted"}


# ── Placements ───────────────────────────────────────

@app.get("/api/placements", tags=["Placements"])
def list_placements(
    student_id: Optional[str] = Query(None),
    company:    Optional[str] = Query(None),
    status:     Optional[str] = Query(None),
    dept_id:    Optional[str] = Query(None),
    page:       int           = Query(1, ge=1),
    size:       int           = Query(20, ge=1, le=100),
    current:    dict          = Depends(get_current_user),
):
    items = list(_PLACEMENTS)
    if student_id: items = [p for p in items if p["student_id"] == student_id]
    if status:     items = [p for p in items if p["status"]     == status]
    if company:    q = company.lower(); items = [p for p in items if q in p["company"].lower()]
    if dept_id:
        sid_set = {s["id"] for s in _STUDENTS if s["dept_id"] == dept_id}
        items = [p for p in items if p["student_id"] in sid_set]
    return paginate(items, page, size)


@app.get("/api/placements/stats", tags=["Placements"])
def placement_stats(current: dict = Depends(get_current_user)):
    accepted = [p for p in _PLACEMENTS if p["status"] == "accepted"]
    packages = [p["package_lpa"] for p in accepted]
    by_company: dict[str, int] = {}
    for p in accepted:
        by_company[p["company"]] = by_company.get(p["company"], 0) + 1
    return {
        "total_offers":   len(_PLACEMENTS),
        "accepted":       len(accepted),
        "highest_package": max(packages) if packages else 0,
        "average_package": round(sum(packages) / len(packages), 2) if packages else 0,
        "by_company":     by_company,
    }


@app.post("/api/placements", tags=["Placements"], status_code=201)
def create_placement(
    body: PlacementCreate,
    current: dict = Depends(require_roles("admin", "hod")),
):
    plc = {"id": f"plc-{str(uuid.uuid4())[:8]}", **body.model_dump()}
    _PLACEMENTS.append(plc)
    return plc


# ── Attendance ───────────────────────────────────────

@app.get("/api/attendance", tags=["Attendance"])
def list_attendance(
    student_id: Optional[str]  = Query(None),
    subject:    Optional[str]  = Query(None),
    month:      Optional[str]  = Query(None),
    below:      Optional[float]= Query(None, description="Filter by percentage < value"),
    page:       int            = Query(1, ge=1),
    size:       int            = Query(20, ge=1, le=100),
    current:    dict           = Depends(get_current_user),
):
    items = list(_ATTENDANCE_RECORDS)
    if student_id: items = [a for a in items if a["student_id"] == student_id]
    if subject:    items = [a for a in items if a["subject"]    == subject]
    if month:      items = [a for a in items if a["month"]      == month]
    if below is not None: items = [a for a in items if a["percentage"] < below]
    return paginate(items, page, size)


@app.post("/api/attendance", tags=["Attendance"], status_code=201)
def create_attendance(
    body: AttendanceCreate,
    current: dict = Depends(require_roles("admin", "hod", "faculty")),
):
    rec = {"id": f"att-{str(uuid.uuid4())[:8]}", **body.model_dump()}
    _ATTENDANCE_RECORDS.append(rec)
    return rec


# ── Exams / Marks ─────────────────────────────────────

@app.get("/api/exams", tags=["Exams"])
def list_exams(
    student_id: Optional[str] = Query(None),
    subject:    Optional[str] = Query(None),
    exam_type:  Optional[str] = Query(None),
    page:       int           = Query(1, ge=1),
    size:       int           = Query(20, ge=1, le=100),
    current:    dict          = Depends(get_current_user),
):
    items = list(_EXAMS)
    if student_id: items = [e for e in items if e["student_id"] == student_id]
    if subject:    items = [e for e in items if e["subject"]    == subject]
    if exam_type:  items = [e for e in items if e["exam_type"]  == exam_type]
    return paginate(items, page, size)


@app.post("/api/exams", tags=["Exams"], status_code=201)
def create_exam(
    body: ExamCreate,
    current: dict = Depends(require_roles("admin", "hod", "faculty")),
):
    rec = {"id": f"exm-{str(uuid.uuid4())[:8]}", **body.model_dump()}
    _EXAMS.append(rec)
    return rec


# ── Faculty ───────────────────────────────────────────

@app.get("/api/faculty", tags=["Faculty"])
def list_faculty(
    dept_id: Optional[str] = Query(None),
    current: dict = Depends(get_current_user),
):
    items = list(_FACULTY)
    if dept_id:
        items = [f for f in items if f["dept_id"] == dept_id]
    return items


# ── Analytics ─────────────────────────────────────────

@app.get("/api/analytics/at-risk", tags=["Analytics"])
def at_risk_students(
    dept_id:     Optional[str]  = Query(None),
    att_thresh:  float          = Query(75.0),
    cgpa_thresh: float          = Query(6.5),
    current:     dict           = Depends(get_current_user),
):
    students = list(_STUDENTS)
    if dept_id:
        students = [s for s in students if s["dept_id"] == dept_id]
    at_risk = [
        s for s in students
        if s["attendance"] < att_thresh or s["cgpa"] < cgpa_thresh
    ]
    return {
        "count":    len(at_risk),
        "students": at_risk,
    }


@app.get("/api/analytics/top-performers", tags=["Analytics"])
def top_performers(
    dept_id: Optional[str] = Query(None),
    limit:   int           = Query(5, ge=1, le=50),
    current: dict          = Depends(get_current_user),
):
    students = list(_STUDENTS)
    if dept_id:
        students = [s for s in students if s["dept_id"] == dept_id]
    top = sorted(students, key=lambda s: (s["cgpa"], s["attendance"]), reverse=True)[:limit]
    return top


@app.get("/api/analytics/cgpa-distribution", tags=["Analytics"])
def cgpa_distribution(
    dept_id: Optional[str] = Query(None),
    current: dict          = Depends(get_current_user),
):
    students = list(_STUDENTS)
    if dept_id:
        students = [s for s in students if s["dept_id"] == dept_id]
    buckets = {"<6": 0, "6–7": 0, "7–8": 0, "8–9": 0, "9–10": 0}
    for s in students:
        c = s["cgpa"]
        if c < 6:       buckets["<6"]  += 1
        elif c < 7:     buckets["6–7"] += 1
        elif c < 8:     buckets["7–8"] += 1
        elif c < 9:     buckets["8–9"] += 1
        else:           buckets["9–10"]+= 1
    return {"distribution": buckets, "total": len(students)}


@app.get("/api/analytics/attendance-distribution", tags=["Analytics"])
def attendance_distribution(
    dept_id: Optional[str] = Query(None),
    current: dict          = Depends(get_current_user),
):
    students = list(_STUDENTS)
    if dept_id:
        students = [s for s in students if s["dept_id"] == dept_id]
    buckets = {"<60": 0, "60–75": 0, "75–85": 0, "85–100": 0}
    for s in students:
        a = s["attendance"]
        if a < 60:     buckets["<60"]    += 1
        elif a < 75:   buckets["60–75"]  += 1
        elif a < 85:   buckets["75–85"]  += 1
        else:          buckets["85–100"] += 1
    return {"distribution": buckets, "total": len(students)}


# ── Research / Publications  ──────────────────────────
# (No separate model; returns Research-category achievements)

@app.get("/api/research", tags=["Research"])
def list_research(
    student_id: Optional[str] = Query(None),
    verified:   Optional[bool]= Query(None),
    page:       int           = Query(1, ge=1),
    size:       int           = Query(20, ge=1, le=100),
    current:    dict          = Depends(get_current_user),
):
    items = [a for a in _ACHIEVEMENTS if a["category"] == "Research"]
    if student_id: items = [a for a in items if a["student_id"] == student_id]
    if verified is not None: items = [a for a in items if a["verified"] == verified]
    return paginate(items, page, size)


# ═══════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("─" * 55)
    print("  CampusIQ Backend starting …")
    print(f"  Docs  → http://localhost:8000/docs")
    print(f"  CORS  → {FRONTEND_ORIGINS}")
    print("─" * 55)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
