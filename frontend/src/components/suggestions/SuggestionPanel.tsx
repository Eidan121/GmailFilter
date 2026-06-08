import { SuggestionCard } from './SuggestionCard'
import { Button } from '../shared/Button'
import { Spinner } from '../shared/Spinner'
import { Badge } from '../shared/Badge'
import { useSuggestionStore } from '../../store/suggestionStore'
import { useAccountStore } from '../../store/accountStore'
import { useToast } from '../shared/Toast'
import './SuggestionPanel.css'

export function SuggestionPanel() {
  const suggestions = useSuggestionStore((s) => s.suggestions)
  const loading = useSuggestionStore((s) => s.loading)
  const scanStatus = useSuggestionStore((s) => s.scanStatus)
  const triggerScan = useSuggestionStore((s) => s.triggerScan)
  const pendingCount = useSuggestionStore((s) => s.pendingCount)
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const { showToast } = useToast()

  const pending = suggestions.filter((s) => s.status === 'pending')

  const handleTrigger = async () => {
    try {
      await triggerScan()
      showToast('Scan started')
    } catch (err) {
      showToast((err as Error).message, 'error')
    }
  }

  return (
    <div className="suggestion-panel">
      <div className="suggestion-panel__header">
        <div className="suggestion-panel__title-row">
          <h2 className="suggestion-panel__title">Suggestions</h2>
          {pendingCount > 0 && (
            <Badge color="red">{pendingCount} pending</Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleTrigger}
          loading={scanStatus?.is_running}
        >
          {scanStatus?.is_running ? 'Scanning…' : 'Scan Now'}
        </Button>
      </div>

      {scanStatus && (
        <div className="suggestion-panel__scan-info">
          {scanStatus.last_run
            ? `Last scan: ${new Date(scanStatus.last_run).toLocaleString()}`
            : 'Never scanned'}
          {scanStatus.next_run && ` · Next: ${new Date(scanStatus.next_run).toLocaleString()}`}
        </div>
      )}

      {loading && (
        <div className="suggestion-panel__loading">
          <Spinner />
        </div>
      )}

      {!loading && pending.length === 0 && (
        <div className="suggestion-panel__empty">
          <p className="suggestion-panel__empty-icon">✦</p>
          <p className="suggestion-panel__empty-text">
            {activeAccountId
              ? 'No pending suggestions — inbox looks clean'
              : 'Select an account to see suggestions'}
          </p>
        </div>
      )}

      <div className="suggestion-panel__list">
        {pending.map((s) => (
          <SuggestionCard key={s.id} suggestion={s} />
        ))}
      </div>
    </div>
  )
}
