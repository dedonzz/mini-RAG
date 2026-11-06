<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '../api'
import { errorText } from '../i18n'
import { state } from '../store'
import type { AskResponse } from '../types'

const { t } = useI18n()

interface Turn {
  id: number
  question: string
  response?: AskResponse
  error?: string
}

const turns = ref<Turn[]>([])
const question = ref('')
const asking = ref(false)
const scroller = ref<HTMLElement | null>(null)
let nextId = 1

async function scrollToBottom() {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

async function ask() {
  const q = question.value.trim()
  if (!q || asking.value) return
  turns.value.push({ id: nextId++, question: q })
  // Grab the reactive proxy so updates below re-render this turn.
  const turn = turns.value[turns.value.length - 1]
  question.value = ''
  asking.value = true
  scrollToBottom()
  try {
    // top_k comes from the saved settings on the server.
    turn.response = await api.ask(q)
  } catch (e) {
    turn.error = e instanceof ApiError ? e.code : 'unknown'
  } finally {
    asking.value = false
    scrollToBottom()
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    ask()
  }
}
</script>

<template>
  <section class="chat">
    <div class="chat-scroll" ref="scroller">
      <div v-if="!turns.length" class="chat-empty">
        <h2>{{ t('chat.emptyTitle') }}</h2>
        <p class="muted">{{ t('chat.emptyBody') }}</p>
      </div>

      <div v-for="turn in turns" :key="turn.id" class="turn">
        <div class="bubble user">{{ turn.question }}</div>

        <div v-if="turn.error" class="bubble assistant">
          <p class="banner error">{{ errorText(turn.error) }}</p>
        </div>

        <div v-else-if="turn.response" class="bubble assistant">
          <div v-if="!turn.response.llm_configured" class="banner warn">
            <strong>⚠️ {{ t('chat.notConfiguredTitle') }}</strong>
            <span>{{ t('chat.notConfiguredBody') }}</span>
          </div>
          <p v-else class="answer">{{ turn.response.answer }}</p>

          <details class="sources" :open="!turn.response.llm_configured">
            <summary>{{ t('chat.sources', { n: turn.response.sources.length }) }}</summary>
            <p v-if="!turn.response.sources.length" class="muted small">{{ t('chat.noSources') }}</p>
            <ol v-else>
              <li v-for="s in turn.response.sources" :key="s.n" class="source">
                <div class="source-head">
                  <span class="badge">[{{ s.n }}]</span>
                  <span class="doc-name">{{ s.doc_id }}</span>
                  <span class="muted small">{{ t('chat.chunk', { n: s.chunk_index }) }}</span>
                  <span class="score small" :title="t('chat.score')">
                    <span class="score-bar"><span :style="{ width: `${Math.max(0, s.score) * 100}%` }"></span></span>
                    {{ s.score.toFixed(3) }}
                  </span>
                </div>
                <p class="source-text">{{ s.text }}</p>
              </li>
            </ol>
          </details>

          <details class="prompt">
            <summary>{{ t('chat.prompt') }}</summary>
            <div v-for="(m, i) in turn.response.messages" :key="i" class="prompt-msg">
              <span class="role">{{ m.role }}</span>
              <pre>{{ m.content }}</pre>
            </div>
          </details>
        </div>

        <div v-else class="bubble assistant muted">
          <span class="spinner" aria-hidden="true"></span> {{ t('chat.thinking') }}
        </div>
      </div>
    </div>

    <form class="composer" @submit.prevent="ask">
      <textarea
        v-model="question"
        rows="2"
        :placeholder="t('chat.placeholder')"
        :disabled="state.status?.needs_reindex"
        @keydown="onKeydown"
      ></textarea>
      <div class="composer-actions">
        <button v-if="turns.length" type="button" class="btn ghost small" @click="turns = []">{{ t('chat.clear') }}</button>
        <button class="btn primary" type="submit" :disabled="asking || !question.trim()">{{ t('chat.send') }}</button>
      </div>
    </form>
  </section>
</template>
