CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_description TEXT NULL,
    company_category TEXT NOT NULL,
    company_country TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    document_type TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)

    UNIQUE(company_id, file_name)
);

CREATE TABLE IF NOT EXISTS document_audits (
    document_id TEXT PRIMARY KEY,
    company_id TEXT 
    status TEXT,
    progress INTEGER,
    audit_summary TEXT,
    hard_failures TEXT,
    soft_failures TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);


CREATE TABLE IF NOT EXISTS audit_rules (
    rule_id TEXT PRIMARY KEY,
    framework TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,         -- HARD / SOFT
    evidence_required TEXT NOT NULL -- JSON list
);