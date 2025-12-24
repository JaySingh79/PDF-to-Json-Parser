import streamlit as st
import fitz
import camelot
import pytesseract
import pandas as pd
import numpy as np
from PIL import Image
import io
import tempfile
import os


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if not os.path.exists(TESSERACT_PATH):
    raise RuntimeError(f"Tesseract not found at {TESSERACT_PATH}")

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

st.set_page_config(layout="wide")
st.title("Multi-Page Table Evidence & Confidence Demo")



# Upload PDF
pdf_file = st.file_uploader("Upload a multi-page PDF with tables", type=["pdf"])
if not pdf_file:
    st.stop()

doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
num_pages = doc.page_count

st.sidebar.header("Page Selection")
page_number = st.sidebar.selectbox(
    "Select page to inspect",
    list(range(1, num_pages + 1))
)

page_index = page_number - 1
page = doc[page_index]



### Extract Page Image
pix = page.get_pixmap(dpi=200)
page_image = Image.open(io.BytesIO(pix.tobytes("png")))
img_np = np.array(page_image)

# -------------------------
# Extract Tables 
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    tmp_file.write(pdf_file.getbuffer())
    temp_pdf_path = tmp_file.name
    
    
tables = camelot.read_pdf(
    temp_pdf_path,
    pages=str(page_number),
    flavor="stream"
)

if len(tables) == 0:
    st.warning("No tables detected on this page")
    st.image(page_image, use_column_width=True)
    st.stop()

pdf_table = tables[0].df

##OCR
ocr_data = pytesseract.image_to_data(
    img_np, output_type=pytesseract.Output.DICT
)

ocr_text = " ".join(ocr_data["text"])
ocr_confidences = [
    c for c in ocr_data["conf"]
    if isinstance(c, int) and c > 0
]

ocr_conf = (
    sum(ocr_confidences) / len(ocr_confidences) / 100
    if ocr_confidences else 0
)

## using hard code weights for now
# Confidence Math
def structural_confidence(df, ocr_txt):
    rows = len(df)
    ocr_row_est = max(1, ocr_txt.count("\n"))
    return max(0, 1 - abs(rows - ocr_row_est) / rows)

def agreement_confidence(df, ocr_txt):
    pdf_tokens = set(" ".join(df.astype(str).values.flatten()).split())
    ocr_tokens = set(ocr_txt.split())
    if not pdf_tokens:
        return 0
    return len(pdf_tokens & ocr_tokens) / len(pdf_tokens)

struct_conf = structural_confidence(pdf_table, ocr_text)
agree_conf = agreement_confidence(pdf_table, ocr_text)

final_conf = (
    0.4 * struct_conf +
    0.3 * ocr_conf +
    0.3 * agree_conf
)



if final_conf >= 0.8:
    mode = "TEXT"
elif final_conf >= 0.6:
    mode = "QUOTED"
else:
    mode = "IMAGE"




st.subheader(f"Page {page_number} Decision")
st.code(f"Answer Mode → {mode}")
st.metric("Final Confidence", round(final_conf, 2))

st.subheader("Confidence Breakdown")
st.json({
    "structural": round(struct_conf, 2),
    "ocr": round(ocr_conf, 2),
    "agreement": round(agree_conf, 2)
})

if mode == "TEXT":
    st.success("High confidence table extraction")
    st.dataframe(pdf_table)

elif mode == "QUOTED":
    st.warning("Medium confidence – showing both evidences")
    st.markdown("### PDF Extracted Table")
    st.dataframe(pdf_table)
    st.markdown("### OCR Evidence (page-level)")
    st.code(ocr_text[:800])

else:
    st.error("Low confidence – showing source page")
    st.image(page_image, use_column_width=True)



with st.expander("Debug Evidence (Page-level)"):
    st.markdown("**OCR Raw Text (truncated)**")
    st.code(ocr_text[:1500])
