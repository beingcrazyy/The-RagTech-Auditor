from fastapi import APIRouter
from infra.db.db_functions import get_all_companies
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("")
def list_companies():
    logger.info("Fetching all companies")
    companies = get_all_companies()
    return companies
