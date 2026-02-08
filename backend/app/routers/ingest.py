"""Ingest router — file upload and processing endpoints."""

import json
import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.models.document import Document, DocumentType, ProcessingStatus
from app.models.schemas import DocumentCreate, DocumentResponse, ProcessingStatusResponse

logger = logging.getLogger("dhakira.ingest")
router = APIRouter()

ALLOWED_AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
ALLOWED_DOCS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
ALLOWED_TEXT = {".txt", ".md"}


def _detect_doc_type(filename: str) -> DocumentType:
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_AUDIO:
        return DocumentType.AUDIO
    elif ext == ".pdf":
        return DocumentType.PDF
    elif ext in ALLOWED_DOCS:
        return DocumentType.IMAGE
    elif ext in ALLOWED_TEXT:
        return DocumentType.TEXT
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. "
            f"Allowed: {ALLOWED_AUDIO | ALLOWED_DOCS | ALLOWED_TEXT}",
        )


def _process_document(doc_id: int, db_url: str):
    """Background task to process an uploaded document."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.error(f"Document {doc_id} not found")
            return

        doc.status = ProcessingStatus.PROCESSING
        db.commit()

        extracted_text = ""

        # Step 1: Extract text based on document type
        if doc.doc_type == DocumentType.AUDIO:
            from app.services.whisper_service import transcribe_audio

            result = transcribe_audio(doc.file_path, language=doc.language or None)
            extracted_text = result["text"]
            doc.duration_seconds = result.get("duration", 0)
            doc.processed_text_path = str(
                Path(settings.processed_dir) / f"{Path(doc.file_path).stem}_transcript.json"
            )

        elif doc.doc_type == DocumentType.PDF:
            from app.services.ocr_service import extract_text_from_pdf

            result = extract_text_from_pdf(doc.file_path)
            extracted_text = result["text"]

        elif doc.doc_type == DocumentType.IMAGE:
            from app.services.ocr_service import extract_text_from_image

            result = extract_text_from_image(doc.file_path)
            extracted_text = result["text"]

        elif doc.doc_type == DocumentType.TEXT:
            with open(doc.file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()

        doc.processed_text = extracted_text

        # Step 2: Extract entities
        if extracted_text:
            from app.services.entity_service import extract_entities

            entities = extract_entities(extracted_text)
            doc.entities_json = json.dumps(entities, ensure_ascii=False)

        # Step 3: Embed in vector store
        if extracted_text:
            from app.services.embedding_service import embed_document

            metadata = {
                "title": doc.title,
                "doc_type": doc.doc_type.value,
                "source": doc.source or "National Archives of Qatar",
                "language": doc.language or "ar",
                "date_original": doc.date_original or "",
                "location": doc.location or "",
            }
            embed_document(doc.id, extracted_text, metadata)

        doc.status = ProcessingStatus.COMPLETED
        db.commit()
        logger.info(f"Document {doc_id} processed successfully")

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = ProcessingStatus.FAILED
            db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    title_ar: str = Form(default=None),
    description: str = Form(default=None),
    description_ar: str = Form(default=None),
    source: str = Form(default="National Archives of Qatar"),
    language: str = Form(default="ar"),
    date_original: str = Form(default=None),
    location: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """Upload a heritage document or audio file for processing."""
    doc_type = _detect_doc_type(file.filename)

    # Choose storage directory
    if doc_type == DocumentType.AUDIO:
        target_dir = Path(settings.audio_dir)
    else:
        target_dir = Path(settings.documents_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = target_dir / file.filename
    # Avoid overwriting
    if file_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while file_path.exists():
            file_path = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = file_path.stat().st_size

    # Create DB record
    doc = Document(
        title=title,
        title_ar=title_ar,
        description=description,
        description_ar=description_ar,
        doc_type=doc_type,
        file_path=str(file_path),
        file_size=file_size,
        source=source,
        language=language,
        date_original=date_original,
        location=location,
        status=ProcessingStatus.PENDING,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"Uploaded: {file.filename} (id={doc.id}, type={doc_type.value})")

    # Trigger background processing
    background_tasks.add_task(_process_document, doc.id, settings.database_url)

    return doc


@router.post("/text", response_model=DocumentResponse)
async def ingest_text(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    text: str = Form(...),
    title_ar: str = Form(default=None),
    description: str = Form(default=None),
    source: str = Form(default="National Archives of Qatar"),
    language: str = Form(default="ar"),
    date_original: str = Form(default=None),
    location: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """Ingest raw text content directly (e.g., pre-transcribed oral histories)."""
    # Save to file
    target_dir = Path(settings.processed_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    file_path = target_dir / f"{safe_title}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    doc = Document(
        title=title,
        title_ar=title_ar,
        description=description,
        doc_type=DocumentType.TEXT,
        file_path=str(file_path),
        file_size=len(text.encode("utf-8")),
        source=source,
        language=language,
        date_original=date_original,
        location=location,
        status=ProcessingStatus.PENDING,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(_process_document, doc.id, settings.database_url)

    return doc


@router.get("/status/{doc_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(doc_id: int, db: Session = Depends(get_db)):
    """Check processing status of a document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return ProcessingStatusResponse(
        document_id=doc.id,
        status=doc.status.value,
        message=f"Document '{doc.title}' is {doc.status.value}",
    )
