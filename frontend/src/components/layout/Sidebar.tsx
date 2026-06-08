import { NavLink } from 'react-router-dom'
import { useAccountStore } from '../../store/accountStore'
import { useSuggestionStore } from '../../store/suggestionStore'
import { AccountItem } from './AccountItem'
import './Sidebar.css'

export function Sidebar() {
  const accounts = useAccountStore((s) => s.accounts)
  const activeAccountId = useAccountStore((s) => s.activeAccountId)
  const setActiveAccount = useAccountStore((s) => s.setActiveAccount)
  const pendingCount = useSuggestionStore((s) => s.pendingCount)

  return (
    <aside className="sidebar">
      <div className="sidebar__top">
        <div className="sidebar__logo">
          <span className="sidebar__logo-icon">◈</span>
          GmailFilter
        </div>

        <div className="sidebar__section-label">Accounts</div>
        <div className="sidebar__accounts">
          {accounts.map((account) => (
            <AccountItem
              key={account.id}
              account={account}
              isActive={account.id === activeAccountId}
              onClick={() => setActiveAccount(account.id)}
            />
          ))}
          {accounts.length === 0 && (
            <p className="sidebar__empty">No accounts connected</p>
          )}
        </div>

        <NavLink to="/accounts/add" className="sidebar__add-btn">
          + Add Account
        </NavLink>
      </div>

      <nav className="sidebar__nav">
        <NavLink
          to="/filters"
          className={({ isActive }) =>
            `sidebar__nav-link ${isActive ? 'sidebar__nav-link--active' : ''}`
          }
        >
          <span className="sidebar__nav-icon">⚙</span>
          Filters
        </NavLink>

        <NavLink
          to="/suggestions"
          className={({ isActive }) =>
            `sidebar__nav-link ${isActive ? 'sidebar__nav-link--active' : ''}`
          }
        >
          <span className="sidebar__nav-icon">✦</span>
          Suggestions
          {pendingCount > 0 && (
            <span className="sidebar__badge">{pendingCount}</span>
          )}
        </NavLink>
      </nav>
    </aside>
  )
}
