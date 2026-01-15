from core.graph.graph import build_graph
from core.state import AuditState

graph = build_graph()

state = AuditState(company_id="abc", document_id= "123" )

result = graph.invoke(state)
print(type(result))
print(result["audit_trace"])
print(result["file_type"], result["document_type"])