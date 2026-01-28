from fastapi import FastAPI
from fastapi import APIRouter, HTTPException
from core.graph.graph import build_graph
from core.state import AuditState
from services.api.models import StartAuditRequest, CreateCompanyRequest
from services.orchestrater.bundle_ingester import enumerate_company_documents
from services.api.create_company import router as create_company_router
from services.api.add_documents import router as upload_document_router
from services.api.start_audit import router as start_audit_router
from services.api.document_audit_details import router as document_detail_router
from services.api.audit_status import router as audit_status_router

app = FastAPI(title = "The RegTech Auditor API")

graph = build_graph()

#-------------------------------------------------------------------------------------------------
# START AUDIT ON DOCUMENT BASIS API 
#-------------------------------------------------------------------------------------------------

@app.post("/audit/start")
def start_audit (req : StartAuditRequest):

    base_path = "data"

    state = AuditState(
        company_id= req.company_id,
        document_id= req.document_id
    )

    result = graph.invoke(state)

    return {
        "company_id": result["company_id"],
        "document_id": result["document_id"],
        "audit_trace": result["audit_trace"],
        "file_type": result["file_type"],
        "document_type": result["document_type"],
    }


#-------------------------------------------------------------------------------------------------
# START AUDIT ON COMPANY BASIS API
#-------------------------------------------------------------------------------------------------

@app.post("/audit/company")
def start_audit (company_name : str):
    base_path = "data"

    docs = enumerate_company_documents(company_name, base_path)

    results = []

    for i, doc in enumerate(docs[:5], start=1):
        print(f"Processing document {i}/{min(len(docs), 5)}: {doc['document_id']}")

        state = AuditState(
            company_id=doc["company_id"],
            document_id=doc["document_id"],
            file_path=doc["file_path"]
        )
        print("Initial State:", state.model_dump())

        result = graph.invoke(state)
        print("Final Result:", result)

        results.append({
            "document_id": doc["document_id"],
            "file_type": result.get("file_type"),
            "parsed_content": result.get("parsed_content"),
            "document_type": result.get("document_type"),
            "extraced_data": result.get("extraced_data"),
            "audit_trace": result.get("audit_trace"),
            "validation_results": result.get("validation_results"),
            "status": result.get("status"),
            "audit_summary": result.get("audit_summary")
        })
    
    return {
        "company_id": company_name,
        "documents_processed": len(results),
        "results": results
    }


#-------------------------------------------------------------------------------------------------
# CREATE COMPANY API
#-------------------------------------------------------------------------------------------------

app.include_router(create_company_router)


#-------------------------------------------------------------------------------------------------
# UPLOAD DOCUMENT API
#-------------------------------------------------------------------------------------------------

app.include_router(upload_document_router)

#-------------------------------------------------------------------------------------------------
# START AUDIT API
#-------------------------------------------------------------------------------------------------

app.include_router(start_audit_router)

#-------------------------------------------------------------------------------------------------
# AUDIT STATUS API
#-------------------------------------------------------------------------------------------------

app.include_router(audit_status_router)

#-------------------------------------------------------------------------------------------------
# AUDIT STATUS API
#-------------------------------------------------------------------------------------------------

app.include_router(document_detail_router)





