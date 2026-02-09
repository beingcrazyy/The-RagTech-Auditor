from infra.db.postgres import get_connection
import json
import psycopg
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
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO documents (
                        document_id,
                        company_id,
                        file_name,
                        file_path
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (document_id, company_id, file_name, file_path)
                )
                conn.commit()
        return True

    except psycopg.IntegrityError:
        logger.warning("Duplicate document upload attempt for %s", file_name)
        return False
    except Exception as e:
        logger.error("Error inserting document: %s", e, exc_info=True)
        return False


def get_documents_for_company(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT document_id, file_path FROM documents WHERE company_id = %s",
                    (company_id,)
                )
                rows = cursor.fetchall()
        return [{"document_id": r[0], "file_path": r[1]} for r in rows]
    except Exception as e:
        logger.error("Error getting documents for company: %s", e, exc_info=True)
        return []


def get_document_file_path(company_id: str, document_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT file_path FROM documents WHERE company_id=%s AND document_id=%s",
                    (company_id, document_id)
                )
                row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error("Error getting document file path: %s", e, exc_info=True)
        return None


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
    fields = []
    values = []

    # ---- core state ----
    if status is not None:
        fields.append("status = %s")
        values.append(status)

        if status == "IN_PROGRESS":
            fields.append(
                "processing_started_at = COALESCE(processing_started_at, CURRENT_TIMESTAMP)"
            )

        if status == "COMPLETED":
            fields.append("completed_at = CURRENT_TIMESTAMP")

    if audit_id is not None:
        fields.append("audit_id = %s")
        values.append(audit_id)

    if result is not None:
        fields.append("result = %s")
        values.append(result)

    if progress is not None:
        fields.append("progress = %s")
        values.append(progress)

    if current_step is not None:
        fields.append("current_step = %s")
        values.append(current_step)

    # ---- classification metadata ----
    if file_type is not None:
        fields.append("file_type = %s")
        values.append(file_type)

    if document_type is not None:
        fields.append("document_type = %s")
        values.append(document_type)

    # ---- execution flags ----
    if is_active is not None:
        fields.append("is_active = %s")
        values.append(is_active)

    # ---- audit output ----
    if hard_failures is not None:
        fields.append("hard_failures = %s")
        values.append(json.dumps(hard_failures))

    if soft_failures is not None:
        fields.append("soft_failures = %s")
        values.append(json.dumps(soft_failures))

    if audit_summary is not None:
        fields.append("audit_summary = %s")
        values.append(audit_summary)

    # ---- heartbeat (always) ----
    fields.append("last_heartbeat_at = CURRENT_TIMESTAMP")

    if not fields:
        return

    values.append(document_id)

    query = f"""
        UPDATE document_audits
        SET {", ".join(fields)}
        WHERE document_id = %s
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
    except Exception as e:
        logger.error("Error updating document state: %s", e, exc_info=True)
