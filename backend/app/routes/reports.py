"""
Reports route — generate and download institutional reports.
Reports are stored in the DB with a JSON summary; download returns a CSV export.
"""

import io
import csv
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Report, Student, Achievement, StridePoint
from app.schemas import ReportCreate, ReportOut

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_report_summary(report_type: str, db: Session) -> dict:
    """Compute a JSON summary for the given report type."""
    summary = {"report_type": report_type}

    if report_type in ("Academic", "Institutional Performance"):
        avg_cgpa = float(db.query(func.avg(Student.cgpa)).scalar() or 0)
        total = db.query(func.count(Student.id)).scalar() or 0
        summary.update({"total_students": total, "average_cgpa": round(avg_cgpa, 2)})

    if report_type in ("Placement", "Institutional Performance"):
        placed = db.query(func.count(Student.id)).filter(Student.placed == True).scalar() or 0
        total = db.query(func.count(Student.id)).scalar() or 1
        avg_pkg = float(db.query(func.avg(Student.package_lpa)).filter(Student.placed == True).scalar() or 0)
        summary.update({
            "placed_students": placed,
            "placement_rate": round(placed / total * 100, 1),
            "average_package_lpa": round(avg_pkg, 2),
        })

    if report_type == "Attendance":
        avg_att = float(db.query(func.avg(Student.attendance_percentage)).scalar() or 0)
        below = db.query(func.count(Student.id)).filter(Student.attendance_percentage < 75).scalar() or 0
        summary.update({"average_attendance": round(avg_att, 1), "below_75_percent": below})

    if report_type == "Stride Points":
        total_pts = db.query(func.sum(StridePoint.points)).scalar() or 0
        participants = db.query(func.count(func.distinct(StridePoint.student_id))).scalar() or 0
        summary.update({"total_stride_points": total_pts, "participants": participants})

    return summary


def _generate_csv(report: Report, db: Session) -> str:
    """Generate a CSV string for a report."""
    output = io.StringIO()
    writer = csv.writer(output)

    rtype = report.report_type
    if rtype in ("Academic", "Institutional Performance"):
        writer.writerow(["student_id", "name", "department", "cgpa", "year"])
        students = db.query(Student).order_by(Student.cgpa.desc()).limit(200).all()
        for s in students:
            writer.writerow([s.student_id, s.name, s.department, s.cgpa, s.year])
    elif rtype == "Placement":
        writer.writerow(["student_id", "name", "department", "company", "package_lpa"])
        students = db.query(Student).filter(Student.placed == True).order_by(Student.package_lpa.desc()).limit(200).all()
        for s in students:
            writer.writerow([s.student_id, s.name, s.department, s.company, s.package_lpa])
    elif rtype == "Attendance":
        writer.writerow(["student_id", "name", "department", "attendance_percentage"])
        students = db.query(Student).order_by(Student.attendance_percentage.asc()).limit(200).all()
        for s in students:
            writer.writerow([s.student_id, s.name, s.department, s.attendance_percentage])
    elif rtype == "Stride Points":
        writer.writerow(["student_id", "category", "activity", "points", "academic_year"])
        points = db.query(StridePoint).order_by(StridePoint.points.desc()).limit(200).all()
        for sp in points:
            writer.writerow([sp.student_id, sp.category, sp.activity, sp.points, sp.academic_year])
    else:
        writer.writerow(["report_type", "generated_at"])
        writer.writerow([report.report_type, str(report.created_at)])

    return output.getvalue()


@router.get("/reports", response_model=list[ReportOut], summary="List all generated reports")
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.id.desc()).all()


@router.post("/reports/generate", response_model=ReportOut, status_code=201, summary="Generate a new report")
def generate_report(payload: ReportCreate, db: Session = Depends(get_db)):
    summary_dict = _build_report_summary(payload.report_type, db)
    report = Report(
        report_type=payload.report_type,
        academic_year=payload.academic_year,
        department_scope=payload.department_scope,
        status="completed",
        summary=json.dumps(summary_dict),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/{report_id}/download", summary="Download a report as CSV")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    csv_content = _generate_csv(report, db)
    filename = f"campusiq_report_{report.report_type.lower().replace(' ', '_')}_{report_id}.csv"
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
