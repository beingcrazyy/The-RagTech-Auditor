from fastapi import HTTPException, APIRouter
from infra.db.db_functions.audit_apis_functions import get_audit_status_for_company
from core.enums.audit_status import AuditStatus
from core.enums.document_results import DocumentResults

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

@router.get("/status")
def audit_status(company_id : str):
    docs = get_audit_status_for_company(company_id)

    print(type(docs), docs)

    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No audit found for this company"
        )

    total = docs["total_documents"]
    verified = docs["verified_documents"]
    failed = docs["failed_documents"]
    flagged = docs["flagged_documents"]

    return {
        "company_id": company_id,
        "summary": {
            "total_documents": total,
            "verified_documents": verified,
            "failed_documents": failed,
            "flagged_documents": flagged
        }
    }
