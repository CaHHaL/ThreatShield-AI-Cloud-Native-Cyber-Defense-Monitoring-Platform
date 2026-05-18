import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import styles from './LiveAttackMap.module.css'

const SEV_COLORS = {
  CRITICAL: '#ff3d71',
  HIGH:     '#ffaa00',
  MEDIUM:   '#a855f7',
  LOW:      '#00e096',
}

const SEV_RADIUS = { CRITICAL: 10, HIGH: 8, MEDIUM: 6, LOW: 5 }

// Helper to format popup content
function AttackPopup({ attack }) {
  const color = SEV_COLORS[attack.severity] || '#94a3b8'
  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      fontSize: '12px',
      color: '#e2e8f0',
      background: '#0a1628',
      padding: '10px 14px',
      borderRadius: '10px',
      border: `1px solid rgba(0,212,255,0.2)`,
      minWidth: '180px',
      lineHeight: 1.6,
    }}>
      <div style={{ color: '#00d4ff', fontWeight: 700, fontSize: '13px', marginBottom: 4 }}>
        {attack.attacker_ip}
      </div>
      <div style={{ color: '#94a3b8' }}>
        {attack.country || 'Unknown'}{attack.city ? ` · ${attack.city}` : ''}
      </div>
      <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center' }}>
        <span style={{ color, fontWeight: 600, fontSize: '11px' }}>{attack.severity}</span>
        <span style={{ color: '#475569' }}>·</span>
        <span style={{ color: '#94a3b8', fontSize: '11px' }}>{attack.attack_type?.replace('_', ' ') || 'unknown'}</span>
      </div>
      <div style={{ color: '#475569', fontSize: '11px', marginTop: 4 }}>
        Score: <span style={{ color: '#7dd3fc' }}>{attack.threat_score}</span>
      </div>
    </div>
  )
}

export default function LiveAttackMap({ attacks }) {
  const plotted = attacks.filter(a => a.latitude && a.longitude).slice(0, 300)

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>🌍 Live Attack Map</span>
        <span className={styles.count}>{plotted.length} IPs plotted</span>
      </div>

      <div className={styles.mapWrap}>
        <MapContainer
          center={[20, 10]}
          zoom={2}
          style={{ width: '100%', height: '100%' }}
          zoomControl={true}
          attributionControl={false}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={8}
          />

          {plotted.map((attack) => {
            const color  = SEV_COLORS[attack.severity] || '#94a3b8'
            const radius = SEV_RADIUS[attack.severity] || 5
            return (
              <CircleMarker
                key={attack.session_id || attack.id}
                center={[attack.latitude, attack.longitude]}
                radius={radius}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 0.8,
                  weight: 1.5,
                  opacity: 1,
                }}
              >
                <Popup className={styles.popup}>
                  <AttackPopup attack={attack} />
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>

      {/* Legend */}
      <div className={styles.legend}>
        {Object.entries(SEV_COLORS).map(([sev, color]) => (
          <div key={sev} className={styles.legendItem}>
            <span className={styles.legendDot} style={{ background: color }} />
            <span className={styles.legendLabel}>{sev}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
