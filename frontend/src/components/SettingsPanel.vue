<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '../api'
import { errorText } from '../i18n'
import { state } from '../store'
import type { RuntimeSettings } from '../types'

const { t } = useI18n()

const form = reactive<RuntimeSettings>({ chunk_size: 500, chunk_overlap: 100, top_k: 4 })
const saving = ref(false)
const message = ref<{ ok: boolean; text: string } | null>(null)

// Copy server settings into the form once they arrive.
watch(
  () => state.settings,
  (s) => s && Object.assign(form, s),
  { immediate: true },
)

async function save() {
  saving.value = true
  message.value = null
  const before = state.settings
  try {
    const saved = await api.putSettings({ ...form })
    if (before && (before.chunk_size !== saved.chunk_size || before.chunk_overlap !== saved.chunk_overlap)) {
      state.chunkSettingsChanged = true
    }
    state.settings = saved
    message.value = { ok: true, text: t('settings.saved') }
  } catch (e) {
    message.value = { ok: false, text: errorText(e instanceof ApiError ? e.code : 'unknown') }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <h2>{{ t('settings.title') }}</h2>
    </div>
    <form class="settings" @submit.prevent="save">
      <label>
        <span>{{ t('settings.chunkSize') }}</span>
        <input v-model.number="form.chunk_size" type="number" min="50" max="4000" step="50" />
      </label>
      <label>
        <span>{{ t('settings.chunkOverlap') }}</span>
        <input v-model.number="form.chunk_overlap" type="number" min="0" :max="form.chunk_size - 1" step="10" />
      </label>
      <label>
        <span>{{ t('settings.topK') }}</span>
        <input v-model.number="form.top_k" type="number" min="1" max="20" />
      </label>
      <p class="muted small">{{ t('settings.chunkNote') }}</p>
      <div class="row">
        <button class="btn primary small" type="submit" :disabled="saving">{{ t('settings.save') }}</button>
        <span v-if="message" class="small" :class="message.ok ? 'ok' : 'fail'">{{ message.text }}</span>
      </div>
    </form>
  </section>
</template>
