// Small shared state for the whole app (no Pinia needed at this size).
import { reactive } from 'vue'
import { api } from './api'
import type { DocumentInfo, RuntimeSettings, Status } from './types'

export const state = reactive({
  status: null as Status | null,
  settings: null as RuntimeSettings | null,
  documents: [] as DocumentInfo[],
  // Set when chunk settings were changed since the last reindex (this session).
  chunkSettingsChanged: false,
  loadError: null as string | null,
})

export async function refresh() {
  try {
    const [status, documents] = await Promise.all([api.status(), api.listDocuments()])
    state.status = status
    state.documents = documents
    state.settings ??= await api.getSettings()
    state.loadError = null
  } catch (e) {
    state.loadError = e instanceof Error ? e.message : 'unknown'
  }
}
