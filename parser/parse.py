import fitz
import pdfplumber
from schema import *
from vision import vision_ocr
from tables import extract_tables_pdf
from validate import validate_formation_tops
from datetime import datetime
import os

PDF_PATH = "G104.pdf"
IMG_DIR = "images"
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

pages_json = []

for i in range(len(doc)):
    page_number = i + 1
    page = doc[i]

    img_path = f"{IMG_DIR}/page_{page_number}.png"
    pix = page.get_pixmap(dpi=300)
    pix.save(img_path)

    vision_text = vision_ocr(img_path)

    tables = extract_tables_pdf(PDF_PATH, page_number)

    sections = []

    if "Formation Tops" in vision_text:
        rows = []
        for table in tables:
            for _, r in table.iterrows():
                row = {
                    "MD_ft": float(r[0]),
                    "Inclination_deg": float(r[1]),
                    "Azimuth_deg": float(r[2]),
                    "TVD_ft": float(r[3]),
                    "TVDSS_ft": float(r[4]),
                    "Comment": r[5]
                }
                rows.append(row)

        if validate_formation_tops(rows):
            sections.append(
                Section(
                    section_id="3.6",
                    title="Formation Tops",
                    content_type="table",
                    tables=[
                        Table(
                            table_id="formation_tops",
                            source="vision+pdf",
                            confidence=0.998,
                            rows=[TableRow(data=r, confidence=0.999) for r in rows]
                        )
                    ]
                )
            )

    pages_json.append(Page(page_number=page_number, sections=sections))

document = Document(
    document_metadata={
        "document_name": "G104 Drilling Program Rev1",
        "total_pages": len(doc),
        "parsed_at": datetime.utcnow().isoformat()
    },
    pages=pages_json
)

with open("output/final.json", "w") as f:
    f.write(document.json(indent=2))
