from fastapi import FastAPI
from api.routes.upload import router as upload_router
from api.routes.structuring import router as structuring_router
from api.routes.extraction import router as extraction_router

app = FastAPI(
    title="ArchMind",
    description="Intelligent Architectural Analysis Engine",
    version="0.1.0",
)

app.include_router(upload_router, prefix="/api/v1", tags=["Diagrams"])
app.include_router(structuring_router, prefix="/api/v1", tags=["Structuring"])
app.include_router(extraction_router, prefix="/api/v1", tags=["Extraction"])
