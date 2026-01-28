import sqlite3

DB_PATH = "infra/db/audit.db"  # adjust if needed

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

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

    started_at DATETIME,
    completed_at DATETIME,

    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
"""

cursor.executescript(sql)
conn.commit()
conn.close()

print("document_audits table recreated successfully")
