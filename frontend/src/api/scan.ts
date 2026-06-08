import { apiFetch } from './client'
import type { ScanStatus } from '../types'

export async function getScanStatus(): Promise<ScanStatus> {
  return apiFetch<ScanStatus>('/api/scan/status')
}

export async function triggerScan(): Promise<void> {
  return apiFetch<void>('/api/scan/trigger', { method: 'POST' })
}
