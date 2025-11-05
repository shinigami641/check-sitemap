import { useState } from 'react'

export default function ScannerForm({ onStart = () => {} }) {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!domain) return
    setLoading(true)
    try {
      await onStart(domain)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card p-4">
      <label className="block text-sm mb-2">Domain/URL untuk scan</label>
      <div className="flex gap-2">
        <input
          type="text"
          className="input"
          placeholder="contoh: https://www.google.com"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <button className="btn-primary whitespace-nowrap" type="submit" disabled={loading}>
          {loading ? (
            <>
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4 animate-spin shrink-0">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.85" />
              </svg>
              <span>Scanning…</span>
            </>
          ) : (
            <>
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4 shrink-0">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" fill="none" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Start Scan</span>
            </>
          )}
        </button>
      </div>
      <p className="text-xs text-slate-400 mt-2">Disclaimer: Scan ini melakukan crawling dan analisis parameter URL untuk indikasi SQLi dasar.</p>
    </form>
  )
}