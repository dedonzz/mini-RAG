import { createApp } from 'vue'
import App from './App.vue'
import { i18n, setLocale } from './i18n'
import './style.css'

setLocale(i18n.global.locale.value as 'zh-TW' | 'en')
createApp(App).use(i18n).mount('#app')
