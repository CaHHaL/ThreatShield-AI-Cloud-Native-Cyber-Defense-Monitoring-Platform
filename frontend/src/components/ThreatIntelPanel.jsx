import { useState } from 'react'
import SessionDetailModal from './SessionDetailModal'
import styles from './ThreatIntelPanel.module.css'

const SEV_CLASS  = { CRITICAL: 'badge-critical', HIGH: 'badge-high', MEDIUM: 'badge-medium', LOW: 'badge-low' }
const TYPE_ICON  = {
  brute_force:         '🔑',
  reconnaissance:      '🔍',
  malware_delivery:    '💀',
  automation:          '🤖',
  credential_stuffing: '🎭',
  web_recon:           '🌐',
  unknown:             '❓',
}
const SOURCE_ICON = { cowrie: '🐚', web_login: '🔒' }

export default function ThreatIntelPanel({ attacks }) {
  const [selected, setSelected] = useState(null)
  const recent = attacks.slice(0, 40)

  return (
    <>
      <div className={styles.wrapper}>
        <div className={styles.header}>
          <span className={styles.title}>🔍 Threat Intelligence</span>
          <span className={styles.sub}>{attacks.length} sessions total</span>
        </div>

        <div className={styles.list}>
          {recent.length === 0 ? (
            <div className={styles.empty}>No sessions captured yet.</div>
          ) : (
            recent.map(s => (
              <div
                key={s.id}
                className={styles.item}
                onClick={() => setSelected(s)}
                title="Click for full details"
              >
                <span className={styles.typeIcon}>{TYPE_ICON[s.attack_type] || '❓'}</span>
                <span className={`mono ${styles.ip}`}>{s.attacker_ip}</span>
                <span className={styles.country}>{s.country_code || '??'}</span>
                <span className={`badge ${SEV_CLASS[s.severity]}`}>{s.severity}</span>
                <span className={styles.type}>{s.attack_type?.replace(/_/g, ' ')}</span>
                <span className={styles.score}>{s.threat_score}</span>
                <span className={styles.source}>{SOURCE_ICON[s.source] || '?'}</span>
                <span className={styles.arrow}>›</span>
              </div>
            ))
          )}
        </div>
      </div>

      {selected && (
        <SessionDetailModal session={selected} onClose={() => setSelected(null)} />
      )}
    </>
  )
}
