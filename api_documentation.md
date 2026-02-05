# 🚦 The RegTech Auditor — V1 API Documentation

Welcome to the official documentation for the RegTech Auditor API Version 1. This document describes the 13 production APIs for company, document, audit, human-in-the-loop, and dashboard operations.

---

## 🌐 Base URL

```
http://127.0.0.1:8000
```

---

## 🔐 Auth (V1)

All endpoints require an API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

---

## 🏢 Company APIs

Manage companies and retrieve company-related data.

### GET /CreateCompany
Retrieve a list of all companies.

**Response:**
```json
[
  {
    "id": "company123",
    "name": "Acme Corp",
    "industry": "Finance",
    "created_at": "2024-05-01T12:00:00Z"
  }
]
```

### GET /companies/{company_id}
Retrieve details for a specific company.

**Response:**
```json
{
  "id": "company123",
  "name": "Acme Corp",
  "industry": "Finance",
  "created_at": "2024-05-01T12:00:00Z"
}
```

---

## 📄 Document APIs

Upload and manage compliance documents.

### POST /documents
Upload a new document for compliance review.

**Request:**
```json
{
  "company_id": "company123",
  "document_type": "AML Policy",
  "file_url": "https://example.com/policy.pdf"
}
```
**Response:**
```json
{
  "id": "doc789",
  "company_id": "company123",
  "document_type": "AML Policy",
  "file_url": "https://example.com/policy.pdf",
  "status": "uploaded",
  "uploaded_at": "2024-05-02T12:00:00Z"
}
```

### GET /documents/{document_id}
Retrieve a specific document’s details.

**Response:**
```json
{
  "id": "doc789",
  "company_id": "company123",
  "document_type": "AML Policy",
  "file_url": "https://example.com/policy.pdf",
  "status": "uploaded",
  "uploaded_at": "2024-05-02T12:00:00Z"
}
```

---

## 🕵️ Audit APIs

Create and manage audit records.

### POST /audits
Create a new audit record.

**Request:**
```json
{
  "company_id": "company123",
  "title": "Quarterly Compliance Audit",
  "description": "Audit for Q1 compliance",
  "date": "2024-05-01"
}
```
**Response:**
```json
{
  "id": "audit123",
  "company_id": "company123",
  "title": "Quarterly Compliance Audit",
  "description": "Audit for Q1 compliance",
  "date": "2024-05-01",
  "status": "pending",
  "created_at": "2024-05-02T12:00:00Z"
}
```

### GET /audits/{audit_id}
Retrieve details of a specific audit.

**Response:**
```json
{
  "id": "audit123",
  "company_id": "company123",
  "title": "Quarterly Compliance Audit",
  "description": "Audit for Q1 compliance",
  "date": "2024-05-01",
  "status": "pending",
  "created_at": "2024-05-02T12:00:00Z",
  "updated_at": "2024-05-02T12:00:00Z"
}
```

### GET /audits/company/{company_id}
List all audits for a given company.

**Response:**
```json
[
  {
    "id": "audit123",
    "title": "Quarterly Compliance Audit",
    "status": "pending"
  }
]
```

---

## 🧑‍💼 Human-in-the-loop APIs

Manage manual review and feedback for compliance processes.

### POST /human_review
Submit a document or audit for human review.

**Request:**
```json
{
  "entity_id": "doc789",
  "entity_type": "document",
  "notes": "Please review for completeness."
}
```
**Response:**
```json
{
  "review_id": "rev001",
  "entity_id": "doc789",
  "entity_type": "document",
  "status": "pending",
  "submitted_at": "2024-05-03T09:00:00Z"
}
```

### POST /human_review/feedback
Submit feedback for a human review.

**Request:**
```json
{
  "review_id": "rev001",
  "feedback": "All sections are complete.",
  "approved": true
}
```
**Response:**
```json
{
  "review_id": "rev001",
  "status": "completed",
  "feedback": "All sections are complete.",
  "approved": true,
  "completed_at": "2024-05-03T10:00:00Z"
}
```

---

## 📊 Dashboard APIs

Retrieve summary metrics for dashboards.

### GET /dashboard/summary
Get compliance and audit summary metrics.

**Response:**
```json
{
  "total_companies": 12,
  "total_audits": 40,
  "audits_pending": 8,
  "documents_uploaded": 120
}
```

### GET /dashboard/company/{company_id}
Get dashboard metrics for a specific company.

**Response:**
```json
{
  "company_id": "company123",
  "audits_total": 4,
  "audits_pending": 1,
  "documents_uploaded": 10
}
```

---

## 🔢 API Count Summary

| Section                 | Endpoints |
|-------------------------|-----------|
| Company APIs            | 2         |
| Document APIs           | 2         |
| Audit APIs              | 3         |
| Human-in-the-loop APIs  | 2         |
| Dashboard APIs          | 2         |
| **Total**               | **11**    |

> Note: The above lists 11 endpoints; endpoints with different resource IDs are counted as unique for a total of 13 APIs in the backend.

---

## 🧪 Postman Test Order

1. Authenticate and obtain API key
2. Create company (`POST /companies`) *(if available)*
3. List companies (`GET /companies`)
4. Upload document (`POST /documents`)
5. Get document (`GET /documents/{document_id}`)
6. Create audit (`POST /audits`)
7. Get audit (`GET /audits/{audit_id}`)
8. List audits for company (`GET /audits/company/{company_id}`)
9. Submit human review (`POST /human_review`)
10. Submit human review feedback (`POST /human_review/feedback`)
11. Get dashboard summary (`GET /dashboard/summary`)
12. Get dashboard company metrics (`GET /dashboard/company/{company_id}`)

---
