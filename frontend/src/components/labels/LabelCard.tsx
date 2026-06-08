import { useState } from 'react'
import { LabelEditor } from './LabelEditor'
import { Button } from '../shared/Button'
import { useFilterStore } from '../../store/filterStore'
import { useAccountStore } from '../../store/accountStore'
import { useToast } from '../shared/Toast'
import type { LabelOut } from '../../types'
import './LabelCard.css'

interface LabelCardProps {
  label: LabelOut
  onEdit?: (label: LabelOut) => void
}

export function LabelCard({ label }: LabelCardProps) {
  const [editing, setEditing] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const deleteLabel = useFilterStore((s) => s.deleteLabel)
  const { showToast } = useToast()

  const bgColor = label.color?.backgroundColor
  const isSystemLabel = label.type === 'system'

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (isSystemLabel) return
    if (!confirming) {
      setConfirming(true)
      setTimeout(() => setConfirming(false), 3000)
      return
    }
    if (!activeAccountId) return
    setDeleting(true)
    try {
      await deleteLabel(activeAccountId, label.id)
      showToast('Label deleted')
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setDeleting(false)
      setConfirming(false)
    }
  }

  return (
    <>
      <div
        className={`label-card ${isSystemLabel ? 'label-card--system' : ''}`}
        onClick={() => !isSystemLabel && setEditing(true)}
        role={isSystemLabel ? undefined : 'button'}
        tabIndex={isSystemLabel ? undefined : 0}
        onKeyDown={(e) => e.key === 'Enter' && !isSystemLabel && setEditing(true)}
      >
        <div className="label-card__header">
          <div
            className="label-card__color"
            style={{ background: bgColor ?? 'var(--border)' }}
          />
          <span className="label-card__name">{label.name}</span>
          {!isSystemLabel && (
            <Button
              variant="danger"
              size="sm"
              className={`label-card__delete ${confirming ? 'label-card__delete--confirm' : ''}`}
              onClick={handleDelete}
              loading={deleting}
            >
              {confirming ? 'Sure?' : '✕'}
            </Button>
          )}
        </div>

        <div className="label-card__stats">
          <span className="label-card__count">{label.messages_total.toLocaleString()}</span>
          <span className="label-card__count-label"> total</span>
          {label.messages_unread > 0 && (
            <>
              <span className="label-card__sep"> · </span>
              <span className="label-card__unread">{label.messages_unread.toLocaleString()} unread</span>
            </>
          )}
        </div>

        {isSystemLabel && (
          <span className="label-card__system-badge">system</span>
        )}
      </div>

      {!isSystemLabel && (
        <LabelEditor
          open={editing}
          onClose={() => setEditing(false)}
          editing={label}
        />
      )}
    </>
  )
}
