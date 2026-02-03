def build_document_classification_prompt(text: str) -> str:
    return f"""
Classify the document into one of:
INVOICE, BANK_STATEMENT, PL_STATEMENT, OTHER

Document:
{text[:3000]}

Return ONLY the category name.
"""