from fastapi import FastAPI
from fastapi import APIRouter, HTTPException
from core.graph.intitialize_graph import graph
from core.state import AuditState
from services.api.models import StartAuditRequest, CreateCompanyRequest
from services.orchestrater.bundle_ingester import enumerate_company_documents
from services.api.company.create_company import router as create_company_router
from services.api.documents.upload_and_get_documents import router as upload_document_router
from services.api.audit.start_audit import router as start_audit_router
from services.api.documents.document_audit_details import router as document_detail_router
from services.api.audit.audit_status import router as audit_status_router
from services.api.authentication.auth import router as auth_router
from services.api.company.get_companies import router as get_companies_router
from services.api.audit.audit_history import router as audit_history_router
from config.logger import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from services.api.documents.view_document import router as view_document_router
from services.api.human_in_loop.override_document import router as override_router
from services.api.dashboard.metrics import router as dashboard_router
from services.api.audit.live_status import router as live_status_router

setup_logging()
app = FastAPI(title = "The RegTech Auditor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#-------------------------------------------------------------------------------------------------
# AUTHENTICATION
#-------------------------------------------------------------------------------------------------
app.include_router(auth_router)


#-------------------------------------------------------------------------------------------------
# COMPANY APIs
#-------------------------------------------------------------------------------------------------
app.include_router(create_company_router)
app.include_router(get_companies_router)


#-------------------------------------------------------------------------------------------------
# DOCUMENT APIs
#-------------------------------------------------------------------------------------------------
app.include_router(upload_document_router)
app.include_router(view_document_router)
app.include_router(document_detail_router)


#-------------------------------------------------------------------------------------------------
# AUDIT APIs
#-------------------------------------------------------------------------------------------------
app.include_router(start_audit_router)
app.include_router(live_status_router)
app.include_router(audit_status_router)
app.include_router(audit_history_router)


#-------------------------------------------------------------------------------------------------
# HUMAN IN LOOP
#-------------------------------------------------------------------------------------------------
app.include_router(override_router)


#-------------------------------------------------------------------------------------------------
# DASHBOARD
#-------------------------------------------------------------------------------------------------
app.include_router(dashboard_router)
