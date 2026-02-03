from services.llm.runner import run_llm
from services.llm.prompts.invoice_extract import build_invoice_extraction_prompt
from core.schemas.invoice import InvoiceSchema
import json

def extract_invoice(parsed_content: dict) -> InvoiceSchema:
    prompt = build_invoice_extraction_prompt(parsed_content)

    content = run_llm(prompt, temperature=0)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON for invoice extraction")
    return InvoiceSchema(**data)