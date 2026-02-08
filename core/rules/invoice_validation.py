from typing import Dict, List, Optional
from infra.db.db_functions.audit_apis_functions import get_rule_by_id

def emit(rule_id: str, message: str, evidence_ref: str, confidence: float = 1.0) -> Dict:
    return {
        "rule_id": rule_id,
        "message": message,
        "evidence_ref": evidence_ref,
        "confidence": confidence
    }


def check_missing_invoice_number(invoice: dict) -> Optional[Dict]:
    if not invoice.get("invoice_number"):
        return emit(
            "FIN_INV_STRUCT_001",
            "Missing invoice number",
            "invoice_number"
        )
    return None


def check_missing_invoice_date(invoice: dict) -> Optional[Dict]:
    if not invoice.get("invoice_date"):
        return emit(
            "FIN_INV_STRUCT_002",
            "Missing invoice date",
            "invoice_date"
        )
    return None


def check_missing_total_amount(invoice: dict) -> Optional[Dict]:
    if invoice.get("total_amount") is None:
        return emit(
            "FIN_INV_STRUCT_003",
            "Missing total amount",
            "total_amount"
        )
    return None


def check_missing_currency(invoice: dict) -> Optional[Dict]:
    if not invoice.get("currency"):
        return emit(
            "FIN_INV_STRUCT_004",
            "Missing currency",
            "currency",
            confidence=0.9
        )
    return None

def check_subtotal_cgst_sgst_equals_total(invoice: dict) -> Optional[Dict]:
    subtotal = invoice.get("subtotal")
    cgst = invoice.get("cgst")
    sgst = invoice.get("sgst")
    total = invoice.get("total_amount")

    if None not in (subtotal, cgst, sgst, total):
        if abs((subtotal + cgst + sgst) - total) > 1:
            return emit(
                "FIN_INV_MATH_001",
                "Subtotal + CGST + SGST does not equal total",
                "tax_breakup"
            )
    return None



def check_subtotal_igst_equals_total(invoice: dict) -> Optional[Dict]:
    subtotal = invoice.get("subtotal")
    igst = invoice.get("igst")
    total = invoice.get("total_amount")

    if None not in (subtotal, igst, total):
        if abs((subtotal + igst) - total) > 1:
            return emit(
                "FIN_INV_MATH_002",
                "Subtotal + IGST does not equal total",
                "tax_breakup"
            )
    return None

def check_cgst_sgst_mismatch(invoice: dict) -> Optional[Dict]:
    cgst = invoice.get("cgst")
    sgst = invoice.get("sgst")

    if None not in (cgst, sgst):
        if abs(cgst - sgst) > 1:
            return emit(
                "FIN_INV_LOGIC_001",
                "CGST and SGST mismatch",
                "tax_breakup",
                confidence=0.95
            )
    return None



INVOICE_RULES = [
    check_missing_invoice_number,
    check_missing_invoice_date,
    check_missing_total_amount,
    check_missing_currency,
    check_subtotal_cgst_sgst_equals_total,
    check_subtotal_igst_equals_total,
    check_cgst_sgst_mismatch
]

def validate_invoice(invoice: dict) -> dict:
    raw_failures = []

    # 1. Execute rules and collect RESULTS
    for rule in INVOICE_RULES:
        result = rule(invoice)
        if result:
            raw_failures.append(result)

    if not raw_failures:
        return {
            "hard_failures": [],
            "soft_failures": []
        }

    hard_failures = []
    soft_failures = []

    # 2. Enrich using rule_id
    for failure in raw_failures:
        rule_id = failure["rule_id"]
        details = get_rule_by_id(rule_id)

        enriched = {
            **failure,
            "severity": details["severity"],
            "category": details["category"],
            "title": details["title"]
        }

        if details["severity"] == "HARD":
            hard_failures.append(enriched)
        else:
            soft_failures.append(enriched)

    return {
        "hard_failures": hard_failures,
        "soft_failures": soft_failures
    }


