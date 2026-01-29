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


def start_document_audit(document_id: str, company_id : str):
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

        return True
    except sqlite3.IntegrityError:
        return False
    finally:
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


def get_documents_for_company(company_id : str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT document_id
        FROM documents
        WHERE company_id = ?
        """,
        (company_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [{"document_id": r[0]} for r in rows]


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


def get_rules_by_framework(framework: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rule_id, category, title, description, severity, evidence_required
        FROM audit_rules
        WHERE framework = ?
        """,
        (framework,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "rule_id": r[0],
            "category": r[1],
            "title": r[2],
            "description": r[3],
            "severity": r[4],
            "evidence_required": json.loads(r[5])
        }
        for r in rows
    ]
