from core.state import AuditState
from core.enums.file_type import FileType
from core.enums.document_type import DocumentType
from services.parser.pdf_parser import parse_pdf
from services.classifiers.heuristics import heuristics_document_classifier
from services.classifiers.llm_classifiers import llm_document_classifier
from services.extractor.invoice_extractor import extract_invoice
from core.rules.invoice_validation import validate_invoice
from core.rules.final_decision import decide_final_status
from services.audit.audit_summary_generator import generate_audit_summary
import os

BASE_PATH = "data"

def ingest_node(state: AuditState) -> dict:
    return {
        "audit_trace": state.audit_trace + ["INGEST"]
    }

def detect_file_type_node(state: AuditState) -> dict:
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

    return {
        "audit_trace" : trace,
        "file_type" : file_type
    }

def parse_pdf_node(state: AuditState) -> dict:
    if state.file_type != FileType.PDF:
        return {}
    
    trace = state.audit_trace + ["PARSE_PDF"]
    file_path = state.file_path

    result = parse_pdf(file_path)

    return {
        "audit_trace" : trace,
        "parsed_content" : result
    }


def classify_document_node(state: AuditState) -> dict:
    if state.file_type != FileType.PDF or not state.parsed_content:
        return {}
    
    text = state.parsed_content["raw_text"]

    doc_type = heuristics_document_classifier(text)

    if doc_type == DocumentType.OTHER :
        doc_type = llm_document_classifier(text)

    return {
        "audit_trace": state.audit_trace + ["CLASSIFY_DOCUMENT"],
        "document_type": doc_type
    }

def extract_invoice_node(state: AuditState) -> dict:
    if state.document_type != DocumentType.INVOICE:
        return {}

    result = extract_invoice(state.parsed_content)

    return {
        "audit_trace": state.audit_trace + ["EXTRACT_INVOICE"],
        "extraced_data": result.model_dump()
    }

def validate_invoice_node(state : AuditState) -> dict:

    if state.document_type != DocumentType.INVOICE:
        return {}
    
    validation_results = validate_invoice(state.extraced_data)

    return {
        "audit_trace": state.audit_trace + ["VALIDATE_INVOICE"],
        "validation_results": validation_results
    }

def final_decision_node(state : AuditState) -> dict:

    final_status = decide_final_status(validation_results= state.validation_results, ml_signals= state.ml_signals)

    return {
        "audit_trace": state.audit_trace + ["FINAL_DECISION"],
        "status": final_status
    }


def audit_summery_generator_node(state : AuditState) -> dict:
    
    summary = generate_audit_summary(
        status= state.status.value,
        hard_failures=state.validation_results.get("hard_failures", []),
        soft_failures=state.validation_results.get("soft_failures", []))

    return {
        "audit_trace": state.audit_trace + ["AUDIT_SUMMARY_GENERATOR"],
        "audit_summary": summary
    }

def retry_detect_file_type_node(state: AuditState) -> dict:
    return {
        "audit_trace": state.audit_trace + ["RETRY_DETECT_FILE_TYPE"],
        "retry_count": state.retry_count + 1
    }


def fail_node(state: AuditState) -> dict:
    return {
        "audit_trace": state.audit_trace + ["FAILED_EARLY"],
        "status": "FAILED"
    }