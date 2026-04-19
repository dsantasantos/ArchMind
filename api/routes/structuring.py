from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from core.structuring.validator import validate_structuring_input
from core.structuring.structurer import process

router = APIRouter()


@router.post("/structuring")
async def structure_input(payload: dict = Body(...)):
    parsed, error = validate_structuring_input(payload)

    if error:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": error},
        )

    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": process(parsed)},
    )
