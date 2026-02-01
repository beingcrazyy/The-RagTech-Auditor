from fastapi import APIRouter
from infra.db.db_functions import get_all_companies

router = APIRouter(prefix="/audit", tags=["reports"])

@router.get("/reports")
def get_reports():
    companies = get_all_companies()
    
    reports = []
    for c in companies:
        reports.append({
            "company_id": c["company_id"],
            "company_name": c["company_name"],
            "total_documents": c["total_documents"],
            "verified": c["verified_documents"],
            "flagged": c["flagged_documents"],
            "failed": c["failed_documents"]
        })
    
    return reports
