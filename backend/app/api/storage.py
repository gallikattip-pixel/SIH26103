"""Storage API routes for document upload, download, and deletion."""

import os
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse

from app.config import (
    RATE_LIMIT_DOC_DELETE_LIMIT,
    RATE_LIMIT_DOC_DELETE_WINDOW,
    RATE_LIMIT_UPLOAD_LIMIT,
    RATE_LIMIT_UPLOAD_WINDOW,
    UPLOAD_DIR,
)
from app.core.rate_limiter import apply_rate_limit
from app.core.security import UserRole, require_roles
from app.models.project import DocumentRecord
from app.services.storage_service import (
    get_document_metadata,
    remove_document,
    save_uploaded_document,
)

router = APIRouter(tags=["storage"])


@router.post(
    "/projects/{project_id}/documents/upload",
    response_model=DocumentRecord,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: str,
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    current_user: dict[str, Any] = Depends(require_roles([UserRole.ADMIN, UserRole.OFFICER])),
) -> DocumentRecord:
    """
    Upload a document for a project.
    Stores file in Cloud Storage (or local storage), records metadata in Firebase RTDB.
    Synchronous disk and Firebase operations are offloaded outside the asyncio event loop via threadpool.
    Requires ADMIN or OFFICER role (401 unauthenticated, 403 viewer).
    Persists authenticated caller's Firebase UID as uploaded_by_uid.
    Rate-limited by user identity (10 uploads / 60s, 50MB / 60s).
    """
    uploader_uid = current_user.get("uid")
    if not uploader_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated token missing user identity.",
        )

    # Rate limit check: Upload count (10 uploads / 60s)
    apply_rate_limit(
        request=request,
        response=response,
        scope="doc_upload_count",
        identity=f"user:{uploader_uid}",
        limit=RATE_LIMIT_UPLOAD_LIMIT,
        window_seconds=RATE_LIMIT_UPLOAD_WINDOW,
    )

    return await save_uploaded_document(
        project_id=project_id,
        file=file,
        title=title,
        uploader_uid=uploader_uid,
    )


@router.delete("/projects/{project_id}/documents/{document_id}")
def delete_document(
    project_id: str,
    document_id: str,
    request: Request,
    response: Response,
    current_user: dict[str, Any] = Depends(require_roles([UserRole.ADMIN, UserRole.OFFICER])),
) -> dict:
    """
    Delete document metadata and storage reference with IDOR protection.
    Rules:
    - ADMIN may delete any document.
    - OFFICER may delete ONLY documents where uploaded_by_uid matches their UID.
    - If document has no uploaded_by_uid (legacy): OFFICER is rejected with 403; ADMIN is allowed.
    - VIEWER is rejected with 403.
    - UNAUTHENTICATED is rejected with 401.
    - Rate-limited by user identity (20 deletes / 60s).
    """
    user_uid = current_user.get("uid")
    if user_uid:
        apply_rate_limit(
            request=request,
            response=response,
            scope="doc_delete",
            identity=f"user:{user_uid}",
            limit=RATE_LIMIT_DOC_DELETE_LIMIT,
            window_seconds=RATE_LIMIT_DOC_DELETE_WINDOW,
        )
    clean_id = project_id.strip().upper()
    doc_meta = get_document_metadata(clean_id, document_id)
    if not doc_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found for project '{clean_id}'.",
        )

    user_role = current_user.get("role")
    user_uid = current_user.get("uid")
    doc_owner = doc_meta.get("uploaded_by_uid")

    if user_role != UserRole.ADMIN.value:
        # Officer: Must own document. Missing ownership fails closed (403).
        if not doc_owner or doc_owner != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Officers may only delete documents they uploaded.",
            )

    success = remove_document(clean_id, document_id)
    return {"status": "deleted" if success else "not_found", "document_id": document_id}


@router.get("/api/storage/files/{filename}")
def get_stored_file(filename: str):
    """Serve uploaded document file with strict canonical path containment."""
    # 1. Strip raw directory separators from the parameter
    clean_filename = Path(filename).name

    # 2. Resolve canonical upload directory
    resolved_upload_dir = UPLOAD_DIR.resolve()

    # 3. Resolve target file path canonically
    target_path = (resolved_upload_dir / clean_filename).resolve()

    # 4. Strict canonical containment check
    if not target_path.is_relative_to(resolved_upload_dir):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path or directory traversal detected.",
        )

    # 5. Verify physical existence
    if not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage server.",
        )

    return FileResponse(target_path)
