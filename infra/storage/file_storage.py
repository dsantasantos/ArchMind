"""
Storage de imagens do ArchMind.

Persiste uploads em disco com identificador único e mantém um registry
JSON com metadados (nome original, mime, datas). API agnóstica de FastAPI
para poder ser usada de qualquer endpoint ou worker.

Layout em disco:
    storage/
    ├── uploads/
    │   ├── <image_id>.png
    │   ├── <image_id>.jpg
    │   └── ...
    └── registry.json     # mapeamento image_id → metadata
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4


# ─── Configuração ──────────────────────────────────────────────────────────

# Por padrão grava em ArchMind/storage/uploads. Override via env var.
BASE_DIR     = Path(__file__).resolve().parent.parent.parent  # → ArchMind/
STORAGE_DIR  = Path(os.getenv("ARCHMIND_STORAGE_DIR", BASE_DIR / "storage"))
UPLOADS_DIR  = STORAGE_DIR / "uploads"
REGISTRY     = STORAGE_DIR / "registry.json"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Extensões aceitas e mapa de media types
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MEDIA_TYPES = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
}


# ─── Registry helpers ──────────────────────────────────────────────────────

def _load_registry() -> dict:
    if not REGISTRY.exists():
        return {}
    try:
        with open(REGISTRY, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry(data: dict) -> None:
    tmp = REGISTRY.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(REGISTRY)


# ─── API pública ────────────────────────────────────────────────────────────

class UnsupportedFormatError(ValueError):
    """Raised when the uploaded file has an extension we don't accept."""


def save_image(stream: BinaryIO, filename: str) -> dict:
    """
    Persiste uma imagem em disco e registra no índice.

    Args:
        stream:   file-like com os bytes da imagem (ex: UploadFile.file).
        filename: nome original com extensão.

    Returns:
        dict com metadados do upload: {image_id, original_name, media_type,
        path, size_bytes, uploaded_at}.

    Raises:
        UnsupportedFormatError: extensão não permitida.
        ValueError:             arquivo vazio.
    """
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Extensão {ext!r} não suportada. Aceitas: {sorted(ALLOWED_EXTENSIONS)}"
        )

    image_id = uuid4().hex
    target   = UPLOADS_DIR / f"{image_id}{ext}"

    with open(target, "wb") as out:
        shutil.copyfileobj(stream, out)

    size = target.stat().st_size
    if size == 0:
        target.unlink(missing_ok=True)
        raise ValueError("Arquivo vazio")

    metadata = {
        "image_id":      image_id,
        "original_name": filename,
        "media_type":    MEDIA_TYPES[ext],
        "path":          str(target),
        "size_bytes":    size,
        "uploaded_at":   datetime.now(timezone.utc).isoformat(),
    }

    registry = _load_registry()
    registry[image_id] = metadata
    _save_registry(registry)

    return metadata


def get_image_metadata(image_id: str) -> Optional[dict]:
    """Retorna metadados de uma imagem por ID, ou None se não existir."""
    return _load_registry().get(image_id)


def get_image_path(image_id: str) -> Optional[Path]:
    """Retorna o Path absoluto da imagem em disco, ou None."""
    meta = get_image_metadata(image_id)
    if not meta:
        return None
    p = Path(meta["path"])
    return p if p.exists() else None


def list_images(limit: int = 100) -> list[dict]:
    """Lista metadados dos uploads, mais recentes primeiro."""
    items = list(_load_registry().values())
    items.sort(key=lambda m: m.get("uploaded_at", ""), reverse=True)
    return items[:limit]


def delete_image(image_id: str) -> bool:
    """Remove a imagem e seu registro. Retorna True se removida."""
    registry = _load_registry()
    meta = registry.pop(image_id, None)
    if not meta:
        return False

    path = Path(meta["path"])
    if path.exists():
        path.unlink(missing_ok=True)

    _save_registry(registry)
    return True