from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import upload, reports
from app.db.mongo import MongoDB
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Establish single thread async persistent client pools
    MongoDB.connect()
    yield
    # Safely clear pools on normal lifecycle stops
    MongoDB.disconnect()

app = FastAPI(
    title="LexWarden Engine Core",
    description="Automated Legal Compliance Semantic Mapping Pipeline Engine.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind Endpoints
app.include_router(upload.router, prefix="/api/v1", tags=["Ingestion Pipeline Module"])
app.include_router(reports.router, prefix="/api/v1", tags=["Data Storage Inquiries"])

@app.get("/healthz", tags=["Diagnostics"])
def health_check():
    return {
        "status": "online",
        "database_connected": MongoDB.db is not None
    }
