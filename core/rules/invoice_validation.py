from typing import Dict, List, Optional

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



def rule_fin_inv_math_002(invoice: dict) -> Optional[Dict]:
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
