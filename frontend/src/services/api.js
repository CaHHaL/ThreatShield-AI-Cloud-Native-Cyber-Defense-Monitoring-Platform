import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_URL  = import.meta.env.VITE_WS_URL  || 'ws://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 12000,
})

// ─── REST API calls ─────────────────────────────────────────────────────────

export const fetchStats      = ()              => api.get('/api/stats').then(r => r.data)
export const fetchAttacks    = (params = {})   => api.get('/api/attacks', { params }).then(r => r.data)
export const fetchAttack     = (id)            => api.get(`/api/attacks/${id}`).then(r => r.data)
export const fetchCountries  = ()              => api.get('/api/countries').then(r => r.data)
export const fetchTopIPs     = ()              => api.get('/api/top-ips').then(r => r.data)
export const fetchTimeline   = (hours = 24)   => api.get('/api/timeline', { params: { hours } }).then(r => r.data)
export const fetchCategories = ()              => api.get('/api/categories').then(r => r.data)

// ─── WebSocket feed ──────────────────────────────────────────────────────────

export const createFeedSocket = (onMessage, onOpen, onClose, onError) => {
  const ws = new WebSocket(`${WS_URL}/ws/feed`)

  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)) } catch { /* ignore malformed */ }
  }
  ws.onopen  = onOpen  || (() => console.log('[WS] Connected to ThreatShield feed'))
  ws.onclose = onClose || (() => console.log('[WS] Feed disconnected'))
  ws.onerror = onError || ((e) => console.warn('[WS] Error', e))

  return ws
}
