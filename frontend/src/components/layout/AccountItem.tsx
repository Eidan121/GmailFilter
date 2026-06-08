import { DotIndicator } from '../shared/DotIndicator'
import type { Account } from '../../types'
import './AccountItem.css'

interface AccountItemProps {
  account: Account
  isActive: boolean
  onClick: () => void
}

export function AccountItem({ account, isActive, onClick }: AccountItemProps) {
  const dotColor = account.is_active ? 'active' : 'idle'

  return (
    <button
      className={`account-item ${isActive ? 'account-item--active' : ''}`}
      onClick={onClick}
      title={account.email}
    >
      <DotIndicator color={dotColor} />
      <span className="account-item__email">{account.email}</span>
    </button>
  )
}
