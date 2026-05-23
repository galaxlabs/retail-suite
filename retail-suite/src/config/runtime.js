const trimTrailingSlash = (value = '') => value.replace(/\/+$/, '')

const env = import.meta.env

export const API_BASE_URL = trimTrailingSlash(
  env.VITE_API_BASE_URL ||
  env.VITE_FRAPPE_URL ||
  env.VITE_FRAPPE_URL_LOCAL ||
  ''
)

export const SOCKET_URL = trimTrailingSlash(
  env.VITE_SOCKET_URL || API_BASE_URL || ''
)

export const VUE_URL = env.VITE_VUE_URL || ''

export const APP_ENV = env.VITE_APP_ENV || env.VITE_ENV || env.MODE || 'development'

export const isDevelopment = env.DEV
export const isProduction = env.PROD

export const resolveBackendUrl = (url = '') => {
  if (/^https?:\/\//i.test(url)) {
    return url
  }

  if (!API_BASE_URL) {
    return url
  }

  const normalizedPath = url.startsWith('/') ? url : `/${url}`
  return `${API_BASE_URL}${normalizedPath}`
}
