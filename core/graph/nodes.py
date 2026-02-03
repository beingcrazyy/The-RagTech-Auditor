from core.state import AuditState
from core.enums.file_type import FileType
from core.enums.document_type import DocumentType
from core.enums.document_status import DocumentStatus
from services.parser.pdf_parser import parse_pdf
from services.classifiers.heuristics_document_classifier import heuristics_document_classifier
from services.classifiers.llm_document_classifiers import llm_document_classifier
from services.extractor.invoice_extractor import extract_invoice
from core.rules.invoice_validation import validate_invoice
from core.rules.final_decision import decide_final_status
from services.audit_helper.audit_summary_generator import generate_audit_summary
from infra.db.db_functions import finalize_document_audit, update_document_state
from config.logger import get_logger

logger = get_logger(__name__)

import os

BASE_PATH = "data/companies"

def ingest_node(state: AuditState) -> dict:
    logger.info(f"[{state.document_id}] Ingesting document")
    return {
        "audit_trace": state.audit_trace + ["INGEST"]
    }

def detect_file_type_node(state: AuditState) -> dict:
    logger.info(f"[{state.document_id}] Detecting file type for {state.file_path}")
    trace = state.audit_trace + ["DETECT_FILE_TYPE"]

    _,ext = os.path.splitext(state.file_path.lower())
    ext = ext.strip()

    if ext == ".pdf":
        file_type = FileType.PDF
    elif ext in {".png", ".img", ".jpeg", ".jpg"}:
        file_type = FileType.IMAGE
    elif ext in {".xlsx", ".csv"}:
        file_type = FileType.EXCEL
    else:
        file_type = FileType.OTHER

    logger.info(f"[{state.document_id}] Detected file type: {file_type.value}")
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=10,
        current_step="detecting file type..."
    )

    return {
        "audit_trace" : trace,
        "file_type" : file_type
    }

def parse_pdf_node(state: AuditState) -> dict:
    if state.file_type != FileType.PDF:
        logger.warning(f"[{state.document_id}] Skipping PDF parsing, file type is {state.file_type.value}")
        return {}
    
    logger.info(f"[{state.document_id}] Parsing PDF")
    trace = state.audit_trace + ["PARSE_PDF"]
    file_path = state.file_path

    result = parse_pdf(file_path)

    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=20,
        current_step="getting data from document"
    )

    return {
        "audit_trace" : trace,
        "parsed_content" : result
    }


def classify_document_node(state: AuditState) -> dict:
    if state.file_type != FileType.PDF or not state.parsed_content:
        logger.warning(f"[{state.document_id}] Skipping classification: insufficient data")
        return {}
    
    logger.info(f"[{state.document_id}] Classifying document")
    text = state.parsed_content["raw_text"]

    doc_type = heuristics_document_classifier(text)

    if doc_type == DocumentType.OTHER :
        logger.info(f"[{state.document_id}] Heuristics failed, using LLM classifier")
        doc_type = llm_document_classifier(text)

    logger.info(f"[{state.document_id}] Document classified as: {doc_type.value}")
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=30,
        current_step="Classifying document"
    )

    return {
        "audit_trace": state.audit_trace + ["CLASSIFY_DOCUMENT"],
        "document_type": doc_type
    }

def extract_invoice_node(state: AuditState) -> dict:
    if state.document_type != DocumentType.INVOICE:
        logger.warning(f"[{state.document_id}] Skipping invoice extraction: document type is {state.document_type.value}")
        return {}

    logger.info(f"[{state.document_id}] Extracting invoice data")
    result = extract_invoice(state.parsed_content)
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=50,
        current_step="extracting invoice"
    )

    return {
        "audit_trace": state.audit_trace + ["EXTRACT_INVOICE"],
        "extraced_data": result.model_dump()
    }

def validate_invoice_node(state : AuditState) -> dict:

    if state.document_type != DocumentType.INVOICE:
        return {}
    
    logger.info(f"[{state.document_id}] Validating invoice data")
    validation_results = validate_invoice(state.extraced_data)

    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=70,
        current_step="validating invoice"
    )

    return {
        "audit_trace": state.audit_trace + ["VALIDATE_INVOICE"],
        "validation_results": validation_results
    }

def final_decision_node(state : AuditState) -> dict:
    logger.info(f"[{state.document_id}] Making final decision")
    final_status = decide_final_status(validation_results= state.validation_results, ml_signals= state.ml_signals)
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=80,
        current_step="reviewing further"
    )

    logger.info(f"[{state.document_id}] Final decision: {final_status.value}")
    return {
        "audit_trace": state.audit_trace + ["FINAL_DECISION"],
        "status": final_status
    }


def audit_summery_generator_node(state : AuditState) -> dict:
    logger.info(f"[{state.document_id}] Generating audit summary")
    summary = generate_audit_summary(
        status= state.status.value,
        hard_failures=state.validation_results.get("hard_failures", []),
        soft_failures=state.validation_results.get("soft_failures", []))
    
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=90,
        current_step="generating audit summery"
    )

    return {
        "audit_trace": state.audit_trace + ["AUDIT_SUMMARY_GENERATOR"],
        "audit_summary": summary
    }

def retry_detect_file_type_node(state: AuditState) -> dict:
    logger.info(f"[{state.document_id}] Retrying file type detection (Retry: {state.retry_count + 1})")

    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=50,
        current_step="detecting file type"
    )

    return {
        "audit_trace": state.audit_trace + ["RETRY_DETECT_FILE_TYPE"],
        "retry_count": state.retry_count + 1
    }


def fail_node(state: AuditState) -> dict:
    logger.error(f"[{state.document_id}] Audit failed early")
    update_document_state(
        document_id=state.document_id,
        status= DocumentStatus.FAILED,
        progress=100,
        current_step="audit failed"
    )
    return {
        "audit_trace": state.audit_trace + ["FAILED_EARLY"],
        "status": "FAILED"
    }

def persist_results_node(state: AuditState) -> dict:
    logger.info(f"[{state.document_id}] Persisting results to database")
    finalize_document_audit(
        document_id=state.document_id,
        status=state.status.value,
        audit_summary=state.audit_summary,
        hard_failures=state.validation_results.get("hard_failures", []),
        soft_failures=state.validation_results.get("soft_failures", [])
    )
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=100,
        current_step="saving results..."
    )

    return {
        "audit_trace": state.audit_trace + ["PERSIST_RESULTS"]
    }

