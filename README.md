# The RegTech Auditor — Backend

Welcome to the **RegTech Auditor** backend. This system provides an intelligent, automated compliance auditing solution for enterprises. It ingests documents (such as invoices and bank statements), extracts data, validates it against predefined rule sets, and generates audit reports using AI-driven logic.

## Overview

The RegTech Auditor employs a sophisticated **Graph-based Architecture** (powered by LangGraph) to process documents through a structured audit pipeline. It leverages Generative AI (OpenAI) to classify documents, extract unstructured data, and generate comprehensive summaries and reports.

## Features

- **Company Management**: Create and manage company profiles.
- **Document Ingestion**: Upload various document types (PDFs, Images) with automatic type detection (Invoice, Bank Statement, P&L, etc.).
- **Automated Auditing**:
    - **Heuristic & LLM Classification**: Accurately identifies document types.
    - **Extraction**: Extracts key fields (Invoice Number, Date, Totals, Tax Breakups).
    - **Validation**: Executes rule-based checks (e.g., Math validation: Subtotal + Tax = Total).
    - **Decision Engine**: Automatically Flags, Verifies, or Fails documents based on confidence scores and hard/soft failures.
- **Human-in-the-Loop**: Enables auditors to override system decisions and provide feedback.
- **Real-time Dashboard**: Track audit progress, flagged documents, and overall compliance health.
- **Audit History**: Maintains a complete history of all audits and their outcomes.

## Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL (Robust, production-grade relational database)
- **AI/LLM**: [LangChain](https://www.langchain.com/), [OpenAI](https://openai.com/)
- **Orchestration**: LangGraph (for stateful audit workflows)
- **Vector Search**: FAISS (for document similarity/search, if enabled)
- **PDF Processing**: `pypdf`, `pdfplumber`

## Prerequisites

- **Python 3.10+** installed.
- **PostgreSQL**: Ensure a Postgres instance is running and accessible.
- **OpenAI API Key**: Required for classification and extraction features.

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd backend-the-ragtech-auditor
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   MODEL_NAME=gpt-4o-mini
   TEMPERATURE=0
   
   # Database Configuration
   POSTGRES_HOST=localhost
   POSTGRES_DB=regtechdb
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   POSTGRES_PORT=5432
   POSTGRES_SSLMODE=prefer
   ```

## Running the Application

1. **Initialize the Database**
   This command initializes the database schema and seeds initial rules.
   ```bash
   python infra/db/init_db.py
   python -m infra.db.seed_financial_rules
   ```

2. **Start the API Server**
   ```bash
   python -m uvicorn services.api.app:app --reload
   ```
   The server will start at `http://127.0.0.1:8000`.

## Project Structure

- **`core/`**: Application logic, including the LangGraph workflow (`graph/`), state definitions, and validation rules.
- **`infra/db/`**: Database configuration and repositories.
    - **`db_functions/`**: Modularized database access functions (Company, Document, Audit, Dashboard).
- **`services/api/`**: FastAPI route handlers grouped by feature.
- **`services/classifiers/`**: Heuristic and LLM-based document classifiers.
- **`services/extractor/`**: Logic for extracting data from documents.
- **`services/orchestrater/`**: Helpers for batch processing.

## API Documentation

The interactive API documentation (Swagger UI) is available at:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

For a static reference, please see [api_documentation.md](api_documentation.md).
