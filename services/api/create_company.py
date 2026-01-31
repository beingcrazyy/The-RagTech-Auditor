from fastapi import APIRouter, HTTPException
from services.api.models import CreateCompanyRequest
from infra.db.db_functions import insert_company
router = APIRouter(prefix="/CreateCompany", tags=["CreateCompany"])

def generate_company_id(name: str) -> str :
    return name.lower().replace(" ", "_")

print("CREATE COMPANY ROUTER LOADED")

@router.post("")
def create_company(request: CreateCompanyRequest):
    company_id = generate_company_id(request.company_name)
    print("company_id created")

    try:
        insert_company(
            company_id=company_id,
            company_name=request.company_name,
            company_category=request.company_category,
            company_country=request.company_country,
            company_description=request.company_description
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Company creation failed: {str(e)}"
        )

    return {
        "company_id": company_id,
        "message": "Company created successfully"
    }


