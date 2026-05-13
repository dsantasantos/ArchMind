from fastapi import APIRouter, UploadFile, File
from schemas.report_schema import DiagramReport
from core.extraction.extractor import extract
from core.structuring.structurer import structure
from core.enrichment.enricher import enrich
from core.analysis.analyzer import analyze
from core.reporting.reporter import generate_report
from core.extraction.extractor import extract_from_image
import base64
router = APIRouter()


@router.post("/upload-diagram", response_model=DiagramReport)
async def upload_diagram(file: UploadFile = File(...)) -> DiagramReport:
    filename = file.filename or "unknown"
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    raw_data = extract_from_image(image_base64, media_type=file.content_type)
    structured_data = structure(raw_data)
    enriched_data = enrich(structured_data)
    analysis_result = analyze(enriched_data)
    report = generate_report(filename, analysis_result)

    return report
