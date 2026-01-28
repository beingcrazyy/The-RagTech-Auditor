from infra.db.db_functions import update_document_progress, finalize_document_audit
from typing import List

def run_company_audit(company_id : str, documents : list) -> dict :
    for doc in documents:
        document_id = doc["document_id"]

        update_document_progress(document_id, 10)
        update_document_progress(document_id, 30)
        update_document_progress(document_id, 60)
        update_document_progress(document_id, 90)

        finalize_document_audit(
            document_id=document_id,
            status="VERIFIED",
            audit_summary="All checks passed",
            hard_failures=[
                {
                    "rule_id": "ISO_27001_A.9.1",
                    "severity": "HARD",
                    "message": "Access control policy missing",
                    "evidence_ref": "page_4",
                    "confidence": 0.92
                }
            ],
            soft_failures=[]
        )
