import { reactive, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import router from '../router'
import { resolveBackendUrl } from '@/config/runtime'

function extractServerMessage(payload, fallback = 'Login failed') {
  if (!payload || typeof payload !== 'object') return fallback

  const direct =
    payload.message?.message ||
    payload.message ||
    payload.exception ||
    payload.exc_type

  if (typeof direct === 'string' && direct.trim()) {
    return direct
  }

  const encoded = payload._server_messages
  if (typeof encoded === 'string' && encoded.trim()) {
    try {
      const parsed = JSON.parse(encoded)
      if (Array.isArray(parsed) && parsed.length) {
        const first = JSON.parse(parsed[0] || '{}')
        if (first?.message) {
          return String(first.message).replace(/<[^>]*>/g, '').trim() || fallback
        }
      }
    } catch (err) {
      return fallback
    }
  }

  return fallback
}

function normalizeAuthError(err, fallback = 'Login failed') {
  const message = err?.message || ''
  if (!message) return fallback

  if (
    message.includes('Failed to fetch') ||
    message.includes('NetworkError') ||
    message.includes('Load failed')
  ) {
    return 'Cannot reach backend. Check VITE_API_BASE_URL and CORS settings.'
  }

  if (message.includes('AuthenticationError') || message.includes('Invalid login')) {
    return 'Invalid username or password.'
  }

  return message
}

function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  const user = cookies.get('user_id')
  return user === 'Guest' ? null : user
}

export const session = reactive({
  user: null,
  isAuthenticated: computed(() => !!session.user),
  full_name: null,
  email: null,

  login: {
    loading: false,
    async submit({ username, password }) {
      session.login.loading = true
      try {
        const response = await fetch(resolveBackendUrl('/api/method/retail.retail.api.vercel_auth.token_login'), {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        })

        const data = await response.json().catch(() => ({}))
        const message = data.message || {}
        if (!response.ok || data.exc || data.exception || !message.success) {
          throw new Error(extractServerMessage(data, 'Login failed'))
        }

        const userData = message.data || {}
        localStorage.setItem('api_key', userData.api_key || message.api_key)
        localStorage.setItem('api_secret', userData.api_secret || message.api_secret)

        session.user = userData.user || userData.user_id || username
        session.full_name = userData.full_name || null
        session.email = userData.email || username
        router.push({ name: 'POS' })
        return data
      } catch (err) {
        throw new Error(normalizeAuthError(err))
      } finally {
        session.login.loading = false
      }
    },
  },

  logout: {
    loading: false,
    async submit() {
      session.logout.loading = true
      try {
        await fetch(resolveBackendUrl('/api/method/logout'), {
          method: 'POST',
          credentials: 'include',
        })
        localStorage.removeItem('api_key')
        localStorage.removeItem('api_secret')
      } finally {
        session.logout.loading = false
        session.user = null
        session.full_name = null
        session.email = null
        router.push({ name: 'Login' })
      }
    },
  },
})

const request = (options) => frappeRequest({
  ...options,
  url: resolveBackendUrl(options.url),
})

export async function checkSession() {
  try {
    const data = await request({
      url: '/api/method/retail.retail.api.auth.get_logged_user',
    })
    const user = data
    if (!user || user === 'Guest') {
      session.user = null
      return false
    }

    session.user = user
    return true
  } catch (err) {
    session.user = null
    return false
  }
}

export const api = {
  get: (url, { params } = {}) => request({ url, params }),
  post: (url, data) => request({ url, method: 'POST', body: data }),
  put: (url, data) => request({ url, method: 'PUT', body: data }),
  delete: (url) => request({ url, method: 'DELETE' }),
  patch: (url, data) => request({ url, method: 'PATCH', body: data }),
}
