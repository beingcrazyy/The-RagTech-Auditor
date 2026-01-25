from pydantic import BaseModel

class StartAuditRequest(BaseModel):
    company_id : str
    document_id : str
    
class CreateCompanyRequest(BaseModel):
    company_name: str
    description: str | None = None
    category: str
    country: str

