import { create } from 'zustand'
import { getAccounts } from '../api/accounts'
import type { Account } from '../types'

interface AccountStore {
  accounts: Account[]
  activeAccountId: number | null
  loading: boolean
  setActiveAccount: (id: number | null) => void
  fetchAccounts: () => Promise<void>
  updateAccountStatus: (id: number, is_active: boolean) => void
}

export const useAccountStore = create<AccountStore>((set, get) => ({
  accounts: [],
  activeAccountId: null,
  loading: false,

  setActiveAccount: (id) => set({ activeAccountId: id }),

  fetchAccounts: async () => {
    set({ loading: true })
    try {
      const accounts = await getAccounts()
      const { activeAccountId } = get()
      // Auto-select first account if none selected
      const newActiveId =
        activeAccountId && accounts.find((a) => a.id === activeAccountId)
          ? activeAccountId
          : accounts[0]?.id ?? null
      set({ accounts, activeAccountId: newActiveId })
    } finally {
      set({ loading: false })
    }
  },

  updateAccountStatus: (id, is_active) =>
    set((state) => ({
      accounts: state.accounts.map((a) =>
        a.id === id ? { ...a, is_active } : a,
      ),
    })),
}))
