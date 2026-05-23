import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import axios from 'axios'

import './index.css'
import './main.css'

import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import router from './router.js'

import {
  frappeRequest,
  setConfig,
} from 'frappe-ui'

import { initSocket } from './socket'
import config from '@/config/frappe'
import { resolveBackendUrl } from '@/config/runtime'

const pinia = createPinia()

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)

setConfig('resourceFetcher', (options) => frappeRequest({
  ...options,
  url: resolveBackendUrl(options.url),
}))

const originalFetch = window.fetch.bind(window)
window.fetch = (input, init = {}) => {
  if (typeof input === 'string') {
    const shouldProxy = input.startsWith('/api/') || input === '/login' || input === '/logout'
    if (shouldProxy) {
      return originalFetch(resolveBackendUrl(input), {
        credentials: init.credentials ?? 'include',
        ...init,
      })
    }
  }

  return originalFetch(input, init)
}

axios.defaults.baseURL = config.FRAPPE_URL || axios.defaults.baseURL
axios.defaults.withCredentials = true

app.use(router)
app.use(pinia)
app.use(Toast)
app.use(vuetify)

setTimeout(async () => {
  const { useToast } = await import('vue-toastification')
  window.$toast = useToast()
}, 0)

function initializeSocketLazy() {
  requestIdleCallback(() => {
    try {
      const siteName = import.meta.env.VITE_SITE_NAME || window.location.hostname

      if (!window.frappe) window.frappe = {}

      const socket = initSocket(siteName)

      setTimeout(() => {
        socket.connect()
      }, 0)

      window.frappe.realtime = socket
    } catch (err) {
      console.warn('[socket] init failed:', err)
    }
  })
}

initializeSocketLazy()

app.mount('#app')
