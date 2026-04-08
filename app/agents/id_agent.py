import json
import os
import re
from typing import List
from groq import Groq

from app.schemas import IDAgentOutput
from app.utils.json_parser import extract_json_from_text

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_id_data_from_images(page_images_base64: List[str]) -> IDAgentOutput:
    if not page_images_base64:
        return IDAgentOutput()

    content = [
        {
            "type": "text",
            "text": """
                You are an ID extraction agent for health insurance claim documents.

                Extract these fields from the image(s):
                - patient_name
                - date_of_birth
                - id_numbers (list)
                - policy_details

                Rules:
                1. Read the text visible in the image carefully.
                2. ID numbers may appear as ID Number, Document Number, License Number, Member ID, Policy Number, etc.
                3. If policy details are not present, return null.
                4. Return ONLY valid JSON.
                5. Do not include markdown fences.

                Return JSON in exactly this format:
                {
                "patient_name": "string or null",
                "date_of_birth": "string or null",
                "id_numbers": ["string"],
                "policy_details": "string or null"
                }
                """.strip()
        }
    ]

    for img_b64 in page_images_base64:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            }
        )

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0,
        max_completion_tokens=500,
    )

    raw_content = response.choices[0].message.content or ""
    
    try:
        json_text = extract_json_from_text(raw_content)
        data = json.loads(json_text)

        return IDAgentOutput(**data)
    except Exception as e:
        raise ValueError(f"Failed to parse ID agent output: {e}")