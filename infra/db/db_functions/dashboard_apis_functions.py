from infra.db.db import get_connection
import sqlite3
from config.logger import get_logger

logger = get_logger(__name__)

# -------------------------
# DASHBOARD / REPORTING
# -------------------------

def get_dashboard_metrics():
    try:
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
    except Exception as e:
        logger.error("Error getting dashboard metrics: %s", e, exc_info=True)
        return {
            "total_companies": 0,
            "total_documents": 0,
            "flagged_documents": 0,
            "failed_documents": 0,
            "running_audits": 0,
        }
