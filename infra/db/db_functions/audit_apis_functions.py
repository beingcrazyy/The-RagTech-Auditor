from infra.db.postgres import get_connection
import json
from config.logger import get_logger

logger = get_logger(__name__)

# -------------------------
# COMPANY AUDIT HISTORY
# -------------------------

def create_company_audit_record(audit_id: str, company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO company_audit_history (audit_id, company_id, status) VALUES (%s, %s, 'RUNNING')",
                    (audit_id, company_id)
                )
                conn.commit()
        return True
                
    except Exception as e:
        logger.error("Error creating company audit record: %s", e, exc_info=True)
        return False


def update_company_audit_status(audit_id: str, status: str, report_path=None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE company_audit_history
                    SET
                        status = %s,
                        completed_at = CASE
                            WHEN %s = 'COMPLETED' THEN CURRENT_TIMESTAMP
                            ELSE completed_at
                        END,
                        report_path = %s
                    WHERE audit_id = %s
                    """,
                    (
                        status,        # for status = %s
                        status,        # for CASE WHEN %s = 'COMPLETED'
                        report_path,   # report_path = %s
                        audit_id       # WHERE audit_id = %s
                    )
                )
                conn.commit()
    except Exception as e:
        logger.error("Error updating company audit status: %s", e, exc_info=True)


def get_latest_company_audit(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT audit_id, status, started_at, completed_at, report_path,
                           total_documents, processed_documents, verified_documents, flagged_documents, failed_documents, out_of_scope_documents
                    FROM company_audit_history
                    WHERE company_id=%s AND status='COMPLETED'
                    ORDER BY completed_at DESC
                    LIMIT 1
                    """,
                    (company_id,)
                )
                row = cursor.fetchone()
        return dict(zip(
            ["audit_id","status","started_at","completed_at","report_path",
             "total_documents", "processed_documents", "verified_documents", "flagged_documents", "failed_documents", "out_of_scope_documents"],
            row
        )) if row else None
    except Exception as e:
        logger.error("Error getting latest company audit: %s", e, exc_info=True)
        return None


def get_company_audit_history(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT audit_id, status, started_at, completed_at, total_documents, processed_documents, verified_documents, flagged_documents, failed_documents, out_of_scope_documents
                    FROM company_audit_history
                    WHERE company_id=%s
                    ORDER BY started_at DESC
                    """,
                    (company_id,)
                )
                rows = cursor.fetchall()
        return [
            dict(zip(
                ["audit_id","status","started_at","completed_at","total_documents", "processed_documents", "verified_documents", "flagged_documents", "failed_documents", "out_of_scope_documents",],
                r
            )) for r in rows
        ]
    except Exception as e:
        logger.error("Error getting company audit history: %s", e, exc_info=True)
        return []

# -------------------------
# DOCUMENT AUDITS (LIVE STATE)
# -------------------------

def create_document_audit(document_id, company_id, audit_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO document_audits
                    (document_id, company_id, audit_id, status, progress, started_at, is_active)
                    VALUES (%s, %s, %s, 'IN_PROGRESS', 0, CURRENT_TIMESTAMP, 1)
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
    except Exception as e:
        logger.error("Error creating document audit: %s", e, exc_info=True)


def finalize_document_audit(
    document_id: str,
    audit_summary: str,
    hard_failures: list,
    soft_failures: list
):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE document_audits
                    SET
                        audit_summary = %s,
                        hard_failures = %s,
                        soft_failures = %s
                    WHERE document_id = %s
                    """,
                    (
                        audit_summary,
                        json.dumps(hard_failures),
                        json.dumps(soft_failures),
                        document_id
                    )
                )
                conn.commit()
    except Exception as e:
        logger.error("Error finalizing document audit: %s", e, exc_info=True)

def get_document_audit_details(company_id: str, document_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT status, progress, audit_summary, hard_failures, soft_failures
                    FROM document_audits
                    WHERE company_id=%s AND document_id=%s
                    """,
                    (company_id, document_id)
                )
                row = cursor.fetchone()
        return {
            "status": row[0],
            "progress": row[1],
            "audit_summary": row[2],
            "hard_failures": json.loads(row[3]) if row[3] else [],
            "soft_failures": json.loads(row[4]) if row[4] else []
        } if row else None
    except Exception as e:
        logger.error("Error getting document audit details: %s", e, exc_info=True)
        return None


def get_document_audits_for_audit(audit_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        document_id,
                        document_type,
                        result,
                        hard_failures,
                        soft_failures,
                        audit_summary
                    FROM document_audits
                    WHERE audit_id = %s
                    """,
                    (audit_id,)
                )
                rows = cursor.fetchall()
            
        documents = []
        for row in rows:
            documents.append({
                "document_id": row[0],
                "document_type": row[1],
                "result": row[2],  # VERIFIED / FLAGGED / FAILED
                "hard_failures": json.loads(row[3]) if row[3] else [],
                "soft_failures": json.loads(row[4]) if row[4] else [],
                "audit_summary": row[5]
            })
        return documents
    except Exception as e:
        logger.error("Error getting document audits for audit: %s", e, exc_info=True)
        return []


