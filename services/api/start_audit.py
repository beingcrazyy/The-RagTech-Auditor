from fastapi import HTTPException, APIRouter, BackgroundTasks
from infra.db.db_functions import start_document_audit, get_documents_for_company, create_company_audit_record
from services.audit.runner import run_company_audit
from datetime import datetime
from core.state import AuditState
from core.graph.intitialize_graph import graph
from config.logger import get_logger
import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

def run_audit_background(company_id: str, docs: list):
    logger.info(f"Starting background audit for company: {company_id}")
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
            logger.error(f"Audit failed for {doc['document_id']} in company {company_id}: {e}", exc_info=True)

@router.post("/start")
def start_audit(company_id : str, background_tasks: BackgroundTasks) -> dict:
    logger.info(f"Received audit request for company: {company_id}")
    docs = get_documents_for_company(company_id)

    if not docs:
        logger.warning(f"No documents found for company: {company_id}")
        raise HTTPException(
            status_code= 400,
            detail="No documents found for this company"
        )
    
    # Create an audit history record
    audit_id = f"audit_{uuid.uuid4().hex[:8]}"
    create_company_audit_record(audit_id, company_id)

    background_tasks.add_task(run_audit_background, company_id, docs)

    return {
        "company_id": company_id,
        "audit_id": audit_id,
        "message": "Audit started in background",
        "documents_queued": len(docs)
    }


        
