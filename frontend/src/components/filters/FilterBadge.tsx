import './FilterBadge.css'

interface FilterBadgeProps {
  label: string
  value: string
}

export function FilterBadge({ label, value }: FilterBadgeProps) {
  return (
    <span className="filter-badge">
      <span className="filter-badge__key">{label}:</span>
      <span className="filter-badge__value">{value}</span>
    </span>
  )
}
