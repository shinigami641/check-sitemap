export default function StatCards({ total = 0, vulnerable = 0, safe = 0 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
      <div className="card p-4">
        <div className="text-sm text-slate-400">Total URLs</div>
        <div className="mt-1 text-2xl font-semibold">{total}</div>
      </div>
      <div className="card p-4">
        <div className="text-sm text-slate-400">Vulnerable</div>
        <div className="mt-1 text-2xl font-semibold text-rose-400">{vulnerable}</div>
      </div>
      <div className="card p-4">
        <div className="text-sm text-slate-400">Safe</div>
        <div className="mt-1 text-2xl font-semibold text-emerald-400">{safe}</div>
      </div>
    </div>
  )
}