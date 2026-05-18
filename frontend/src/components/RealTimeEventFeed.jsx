import { useEffect, useRef } from 'react'
import styles from './RealTimeEventFeed.module.css'

const SEV_COLORS = {
  CRITICAL: '#ff3d71',
  HIGH:     '#ffaa00',
  MEDIUM:   '#a855f7',
  LOW:      '#00e096',
  INFO:     '#00d4ff',
}

const TYPE_ICONS = {
  new_session:         '🌐',
  credential_attempt:  '🔑',
  suspicious_command:  '⚠️',
  malware_download:    '💀',
  web_login_attempt:   '🔒',
  CRITICAL:            '🚨',
  HIGH:                '⚠️',
  MEDIUM:              '🔍',
  LOW:                 '📡',
}

function EventItem({ evt }) {
  const color = SEV_COLORS[evt.severity] || '#94a3b8'
  const icon  = TYPE_ICONS[evt.type] || TYPE_ICONS[evt.severity] || '📡'
  const time  = evt.timestamp
    ? new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : 'now'

  return (
    <div className={`${styles.event} animate-slide`}>
      <span className={styles.evtIcon}>{icon}</span>
      <div className={styles.evtBody}>
        <span className={styles.evtSev} style={{ color }}>[{evt.severity || 'INFO'}]</span>
        {' '}
        <span className={styles.evtMsg}>{evt.message}</span>
        {evt.country && (
          <span className={styles.evtCountry}> · {evt.country}</span>
        )}
        {evt.ip && (
          <span className={styles.evtIp}> {evt.ip}</span>
        )}
      </div>
      <span className={styles.evtTime}>{time}</span>
    </div>
  )
}

export default function RealTimeEventFeed({ events, connected }) {
  const listRef = useRef(null)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0
    }
  }, [events.length])

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>🚨 Live Event Feed</span>
        <div className={`${styles.status} ${connected ? styles.live : styles.offline}`}>
          <span className={`pulse ${connected ? 'pulse-green' : 'pulse-danger'}`} />
          <span>{connected ? 'LIVE' : 'OFFLINE'}</span>
        </div>
      </div>

      <div className={styles.list} ref={listRef}>
        {events.length === 0 ? (
          <div className={styles.empty}>
            <span className="pulse pulse-accent" />
            <span>Waiting for attack events...</span>
          </div>
        ) : (
          events.map(evt => (
            <EventItem key={evt.id} evt={evt} />
          ))
        )}
      </div>

      <div className={styles.footer}>
        <span>{events.length} events captured</span>
      </div>
    </div>
  )
}
