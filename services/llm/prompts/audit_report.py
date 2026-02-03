from typing import List, Dict
from datetime import datetime
from config.logger import get_logger


def build_audit_report_prompt(
    company: Dict,
    audit: Dict,
    document_audits: List[Dict]
) -> str:
    return f"""
You are a senior financial compliance auditor.

Generate a professional audit report based on the following data.
Use formal audit language. Be concise. No markdown.

Company:
{company}

Audit:
{audit}

Document Audit Results:
{document_audits}

Rules:
- Do NOT invent issues
- Base conclusions strictly on provided data
- Classify overall risk correctly
- Produce structured JSON exactly as instructed

Return JSON with fields:
- report_metadata
- executive_summary
- risk_overview
- document_findings
- recommendations
- auditor_disclaimer
"""
