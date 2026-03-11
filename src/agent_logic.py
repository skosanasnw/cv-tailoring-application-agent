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

    def analyze_and_tailor(self, master_cv_text: str, source: str, is_image: bool = True):
        """
        Extracts Job description from a screenshot, identifies gaps, and rewrites
        the CV.
        Returns a dictionary containing the tailored CV and interview prep.
        """
        # Prepare the Parts list
        if is_image:
            with open(source, "rb") as f:
                image_bytes = f.read()
            # If is image, send bytes
            content_parts = [
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                f"Tailor this CV to the job in the image. Master CV: {master_cv_text}"
            ]
        else:
            # If it's text (from .txt), we just send strings
            content_parts = [
                f"Job Description: {source}",
                f"Tailor this CV to the job description above. Master CV: {master_cv_text}"
            ]
        # Force the AI to include 'metadata'
        response_schema = {
            "type": "OBJECT",
            "properties":{
                "metadata": {
                    "type": "OBJECT",
                    "properties": {
                        "company":{"type": "STRING"},
                        "role": {"type": "STRING"}
                    },
                    "required": ["company", "role"]
                },
                "cv_md": {"type": "STRING"},
            },
            "required": ["metadata", "cv_md"]
        }

        # Call Gemini 3 and set thinking level and factuality
        response = self.client.models.generate_content(
            model=self.modal_id,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1
                ),
                contents=content_parts
        )

        # Directly return the parsed dictionary
        return response.parsed
