import { useDashboardData, useFeed } from '../services/hooks'
import NavBar            from '../components/NavBar'
import StatsCards        from '../components/StatsCards'
import LiveAttackMap     from '../components/LiveAttackMap'
import RealTimeEventFeed from '../components/RealTimeEventFeed'
import TopAttackerIPs    from '../components/TopAttackerIPs'
import ThreatIntelPanel  from '../components/ThreatIntelPanel'
import CommandHistoryPanel from '../components/CommandHistoryPanel'
import AttackTimeline    from '../charts/AttackTimeline'
import AttackCategories  from '../charts/AttackCategories'
import CountryStats      from '../charts/CountryStats'

const S = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
    background: 'var(--bg-base)',
  },
  main: {
    padding: '1.5rem 2rem',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
    maxWidth: '1800px',
    margin: '0 auto',
    width: '100%',
  },
  row2col: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '1.5rem',
    alignItems: 'stretch',
  },
  row3col: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '1.5rem',
  },
  row2colEqual: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '1.5rem',
  },
}

export default function Dashboard() {
  const { stats, attacks, countries, topIPs, timeline, categories, loading } = useDashboardData(15000)
  const { events, connected } = useFeed(200)

  return (
    <div style={S.page}>
      <NavBar connected={connected} />

      <main style={S.main}>

        {/* Row 1: KPI cards */}
        <StatsCards stats={stats} loading={loading} />

        {/* Row 2: Map + Live Feed */}
        <div style={S.row2col}>
          <LiveAttackMap attacks={attacks} />
          <RealTimeEventFeed events={events} connected={connected} />
        </div>

        {/* Row 3: Charts */}
        <div style={S.row3col}>
          <AttackTimeline   data={timeline} />
          <AttackCategories data={categories} />
          <CountryStats     data={countries} />
        </div>

        {/* Row 4: IP table + Threat Intel */}
        <div style={S.row2colEqual}>
          <TopAttackerIPs  data={topIPs} />
          <ThreatIntelPanel attacks={attacks} />
        </div>

        {/* Row 5: Command History */}
        <CommandHistoryPanel attacks={attacks} />

      </main>
    </div>
  )
}
