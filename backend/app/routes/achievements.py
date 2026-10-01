from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Achievement
from app.schemas import AchievementOut, AchievementListResponse, AchievementCreate

router = APIRouter()


@router.get("/achievements", response_model=AchievementListResponse, summary="List achievement records")
def list_achievements(
    category: str = Query(None),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Achievement)
    if category:
        q = q.filter(Achievement.category.ilike(f"%{category}%"))
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            Achievement.title.ilike(pattern)
            | Achievement.student_id.ilike(pattern)
            | Achievement.certification_name.ilike(pattern)
        )
    total = q.count()
    achievements = q.order_by(Achievement.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return AchievementListResponse(achievements=achievements, total=total)


@router.post("/achievements", response_model=AchievementOut, status_code=201)
def create_achievement(payload: AchievementCreate, db: Session = Depends(get_db)):
    a = Achievement(**payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
