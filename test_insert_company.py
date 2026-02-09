from infra.db.db_functions import get_company_by_id


company = get_company_by_id("alpha_fintech")
print(company)