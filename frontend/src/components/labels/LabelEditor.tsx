import { useState } from 'react'
import { Modal } from '../shared/Modal'
import { Button } from '../shared/Button'
import { useFilterStore } from '../../store/filterStore'
import { useAccountStore } from '../../store/accountStore'
import { useToast } from '../shared/Toast'
import type { LabelOut } from '../../types'
import './LabelEditor.css'

// Gmail-compatible label colors
const PRESET_COLORS = [
  { text: '#ffffff', bg: '#e53e3e' },  // red
  { text: '#ffffff', bg: '#dd6b20' },  // orange
  { text: '#ffffff', bg: '#d69e2e' },  // yellow
  { text: '#ffffff', bg: '#38a169' },  // green
  { text: '#ffffff', bg: '#3182ce' },  // blue
  { text: '#ffffff', bg: '#805ad5' },  // purple
  { text: '#ffffff', bg: '#d53f8c' },  // pink
  { text: '#ffffff', bg: '#2d3748' },  // dark
  { text: '#2d3748', bg: '#edf2f7' },  // light
  { text: '#ffffff', bg: '#2c7a7b' },  // teal
]

interface LabelEditorProps {
  open: boolean
  onClose: () => void
  editing?: LabelOut
}

export function LabelEditor({ open, onClose, editing }: LabelEditorProps) {
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const createLabel = useFilterStore((s) => s.createLabel)
  const updateLabel = useFilterStore((s) => s.updateLabel)
  const { showToast } = useToast()

  const [name, setName] = useState(editing?.name ?? '')
  const [selectedColor, setSelectedColor] = useState(
    editing?.color
      ? { text: editing.color.textColor ?? '#ffffff', bg: editing.color.backgroundColor ?? '#7070a0' }
      : null as { text: string; bg: string } | null,
  )
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!activeAccountId || !name.trim()) return
    setLoading(true)
    try {
      const color = selectedColor
        ? { textColor: selectedColor.text, backgroundColor: selectedColor.bg }
        : undefined

      if (editing) {
        await updateLabel(activeAccountId, editing.id, { name: name.trim(), color })
        showToast('Label updated')
      } else {
        await createLabel(activeAccountId, {
          name: name.trim(),
          label_list_visibility: 'labelShow',
          message_list_visibility: 'show',
          color,
        })
        showToast('Label created')
      }
      onClose()
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editing ? 'Edit Label' : 'New Label'}
      width={380}
    >
      <div className="label-editor">
        <label className="label-editor__field">
          <span>Name</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Label name…"
            className="label-editor__input"
            autoFocus
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          />
        </label>

        <div className="label-editor__color-section">
          <span className="label-editor__color-label">Color (optional)</span>
          <div className="label-editor__swatches">
            <button
              className={`label-editor__swatch label-editor__swatch--none ${!selectedColor ? 'label-editor__swatch--selected' : ''}`}
              onClick={() => setSelectedColor(null)}
              title="No color"
            >
              ✕
            </button>
            {PRESET_COLORS.map((c) => (
              <button
                key={c.bg}
                className={`label-editor__swatch ${selectedColor?.bg === c.bg ? 'label-editor__swatch--selected' : ''}`}
                style={{ background: c.bg }}
                onClick={() => setSelectedColor(c)}
                title={c.bg}
              />
            ))}
          </div>
        </div>

        {name && (
          <div className="label-editor__preview">
            <span
              className="label-editor__preview-pill"
              style={
                selectedColor
                  ? { background: selectedColor.bg, color: selectedColor.text }
                  : {}
              }
            >
              {name}
            </span>
          </div>
        )}

        <div className="label-editor__footer">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit} loading={loading} disabled={!name.trim()}>
            {editing ? 'Update' : 'Create'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
