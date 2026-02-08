from infra.db.db import get_connection
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
