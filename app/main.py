from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.utils.pdf_extractor import extract_pages_from_pdf

app = FastAPI(title="Claim Processing Pipeline")
@app.post("/api/process")
async def process_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...)
):
    pdf_content = await file.read()
    extracted_pages = extract_pages_from_pdf(pdf_content)
    return JSONResponse(
        content={
            "claim_id": claim_id,
            "filename": file.filename,
            "total_pages": len(extracted_pages),
            "pages": extracted_pages
        }
    )