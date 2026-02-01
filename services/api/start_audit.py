from fastapi import HTTPException, APIRouter, BackgroundTasks
from infra.db.db_functions import start_document_audit, get_documents_for_company
from services.audit.runner import run_company_audit
from datetime import datetime
from core.state import AuditState
from core.graph.intitialize_graph import graph
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

@router.post("/start")
def start_audit(company_id : str) -> dict:
    logger.info(f"Starting audit for company: {company_id}")
    docs = get_documents_for_company(company_id)

    if not docs:
        logger.warning(f"No documents found for company: {company_id}")
        raise HTTPException(
            status_code= 400,
            detail="No documents found for this company"
        )

    for doc in docs:
        logger.info(f"Queueing audit for document: {doc['document_id']} (Company: {company_id})")
        start_document_audit(document_id=doc["document_id"], company_id=company_id)

        state = AuditState(
            company_id=company_id,
            document_id=doc["document_id"],
            file_path=doc["file_path"]
        )

        try:
            logger.info(f"Invoking graph for document: {doc['document_id']}")
            graph.invoke(state)
            logger.info(f"Successfully finished audit for document: {doc['document_id']}")
        except Exception as e:
            # Log but DO NOT crash the API
            logger.error(f"Audit failed for {doc['document_id']} in company {company_id}: {e}", exc_info=True)

    return {
        "company_id": company_id,
        "message": "Audit started",
        "documents_queued": len(docs)
    }


        
