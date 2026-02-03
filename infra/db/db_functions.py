from infra.db.db import get_connection
import sqlite3
import json
from datetime import datetime
from config.logger import get_logger

logger = get_logger(__name__)

# -------------------------
# COMPANY
# -------------------------

def insert_company(company_id, company_name, company_category, company_country, company_description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO companies (
            company_id, company_name, company_category, company_country, company_description
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (company_id, company_name, company_category, company_country, company_description)
    )
    conn.commit()
    conn.close()


def get_company_by_id(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT company_id, company_name, company_category, company_country, company_description FROM companies WHERE company_id = ?",
        (company_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(zip(
        ["company_id","company_name","company_category","company_country","company_description"],
        row
    )) if row else None


def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            c.company_id,
            c.company_name,
            c.company_category,
            c.company_country,
            COUNT(d.document_id) AS total_documents,
            COUNT(CASE WHEN da.status='VERIFIED' THEN 1 END),
            COUNT(CASE WHEN da.status='FLAGGED' THEN 1 END),
            COUNT(CASE WHEN da.status='FAILED' THEN 1 END)
        FROM companies c
        LEFT JOIN documents d ON c.company_id = d.company_id
        LEFT JOIN document_audits da ON d.document_id = da.document_id
        GROUP BY c.company_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "company_id": r[0],
            "company_name": r[1],
            "company_category": r[2],
            "company_country": r[3],
            "total_documents": r[4],
            "verified_documents": r[5],
            "flagged_documents": r[6],
            "failed_documents": r[7],
        }
        for r in rows
    ]

# -------------------------
# DOCUMENTS
# -------------------------

def insert_document(document_id, company_id, file_name, file_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents (document_id, company_id, file_name, file_path)
        VALUES (?, ?, ?, ?)
        """,
        (document_id, company_id, file_name, file_path)
    )
    conn.commit()
    conn.close()


def get_documents_for_company(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT document_id, file_path FROM documents WHERE company_id = ?",
        (company_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"document_id": r[0], "file_path": r[1]} for r in rows]


def get_document_file_path(company_id: str, document_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT file_path FROM documents WHERE company_id=? AND document_id=?",
        (company_id, document_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# -------------------------
# COMPANY AUDIT HISTORY
# -------------------------

def create_company_audit_record(audit_id: str, company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO company_audit_history (audit_id, company_id, status) VALUES (?, ?, 'RUNNING')",
        (audit_id, company_id)
    )
    conn.commit()
    conn.close()


def update_company_audit_status(audit_id: str, status: str, details=None, report_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE company_audit_history
        SET status=?,
            completed_at = CASE WHEN ?='COMPLETED' THEN CURRENT_TIMESTAMP ELSE completed_at END,
            details=?,
            report_path=?
        WHERE audit_id=?
        """,
        (status, status, details, report_path, audit_id)
    )
    conn.commit()
    conn.close()


def get_latest_company_audit(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT audit_id, status, started_at, completed_at, report_path
        FROM company_audit_history
        WHERE company_id=?
        ORDER BY started_at DESC
        LIMIT 1
        """,
        (company_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(zip(
        ["audit_id","status","started_at","completed_at","report_path"],
        row
    )) if row else None


def get_company_audit_history(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT audit_id, status, started_at, completed_at, details, report_path
        FROM company_audit_history
        WHERE company_id=?
        ORDER BY started_at DESC
        """,
        (company_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(zip(
            ["audit_id","status","started_at","completed_at","details","report_path"],
            r
        )) for r in rows
    ]

# -------------------------
# DOCUMENT AUDITS (LIVE STATE)
# -------------------------

def create_document_audit(document_id, company_id, audit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO document_audits
        (document_id, company_id, audit_id, status, progress, started_at, last_updated_at)
        VALUES (?, ?, ?, 'IN_PROGRESS', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        (document_id, company_id, audit_id)
    )
    conn.commit()
    conn.close()


def finalize_document_audit(document_id, status, audit_summary, hard_failures, soft_failures):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE document_audits
        SET status=?, progress=100, audit_summary=?, hard_failures=?, soft_failures=?,
            completed_at=CURRENT_TIMESTAMP, is_active=0
        WHERE document_id=?
        """,
        (
            status,
            audit_summary,
            json.dumps(hard_failures),
            json.dumps(soft_failures),
            document_id
        )
    )
    conn.commit()
    conn.close()


def get_document_audit_details(company_id: str, document_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT status, progress, audit_summary, hard_failures, soft_failures
        FROM document_audits
        WHERE company_id=? AND document_id=?
        """,
        (company_id, document_id)
    )
    row = cursor.fetchone()
    conn.close()
    return {
        "status": row[0],
        "progress": row[1],
        "audit_summary": row[2],
        "hard_failures": json.loads(row[3]) if row[3] else [],
        "soft_failures": json.loads(row[4]) if row[4] else []
    } if row else None

# -------------------------
# DASHBOARD / REPORTING
# -------------------------

def get_dashboard_metrics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM companies),
            (SELECT COUNT(*) FROM documents),
            (SELECT COUNT(*) FROM document_audits WHERE status='FLAGGED'),
            (SELECT COUNT(*) FROM document_audits WHERE status='FAILED'),
            (SELECT COUNT(*) FROM company_audit_history WHERE status='RUNNING')
        """
    )
    row = cursor.fetchone()
    conn.close()
    return {
        "total_companies": row[0],
        "total_documents": row[1],
        "flagged_documents": row[2],
        "failed_documents": row[3],
        "running_audits": row[4],
    }


def get_document_audits_for_audit(audit_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT document_id, status, audit_summary, hard_failures, soft_failures
        FROM document_audits
        WHERE audit_id=?
        """,
        (audit_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "document_id": r[0],
            "status": r[1],
            "audit_summary": r[2],
            "hard_failures": json.loads(r[3]) if r[3] else [],
            "soft_failures": json.loads(r[4]) if r[4] else []
        }
        for r in rows
    ]


