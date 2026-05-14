"""
infra/storage/file_storage.py — persistência de imagens em disco.

Camada de infraestrutura pura: trabalha com bytes brutos e nome do arquivo.
Não conhece HTTP, upload, base64, URL etc. Quem cuida disso são as rotas
em `api/routes/`.

Layout em disco:
    storage/
    ├── uploads/
    │   └── <image_id>.<ext>
    └── registry.json
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


# ─── Configuração ──────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).resolve().parent.parent.parent  # → ArchMind/
STORAGE_DIR  = Path(os.getenv("ARCHMIND_STORAGE_DIR", BASE_DIR / "storage"))
UPLOADS_DIR  = STORAGE_DIR / "uploads"
REGISTRY     = STORAGE_DIR / "registry.json"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MEDIA_TYPES = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
}


# ─── Erros públicos ────────────────────────────────────────────────────────

class UnsupportedFormatError(ValueError):
    """Extensão de arquivo não suportada."""


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

def save_image_bytes(
    data: bytes,
    filename: str,
    source_metadata: Optional[dict[str, Any]] = None,
) -> dict:
    """
    Persiste bytes de imagem em disco e registra no índice.
    """
    if not data:
        raise ValueError("Dados vazios")

    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Extensão {ext!r} não suportada. Aceitas: {sorted(ALLOWED_EXTENSIONS)}"
        )

    image_id = uuid4().hex
    target   = UPLOADS_DIR / f"{image_id}{ext}"

    with open(target, "wb") as out:
        out.write(data)

    metadata = {
        "image_id":        image_id,
        "original_name":   filename,
        "media_type":      MEDIA_TYPES[ext],
        "path":            str(target),
        "size_bytes":      len(data),
        "uploaded_at":     datetime.now(timezone.utc).isoformat(),
        "source_metadata": source_metadata or {},
    }

    registry = _load_registry()
    registry[image_id] = metadata
    _save_registry(registry)

    return metadata


def get_image_metadata(image_id: str) -> Optional[dict]:
    return _load_registry().get(image_id)


def get_image_path(image_id: str) -> Optional[Path]:
    meta = get_image_metadata(image_id)
    if not meta:
        return None
    p = Path(meta["path"])
    return p if p.exists() else None


def list_images(limit: int = 100) -> list[dict]:
    items = list(_load_registry().values())
    items.sort(key=lambda m: m.get("uploaded_at", ""), reverse=True)
    return items[:limit]


def delete_image(image_id: str) -> bool:
    registry = _load_registry()
    meta = registry.pop(image_id, None)
    if not meta:
        return False
    Path(meta["path"]).unlink(missing_ok=True)
    _save_registry(registry)
    return True