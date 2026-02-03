from fastapi import HTTPException, APIRouter, BackgroundTasks
from infra.db.db_functions import reset_document_audit, get_document_audit_details
from services.audit_helper.runner import run_single_document_audit

router = APIRouter(
    prefix="/companies/{company_id}/audit",
    tags=["audit"]
)

@router.post("/documents/{document_id}/retry")
def retry_audit(company_id : str, document_id : str, background_tasks : BackgroundTasks):
    audit = get_document_audit_details(company_id, document_id)

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Document audit not found"
        )
    
    reset_document_audit(company_id, document_id)

    background_tasks.add_task(
        run_single_document_audit,
        company_id,
        document_id
    )

    return {
        "company_id": company_id,
        "document_id": document_id,
        "message": "Document re-audit started"
    }


