from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from core.enrichment.validator import validate_enrichment_input
from core.enrichment.enricher import enrich

router = APIRouter()


@router.post("/enrichment")
async def enrich_structured_data(payload: dict = Body(...)):
    data, error = validate_enrichment_input(payload)

    if error:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": error},
        )

    result = enrich(data)
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "execution_id": result.pop("execution_id"),
            "data": result,
        },
    )
