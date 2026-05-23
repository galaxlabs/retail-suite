import { io } from 'socket.io-client'
import config from '@/config/frappe'

let socket = null

export function initSocket(siteName) {
  if (socket) return socket
  try {
    const socketTarget = config.SOCKET_URL || config.FRAPPE_URL || window.location.origin

    socket = io(socketTarget, {
      path: '/socket.io',
      withCredentials: true,
      reconnectionAttempts: 5,
      autoConnect: false,
      transports: ['polling', 'websocket'],
    })
    console.log('[socket] connecting', socket)
    socket.on('connect', () => console.log('[socket] connected'))
    socket.on('connect_error', (err) => console.warn('[socket] error:', err.message))
    socket.on('disconnect', () => console.log('[socket] disconnected'))
    return socket
  } catch (err) {
    console.error('[socket] init failed:', err)
    return { on: () => {}, off: () => {}, emit: () => {}, connect: () => {}, disconnect: () => {} }
  }
}
