import logging

from fastapi import FastAPI

from infra.log_store import ExecutionLogHandler
from api.routes.upload import router as upload_router
from api.routes.structuring import router as structuring_router
from api.routes.withllm_structuring import router as withllm_structuring_router
from api.routes.extraction import router as extraction_router
from api.routes.execution_logs import router as execution_logs_router
from api.routes.enrichment import router as enrichment_router
from api.routes.enrichment_logs import router as enrichment_logs_router
from api.routes.withllm_enrichment import router as withllm_enrichment_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logging.getLogger().addHandler(ExecutionLogHandler())

app = FastAPI(
    title="ArchMind",
    description="Intelligent Architectural Analysis Engine",
    version="0.1.0",
)

app.include_router(upload_router, prefix="/api/v1", tags=["Diagrams"])
app.include_router(structuring_router, prefix="/api/v1", tags=["Structuring"])
app.include_router(execution_logs_router, prefix="/api/v1", tags=["Structuring"])
app.include_router(withllm_structuring_router, prefix="/api/v1/withllm", tags=["Structuring (LLM)"])
app.include_router(withllm_enrichment_router, prefix="/api/v1/withllm", tags=["Enrichment (LLM)"])
app.include_router(extraction_router, prefix="/api/v1", tags=["Extraction"])
app.include_router(enrichment_router, prefix="/api/v1", tags=["Enrichment"])
app.include_router(enrichment_logs_router, prefix="/api/v1", tags=["Enrichment"])
