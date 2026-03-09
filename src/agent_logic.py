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

        # Build the agent prompt
        # Use a sinlge multi-modal turn to save latency and cost
        prompt = f"""
        CONTEXT:
        Master CV Content: {master_cv_text}

        TASK:
        1. Examine the attached LinkedIn job description image.
        2. Identify the Company Name and Role Title
        3. Conduct a sementic keyword gap analysis between my CV and this JD.
        4. Rewrite the CV into a professional Markdown format.
        5. Generate 5 intervieew questions and an ATS Match Score.

        OUT FORMAT:
        Please separate sections with '==Section_Break=='
        Order: [Metadata (Company|Role)] , [Tailored CV] , [Interview Prep & ATS Score]
        """

        # Call Gemini 3 with 'High' thinking level for deep reasoning
        response = self.client.models.generate_content(
            model=self.modal_id,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
                temperature=0.1 # Focuses AI on the facts
            ),
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                prompt
            ]
        )
        return self._parse_response(response.text)

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