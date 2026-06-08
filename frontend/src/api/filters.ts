import { apiFetch } from './client'
import type { FilterOut, FilterCreate } from '../types'

export async function getFilters(accountId: number): Promise<FilterOut[]> {
  return apiFetch<FilterOut[]>(`/api/accounts/${accountId}/filters`)
}

export async function createFilter(accountId: number, filter: FilterCreate): Promise<FilterOut> {
  return apiFetch<FilterOut>(`/api/accounts/${accountId}/filters`, {
    method: 'POST',
    body: JSON.stringify(filter),
  })
}

export async function deleteFilter(accountId: number, filterId: string): Promise<void> {
  return apiFetch<void>(`/api/accounts/${accountId}/filters/${filterId}`, {
    method: 'DELETE',
  })
}

export async function syncFilters(accountId: number): Promise<void> {
  return apiFetch<void>(`/api/accounts/${accountId}/filters/sync`, {
    method: 'POST',
  })
}
