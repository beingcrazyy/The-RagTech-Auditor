from infra.db.db import get_connection
import sqlite3
import json
from config.logger import get_logger

logger = get_logger(__name__)

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


def update_document_state(
    document_id: str,
    *,
    status: str | None = None,              # IN_PROGRESS / COMPLETED
    audit_id: str | None = None,
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

    if audit_id is not None:
        fields.append("audit_id = ?")
        values.append(audit_id)

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
