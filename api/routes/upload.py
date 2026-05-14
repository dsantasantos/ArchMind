"""
api/routes/upload.py — endpoint único que faz upload + extração.

Modular por design: a parte de "de onde vem a imagem" é abstraída via
ImageSource. Hoje só temos upload via form-data; pra adicionar URL/S3/
base64 no futuro, basta criar outra classe ImageSource e outro endpoint
chamando _process_source com ela.

Endpoints:
    POST /upload                 — upload de arquivo + extração
    GET  /upload                 — lista imagens já processadas
    GET  /upload/{image_id}      — baixa imagem original
    DELETE /upload/{image_id}    — remove imagem
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from core.extraction.extractor import extract
from infra.storage.file_storage import (
    UnsupportedFormatError,
    delete_image,
    get_image_metadata,
    get_image_path,
    list_images,
    save_image_bytes,
)

router = APIRouter()


# ─── Abstração de fonte de imagem ──────────────────────────────────────────
#
# Fica aqui no routes (próximo de quem usa) para deixar claro que é a
# camada de entrada. Pra adicionar uma nova fonte, criar uma subclasse
# e um novo endpoint que a instancia.

class ImageSourceError(ValueError):
    """Erro ao obter bytes da imagem."""


class ImageSource(ABC):
    """Interface mínima de uma fonte de imagem."""

    @property
    @abstractmethod
    def filename(self) -> str:
        ...

    @abstractmethod
    def fetch_bytes(self) -> bytes:
        ...

    def metadata(self) -> dict[str, Any]:
        return {"source_type": type(self).__name__}


class UploadFileSource(ImageSource):
    """Fonte: arquivo enviado via multipart/form-data."""

    def __init__(self, upload_file: UploadFile):
        self._upload = upload_file

    @property
    def filename(self) -> str:
        return self._upload.filename or "image.png"

    def fetch_bytes(self) -> bytes:
        self._upload.file.seek(0)
        data = self._upload.file.read()
        if not data:
            raise ImageSourceError("Upload vazio")
        return data

    def metadata(self) -> dict[str, Any]:
        return {
            "source_type":  "upload",
            "content_type": getattr(self._upload, "content_type", None),
        }


# ─── Pipeline central — agnóstico de fonte ─────────────────────────────────

def _process_source(source: ImageSource) -> dict:
    """
    Salva os bytes da fonte e roda extração. Função pura: dada uma
    ImageSource, devolve a resposta padronizada.
    """
    try:
        data = source.fetch_bytes()
    except ImageSourceError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        metadata = save_image_bytes(
            data=data,
            filename=source.filename,
            source_metadata=source.metadata(),
        )
    except UnsupportedFormatError as e:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        result = extract(metadata["path"])
    except (FileNotFoundError, IOError) as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na extração: {e}",
        )

    return {
        "status":   "success",
        "image_id": metadata["image_id"],
        "metadata": metadata,
        "result":   result,
    }


# ─── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_and_extract(file: UploadFile = File(..., description="Imagem .png/.jpg/.jpeg")):
    """
    Faz upload de uma imagem, salva em disco e retorna o JSON da extração.

    Retorna:
        - image_id  (referência para os outros endpoints)
        - metadata  (dados do upload: nome, path, tamanho, etc.)
        - result    (JSON da extração: text_blocks, grouped_elements, etc.)
    """
    return _process_source(UploadFileSource(file))


@router.get("/upload")
async def list_uploaded_images(limit: int = 100):
    """Lista as imagens já processadas, mais recentes primeiro."""
    images = list_images(limit=limit)
    return {"total": len(images), "images": images}


@router.get("/upload/{image_id}")
async def get_uploaded_image(image_id: str):
    """Baixa a imagem original pelo ID."""
    meta = get_image_metadata(image_id)
    if not meta:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Imagem {image_id!r} não encontrada.")
    path = get_image_path(image_id)
    if not path:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="Arquivo removido do disco.")
    return FileResponse(path,
                        media_type=meta["media_type"],
                        filename=meta["original_name"])


@router.delete("/upload/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_image(image_id: str):
    if not delete_image(image_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Imagem {image_id!r} não encontrada.")