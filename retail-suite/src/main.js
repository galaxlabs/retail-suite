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
import { API_BASE_URL, resolveBackendUrl } from '@/config/runtime'

const pinia = createPinia()

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)

const getAuthHeader = () => {
  const apiKey = localStorage.getItem('api_key')
  const apiSecret = localStorage.getItem('api_secret')

  return apiKey && apiSecret ? 'token ' + apiKey + ':' + apiSecret : null
}

const withAuthHeaders = (init = {}) => {
  const authHeader = getAuthHeader()
  if (!authHeader) return init

  const headers = new Headers(init.headers || {})
  if (!headers.has('Authorization')) {
    headers.set('Authorization', authHeader)
  }

  return { ...init, headers }
}

const resolveResourceUrl = (url = '') => {
  if (!url || /^https?:\/\//i.test(url)) return url
  if (url.startsWith('/')) return resolveBackendUrl(url)

  return resolveBackendUrl('/api/method/' + url)
}

setConfig('resourceFetcher', (options) => frappeRequest({
  ...options,
  headers: withAuthHeaders({ headers: options.headers }).headers,
  url: resolveResourceUrl(options.url),
}))

const originalFetch = window.fetch.bind(window)
window.fetch = (input, init = {}) => {
  if (typeof input === 'string') {
    const isBackendPath = input.startsWith('/api/') || input === '/login' || input === '/logout'
    const isBackendUrl = API_BASE_URL && input.startsWith(API_BASE_URL + '/api/')

    if (isBackendPath || isBackendUrl) {
      const requestUrl = isBackendPath ? resolveBackendUrl(input) : input
      return originalFetch(requestUrl, withAuthHeaders({
        ...init,
        credentials: init.credentials ?? 'include',
      }))
    }
  }

  return originalFetch(input, init)
}

axios.defaults.baseURL = config.FRAPPE_URL || axios.defaults.baseURL
axios.defaults.withCredentials = true
axios.interceptors.request.use((requestConfig) => {
  const authHeader = getAuthHeader()
  if (authHeader) {
    requestConfig.headers = requestConfig.headers || {}
    requestConfig.headers.Authorization = requestConfig.headers.Authorization || authHeader
  }
  return requestConfig
})

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
