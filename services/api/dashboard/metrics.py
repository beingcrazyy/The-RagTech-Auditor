from fastapi import APIRouter
from infra.db.db_functions import get_dashboard_metrics
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/metrics")
def dashboard_metrics():
    logger.info("Fetching dashboard metrics")
    return get_dashboard_metrics()