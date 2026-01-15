from langgraph.graph import StateGraph, END
from core.state import AuditState
from core.graph.nodes import (
    ingest_node,
    detect_file_type_node,
    classify_document_node
)

def build_graph():
    graph = StateGraph(AuditState)

    graph.add_node("INGEST", ingest_node )
    graph.add_node("DETECT_FILE_TYPE", detect_file_type_node)
    graph.add_node("CLASSIFY_DOCUMENT", classify_document_node)

    graph.set_entry_point("INGEST")

    graph.add_edge("INGEST", "DETECT_FILE_TYPE")
    graph.add_edge("DETECT_FILE_TYPE", "CLASSIFY_DOCUMENT")
    graph.add_edge("CLASSIFY_DOCUMENT", END)

    return graph.compile()