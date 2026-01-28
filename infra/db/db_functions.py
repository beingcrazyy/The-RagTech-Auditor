from infra.db.db import get_connection
import sqlite3
import json

def insert_company(
        company_id, 
        company_name,
        category,
        country,
        description
        ):
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
        (company_id, company_name, category, country, description)
    )

    conn.commit()
    conn.close()

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


def start_document_audit(document_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO document_audits (
            document_id,
            status,
            progress,
            started_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (document_id, "IN_PROGRESS", 0)
    )

    conn.commit()
    conn.close()


def update_document_progress(document_id: str, progress: int):
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
