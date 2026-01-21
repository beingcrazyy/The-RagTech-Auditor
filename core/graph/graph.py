from langgraph.graph import StateGraph, END
from core.state import AuditState
from core.graph.nodes import (
    ingest_node,
    detect_file_type_node,
    retry_detect_file_type_node,
    parse_pdf_node,
    classify_document_node,
    extract_invoice_node,
    validate_invoice_node,
    final_decision_node,
    audit_summery_generator_node,
    fail_node
)

from core.enums.file_type import FileType

def build_graph():
    graph = StateGraph(AuditState)

    graph.add_node("INGEST", ingest_node )
    graph.add_node("DETECT_FILE_TYPE", detect_file_type_node)
    graph.add_node("RETRY_DETECT_FILE_TYPE",retry_detect_file_type_node)
    graph.add_node("PARSE_PDF", parse_pdf_node)
    graph.add_node("CLASSIFY_DOCUMENT", classify_document_node)
    graph.add_node("EXTRACT_INVOICE", extract_invoice_node)
    graph.add_node("VALIDATE_INVOICE", validate_invoice_node)
    graph.add_node("FINAL_DECISION", final_decision_node)
    graph.add_node("AUDIT_SUMMARY", audit_summery_generator_node)
    graph.add_node("FAIL", fail_node)
    

    graph.set_entry_point("INGEST")

    graph.add_edge("INGEST", "DETECT_FILE_TYPE")
    graph.add_conditional_edges("DETECT_FILE_TYPE",
        route_after_file_detection,
        {
            "RETRY_DETECT_FILE_TYPE": "RETRY_DETECT_FILE_TYPE",
            "PARSE_PDF": "PARSE_PDF",
            "FAIL": "FAIL",
        })
    graph.add_edge("RETRY_DETECT_FILE_TYPE", "DETECT_FILE_TYPE")
    graph.add_edge("PARSE_PDF", "CLASSIFY_DOCUMENT")
    graph.add_edge("CLASSIFY_DOCUMENT", "EXTRACT_INVOICE")
    graph.add_edge("EXTRACT_INVOICE", "VALIDATE_INVOICE")
    graph.add_edge("VALIDATE_INVOICE", "FINAL_DECISION")
    graph.add_edge("FINAL_DECISION", "AUDIT_SUMMARY")
    graph.add_edge("AUDIT_SUMMARY", END)
    graph.add_edge("FAIL", END)

    return graph.compile()

def route_after_file_detection(state : dict) -> str:
    if state.file_type ==  FileType.OTHER:
        return "FAIL"
    return "PARSE_PDF"