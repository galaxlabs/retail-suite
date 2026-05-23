import { reactive, computed } from 'vue'
import { createResource, frappeRequest, call } from 'frappe-ui'
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

  login: createResource({
    url: 'login',
    makeParams({ username, password }) {
      return { usr: username, pwd: password }
    },
    async onSuccess(data) {
      session.user = sessionUser()
      session.full_name = data?.full_name || null
      session.email = data?.email || null
      session.login.reset()
      router.push({ name: 'POS' })
    },
    onError(err) {
      console.error('❌ Login error:', err)
    },
  }),

  logout: createResource({
    url: 'logout',
    onSuccess() {
      session.user = null
      session.full_name = null
      session.email = null
      router.push({ name: 'Login' })
    },
    onError() {
      session.user = null
      router.push({ name: 'Login' })
    },
  }),
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
