from infra.db.db import get_connection
import json
from config.logger import get_logger

logger = get_logger(__name__)



def delete_company(company_id: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Delete audit history for this company
            cursor.execute(
                "DELETE FROM company_audit_history WHERE company_id = %s",
                (company_id,)
            )

            # 2. Delete document_audits linked to this company's documents
            cursor.execute(
                """
                DELETE FROM document_audits
                WHERE document_id IN (
                    SELECT document_id FROM documents WHERE company_id = %s
                )
                """,
                (company_id,)
            )

            # 3. Delete the documents themselves
            cursor.execute(
                "DELETE FROM documents WHERE company_id = %s",
                (company_id,)
            )

            # 4. Now safely delete the company
            cursor.execute(
                """
                DELETE FROM companies
                WHERE company_id = %s
                RETURNING company_id
                """,
                (company_id,)
            )

            deleted = cursor.fetchone()
            conn.commit()

    return deleted


def delete_documents_by_company(company_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        # First delete related document_audits for all documents of this company
        cursor.execute(
            """
            DELETE FROM document_audits
            WHERE document_id IN (
                SELECT document_id FROM documents WHERE company_id = %s
            )
            """,
            (company_id,)
        )

        cursor.execute(
            """
            DELETE FROM documents
            WHERE company_id = %s
            RETURNING document_id
            """,
            (company_id,)
        )

        deleted = cursor.fetchall()
        conn.commit()

    return deleted


def delete_document_by_id(document_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        # First delete related document_audits to avoid FK constraint violation
        cursor.execute(
            """
            DELETE FROM document_audits
            WHERE document_id = %s
            """,
            (document_id,)
        )

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

    return deleted