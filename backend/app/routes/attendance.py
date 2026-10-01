from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Student
from app.schemas import AttendanceResponse

router = APIRouter()


@router.get("/attendance", response_model=AttendanceResponse, summary="Attendance analytics")
def get_attendance(
    threshold: float = Query(75.0, description="Attendance threshold %"),
    db: Session = Depends(get_db),
):
    avg_att = float(db.query(func.avg(Student.attendance_percentage)).scalar() or 0.0)

    defaulters = (
        db.query(Student)
        .filter(Student.attendance_percentage < threshold)
        .order_by(Student.attendance_percentage.asc())
        .limit(50)
        .all()
    )
    below_count = (
        db.query(func.count(Student.id))
        .filter(Student.attendance_percentage < threshold)
        .scalar()
        or 0
    )

    dept_rows = (
        db.query(
            Student.department,
            func.avg(Student.attendance_percentage).label("avg_att"),
            func.count(Student.id).label("count"),
        )
        .filter(Student.attendance_percentage != None)
        .group_by(Student.department)
        .all()
    )
    dept_attendance = [
        {
            "department": row.department,
            "average_attendance": round(float(row.avg_att), 1),
            "total_students": row.count,
        }
        for row in dept_rows
    ]

    return AttendanceResponse(
        average_attendance=round(avg_att, 1),
        below_threshold_count=below_count,
        threshold=threshold,
        defaulters=defaulters,
        department_attendance=dept_attendance,
    )
