import { useEffect, useState } from 'react'
import { fetchHistory } from '../../config/api'

export default function HistoryPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    (async () => {
      const data = await fetchHistory()
      setItems(data)
    })()
  }, [])

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <h2 className="text-2xl font-bold mb-4">Scan History</h2>
      <div className="grid gap-3">
        {items.map((it) => (
          <div key={it.id} className="card p-4 flex items-center justify-between">
            <div>
              <div className="font-semibold">{it.name}</div>
              <div className="text-xs text-slate-400">{it.time}</div>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-sm text-slate-300">Total URLs <span className="font-semibold">{it.totalUrls}</span></div>
              <div className="text-sm text-emerald-400">Safe <span className="font-semibold">{it.safe}</span></div>
              <div className="text-sm text-rose-400">Vulnerable <span className="font-semibold">{it.vulnerable}</span></div>
              <span className="badge bg-emerald-700/60 text-emerald-200">completed</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}