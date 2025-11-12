import { useEffect, useRef, useState } from 'react'
import { getAllScans, getCrawlByJobId, getScanStatus } from '../../config/api'
import CrawlList from '../components/CrawlList'

export default function HistoryPage() {
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState(null) // job object
  const [crawl, setCrawl] = useState([])
  const [status, setStatus] = useState('idle')
  const timerRef = useRef(null)

  useEffect(() => {
    (async () => {
      try {
        const data = await getAllScans()
        setItems(data)
      } catch (e) {
        setItems([])
      }
    })()
  }, [])

  const openModal = async (job) => {
    setSelected(job)
    setCrawl([])
    setStatus('running')
    clearInterval(timerRef.current)
    // initial fetch
    try {
      const list = await getCrawlByJobId(job.job_id)
      setCrawl(list)
    } catch {}
    try {
      const st = await getScanStatus(job.job_id)
      setStatus(st.status)
    } catch {}
    // start polling every 2s until finish
    timerRef.current = setInterval(async () => {
      try {
        const list = await getCrawlByJobId(job.job_id)
        setCrawl(list)
      } catch {}
      try {
        const st = await getScanStatus(job.job_id)
        setStatus(st.status)
        if (st.status === 'finish' || st.status === 'done' || st.status === 'error') {
          clearInterval(timerRef.current)
        }
      } catch {}
    }, 2000)
  }

  const closeModal = () => {
    setSelected(null)
    setCrawl([])
    setStatus('idle')
    clearInterval(timerRef.current)
  }

  // Tutup modal dengan tombol Escape
  useEffect(() => {
    if (!selected) return
    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        closeModal()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [selected])

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <h2 className="text-2xl font-bold mb-4">Scan History</h2>
      <div className="grid gap-3">
        {items.map((it) => (
          <button onClick={() => openModal(it)} key={it.id} className="card p-4 flex items-center justify-between text-left">
            <div>
              <div className="font-semibold">{it.domain}</div>
              <div className="text-xs text-slate-400">Job: {it.job_id} • {it.created_at ? new Date(it.created_at).toLocaleString() : '-'}</div>
            </div>
            <div className="flex items-center gap-6">
              <span className={`badge ${it.status === 'finish' ? 'bg-emerald-700/60 text-emerald-200' : it.status === 'error' ? 'bg-rose-700/60 text-rose-200' : 'bg-amber-700/60 text-amber-200'}`}>{it.status}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Modal */}
      {selected && (
        <div className="fixed inset-0 z-20 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4" onClick={closeModal}>
          <div className="w-full max-w-3xl card max-h-[85vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <div>
                <div className="font-semibold">Detail Crawl • {selected.domain}</div>
                <div className="text-xs text-slate-400">Job: {selected.job_id} • Status: {status}</div>
              </div>
              <button className="btn-muted" onClick={closeModal}>
                <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4">
                  <path d="M6 6l12 12M6 18L18 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
                Tutup
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[70vh]">
              <CrawlList items={crawl} loading={status !== 'finish' && status !== 'done' && status !== 'error'} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}