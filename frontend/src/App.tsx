import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import { ToastProvider } from './components/shared/Toast'
import { AppShell } from './components/layout/AppShell'
import { Dashboard } from './pages/Dashboard'
import { FilterManager } from './pages/FilterManager'
import { Suggestions } from './pages/Suggestions'
import { AddAccount } from './pages/AddAccount'
import { NotFound } from './pages/NotFound'

export default function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/filters" element={<FilterManager />} />
            <Route path="/suggestions" element={<Suggestions />} />
            <Route path="/accounts/add" element={<AddAccount />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  )
}
