from fastapi import FastAPI
from core.graph.graph import build_graph
from core.state import AuditState
from services.api.models import StartAuditRequest
from services.orchestrater.bundle_ingester import enumerate_company_documents

app = FastAPI(title = "The RegTech Auditor API")

graph = build_graph()

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


@app.post("/audit/company")
def start_audit (company_name : str):
    base_path = "data"

    docs = enumerate_company_documents(company_name, base_path)

    results = []

    for doc in docs:
        state = AuditState(
            company_id= doc["company_id"],
            document_id=doc["document_id"],
            file_path=doc["file_path"]
        )

        result = graph.invoke(state)

        results.append({
                "document_id": doc["document_id"],
                "file_type": result.get("file_type"),
                "parsed_content" : result.get("parsed_content"),
                "document_type" : result.get("document_type"),
                "extraced_data" : result.get("extraced_data"),
                "audit_trace": result.get("audit_trace"),
        })
    
    return {
        "company_id": company_name,
        "documents_processed": len(results),
        "results": results
    }



