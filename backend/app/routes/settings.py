from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminProfile
from app.schemas import AdminProfileOut, AdminProfileUpdate

router = APIRouter()


def _get_or_create_profile(db: Session) -> AdminProfile:
    profile = db.query(AdminProfile).first()
    if not profile:
        profile = AdminProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/settings/profile", response_model=AdminProfileOut, summary="Get admin profile settings")
def get_profile(db: Session = Depends(get_db)):
    return _get_or_create_profile(db)


@router.put("/settings/profile", response_model=AdminProfileOut, summary="Update admin profile settings")
def update_profile(payload: AdminProfileUpdate, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
