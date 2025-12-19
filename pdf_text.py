## EXTRACTING TEXT USING PYPDF

# from pypdf import PdfReader
# reader = PdfReader("D:/Resources/Assignment Task_ PDF Parsing.pdf")
# text=""
# for index, page in enumerate(reader.pages):
#     text+=f'Page {index+1}\n{page.extract_text()}\n\n'
# meta = reader.metadata    
# print(meta,meta.author, meta.producer, meta.creator, meta.title, meta.subject, sep="\n\n")
# print()





### TESTING PDFPLUMBER

# with pdfplumber.open("D:/Resources/Assignment Task_ PDF Parsing.pdf") as pdf:
#     first_page = pdf.pages[0]
#     text = first_page.extract_text()
#     print(text)
    
    
    
    
## FOR EXTRACTING TABLES    

# import pdfplumber
# with pdfplumber.open("C:/Users/binit/Downloads/[Fund Factsheet - May]360ONE-MF-May 2025.pdf.pdf") as pdf:
#     # first_page = pdf.pages[3]
#     for index, page in enumerate(pdf.pages):
#         tables = page.extract_tables()
#         for table in tables:
    
#             print(index, table, sep="\n")
#             print("\n\n")




##EXTRACTING IMAGE USING PYMUPDF
import fitz
from PIL import Image

pdf_path = "ROVA USECASE.pdf"
page_number = 16

doc = fitz.open(pdf_path)
page = doc.load_page(page_number)
# zoom = 3
dpi=300
zoom=dpi / 72
matrix = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=matrix, alpha=False)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
img.show()
# Now 'img' is a PIL Image object of the PDF page