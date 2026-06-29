import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.verify import router as api_v1_router
from backend.core.config import settings
from datetime import datetime

from datetime import datetime, timezone

app = FastAPI(
    title="TruthLens API",
    description="Platform-agnostic, evidence-based verification intelligence backend for TruthLens.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for extension origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API router
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TruthLens Backend",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True if settings.LOG_LEVEL == "debug" else False
    )
