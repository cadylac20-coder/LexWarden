from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ClauseReport(BaseModel):
    scanned_clause: str = Field(..., description="The raw clause string captured from the scan.")
    risk_level: str = Field(..., description="Evaluated risk metric matching GREEN, YELLOW, or RED.")
    explanation: str = Field(..., description="Analytical layout of risks contained in the wording.")
    suggested_revision: str = Field(..., description="Optimized, safe alternative text option.")

class ContractReportDocument(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB Object String Identifier.")
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    overall_status: str  # "COMPLIANT" or "RISKY (RED FLAGS)"
    clauses_analyzed: List[ClauseReport]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
