import { useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'
export default function NavBar({ active = 'scanner', onTabChange = () => {} }) {
  const [wsConnected, setWsConnected] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const socketRef = useRef(null)

  useEffect(() => {
    // Connect to Socket.IO namespace '/notifications'
    const socket = io('http://localhost:5000/notifications', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })
    socketRef.current = socket

    socket.on('connect', () => setWsConnected(true))
    socket.on('disconnect', () => setWsConnected(false))

    // Listen event: scan_result
    socket.on('scan_result', (payload) => {
      // payload: { job_id, message }
      setNotifications(prev => [{
        job_id: payload?.job_id,
        message: payload?.message || 'Scan result received',
        ts: new Date().toISOString()
      }, ...prev].slice(0, 50))
    })

    return () => {
      try { socket.disconnect() } catch (e) {}
    }
  }, [])

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

          {/* Notification bell */}
          <div className="relative ml-2">
            <button
              aria-label="Notifications"
              className="px-3 py-2 rounded-md text-sm inline-flex items-center gap-2 text-slate-300 hover:text-white hover:bg-slate-800/60"
              onClick={() => setShowDropdown(s => !s)}
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5">
                <path d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2z" fill="currentColor" />
                <path d="M18 16v-5a6 6 0 10-12 0v5l-2 2h16l-2-2z" fill="currentColor" />
              </svg>
              {/* Badge */}
              {notifications.length > 0 && (
                <span className="ml-1 inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-full bg-red-600 text-white text-xs font-bold">
                  {Math.min(notifications.length, 99)}
                </span>
              )}
              {/* Connection indicator */}
              <span className={`ml-2 w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-slate-500'}`}></span>
            </button>

            {/* Dropdown */}
            {showDropdown && (
              <div className="absolute right-0 mt-2 w-80 max-h-96 overflow-auto rounded-md border border-slate-700 bg-slate-900 shadow-lg">
                <div className="px-3 py-2 border-b border-slate-800 text-slate-200 font-semibold flex items-center justify-between">
                  <span>Notifications</span>
                  <button className="text-xs text-slate-400 hover:text-slate-200" onClick={() => setNotifications([])}>Clear</button>
                </div>
                {notifications.length === 0 ? (
                  <div className="px-3 py-4 text-slate-400">No notifications</div>
                ) : (
                  <ul className="divide-y divide-slate-800">
                    {notifications.map((n, idx) => (
                      <li key={idx} className="px-3 py-2 text-sm text-slate-200">
                        <div className="font-mono text-xs text-slate-400">Job: {n.job_id || '-'} • {new Date(n.ts).toLocaleTimeString()}</div>
                        <div className="mt-1">{n.message}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  )
}