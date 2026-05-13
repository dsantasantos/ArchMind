"""
Módulo de extração de diagramas — pertence ao pipeline ArchMind.

Exports:
    extract(filename)              → dict  — usado por upload.py
    extract_from_image(b64, type)  → dict  — usado por extraction.py
    DiagramExtractor               → classe — para uso avançado/customizado
"""

from .extractor import extract, extract_from_image, DiagramExtractor

__all__ = ["extract", "extract_from_image", "DiagramExtractor"]
