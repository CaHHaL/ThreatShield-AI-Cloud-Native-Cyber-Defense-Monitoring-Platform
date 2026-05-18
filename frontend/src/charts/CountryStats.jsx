import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import styles from './Charts.module.css'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className={styles.tooltip}>
      <div className={styles.ttLabel}>{label}</div>
      <div className={styles.ttValue} style={{ color: '#a855f7' }}>
        {payload[0].value} attacks
      </div>
    </div>
  )
}

export default function CountryStats({ data }) {
  const top = (data || []).slice(0, 10)

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.title}>🌐 Top Countries</span>
        <span className={styles.sub}>{data?.length || 0} countries</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={top} margin={{ top: 8, right: 8, bottom: 0, left: -20 }} barSize={12}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis
            dataKey="country_code"
            tick={{ fill: '#475569', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#475569', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <Bar dataKey="attacks" radius={[4, 4, 0, 0]}>
            {top.map((_, i) => (
              <Cell
                key={`cell-${i}`}
                fill={i === 0 ? '#ff3d71' : i === 1 ? '#ffaa00' : '#a855f7'}
                opacity={1 - i * 0.06}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
