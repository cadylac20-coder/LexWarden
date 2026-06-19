from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import OCRService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService

router = APIRouter()
vector_service = VectorService()
llm_service = LLMService()

@router.post("/analyze-contract")
async def analyze_contract(file: UploadFile = File(...)):
    # 1. Read and OCR the physical document
    file_bytes = await file.read()
    raw_text = await OCRService.extract_text(file_bytes)
    
    # 2. Chunk text into distinct clauses
    chunks = OCRService.chunk_text(raw_text)
    
    dashboard_report = []
    
    # 3. Process each clause through RAG pipeline
    for chunk in chunks:
        # Get the standard "safe" baseline from Vector DB
        safe_baseline = vector_service.find_similar_safe_clause(chunk)
        
        # Let LLM evaluate the differences
        analysis = llm_service.assess_clause_risk(chunk, safe_baseline)
        
        dashboard_report.append({
            "scanned_clause": chunk,
            "assessment": analysis
        })
        
    # TODO: Save dashboard_report & metadata into MongoDB here
    
    return {"status": "success", "report": dashboard_report}
