def aggregate_company_metrics(documents: list[dict]) -> dict:
    return {
        "total_documents": len(documents),
        "verified_documents": sum(d["result"] == "VERIFIED" for d in documents),
        "flagged_documents": sum(d["result"] == "FLAGGED" for d in documents),
        "failed_documents": sum(d["result"] == "FAILED" for d in documents),
        "out_of_scope_documents": sum(d["result"] == "OUT_OF_SCOPE" for d in documents),
    }


def aggregate_document_results(documents: list[dict]) -> list[dict]:
    aggregated = []

    for doc in documents:
        hard = doc.get("hard_failures", [])
        soft = doc.get("soft_failures", [])

        aggregated.append({
            "document_id": doc["document_id"],
            "document_type": doc["document_type"],
            "result": doc["result"],
            "hard_issues_count": len(hard),
            "soft_issues_count": len(soft),
            "total_issues": len(hard) + len(soft),
            "hard_issues": hard,
            "soft_issues": soft,
            "summary": doc.get("audit_summary")
        })

    return aggregated



def aggregate_rule_impact(documents: list[dict]) -> list[dict]:
    rule_map = {}

    for doc in documents:
        doc_id = doc["document_id"]

        for issue in doc.get("hard_failures", []) + doc.get("soft_failures", []):
            rule_id = issue["rule_id"]

            if rule_id not in rule_map:
                rule_map[rule_id] = {
                    "rule_id": rule_id,
                    "title": issue.get("title"),
                    "category": issue.get("category"),
                    "severity": issue.get("severity"),
                    "affected_documents": set()
                }

            rule_map[rule_id]["affected_documents"].add(doc_id)

    # finalize
    aggregated = []
    for rule in rule_map.values():
        aggregated.append({
            "rule_id": rule["rule_id"],
            "title": rule["title"],
            "category": rule["category"],
            "severity": rule["severity"],
            "affected_documents_count": len(rule["affected_documents"]),
            "affected_documents": sorted(rule["affected_documents"])
        })

    return aggregated