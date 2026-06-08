import { useEffect } from 'react'
import { SuggestionPanel } from '../components/suggestions/SuggestionPanel'
import { useSuggestionStore } from '../store/suggestionStore'
import { useAccountStore } from '../store/accountStore'
import './Suggestions.css'

export function Suggestions() {
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const fetchSuggestions = useSuggestionStore((s) => s.fetchSuggestions)
  const fetchScanStatus = useSuggestionStore((s) => s.fetchScanStatus)

  useEffect(() => {
    fetchScanStatus().catch(() => undefined)
    if (activeAccountId) {
      fetchSuggestions(activeAccountId)
    }
  }, [activeAccountId, fetchSuggestions, fetchScanStatus])

  return (
    <div className="suggestions-page">
      <SuggestionPanel />
    </div>
  )
}
