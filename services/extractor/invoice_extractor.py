from openai import OpenAI
from core.schemas.invoice import InvoiceSchema
import json

client = OpenAI()

from openai import OpenAI
from core.schemas.invoice import InvoiceSchema
import json
import logging

logger = logging.getLogger(__name__)
client = OpenAI()

def extract_invoice(parsed_content: dict) -> InvoiceSchema:

    print("DEBUG parsed_content type:", type(parsed_content))
    print("DEBUG parsed_content:", parsed_content)
    
    # Defensive check
    if not isinstance(parsed_content, dict):
        raise TypeError(f"Expected dict, got {type(parsed_content).__name__}")
    
    text = parsed_content["raw_text"]
    tables = parsed_content["tables"]

    prompt = f"""
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

    Return ONLY valid JSON matching the schema. Do not include markdown formatting or code blocks.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    
    # Debug logging
    logger.info(f"LLM Response: {content}")
    print(f"DEBUG LLM response: {content}")
    
    # Handle markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    if not content:
        raise ValueError("LLM returned empty response")
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {content}")
        raise ValueError(f"Invalid JSON from LLM: {e}")
    
    return InvoiceSchema(**data)