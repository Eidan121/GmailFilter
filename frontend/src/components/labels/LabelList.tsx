import { useState } from 'react'
import { LabelCard } from './LabelCard'
import { LabelEditor } from './LabelEditor'
import { Button } from '../shared/Button'
import { Spinner } from '../shared/Spinner'
import { useFilterStore } from '../../store/filterStore'
import './LabelList.css'

export function LabelList() {
  const labels = useFilterStore((s) => s.labels)
  const loading = useFilterStore((s) => s.loading)
  const [creating, setCreating] = useState(false)

  const userLabels = labels.filter((l) => l.type === 'user')
  const systemLabels = labels.filter((l) => l.type === 'system')

  if (loading && labels.length === 0) {
    return (
      <div className="label-list__loading">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="label-list">
      <div className="label-list__header">
        <h2 className="label-list__title">Labels</h2>
        <Button variant="primary" size="sm" onClick={() => setCreating(true)}>
          + New Label
        </Button>
      </div>

      {userLabels.length > 0 && (
        <section className="label-list__section">
          <h3 className="label-list__section-title">Your Labels</h3>
          <div className="label-list__grid">
            {userLabels.map((label) => (
              <LabelCard key={label.id} label={label} />
            ))}
          </div>
        </section>
      )}

      {systemLabels.length > 0 && (
        <section className="label-list__section">
          <h3 className="label-list__section-title">System Labels</h3>
          <div className="label-list__grid">
            {systemLabels.map((label) => (
              <LabelCard key={label.id} label={label} />
            ))}
          </div>
        </section>
      )}

      {labels.length === 0 && (
        <div className="label-list__empty">
          <p>No labels found.</p>
        </div>
      )}

      <LabelEditor open={creating} onClose={() => setCreating(false)} />
    </div>
  )
}
