from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path
from datetime import datetime


def render_audit_report_pdf(report: dict) -> str:
    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    metadata = report["report_metadata"]
    filename = f"{metadata['company_name'].replace(' ', '_')}_{metadata['audit_id']}.pdf"
    pdf_path = reports_dir / filename

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    x_margin = 40
    y = height - 40

    def draw_heading(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, y, text)
        y -= 20

    def draw_subheading(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_margin, y, text)
        y -= 15

    def draw_text(text):
        nonlocal y
        c.setFont("Helvetica", 10)
        for line in text.split("\n"):
            if y < 60:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 40
            c.drawString(x_margin, y, line)
            y -= 14

    # ---------- COVER ----------
    draw_heading("Independent Financial Audit Report")
    draw_text(f"Company: {metadata['company_name']}")
    draw_text(f"Audit ID: {metadata['audit_id']}")
    draw_text(f"Audit Date: {metadata['audit_date']}")
    draw_text(f"Overall Status: {metadata['overall_status']}")
    y -= 20

    # ---------- EXECUTIVE SUMMARY ----------
    draw_heading("Executive Summary")
    draw_text(report.get("executive_summary", ""))
    y -= 10

    # ---------- RISK OVERVIEW ----------
    risk = report.get("risk_overview", {})
    draw_heading("Risk Overview")
    draw_text(
        f"Total Documents: {risk.get('total_documents', 0)}\n"
        f"Verified: {risk.get('verified_documents', 0)}\n"
        f"Flagged: {risk.get('flagged_documents', 0)}\n"
        f"Failed: {risk.get('failed_documents', 0)}\n"
        f"Overall Risk Level: {risk.get('risk_level', 'N/A')}"
    )
    y -= 10

    # ---------- DOCUMENT FINDINGS ----------
    draw_heading("Document-wise Findings")

    for doc in report.get("document_findings", []):
        draw_subheading(f"Document: {doc['document_id']}")
        draw_text(f"Status: {doc['status']}")

        if doc.get("critical_issues"):
            draw_text("Critical Issues:")
            for issue in doc["critical_issues"]:
                draw_text(f"- {issue}")

        if doc.get("observations"):
            draw_text("Observations:")
            for obs in doc["observations"]:
                draw_text(f"- {obs}")

        draw_text(doc.get("narrative", ""))
        y -= 10

    # ---------- RECOMMENDATIONS ----------
    draw_heading("Recommendations")
    for rec in report.get("recommendations", []):
        draw_text(f"- {rec}")
    y -= 10

    # ---------- DISCLAIMER ----------
    draw_heading("Auditor Disclaimer")
    draw_text(report.get("auditor_disclaimer", ""))

    c.showPage()
    c.save()

    return str(pdf_path)