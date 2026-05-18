import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import styles from './Charts.module.css'

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { name, value, color } = payload[0].payload
  return (
    <div className={styles.tooltip}>
      <div className={styles.ttLabel} style={{ color }}>{name?.replace(/_/g, ' ')}</div>
      <div className={styles.ttValue}>{value} attacks</div>
    </div>
  )
}

function CustomLegend({ payload }) {
  return (
    <div className={styles.legend}>
      {payload.map(e => (
        <div key={e.value} className={styles.legendItem}>
          <span className={styles.legendDot} style={{ background: e.color }} />
          <span className={styles.legendLabel}>{e.value?.replace(/_/g, ' ')}</span>
        </div>
      ))}
    </div>
  )
}

export default function AttackCategories({ data }) {
  const total = (data || []).reduce((s, d) => s + (d.value || 0), 0)

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.title}>🥧 Attack Types</span>
        <span className={styles.sub}>{total} sessions</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data || []}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
            nameKey="name"
          >
            {(data || []).map((entry, i) => (
              <Cell
                key={`cell-${i}`}
                fill={entry.color}
                opacity={0.85}
                stroke="rgba(0,0,0,0.3)"
                strokeWidth={1}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
