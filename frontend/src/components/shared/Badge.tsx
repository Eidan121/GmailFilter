import React from 'react'
import './Badge.css'

interface BadgeProps {
  children: React.ReactNode
  color?: 'red' | 'green' | 'amber' | 'muted'
  className?: string
}

export function Badge({ children, color = 'muted', className = '' }: BadgeProps) {
  return (
    <span className={`badge badge--${color} ${className}`}>
      {children}
    </span>
  )
}
