from typing import List, Dict
from datetime import datetime
from config.logger import get_logger


def build_audit_report_prompt(
    company: Dict,
    audit: Dict,
    document_audits: List[Dict]
) -> str:
    return f"""
    You are a senior financial audit partner at a Big-4 firm.

    Your task is to generate a FINAL audit report in STRICT JSON format.
    You must NOT invent data.
    You must ONLY format and summarize the provided facts.

    =====================
    INPUT DATA
    =====================

    Company Details:
    {company}

    Audit Details:
    {audit}

    Document Audit Records (already processed and finalized):
    {document_audits}

    =====================
    CRITICAL DEFINITIONS
    =====================

    - status = processing state (COMPLETED / IN_PROGRESS)
    - result = audit outcome (VERIFIED / FLAGGED / FAILED / OUT_OF_SCOPE)

    - ALL documents here are already COMPLETED
    - You must NOT re-calculate counts, only summarize

    =====================
    MANDATORY TABLES
    =====================

    You MUST produce the following structured tables inside JSON.

    ---------------------
    TABLE 1 — DOCUMENT_SUMMARY_TABLE
    ---------------------
    One row per document.

    Columns:
    - document_id
    - document_type
    - result
    - hard_issues_count
    - soft_issues_count

    ---------------------
    TABLE 2 — RULE_IMPACT_TABLE
    ---------------------
    One row per rule violated.

    Columns:
    - rule_id
    - rule_title
    - severity
    - affected_documents_count
    - affected_documents (list of document_ids)

    ---------------------
    TABLE 3 — COMPANY_RISK_SUMMARY
    ---------------------

    Fields:
    - total_documents
    - verified_documents
    - flagged_documents
    - failed_documents
    - out_of_scope_documents
    - overall_risk_level

    Risk Level Rules:
    - HIGH → any FAILED
    - MEDIUM → FLAGGED only
    - LOW → all VERIFIED / OUT_OF_SCOPE

    =====================
    EXECUTIVE SUMMARY RULES
    =====================

    - 3–4 full professional sentences
    - Mention:
    - total documents
    - number of flagged / failed
    - overall risk level
    - Do NOT truncate
    - Do NOT repeat table data verbatim

    =====================
    OUTPUT FORMAT (STRICT JSON)
    =====================

    Return ONLY valid JSON with EXACTLY this structure:

    {{
    "report_metadata": {{
        "company_name": string,
        "company_id": string,
        "audit_id": string,
        "audit_date": string (ISO format),
        "overall_status": "COMPLETED",
        "risk_level": "LOW" | "MEDIUM" | "HIGH"
    }},

    "executive_summary": string,

    "tables": {{
        "document_summary_table": [
        {{
            "document_id": string,
            "document_type": string,
            "result": string,
            "hard_issues_count": number,
            "soft_issues_count": number
        }}
        ],

        "rule_impact_table": [
        {{
            "rule_id": string,
            "rule_title": string,
            "severity": string,
            "affected_documents_count": number,
            "affected_documents": [string]
        }}
        ],

        "company_risk_summary": {{
        "total_documents": number,
        "verified_documents": number,
        "flagged_documents": number,
        "failed_documents": number,
        "out_of_scope_documents": number,
        "overall_risk_level": "LOW" | "MEDIUM" | "HIGH"
        }}
    }},

    "recommendations": [string],
    "auditor_disclaimer": string
    }}

    =====================
    ABSOLUTE RULES
    =====================

    - DO NOT include markdown
    - DO NOT include explanations
    - DO NOT add extra fields
    - DO NOT omit any table
    - Output JSON only
    """