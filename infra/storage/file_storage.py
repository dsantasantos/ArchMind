from pathlib import Path


UPLOAD_DIR = Path("uploads")


def save_upload(filename: str, content: bytes) -> Path:
    # Future: swap for S3 / GCS when moving off local storage
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / filename
    destination.write_bytes(content)
    return destination


def get_upload_path(filename: str) -> Path:
    return UPLOAD_DIR / filename
