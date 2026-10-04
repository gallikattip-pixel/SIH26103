"""Cloud document storage and metadata service."""

from datetime import datetime
import io
import logging
from pathlib import Path
import uuid
import zipfile
from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.config import (
    MAX_FILE_SIZE_MB,
    RATE_LIMIT_UPLOAD_MAX_MB,
    RATE_LIMIT_UPLOAD_WINDOW,
    UPLOAD_DIR,
)
from app.core.rate_limiter import apply_rate_limit
from app.models.project import DocumentRecord
from app.services.firebase_service import (
    delete_document_from_firebase,
    get_document_from_firebase,
    save_document_to_firebase,
)

logger = logging.getLogger("infraplus.storage")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".png", ".jpg", ".jpeg"}

# Obvious executable / script signatures to reject immediately
DANGEROUS_SIGNATURES = [
    b"MZ",           # Windows PE executable / DLL
    b"\x7fELF",      # Linux executable binary
    b"#!",           # Unix shell script shebang
    b"<?php",        # PHP script
    b"<script",      # HTML/JS embedded script
    b"<!DOCTYPE html", # Raw HTML
    b"<html",        # Raw HTML
]


def validate_document_content(contents: bytes, ext: str):
    """
    Validate binary content, magic bytes, and internal structures.
    Rejects disguised executables, scripts, and content mismatches (HTTP 400).
    """
    # 1. Reject obvious executable / script headers
    for sig in DANGEROUS_SIGNATURES:
        if contents.startswith(sig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security violation: Executable or script content detected ({sig.decode('ascii', errors='ignore')}).",
            )

    # 2. Format-specific magic-byte verification
    if ext == ".pdf":
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file: Missing '%PDF-' binary signature.",
            )
    elif ext == ".png":
        if not contents.startswith(b"\x89PNG\r\n\x1a\n"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PNG file: Missing PNG binary signature.",
            )
    elif ext in (".jpg", ".jpeg"):
        if not contents.startswith(b"\xff\xd8\xff"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JPEG file: Missing JPEG binary signature.",
            )
    elif ext in (".docx", ".xlsx"):
        # Both are ZIP-based OpenXML packages starting with PK\x03\x04
        if not contents.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {ext.upper()} file: Not a valid ZIP container.",
            )
        try:
            with zipfile.ZipFile(io.BytesIO(contents)) as zf:
                namelist = zf.namelist()
                if ext == ".docx":
                    # Must contain word/ directory or document.xml
                    if not any("word/" in name for name in namelist):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid DOCX file: Archive missing Word document structure.",
                        )
                elif ext == ".xlsx":
                    # Must contain xl/ directory or workbook.xml
                    if not any("xl/" in name for name in namelist):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid XLSX file: Archive missing Excel workbook structure.",
                        )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Corrupted or invalid {ext.upper()} ZIP package.",
            )
    elif ext == ".doc":
        # Legacy Microsoft Word 97-2003 Compound File Binary format (OLE CFBF)
        ole_signature = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        if not contents.startswith(ole_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid legacy DOC file: Missing Compound File Binary signature.",
            )


