/**
 * Dhakira API client — communicates with the FastAPI backend.
 */

const API_BASE = "/api";

export interface Document {
  id: number;
  title: string;
  title_ar: string | null;
  description: string | null;
  description_ar: string | null;
  doc_type: string;
  file_path: string;
  file_size: number | null;
  status: string;
  processed_text: string | null;
  entities_json: string | null;
  duration_seconds: number | null;
  source: string | null;
  language: string;
  date_original: string | null;
  location: string | null;
  created_at: string;
  updated_at: string;
}

export interface SourceReference {
  document_id: number;
  document_title: string;
  chunk_text: string;
  relevance_score: number;
  page_or_timestamp: string | null;
}

export interface QueryResponse {
  answer: string;
  sources: SourceReference[];
  session_id: string;
  language: string;
}

export interface ArchiveStats {
  total_documents: number;
  completed: number;
  processing: number;
  failed: number;
  by_type: Record<string, number>;
  vectors_count: number;
}

export interface Entity {
  text: string;
  label: string;
  start?: number;
  end?: number;
}

// ── Query ────────────────────────────────────────────────────────

export async function askQuestion(
  question: string,
  sessionId?: string,
  language: string = "auto"
): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      session_id: sessionId,
      language,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Query failed" }));
    throw new Error(err.detail || "Query failed");
  }

  return res.json();
}

// ── Documents ────────────────────────────────────────────────────

export async function getDocuments(): Promise<{
  documents: Document[];
  total: number;
}> {
  const res = await fetch(`${API_BASE}/documents/`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function getStats(): Promise<ArchiveStats> {
  const res = await fetch(`${API_BASE}/documents/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function getDocumentEntities(
  docId: number
): Promise<{ document_id: number; entities: Entity[] }> {
  const res = await fetch(`${API_BASE}/documents/${docId}/entities`);
  if (!res.ok) throw new Error("Failed to fetch entities");
  return res.json();
}

// ── Upload ───────────────────────────────────────────────────────

export async function uploadDocument(
  file: File,
  metadata: {
    title: string;
    title_ar?: string;
    description?: string;
    source?: string;
    language?: string;
    date_original?: string;
    location?: string;
  }
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", metadata.title);
  if (metadata.title_ar) formData.append("title_ar", metadata.title_ar);
  if (metadata.description) formData.append("description", metadata.description);
  if (metadata.source) formData.append("source", metadata.source);
  if (metadata.language) formData.append("language", metadata.language);
  if (metadata.date_original) formData.append("date_original", metadata.date_original);
  if (metadata.location) formData.append("location", metadata.location);

  const res = await fetch(`${API_BASE}/ingest/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

// ── Health ───────────────────────────────────────────────────────

export async function checkHealth(): Promise<{
  status: string;
  version: string;
  app: string;
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend is not reachable");
  return res.json();
}