def override_document_status(document_id: str, status: str, comment: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE document_audits
        SET status=?, audit_summary=?
        WHERE document_id=?
        """,
        (status, comment, document_id)
    )
    conn.commit()
    conn.close()


def get_rule_by_id(rule_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rule_id, severity, category, title FROM audit_rules WHERE rule_id=?",
        (rule_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return {
        "rule_id": row[0],
        "severity": row[1],
        "category": row[2],
        "title": row[3]
    }

def update_document_state(
    document_id: str,
    status: str | None = None,
    progress: int | None = None,
    current_step: str | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    if status is not None:
        fields.append("status = ?")
        values.append(status)

    if progress is not None:
        fields.append("progress = ?")
        values.append(progress)

    if current_step is not None:
        fields.append("current_step = ?")
        values.append(current_step)

    fields.append("last_updated_at = CURRENT_TIMESTAMP")
    values.append(document_id)

    query = f"""
        UPDATE document_audits
        SET {", ".join(fields)}
        WHERE document_id = ?
    """

    cursor.execute(query, values)
    conn.commit()
    conn.close()


def get_company_live_audit_state(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    # total + processed documents
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_docs,
            COUNT(CASE WHEN status IN ('VERIFIED','FAILED') THEN 1 END) AS processed_docs
        FROM document_audits
        WHERE company_id=?
        """,
        (company_id,)
    )
    total_docs, processed_docs = cursor.fetchone()

    # active document (latest)
    cursor.execute(
        """
        SELECT current_step
        FROM document_audits
        WHERE company_id=?
          AND status='IN_PROGRESS'
        ORDER BY last_updated_at DESC
        LIMIT 1
        """,
        (company_id,)
    )
    row = cursor.fetchone()
    conn.close()

    return {
        "total_documents": total_docs,
        "processed_documents": processed_docs,
        "current_step": row[0] if row else "Finalizing audit...",
        "status": "IN_PROGRESS" if processed_docs < total_docs else "COMPLETED"
    }