def _persist_document_sync(
    clean_id: str,
    doc_id: str,
    filename: str,
    safe_filename: str,
    contents: bytes,
    content_type: str | None,
    title: str | None,
    uploader_uid: str | None,
    size_bytes: int,
) -> DocumentRecord:
    """
    Synchronously write document to storage and record metadata in Firebase.
    Executed in a worker thread via run_in_threadpool to keep the event loop non-blocking.
    Rolls back (unlinks) local storage file if Firebase metadata persistence fails.
    """
    download_url = None
    target_path = None

    # Try uploading to Firebase Storage if Firebase Admin storage is configured
    try:
        from firebase_admin import storage
        bucket = storage.bucket()
        blob = bucket.blob(f"documents/{clean_id}/{safe_filename}")
        blob.upload_from_string(contents, content_type=content_type)
        blob.make_public()
        download_url = blob.public_url
        logger.info(f"Uploaded {filename} to Firebase Storage.")
    except Exception as exc:
        logger.info(f"Firebase Storage upload bypassed/unavailable: {exc}. Storing locally.")

    # Local storage fallback for file persistence
    if not download_url:
        target_path = UPLOAD_DIR / safe_filename
        with open(target_path, "wb") as f:
            f.write(contents)
        download_url = f"/api/storage/files/{safe_filename}"

    doc_data = {
        "id": doc_id,
        "project_id": clean_id,
        "filename": filename,
        "title": title or filename,
        "file_type": content_type or "application/octet-stream",
        "file_size_kb": round(size_bytes / 1024.0, 1),
        "uploaded_at": datetime.now().isoformat(),
        "download_url": download_url,
        "uploaded_by_uid": uploader_uid,
    }

    # Save metadata in Firebase Realtime Database
    saved = False
    try:
        saved = save_document_to_firebase(clean_id, doc_id, doc_data)
    except Exception as exc:
        logger.error(f"Error persisting document metadata to Firebase: {exc}")
        saved = False

    if not saved:
        # Rollback: delete newly created local file if it was created
        if target_path and target_path.is_file():
            try:
                target_path.unlink(missing_ok=True)
                logger.info(f"Rolled back local file {target_path} after Firebase metadata persistence failure.")
            except Exception as cleanup_err:
                logger.warning(f"Failed to delete local file during rollback: {cleanup_err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to persist document metadata to database.",
        )

    return DocumentRecord(**doc_data)


async def save_uploaded_document(
    project_id: str,
    file: UploadFile,
    title: str | None = None,
    uploader_uid: str | None = None,
) -> DocumentRecord:
    """Validate, store document, and record metadata with ownership in Firebase."""
    clean_id = project_id.strip().upper()
    raw_filename = file.filename or "document.pdf"
    filename = Path(raw_filename).name
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' is not permitted. Permitted types: PDF, DOCX, DOC, XLSX, PNG, JPG.",
        )

    # Safe filename stem length bound (<= 64 chars) to prevent Windows MAX_PATH violations
    clean_stem = Path(filename).stem[:64]
    filename = f"{clean_stem}{ext}"

    # Read content to verify size and content integrity
    contents = await file.read()
    size_bytes = len(contents)
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB.",
        )

    # Validate content magic bytes and structure
    validate_document_content(contents, ext)

    # Enforce aggregate upload volume rate limit (50 MB / 60s per user)
    if uploader_uid:
        max_volume_bytes = RATE_LIMIT_UPLOAD_MAX_MB * 1024 * 1024
        apply_rate_limit(
            request=None,
            response=None,
            scope="doc_upload_volume",
            identity=f"user:{uploader_uid}",
            limit=999999,
            window_seconds=RATE_LIMIT_UPLOAD_WINDOW,
            bytes_cost=size_bytes,
            max_bytes=max_volume_bytes,
        )

    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    safe_filename = f"{clean_id}_{doc_id}_{filename}"

    # Offload synchronous disk I/O and Firebase database mutations to worker threadpool
    return await run_in_threadpool(
        _persist_document_sync,
        clean_id=clean_id,
        doc_id=doc_id,
        filename=filename,
        safe_filename=safe_filename,
        contents=contents,
        content_type=file.content_type,
        title=title,
        uploader_uid=uploader_uid,
        size_bytes=size_bytes,
    )


def get_document_metadata(project_id: str, doc_id: str) -> dict | None:
    """Fetch document metadata from Firebase for IDOR authorization checks."""
    clean_id = project_id.strip().upper()
    return get_document_from_firebase(clean_id, doc_id)


def remove_document(project_id: str, doc_id: str) -> bool:
    """Remove document metadata and file."""
    clean_id = project_id.strip().upper()
    file_removed = False

    # Remove matching local file from UPLOAD_DIR if stored locally
    prefix = f"{clean_id}_{doc_id}_"
    try:
        for f in UPLOAD_DIR.glob(f"{prefix}*"):
            if f.is_file():
                f.unlink(missing_ok=True)
                file_removed = True
                logger.info(f"Removed local document file: {f.name}")
    except Exception as exc:
        logger.warning(f"Error removing local file for {doc_id}: {exc}")

    fb_deleted = delete_document_from_firebase(clean_id, doc_id)

    return file_removed or fb_deleted or True
