import styles from './CommandHistoryPanel.module.css'

const RISK_KEYWORDS = [
  'wget', 'curl', 'chmod', 'base64', 'eval', 'exec', 'nc ', 'netcat',
  'nmap', '/tmp/', 'xmrig', 'miner', 'rm -rf', '|bash', '|sh',
  'python', 'perl', 'ruby', '/dev/tcp', 'mkfifo',
]

function highlight(cmd) {
  let result = cmd
  const found = RISK_KEYWORDS.filter(kw => cmd.toLowerCase().includes(kw))
  return { cmd, found, isRisky: found.length > 0 }
}

export default function CommandHistoryPanel({ attacks }) {
  // Gather all commands from sessions that have them
  const sessions = attacks.filter(a => a.commands_run > 0).slice(0, 10)

  if (sessions.length === 0) {
    return (
      <div className={`card ${styles.wrapper}`}>
        <div className={styles.header}>
          <span className={styles.title}>💻 Command History</span>
        </div>
        <div className={styles.empty}>
          No post-exploitation commands captured yet.
          SSH connections that execute commands will appear here.
        </div>
      </div>
    )
  }

  return (
    <div className={`card ${styles.wrapper}`}>
      <div className={styles.header}>
        <span className={styles.title}>💻 Command History</span>
        <span className={styles.sub}>
          {sessions.reduce((s, a) => s + (a.commands_run || 0), 0)} commands from {sessions.length} sessions
        </span>
      </div>

      <div className={styles.sessions}>
        {sessions.map(session => (
          <div key={session.id} className={styles.session}>
            <div className={styles.sessionHeader}>
              <span className={`mono ${styles.sessionIP}`}>{session.attacker_ip}</span>
              <span className={styles.sessionCountry}>{session.country}</span>
              <span className={`badge badge-${session.severity?.toLowerCase()}`}>{session.severity}</span>
              <span className={styles.sessionCmds}>{session.commands_run} cmds</span>
            </div>
            <div className={styles.terminal}>
              <div className={styles.termDots}>
                <span className={styles.dot} style={{ background: '#ff5f57' }} />
                <span className={styles.dot} style={{ background: '#febc2e' }} />
                <span className={styles.dot} style={{ background: '#28c840' }} />
                <span className={styles.termTitle}>bash — {session.attacker_ip}</span>
              </div>
              <div className={styles.termBody}>
                <div className={styles.termLine}>
                  <span className={styles.prompt}>root@honeypot:~#</span>
                  <span className={styles.cmd} style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                    [session {session.session_id?.slice(-8)}]
                  </span>
                </div>
                <div className={styles.termLine}>
                  <span className={styles.prompt}>root@honeypot:~#</span>
                  <span className={styles.cmd} style={{ color: '#7dd3fc' }}>
                    {session.commands_run} commands executed
                  </span>
                </div>
                <div className={styles.termLine}>
                  <span className={styles.prompt}>root@honeypot:~#</span>
                  <span className={styles.cmd} style={{ color: '#fbbf24' }}>
                    {session.malware_downloads > 0
                      ? `⚠️ ${session.malware_downloads} malware download(s) attempted`
                      : 'No malware downloads'}
                  </span>
                </div>
                <div className={styles.termLine}>
                  <span className={styles.prompt}>root@honeypot:~#</span>
                  <span className={styles.cmd}>
                    Click <span style={{ color: '#00d4ff' }}>"Threat Intelligence"</span> panel → select session for full command log
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
