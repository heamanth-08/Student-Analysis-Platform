"""Utility helpers shared across the application."""

import re
import os
import uuid


def safe_filename(original: str) -> str:
    """Return a safe filename, preserving extension."""
    ext = os.path.splitext(original)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def is_allowed_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in {".csv", ".xlsx", ".xls"}
