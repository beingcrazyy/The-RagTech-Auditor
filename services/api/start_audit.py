from fastapi import HTTPException, APIRouter, BackgroundTasks
from infra.db.db_functions import start_document_audit, get_documents_for_company
from services.audit.runner import run_company_audit
from datetime import datetime
from core.state import AuditState
from core.graph.intitialize_graph import graph

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

@router.post("/start")
def start_audit(company_id : str) -> dict:
    docs = get_documents_for_company(company_id)

    if not docs:
        raise HTTPException(
            status_code= 400,
            detail="No documents found for this company"
        )

    for doc in docs:
        start_document_audit(document_id=doc["document_id"], company_id=company_id)

        state = AuditState(
            company_id=company_id,
            document_id=doc["document_id"],
            file_path=doc["file_path"]
        )

        try:
            graph.invoke(state)
        except Exception as e:
            # Log but DO NOT crash the API
            print(f"Audit failed for {doc['document_id']}: {e}")

    return {
        "company_id": company_id,
        "message": "Audit started",
        "documents_queued": len(docs)
    }


        
