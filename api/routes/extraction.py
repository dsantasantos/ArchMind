import base64
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from core.extraction.extractor import extract_from_image

router = APIRouter()

_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_MEDIA_TYPE_MAP = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


@router.post("/extraction")
async def extraction_endpoint(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Only .png, .jpg, .jpeg images are accepted."},
        )

    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    media_type = _MEDIA_TYPE_MAP[ext]

    try:
        result = extract_from_image(image_base64, media_type=media_type)
    except ValueError as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )

    return JSONResponse(status_code=200, content=result)
