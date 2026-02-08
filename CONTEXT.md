# Dhakira (ذاكرة) - Qatar Heritage AI Assistant
## Project Context File (kept updated across sessions)

---

## Project Overview
- **Client**: National Archives of Qatar (NAQ)
- **Goal**: Build a PoC AI tool for heritage preservation — oral history processing + document intelligence + conversational RAG search
- **Strategy Alignment**: NAQ's "Memory of the Future" 2025-2030 strategy
- **Gap We Fill**: Oral History + Heritage RAG (Microsoft covers newspaper digitization)

---

## Tech Stack (Confirmed)
| Layer | Tool |
|-------|------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | Next.js 14 (App Router) / Tailwind CSS |
| Speech-to-Text | OpenAI Whisper large-v3 |
| OCR | EasyOCR (Arabic + English) |
| Embeddings | intfloat/multilingual-e5-large |
| Vector Store | ChromaDB (persistent) |
| RAG Framework | LangChain + Anthropic |
| LLM | Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) |
| Arabic NLP | spaCy + CAMeL Tools (fallback to regex) |
| Metadata DB | SQLite via SQLAlchemy |
| File Storage | Local filesystem |

---

## Architecture
```
Next.js Frontend (Bilingual AR/EN with RTL support)
        ↕ (proxied via next.config.js rewrites)
FastAPI Backend (localhost:8000)
  ├── POST /api/ingest/upload     — file upload + background processing
  ├── POST /api/ingest/text       — direct text ingestion
  ├── GET  /api/ingest/status/:id — processing status
  ├── POST /api/query/ask         — RAG Q&A with citations
  ├── GET  /api/query/history/:id — chat history
  ├── GET  /api/documents/        — list all documents
  ├── GET  /api/documents/stats   — archive statistics
  ├── GET  /api/documents/:id     — document detail
  ├── GET  /api/documents/:id/entities — extracted entities
  └── GET  /api/health            — health check
        ↕
SQLite (dhakira.db) + ChromaDB (data/chroma/) + Local Files
```

---

## Files Created (Session 1)

### Backend (backend/)
- `app/main.py` — FastAPI app with CORS, lifespan, routers
- `app/config.py` — Pydantic settings from .env
- `app/db/database.py` — SQLAlchemy engine, session, Base
- `app/models/document.py` — Document, ChatSession, ChatMessage models
- `app/models/schemas.py` — Pydantic request/response schemas
- `app/routers/ingest.py` — Upload endpoints + background processing pipeline
- `app/routers/query.py` — RAG Q&A endpoint + chat history
- `app/routers/documents.py` — Document CRUD + stats + entities
- `app/services/whisper_service.py` — Whisper transcription (lazy-loaded)
- `app/services/ocr_service.py` — EasyOCR for images + PyPDF2 for PDFs
- `app/services/embedding_service.py` — Text chunking + ChromaDB storage + similarity search
- `app/services/rag_service.py` — Claude RAG with bilingual system prompts + citations
- `app/services/entity_service.py` — NER with CAMeL Tools / spaCy / regex fallback
- `requirements.txt` — All Python dependencies
- `.env.example` — Environment variable template

### Frontend (frontend/)
- `package.json` — Next.js 14 + Tailwind + lucide-react
- `next.config.js` — API proxy rewrites to backend
- `tailwind.config.ts` — Qatar brand colors (Al Adaam, gold, dune), dark surfaces, animations, custom shadows
- `src/app/layout.tsx` — Root layout with Islamic pattern + ambient glow orbs
- `src/app/globals.css` — Dark glassmorphism theme, glass-panel/glass-input, Islamic SVG pattern, glow orbs, RTL
- `src/app/page.tsx` — Main page with tab navigation (Chat / Archive / Upload)
- `src/components/Header.tsx` — Frosted glass nav bar with gold shimmer logo
- `src/components/ChatInterface.tsx` — Geometric hero emblem, glass panels, staggered animations, gold accents
- `src/components/ArchiveView.tsx` — Museum-grade stat cards, doc-card grid with fade-up stagger, entity chips
- `src/components/UploadView.tsx` — Glass drop zone with gold corner decorations, dark form inputs
- `src/lib/api.ts` — TypeScript API client for all backend endpoints
- `src/lib/utils.ts` — RTL detection, formatting helpers

