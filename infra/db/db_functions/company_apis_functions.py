from infra.db.postgres import get_connection
from config.logger import get_logger

logger = get_logger(__name__)

# -------------------------
# COMPANY
# -------------------------

def insert_company(company_id, company_name, company_category, company_country, company_description):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO companies (
                        company_id, company_name, company_category, company_country, company_description
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (company_id, company_name, company_category, company_country, company_description)
                )
                conn.commit()
        return True
    except Exception as e:
        logger.error("Error inserting company: %s", e, exc_info=True)
        return False


def get_company_by_id(company_id: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        company_id,
                        company_name,
                        company_category,
                        company_country,
                        company_description
                    FROM companies
                    WHERE company_id = %s
                    """,
                    (company_id,)
                )

                row = cursor.fetchone()
                if row is None:
                    return None

                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

    except Exception as e:
        logger.error("Error fetching company by id: %s", e, exc_info=True)
        return None
    



def get_all_companies():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.company_id,
                        c.company_name,
                        c.company_category,
                        c.company_country,
                        COUNT(d.document_id) AS total_documents,
                        COUNT(CASE WHEN da.result='VERIFIED' THEN 1 END),
                        COUNT(CASE WHEN da.result='FLAGGED' THEN 1 END),
                        COUNT(CASE WHEN da.result='FAILED' THEN 1 END)
                    FROM companies c
                    LEFT JOIN documents d ON c.company_id = d.company_id
                    LEFT JOIN document_audits da ON d.document_id = da.document_id
                    GROUP BY c.company_id
                    """
                )
                rows = cursor.fetchall()
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
    except Exception as e:
        logger.error("Error getting all companies: %s", e, exc_info=True)
        return []
