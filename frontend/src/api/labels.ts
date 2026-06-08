import { apiFetch } from './client'
import type { LabelOut, LabelCreate, LabelUpdate } from '../types'

export async function getLabels(accountId: number): Promise<LabelOut[]> {
  return apiFetch<LabelOut[]>(`/api/accounts/${accountId}/labels`)
}

export async function createLabel(accountId: number, label: LabelCreate): Promise<LabelOut> {
  return apiFetch<LabelOut>(`/api/accounts/${accountId}/labels`, {
    method: 'POST',
    body: JSON.stringify(label),
  })
}

export async function updateLabel(
  accountId: number,
  labelId: string,
  update: LabelUpdate,
): Promise<LabelOut> {
  return apiFetch<LabelOut>(`/api/accounts/${accountId}/labels/${labelId}`, {
    method: 'PATCH',
    body: JSON.stringify(update),
  })
}

export async function deleteLabel(accountId: number, labelId: string): Promise<void> {
  return apiFetch<void>(`/api/accounts/${accountId}/labels/${labelId}`, {
    method: 'DELETE',
  })
}