def override_document_status(document_id: str, status: str, comment: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE document_audits
                    SET status=%s, audit_summary=%s
                    WHERE document_id=%s
                    """,
                    (status, comment, document_id)
                )
                conn.commit()
    except Exception as e:
        logger.error("Error overriding document status: %s", e, exc_info=True)


def get_rule_by_id(rule_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT rule_id, severity, category, title FROM audit_rules WHERE rule_id=%s",
                    (rule_id,)
                )
                row = cursor.fetchone()
        return {
            "rule_id": row[0],
            "severity": row[1],
            "category": row[2],
            "title": row[3]
        } if row else None
    except Exception as e:
        logger.error("Error getting rule by id: %s", e, exc_info=True)
        return None


def get_company_live_audit_state(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # --- Core progress stats ---
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_documents,
                        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS processed_documents,
                        AVG(progress) AS avg_progress
                    FROM document_audits
                    WHERE company_id = %s
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
                    WHERE da.company_id = %s
                    AND da.is_active = 1
                    ORDER BY da.processing_started_at DESC
                    LIMIT 1
                    """,
                    (company_id,)
                )

                row = cursor.fetchone()

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
    except Exception as e:
        logger.error("Error getting company live audit state: %s", e, exc_info=True)
        return {
            "total_documents": 0,
            "processed_documents": 0,
            "active_document_name": None,
            "progress_avg": 0.0,
            "message": "Error loading audit state.",
            "status": "COMPLETED"
        }


def get_audit_status_for_company(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_documents,
                        COUNT(CASE WHEN result = 'VERIFIED' THEN 1 END) AS verified_documents,
                        COUNT(CASE WHEN result = 'FAILED' THEN 1 END) AS failed_documents,
                        COUNT(CASE WHEN result = 'FLAGGED' THEN 1 END) AS flagged_documents
                    FROM document_audits
                    WHERE company_id = %s
                    """,
                    (company_id,)
                )

                row = cursor.fetchone()

        return {
            "total_documents": row[0],
            "verified_documents": row[1],
            "failed_documents": row[2],
            "flagged_documents": row[3]
        }
    except Exception as e:
        logger.error("Error getting audit status for company: %s", e, exc_info=True)
        return {
            "total_documents": 0,
            "verified_documents": 0,
            "failed_documents": 0,
            "flagged_documents": 0
        }


# -------------------------
# AUDIT HISTORY APPEND
# -------------------------


def try_finalize_company_audit(document_id: str) -> None:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Get audit_id and company_id for this document
                cursor.execute(
                    """
                    SELECT audit_id, company_id
                    FROM document_audits
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return

                audit_id = row[0]

                # 2. Check if any documents are still IN_PROGRESS for this audit
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM document_audits
                    WHERE audit_id = %s
                    AND status = 'IN_PROGRESS'
                    """,
                    (audit_id,)
                )
                remaining = cursor.fetchone()[0]

                logger.info("%s docs are being processed", remaining)

                # If even one document is running, do NOT finalize
                if remaining > 0:
                    return
                
                logger.info("processing")

                # 3. Aggregate final document results
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_documents,
                        SUM(result = 'VERIFIED') AS verified_documents,
                        SUM(result = 'FLAGGED') AS flagged_documents,
                        SUM(result = 'FAILED') AS failed_documents,
                        SUM(result = 'OUT_OF_SCOPE') AS out_of_scope_documents
                    FROM document_audits
                    WHERE audit_id = %s
                    """,
                    (audit_id,)
                )
                (
                    total_documents,
                    verified_documents,
                    flagged_documents,
                    failed_documents,
                    out_of_scope_documents
                ) = cursor.fetchone()

                # 4. Mark company audit as COMPLETED
                cursor.execute(
                    """
                    UPDATE company_audit_history
                    SET
                        status = 'COMPLETED',
                        completed_at = CURRENT_TIMESTAMP,
                        total_documents = %s,
                        verified_documents = %s,
                        flagged_documents = %s,
                        failed_documents = %s,
                        out_of_scope_documents = %s
                    WHERE audit_id = %s
                    """,
                    (
                        total_documents,
                        verified_documents or 0,
                        flagged_documents or 0,
                        failed_documents or 0,
                        out_of_scope_documents or 0,
                        audit_id
                    )
                )

                conn.commit()
    except Exception as e:
        logger.error("Error trying to finalize company audit: %s", e, exc_info=True)


def count_remaining_documents_for_audit(audit_id: str) -> int:
        """
        Returns number of documents still being processed for a given audit.
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM document_audits
                        WHERE audit_id = %s
                        AND status = 'IN_PROGRESS'
                        """,
                        (audit_id,)
                    )
                    remaining = cursor.fetchone()[0] or 0
            return remaining
        except Exception as e:
            logger.error("Error counting remaining documents: %s", e, exc_info=True)
            return 0

def reset_document_audit(company_id: str, document_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE document_audits
                    SET status='IN_PROGRESS', progress=0, result=NULL,
                        hard_failures=NULL, soft_failures=NULL, audit_summary=NULL,
                        completed_at=NULL, processing_started_at=CURRENT_TIMESTAMP
                    WHERE company_id=%s AND document_id=%s
                """, (company_id, document_id))
                conn.commit()
    except Exception as e:
        logger.error("Error resetting document audit: %s", e, exc_info=True)
