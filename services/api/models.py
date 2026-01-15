from pydantic import BaseModel

class StartAuditRequest(BaseModel):
    company_id : str
    document_id : str
    