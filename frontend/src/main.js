import { createApp } from 'vue'
import App from '@/App.vue'
// Be Vietnam Pro, bundled (served from /assets/ like the rest of the app, no Google Fonts request). Each file
// covers Vietnamese, Latin and Latin-extended; the browser only downloads the ranges a page uses.
import '@fontsource/be-vietnam-pro/400.css'
import '@fontsource/be-vietnam-pro/500.css'
import '@fontsource/be-vietnam-pro/600.css'
import '@fontsource/be-vietnam-pro/700.css'
import '@fontsource/be-vietnam-pro/800.css'
import '@fontsource/be-vietnam-pro/700-italic.css'
import '@fontsource/be-vietnam-pro/800-italic.css'
import '@/style.css'
createApp(App).mount('#app')
