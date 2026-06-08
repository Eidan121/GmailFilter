import { useEffect } from 'react'
import { FilterList } from '../components/filters/FilterList'
import { LabelList } from '../components/labels/LabelList'
import { useFilterStore } from '../store/filterStore'
import { useAccountStore } from '../store/accountStore'
import './FilterManager.css'

export function FilterManager() {
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const fetchFilters = useFilterStore((s) => s.fetchFilters)
  const fetchLabels = useFilterStore((s) => s.fetchLabels)

  useEffect(() => {
    if (activeAccountId) {
      fetchFilters(activeAccountId)
      fetchLabels(activeAccountId)
    }
  }, [activeAccountId, fetchFilters, fetchLabels])

  if (!activeAccountId) {
    return (
      <div className="filter-manager__empty">
        <p className="filter-manager__empty-title">No account selected</p>
        <p className="filter-manager__empty-desc">
          Connect a Gmail account using the sidebar to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="filter-manager">
      <h1 className="filter-manager__heading">Filter Manager</h1>
      <div className="filter-manager__panels">
        <section className="filter-manager__panel">
          <FilterList />
        </section>
        <section className="filter-manager__panel">
          <LabelList />
        </section>
      </div>
    </div>
  )
}
