import { useState, useEffect, useCallback, useRef } from 'react'
import {
  fetchStats, fetchAttacks, fetchCountries,
  fetchTopIPs, fetchTimeline, fetchCategories,
  createFeedSocket,
} from './api'

// ─── useDashboardData ──────────────────────────────────────────────────────────
/**
 * Fetches all dashboard data in parallel and refreshes every `intervalMs`.
 */
export function useDashboardData(intervalMs = 15000) {
  const [state, setState] = useState({
    stats:      null,
    attacks:    [],
    countries:  [],
    topIPs:     [],
    timeline:   [],
    categories: [],
    loading:    true,
    error:      null,
  })

  const load = useCallback(async () => {
    try {
      const [stats, attacks, countries, topIPs, timeline, categories] = await Promise.all([
        fetchStats(),
        fetchAttacks({ limit: 200 }),
        fetchCountries(),
        fetchTopIPs(),
        fetchTimeline(24),
        fetchCategories(),
      ])
      setState(s => ({
        ...s, stats, attacks, countries, topIPs, timeline, categories,
        loading: false, error: null,
      }))
    } catch (err) {
      setState(s => ({ ...s, loading: false, error: err.message }))
    }
  }, [])

  useEffect(() => {
    load()
    const id = setInterval(load, intervalMs)
    return () => clearInterval(id)
  }, [load, intervalMs])

  return { ...state, reload: load }
}


// ─── useFeed ──────────────────────────────────────────────────────────────────
/**
 * Manages a WebSocket connection to /ws/feed.
 * Returns live events and connection status.
 * Reconnects automatically on disconnect.
 */
export function useFeed(maxEvents = 150) {
  const [events,    setEvents]    = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef      = useRef(null)
  const retryTimer = useRef(null)

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState < 2) return // already open/connecting

    wsRef.current = createFeedSocket(
      (event) => {
        setConnected(true)
        setEvents(prev => [{ ...event, id: Date.now() + Math.random() }, ...prev].slice(0, maxEvents))
      },
      () => setConnected(true),
      () => {
        setConnected(false)
        // Auto-reconnect after 3s
        retryTimer.current = setTimeout(connect, 3000)
      },
      () => setConnected(false),
    )
  }, [maxEvents])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(retryTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { events, connected }
}
