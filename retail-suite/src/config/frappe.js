import {
  API_BASE_URL,
  APP_ENV,
  SOCKET_URL,
  VUE_URL,
  isDevelopment,
  isProduction,
  resolveBackendUrl,
} from './runtime'

const config = {
  FRAPPE_URL: API_BASE_URL,
  SOCKET_URL,
  VUE_URL,
  ENV: APP_ENV,
  isDevelopment,
  isProduction,
  mode: import.meta.env.MODE,
}

export default config

export const generateCredential = async (username, password) => {
  try {
    const response = await fetch(
      resolveBackendUrl('/api/method/equipment.api.auth.authenticate_and_generate_api_key'),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      }
    )

    const data = await response.json()
    if (data.message && data.message.success) {
      const creds = data.message
      localStorage.setItem('api_key', creds.api_key)
      localStorage.setItem('api_secret', creds.api_secret)
      return creds
    } else {
      throw new Error(data.message?.message || 'Login failed')
    }
  } catch (err) {
    console.error('❌ Error generating credentials:', err)
    return null
  }
}

export const getFrappeConfig = () => {
  const apiKey = localStorage.getItem('api_key')
  const apiSecret = localStorage.getItem('api_secret')

  return {
    baseURL: config.FRAPPE_URL,
    headers: {
      Authorization: `token ${apiKey}:${apiSecret}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  }
}
