from google import genai
from pydantic import BaseModel, Field

# 1. Define the exact response shape using Pydantic
class ClauseAssessment(BaseModel):
    risk_level: str = Field(description="Must be exactly 'GREEN', 'YELLOW', or 'RED'")
    explanation: str = Field(description="Clear explanation of why this clause is risky or how it departs from standard practice.")
    suggested_revision: str = Field(description="A safer, corporate-standard way to phrase this clause.")

class LLMService:
    def __init__(self):
        # The Client automatically reads GEMINI_API_KEY from your .env file
        self.client = genai.Client()

    def assess_clause_risk(self, scanned_clause: str, safe_clause: str) -> ClauseAssessment:
        prompt = f"""
        You are an expert corporate legal counsel. Compare the scanned contract clause against our safe standard baseline.
        Identify if there are any predatory terms, unusual liabilities, or non-standard compliance terms.
        
        Scanned Clause from Contract: "{scanned_clause}"
        Safe Standard Template Baseline: "{safe_clause}"
        """
        
        # 2. Invoke the model using the recommended gemini-2.5-flash for speed and low-latency
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ClauseAssessment,  # Enforces the Pydantic structure
            }
        )
        
        # 3. The SDK automatically parses the JSON string directly into your Pydantic class object
        return response.parsed
