<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ChatPanel from './components/ChatPanel.vue'
import DocumentPanel from './components/DocumentPanel.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import { LOCALES, setLocale, errorText, type Locale } from './i18n'
import { refresh, state } from './store'

const { t, locale } = useI18n()
const sidebarOpen = ref(false)

onMounted(refresh)
</script>

<template>
  <div class="layout">
    <header class="topbar">
      <div class="brand">
        <span class="logo" aria-hidden="true">◆</span>
        <div>
          <h1>mini-RAG</h1>
          <p class="muted small">{{ t('app.subtitle') }}</p>
        </div>
      </div>

      <div class="status" v-if="state.status">
        <span class="pill" :class="{ warn: !state.status.llm_configured }">
          {{ t('status.llm') }}: {{ state.status.llm }}
          <template v-if="!state.status.llm_configured"> · {{ t('status.notConfigured') }}</template>
        </span>
        <span class="pill">{{ t('status.embedder') }}: {{ state.status.embedder }}</span>
        <span class="muted small">
          {{ t('status.stats', { documents: state.status.documents, chunks: state.status.chunks }) }}
        </span>
      </div>

      <div class="topbar-actions">
        <div class="segmented" role="group" :aria-label="t('lang.label')">
          <button
            v-for="l in LOCALES"
            :key="l.code"
            :class="{ active: locale === l.code }"
            :aria-pressed="locale === l.code"
            @click="setLocale(l.code as Locale)"
          >
            {{ l.label }}
          </button>
        </div>
        <button class="btn ghost menu-btn" @click="sidebarOpen = true">☰ {{ t('app.menu') }}</button>
      </div>
    </header>

    <p v-if="state.loadError" class="banner error">{{ errorText(state.loadError) }}</p>

    <div class="body">
      <div class="scrim" v-if="sidebarOpen" @click="sidebarOpen = false"></div>
      <aside class="sidebar" :class="{ open: sidebarOpen }">
        <button class="btn ghost close-btn" @click="sidebarOpen = false">✕ {{ t('app.close') }}</button>
        <DocumentPanel />
        <SettingsPanel />
      </aside>
      <main class="main">
        <ChatPanel />
      </main>
    </div>
  </div>
</template>
