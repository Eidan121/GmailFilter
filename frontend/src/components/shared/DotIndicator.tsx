import './DotIndicator.css'

interface DotIndicatorProps {
  color: 'active' | 'idle' | 'error'
  pulse?: boolean
}

export function DotIndicator({ color, pulse = false }: DotIndicatorProps) {
  return (
    <span
      className={`dot dot--${color} ${pulse ? 'dot--pulse' : ''}`}
      aria-hidden="true"
    />
  )
}
