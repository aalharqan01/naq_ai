"""RAG service — Retrieval-Augmented Generation with Claude for heritage Q&A."""

import json
import logging
import uuid
from typing import Optional

from anthropic import Anthropic

from app.config import settings
from app.services.embedding_service import search_similar

logger = logging.getLogger("dhakira.rag")

_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


SYSTEM_PROMPT_EN = """You are Dhakira (ذاكرة), an AI heritage assistant for the National Archives of Qatar.
Your role is to help researchers, historians, and the public explore Qatar's rich heritage
through archived documents, oral histories, and historical records.

IMPORTANT RULES:
1. ONLY answer based on the provided source documents. Never fabricate information.
2. If the sources don't contain enough information, say so honestly.
3. Always cite your sources by referencing the document title and relevant details.
4. Be respectful of Qatari culture, traditions, and heritage.
5. You can respond in both Arabic and English — match the user's language.
6. When quoting oral histories, preserve the speaker's voice and context.
7. Format citations as [Source: Document Title] inline.

You represent the National Archives of Qatar's commitment to preserving heritage
for future generations through the "Memory of the Future" initiative."""

SYSTEM_PROMPT_AR = """أنت ذاكرة، مساعد الذكاء الاصطناعي للتراث في الأرشيف الوطني لدولة قطر.
دورك هو مساعدة الباحثين والمؤرخين والجمهور في استكشاف تراث قطر الغني
من خلال الوثائق المؤرشفة والتاريخ الشفوي والسجلات التاريخية.

القواعد المهمة:
1. أجب فقط بناءً على الوثائق المصدرية المقدمة. لا تختلق معلومات أبداً.
2. إذا لم تحتوي المصادر على معلومات كافية، قل ذلك بصدق.
3. استشهد دائماً بمصادرك من خلال الإشارة إلى عنوان الوثيقة والتفاصيل ذات الصلة.
4. كن محترماً للثقافة والتقاليد والتراث القطري.
5. يمكنك الرد باللغتين العربية والإنجليزية — طابق لغة المستخدم.
6. عند اقتباس التاريخ الشفوي، حافظ على صوت المتحدث وسياقه.
7. صيغ الاستشهادات كالتالي [المصدر: عنوان الوثيقة] داخل النص.

أنت تمثل التزام الأرشيف الوطني لدولة قطر بحفظ التراث
للأجيال القادمة من خلال مبادرة "ذاكرة المستقبل"."""


def _detect_language(text: str) -> str:
    """Simple heuristic to detect Arabic vs English."""
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    return "ar" if arabic_chars > len(text) * 0.3 else "en"


def _format_context(results: list[dict]) -> str:
    """Format retrieved chunks into a context block for the LLM."""
    if not results:
        return "No relevant documents found in the archive."

    parts = []
    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})
        title = meta.get("title", f"Document {meta.get('document_id', '?')}")
        doc_type = meta.get("doc_type", "document")
        source = meta.get("source", "National Archives of Qatar")

        parts.append(
            f"--- Source {i}: {title} ({doc_type}) ---\n"
            f"Origin: {source}\n"
            f"Content:\n{r['text']}\n"
        )

    return "\n".join(parts)


def query_heritage(
    question: str,
    session_id: Optional[str] = None,
    language: str = "auto",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Answer a heritage question using RAG.

    Returns:
        {
            "answer": "...",
            "sources": [...],
            "session_id": "...",
            "language": "ar" | "en"
        }
    """
    client = _get_client()

    # Detect language
    if language == "auto":
        language = _detect_language(question)

    # Retrieve relevant chunks
    results = search_similar(question, top_k=settings.rag_top_k)
    context = _format_context(results)

    # Build messages
    system_prompt = SYSTEM_PROMPT_AR if language == "ar" else SYSTEM_PROMPT_EN

    messages = []

    # Include chat history if provided
    if chat_history:
        for msg in chat_history[-6:]:  # Last 3 exchanges
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Current question with context
    user_message = (
        f"Based on the following archived sources, answer the question.\n\n"
        f"ARCHIVED SOURCES:\n{context}\n\n"
        f"QUESTION: {question}"
    )
    messages.append({"role": "user", "content": user_message})

    # Call Claude
    logger.info(f"Querying Claude ({language}): {question[:100]}...")

    try:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )
        answer = response.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        # Fallback: return retrieved context directly so the demo still works
        if results:
            snippets = "\n\n".join(
                f"From \"{r.get('metadata', {}).get('title', 'Archive')}\":\n{r['text'][:300]}"
                for r in results[:3]
            )
            answer = (
                "⚠ AI generation is temporarily unavailable. "
                "Here are the most relevant archived passages:\n\n"
                + snippets
            ) if language == "en" else (
                "⚠ توليد الذكاء الاصطناعي غير متاح مؤقتاً. "
                "إليك المقاطع الأرشيفية الأكثر صلة:\n\n"
                + snippets
            )
        else:
            answer = (
                "Sorry, I couldn't process your question at this time. "
                "Please check the API key configuration."
                if language == "en"
                else "عذراً، لم أتمكن من معالجة سؤالك حالياً. يرجى التحقق من إعدادات مفتاح API."
            )

    # Build source references
    sources = []
    for r in results:
        meta = r.get("metadata", {})
        sources.append(
            {
                "document_id": int(meta.get("document_id", 0)),
                "document_title": meta.get("title", "Unknown"),
                "chunk_text": r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"],
                "relevance_score": round(1 - (r.get("distance", 0) or 0), 3),
                "page_or_timestamp": meta.get("page_or_timestamp"),
            }
        )

    if not session_id:
        session_id = str(uuid.uuid4())

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "language": language,
    }
