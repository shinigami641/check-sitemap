export default function ProgressBar({ step = 0, total = 3 }) {
  const percent = Math.min(100, Math.round((step / total) * 100))
  const labels = ['Crawling sitemap…', 'Parsing robots.txt…', 'Analyzing parameters…']
  const label = labels[Math.max(0, Math.min(labels.length - 1, step - 1))] || labels[0]

  return (
    <div className="card p-4">
      <div className="flex items-center gap-3 mb-2">
        <span className="badge bg-slate-700 text-slate-200">Step {step} of {total}</span>
        <span className="text-slate-300 text-sm">{label}</span>
      </div>
      <div className="w-full h-2 bg-slate-700 rounded">
        <div
          className="h-2 rounded bg-brand-500 transition-[width]"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}