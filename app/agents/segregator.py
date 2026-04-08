from typing import List
import json
import os
import re
from groq import Groq

from app.schemas import PageData, SegregationResult
from app.utils.json_parser import extract_json_from_text

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_segregator_prompt(pages: List[PageData]) -> str:
    page_sections = []

    for page in pages:
        text = (page.text or "").strip()
        if not text:
            text = "[EMPTY OCR TEXT]"
        text = text[:2000]

        page_sections.append(f"Page {page.page_number}:\n{text}")

    all_pages = "\n\n".join(page_sections)

    return f"""
        You are a precise document classification assistant.

        Classify each page into exactly one of these document types:
        - claim_forms
        - cheque_or_bank_details
        - identity_document
        - itemized_bill
        - discharge_summary
        - prescription
        - investigation_report
        - cash_receipt
        - other

        Rules:
        1. Return exactly one result per page.
        2. Use the field name "doc_type".
        3. Return ONLY valid JSON.
        4. Do not include markdown.
        5. Do not include explanation outside JSON.

        Return JSON in exactly this format:
        {{
        "segregation": [
            {{
            "page_number": 1,
            "doc_type": "identity_document",
            "reason": "Contains DOB details"
            }}
        ]
        }}

        Pages:
        {all_pages}
        """.strip()

def segregate_pages(pages: List[PageData]) -> SegregationResult:
    prompt = build_segregator_prompt(pages)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content or ""

    try:
        json_text = extract_json_from_text(content)
        data = json.loads(json_text)
        return SegregationResult(**data)
    except Exception as e:
        raise ValueError(f"Failed to parse segregation result: {e}")