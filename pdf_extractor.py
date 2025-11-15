import pymupdf  # PyMuPDF
from cleaner import cleaner

# used in APP.PY to extract text from pdf
def pdf_extractor(pdf_path):
    text = ""
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text()
            text += page_text + " "
    return cleaner(text)