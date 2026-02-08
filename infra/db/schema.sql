-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS document_audits;
DROP TABLE IF EXISTS audit_rules;
DROP TABLE IF EXISTS company_audit_history;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS companies;

-- Create tables in dependency order

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_description TEXT,
    company_category TEXT NOT NULL,
    company_country TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, file_name)
);

CREATE TABLE company_audit_history (
    audit_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,

    status TEXT CHECK(status IN ('RUNNING', 'COMPLETED')) NOT NULL,

    total_documents INTEGER DEFAULT 0,
    processed_documents INTEGER DEFAULT 0,

    verified_documents INTEGER DEFAULT 0,
    flagged_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    out_of_scope_documents INTEGER DEFAULT 0,

    started_at DATETIME,
    completed_at DATETIME, 
    report_path TEXT,

    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE audit_rules (
    rule_id TEXT PRIMARY KEY,
    framework TEXT,
    category TEXT,
    title TEXT,
    description TEXT,
    severity TEXT
);

CREATE TABLE document_audits (
    document_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    audit_id TEXT NOT NULL,

    status TEXT CHECK(status IN ('IN_PROGRESS','COMPLETED')),
    result TEXT CHECK(result IN ('VERIFIED','FLAGGED','FAILED')),
    progress INTEGER CHECK(progress BETWEEN 0 AND 100),

    current_step TEXT,                 -- which node is running
    file_type TEXT,
    document_type TEXT,

    is_active INTEGER DEFAULT 0,
    processing_started_at DATETIME,
    last_heartbeat_at DATETIME,

    hard_failures TEXT,
    soft_failures TEXT,
    audit_summary TEXT,

    started_at DATETIME,
    completed_at DATETIME,

    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (audit_id) REFERENCES company_audit_history(audit_id)
);


-- Seed Rules
INSERT INTO audit_rules
(rule_id, framework, category, title, description, severity)
VALUES
-- Structural
('FIN_INV_STRUCT_001','FINANCIAL','Structural','Missing invoice number','Invoice must have an invoice number','HARD'),
('FIN_INV_STRUCT_002','FINANCIAL','Structural','Missing invoice date','Invoice must have an invoice date','HARD'),
('FIN_INV_STRUCT_003','FINANCIAL','Structural','Missing total amount','Invoice must have total amount','HARD'),
('FIN_INV_STRUCT_004','FINANCIAL','Structural','Missing currency','Invoice currency is missing','SOFT'),

-- Arithmetic
('FIN_INV_MATH_001','FINANCIAL','Arithmetic','Subtotal + CGST + SGST mismatch','Subtotal + CGST + SGST must equal total','HARD'),
('FIN_INV_MATH_002','FINANCIAL','Arithmetic','Subtotal + IGST mismatch','Subtotal + IGST must equal total','HARD'),

-- Logical
('FIN_INV_LOGIC_001','FINANCIAL','Logical','CGST and SGST mismatch','CGST and SGST should be equal','SOFT'),

-- Cross Document
('FIN_INV_BANK_001','FINANCIAL','Cross Document','Invoice not found in bank','Invoice amount not found in bank credits','HARD'),
('FIN_INV_PL_001','FINANCIAL','Cross Document','Invoice missing in P&L','Invoice not reflected in P&L statement','SOFT');
