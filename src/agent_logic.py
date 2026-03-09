import  os
import datetime
from google import genai
from google.genai import types

class JobTailorAgent:
    """
    A multi=modal AI  agent that uses Gemini 3 Flash to analyze job descriptions
    form images and tailor CVs accordingly.
    """
    def __init__(self, api_key: str ):
        self.client = genai.Client(api_key=api_key)
        self.modal_id = "gemini-3.1-flash-lite-preview"

    def analyze_and_tailor(self, master_cv_text: str, screenshot_path: str):
        """
        Extracts Job description from a screenshot, identifies gaps, and rewrites
        the CV.
        Returns a dictionary containing the tailored CV and interview prep.
        """
        # Read the image bytes
        with open(screenshot_path, "rb") as f:
            image_bytes = f.read()

        # Force the AI to include 'metadata'
        response_schema = {
            "type": "OBJECT",
            "properties":{
                "metadata": {
                    "type": "STRING",
                    "description": "Format: Company|Role|Score (Score) (e.g., Google|Python Dev|85)"
                },
                "cv_content": {
                    "type": "STRING",
                    "description": "The full tailored CV in Markdown format"
                }
            },
            "required": ["metadata", "cv_content"]
        }

        # Call Gemini 3 and set thinking level and factuality
        response = self.client.models.generate_content(
            model=self.modal_id,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1
                ),
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    f"Tailor this CV to the job in the image: {master_cv_text}"
                ]
        )

        # Directly return the parsed dictionary
        return response.parsed


    def _parse_response(self, raw_text: str):
        parts = raw_text.split("SECTION_BREAK")
        # Handle edge case if Gemini fails to split correctly
        if len(parts) < 3:
            return {"error": "Incomplete generation", "raw": raw_text}

        # .strip(" =") removes ANY combination of '=' and ' ' from the ends
        return {
            "metadata": parts[0].strip().rstrip("="),
            "cv_md": parts[1].strip(" ="),
            "prep_md": parts[2].strip(" =")
        }