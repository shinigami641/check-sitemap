export const API_CONFIG = {
  baseURL: 'http://localhost:5000',
};

export async function startScan(domain) {
  // Placeholder: sesuaikan endpoint saat backend siap
  const res = await fetch(`${API_CONFIG.baseURL}/api/data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain }),
  });
  return res.json();
}

export async function fetchHistory() {
  // Placeholder history data
  return [
    {
      id: 'scan-1',
      name: 'google.com',
      totalUrls: 15,
      vulnerable: 0,
      safe: 15,
      time: new Date().toLocaleString(),
    },
  ];
}