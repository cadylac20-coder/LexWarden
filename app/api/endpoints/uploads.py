from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import OCRService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.db.mongo import MongoDB
from app.db.models import ContractReportDocument, ClauseReport

router = APIRouter()
vector_service = VectorService()
llm_service = LLMService()

@router.post("/analyze-contract", response_model=ContractReportDocument)
async def analyze_contract(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="LexWarden currently processes vector-born or digital PDF payloads only.")
    
    try:
        file_bytes = await file.read()
        raw_text = await OCRService.extract_text(file_bytes)
        chunks = OCRService.chunk_text(raw_text)
        
        if not chunks:
            raise HTTPException(status_code=422, detail="No readable legal paragraphs or clauses could be parsed from data stream.")
        
        analyzed_clauses = []
        has_red_flags = False
        
        for chunk in chunks:
            # Query standard database context
            safe_baseline = vector_service.find_similar_safe_clause(chunk)
            # Evaluate using Gemini
            assessment = llm_service.assess_clause_risk(chunk, safe_baseline)
            
            if assessment.risk_level == "RED":
                has_red_flags = True
                
            analyzed_clauses.append(
                ClauseReport(
                    scanned_clause=chunk,
                    risk_level=assessment.risk_level,
                    explanation=assessment.explanation,
                    suggested_revision=assessment.suggested_revision
                )
            )
            
        report_doc = ContractReportDocument(
            filename=file.filename,
            overall_status="RISKY (RED FLAGS)" if has_red_flags else "COMPLIANT",
            clauses_analyzed=analyzed_clauses
        )
        
        if MongoDB.db is not None:
            # Drop data mapping seamlessly into MongoDB
            payload = report_doc.model_dump(by_alias=True, exclude_none=True)
            inserted_result = await MongoDB.db.reports.insert_one(payload)
            report_doc.id = str(inserted_result.inserted_id)
            
        return report_doc
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Engine Pipeline Processing Error: {str(e)}")
