from typing import List, Dict
from datetime import datetime
import json
from config.logger import get_logger
from config.settings import TEMPERATURE, MODEL_NAME
from services.llm.prompts.audit_report import build_audit_report_prompt

logger = get_logger(__name__)

def extract_json(text: str) -> str:
    """
    Extract the first valid JSON object from text.
    """
    text = text.strip()

    # Remove markdown fences
    if text.startswith("```"):
        text = text.split("```", 2)[1]

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response")

    return text[start : end + 1]

def generate_text_audit_report(
    company: Dict,
    audit: Dict,
    document_audits: List[Dict],
    llm_client
) -> Dict:
    """
    Calls LLM and returns structured audit report JSON
    """

    prompt = build_audit_report_prompt(company, audit, document_audits)

    logger.info(
        f"Generating audit report via LLM for company={company.get('company_id')} audit={audit.get('audit_id')}"
    )

    try:
        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior financial audit analyst generating a structured audit report. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        raw_text = response.choices[0].message.content
        clean_json_text = extract_json(raw_text)
        
        logger.debug(f"LLM response text: {clean_json_text}")
    except Exception as e:
        logger.error(f"Error during LLM call: {e}")
        raise

    try:
        audit_report = json.loads(clean_json_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"LLM response text was: {clean_json_text}")
        raise ValueError("LLM response is not valid JSON") from e

    # Optional: Validate audit_report structure here if needed

    logger.info(f"Successfully generated audit report for company={company.get('company_id')} audit={audit.get('audit_id')}")
    return audit_report