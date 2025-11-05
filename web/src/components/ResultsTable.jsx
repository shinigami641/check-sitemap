function RiskBadge({ level }) {
  const color = level === 'Safe' ? 'bg-emerald-700/60 text-emerald-200' : level === 'Warning' ? 'bg-amber-700/60 text-amber-200' : 'bg-rose-700/60 text-rose-200'
  return <span className={`badge ${color}`}>{level}</span>
}

export default function ResultsTable({ rows = [] }) {
  return (
    <div className="card">
      <div className="p-4 border-b border-slate-700">
        <h3 className="font-semibold">Scan Results</h3>
        <p className="text-sm text-slate-400">Daftar URL hasil crawling dan status resiko</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-800">
            <tr className="text-left">
              <th className="px-4 py-3 border-b border-slate-700">URL</th>
              <th className="px-4 py-3 border-b border-slate-700">Status</th>
              <th className="px-4 py-3 border-b border-slate-700">Risk Level</th>
              <th className="px-4 py-3 border-b border-slate-700">Details</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="odd:bg-slate-800/40">
                <td className="px-4 py-3 border-t border-slate-800"><a className="text-brand-400 hover:underline" href={row.url} target="_blank" rel="noreferrer">{row.url}</a></td>
                <td className="px-4 py-3 border-t border-slate-800"><span className="badge bg-slate-700 text-slate-200">{row.status}</span></td>
                <td className="px-4 py-3 border-t border-slate-800"><RiskBadge level={row.risk}/></td>
                <td className="px-4 py-3 border-t border-slate-800 text-slate-300">{row.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}