from infra.db.db import get_connection
import sqlite3
import json
from config.logger import get_logger

logger = get_logger(__name__)

def insert_company(
        company_id, 
        company_name,
        company_category,
        company_country,
        company_description
        ):
    logger.info(f"Inserting company: {company_name} ({company_id})")
    conn = get_connection()
    cursor = conn.cursor()

  
    cursor.execute(
        """
        INSERT INTO companies (
        company_id, 
        company_name,
        company_category,
        company_country,
        company_description
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (company_id, company_name, company_category, company_country, company_description)
    )

    conn.commit()
    conn.close()
    logger.info(f"Successfully inserted company: {company_id}")

def insert_document(
    document_id: str,
    company_id: str,
    file_name: str,
    file_path: str
):
    logger.info(f"Inserting document: {file_name} for company: {company_id}")
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
        logger.info(f"Successfully inserted document: {document_id}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Document already exists: {document_id}")
        return False
    except Exception as e:
        logger.error(f"Error inserting document {document_id}: {e}")
        return False
    finally:
        conn.close()


def start_document_audit(document_id: str, company_id : str):
    logger.info(f"Starting audit record for document: {document_id} (Company: {company_id})")
    conn = get_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute(
            """
            INSERT INTO document_audits (
                document_id,
                company_id,
                status,
                progress,
                started_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (document_id,company_id, "IN_PROGRESS", 0)
        )
        conn.commit()
        logger.info(f"Audit record created for {document_id}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Audit already in progress/exists for document: {document_id}")
        return False
    except Exception as e:
        logger.error(f"Error starting audit record for {document_id}: {e}")
        return False
    finally:
        conn.close()



def update_document_progress(document_id: str, progress: int):
    logger.debug(f"Updating progress for {document_id}: {progress}%")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE document_audits
        SET progress = ?
        WHERE document_id = ?
        """,
        (progress, document_id)
    )

    conn.commit()
    conn.close()


def finalize_document_audit(
    document_id: str,
    status: str,
    audit_summary: str,
    hard_failures: list,
    soft_failures: list
):
    logger.info(f"Finalizing audit for {document_id} with status: {status}")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE document_audits
        SET
            status = ?,
            progress = ?,
            audit_summary = ?,
            hard_failures = ?,
            soft_failures = ?,
            completed_at = CURRENT_TIMESTAMP
        WHERE document_id = ?
        """,
        (
            status,
            100,
            audit_summary,
            json.dumps(hard_failures),
            json.dumps(soft_failures),
            document_id
        )
    )

    conn.commit()
    conn.close()
    logger.info(f"Successfully finalized audit for {document_id}")


def get_documents_for_company(company_id : str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT document_id,file_path
        FROM documents
        WHERE company_id = ?
        """,
        (company_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [{
            "document_id": r[0],
            "file_path": r[1]
        }
        for r in rows
    ]


def get_audit_status_for_company(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            document_id,
            status,
            progress,
            started_at,
            completed_at
        FROM document_audits
        WHERE company_id = ?
        ORDER BY started_at ASC
        """,
        (company_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "document_id": r[0],
            "status": r[1],
            "progress": r[2],
            "started_at": r[3],
            "completed_at": r[4],
        }
        for r in rows
    ]


def get_document_audit_details(company_id: str, document_id: str) -> dict :
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            document_id,
            status,
            progress,
            audit_summary,
            hard_failures,
            soft_failures,
            started_at,
            completed_at
        FROM document_audits
        WHERE company_id = ?
          AND document_id = ?
        """,
        (company_id, document_id)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "document_id": row[0],
        "status": row[1],
        "progress": row[2],
        "audit_summary": row[3],
        "hard_failures": json.loads(row[4]) if row[4] else [],
        "soft_failures": json.loads(row[5]) if row[5] else [],
        "started_at": row[6],
        "completed_at": row[7],
    }

def reset_document_audit(company_id : str, document_id : str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE document_audits
        SET
            status = 'IN_PROGRESS'
            progress = 0,
            audit_summary = NULL,
            hard_failures = NULL,
            soft_failures = NULL,
            completed_at = CURRENT_TIMESTAMP
        WHERE document_id = ?
        """,
        (document_id,)
    )

    conn.commit()
    conn.close()


def get_rule_by_id(rule_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rule_id, severity, category, title
        FROM audit_rules
        WHERE rule_id = ?
        """,
        (rule_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise Exception(f"Rule not found: {rule_id}")

    return {
        "rule_id": row[0],
        "severity": row[1],
        "category": row[2],
        "title": row[3]
    }


def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor()

    # Query to get company info along with document counts and audit status counts
    cursor.execute(
        """
        SELECT 
            c.company_id, 
            c.company_name, 
            c.company_category, 
            c.company_country,
            COUNT(d.document_id) as total_documents,
            COUNT(CASE WHEN da.status = 'VERIFIED' THEN 1 END) as verified_documents,
            COUNT(CASE WHEN da.status = 'FLAGGED' THEN 1 END) as flagged_documents,
            COUNT(CASE WHEN da.status = 'FAILED' THEN 1 END) as failed_documents
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
            "failed_documents": r[7]
        }
        for r in rows
    ]


def get_company_documents_detailed(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            d.document_id,
            d.file_name,
            d.file_path,
            d.uploaded_at,
            da.status,
            da.progress,
            da.audit_summary
        FROM documents d
        LEFT JOIN document_audits da ON d.document_id = da.document_id
        WHERE d.company_id = ?
        """,
        (company_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "document_id": r[0],
            "file_name": r[1],
            "file_path": r[2],
            "uploaded_at": r[3],
            "status": r[4],
            "progress": r[5],
            "audit_summary": r[6]
        }
        for r in rows
    ]


def create_company_audit_record(audit_id: str, company_id: str, status: str = "INITIATED"):
    conn = get_connection()
    cursor = conn.cursor()
    
    logger.info(f"Creating audit history record {audit_id} for company {company_id}")
    
    cursor.execute(
        """
        INSERT INTO company_audit_history (audit_id, company_id, status)
        VALUES (?, ?, ?)
        """,
        (audit_id, company_id, status)
    )
    
    conn.commit()
    conn.close()


def get_company_audit_history(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT audit_id, status, started_at, completed_at, details
        FROM company_audit_history
        WHERE company_id = ?
        ORDER BY started_at DESC
        """,
        (company_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "audit_id": r[0],
            "status": r[1],
            "started_at": r[2],
            "completed_at": r[3],
            "details": r[4]
        }
        for r in rows
    ]

