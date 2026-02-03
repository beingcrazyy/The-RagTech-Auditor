from fastapi import APIRouter, HTTPException
from infra.db.db_functions import (
    get_latest_company_audit,
    get_document_audits_for_audit,
    get_company_by_id,
    update_company_audit_status
)
from services.audit_helper.audit_report_generator import generate_audit_report
from services.audit_helper.pdf_generator import render_audit_report_pdf
from services.llm.client import get_llm_client
from datetime import datetime
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/companies/{company_id}/audit",
    tags=["report"]
)

@router.post("/report/generate")
def generate_audit_report(company_id: str):
    logger.info(f"Generating audit report for company={company_id}")

    # Fetch latest audit
    audit = get_latest_company_audit(company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="No audit found for company")

    audit_id = audit["audit_id"]

    # Fetch company + document audits
    company = get_company_by_id(company_id)
    documents = get_document_audits_for_audit(audit_id)

    if not documents:
        raise HTTPException(
            status_code=400,
            detail="No document audit results found"
        )

    # Build audit context
    audit_context = {
        "audit_id": audit_id,
        "started_at": audit["started_at"],
        "completed_at": audit["completed_at"] or datetime.utcnow().isoformat()
    }

    # Generate structured report via LLM
    llm_client = get_llm_client()

    report_json = generate_audit_report(
        company=company,
        audit=audit_context,
        document_audits=documents,
        llm_client=llm_client
    )

    # 5Render PDF
    pdf_path = render_audit_report_pdf(report_json)

    # Persist report path
    update_company_audit_status(
        audit_id=audit_id,
        status="COMPLETED",
        report_path=pdf_path
    )

    return {
        "company_id": company_id,
        "audit_id": audit_id,
        "report_path": pdf_path,
        "message": "Audit report generated successfully"
    }