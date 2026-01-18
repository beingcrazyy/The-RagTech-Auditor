from langgraph.graph import StateGraph, END
from core.state import AuditState
from core.graph.nodes import (
    ingest_node,
    detect_file_type_node,
    retry_detect_file_type_node,
    classify_document_node,
    fail_node
)

def build_graph():
    graph = StateGraph(AuditState)

    graph.add_node("INGEST", ingest_node )
    graph.add_node("DETECT_FILE_TYPE", detect_file_type_node)
    graph.add_node("RETRY_DETECT_FILE_TYPE",retry_detect_file_type_node)
    graph.add_node("CLASSIFY_DOCUMENT", classify_document_node)
    graph.add_node("FAIL", fail_node)

    graph.set_entry_point("INGEST")

    graph.add_edge("INGEST", "DETECT_FILE_TYPE")
    graph.add_conditional_edges("DETECT_FILE_TYPE",
        route_after_file_detection,
        {
            "RETRY_DETECT_FILE_TYPE": "RETRY_DETECT_FILE_TYPE",
            "CLASSIFY_DOCUMENT": "CLASSIFY_DOCUMENT",
            "FAIL": "FAIL",
        })
    graph.add_edge("RETRY_DETECT_FILE_TYPE", "DETECT_FILE_TYPE")
    graph.add_edge("CLASSIFY_DOCUMENT", END)
    graph.add_edge("FAIL", END)

    return graph.compile()

def route_after_file_detection(state : dict) -> str:
    if state.file_type is None :
        if state.retry_count < 1:
            return "RETRY_DETECT_FILE_TYPE"
        return "FAIL"
    return "CLASSIFY_DOCUMENT"