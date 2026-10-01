from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime


# ── Student schemas ───────────────────────────────────────────────────────────

class StudentBase(BaseModel):
    student_id: str
    name: str
    department: str
    year: int
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    attendance_percentage: Optional[float] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    batch: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    hostel: bool = False
    placed: bool = False
    company: Optional[str] = None
    package_lpa: Optional[float] = None


class StudentCreate(StudentBase):
    pass


class StudentOut(StudentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    students: List[StudentOut]
    total: int
    page: int
    page_size: int


# ── Department schemas ────────────────────────────────────────────────────────

class DepartmentOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    head: Optional[str] = None
    total_students: int = 0
    average_cgpa: Optional[float] = None
    average_attendance: Optional[float] = None
    placement_rate: Optional[float] = None

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    departments: List[DepartmentOut]
    total: int


# ── Dashboard schema ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_students: int
    average_cgpa: float
    placement_rate: float
    average_attendance: float
    total_departments: int
    total_achievements: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    department_performance: List[DepartmentOut]


# ── Academics schema ─────────────────────────────────────────────────────────

class AcademicsResponse(BaseModel):
    average_cgpa: float
    total_students: int
    cgpa_distribution: dict
    top_students: List[StudentOut]
    department_cgpa: List[dict]


# ── Attendance schema ────────────────────────────────────────────────────────

class AttendanceResponse(BaseModel):
    average_attendance: float
    below_threshold_count: int
    threshold: float
    defaulters: List[StudentOut]
    department_attendance: List[dict]


# ── Placement schema ─────────────────────────────────────────────────────────

class PlacementOut(BaseModel):
    student_id: str
    name: str
    department: str
    company: Optional[str] = None
    package_lpa: Optional[float] = None
    year: int
    batch: Optional[str] = None

    class Config:
        from_attributes = True


class PlacementResponse(BaseModel):
    placed_students: int
    total_students: int
    placement_rate: float
    average_package_lpa: float
    highest_package_lpa: float
    recent_placements: List[PlacementOut]


# ── Achievement schemas ──────────────────────────────────────────────────────

class AchievementCreate(BaseModel):
    student_id: str
    title: str
    category: str
    certification_name: Optional[str] = None
    issuer: Optional[str] = None
    date_achieved: Optional[str] = None
    score: Optional[float] = None
    description: Optional[str] = None


class AchievementOut(BaseModel):
    id: int
    student_id: str
    title: str
    category: str
    certification_name: Optional[str] = None
    issuer: Optional[str] = None
    date_achieved: Optional[str] = None
    score: Optional[float] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AchievementListResponse(BaseModel):
    achievements: List[AchievementOut]
    total: int


# ── Stride Points schemas ────────────────────────────────────────────────────

class StridePointCreate(BaseModel):
    student_id: str
    category: str
    activity: str
    points: int
    academic_year: str = "2024-25"
    verified: bool = True


class StridePointOut(BaseModel):
    id: int
    student_id: str
    category: str
    activity: str
    points: int
    academic_year: str
    verified: bool

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    student_id: str
    name: str
    department: str
    total_points: int
    rank: int


class StridePointsResponse(BaseModel):
    average_points: float
    highest_points: int
    highest_student: str
    leaderboard: List[LeaderboardEntry]
    category_breakdown: List[dict]


# ── Report schemas ───────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    report_type: str
    academic_year: Optional[str] = "AY 2024-25"
    department_scope: Optional[str] = "All Departments (Institutional)"


class ReportOut(BaseModel):
    id: int
    report_type: str
    academic_year: Optional[str] = None
    department_scope: Optional[str] = None
    status: str
    summary: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Upload schemas ───────────────────────────────────────────────────────────

class FileUploadResult(BaseModel):
    file_name: str
    status: str
    rows_imported: int = 0
    message: Optional[str] = None


class UploadResponse(BaseModel):
    results: List[FileUploadResult]


class UploadedFileOut(BaseModel):
    id: int
    file_name: str
    file_type: str
    rows_imported: int
    status: str
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Settings schemas ─────────────────────────────────────────────────────────

class AdminProfileOut(BaseModel):
    id: int
    full_name: str
    email: str
    institutional_role: str
    department: str
    phone: Optional[str] = None
    notifications_enabled: bool = True
    theme: str = "dark"
    language: str = "English"

    class Config:
        from_attributes = True


class AdminProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    institutional_role: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    theme: Optional[str] = None
    language: Optional[str] = None
