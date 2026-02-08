"""Documents router — listing, detail, and management endpoints."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document, ProcessingStatus
from app.models.schemas import DocumentListResponse, DocumentResponse, EntitiesResponse, Entity
from app.services.embedding_service import get_vector_count

logger = logging.getLogger("dhakira.documents")
router = APIRouter()


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    doc_type: str = Query(None),
    db: Session = Depends(get_db),
):
    """List all documents in the archive."""
    query = db.query(Document)

    if status:
        query = query.filter(Document.status == status)
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)

    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return DocumentListResponse(documents=documents, total=total)


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get archive statistics."""
    total = db.query(Document).count()
    completed = db.query(Document).filter(Document.status == ProcessingStatus.COMPLETED).count()
    processing = db.query(Document).filter(Document.status == ProcessingStatus.PROCESSING).count()
    failed = db.query(Document).filter(Document.status == ProcessingStatus.FAILED).count()

    by_type = {}
    for doc_type in ["audio", "pdf", "image", "text"]:
        by_type[doc_type] = db.query(Document).filter(Document.doc_type == doc_type).count()

    return {
        "total_documents": total,
        "completed": completed,
        "processing": processing,
        "failed": failed,
        "by_type": by_type,
        "vectors_count": get_vector_count(),
    }


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{doc_id}/entities", response_model=EntitiesResponse)
async def get_document_entities(doc_id: int, db: Session = Depends(get_db)):
    """Get extracted entities for a document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    entities = []
    if doc.entities_json:
        raw = json.loads(doc.entities_json)
        entities = [Entity(**e) for e in raw]

    return EntitiesResponse(document_id=doc.id, entities=entities)


@router.delete("/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document from the archive."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector store
    try:
        from app.services.embedding_service import _get_collection
        collection = _get_collection()
        existing = collection.get(where={"document_id": str(doc_id)})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception as e:
        logger.warning(f"Could not remove vectors for doc {doc_id}: {e}")

    db.delete(doc)
    db.commit()

    return {"message": f"Document {doc_id} deleted"}
