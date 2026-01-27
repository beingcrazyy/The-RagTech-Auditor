from fastapi import UploadFile, APIRouter, HTTPException, File
from infra.db.db_functions import insert_document
from typing import List
import os

router = APIRouter(prefix="/companies/{company_id}/documents", tags=["documents"])

BASE_DATA_PATH = "data/companies"

def ensure_company_dir(company_id : str) -> str:
    path = os.path.join(BASE_DATA_PATH,company_id)
    os.makedirs(path, exist_ok= True)
    return path

def create_document_id(filename: str) -> str:
    return filename

@router.post("")
async def upload_documents(company_id : str, files : List[UploadFile] = File(...)):
    if not files:
        raise HTTPException (status_code= 400, detail= "No files uploaded")
    
    company_dir = ensure_company_dir(company_id)
    
    inserted= []

    for file in files:
        document_id = create_document_id(file.filename)
        filepath = os.path.join(company_dir, document_id)

        content = await file.read()
        with open (filepath, "wb") as f:
            f.write(content)

        insert_document(
            document_id=document_id,
            company_id= company_id,
            file_name=file.filename,
            file_path=filepath
            )
        
        inserted.append({
            "document_id" : document_id,
            "file_name" : file.filename
        })

        return {
            "company_id" : company_id,
            "document_inserted" : len(inserted),
            "documents" : inserted
        }

        

                           


