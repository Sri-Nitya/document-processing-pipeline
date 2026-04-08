import json
import os
import re
from typing import List
from groq import Groq

from app.schemas import PageData, ItemizedBillAgentOutput
from app.utils.json_parser import extract_json_from_text

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_itemized_bill_data(pages: List[PageData]) -> ItemizedBillAgentOutput:
    if not pages:
        return ItemizedBillAgentOutput()

    combined_text = "\n\n".join(
        [f"Page {page.page_number}:\n{page.text[:4000]}" for page in pages]
    )

    prompt = f"""
    You are an itemized bill extraction agent for health insurance claim documents.

    Extract:
    - items: list of bill items with item name and amount
    - total_amount: Sum of all total amounts on the bill

    Return ONLY valid JSON in this exact format:
    {{
    "items": [
        {{
        "item": "string",
        "amount": 0.0
        }}
    ],
    "total_amount": 0.0
    }}

    Rules:
    - If exact line items are unclear, return the most confident bill items you can identify.
    - total_amount should be numeric.
    - Do not return text outside JSON.

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

        return ItemizedBillAgentOutput(**data)
    except Exception as e:
        raise ValueError(f"Failed to parse itemized bill data: {e}")