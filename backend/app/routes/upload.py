"""
File upload and ingestion route.
Accepts CSV / Excel files, processes them with Pandas, and imports data
into the students table. Also returns a list of all previously uploaded files.
"""

import io
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.database import get_db
from app.models import Student, UploadedFile, Department
from app.schemas import UploadResponse, FileUploadResult, UploadedFileOut
from app.utils.helpers import is_allowed_file, safe_filename

logger = logging.getLogger(__name__)
router = APIRouter()

REQUIRED_COLUMNS = {"student_id", "name", "department", "year"}
MAX_FILE_SIZE_MB = 10


def _process_dataframe(df: pd.DataFrame, db: Session) -> tuple[int, str]:
    """Validate and import students from a DataFrame. Returns (rows_imported, message)."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return 0, f"Missing required columns: {', '.join(sorted(missing))}"

    df = df.dropna(subset=["student_id", "name"])
    imported = 0
    for _, row in df.iterrows():
        sid = str(row["student_id"]).strip()
        if not sid:
            continue
        existing = db.query(Student).filter(Student.student_id == sid).first()
        if existing:
            continue  # skip duplicates

        def safe_float(col):
            try:
                v = row.get(col)
                return float(v) if v is not None and str(v).strip() != "" else None
            except Exception:
                return None

        def safe_bool(col):
            try:
                v = row.get(col)
                if v is None:
                    return False
                return str(v).strip().lower() in {"true", "yes", "1"}
            except Exception:
                return False

        s = Student(
            student_id=sid,
            name=str(row["name"]).strip(),
            department=str(row.get("department", "Unknown")).strip(),
            year=int(float(row.get("year", 1))),
            semester=int(float(row["semester"])) if "semester" in df.columns and str(row.get("semester", "")).strip() else None,
            cgpa=safe_float("cgpa"),
            attendance_percentage=safe_float("attendance_percentage"),
            email=str(row["email"]).strip() if "email" in df.columns and str(row.get("email", "")).strip() else None,
            phone=str(row["phone"]).strip() if "phone" in df.columns and str(row.get("phone", "")).strip() else None,
            batch=str(row.get("batch", "")).strip() or None,
            section=str(row.get("section", "")).strip() or None,
            gender=str(row.get("gender", "")).strip() or None,
            hostel=safe_bool("hostel"),
            placed=safe_bool("placed"),
            company=str(row["company"]).strip() if "company" in df.columns and str(row.get("company", "")).strip() else None,
            package_lpa=safe_float("package_lpa"),
        )
        db.add(s)
        imported += 1

    if imported:
        db.commit()
    return imported, f"Imported {imported} new student records."


@router.post("/upload/files", response_model=UploadResponse, summary="Upload CSV/Excel datasets")
async def upload_files(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results: list[FileUploadResult] = []
    for upload in files:
        fname = upload.filename or "unknown"
        if not is_allowed_file(fname):
            results.append(FileUploadResult(
                file_name=fname, status="error",
                message="Only .csv, .xlsx, and .xls files are accepted."
            ))
            continue

        content = await upload.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            results.append(FileUploadResult(
                file_name=fname, status="error",
                message=f"File exceeds {MAX_FILE_SIZE_MB} MB limit."
            ))
            continue

        try:
            ext = fname.rsplit(".", 1)[-1].lower()
            if ext == "csv":
                df = pd.read_csv(io.BytesIO(content))
            else:
                df = pd.read_excel(io.BytesIO(content))

            rows_imported, msg = _process_dataframe(df, db)
            status = "success" if rows_imported > 0 else "warning"

            # Record the upload
            record = UploadedFile(
                file_name=fname,
                file_type=ext,
                rows_imported=rows_imported,
                status=status,
                message=msg,
            )
            db.add(record)
            db.commit()

            results.append(FileUploadResult(
                file_name=fname, status=status, rows_imported=rows_imported, message=msg
            ))
        except Exception as exc:
            logger.exception("Error processing file %s", fname)
            results.append(FileUploadResult(
                file_name=fname, status="error",
                message=f"Processing failed: {str(exc)[:200]}"
            ))

    return UploadResponse(results=results)


@router.get("/upload/files", response_model=list[UploadedFileOut], summary="List previously uploaded files")
def list_uploads(db: Session = Depends(get_db)):
    return db.query(UploadedFile).order_by(UploadedFile.id.desc()).all()
