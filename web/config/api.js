export const API_CONFIG = {
  baseURL: 'http://localhost:5000',
};

export async function startScan(domain) {
  // Hit endpoint backend untuk memulai scan
  const res = await fetch(`${API_CONFIG.baseURL}/api/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain }),
  });
  const json = await res.json();
  if (!res.ok || json.status !== 1) throw new Error(json.message || 'Failed to start scan');
  return json?.data; // { job_id }
}

export async function getScanStatus(jobId) {
  const res = await fetch(`${API_CONFIG.baseURL}/api/scan/status/${jobId}`);
  const json = await res.json();
  if (!res.ok || json.status !== 1) throw new Error(json.message || 'Failed to get status');
  return json?.data; // { status, progress }
}

export async function getCrawlByJobId(jobId) {
  const res = await fetch(`${API_CONFIG.baseURL}/api/scan/all/crawl/${jobId}`);
  const json = await res.json();
  if (!res.ok || json.status !== 1) throw new Error(json.message || 'Failed to get crawl list');
  return json?.data || [];
}

export async function getAllScans() {
  const res = await fetch(`${API_CONFIG.baseURL}/api/scan/all`);
  const json = await res.json();
  if (!res.ok || json.status !== 1) throw new Error(json.message || 'Failed to get scans');
  return json?.data || [];
}

export async function getVulnByJobId(jobId) {
  const res = await fetch(`${API_CONFIG.baseURL}/api/scan/all/vuln/${jobId}`);
  const json = await res.json();
  if (!res.ok || json.status !== 1) throw new Error(json.message || 'Failed to get vulnerability list');
  return json?.data || [];
}