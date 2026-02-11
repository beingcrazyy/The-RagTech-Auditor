import pdfplumber

def parse_pdf(file_obj) -> dict:
    raw_text = []
    tables = []
    page_text_map = {}

    with pdfplumber.open(file_obj) as pdf:
        for i, page in enumerate(pdf.pages, start = 1):
            text = page.extract_text()
            raw_text.append(text)
            page_text_map[i] = text

            page_tables = page.extract_tables()
            if page_tables:
                tables.append(page_tables)
    
    return{
        "raw_text" : "/n".join(raw_text),
        "tables" : tables,
        "page_text_map" : page_text_map
    }