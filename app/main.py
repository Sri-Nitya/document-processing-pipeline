from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.utils.pdf_extractor import extract_pages_from_pdf
from app.schemas import PageData
from app.graph import build_claim_processing_graph

app = FastAPI(title="Claim Processing Pipeline")
claim_graph = build_claim_processing_graph()

@app.post("/api/process")
async def process_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    pdf_content = await file.read()
    extracted_pages = extract_pages_from_pdf(pdf_content)

    pages = [PageData(**page) for page in extracted_pages]
    
    initial_state = {
        "claim_id": claim_id,
        "pdf_bytes": pdf_content,
        "pages": pages,
        "segregation_result": None,
        "id_result": None,
        "discharge_result": None,
        "itemized_bill_result": None,
        "final_output": None,
    }

    final_state = claim_graph.invoke(initial_state)

    return final_state["final_output"]