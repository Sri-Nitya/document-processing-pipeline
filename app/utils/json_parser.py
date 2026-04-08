import json
import re


def extract_json_from_text(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("Model returned empty response")

    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        possible_json = match.group(0)
        json.loads(possible_json)
        return possible_json

    raise ValueError(f"Could not find valid JSON in model response: {text}")