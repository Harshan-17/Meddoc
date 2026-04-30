import io
import json
import os
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract

app = FastAPI(title="MedMemory AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FALLBACK_TEXT = """
Patient report summary:
- 2022: Diagnosed with Diabetes Mellitus Type 2.
- 2023: Started Metformin 500mg twice daily.
- 2024: Follow-up noted elevated HbA1c and high sugar risk.
"""


def extract_text_from_file(filename: str, content: bytes) -> str:
    """Extract text from image/PDF using OCR; fallback when extraction fails."""
    text_parts: List[str] = []

    try:
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            images = convert_from_bytes(content)
            for image in images[:3]:  # keep demo fast
                page_text = pytesseract.image_to_string(image)
                if page_text.strip():
                    text_parts.append(page_text)
        else:
            image = Image.open(io.BytesIO(content)).convert("RGB")
            page_text = pytesseract.image_to_string(image)
            if page_text.strip():
                text_parts.append(page_text)
    except Exception:
        pass

    full_text = "\n".join(text_parts).strip()
    return full_text if full_text else FALLBACK_TEXT


def analyze_with_ai(text: str) -> dict:
    """Extract disease, medication, risk, and timeline via OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # local fallback if API key missing
        return {
            "disease": "Diabetes",
            "medication": "Metformin",
            "risk": "High",
            "timeline": [
                {"year": "2022", "event": "Diagnosed"},
                {"year": "2023", "event": "Medication started"},
                {"year": "2024", "event": "High sugar detected"},
            ],
        }

    client = OpenAI(api_key=api_key)
    prompt = (
        "Extract disease, medication, and risk from this medical text. "
        "Return ONLY JSON with keys: disease, medication, risk, timeline. "
        "Timeline must be array with up to 3 events, each having year and event.\n\n"
        f"Medical text:\n{text}"
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0,
    )

    raw_output = response.output_text.strip()
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # robust parser fallback
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw_output[start : end + 1])
        raise


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    extracted_text = extract_text_from_file(file.filename, content)
    result = analyze_with_ai(extracted_text)

    # normalize timeline length max 3
    timeline = result.get("timeline", [])[:3]

    return {
        "disease": result.get("disease", "Unknown"),
        "medication": result.get("medication", "Unknown"),
        "risk": result.get("risk", "Unknown"),
        "timeline": timeline,
        "insight": f"Patient appears to have {result.get('disease', 'a condition')} with {result.get('risk', 'unknown')} risk.",
        "raw_text_preview": extracted_text[:500],
    }
