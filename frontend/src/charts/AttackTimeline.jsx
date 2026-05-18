import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { format, parseISO } from 'date-fns'
import styles from './Charts.module.css'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className={styles.tooltip}>
      <div className={styles.ttLabel}>{label}</div>
      <div className={styles.ttValue} style={{ color: '#00d4ff' }}>
        {payload[0].value} attacks
      </div>
    </div>
  )
}

export default function AttackTimeline({ data }) {
  const formatted = (data || []).map(d => {
    let time = d.time || ''
    try { time = d.time ? format(parseISO(d.time), 'HH:mm') : '' } catch { }
    return { ...d, time }
  })

  const total = (data || []).reduce((s, d) => s + (d.attacks || 0), 0)

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.title}>📈 Attack Timeline (24h)</span>
        <span className={styles.sub}>{total.toLocaleString()} total</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={formatted} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
          <defs>
            <linearGradient id="timelineGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#475569', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#475569', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="attacks"
            stroke="#00d4ff"
            strokeWidth={2}
            fill="url(#timelineGrad)"
            dot={false}
            activeDot={{ r: 4, fill: '#00d4ff', strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
