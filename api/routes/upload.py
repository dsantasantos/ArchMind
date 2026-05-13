"""
Endpoints de upload e gerenciamento de imagens.

Fluxo de uso:
    1. POST   /upload                → salva imagem, devolve image_id
    2. POST   /extraction/{image_id} → extrai JSON da imagem salva
    3. GET    /upload                → lista imagens disponíveis
    4. GET    /upload/{image_id}     → baixa a imagem original
    5. DELETE /upload/{image_id}     → remove a imagem

A extração foi separada para permitir reuso (extrair várias vezes a mesma
imagem com parâmetros diferentes, executar workers async, etc.).
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from infra.storage.file_storage import (
    UnsupportedFormatError,
    delete_image,
    get_image_metadata,
    get_image_path,
    list_images,
    save_image,
)

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...)) -> dict:
    """
    Recebe uma imagem (.png/.jpg/.jpeg) e persiste em disco.

    Returns:
        Metadados do upload, incluindo `image_id` para uso em /extraction.
    """
    try:
        metadata = save_image(file.file, file.filename or "image.png")
    except UnsupportedFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "status":   "success",
        "image_id": metadata["image_id"],
        "metadata": metadata,
        "message":  "Use POST /extraction/{image_id} para extrair o JSON.",
    }


@router.get("/upload")
async def list_uploaded_images(limit: int = 100) -> dict:
    """Lista as imagens já carregadas, mais recentes primeiro."""
    images = list_images(limit=limit)
    return {"total": len(images), "images": images}


@router.get("/upload/{image_id}")
async def get_uploaded_image(image_id: str):
    """Retorna a imagem original em bytes."""
    meta = get_image_metadata(image_id)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagem {image_id!r} não encontrada.",
        )
    path = get_image_path(image_id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo removido do disco.",
        )
    return FileResponse(
        path,
        media_type=meta["media_type"],
        filename=meta["original_name"],
    )


@router.delete("/upload/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_image(image_id: str):
    """Remove a imagem do storage."""
    if not delete_image(image_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagem {image_id!r} não encontrada.",
        )