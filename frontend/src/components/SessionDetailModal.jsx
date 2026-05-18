import { useEffect, useState } from 'react'
import { fetchAttack } from '../services/api'
import styles from './SessionDetailModal.module.css'

const SEV_CLASS = { CRITICAL: 'badge-critical', HIGH: 'badge-high', MEDIUM: 'badge-medium', LOW: 'badge-low' }

export default function SessionDetailModal({ session, onClose }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchAttack(session.session_id)
      .then(setDetail)
      .catch(() => setDetail(session))
      .finally(() => setLoading(false))
  }, [session.session_id])

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  const d = detail || session

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={`badge ${SEV_CLASS[d.severity]}`}>{d.severity}</span>
            <span className={`mono ${styles.ip}`}>{d.attacker_ip}</span>
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">×</button>
        </div>

        {/* Body */}
        <div className={styles.body}>
          {loading ? (
            <div className={styles.loading}>Loading session details...</div>
          ) : (
            <>
              {/* Info Grid */}
              <div className={styles.infoGrid}>
                <InfoRow label="Session ID" value={d.session_id} mono />
                <InfoRow label="Source" value={d.source === 'cowrie' ? '🐚 Cowrie SSH/Telnet' : '🔒 Web Login'} />
                <InfoRow label="Country" value={`${d.country || 'Unknown'}${d.city ? ` · ${d.city}` : ''}`} />
                <InfoRow label="Attack Type" value={d.attack_type?.replace(/_/g, ' ')} />
                <InfoRow label="Threat Score" value={`${d.threat_score}/100`} mono />
                <InfoRow label="Login Attempts" value={d.login_attempts} mono />
                <InfoRow label="Commands Run" value={d.commands_run} mono />
                <InfoRow label="Malware DLs" value={d.malware_downloads} mono />
                <InfoRow
                  label="Started"
                  value={d.started_at ? new Date(d.started_at).toLocaleString() : '—'}
                  mono
                />
                <InfoRow
                  label="Ended"
                  value={d.ended_at ? new Date(d.ended_at).toLocaleString() : 'Active'}
                  mono
                />
              </div>

              {/* Credentials */}
              {d.credentials?.length > 0 && (
                <div className={styles.section}>
                  <div className={styles.sectionTitle}>🔑 Credential Attempts ({d.credentials.length})</div>
                  <div className={styles.credList}>
                    {d.credentials.slice(0, 20).map((c, i) => (
                      <div key={i} className={styles.credRow}>
                        <span className={styles.credUser}>{c.username}</span>
                        <span className={styles.credSep}>:</span>
                        <span className={styles.credPass}>{c.password}</span>
                        {c.success && <span className={styles.credSuccess}>✓ SUCCESS</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Commands */}
              {d.commands?.length > 0 && (
                <div className={styles.section}>
                  <div className={styles.sectionTitle}>💻 Commands ({d.commands.length})</div>
                  <div className={styles.cmdList}>
                    {d.commands.slice(0, 15).map((c, i) => (
                      <div key={i} className={`${styles.cmdRow} ${c.is_suspicious ? styles.cmdSusp : ''}`}>
                        <span className={styles.cmdPrompt}>$</span>
                        <span className={styles.cmdText}>{c.command}</span>
                        {c.is_suspicious && <span className={styles.suspLabel}>⚠️</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value, mono }) {
  return (
    <div className={styles.infoRow}>
      <span className={styles.infoLabel}>{label}</span>
      <span className={`${styles.infoValue} ${mono ? 'mono' : ''}`}>{value ?? '—'}</span>
    </div>
  )
}
