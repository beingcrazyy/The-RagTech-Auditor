from fastapi import APIRouter, HTTPException
from infra.db.db_functions import get_document_audit_details

router = APIRouter(
    prefix="/companies/{company_id}/audit",
    tags=["audit"]
)

@router.get("/documents/{document_id}")
def document_audit_detail(company_id: str, document_id: str):

    audit = get_document_audit_details(company_id, document_id)

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found for this document"
        )

    return {
        "company_id": company_id,
        **audit
    }
