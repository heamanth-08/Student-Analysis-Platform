from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import StridePoint, Student
from app.schemas import StridePointsResponse, StridePointCreate, StridePointOut, LeaderboardEntry

router = APIRouter()


@router.get("/stride-points", response_model=StridePointsResponse, summary="Stride Points leaderboard and analytics")
def get_stride_points(
    academic_year: str = Query("2024-25"),
    department: str = Query(None),
    db: Session = Depends(get_db),
):
    # Total points per student
    q = (
        db.query(
            StridePoint.student_id,
            func.sum(StridePoint.points).label("total_points"),
        )
        .filter(StridePoint.academic_year == academic_year)
        .group_by(StridePoint.student_id)
    )

    leaderboard_raw = q.order_by(func.sum(StridePoint.points).desc()).all()

    if not leaderboard_raw:
        return StridePointsResponse(
            average_points=0.0,
            highest_points=0,
            highest_student="N/A",
            leaderboard=[],
            category_breakdown=[],
        )

    total_pts = [row.total_points for row in leaderboard_raw]
    avg_pts = round(sum(total_pts) / len(total_pts), 1)
    max_pts = max(total_pts)

    # Build leaderboard with student details
    leaderboard = []
    for rank, row in enumerate(leaderboard_raw[:50], start=1):
        student = db.query(Student).filter(Student.student_id == row.student_id).first()
        if student:
            if department and department.lower() not in student.department.lower():
                continue
            leaderboard.append(
                LeaderboardEntry(
                    student_id=row.student_id,
                    name=student.name,
                    department=student.department,
                    total_points=row.total_points,
                    rank=rank,
                )
            )

    highest_student = leaderboard[0].name if leaderboard else "N/A"

    # Category breakdown
    cat_rows = (
        db.query(StridePoint.category, func.sum(StridePoint.points).label("total"))
        .filter(StridePoint.academic_year == academic_year)
        .group_by(StridePoint.category)
        .all()
    )
    category_breakdown = [
        {"category": row.category, "total_points": row.total}
        for row in cat_rows
    ]

    return StridePointsResponse(
        average_points=avg_pts,
        highest_points=max_pts,
        highest_student=highest_student,
        leaderboard=leaderboard,
        category_breakdown=category_breakdown,
    )


@router.post("/stride-points", response_model=StridePointOut, status_code=201, summary="Add a Stride Point record")
def add_stride_point(payload: StridePointCreate, db: Session = Depends(get_db)):
    sp = StridePoint(**payload.model_dump())
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return sp
