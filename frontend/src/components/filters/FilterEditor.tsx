import { useState } from 'react'
import { Modal } from '../shared/Modal'
import { Button } from '../shared/Button'
import { useFilterStore } from '../../store/filterStore'
import { useAccountStore } from '../../store/accountStore'
import { useToast } from '../shared/Toast'
import type { FilterOut, FilterCreate, FilterCriteria, FilterAction } from '../../types'
import './FilterEditor.css'

interface FilterEditorProps {
  open: boolean
  onClose: () => void
  editing?: FilterOut
}

const emptyForm = (): { criteria: FilterCriteria; action: FilterAction } => ({
  criteria: { from: '', to: '', subject: '', query: '' },
  action: { archive: false, addLabelIds: [], removeLabelIds: [] },
})

export function FilterEditor({ open, onClose, editing }: FilterEditorProps) {
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const labels = useFilterStore((s) => s.labels)
  const createFilter = useFilterStore((s) => s.createFilter)
  const deleteFilter = useFilterStore((s) => s.deleteFilter)
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState(() => {
    if (editing) {
      return {
        criteria: { ...editing.criteria },
        action: { ...editing.action, addLabelIds: [...(editing.action.addLabelIds ?? [])] },
      }
    }
    return emptyForm()
  })

  const setCriteria = (key: keyof FilterCriteria, value: string) =>
    setForm((f) => ({ ...f, criteria: { ...f.criteria, [key]: value } }))

  const toggleLabel = (labelId: string) => {
    setForm((f) => {
      const ids = f.action.addLabelIds ?? []
      const updated = ids.includes(labelId)
        ? ids.filter((id) => id !== labelId)
        : [...ids, labelId]
      return { ...f, action: { ...f.action, addLabelIds: updated } }
    })
  }

  const handleSubmit = async () => {
    if (!activeAccountId) return
    setLoading(true)
    try {
      // Strip empty strings from criteria
      const criteria: FilterCriteria = Object.fromEntries(
        Object.entries(form.criteria).filter(([, v]) => v !== '' && v !== undefined),
      ) as FilterCriteria

      const filterData: FilterCreate = { criteria, action: form.action }

      if (editing) {
        await deleteFilter(activeAccountId, editing.id)
      }
      await createFilter(activeAccountId, filterData)
      showToast(editing ? 'Filter updated' : 'Filter created')
      onClose()
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const userLabels = labels.filter((l) => l.type === 'user')
  const selectedLabelIds = form.action.addLabelIds ?? []

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editing ? 'Edit Filter' : 'New Filter'}
      width={520}
    >
      <div className="filter-editor">
        <fieldset className="filter-editor__fieldset">
          <legend>Criteria</legend>
          {(['from', 'to', 'subject', 'query'] as const).map((field) => (
            <label key={field} className="filter-editor__field">
              <span>{field}</span>
              <input
                type="text"
                value={(form.criteria[field] as string) ?? ''}
                onChange={(e) => setCriteria(field, e.target.value)}
                placeholder={`Filter by ${field}…`}
                className="filter-editor__input"
              />
            </label>
          ))}
        </fieldset>

        <fieldset className="filter-editor__fieldset">
          <legend>Actions</legend>
          <label className="filter-editor__check">
            <input
              type="checkbox"
              checked={form.action.archive ?? false}
              onChange={(e) =>
                setForm((f) => ({ ...f, action: { ...f.action, archive: e.target.checked } }))
              }
            />
            Archive (skip inbox)
          </label>

          {userLabels.length > 0 && (
            <div className="filter-editor__labels">
              <span className="filter-editor__sublabel">Apply label:</span>
              <div className="filter-editor__label-grid">
                {userLabels.map((label) => (
                  <label key={label.id} className="filter-editor__label-option">
                    <input
                      type="checkbox"
                      checked={selectedLabelIds.includes(label.id)}
                      onChange={() => toggleLabel(label.id)}
                    />
                    <span
                      className="filter-editor__label-dot"
                      style={{ background: label.color?.backgroundColor ?? '#7070a0' }}
                    />
                    {label.name}
                  </label>
                ))}
              </div>
            </div>
          )}
        </fieldset>

        <div className="filter-editor__footer">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit} loading={loading}>
            {editing ? 'Update' : 'Create'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
