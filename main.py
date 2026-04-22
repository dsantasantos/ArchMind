from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html")
