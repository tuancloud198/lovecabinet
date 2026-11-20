import { createApp } from 'vue'
import App from '@/App.vue'
import { applyTheme } from '@/theme.js'
import '@/style.css'
applyTheme() // before mounting, so the saved season shows without a flash
createApp(App).mount('#app')
