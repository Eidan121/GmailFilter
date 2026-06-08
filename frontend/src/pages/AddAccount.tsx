import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { connectAccount } from '../api/accounts'
import { useAccountStore } from '../store/accountStore'
import { Button } from '../components/shared/Button'
import './AddAccount.css'

export function AddAccount() {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<'idle' | 'waiting' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const fetchAccounts = useAccountStore((s) => s.fetchAccounts)
  const accounts = useAccountStore((s) => s.accounts)
  const navigate = useNavigate()
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const prevCountRef = useRef(accounts.length)

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  const handleConnect = async () => {
    setLoading(true)
    setErrorMsg(null)
    try {
      const { auth_url } = await connectAccount()
      const popup = window.open(auth_url, 'gmail-oauth', 'width=520,height=640')
      if (!popup) {
        setErrorMsg('Popup blocked. Please allow popups for this site.')
        setLoading(false)
        return
      }

      setStatus('waiting')
      prevCountRef.current = accounts.length

      // Poll every 2s for new account
      pollRef.current = setInterval(async () => {
        if (popup.closed) {
          clearInterval(pollRef.current!)
          await fetchAccounts()
          navigate('/')
          return
        }
        await fetchAccounts()
        const current = useAccountStore.getState().accounts
        if (current.length > prevCountRef.current) {
          clearInterval(pollRef.current!)
          popup.close()
          navigate('/')
        }
      }, 2000)
    } catch (err) {
      setErrorMsg((err as Error).message)
      setStatus('error')
      setLoading(false)
    }
  }

  return (
    <div className="add-account">
      <div className="add-account__icon">◈</div>
      <h1 className="add-account__title">Connect Gmail Account</h1>
      <p className="add-account__desc">
        A Google sign-in window will open. Grant access to manage your filters,
        labels, and scan for email patterns. Each sign-in replaces any
        previously stored access for this account — your token is encrypted
        before being stored.
      </p>

      {errorMsg && (
        <div className="add-account__error">{errorMsg}</div>
      )}

      {status === 'waiting' && (
        <div className="add-account__waiting">
          Waiting for authorization…
        </div>
      )}

      <Button
        variant="primary"
        onClick={handleConnect}
        loading={loading}
        disabled={status === 'waiting'}
      >
        {status === 'waiting' ? 'Waiting for sign-in…' : 'Connect with Google'}
      </Button>

      <p className="add-account__scopes">
        Requires: gmail.readonly · gmail.labels · gmail.settings.basic
      </p>
    </div>
  )
}
