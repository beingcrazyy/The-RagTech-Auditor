from fastapi import APIRouter
from infra.db.db_functions.dashboard_apis_functions import get_dashboard_metrics
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/metrics")
def dashboard_metrics():
    logger.info("Fetching dashboard metrics")
    try:
        return get_dashboard_metrics()
    except Exception as e:
        logger.error("Error fetching metrics: %s", e, exc_info=True)
        # return empty state or raise 500
        raise HTTPException(status_code=500, detail="Internal server error")