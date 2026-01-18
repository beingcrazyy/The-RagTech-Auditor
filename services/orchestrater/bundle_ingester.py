from typing import Dict, List
import os

SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".png", "jpg", ".jpeg", ".csv", ".img"}

def enumerate_company_documents(company_name : str, base_path : str) -> List[Dict]:

    company_path = os.path.join(base_path, company_name)
    print("company_path :", company_path)
    if not os.path.isdir(company_path) :
        raise ValueError(f"Company folder not found: {company_path}")
    
    documents = []

    for filename in os.listdir(company_path):
        print("FOUND:", repr(filename))
        file_path = os.path.join(company_path, filename)

        if not os.path.isfile(file_path):
            print("the path of {filename} is not found")
            continue

        _, ext = os.path.splitext(filename.lower())
        print(ext)
        if ext not in SUPPORTED_EXTENSIONS:
            continue

        documents.append({
            "company_id": company_name,
            "document_id": filename,
            "file_path": file_path,
        })


    return documents



