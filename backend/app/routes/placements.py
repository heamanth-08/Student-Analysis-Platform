from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Student
from app.schemas import PlacementResponse, PlacementOut

router = APIRouter()


@router.get("/placements", response_model=PlacementResponse, summary="Placement analytics")
def get_placements(
    department: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    total_students = db.query(func.count(Student.id)).scalar() or 0
    q_placed = db.query(Student).filter(Student.placed == True)
    if department:
        q_placed = q_placed.filter(Student.department.ilike(f"%{department}%"))

    placed_students_count = (
        db.query(func.count(Student.id)).filter(Student.placed == True).scalar() or 0
    )
    placement_rate = round(placed_students_count / total_students * 100, 1) if total_students else 0.0

    avg_pkg_result = (
        db.query(func.avg(Student.package_lpa))
        .filter(Student.placed == True, Student.package_lpa != None)
        .scalar()
    )
    avg_pkg = round(float(avg_pkg_result), 2) if avg_pkg_result else 0.0

    max_pkg_result = (
        db.query(func.max(Student.package_lpa))
        .filter(Student.placed == True)
        .scalar()
    )
    max_pkg = round(float(max_pkg_result), 2) if max_pkg_result else 0.0

    recent = (
        q_placed.order_by(Student.package_lpa.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    placements_out = [
        PlacementOut(
            student_id=s.student_id,
            name=s.name,
            department=s.department,
            company=s.company,
            package_lpa=s.package_lpa,
            year=s.year,
            batch=s.batch,
        )
        for s in recent
    ]

    return PlacementResponse(
        placed_students=placed_students_count,
        total_students=total_students,
        placement_rate=placement_rate,
        average_package_lpa=avg_pkg,
        highest_package_lpa=max_pkg,
        recent_placements=placements_out,
    )
