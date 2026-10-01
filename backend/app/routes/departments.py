from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Department
from app.schemas import DepartmentListResponse, DepartmentOut

router = APIRouter()


@router.get("/departments", response_model=DepartmentListResponse, summary="Department performance list")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return DepartmentListResponse(
        departments=[DepartmentOut.model_validate(d) for d in depts],
        total=len(depts),
    )
