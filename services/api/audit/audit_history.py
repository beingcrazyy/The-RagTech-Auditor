from fastapi import APIRouter
from infra.db.db_functions.audit_apis_functions import get_company_audit_history
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/companies/{company_id}/history", tags=["audit-history"])

@router.get("")
def get_audit_history(company_id: str):
    logger.info(f"Fetching audit history for company: {company_id}")
    return get_company_audit_history(company_id)
