"""Query router — heritage Q&A with RAG."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import ChatMessage, ChatSession
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import query_heritage

logger = logging.getLogger("dhakira.query")
router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Ask a question about Qatar's heritage.
    The system retrieves relevant archived content and generates
    a cited answer using Claude.
    """
    # Load chat history if session exists
    chat_history = []
    if request.session_id:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == request.session_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        chat_history = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

    # Query RAG
    result = query_heritage(
        question=request.question,
        session_id=request.session_id,
        language=request.language,
        chat_history=chat_history,
    )

    # Save session and messages
    session_id = result["session_id"]

    existing_session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .first()
    )
    if not existing_session:
        session = ChatSession(
            session_id=session_id,
            language=result["language"],
        )
        db.add(session)

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.question,
    )
    db.add(user_msg)

    # Save assistant message
    import json

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=result["answer"],
        sources_json=json.dumps(result["sources"], ensure_ascii=False),
    )
    db.add(assistant_msg)

    db.commit()

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session_id,
        language=result["language"],
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "sources": msg.sources_json,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    }
