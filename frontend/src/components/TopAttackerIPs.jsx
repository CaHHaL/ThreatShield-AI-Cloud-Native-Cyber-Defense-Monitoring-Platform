import styles from './TopAttackerIPs.module.css'

const FLAG_URL = (code) =>
  `https://flagcdn.com/16x12/${code?.toLowerCase()}.png`

export default function TopAttackerIPs({ data }) {
  if (!data?.length) {
    return (
      <div className={`card ${styles.wrapper}`}>
        <div className={styles.header}>
          <span className={styles.title}>🔝 Top Attacker IPs</span>
        </div>
        <div className={styles.empty}>No data yet</div>
      </div>
    )
  }

  const max = Math.max(...data.map(d => d.attack_count), 1)

  return (
    <div className={`card ${styles.wrapper}`}>
      <div className={styles.header}>
        <span className={styles.title}>🔝 Top Attacker IPs</span>
        <span className={styles.sub}>{data.length} attackers</span>
      </div>

      <div className={styles.list}>
        {data.map((item, i) => {
          const pct = (item.attack_count / max) * 100
          return (
            <div key={item.ip} className={styles.row}>
              <span className={styles.rank}>#{i + 1}</span>

              <div className={styles.ipBlock}>
                {item.country_code && (
                  <img
                    src={FLAG_URL(item.country_code)}
                    alt={item.country}
                    className={styles.flag}
                    onError={e => e.target.style.display = 'none'}
                  />
                )}
                <span className={`mono ${styles.ip}`}>{item.ip}</span>
                <span className={styles.country}>{item.country}</span>
              </div>

              <div className={styles.barWrap}>
                <div className={styles.bar} style={{ width: `${pct}%` }} />
              </div>

              <span className={`mono ${styles.count}`}>{item.attack_count}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
