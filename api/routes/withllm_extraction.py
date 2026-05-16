from fastapi import APIRouter, File, HTTPException, UploadFile

from core.withllm.extraction.extractor import extract_from_image

router = APIRouter()

_ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg"}


@router.post("/extraction")
async def extract_with_llm(file: UploadFile = File(...)):
    media_type = file.content_type or "image/jpeg"
    if media_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {media_type}")
    image_bytes = await file.read()
    return extract_from_image(image_bytes, media_type=media_type)
