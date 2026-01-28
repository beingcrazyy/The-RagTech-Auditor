from fastapi import HTTPException, APIRouter, BackgroundTasks
from infra.db.db_functions import start_document_audit, get_documents_for_company
from services.audit.runner import run_company_audit
from datetime import datetime

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

@router.post("/start")
def start_audit(company_id : str, background_tasks : BackgroundTasks) -> dict:
    docs = get_documents_for_company(company_id)

    if not docs:
        raise HTTPException(
            status_code= 400,
            detail="No documents found for this company"
        )

    for doc in docs:
        start_document_audit(
            document_id= doc["document_id"],
            company_id=company_id
        )

    background_tasks.add_task(
        run_company_audit,
        company_id,
        docs
    )

    return {
        "company_id" : company_id,
        "message" : "Audit Started",
        "documents_queued" : len(docs)
    }


        
