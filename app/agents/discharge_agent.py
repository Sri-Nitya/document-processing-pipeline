import json
import os
import re
from typing import List
from groq import Groq

from app.schemas import PageData, DischargeSummaryAgentOutput
from app.utils.json_parser import extract_json_from_text

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_discharge_summary_data(pages: List[PageData]) -> DischargeSummaryAgentOutput:
    if not pages:
        return DischargeSummaryAgentOutput()

    combined_text = "\n\n".join(
        [f"Page {page.page_number}:\n{page.text[:3000]}" for page in pages]
    )

    prompt = f"""
        You are a discharge summary extraction agent for health insurance claim documents.

        Extract the following fields:
        - diagnosis
        - admit_date
        - discharge_date
        - physician_details

        Return ONLY valid JSON in this exact format:
        {{
        "diagnosis": "string or null",
        "admit_date": "string or null",
        "discharge_date": "string or null",
        "physician_details": "string or null"
        }}

        Pages:
        {combined_text}
        """.strip()

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

        return DischargeSummaryAgentOutput(**data)
    except Exception as e:
        raise ValueError(f"Failed to parse discharge summary data: {e}")