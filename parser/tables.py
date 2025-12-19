import camelot

def extract_tables_pdf(pdf_path, page):
    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages=str(page),
            flavor="lattice"
        )
        return [t.df for t in tables]
    except:
        return []
