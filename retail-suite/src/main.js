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
const isVercelHost = /\.vercel\.app$/i.test(window.location.hostname)
if (!API_BASE_URL && isVercelHost) {
  console.error("[config] Missing VITE_API_BASE_URL. API calls will fail on Vercel host:", window.location.hostname)
}

// Browser should use session cookies by default.

const clearSession = () => {
  // Prevent redirect loop
  if (window.location.pathname.endsWith("/login")) return
  localStorage.removeItem("api_key")
  localStorage.removeItem("api_secret")
  sessionStorage.setItem("session_expired", "1")
  const base = window.location.pathname.startsWith("/retail_suite/") ? "/retail_suite/" : "/"
  window.location.href = window.location.origin + base + "login"
}

const USE_BROWSER_TOKEN_AUTH = (import.meta.env.VITE_USE_API_TOKEN === 'true') || (Boolean(API_BASE_URL) && (new URL(API_BASE_URL)).hostname !== window.location.hostname)

const getAuthHeader = () => {
  if (!USE_BROWSER_TOKEN_AUTH) return null
  const apiKey = localStorage.getItem('api_key')
  const apiSecret = localStorage.getItem('api_secret')

  return apiKey && apiSecret ? 'token ' + apiKey + ':' + apiSecret : null
}

const isPublicAuthEndpoint = (url = '') => {
  const normalized = String(url || '')
  return normalized.includes('/api/method/ping') ||
    normalized.includes('/api/method/login') ||
    normalized.includes('/api/method/logout') ||
    normalized.includes('/api/method/retail.retail.api.vercel_auth.token_login')
}

const withAuthHeaders = (init = {}, url = '') => {
  if (isPublicAuthEndpoint(url)) return init

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

setConfig('resourceFetcher', (options) => {
  const resolvedUrl = resolveResourceUrl(options.url)
  return frappeRequest({
    ...options,
    headers: withAuthHeaders({ headers: options.headers }, resolvedUrl).headers,
    url: resolvedUrl,
  })
})

const originalFetch = window.fetch.bind(window)
window.fetch = (input, init = {}) => {
  if (typeof input === 'string') {
    const isBackendPath = input.startsWith('/api/') || input === '/login' || input === '/logout'
    const isBackendUrl = API_BASE_URL && input.startsWith(API_BASE_URL + '/api/')

    if (isBackendPath || isBackendUrl) {
      if (isBackendPath && !API_BASE_URL) {
        console.error("[fetch] Missing VITE_API_BASE_URL for backend path:", input)
      }

      const requestUrl = isBackendPath ? resolveBackendUrl(input) : input
      const fetchPromise = originalFetch(requestUrl, withAuthHeaders({
        ...init,
        credentials: init.credentials ?? "include",
      }, requestUrl))

      return fetchPromise
        .then(function (resp) {
          // Only clear session for non-public endpoints
          if (!isPublicAuthEndpoint(requestUrl) && resp.status === 401) {
            clearSession()
            return Promise.reject(new Error("Session expired"))
          }
          return resp
        })
        .catch(function (error) {
          console.error("[fetch] Backend request failed", {
            input: input,
            requestUrl: requestUrl,
            apiBaseUrl: API_BASE_URL || null,
            message: error?.message || String(error),
          })
          throw error
        })
    }
  }

  return originalFetch(input, init)
}

axios.defaults.baseURL = config.FRAPPE_URL || axios.defaults.baseURL
axios.defaults.withCredentials = true
axios.interceptors.request.use((requestConfig) => {
  const requestUrl = String(requestConfig?.url || '')
  if (isPublicAuthEndpoint(requestUrl)) {
    return requestConfig
  }

  const authHeader = getAuthHeader()
  if (authHeader) {
    requestConfig.headers = requestConfig.headers || {}
    requestConfig.headers.Authorization = requestConfig.headers.Authorization || authHeader
  }
  return requestConfig
})


axios.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 401) {
      clearSession()
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)


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
      const enableSocket = import.meta.env.VITE_ENABLE_SOCKET !== 'false'
      const backendHost = API_BASE_URL ? new URL(API_BASE_URL).hostname : ''
      const frontendHost = window.location.hostname
      const isCrossHost = backendHost && backendHost !== frontendHost

      if (!enableSocket || isCrossHost) {
        return
      }

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
