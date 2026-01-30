from core.rules.invoice_validation import INVOICE_RULES
from infra.db.db_functions import (
    update_document_progress,
    finalize_document_audit,
    get_rule_by_id
)
import json

def enrich_failures(raw_failures: list) -> tuple[list, list]:
    hard = []
    soft = []

    for f in raw_failures:
        rule = get_rule_by_id(f["rule_id"])

        enriched = {
            **f,
            "severity": rule["severity"],
            "category": rule["category"],
            "title": rule["title"]
        }

        if rule["severity"] == "HARD":
            hard.append(enriched)
        else:
            soft.append(enriched)

    return hard, soft

def run_invoice_audit(document_id: str, invoice_data: dict):
    update_document_progress(document_id, 20)

    raw_failures = []

    for rule in INVOICE_RULES:
        result = rule(invoice_data)
        if result:
            raw_failures.append(result)

    update_document_progress(document_id, 70)

    hard_failures, soft_failures = enrich_failures(raw_failures)

    status = "VERIFIED" if not hard_failures else "FAILED"

    finalize_document_audit(
        document_id=document_id,
        status=status,
        audit_summary=f"{len(hard_failures)} hard failures, {len(soft_failures)} soft failures",
        hard_failures=hard_failures,
        soft_failures=soft_failures
    )


def run_company_audit(company_id: str, documents: list):
    for doc in documents:
        document_id = doc["document_id"]

        # TODO (V1 assumption): invoice_data already parsed
        invoice_data = doc["parsed_data"]

        

        run_invoice_audit(document_id, invoice_data)

        

def run_single_document_audit(company_id : str, document_id : str):
    documents = [{"document_id": document_id}]
    run_company_audit(company_id= company_id, documents= documents)