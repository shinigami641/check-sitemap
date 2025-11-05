import NavBar from './components/NavBar'
import ScannerPage from './pages/ScannerPage'
import HistoryPage from './pages/HistoryPage'
import { useState } from 'react'

export default function App() {
  const [tab, setTab] = useState('scanner')
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <NavBar active={tab} onTabChange={setTab} />
      {tab === 'scanner' ? <ScannerPage /> : <HistoryPage />}
    </div>
  )
}
