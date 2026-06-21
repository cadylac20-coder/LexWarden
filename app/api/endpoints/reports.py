import logging
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.mongo import MongoDB
from app.db.models import ContractReportDocument
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/reports", response_model=List[ContractReportDocument])
async def list_reports():
    if MongoDB.db is None:
        raise HTTPException(status_code=503, detail="Database subsystem offline.")

    try:
        cursor = MongoDB.db.reports.find().sort("uploaded_at", -1).limit(100)
        reports = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            reports.append(ContractReportDocument(**doc))
        return reports
    except Exception as e:
        logger.exception("Failed to fetch reports list")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@router.get("/reports/{report_id}", response_model=ContractReportDocument)
async def get_report(report_id: str):
    if MongoDB.db is None:
        raise HTTPException(status_code=503, detail="Database subsystem offline.")  # was 533 — invalid HTTP code

    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="Invalid report ID format.")

    try:
        doc = await MongoDB.db.reports.find_one({"_id": ObjectId(report_id)})
        if not doc:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

        doc["_id"] = str(doc["_id"])
        return ContractReportDocument(**doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch report {report_id}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.delete("/reports/{report_id}", status_code=204)
async def delete_report(report_id: str):
    if MongoDB.db is None:
        raise HTTPException(status_code=503, detail="Database subsystem offline.")

    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="Invalid report ID format.")

    try:
        result = await MongoDB.db.reports.delete_one({"_id": ObjectId(report_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete report {report_id}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
