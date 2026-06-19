from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.config import settings

class ClauseAssessment(BaseModel):
    risk_level: str = Field(description="Must evaluate strictly to 'GREEN', 'YELLOW', or 'RED'")
    explanation: str = Field(description="Deep context explaining legal variations, vulnerabilities, or changes.")
    suggested_revision: str = Field(description="Alternative legal text compliant with standard templates.")

class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Using flash for low latency
        self.model_name = "gemini-2.5-flash"

    def assess_clause_risk(self, scanned_clause: str, safe_clause: str) -> ClauseAssessment:
        system_instruction = (
            "You are an elite automated contract analyzer and corporate legal officer. Your sole responsibility "
            "is checking input text variations against gold standard baselines and returning clean structured evaluations."
        )
        
        prompt = f"""
        Analyze the scanned contract fragment and contrast it against our standard safe baseline.
        
        [SCANNED CLAUSE]
        {scanned_clause}
        
        [SAFE BASELINE TEMPLATE]
        {safe_clause}
        
        If the scanned text introduces severe unexpected liabilities, high financial penalties, or removes mutual protections, 
        mark it as 'RED'. If definitions are asymmetrical or vague, mark it as 'YELLOW'. If standard, mark it as 'GREEN'.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ClauseAssessment,
                temperature=0.1  # Highly deterministic responses
            )
        )
        return response.parsed
