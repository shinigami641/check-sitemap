export default function CrawlList({ items = [], loading = false }) {
  // Urutkan data: yang terbaru (created_at paling besar) di atas
  const sortedItems = Array.isArray(items)
    ? [...items].sort((a, b) => {
        const ta = a?.created_at ? new Date(a.created_at).getTime() : 0
        const tb = b?.created_at ? new Date(b.created_at).getTime() : 0
        return tb - ta
      })
    : []
  return (
    <div className="card">
      <div className="p-4 border-b border-slate-700">
        <h3 className="font-semibold">Crawled URLs</h3>
        <p className="text-sm text-slate-400">Daftar URL hasil crawling</p>
      </div>
      {loading && (
        <div className="p-4 text-sm text-slate-300 flex items-center gap-2">
          <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4 animate-spin shrink-0">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.85" />
          </svg>
          <span>Mengambil data crawling…</span>
        </div>
      )}
      {/* Body dengan tinggi konsisten dan scroll, gaya terminal */}
      <div className="border-t border-slate-700 bg-slate-950">
        <div className="h-[360px] overflow-y-auto font-mono text-xs leading-6 p-4">
          {sortedItems.map((row, i) => {
            const ts = row.created_at ? new Date(row.created_at) : null
            const tsStr = ts ? ts.toLocaleString() : '-'
            const lineNo = (i + 1).toString().padStart(3, ' ')
            return (
              <div key={row.id ?? i} className="py-1">
                <span className="text-slate-500">{lineNo}</span>
                <span className="mx-2 text-emerald-500">➜</span>
                <a
                  className="text-emerald-300 hover:text-emerald-200 hover:underline break-words"
                  href={row.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {row.url}
                </a>
                <span className="ml-2 text-slate-600">[{tsStr}]</span>
              </div>
            )
          })}
          {sortedItems.length === 0 && (
            <div className="text-slate-400">Belum ada data crawling untuk job ini.</div>
          )}
        </div>
      </div>
    </div>
  )
}