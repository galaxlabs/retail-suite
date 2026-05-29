// apiClient.js -- Unified API wrapper for Frappe backend
import { call } from 'frappe-ui'

/**
 * Standardized Frappe API response shape.
 * Always returns { success, data, error } regardless of backend response format.
 */
const normalizeFrappeResponse = (response) => {
  if (!response) return { success: false, data: null, error: 'No response' }

  const msg = response.message || response.data || response
  if (msg === undefined || msg === null) {
    return { success: true, data: response, error: null }
  }

  if (response.exc || response.exception || response.exc_type) {
    return { success: false, data: null, error: extractErrorMessage(response) }
  }

  if (msg && typeof msg === 'object' && msg.status === 'error') {
    return { success: false, data: null, error: msg.message || 'Unknown error' }
  }

  return { success: true, data: msg, error: null }
}

const extractErrorMessage = (response) => {
  try {
    const sm = response._server_messages
    if (typeof sm === 'string') {
      const parsed = JSON.parse(sm)
      if (Array.isArray(parsed) && parsed.length) {
        const first = JSON.parse(parsed[0] || '{}')
        const msg = (first.message || '').replace(/<[^>]*>/g, '').trim()
        return msg || response.exc || 'Server error'
      }
    }
  } catch {}
  return String(response.exc || response.exception || 'Server error')
}

export const safeCall = async (method, params = {}, options = {}) => {
  const { retry = true, timeout = 15000 } = options
  const doCall = () =>
    Promise.race([
      call(method, params),
      new Promise((_, rej) => setTimeout(() => rej(new Error('Request timeout')), timeout)),
    ])

  try {
    const response = await doCall()
    return normalizeFrappeResponse(response)
  } catch (error) {
    const msg = error?.message || String(error)
    if (retry && (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('timeout'))) {
      try {
        await new Promise(r => setTimeout(r, 1000))
        const r2 = await doCall()
        return normalizeFrappeResponse(r2)
      } catch (e2) {
        return { success: false, data: null, error: e2?.message || String(e2) }
      }
    }
    return { success: false, data: null, error: msg }
  }
}

export default safeCall
