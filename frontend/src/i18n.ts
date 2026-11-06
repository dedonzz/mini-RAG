import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zhTW from './locales/zh-TW.json'

export const LOCALES = [
  { code: 'zh-TW', label: '中文' },
  { code: 'en', label: 'EN' },
] as const
export type Locale = (typeof LOCALES)[number]['code']

const STORAGE_KEY = 'mini-rag.locale'

function initialLocale(): Locale {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'zh-TW' || saved === 'en') return saved
  } catch {
    // storage unavailable (private mode etc.) — fall through
  }
  return navigator.language.toLowerCase().startsWith('zh') ? 'zh-TW' : 'en'
}

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: 'en',
  messages: { 'zh-TW': zhTW, en },
})

export function setLocale(locale: Locale) {
  i18n.global.locale.value = locale
  document.documentElement.lang = locale === 'zh-TW' ? 'zh-Hant' : 'en'
  try {
    localStorage.setItem(STORAGE_KEY, locale)
  } catch {
    // ignore
  }
}

/** Translate an API error code, falling back to a generic message. */
export function errorText(code: string): string {
  const key = `errors.${code}`
  return i18n.global.te(key) ? i18n.global.t(key) : i18n.global.t('errors.unknown')
}
