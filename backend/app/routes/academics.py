from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Student
from app.schemas import AcademicsResponse

router = APIRouter()


@router.get("/academics", response_model=AcademicsResponse, summary="Academic performance analytics")
def get_academics(db: Session = Depends(get_db)):
    total_students = db.query(func.count(Student.id)).scalar() or 0
    avg_cgpa = float(db.query(func.avg(Student.cgpa)).scalar() or 0.0)

    # CGPA distribution buckets
    all_cgpas = [r.cgpa for r in db.query(Student.cgpa).filter(Student.cgpa != None).all()]
    dist = {"<6": 0, "6-7": 0, "7-8": 0, "8-9": 0, "9+": 0}
    for c in all_cgpas:
        if c < 6:
            dist["<6"] += 1
        elif c < 7:
            dist["6-7"] += 1
        elif c < 8:
            dist["7-8"] += 1
        elif c < 9:
            dist["8-9"] += 1
        else:
            dist["9+"] += 1

    # Top 10 students by CGPA
    top_students = (
        db.query(Student)
        .filter(Student.cgpa != None)
        .order_by(Student.cgpa.desc())
        .limit(10)
        .all()
    )

    # Per-department average CGPA
    dept_rows = (
        db.query(Student.department, func.avg(Student.cgpa).label("avg_cgpa"), func.count(Student.id).label("count"))
        .filter(Student.cgpa != None)
        .group_by(Student.department)
        .all()
    )
    dept_cgpa = [
        {"department": row.department, "average_cgpa": round(float(row.avg_cgpa), 2), "total_students": row.count}
        for row in dept_rows
    ]

    return AcademicsResponse(
        average_cgpa=round(avg_cgpa, 2),
        total_students=total_students,
        cgpa_distribution=dist,
        top_students=top_students,
        department_cgpa=dept_cgpa,
    )
