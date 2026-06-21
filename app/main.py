from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.endpoints import uploads, reports
from app.db.mongo import MongoDB
from contextlib import asynccontextmanager

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    MongoDB.connect()
    yield
    MongoDB.disconnect()

app = FastAPI(
    title="LexWarden Engine Core",
    description="Automated Legal Compliance Semantic Mapping Pipeline Engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — credentials require explicit origins, not wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind Endpoints
app.include_router(uploads.router, prefix="/api/v1", tags=["Ingestion Pipeline"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])

@app.get("/healthz", tags=["Diagnostics"])
def health_check():
    return {
        "status": "online",
        "database_connected": MongoDB.db is not None
    }
