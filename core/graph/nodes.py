from core.enums.document_results import DocumentResults
from core.enums.audit_status import AuditStatus
from core.state import AuditState
from core.enums.file_type import FileType
from core.enums.document_type import DocumentType
from core.enums.audit_status import AuditStatus
from services.parser.pdf_parser import parse_pdf
from services.classifiers.heuristics_document_classifier import heuristics_document_classifier
from services.classifiers.llm_document_classifiers import llm_document_classifier
from services.extractor.invoice_extractor import extract_invoice
from core.rules.invoice_validation import validate_invoice
from core.rules.final_decision import decide_final_status
from services.audit_helper.audit_summary_generator import generate_audit_summary
from infra.db.db_functions.audit_apis_functions import finalize_document_audit, try_finalize_company_audit
from infra.db.db_functions.document_apis_functions import update_document_state
from config.logger import get_logger
from infra.storage.blob_client import download_bytes, upload_bytes
import io


from infra.db.db_functions.audit_apis_functions import (
    get_latest_company_audit,
    get_document_audits_for_audit,
    update_company_audit_status,
    count_remaining_documents_for_audit,
    get_document_audits_for_audit
)
from infra.db.db_functions.company_apis_functions import get_company_by_id

from services.audit_helper.aggregate_functions import aggregate_company_metrics, aggregate_document_results, aggregate_rule_impact
from services.audit_helper.audit_report_generator import generate_text_audit_report
from services.audit_helper.pdf_generator import render_audit_report_pdf
from services.llm.client import get_llm_client
from datetime import datetime

logger = get_logger(__name__)

import os


def _coerce_enum(value, enum_cls):
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except Exception:
        return value


# ============================================================
# INGESTION & FILE TYPE DETECTION
# ============================================================


def ingest_node(state: AuditState) -> dict:
    try:
        logger.info(f"[{state.document_id}] Ingesting document")
        return {
            "audit_trace": state.audit_trace + ["INGEST"]
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in ingest_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


def detect_file_type_node(state: AuditState) -> dict:
    try:
        logger.info(f"[{state.document_id}] Detecting file type for {state.file_path}")
        trace = state.audit_trace + ["DETECT_FILE_TYPE"]

        _,ext = os.path.splitext(state.file_path.lower())
        ext = ext.strip()

        if ext == ".pdf":
            file_type = FileType.PDF
        elif ext in {".png", ".img", ".jpeg", ".jpg"}:
            file_type = FileType.IMAGE
        elif ext in {".xlsx", ".csv"}:
            file_type = FileType.EXCEL
        else:
            file_type = FileType.OTHER

        logger.info(f"[{state.document_id}] Detected file type: {file_type.value}")
        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=10,
            current_step="detecting file type...",
            file_type=file_type.value,
            is_active=1
        )

        return {
            "audit_trace" : trace,
            "file_type" : file_type
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in detect_file_type_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


# ============================================================
# PARSING & CLASSIFICATION
# ============================================================


def parse_pdf_node(state: AuditState) -> dict:
    try:
        state.file_type = _coerce_enum(state.file_type, FileType)
        if state.file_type != FileType.PDF:
            ft = state.file_type.value if hasattr(state.file_type, "value") else state.file_type
            logger.warning(f"[{state.document_id}] Skipping PDF parsing, file type is {ft}")
            return {}
        
        logger.info(f"[{state.document_id}] Parsing PDF")
        trace = state.audit_trace + ["PARSE_PDF"]
        file_bytes = download_bytes(state.file_path)

        result = parse_pdf(io.BytesIO(file_bytes))

        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=20,
            current_step="getting data from document",
            is_active=1
        )

        return {
            "audit_trace" : trace,
            "parsed_content" : result
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in parse_pdf_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


def classify_document_node(state: AuditState) -> dict:
    try:
        state.file_type = _coerce_enum(state.file_type, FileType)
        if state.file_type != FileType.PDF or not state.parsed_content:
            logger.warning(f"[{state.document_id}] Skipping classification: insufficient data")
            return {}
        
        logger.info(f"[{state.document_id}] Classifying document")
        text = state.parsed_content["raw_text"]

        doc_type = heuristics_document_classifier(text)

        if doc_type == DocumentType.OTHER :
            logger.info(f"[{state.document_id}] Heuristics failed, using LLM classifier")
            doc_type = llm_document_classifier(text)

        logger.info(f"[{state.document_id}] Document classified as: {doc_type.value}")
        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=30,
            current_step="Classifying document",
            document_type=doc_type.value,
            is_active=1
        )

        return {
            "audit_trace": state.audit_trace + ["CLASSIFY_DOCUMENT"],
            "document_type": doc_type
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in classify_document_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


# ============================================================
# NON-INVOICE DOCUMENT HANDLING (BANK / P&L)
# ============================================================


# Handle non-invoice document types: BANK and PL
def handle_non_invoice_node(state: AuditState) -> dict:
    state.document_type = _coerce_enum(state.document_type, DocumentType)
    if state.document_type != DocumentType.INVOICE:
        dt = state.document_type.value if hasattr(state.document_type, "value") else state.document_type
        logger.info(
            f"[{state.document_id}] Handling non-invoice / unsupported document type ({dt})"
        )

        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=80,
            current_step="processing non-invoice / unsupported document",
            is_active=1
        )

        # IMPORTANT:
        # - BANK / P&L → VERIFIED (dummy support)
        # - OTHER → FAILED (out of scope)
        result = (
            DocumentResults.VERIFIED
            if state.document_type in [DocumentType.BANK_STATEMENT, DocumentType.P_AND_L]
            else DocumentResults.FAILED
        )

        summary = (
            "Document type currently supported at a limited level."
            if result == DocumentResults.VERIFIED
            else "Document type is not supported and marked as out of scope."
        )

        return {
            "audit_trace": state.audit_trace + ["HANDLE_NON_INVOICE"],
            "status": AuditStatus.IN_PROGRESS,
            "results": result,
            "audit_summary": summary
        }

    return {}

