from infra.db.db import get_connection
import json
from config.logger import get_logger

logger = get_logger(__name__)



def delete_company(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM companies
        WHERE company_id = %s
        """,
        (company_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()



def delete_documents_by_company(company_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM documents
        WHERE company_id = %s
        """,
        (company_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()


def delete_document_by_id(document_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM documents
        WHERE document_id = %s
        RETURNING document_id
        """,
        (document_id,)
    )

    deleted = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return deleted