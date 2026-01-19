from core.state import AuditState
from core.enums.file_type import FileType
from core.enums.document_type import DocumentType
from services.parser.pdf_parser import parse_pdf
from services.classifiers.heuristics import heuristics_document_classifier
from services.classifiers.llm_classifiers import llm_document_classifier
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
    
    trace = state.audit_trace + ["PDF PARSED"]
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