from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from infra.db.db_functions.audit_apis_functions import override_document_status
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/companies/{company_id}/documents", tags=["human-in-loop"])

class OverrideRequest(BaseModel):
    status: str  # VERIFIED | FLAGGED | FAILED
    comment: str

@router.post("/{document_id}/override")
def override_document(company_id: str, document_id: str, payload: OverrideRequest):
    status = payload.status.upper()

    if status not in {"VERIFIED", "FLAGGED", "FAILED"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    logger.info(
        f"Human override for document {document_id}: {status} | {payload.comment}"
    )

    override_document_status(
        document_id=document_id,
        status=status,
        comment=payload.comment
    )

    return {
        "document_id": document_id,
        "status": status,
        "message": "Document status overridden successfully"
    }