# ============================================================
# INVOICE PROCESSING PIPELINE
# ============================================================


def extract_invoice_node(state: AuditState) -> dict:
    try:
        state.document_type = _coerce_enum(state.document_type, DocumentType)
        if state.document_type != DocumentType.INVOICE:
            logger.warning(f"[{state.document_id}] Skipping invoice extraction: document type is {state.document_type.value}")
            return {}

        logger.info(f"[{state.document_id}] Extracting invoice data")
        result = extract_invoice(state.parsed_content)
        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=50,
            current_step="extracting invoice",
            is_active=1
        )

        return {
            "audit_trace": state.audit_trace + ["EXTRACT_INVOICE"],
            "extraced_data": result.model_dump()
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in extract_invoice_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


def validate_invoice_node(state : AuditState) -> dict:
    try:
        state.document_type = _coerce_enum(state.document_type, DocumentType)
        if state.document_type != DocumentType.INVOICE:
            return {}
        
        logger.info(f"[{state.document_id}] Validating invoice data")
        validation_results = validate_invoice(state.extraced_data)

        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=70,
            current_step="validating invoice",
            hard_failures=validation_results.get("hard_failures"),
            soft_failures=validation_results.get("soft_failures"),
            is_active=1
        )

        return {
            "audit_trace": state.audit_trace + ["VALIDATE_INVOICE"],
            "validation_results": validation_results
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in validate_invoice_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


def final_decision_node(state: AuditState) -> dict:
    try:
        state.document_type = _coerce_enum(state.document_type, DocumentType)
        logger.info(f"[{state.document_id}] Making final decision")

        final_result = decide_final_status(
            validation_results=state.validation_results,
            ml_signals=state.ml_signals
        )

        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=80,
            current_step="final decision",
            is_active=1
        )

        return {
            "audit_trace": state.audit_trace + ["FINAL_DECISION"],
            "status": AuditStatus.IN_PROGRESS,      # ✅ PROCESS STATE
            "results": final_result               # ✅ AUDIT RESULT
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in final_decision_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


def audit_summery_generator_node(state : AuditState) -> dict:
    try:
        logger.info(f"[{state.document_id}] Generating audit summary")
        summary = generate_audit_summary(
            status= state.status.value,
            hard_failures=state.validation_results.get("hard_failures", []),
            soft_failures=state.validation_results.get("soft_failures", []))
        
        update_document_state(
            document_id=state.document_id,
            status="IN_PROGRESS",
            progress=90,
            current_step="generating audit summery",
            audit_summary=summary,
            is_active=1
        )

        return {
            "audit_trace": state.audit_trace + ["AUDIT_SUMMARY_GENERATOR"],
            "audit_summary": summary
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in audit_summery_generator_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


# ============================================================
# ERROR HANDLING & RETRIES
# ============================================================


def retry_detect_file_type_node(state: AuditState) -> dict:
    logger.info(f"[{state.document_id}] Retrying file type detection (Retry: {state.retry_count + 1})")

    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        progress=50,
        current_step="detecting file type"
    )

    return {
        "audit_trace": state.audit_trace + ["RETRY_DETECT_FILE_TYPE"],
        "retry_count": state.retry_count + 1
    }


def fail_node(state: AuditState) -> dict:
    logger.error(f"[{state.document_id}] Audit failed early")
    update_document_state(
        document_id=state.document_id,
        status="IN_PROGRESS",
        result="FAILED",
        progress=100,
        current_step="Document out of scope",
        is_active=0
    )
    return {
        "audit_trace": state.audit_trace + ["FAILED_EARLY"],
        "results": DocumentResults.FAILED
    }


# ============================================================
# FINALIZATION & PERSISTENCE
# ============================================================


def persist_results_node(state: AuditState) -> dict:
    try:
        logger.info(f"[{state.document_id}] Persisting results to database")

        finalize_document_audit(
            document_id=state.document_id,
            audit_summary=state.audit_summary,
            hard_failures=state.validation_results.get("hard_failures", []),
            soft_failures=state.validation_results.get("soft_failures", [])
        )

        update_document_state(
            document_id=state.document_id,
            status="COMPLETED",
            result=state.results.value,
            progress=100,
            current_step="Completed",
            is_active=0
        )

        # 🔥 NEW — attempt to finalize company audit
        try_finalize_company_audit(document_id= state.document_id)

        return {
            "audit_trace": state.audit_trace + ["PERSIST_RESULTS"]
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in persist_results_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}


# ============================================================
# COMPANY AUDIT REPORT GENERATION
# ===========================================================


def generate_audit_report_node(state: AuditState) -> dict:
    try:
        logger.info(
            f"[{state.document_id}] Checking if company audit can be finalized and report generated"
        )

        audit = get_latest_company_audit(state.company_id)
        if not audit:
            logger.warning(f"No audit found for company={state.company_id}")
            return {}

        audit_id = audit["audit_id"]

        remaining = count_remaining_documents_for_audit(audit_id)
        if remaining > 0:
            logger.info(
                f"[{state.document_id}] {remaining} documents still processing, skipping report generation"
            )
            return {}

        # Guard: only generate report once audit is completed
        if audit.get("status") != "COMPLETED":
            logger.info(f"Audit {audit_id} not completed yet, skipping report generation")
            return {}

        document_audits = get_document_audits_for_audit(audit_id)
        if not document_audits:
            logger.warning(f"No document audits found for audit_id={audit_id}")
            return {}

        company_metrics = aggregate_company_metrics(document_audits)
        document_results = aggregate_document_results(document_audits)
        rule_impact = aggregate_rule_impact(document_audits)

        if not state.company_id:
            logger.error("company_id missing in state during report generation")
            return {}

        company = get_company_by_id(state.company_id)
        if not company:
            logger.error(f"Company not found for company_id={state.company_id}")
            return {}
        
        audit_context = {
            "audit_id": audit_id,
            "started_at": audit.get("started_at"),
            "completed_at": audit.get("completed_at") or datetime.utcnow().isoformat(),
            "metrics": company_metrics,
            "rule_impact": rule_impact,
            "document_results" : document_results
        }

        llm_client = get_llm_client()

        report_json = generate_text_audit_report(
            company=company,
            audit=audit_context,
            document_audits=document_results,
            llm_client=llm_client
        )

        report_json.setdefault("report_metadata", {})
        report_json["report_metadata"].setdefault(
            "audit_date",
            datetime.utcnow().strftime("%Y-%m-%d")
        )
        report_json["report_metadata"].setdefault(
            "overall_status",
            audit.get("status", "COMPLETED")
        )

        report_json["report_metadata"].setdefault(
            "audit_id",
            audit_id
        )

        report_json["report_metadata"].setdefault(
            "company_name",
            company.get("company_name") or company.get("name") or state.company_id
        )

        pdf_path = render_audit_report_pdf(report_json)

        update_company_audit_status(
            audit_id=audit_id,
            status="COMPLETED",
            report_path=pdf_path
        )

        logger.info(
            f"[{state.document_id}] Audit report generated successfully at {pdf_path}"
        )

        return {
            "audit_trace": state.audit_trace + ["GENERATE_AUDIT_REPORT"]
        }
    except Exception as e:
        logger.error(f"[{state.document_id}] Error in generate_audit_report_node: {e}", exc_info=True)
        return {"results": DocumentResults.FAILED}
