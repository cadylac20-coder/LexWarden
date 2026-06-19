from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.mongo import MongoDB
from app.db.models import ContractReportDocument
from typing import List

router = APIRouter()

@router.get("/reports", response_model=List[ContractReportDocument])
async def list_reports():
    if MongoDB.db is None:
        raise HTTPException(status_code=503, detail="Database subsystem offline.")
    
    cursor = MongoDB.db.reports.find().sort("uploaded_at", -1)
    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        reports.append(ContractReportDocument(**doc))
    return reports

@router.get("/reports/{report_id}", response_model=ContractReportDocument)
async def get_report(report_id: str):
    if MongoDB.db is None:
        raise HTTPException(status_code=533, detail="Database engine tracking subsystem uninitialized.")
    
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="Invalid report primary key string structure.")
        
    doc = await MongoDB.db.reports.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Target risk document report not found inside historical storage log collections.")
        
    doc["_id"] = str(doc["_id"])
    return ContractReportDocument(**doc)
