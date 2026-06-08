import { lazy, Suspense, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAccountStore } from '../store/accountStore'
import { useSuggestionStore } from '../store/suggestionStore'
import { useFilterStore } from '../store/filterStore'
import './Dashboard.css'

const HeroBackground = lazy(() => import('../components/three/HeroBackground'))

export function Dashboard() {
  const accounts = useAccountStore((s) => s.accounts)
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const pendingCount = useSuggestionStore((s) => s.pendingCount)
  const scanStatus = useSuggestionStore((s) => s.scanStatus)
  const filters = useFilterStore((s) => s.filters)
  const labels = useFilterStore((s) => s.labels)
  const fetchFilters = useFilterStore((s) => s.fetchFilters)
  const fetchLabels = useFilterStore((s) => s.fetchLabels)

  useEffect(() => {
    if (activeAccountId) {
      fetchFilters(activeAccountId)
      fetchLabels(activeAccountId)
    }
  }, [activeAccountId, fetchFilters, fetchLabels])

  const userLabels = labels.filter((l) => l.type === 'user')

  const statCards = [
    { label: 'Filters', value: filters.length, link: '/filters', accent: false },
    { label: 'Labels', value: userLabels.length, link: '/filters', accent: false },
    { label: 'Suggestions', value: pendingCount, link: '/suggestions', accent: pendingCount > 0 },
  ]

  return (
    <div className="dashboard">
      <Suspense fallback={null}>
        <HeroBackground />
      </Suspense>

      <div className="dashboard__hero">
        <h1 className="dashboard__heading">
          Filter Manager
        </h1>
        <p className="dashboard__subheading">
          {accounts.length
            ? `Managing ${accounts.length} account${accounts.length > 1 ? 's' : ''}`
            : 'Connect a Gmail account to get started'}
        </p>
      </div>

      {activeAccountId && (
        <div className="dashboard__stats">
          {statCards.map((card) => (
            <Link
              key={card.label}
              to={card.link}
              className={`dashboard__stat-card ${card.accent ? 'dashboard__stat-card--accent' : ''}`}
            >
              <span className="dashboard__stat-value">{card.value}</span>
              <span className="dashboard__stat-label">{card.label}</span>
            </Link>
          ))}
        </div>
      )}

      {!activeAccountId && accounts.length === 0 && (
        <div className="dashboard__empty">
          <p className="dashboard__empty-icon">◈</p>
          <p className="dashboard__empty-title">No accounts connected</p>
          <p className="dashboard__empty-desc">
            Add a Gmail account to start managing filters and detecting email floods.
          </p>
          <Link to="/accounts/add" className="dashboard__cta">
            Connect Gmail Account
          </Link>
        </div>
      )}

      {scanStatus && activeAccountId && (
        <div className="dashboard__scan-bar">
          Background scan ·{' '}
          {scanStatus.is_running ? (
            <span className="dashboard__scan-running">Running…</span>
          ) : scanStatus.last_run ? (
            `Last run ${new Date(scanStatus.last_run).toLocaleString()}`
          ) : (
            'Never run yet'
          )}
          {scanStatus.next_run && !scanStatus.is_running && (
            <> · Next: {new Date(scanStatus.next_run).toLocaleString()}</>
          )}
        </div>
      )}
    </div>
  )
}
