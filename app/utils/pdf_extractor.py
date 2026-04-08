import fitz
import pytesseract
from PIL import Image
from typing import List, Dict
import io

def extract_pages_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        text = pytesseract.image_to_string(image).strip()

        pages.append({
            "page_number": i + 1,
            "text": text
        })

    doc.close()
    return pages