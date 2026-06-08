import { useState } from 'react'
import { Button } from '../shared/Button'
import { FloodBadge } from './FloodBadge'
import { useSuggestionStore } from '../../store/suggestionStore'
import { useToast } from '../shared/Toast'
import type { SuggestionOut } from '../../types'
import './SuggestionCard.css'

interface SuggestionCardProps {
  suggestion: SuggestionOut
}

const ACTION_LABELS: Record<string, string> = {
  label: 'Label only',
  archive: 'Archive only',
  'label+archive': 'Label + Archive',
}

export function SuggestionCard({ suggestion }: SuggestionCardProps) {
  const [rationaleOpen, setRationaleOpen] = useState(false)
  const [accepting, setAccepting] = useState(false)
  const [dismissing, setDismissing] = useState(false)
  const acceptSuggestion = useSuggestionStore((s) => s.acceptSuggestion)
  const dismissSuggestion = useSuggestionStore((s) => s.dismissSuggestion)
  const { showToast } = useToast()

  if (suggestion.status !== 'pending') return null

  const handleAccept = async () => {
    setAccepting(true)
    try {
      await acceptSuggestion(suggestion.id)
      showToast(`Filter created for ${suggestion.sender_domain}`)
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setAccepting(false)
    }
  }

  const handleDismiss = async () => {
    setDismissing(true)
    try {
      await dismissSuggestion(suggestion.id)
    } catch (err) {
      showToast((err as Error).message, 'error')
    } finally {
      setDismissing(false)
    }
  }

  const actionLabel = ACTION_LABELS[suggestion.suggested_action] ?? suggestion.suggested_action

  return (
    <div className="suggestion-card">
      <div className="suggestion-card__top">
        <div className="suggestion-card__sender">
          <span className="suggestion-card__email">{suggestion.sender_email}</span>
          {suggestion.sender_domain !== suggestion.sender_email && (
            <span className="suggestion-card__domain">{suggestion.sender_domain}</span>
          )}
        </div>
        <FloodBadge count={suggestion.email_count} senderEmail={suggestion.sender_email} />
      </div>

      <div className="suggestion-card__action">
        <span className="suggestion-card__action-label">Action:</span>
        <span className="suggestion-card__action-value">
          {suggestion.suggested_label && `${suggestion.suggested_label} · `}{actionLabel}
        </span>
      </div>

      {suggestion.ai_rationale && (
        <div className="suggestion-card__rationale">
          <button
            className="suggestion-card__rationale-toggle"
            onClick={() => setRationaleOpen((o) => !o)}
          >
            {rationaleOpen ? '▾' : '▸'} AI rationale
          </button>
          {rationaleOpen && (
            <p className="suggestion-card__rationale-text">{suggestion.ai_rationale}</p>
          )}
        </div>
      )}

      <div className="suggestion-card__footer">
        <Button variant="ghost" size="sm" onClick={handleDismiss} loading={dismissing}>
          Dismiss
        </Button>
        <Button variant="primary" size="sm" onClick={handleAccept} loading={accepting}>
          Accept
        </Button>
      </div>
    </div>
  )
}
