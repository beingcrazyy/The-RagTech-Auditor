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
    framework TEXT,
    category TEXT,
    title TEXT,
    description TEXT,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS company_audit_history (
    audit_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    status TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    details TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

INSERT OR IGNORE INTO audit_rules
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
