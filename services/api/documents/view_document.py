from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from infra.db.db_functions.document_apis_functions import get_document_file_path
import os
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/companies/{company_id}/documents",
    tags=["documents"]
)

@router.get("/{document_id}/view")
def view_document(company_id: str, document_id: str):
    logger.info(f"Viewing document {document_id} for company {company_id}")

    file_path = get_document_file_path(company_id, document_id)
    logger.info(f"File path resolved: {file_path}")

    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path)
    )