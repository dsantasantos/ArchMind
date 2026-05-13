"""
Endpoint de extração — opera sobre imagens já carregadas via /upload.

Fluxo:
    POST /upload                → image_id
    POST /extraction/{image_id} → JSON extraído
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from core.extraction.extractor import extract
from infra.storage.file_storage import get_image_metadata, get_image_path

router = APIRouter()


@router.post("/extraction/{image_id}")
async def extraction_endpoint(image_id: str):
    """
    Executa OCR e extração estrutural sobre uma imagem já carregada.

    Args:
        image_id: identificador retornado por POST /upload.

    Returns:
        JSON com text_blocks, grouped_elements, relationship_hints,
        context_groups e detected_keywords.
    """
    meta = get_image_metadata(image_id)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagem {image_id!r} não encontrada. "
                   f"Faça upload primeiro via POST /upload.",
        )

    image_path = get_image_path(image_id)
    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo removido do disco.",
        )

    try:
        result = extract(str(image_path))
    except (FileNotFoundError, IOError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na extração: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {e}",
        )

    return JSONResponse(
        status_code=200,
        content={
            "status":   "success",
            "image_id": image_id,
            "result":   result,
        },
    )