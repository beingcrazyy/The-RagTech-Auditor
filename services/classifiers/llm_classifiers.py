from core.enums.document_type import DocumentType
from openai import OpenAI
from config.settings import MODEL_NAME, TEMPERATURE

client = OpenAI()

def llm_document_classifier(text: str) -> DocumentType:
    prompt = f"""
    You are a financial document classifier.

    Classify the document into EXACTLY one of:
    - INVOICE
    - BANK_STATEMENT
    - P_AND_L
    - OTHER

    Rules:
    - Return ONLY one of the above words
    - Do not explain
    - Do not infer numbers

    Document text:
    {text[:3000]}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = resp.choices[0].message.content.strip()

    try:
        return DocumentType(result)
    except ValueError:
        return DocumentType.OTHER