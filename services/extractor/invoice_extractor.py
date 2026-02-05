from services.llm.runner import run_llm
from services.llm.prompts.invoice_extract import build_invoice_extraction_prompt
from core.schemas.invoice import InvoiceSchema
import json
import re
import logging

logger = logging.getLogger(__name__)

def safe_json_parse(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty LLM response for invoice extraction")

    # Remove markdown fences if present
    cleaned = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from LLM:\n{cleaned}")
        raise ValueError(f"LLM returned invalid JSON for invoice extraction: {e}")

def extract_invoice(parsed_content: dict) -> InvoiceSchema:
    prompt = build_invoice_extraction_prompt(parsed_content)

    content = run_llm(prompt, temperature=0)

    logger.debug(f"RAW LLM INVOICE RESPONSE:\n{content}")

    data = safe_json_parse(content)

    return InvoiceSchema(**data)