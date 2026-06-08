import { lazy, Suspense, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { useAccountStore } from '../../store/accountStore'
import { useSuggestionStore } from '../../store/suggestionStore'
import { subscribeToEvents } from '../../api/events'
import { Sidebar } from './Sidebar'
import type { SSEEvent } from '../../types'
import './AppShell.css'

const HeroBackground = lazy(() => import('../three/HeroBackground'))

export function AppShell() {
  const fetchAccounts = useAccountStore((s) => s.fetchAccounts)
  const updateAccountStatus = useAccountStore((s) => s.updateAccountStatus)
  const setScanStatus = useSuggestionStore((s) => s.setScanStatus)
  const fetchScanStatus = useSuggestionStore((s) => s.fetchScanStatus)

  useEffect(() => {
    fetchAccounts()
    fetchScanStatus().catch(() => undefined)
  }, [fetchAccounts, fetchScanStatus])

  useEffect(() => {
    const cleanup = subscribeToEvents((event: SSEEvent) => {
      if (event.type === 'account_status_changed') {
        const payload = event.payload as { id: number; is_active: boolean }
        updateAccountStatus(payload.id, payload.is_active)
      } else if (event.type === 'scan_complete') {
        const payload = event.payload as {
          last_run: string
          next_run: string | null
          pending_suggestions: number
          is_running: boolean
        }
        setScanStatus({
          last_run: payload.last_run,
          next_run: payload.next_run,
          pending_suggestions: payload.pending_suggestions,
          is_running: payload.is_running,
        })
      }
    })
    return cleanup
  }, [updateAccountStatus, setScanStatus])

  return (
    <div className="app-shell">
      <Suspense fallback={null}>
        <HeroBackground />
      </Suspense>
      <Sidebar />
      <main className="app-shell__main">
        <Outlet />
      </main>
    </div>
  )
}
