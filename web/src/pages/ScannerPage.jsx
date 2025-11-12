import { useEffect, useRef, useState } from 'react'
import ScannerForm from '../components/ScannerForm'
import ProgressBar from '../components/ProgressBar'
import CrawlList from '../components/CrawlList'
import StatCards from '../components/StatCards'
import { startScan, getScanStatus, getCrawlByJobId } from '../../config/api'

const demoRows = [
  { url: 'https://www.google.com/', status: 'Safe', risk: 'Safe', details: 'Homepage does not contain query parameters for assessment.' },
  { url: 'https://www.google.com/about/', status: 'Safe', risk: 'Safe', details: 'About page does not use dynamic query parameters.' },
]

export default function ScannerPage() {
  const [progressStep, setProgressStep] = useState(0)
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState('idle')
  const [rows, setRows] = useState([])
  const [stats, setStats] = useState({ total: 0, vulnerable: 0, safe: 0 })
  const timerRef = useRef(null)

  // Polling helper
  const startPolling = (jid) => {
    clearInterval(timerRef.current)
    timerRef.current = setInterval(async () => {
      try {
        const st = await getScanStatus(jid)
        setStatus(st.status)
        const step = st.progress < 34 ? 1 : st.progress < 67 ? 2 : 3
        setProgressStep(step)
        // Stop polling when job has finished or errored
        if (st.status === 'finish' || st.status === 'done' || st.status === 'error') {
          clearInterval(timerRef.current)
          setProgressStep(3)
        }
      } catch {}
      try {
        const list = await getCrawlByJobId(jid)
        setRows(list)
        setStats({ total: list.length, vulnerable: 0, safe: list.length })
      } catch {}
    }, 2000)
  }

  useEffect(() => {
    return () => clearInterval(timerRef.current)
  }, [])

  const handleStart = async (domain) => {
    // reset state
    setRows([])
    setStats({ total: 0, vulnerable: 0, safe: 0 })
    setStatus('pending')
    setProgressStep(1)
    // call backend
    try {
      const res = await startScan(domain)
      const jid = res?.job_id
      if (jid) {
        setJobId(jid)
        setStatus('running')
        setProgressStep(1)
        startPolling(jid)
      }
    } catch (e) {
      setStatus('error')
      clearInterval(timerRef.current)
    }
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

      {status !== 'idle' && (
        <div className="mt-4">
          <ProgressBar step={progressStep} total={3} />
        </div>
      )}

      <div className="mt-6">
        <CrawlList items={rows} loading={status !== 'finish' && status !== 'done' && status !== 'error' && status !== 'idle'} />
        {rows.length > 0 && (
          <StatCards total={stats.total} vulnerable={0} safe={stats.safe} />
        )}
      </div>
    </div>
  )
}