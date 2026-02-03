from core.enums.document_type import DocumentType

def heuristics_document_classifier(text: str) -> DocumentType:
    t = text.lower()

    if any(k in t for k in [
        "invoice no",
        "tax invoice",
        "bill to",
        "gstin",
        "cgst",
        "sgst"
    ]):
        return DocumentType.INVOICE
    
    if any(k in t for k in [
        "bank statement",
        "account statement",
        "opening balance",
        "closing balance",
        "debit",
        "credit",
        "account number"
    ]):
        return DocumentType.BANK_STATEMENT

    # ---- P&L signals ----
    if any(k in t for k in [
        "profit and loss",
        "statement of profit",
        "net profit",
        "total revenue",
        "total expenses"
    ]):
        return DocumentType.P_AND_L
    
    return DocumentType.OTHER


    
