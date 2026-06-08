import { useState } from 'react'
import { FilterBadge } from './FilterBadge'
import { FilterEditor } from './FilterEditor'
import { Button } from '../shared/Button'
import { useFilterStore } from '../../store/filterStore'
import { useAccountStore } from '../../store/accountStore'
import { useToast } from '../shared/Toast'
import type { FilterOut } from '../../types'
import './FilterRow.css'

interface FilterRowProps {
  filter: FilterOut
}

export function FilterRow({ filter }: FilterRowProps) {
  const [editing, setEditing] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const deleteFilter = useFilterStore((s) => s.deleteFilter)
  const labels = useFilterStore((s) => s.labels)
  const { showToast } = useToast()

  const criteriaBadges = Object.entries(filter.criteria)
    .filter(([, v]) => v !== undefined && v !== '')
    .slice(0, 4) as [string, string][]

  const actionSummary: string[] = []
  if (filter.action.archive) actionSummary.push('Archive')
  if (filter.action.addLabelIds?.length) {
    const names = filter.action.addLabelIds.map(
      (id) => labels.find((l) => l.id === id)?.name ?? id,
    )
    actionSummary.push(`Label: ${names.join(', ')}`)
  }
  if (filter.action.markRead) actionSummary.push('Mark read')

  const handleDelete = async () => {
    if (!activeAccountId) return
    if (!confirming) {
      setConfirming(true)
      setTimeout(() => setConfirming(false), 3000)
      return
    }
    setDeleting(true)
    try {
      await deleteFilter(activeAccountId, filter.id)
      showToast('Filter deleted')
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setDeleting(false)
      setConfirming(false)
    }
  }

  return (
    <>
      <tr className="filter-row">
        <td className="filter-row__criteria">
          <div className="filter-row__badges">
            {criteriaBadges.map(([key, value]) => (
              <FilterBadge key={key} label={key} value={String(value)} />
            ))}
            {criteriaBadges.length === 0 && (
              <span className="filter-row__empty">No criteria</span>
            )}
          </div>
        </td>
        <td className="filter-row__action">
          {actionSummary.join(' · ') || <span className="filter-row__empty">No action</span>}
        </td>
        <td className="filter-row__actions">
          <Button variant="ghost" size="sm" onClick={() => setEditing(true)}>
            Edit
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={handleDelete}
            loading={deleting}
          >
            {confirming ? 'Sure?' : 'Delete'}
          </Button>
        </td>
      </tr>

      <FilterEditor
        open={editing}
        onClose={() => setEditing(false)}
        editing={filter}
      />
    </>
  )
}
