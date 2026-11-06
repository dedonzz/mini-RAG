<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '../api'
import { errorText } from '../i18n'
import { refresh, state } from '../store'

const { t } = useI18n()

const busy = ref<'upload' | 'reindex' | null>(null)
const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
// Feedback lines shown under the drop zone after an action.
const notices = ref<{ ok: boolean; text: string }[]>([])

function codeOf(e: unknown) {
  return e instanceof ApiError ? e.code : 'unknown'
}

async function upload(files: File[]) {
  if (!files.length || busy.value) return
  busy.value = 'upload'
  notices.value = []
  try {
    const results = await api.upload(files)
    notices.value = results.map((r) =>
      r.ok
        ? { ok: true, text: t('docs.uploadOk', { name: r.doc_id, n: r.chunks }) }
        : { ok: false, text: t('docs.uploadFail', { name: r.doc_id, error: errorText(r.error ?? 'unknown') }) },
    )
  } catch (e) {
    notices.value = [{ ok: false, text: errorText(codeOf(e)) }]
  } finally {
    busy.value = null
    await refresh()
  }
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  upload(Array.from(input.files ?? []))
  input.value = ''
}

function onDrop(e: DragEvent) {
  dragging.value = false
  upload(Array.from(e.dataTransfer?.files ?? []))
}

async function remove(docId: string) {
  if (!confirm(t('docs.confirmDelete', { name: docId }))) return
  try {
    await api.deleteDocument(docId)
  } catch (e) {
    notices.value = [{ ok: false, text: errorText(codeOf(e)) }]
  }
  await refresh()
}

async function reindex() {
  busy.value = 'reindex'
  notices.value = []
  try {
    const res = await api.reindex()
    state.chunkSettingsChanged = false
    notices.value = [
      { ok: true, text: t('docs.reindexDone', { n: res.chunks }) },
      ...Object.entries(res.errors).map(([name, code]) => ({
        ok: false,
        text: t('docs.uploadFail', { name, error: errorText(code) }),
      })),
    ]
  } catch (e) {
    notices.value = [{ ok: false, text: errorText(codeOf(e)) }]
  } finally {
    busy.value = null
    await refresh()
  }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <h2>{{ t('docs.title') }}</h2>
      <button class="btn small" :disabled="!!busy || !state.documents.length" @click="reindex">
        {{ busy === 'reindex' ? t('docs.reindexing') : t('docs.reindex') }}
      </button>
    </div>

    <p v-if="state.status?.needs_reindex" class="banner error">{{ t('docs.needsReindex') }}</p>
    <p v-else-if="state.chunkSettingsChanged" class="banner warn">{{ t('docs.settingsChanged') }}</p>

    <div
      class="dropzone"
      :class="{ dragging, busy: busy === 'upload' }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <template v-if="busy === 'upload'">
        <span class="spinner" aria-hidden="true"></span>
        <span>{{ t('docs.uploading') }}</span>
      </template>
      <template v-else>
        <span>
          {{ t('docs.drop') }}
          <button class="linklike" @click="fileInput?.click()">{{ t('docs.browse') }}</button>
        </span>
        <span class="muted small">{{ t('docs.hint', { mb: state.status?.max_upload_mb ?? 20 }) }}</span>
      </template>
      <input ref="fileInput" type="file" multiple accept=".txt,.md,.pdf" hidden @change="onPick" />
    </div>

    <ul v-if="notices.length" class="notices">
      <li v-for="(n, i) in notices" :key="i" :class="n.ok ? 'ok' : 'fail'">{{ n.ok ? '✓' : '✕' }} {{ n.text }}</li>
    </ul>

    <p v-if="!state.documents.length" class="muted small empty">{{ t('docs.empty') }}</p>
    <ul v-else class="doc-list">
      <li v-for="doc in state.documents" :key="doc.doc_id">
        <div class="doc-info">
          <span class="doc-name" :title="doc.doc_id">{{ doc.doc_id }}</span>
          <span class="muted small">{{ formatSize(doc.size_bytes) }} · {{ t('docs.chunks', { n: doc.chunks }) }}</span>
        </div>
        <button class="btn ghost small danger" :disabled="!!busy" :aria-label="t('docs.delete')" @click="remove(doc.doc_id)">
          {{ t('docs.delete') }}
        </button>
      </li>
    </ul>
  </section>
</template>
