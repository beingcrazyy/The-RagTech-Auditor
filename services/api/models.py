from pydantic import BaseModel

class StartAuditRequest(BaseModel):
    company_id : str
    document_id : str
    
class CreateCompanyRequest(BaseModel):
    company_name: str
    company_description: str | None = None
    company_category: str
    company_country: str

