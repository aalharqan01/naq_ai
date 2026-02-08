"""OCR service for extracting text from scanned documents and images."""

import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger("dhakira.ocr")

# Lazy-loaded EasyOCR reader
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        logger.info("Loading EasyOCR reader (Arabic + English)")
        _reader = easyocr.Reader(["ar", "en"], gpu=True)
        logger.info("EasyOCR reader loaded")
    return _reader


def extract_text_from_image(image_path: str) -> dict:
    """
    Extract text from a scanned document image.

    Returns:
        {
            "text": "full extracted text",
            "blocks": [{"text": "...", "confidence": 0.95, "bbox": [...]}],
            "languages": ["ar", "en"]
        }
    """
    reader = _get_reader()
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    logger.info(f"Running OCR on: {path.name}")

    results = reader.readtext(str(path))

    blocks = []
    full_text_parts = []

    for bbox, text, confidence in results:
        blocks.append(
            {
                "text": text.strip(),
                "confidence": round(confidence, 3),
                "bbox": [[int(p) for p in point] for point in bbox],
            }
        )
        if text.strip():
            full_text_parts.append(text.strip())

    full_text = "\n".join(full_text_parts)

    result = {
        "text": full_text,
        "blocks": blocks,
        "block_count": len(blocks),
    }

    # Save processed result
    out_path = Path(settings.processed_dir) / f"{path.stem}_ocr.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"OCR complete: {len(blocks)} text blocks extracted")

    return result


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text from a PDF file. Tries direct text extraction first,
    falls back to OCR for scanned pages.
    """
    from PyPDF2 import PdfReader

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    logger.info(f"Extracting text from PDF: {path.name}")

    reader = PdfReader(str(path))
    pages = []
    full_text_parts = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        if text:
            pages.append({"page": i + 1, "text": text, "method": "direct"})
            full_text_parts.append(text)
        else:
            # Page might be scanned — flag for OCR
            pages.append({"page": i + 1, "text": "", "method": "needs_ocr"})

    result = {
        "text": "\n\n".join(full_text_parts),
        "pages": pages,
        "page_count": len(reader.pages),
        "pages_with_text": sum(1 for p in pages if p["text"]),
    }

    # Save processed result
    out_path = Path(settings.processed_dir) / f"{path.stem}_pdf.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(
        f"PDF extraction: {result['pages_with_text']}/{result['page_count']} "
        f"pages with text"
    )

    return result
