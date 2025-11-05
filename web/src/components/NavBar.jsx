export default function NavBar({ active = 'scanner', onTabChange = () => {} }) {
  const tabs = [
    { key: 'scanner', label: 'Scanner' },
    { key: 'history', label: 'Scan History' },
  ]
  return (
    <header className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur border-b border-slate-800">
      <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="inline-grid place-items-center h-8 w-8 rounded-lg bg-brand-500 text-white">
            {/* Shield icon */}
            <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5">
              <path d="M12 3l7 4v5c0 4-3 7-7 9-4-2-7-5-7-9V7l7-4z" fill="currentColor"></path>
            </svg>
          </div>
          <span className="font-semibold">Scanner Dashboard</span>
        </div>
        <nav className="flex items-center gap-1">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => onTabChange(t.key)}
              className={`px-3 py-2 rounded-md font-bold text-sm inline-flex items-center gap-2 ${active === t.key ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`}
            >
              {/* Tab icons */}
              {t.key === 'scanner' ? (
                <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4">
                  <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" fill="none" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              ) : (
                <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4">
                  <circle cx="12" cy="12" r="7" stroke="currentColor" strokeWidth="2" fill="none" />
                  <path d="M12 8v4l3 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                </svg>
              )}
              {t.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}