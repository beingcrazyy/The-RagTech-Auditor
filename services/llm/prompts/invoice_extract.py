import json
from core.schemas.invoice import InvoiceSchema

def build_invoice_extraction_prompt(parsed_content: dict) -> str:
    text = parsed_content["raw_text"]
    tables = parsed_content["tables"]

    return f"""
You are an information extraction engine for financial invoices.

Extract ONLY fields defined in the schema below.
If a value is not explicitly present, return null.
Do NOT calculate or infer values.

Schema:
{json.dumps(InvoiceSchema.model_json_schema(), indent=2)}

Document Text:
{text[:4000]}

Tables:
{tables[:5]}

Return ONLY valid JSON matching the schema.
"""