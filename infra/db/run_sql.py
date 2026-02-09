from infra.db.db import get_connection

def recreate_document_audits():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                DROP TABLE IF EXISTS document_audits;

                CREATE TABLE IF NOT EXISTS document_audits (
                    document_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,

                    status TEXT,
                    progress INTEGER,
                    audit_summary TEXT,
                    hard_failures TEXT,
                    soft_failures TEXT,

                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE,

                    FOREIGN KEY (document_id) REFERENCES documents(document_id),
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                );
                """
                cursor.execute(sql)
                conn.commit()
                print("document_audits table recreated successfully")
    except Exception as e:
        print(f"Error recreating document_audits table: {e}")

if __name__ == "__main__":
    recreate_document_audits()
