from core.state import AuditState

def ingest_node(state: AuditState) -> dict:
    return {
        "audit_trace": state.audit_trace + ["INGEST"]
    }

def detect_file_type_node(state: AuditState) -> dict:
    trace = state.audit_trace + ["DETECT_FILE_TYPE"]

    if state.retry_count == 0:
        return {
            "audit_trace": trace,
            "file_type": None
        }

    return {
        "audit_trace": trace,
        "file_type": "PDF"
    }

def classify_document_node(state: AuditState) -> dict:
    return {
        "audit_trace": state.audit_trace + ["CLASSIFY_DOCUMENT"],
        "document_type": "INVOICE",
        "classification_confidence": 0.99
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