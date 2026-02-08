from fastapi import APIRouter, HTTPException
from infra.db.db_functions.audit_apis_functions import get_company_live_audit_state

router = APIRouter(
    prefix="/companies/{company_id}/audit",
    tags=["Audit Live Status"]
)

@router.get("/live")
def get_company_live_status(company_id: str):
    state = get_company_live_audit_state(company_id)

    if state["total_documents"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No audit running for this company"
        )

    return state