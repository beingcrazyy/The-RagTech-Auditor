from fastapi import APIRouter, HTTPException
from services.api.models import CreateCompanyRequest
from infra.db.db_functions.company_apis_functions import insert_company
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/CreateCompany", tags=["CreateCompany"])

def generate_company_id(name: str) -> str :
    return name.lower().replace(" ", "_").strip()

@router.post("")
def create_company(request: CreateCompanyRequest):
    logger.info(f"Received request to create company: {request.company_name}")
    company_id = generate_company_id(request.company_name)

    try:
        result = insert_company(
            company_id=company_id,
            company_name=request.company_name,
            company_category=request.company_category,
            company_country=request.company_country,
            company_description=request.company_description
        )
        if not result:
             raise HTTPException(status_code=500, detail="Database insertion failed")
        logger.info(f"Company created successfully: {company_id}")
    except Exception as e:
        logger.error(f"Company creation failed for {request.company_name}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Company creation failed: {str(e)}"
        )

    return {
        "company_id": company_id,
        "message": "Company created successfully"
    }


