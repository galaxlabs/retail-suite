import { reactive, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import router from '../router'
import { resolveBackendUrl } from '@/config/runtime'

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
        const response = await fetch(resolveBackendUrl('/api/method/login'), {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ usr: username, pwd: password }),
        })

        const data = await response.json().catch(() => ({}))
        if (!response.ok || data.exc || data.exception) {
          throw new Error(data.message || data.exception || 'Login failed')
        }

        session.user = sessionUser() || username
        session.full_name = data.full_name || null
        session.email = username
        router.push({ name: 'POS' })
        return data
      } catch (err) {
        console.error('Login error:', err)
        throw err
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
      url: '/api/method/frappe.auth.get_logged_user',
    })
    console.log('👤 Logged in user:', data)
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
