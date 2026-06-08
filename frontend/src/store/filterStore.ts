import { create } from 'zustand'
import * as filtersApi from '../api/filters'
import * as labelsApi from '../api/labels'
import type { FilterOut, FilterCreate, LabelOut, LabelCreate, LabelUpdate } from '../types'

interface FilterStore {
  filters: FilterOut[]
  labels: LabelOut[]
  loading: boolean
  fetchFilters: (accountId: number) => Promise<void>
  fetchLabels: (accountId: number) => Promise<void>
  createFilter: (accountId: number, filter: FilterCreate) => Promise<void>
  deleteFilter: (accountId: number, filterId: string) => Promise<void>
  createLabel: (accountId: number, label: LabelCreate) => Promise<void>
  updateLabel: (accountId: number, labelId: string, update: LabelUpdate) => Promise<void>
  deleteLabel: (accountId: number, labelId: string) => Promise<void>
}

export const useFilterStore = create<FilterStore>((set) => ({
  filters: [],
  labels: [],
  loading: false,

  fetchFilters: async (accountId) => {
    set({ loading: true })
    try {
      const filters = await filtersApi.getFilters(accountId)
      set({ filters })
    } finally {
      set({ loading: false })
    }
  },

  fetchLabels: async (accountId) => {
    set({ loading: true })
    try {
      const labels = await labelsApi.getLabels(accountId)
      set({ labels })
    } finally {
      set({ loading: false })
    }
  },

  createFilter: async (accountId, filter) => {
    const created = await filtersApi.createFilter(accountId, filter)
    set((state) => ({ filters: [...state.filters, created] }))
  },

  deleteFilter: async (accountId, filterId) => {
    await filtersApi.deleteFilter(accountId, filterId)
    set((state) => ({
      filters: state.filters.filter((f) => f.id !== filterId),
    }))
  },

  createLabel: async (accountId, label) => {
    const created = await labelsApi.createLabel(accountId, label)
    set((state) => ({ labels: [...state.labels, created] }))
  },

  updateLabel: async (accountId, labelId, update) => {
    const updated = await labelsApi.updateLabel(accountId, labelId, update)
    set((state) => ({
      labels: state.labels.map((l) => (l.id === labelId ? updated : l)),
    }))
  },

  deleteLabel: async (accountId, labelId) => {
    await labelsApi.deleteLabel(accountId, labelId)
    set((state) => ({
      labels: state.labels.filter((l) => l.id !== labelId),
    }))
  },
}))
