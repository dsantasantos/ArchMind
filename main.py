from fastapi import FastAPI
from api.routes.upload import router as upload_router

app = FastAPI(
    title="ArchMind",
    description="Intelligent Architectural Analysis Engine",
    version="0.1.0",
)

app.include_router(upload_router, prefix="/api/v1", tags=["Diagrams"])
