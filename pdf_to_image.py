# from pdf2image import convert_from_path
# pdf_path = "ROVA USECASE.pdf"
# images = convert_from_path(pdf_path, poppler_path="poppler-25.07.0/Library/bin", dpi=300)
# count = 10
# for i, img in enumerate(images):
#     img.show()
#     if i>5:
#         break
    
#     count+=1

import fitz  # PyMuPDF

pdf_path = "Test Corvel WC.pdf"
page_number = 2  # 0-based index

doc = fitz.open(pdf_path)
page = doc.load_page(page_number)

pix = page.get_pixmap(dpi=300)
pix.save("page_2.png")