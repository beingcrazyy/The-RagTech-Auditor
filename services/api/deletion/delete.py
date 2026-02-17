from fastapi import APIRouter, HTTPException
from infra.db.db_functions.delete_functions import (
    delete_company,
    delete_documents_by_company,
    delete_document_by_id
)

router = APIRouter(prefix="/delete", tags=["Delete"])

@router.delete("/company/{company_id}")
def remove_company(company_id: str):
    try:
        delete_company(company_id)
        return {"message": "Company deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{company_id}")
def remove_documents(company_id: str):
    try:
        delete_documents_by_company(company_id)
        return {"message": "Documents deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/document/{document_id}")
def remove_document(document_id: str):
    deleted = delete_document_by_id(document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}