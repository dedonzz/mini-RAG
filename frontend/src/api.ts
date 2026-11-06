import type {
  AskResponse,
  DocumentInfo,
  RuntimeSettings,
  Status,
  UploadResult,
} from './types'

/** Thrown for any failed request. `code` is translated via i18n `errors.<code>`. */
export class ApiError extends Error {
  constructor(public code: string) {
    super(code)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`/api${path}`, init)
  } catch {
    throw new ApiError('network_error')
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const code = body?.detail?.code
    throw new ApiError(typeof code === 'string' ? code : res.status === 422 ? 'invalid_input' : 'unknown')
  }
  return res.json() as Promise<T>
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

export const api = {
  status: () => request<Status>('/status'),
  getSettings: () => request<RuntimeSettings>('/settings'),
  putSettings: (s: RuntimeSettings) => request<RuntimeSettings>('/settings', json('PUT', s)),
  listDocuments: () => request<DocumentInfo[]>('/documents'),
  upload(files: File[]) {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return request<UploadResult[]>('/documents', { method: 'POST', body: form })
  },
  deleteDocument: (docId: string) =>
    request<{ ok: boolean }>(`/documents/${encodeURIComponent(docId)}`, { method: 'DELETE' }),
  reindex: () => request<{ errors: Record<string, string>; chunks: number }>('/reindex', { method: 'POST' }),
  ask: (question: string, topK?: number) =>
    request<AskResponse>('/ask', json('POST', { question, top_k: topK })),
}
