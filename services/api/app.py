from fastapi import FastAPI
from core.graph.graph import build_graph
from core.state import AuditState
from services.api.models import StartAuditRequest

app = FastAPI(title = "The RegTech Auditor API")

graph = build_graph()

@app.post("/audit/start")

def start_audit (req : StartAuditRequest):
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



