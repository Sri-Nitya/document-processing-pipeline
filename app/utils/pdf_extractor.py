import fitz
import pytesseract
from PIL import Image, ImageEnhance
from typing import List, Dict
import io
import base64

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.5)
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    return image


def ocr_image(image: Image.Image, psm: int = 6) -> str:
    processed = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(
        processed,
        config=f"--oem 3 --psm {psm}"
    )
    return text.strip()


def extract_pages_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        full_text = ocr_image(image, psm=6)

        pages.append({
            "page_number": i + 1,
            "text": full_text
        })

    doc.close()
    return pages

def render_pdf_page_to_base64_image(pdf_bytes: bytes, page_number: int, zoom: int = 2) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_number - 1]

    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))

    doc.close()

    max_pixels = 30_000_000
    current_pixels = image.width * image.height

    if current_pixels > max_pixels:
        scale = (max_pixels / current_pixels) ** 0.5
        new_size = (
            int(image.width * scale),
            int(image.height * scale)
        )
        image = image.resize(new_size)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")