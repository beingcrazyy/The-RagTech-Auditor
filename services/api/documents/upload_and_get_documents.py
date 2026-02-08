from fastapi import UploadFile, APIRouter, HTTPException, File
from infra.db.db_functions.document_apis_functions import insert_document, get_documents_for_company
from typing import List
import os
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/companies/{company_id}/documents", tags=["documents"])

BASE_DATA_PATH = "data/companies"

@router.get("")
def list_documents(company_id: str):
    logger.info(f"Fetching documents for company: {company_id}")
    return get_documents_for_company(company_id)

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

    duplicate = 0

    for file in files:
        document_id = create_document_id(file.filename)
        filepath = os.path.join(company_dir, document_id)

        try:
            content = await file.read()
            with open (filepath, "wb") as f:
                f.write(content)

            inserted_flag = insert_document(
                document_id=document_id,
                company_id= company_id,
                file_name=file.filename,
                file_path=filepath
            )
            
            if inserted_flag:
                inserted.append({
                    "document_id": document_id,
                    "file_name": file.filename
                })
            else:
                duplicate+=1
        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {e}", exc_info=True)
            continue

    return {
        "company_id" : company_id,
        "document_inserted" : len(inserted),
        "duplicate_documents" : duplicate,
        "documents" : inserted
    }

        

                           


