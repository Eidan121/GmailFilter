import { useState } from 'react'
import { FilterRow } from './FilterRow'
import { FilterEditor } from './FilterEditor'
import { Button } from '../shared/Button'
import { Spinner } from '../shared/Spinner'
import { useFilterStore } from '../../store/filterStore'
import './FilterList.css'

export function FilterList() {
  const filters = useFilterStore((s) => s.filters)
  const loading = useFilterStore((s) => s.loading)
  const [creating, setCreating] = useState(false)

  if (loading) {
    return (
      <div className="filter-list__loading">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="filter-list">
      <div className="filter-list__header">
        <h2 className="filter-list__title">Filters</h2>
        <Button variant="primary" size="sm" onClick={() => setCreating(true)}>
          + New Filter
        </Button>
      </div>

      {filters.length === 0 ? (
        <div className="filter-list__empty">
          <p>No filters yet. Create one to get started.</p>
        </div>
      ) : (
        <table className="filter-list__table">
          <thead>
            <tr>
              <th>Criteria</th>
              <th>Action</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filters.map((filter) => (
              <FilterRow key={filter.id} filter={filter} />
            ))}
          </tbody>
        </table>
      )}

      <FilterEditor open={creating} onClose={() => setCreating(false)} />
    </div>
  )
}
