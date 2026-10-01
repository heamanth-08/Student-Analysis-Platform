from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Student, Department, Achievement
from app.schemas import DashboardResponse, DashboardStats, DepartmentOut

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, summary="Campus overview dashboard stats")
def get_dashboard(db: Session = Depends(get_db)):
    total_students = db.query(func.count(Student.id)).scalar() or 0
    avg_cgpa = db.query(func.avg(Student.cgpa)).scalar() or 0.0
    placed_count = db.query(func.count(Student.id)).filter(Student.placed == True).scalar() or 0
    placement_rate = round(placed_count / total_students * 100, 1) if total_students else 0.0
    avg_attendance = db.query(func.avg(Student.attendance_percentage)).scalar() or 0.0
    total_achievements = db.query(func.count(Achievement.id)).scalar() or 0

    depts = db.query(Department).all()
    total_departments = len(depts)

    stats = DashboardStats(
        total_students=total_students,
        average_cgpa=round(float(avg_cgpa), 2),
        placement_rate=float(placement_rate),
        average_attendance=round(float(avg_attendance), 1),
        total_departments=total_departments,
        total_achievements=total_achievements,
    )

    dept_out = [
        DepartmentOut(
            id=d.id,
            name=d.name,
            code=d.code,
            head=d.head,
            total_students=d.total_students or 0,
            average_cgpa=d.average_cgpa,
            average_attendance=d.average_attendance,
            placement_rate=d.placement_rate,
        )
        for d in depts
    ]

    return DashboardResponse(stats=stats, department_performance=dept_out)
