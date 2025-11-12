import { useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'
import ScannerForm from '../components/ScannerForm'
import ProgressBar from '../components/ProgressBar'
import CrawlList from '../components/CrawlList'
import StatCards from '../components/StatCards'
import VulnerabilityList from '../components/VulnerabilityList'
import { startScan, getScanStatus, getCrawlByJobId, getVulnByJobId } from '../../config/api'

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
  const [vulns, setVulns] = useState([])
  const timerRef = useRef(null)
  const socketRef = useRef(null)
  const jobIdRef = useRef(null)

  // Sinkronkan ref dengan state jobId agar handler Socket.IO tidak memakai nilai stale
  useEffect(() => {
    jobIdRef.current = jobId
  }, [jobId])

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
        setStats((prev) => ({ total: list.length, vulnerable: prev.vulnerable || 0, safe: Math.max(0, list.length - (prev.vulnerable || 0)) }))
      } catch {}
      try {
        const vlist = await getVulnByJobId(jid)
        setVulns(vlist)
        setStats((prev) => ({ total: prev.total, vulnerable: vlist.length, safe: Math.max(0, prev.total - vlist.length) }))
      } catch {}
    }, 2000)
  }

  useEffect(() => {
    // Setup Socket.IO untuk menerima notifikasi selesai scan dan trigger refresh data
    const socket = io('http://localhost:5000/notifications', {
      transports: ['websocket', 'polling'],
      path: '/socket.io',
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      withCredentials: false,
    })
    socketRef.current = socket
    socket.on('connect_error', (err) => {
      console.error('[WS] connect_error', err)
    })
    socket.on('scan_result', async (payload) => {
      const jid = payload?.job_id
      if (!jid) return
      // Hanya refresh jika job yang aktif sama
      if (jid !== jobIdRef.current) return
      try {
        const list = await getCrawlByJobId(jid)
        setRows(list)
        setStats(prev => ({ total: list.length, vulnerable: prev.vulnerable || 0, safe: Math.max(0, list.length - (prev.vulnerable || 0)) }))
      } catch {}
      try {
        const vlist = await getVulnByJobId(jid)
        setVulns(vlist)
        setStats(prev => ({ total: prev.total, vulnerable: vlist.length, safe: Math.max(0, prev.total - vlist.length) }))
      } catch {}
      // Pastikan status langsung ditandai selesai
      setStatus('done')
      setProgressStep(3)
    })

    return () => {
      clearInterval(timerRef.current)
      try { socket.disconnect() } catch {}
    }
  }, [])

  const handleStart = async (domain) => {
    // reset state
    setRows([])
    setStats({ total: 0, vulnerable: 0, safe: 0 })
    setVulns([])
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

      <div className="mt-6 grid gap-6">
        <CrawlList items={rows} loading={status !== 'finish' && status !== 'done' && status !== 'error' && status !== 'idle'} />
        <VulnerabilityList items={vulns} loading={status !== 'finish' && status !== 'done' && status !== 'error' && status !== 'idle'} />
        {(rows.length > 0 || vulns.length > 0) && (
          <StatCards total={stats.total} vulnerable={stats.vulnerable} safe={stats.safe} />
        )}
      </div>
    </div>
  )
}