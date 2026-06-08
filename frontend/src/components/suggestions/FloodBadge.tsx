import './FloodBadge.css'

interface FloodBadgeProps {
  count: number
  senderEmail: string
}

export function FloodBadge({ count, senderEmail }: FloodBadgeProps) {
  return (
    <span className="flood-badge">
      {count} unfiltered from {senderEmail}
    </span>
  )
}
