import type { SSEEvent } from '../types'

export function subscribeToEvents(
  onEvent: (e: SSEEvent) => void,
): () => void {
  const source = new EventSource('/api/events/stream')

  source.onmessage = (event: MessageEvent) => {
    try {
      const parsed = JSON.parse(event.data as string) as SSEEvent
      onEvent(parsed)
    } catch {
      // ignore malformed events
    }
  }

  source.onerror = () => {
    // SSE will auto-reconnect; no action needed
  }

  return () => {
    source.close()
  }
}
