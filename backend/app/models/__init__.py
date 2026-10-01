from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=True)
    cgpa = Column(Float, nullable=True)
    attendance_percentage = Column(Float, nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    batch = Column(String(10), nullable=True)
    section = Column(String(10), nullable=True)
    gender = Column(String(10), nullable=True)
    hostel = Column(Boolean, default=False)
    placed = Column(Boolean, default=False)
    company = Column(String(150), nullable=True)
    package_lpa = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    achievements = relationship("Achievement", back_populates="student", cascade="all, delete-orphan")
    stride_points = relationship("StridePoint", back_populates="student", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=True)
    head = Column(String(100), nullable=True)
    total_students = Column(Integer, default=0)
    average_cgpa = Column(Float, nullable=True)
    average_attendance = Column(Float, nullable=True)
    placement_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    certification_name = Column(String(200), nullable=True)
    issuer = Column(String(150), nullable=True)
    date_achieved = Column(String(20), nullable=True)
    score = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="achievements")


class StridePoint(Base):
    __tablename__ = "stride_points"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    category = Column(String(100), nullable=False)
    activity = Column(String(200), nullable=False)
    points = Column(Integer, nullable=False, default=0)
    academic_year = Column(String(10), default="2024-25")
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="stride_points")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(100), nullable=False)
    academic_year = Column(String(10), nullable=True)
    department_scope = Column(String(200), nullable=True)
    status = Column(String(30), default="completed")
    file_path = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(300), nullable=False)
    file_type = Column(String(10), nullable=False)
    rows_imported = Column(Integer, default=0)
    status = Column(String(30), default="processed")
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminProfile(Base):
    __tablename__ = "admin_profile"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), default="Dr. Evelyn Vance")
    email = Column(String(150), default="evelyn.vance@campusiq.edu")
    institutional_role = Column(String(100), default="Dean of Academic Affairs")
    department = Column(String(100), default="Office of Academic Affairs")
    phone = Column(String(20), nullable=True)
    notifications_enabled = Column(Boolean, default=True)
    theme = Column(String(20), default="dark")
    language = Column(String(20), default="English")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
