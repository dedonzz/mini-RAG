// Shapes of the JSON returned by the FastAPI backend (backend/app/main.py).

export interface Status {
  llm: string
  llm_configured: boolean
  embedder: string
  needs_reindex: boolean
  documents: number
  chunks: number
  max_upload_mb: number
}

export interface RuntimeSettings {
  chunk_size: number
  chunk_overlap: number
  top_k: number
}

export interface DocumentInfo {
  doc_id: string
  size_bytes: number
  uploaded_at: string
  chunks: number
}

export interface UploadResult {
  doc_id: string
  ok: boolean
  chunks?: number
  error?: string
}

export interface Source {
  n: number
  doc_id: string
  chunk_index: number
  score: number
  text: string
}

export interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface AskResponse {
  answer: string
  llm_configured: boolean
  sources: Source[]
  messages: Message[]
}
