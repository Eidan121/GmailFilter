import { apiFetch } from './client'
import type { Account, AccountStatus } from '../types'

export async function getAccounts(): Promise<Account[]> {
  return apiFetch<Account[]>('/api/accounts')
}

export async function connectAccount(): Promise<{ auth_url: string; state: string }> {
  return apiFetch<{ auth_url: string; state: string }>('/api/accounts/connect', {
    method: 'POST',
  })
}

export async function deleteAccount(id: number): Promise<void> {
  return apiFetch<void>(`/api/accounts/${id}`, { method: 'DELETE' })
}

export async function getAccountStatus(id: number): Promise<AccountStatus> {
  return apiFetch<AccountStatus>(`/api/accounts/${id}/status`)
}
