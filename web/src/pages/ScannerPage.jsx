import { useState } from 'react'
import ScannerForm from '../components/ScannerForm'
import ProgressBar from '../components/ProgressBar'
import ResultsTable from '../components/ResultsTable'
import StatCards from '../components/StatCards'
import { startScan } from '../../config/api'

const demoRows = [
  { url: 'https://www.google.com/', status: 'Safe', risk: 'Safe', details: 'Homepage does not contain query parameters for assessment.' },
  { url: 'https://www.google.com/about/', status: 'Safe', risk: 'Safe', details: 'About page does not use dynamic query parameters.' },
]

export default function ScannerPage() {
  const [progressStep, setProgressStep] = useState(0)
  const [rows, setRows] = useState([])
  const [stats, setStats] = useState({ total: 0, vulnerable: 0, safe: 0 })

  const handleStart = async (domain) => {
    setRows([])
    setStats({ total: 0, vulnerable: 0, safe: 0 })
    // Simulasi progress 3 step
    setProgressStep(1)
    await new Promise(r => setTimeout(r, 800))
    setProgressStep(2)
    await new Promise(r => setTimeout(r, 800))
    setProgressStep(3)
    await new Promise(r => setTimeout(r, 800))

    // Contoh panggilan API; saat backend siap, gunakan hasil nyata
    try {
      await startScan(domain)
    } catch {}
    const data = demoRows
    setRows(data)
    setStats({ total: data.length, vulnerable: 0, safe: data.length })
    setProgressStep(0)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <div className="text-center mb-6">
        <div className="inline-grid place-items-center h-12 w-12 rounded-xl bg-brand-500 text-white mb-2">
          {/* Shield icon */}
          <svg aria-hidden="true" viewBox="0 0 24 24" className="h-7 w-7">
            <path d="M12 3l7 4v5c0 4-3 7-7 9-4-2-7-5-7-9V7l7-4z" fill="currentColor"></path>
          </svg>
        </div>
        <h2 className="text-3xl font-bold">Vulnerability Scanner</h2>
        <p className="text-slate-400 mt-1">Scan website untuk menemukan URL dari sitemap dan cek potensi SQL injection vulnerability</p>
      </div>

      <ScannerForm onStart={handleStart} />

      {progressStep > 0 && (
        <div className="mt-4">
          <ProgressBar step={progressStep} total={3} />
        </div>
      )}

      {rows.length > 0 && (
        <div className="mt-6">
          <ResultsTable rows={rows} />
          <StatCards total={stats.total} vulnerable={stats.vulnerable} safe={stats.safe} />
        </div>
      )}
    </div>
  )
}