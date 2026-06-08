import { create } from 'zustand'
import * as suggestionsApi from '../api/suggestions'
import { getScanStatus, triggerScan } from '../api/scan'
import type { SuggestionOut, ScanStatus } from '../types'

interface SuggestionStore {
  suggestions: SuggestionOut[]
  pendingCount: number
  scanStatus: ScanStatus | null
  loading: boolean
  fetchSuggestions: (accountId: number) => Promise<void>
  acceptSuggestion: (id: number) => Promise<void>
  dismissSuggestion: (id: number) => Promise<void>
  setScanStatus: (status: ScanStatus) => void
  fetchScanStatus: () => Promise<void>
  triggerScan: () => Promise<void>
}

export const useSuggestionStore = create<SuggestionStore>((set, get) => ({
  suggestions: [],
  pendingCount: 0,
  scanStatus: null,
  loading: false,

  fetchSuggestions: async (accountId) => {
    set({ loading: true })
    try {
      const suggestions = await suggestionsApi.getSuggestions(accountId)
      const pendingCount = suggestions.filter((s) => s.status === 'pending').length
      set({ suggestions, pendingCount })
    } finally {
      set({ loading: false })
    }
  },

  acceptSuggestion: async (id) => {
    // Optimistic update
    set((state) => ({
      suggestions: state.suggestions.map((s) =>
        s.id === id ? { ...s, status: 'accepted' as const } : s,
      ),
      pendingCount: Math.max(0, state.pendingCount - 1),
    }))
    try {
      await suggestionsApi.acceptSuggestion(id)
    } catch {
      // Revert on error by re-fetching
      const accountId = get().suggestions.find((s) => s.id === id)?.account_id
      if (accountId) await get().fetchSuggestions(accountId)
      throw new Error('Failed to accept suggestion')
    }
  },

  dismissSuggestion: async (id) => {
    // Optimistic update
    set((state) => ({
      suggestions: state.suggestions.map((s) =>
        s.id === id ? { ...s, status: 'dismissed' as const } : s,
      ),
      pendingCount: Math.max(0, state.pendingCount - 1),
    }))
    try {
      await suggestionsApi.dismissSuggestion(id)
    } catch {
      const accountId = get().suggestions.find((s) => s.id === id)?.account_id
      if (accountId) await get().fetchSuggestions(accountId)
      throw new Error('Failed to dismiss suggestion')
    }
  },

  setScanStatus: (status) => set({ scanStatus: status }),

  fetchScanStatus: async () => {
    const scanStatus = await getScanStatus()
    set({ scanStatus, pendingCount: scanStatus.pending_suggestions })
  },

  triggerScan: async () => {
    await triggerScan()
    await get().fetchScanStatus()
  },
}))
