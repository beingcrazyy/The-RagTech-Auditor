from infra.db.db import get_connection

RULES = [
    ("FIN_INV_STRUCT_001","FINANCIAL","Structural","Missing invoice number","Invoice must have an invoice number","HARD"),
    ("FIN_INV_STRUCT_002","FINANCIAL","Structural","Missing invoice date","Invoice must have an invoice date","HARD"),
    ("FIN_INV_STRUCT_003","FINANCIAL","Structural","Missing total amount","Invoice must have total amount","HARD"),
    ("FIN_INV_STRUCT_004","FINANCIAL","Structural","Missing currency","Invoice currency is missing","SOFT"),
    ("FIN_INV_MATH_001","FINANCIAL","Arithmetic","Subtotal + CGST + SGST mismatch","Subtotal + CGST + SGST must equal total","HARD"),
    ("FIN_INV_MATH_002","FINANCIAL","Arithmetic","Subtotal + IGST mismatch","Subtotal + IGST must equal total","HARD"),
    ("FIN_INV_LOGIC_001","FINANCIAL","Logical","CGST and SGST mismatch","CGST and SGST should be equal","SOFT"),
    ("FIN_INV_BANK_001","FINANCIAL","Cross Document","Invoice not found in bank","Invoice amount not found in bank credits","HARD"),
    ("FIN_INV_PL_001","FINANCIAL","Cross Document","Invoice missing in P&L","Invoice not reflected in P&L statement","SOFT"),
]

with get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO audit_rules
            (rule_id, framework, category, title, description, severity)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (rule_id) DO NOTHING
            """,
            RULES
        )
        conn.commit()

print("✅ Financial rules seeded")
