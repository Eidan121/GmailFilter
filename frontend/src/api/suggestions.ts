import { apiFetch } from './client'
import type { SuggestionOut } from '../types'

export async function getSuggestions(accountId: number): Promise<SuggestionOut[]> {
  return apiFetch<SuggestionOut[]>(`/api/suggestions?account_id=${accountId}`)
}

export async function acceptSuggestion(id: number): Promise<SuggestionOut> {
  return apiFetch<SuggestionOut>(`/api/suggestions/${id}/accept`, { method: 'POST' })
}

export async function dismissSuggestion(id: number): Promise<SuggestionOut> {
  return apiFetch<SuggestionOut>(`/api/suggestions/${id}/dismiss`, { method: 'POST' })
}
