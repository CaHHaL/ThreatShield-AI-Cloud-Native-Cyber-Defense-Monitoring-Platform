import styles from './NavBar.module.css'

export default function NavBar({ connected, lastUpdated }) {
  const now = lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : new Date().toLocaleTimeString()

  return (
    <nav className={styles.nav}>
      {/* Left — Logo */}
      <div className={styles.left}>
        <div className={styles.logoIcon}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" fill="#00d4ff" />
            <path d="M10 17l-3-3 1.4-1.4 1.6 1.6 4.6-4.6 1.4 1.4-6 6z" fill="#060d1a" />
          </svg>
        </div>
        <div>
          <div className={styles.logoText}>ThreatShield <span className={styles.logoAI}>AI</span></div>
          <div className={styles.logoSub}>Cybersecurity Intelligence Platform</div>
        </div>
      </div>

      {/* Center — Status pills */}
      <div className={styles.center}>
        <div className={styles.pill}>
          <span className={`pulse ${connected ? 'pulse-green' : 'pulse-danger'}`} />
          <span>{connected ? 'Live Feed Active' : 'Reconnecting...'}</span>
        </div>
        <div className={styles.pill}>
          <span className="pulse pulse-accent" />
          <span>2 Honeypots Online</span>
        </div>
      </div>

      {/* Right — Metadata */}
      <div className={styles.right}>
        <div className={styles.meta}>
          <span className={styles.metaLabel}>Last sync</span>
          <span className={styles.metaValue}>{now}</span>
        </div>
        <div className={styles.sep} />
        <a
          href="http://localhost:9090"
          target="_blank"
          rel="noreferrer"
          className={styles.iconLink}
          title="Prometheus"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
          </svg>
        </a>
        <a
          href="http://localhost:3001"
          target="_blank"
          rel="noreferrer"
          className={styles.iconLink}
          title="Grafana"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 3h18v18H3V3zm16 16V5H5v14h14zm-8-2H9V9h2v8zm4 0h-2V7h2v10z" />
          </svg>
        </a>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className={styles.iconLink}
          title="API Docs"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" />
          </svg>
        </a>
      </div>
    </nav>
  )
}
