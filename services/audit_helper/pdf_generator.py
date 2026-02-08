from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from pathlib import Path


def safe_text(value):
    if value is None:
        return "—"
    return str(value)

def render_audit_report_pdf(report: dict) -> str:
    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    metadata = report["report_metadata"]
    filename = f"{metadata['company_name'].replace(' ', '_')}_{metadata['audit_id']}.pdf"
    pdf_path = reports_dir / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Independent Financial Audit Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Company:</b> {metadata['company_name']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Audit ID:</b> {metadata['audit_id']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Audit Date:</b> {metadata['audit_date']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Overall Status:</b> {metadata['overall_status']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk Level:</b> {metadata['risk_level']}", styles["Normal"]))

    story.append(Spacer(1, 20))


    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(report["executive_summary"], styles["Normal"]))
    story.append(Spacer(1, 16))



    doc_table_data = [
        [
            "Document ID",
            "Document Type",
            "Result",
            "Hard Issues",
            "Soft Issues"
        ]
    ]

    for row in report["tables"]["document_summary_table"]:
        doc_table_data.append([
            Paragraph(safe_text(row.get("document_id")), styles["Normal"]),
            Paragraph(safe_text(row.get("document_type")), styles["Normal"]),
            Paragraph(safe_text(row.get("result")), styles["Normal"]),
            Paragraph(safe_text(row.get("hard_issues_count")), styles["Normal"]),
            Paragraph(safe_text(row.get("soft_issues_count")), styles["Normal"]),
        ])


    doc_table = Table(doc_table_data, repeatRows=1, colWidths=[90, 90, 70, 70, 70])
    doc_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP")
    ]))

    story.append(Paragraph("<b>Document Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(doc_table)
    story.append(Spacer(1, 20))

    rule_table_data = [
        [
            "Rule ID",
            "Rule Title",
            "Severity",
            "Affected Docs Count",
            "Affected Documents"
        ]
    ]

    for rule in report["tables"]["rule_impact_table"]:
        rule_table_data.append([
            Paragraph(safe_text(rule.get("rule_id")), styles["Normal"]),
            Paragraph(safe_text(rule.get("rule_title")), styles["Normal"]),
            Paragraph(safe_text(rule.get("severity")), styles["Normal"]),
            Paragraph(safe_text(rule.get("affected_documents_count")), styles["Normal"]),
            Paragraph(safe_text(", ".join(rule.get("affected_documents", []))), styles["Normal"]),
        ])
    
    rule_table = Table(rule_table_data, repeatRows=1, colWidths=[70, 140, 70, 80, 120])
    rule_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP")
    ]))

    story.append(Paragraph("<b>Rule Impact Analysis</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(rule_table)
    story.append(Spacer(1, 20))



    risk = report["tables"]["company_risk_summary"]

    story.append(Paragraph("<b>Company Risk Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    for k, v in risk.items():
        story.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b> {v}", styles["Normal"]))

    story.append(Spacer(1, 20))


    story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
    for rec in report["recommendations"]:
        story.append(Paragraph(f"- {rec}", styles["Normal"]))

    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Auditor Disclaimer</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(report["auditor_disclaimer"], styles["Normal"]))

    doc.build(story)
    return str(pdf_path)