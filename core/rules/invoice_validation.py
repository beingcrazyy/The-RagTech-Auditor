from typing import Dict, List

def validate_invoice(invoice : dict) -> dict:
    
    hard_failures: List[str] = []
    soft_failures: List[str] = []

    # ---- Structural ----
    if not invoice.get("invoice_number"):
        hard_failures.append("Missing invoice number")

    if not invoice.get("invoice_date"):
        hard_failures.append("Missing invoice date")

    if invoice.get("total_amount") is None:
        hard_failures.append("Missing total amount")

    if not invoice.get("currency"):
        soft_failures.append("Missing currency")

    # ---- Mathematical ----
    subtotal = invoice.get("subtotal")
    total = invoice.get("total_amount")
    cgst = invoice.get("cgst")
    sgst = invoice.get("sgst")
    igst = invoice.get("igst")

    if subtotal is not None and total is not None:
        if cgst is not None and sgst is not None:
            if abs((subtotal + cgst + sgst) - total) > 1:
                hard_failures.append("Subtotal + CGST + SGST != Total")

        if igst is not None:
            if abs((subtotal + igst) - total) > 1:
                hard_failures.append("Subtotal + IGST != Total")

    # ---- Semantic ----
    if cgst is not None and sgst is not None:
        if abs(cgst - sgst) > 1:
            soft_failures.append("CGST and SGST mismatch")

    return {
        "passed": len(hard_failures) == 0,
        "hard_failures": hard_failures,
        "soft_failures": soft_failures
    }
