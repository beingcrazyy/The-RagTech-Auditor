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

def insert_document(
    document_id: str,
    company_id: str,
    file_name: str,
    file_path: str
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO documents (
                document_id,
                company_id,
                file_name,
                file_path
            )
            VALUES (?, ?, ?, ?)
            """,
            (document_id, company_id, file_name, file_path)
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
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
        (document_id, company_id, audit_id, status, progress, started_at, is_active)
        VALUES (?, ?, ?, 'IN_PROGRESS', 0, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(document_id)
        DO UPDATE SET
            audit_id = excluded.audit_id,
            status = 'IN_PROGRESS',
            progress = 0,
            started_at = CURRENT_TIMESTAMP,
            completed_at = NULL,
            is_active = 1
        """,
        (document_id, company_id, audit_id)
    )
    conn.commit()
    conn.close()


def finalize_document_audit(
    document_id: str,
    audit_summary: str,
    hard_failures: list,
    soft_failures: list
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE document_audits
        SET
            audit_summary = ?,
            hard_failures = ?,
            soft_failures = ?
        WHERE document_id = ?
        """,
        (
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
    *,
    status: str | None = None,              # IN_PROGRESS / COMPLETED
    result: str | None = None,              # VERIFIED / FLAGGED / FAILED
    progress: int | None = None,             # 0–100
    current_step: str | None = None,         # graph node name
    file_type: str | None = None,            # PDF / IMAGE / OTHER
    document_type: str | None = None,        # INVOICE / BANK / PL
    is_active: int | None = None,            # 1 / 0
    hard_failures: list | None = None,
    soft_failures: list | None = None,
    audit_summary: str | None = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    # ---- core state ----
    if status is not None:
        fields.append("status = ?")
        values.append(status)

        if status == "IN_PROGRESS":
            fields.append(
                "processing_started_at = COALESCE(processing_started_at, CURRENT_TIMESTAMP)"
            )

        if status == "COMPLETED":
            fields.append("completed_at = CURRENT_TIMESTAMP")

    if result is not None:
        fields.append("result = ?")
        values.append(result)

    if progress is not None:
        fields.append("progress = ?")
        values.append(progress)

    if current_step is not None:
        fields.append("current_step = ?")
        values.append(current_step)

    # ---- classification metadata ----
    if file_type is not None:
        fields.append("file_type = ?")
        values.append(file_type)

    if document_type is not None:
        fields.append("document_type = ?")
        values.append(document_type)

    # ---- execution flags ----
    if is_active is not None:
        fields.append("is_active = ?")
        values.append(is_active)

    # ---- audit output ----
    if hard_failures is not None:
        fields.append("hard_failures = ?")
        values.append(json.dumps(hard_failures))

    if soft_failures is not None:
        fields.append("soft_failures = ?")
        values.append(json.dumps(soft_failures))

    if audit_summary is not None:
        fields.append("audit_summary = ?")
        values.append(audit_summary)

    # ---- heartbeat (always) ----
    fields.append("last_heartbeat_at = CURRENT_TIMESTAMP")

    if not fields:
        conn.close()
        return

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

    # --- Core progress stats ---
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_documents,
            COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS processed_documents,
            AVG(progress) AS avg_progress
        FROM document_audits
        WHERE company_id = ?
        """,
        (company_id,)
    )

    total_docs, processed_docs, avg_progress = cursor.fetchone()

    total_docs = total_docs or 0
    processed_docs = processed_docs or 0
    avg_progress = float(avg_progress) if avg_progress is not None else 0.0

    # --- Active document ---
    cursor.execute(
        """
        SELECT
            d.file_name,
            da.current_step,
            da.progress
        FROM document_audits da
        JOIN documents d ON d.document_id = da.document_id
        WHERE da.company_id = ?
          AND da.is_active = 1
        ORDER BY da.processing_started_at DESC
        LIMIT 1
        """,
        (company_id,)
    )

    row = cursor.fetchone()
    conn.close()

    active_doc = None
    current_step = None
    current_progress = None

    if row:
        active_doc, current_step, current_progress = row

    status = "IN_PROGRESS" if active_doc else "COMPLETED"

    # --- UI message ---
    if total_docs == 0:
        message = "No documents available for audit."

    elif status == "COMPLETED":
        message = f"Audit completed for all {total_docs} documents."

    else:
        message = (
            f"Processing documents ({processed_docs + 1}/{total_docs}) — "
            f"{active_doc} "
            f"({current_progress or 0}% completed, step: {current_step})"
        )

    return {
        "total_documents": total_docs,
        "processed_documents": processed_docs,
        "active_document_name": active_doc,
        "progress_avg": avg_progress,
        "message": message,
        "status": status
    }


def get_audit_status_for_company(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_documents,
            COUNT(CASE WHEN status = 'VERIFIED' THEN 1 END) AS verified_documents,
            COUNT(CASE WHEN status = 'FAILED' THEN 1 END) AS failed_documents
        FROM document_audits
        WHERE company_id = ?
        """,
        (company_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return {
        "total_documents": row[0],
        "verified_documents": row[1],
        "failed_documents": row[2]
    }