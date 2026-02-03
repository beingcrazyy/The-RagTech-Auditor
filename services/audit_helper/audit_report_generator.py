from typing import List, Dict
from datetime import datetime
from config.logger import get_logger
from services.llm.prompts.audit_report import build_audit_report_prompt

logger = get_logger(__name__)

def generate_audit_report(
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
        f"Generating audit report via LLM for company={company['company_id']} audit={audit['audit_id']}"
    )

    response = llm_client.generate(
        prompt=prompt,
        temperature=0.2
    )

    # IMPORTANT: LLM must return valid JSON
    return response