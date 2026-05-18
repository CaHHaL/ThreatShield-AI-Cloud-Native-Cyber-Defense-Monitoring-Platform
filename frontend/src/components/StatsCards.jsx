import styles from './StatsCards.module.css'

const CARDS = [
  {
    key:    'total_attacks',
    label:  'Total Attacks',
    icon:   '⚡',
    color:  'accent',
    format: v => v?.toLocaleString() ?? '—',
    delta:  null,
  },
  {
    key:    'active_honeypots',
    label:  'Active Honeypots',
    icon:   '🍯',
    color:  'green',
    format: v => v ?? '—',
  },
  {
    key:    'critical_threats',
    label:  'Critical Threats',
    icon:   '🚨',
    color:  'danger',
    format: v => v?.toLocaleString() ?? '—',
  },
  {
    key:    'unique_ips',
    label:  'Unique Attackers',
    icon:   '🎭',
    color:  'purple',
    format: v => v?.toLocaleString() ?? '—',
  },
  {
    key:    'countries_detected',
    label:  'Countries',
    icon:   '🌍',
    color:  'accent2',
    format: v => v ?? '—',
  },
  {
    key:    'avg_threat_score',
    label:  'Avg Threat Score',
    icon:   '📊',
    color:  'warning',
    format: v => v != null ? `${v}/100` : '—',
  },
]

export default function StatsCards({ stats, loading }) {
  return (
    <div className={styles.grid}>
      {CARDS.map((card, i) => (
        <div
          key={card.key}
          className={`${styles.card} ${styles[card.color]} animate-fade`}
          style={{ animationDelay: `${i * 0.06}s` }}
        >
          {/* Glow effect */}
          <div className={styles.glow} />

          {/* Icon */}
          <div className={styles.iconWrap}>
            <span className={styles.icon}>{card.icon}</span>
          </div>

          {/* Value */}
          <div className={styles.body}>
            <div className={`${styles.value} ${loading ? 'skeleton' : ''}`}>
              {loading ? '\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0' : card.format(stats?.[card.key])}
            </div>
            <div className={styles.label}>{card.label}</div>
          </div>

          {/* Trend indicator */}
          <div className={styles.trend}>
            <svg width="40" height="24" viewBox="0 0 40 24" fill="none" opacity="0.3">
              <path
                d={i % 2 === 0
                  ? "M0 20 C10 18 20 5 40 4"
                  : "M0 18 C15 20 25 8 40 6"}
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
              />
            </svg>
          </div>
        </div>
      ))}
    </div>
  )
}
