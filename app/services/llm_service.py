import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger(__name__)

class ClauseAssessment(BaseModel):
    risk_level: str = Field(description="Must be strictly 'GREEN', 'YELLOW', or 'RED'.")
    explanation: str = Field(description="Detailed explanation of legal risks or compliance status.")
    suggested_revision: str = Field(description="Alternative clause text aligned with safe legal standards.")

class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    def assess_clause_risk(self, scanned_clause: str, safe_clause: str) -> ClauseAssessment:
        system_instruction = (
            "You are an elite automated contract analyzer and corporate legal compliance officer. "
            "Your sole responsibility is evaluating contract clauses against gold standard baselines "
            "and returning structured risk assessments. Be precise, consistent, and conservative — "
            "when in doubt, escalate to a higher risk level."
        )

        prompt = f"""
        Analyze the scanned contract clause below and compare it against the provided safe baseline.

        [SCANNED CLAUSE]
        {scanned_clause}

        [SAFE BASELINE TEMPLATE]
        {safe_clause}

        Evaluation criteria:
        - RED: Introduces severe unexpected liabilities, removes mutual protections, imposes uncapped financial penalties, or grants unilateral rights to one party.
        - YELLOW: Contains asymmetric definitions, vague scope, missing standard protections, or non-standard terminology.
        - GREEN: Aligns with or improves upon the safe baseline standard.

        If no safe baseline was found (indicated by the baseline text starting with "No matching"), evaluate the clause independently using general corporate legal standards.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=ClauseAssessment,
                    temperature=0.1
                )
            )
            return response.parsed
        except Exception as e:
            logger.error(f"LLM assessment failed: {e}")
            raise RuntimeError(f"LLM clause assessment failed: {str(e)}")
