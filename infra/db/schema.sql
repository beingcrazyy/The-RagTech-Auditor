-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS document_audits CASCADE;
DROP TABLE IF EXISTS audit_rules CASCADE;
DROP TABLE IF EXISTS company_audit_history CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- =========================
-- COMPANIES
-- =========================
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_description TEXT,
    company_category TEXT NOT NULL,
    company_country TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- DOCUMENTS
-- =========================
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id),
    CONSTRAINT uq_company_file UNIQUE (company_id, file_name)
);

-- =========================
-- COMPANY AUDIT HISTORY
-- =========================
CREATE TABLE company_audit_history (
    audit_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,

    status TEXT CHECK (status IN ('RUNNING', 'COMPLETED')) NOT NULL,

    total_documents INTEGER DEFAULT 0,
    processed_documents INTEGER DEFAULT 0,

    verified_documents INTEGER DEFAULT 0,
    flagged_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    out_of_scope_documents INTEGER DEFAULT 0,

    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    report_path TEXT,

    CONSTRAINT fk_audit_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- =========================
-- AUDIT RULES
-- =========================
CREATE TABLE audit_rules (
    rule_id TEXT PRIMARY KEY,
    framework TEXT,
    category TEXT,
    title TEXT,
    description TEXT,
    severity TEXT
);

-- =========================
-- DOCUMENT AUDITS
-- =========================
CREATE TABLE document_audits (
    document_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    audit_id TEXT NOT NULL,

    status TEXT CHECK (status IN ('IN_PROGRESS', 'COMPLETED')),
    result TEXT CHECK (result IN ('VERIFIED', 'FLAGGED', 'FAILED')),
    progress INTEGER CHECK (progress BETWEEN 0 AND 100),

    current_step TEXT,
    file_type TEXT,
    document_type TEXT,

    is_active BOOLEAN DEFAULT FALSE,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    last_heartbeat_at TIMESTAMP WITH TIME ZONE,

    hard_failures TEXT,
    soft_failures TEXT,
    audit_summary TEXT,

    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_doc_audit_document
        FOREIGN KEY (document_id) REFERENCES documents(document_id),

    CONSTRAINT fk_doc_audit_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id),

    CONSTRAINT fk_doc_audit_audit
        FOREIGN KEY (audit_id) REFERENCES company_audit_history(audit_id)
);

-- =========================
-- SEED AUDIT RULES
-- =========================
INSERT INTO audit_rules
(rule_id, framework, category, title, description, severity)
VALUES
('FIN_INV_STRUCT_001','FINANCIAL','Structural','Missing invoice number','Invoice must have an invoice number','HARD'),
('FIN_INV_STRUCT_002','FINANCIAL','Structural','Missing invoice date','Invoice must have an invoice date','HARD'),
('FIN_INV_STRUCT_003','FINANCIAL','Structural','Missing total amount','Invoice must have total amount','HARD'),
('FIN_INV_STRUCT_004','FINANCIAL','Structural','Missing currency','Invoice currency is missing','SOFT'),
('FIN_INV_MATH_001','FINANCIAL','Arithmetic','Subtotal + CGST + SGST mismatch','Subtotal + CGST + SGST must equal total','HARD'),
('FIN_INV_MATH_002','FINANCIAL','Arithmetic','Subtotal + IGST mismatch','Subtotal + IGST must equal total','HARD'),
('FIN_INV_LOGIC_001','FINANCIAL','Logical','CGST and SGST mismatch','CGST and SGST should be equal','SOFT'),
('FIN_INV_BANK_001','FINANCIAL','Cross Document','Invoice not found in bank','Invoice amount not found in bank credits','HARD'),
('FIN_INV_PL_001','FINANCIAL','Cross Document','Invoice missing in P&L','Invoice not reflected in P&L statement','SOFT');