from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models import Student
from app.schemas import StudentOut, StudentListResponse, StudentCreate

router = APIRouter()


@router.get("/students", response_model=StudentListResponse, summary="List students with optional filters")
def list_students(
    search: str = Query(None, description="Search by name, ID, or department"),
    department: str = Query(None),
    year: int = Query(None),
    placed: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Student)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            or_(
                Student.name.ilike(pattern),
                Student.student_id.ilike(pattern),
                Student.department.ilike(pattern),
            )
        )
    if department:
        q = q.filter(Student.department.ilike(f"%{department}%"))
    if year is not None:
        q = q.filter(Student.year == year)
    if placed is not None:
        q = q.filter(Student.placed == placed)

    total = q.count()
    students = q.offset((page - 1) * page_size).limit(page_size).all()
    return StudentListResponse(
        students=students, total=total, page=page, page_size=page_size
    )


@router.get("/students/{student_id}", response_model=StudentOut, summary="Get individual student profile")
def get_student(student_id: str, db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.student_id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return s


@router.post("/students", response_model=StudentOut, status_code=201, summary="Create a student record")
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.student_id == payload.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    s = Student(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/students/{student_id}", response_model=StudentOut, summary="Update student record")
def update_student(student_id: str, payload: StudentCreate, db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.student_id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/students/{student_id}", status_code=204, summary="Delete a student record")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.student_id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(s)
    db.commit()
