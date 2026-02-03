from fastapi import HTTPException, APIRouter
from infra.db.db_functions import get_audit_status_for_company

router = APIRouter(prefix="/companies/{company_id}/audit", tags=["audit"])

@router.get("/status")
def audit_status(company_id : str):
    docs = get_audit_status_for_company(company_id)

    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No audit found for this company"
        )

    # overall status
    overall_status = (
        "COMPLETED"
        if all(d["status"] == "VERIFIED" for d in docs)
        else "IN_PROGRESS"
    )

    return {
        "company_id": company_id,
        "overall_status": overall_status,
        "documents": docs
    }