### Scripts & Data
- `scripts/seed_demo.py` — Seeds 5 rich sample documents about Qatar heritage (pearl diving, Doha history, Al Zubarah, women's roles, architecture)

---

## Implementation Progress

### Phase 1: Backend Core ✅ COMPLETE
- [x] Project scaffolding (dirs, configs, requirements)
- [x] FastAPI app with config and DB setup
- [x] SQLite models (Document, ChatSession, ChatMessage)
- [x] Ingest API (file upload + text ingestion + background processing)
- [x] Whisper service (audio → timestamped transcript)
- [x] OCR service (image → text via EasyOCR, PDF → text via PyPDF2)
- [x] Embedding service (text chunking → ChromaDB vectors)
- [x] RAG service (retrieval → Claude → bilingual cited answer)
- [x] Entity extraction service (spaCy + CAMeL + regex fallback)
- [x] Query API endpoints (ask + history)
- [x] Document management endpoints (list, detail, stats, entities, delete)

### Phase 2: Frontend ✅ COMPLETE
- [x] Next.js project setup with Tailwind + RTL + heritage theme
- [x] Bilingual header with language toggle (EN/AR)
- [x] Chat interface with suggested questions + typing animation
- [x] Source citation display (expandable, with relevance scores)
- [x] Archive view with stats dashboard + document cards + entity display
- [x] Upload interface (drag & drop + metadata form)
- [x] API proxy configuration

### Phase 3: Integration & Demo ✅ COMPLETE
- [x] Seed script with 5 rich sample documents
- [x] Install dependencies and test end-to-end
- [x] Fix runtime issues (langchain import, spaCy fallback, Windows encoding)
- [x] Add Anthropic API key to backend/.env (account needs credits for full RAG)
- [x] Graceful fallback when Claude API unavailable (shows retrieved archive content)
- [ ] Demo script / walkthrough

### Phase 4: UI Redesign ✅ COMPLETE
- [x] Research Qatar Museums / National Museum / MIA website design patterns
- [x] Qatar Government Brand Architecture colors: Al Adaam maroon (#8A1538), gold (#E9C56B), dune (#A29475)
- [x] Tailwind config: full Qatar brand palette, dark surfaces, heritage accents, animations, custom shadows
- [x] globals.css: glassmorphism, Islamic geometric SVG pattern background, ambient glow orbs, RTL chat overrides
- [x] layout.tsx: ambient background elements (pattern + 3 glow orbs)
- [x] Header: frosted glass nav bar, gold shimmer logo, pill-shaped tab navigation
- [x] ChatInterface: geometric hero emblem, staggered animations, glass input bar, gold typing indicator
- [x] ArchiveView: museum-grade stat cards with color-coded icons, doc-card grid with fade-up stagger
- [x] UploadView: glass drop zone with gold corner decorations, dark form inputs, Sparkles upload button

### Runtime Fixes Applied
- `openai-whisper` → `faster-whisper` (Python 3.13 compat)
- `langchain.text_splitter` → `langchain_text_splitters` (LangChain 1.x)
- spaCy `_get_spacy_en()` catches `ImportError` in addition to `OSError`
- Seed script uses ASCII-safe print for Arabic titles on Windows console
- Anthropic API no credits → fallback shows retrieved archive content directly
- `@apply` with custom theme colors in CSS → replaced with raw CSS values (Tailwind limitation)

---

## How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # optional, for English NER
cp .env.example .env                     # edit with your Anthropic API key
python ../scripts/seed_demo.py           # seed sample data
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev    # starts at localhost:3000
```

### Environment Variables Needed
- `ANTHROPIC_API_KEY` — required for RAG queries

---

## Key Decisions Made
1. LLM: Claude API (Sonnet 4.5) — confirmed by user
2. Sample data: 5 curated heritage documents (pearl diving, Doha, Al Zubarah, women, architecture)
3. PoC scope: Upload → Process → Conversational Q&A with citations — confirmed
4. No Docker/K8s — runs locally for in-person demo
5. Deferred: Neo4j, fine-tuned Whisper, auth, cloud deploy, speaker diarization
6. Arabic NER: CAMeL Tools primary, regex fallback for common Qatari entities

---

## Sample Data Summary
1. **Pearl Diving in Qatar** (EN) — oral history of Ghous traditions, Nokhatha captains, pearl trade
2. **تطور الدوحة** (AR) — Doha's transformation from fishing village to modern capital
3. **Al Zubarah UNESCO Site** (EN) — archaeological history, 18th century trading port
4. **Women of Qatar** (EN) — oral histories of women's roles, Al Sadu weaving, traditional medicine
5. **Traditional Architecture & Barjeel** (EN) — wind towers, courtyard houses, Souq Waqif

---

## Notes & Lessons Learned
- ChromaDB SentenceTransformerEmbeddingFunction handles multilingual E5 natively
- Arabic text direction detection: count chars in \u0600-\u06FF range, >30% = RTL
- Next.js rewrites in next.config.js cleanly proxy /api/* to FastAPI backend
- Background tasks in FastAPI need their own DB sessions (can't reuse request-scoped ones)

---

## Resume Instructions
When starting a new chat session, read this file first to understand:
1. What has been built (check Progress section above)
2. What's next (Phase 3: install deps, test, fix issues)
3. Key files are listed in "Files Created" section
4. Run instructions in "How to Run" section
