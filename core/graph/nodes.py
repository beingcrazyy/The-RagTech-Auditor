from core.state import AuditState

def ingest_node(state : AuditState) -> AuditState:
    state.audit_trace.append("INGEST")
    return state

def detect_file_type_node(state : AuditState) -> AuditState:
    state.audit_trace.append("DETECT_FILE_TYPE")
    state.file_type = "PDF"
    return state


def classify_document_node(state : AuditState) -> AuditState:
    state.audit_trace.append("CLASSIFING_DOCUMENT")
    state.document_type = "INVOICE"
    state.classification_confidence = 0.89
    return state