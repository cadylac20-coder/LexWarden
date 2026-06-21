import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.ocr_service import OCRService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.db.mongo import MongoDB
from app.db.models import ContractReportDocument, ClauseReport

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def get_vector_service() -> VectorService:
    return VectorService()

def get_llm_service() -> LLMService:
    return LLMService()

@router.post("/analyze-contract", response_model=ContractReportDocument)
@limiter.limit("10/minute")
async def analyze_contract(
    request: Request,
    file: UploadFile = File(...),
    vector_service: VectorService = Depends(get_vector_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    filename = file.filename or ""
    ext = "." + filename.lower().split(".")[-1] if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. LexWarden accepts: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        file_bytes = await file.read()
        raw_text = await OCRService.extract_text(file_bytes, filename=filename)
        chunks = OCRService.chunk_text(raw_text)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No readable legal clauses could be parsed from the document."
            )

        analyzed_clauses = []
        has_red_flags = False

        for chunk in chunks:
            safe_baseline, similarity_score = vector_service.find_similar_safe_clause(chunk)
            assessment = llm_service.assess_clause_risk(chunk, safe_baseline)

            if assessment.risk_level == "RED":
                has_red_flags = True

            analyzed_clauses.append(
                ClauseReport(
                    scanned_clause=chunk,
                    risk_level=assessment.risk_level,
                    explanation=assessment.explanation,
                    suggested_revision=assessment.suggested_revision,
                    similarity_score=similarity_score
                )
            )

        report_doc = ContractReportDocument(
            filename=filename,
            overall_status="RISKY (RED FLAGS)" if has_red_flags else "COMPLIANT",
            clauses_analyzed=analyzed_clauses
        )

        if MongoDB.db is not None:
            payload = report_doc.model_dump(by_alias=True, exclude_none=True)
            inserted_result = await MongoDB.db.reports.insert_one(payload)
            report_doc.id = str(inserted_result.inserted_id)
        else:
            logger.warning("MongoDB unavailable — report not persisted.")

        return report_doc

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error during contract analysis pipeline")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
