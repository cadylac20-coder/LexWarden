from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional

class ClauseReport(BaseModel):
    scanned_clause: str = Field(..., description="The raw clause string captured from the scan.")
    risk_level: str = Field(..., description="Evaluated risk metric: GREEN, YELLOW, or RED.")
    explanation: str = Field(..., description="Analytical breakdown of risks in the clause wording.")
    suggested_revision: str = Field(..., description="Optimized, safe alternative clause text.")
    similarity_score: Optional[float] = Field(None, description="Cosine similarity score vs. safe baseline (0.0–1.0).")

class ContractReportDocument(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB Object ID.")
    filename: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall_status: str  # "COMPLIANT" or "RISKY (RED FLAGS)"
    clauses_analyzed: List[ClauseReport]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
