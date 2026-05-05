const API = 'http://localhost:8000';

const totalJobs = document.getElementById('totalJobs');
const queueSize = document.getElementById('queueSize');
const avgTime = document.getElementById('avgTime');
const lastUpdated = document.getElementById('lastUpdated');
const workersBody = document.getElementById('workersBody');
const statusBars = document.getElementById('statusBars');
const liveStatus = document.getElementById('liveStatus');

function fmtTime(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleTimeString();
}

function renderStatusBars(data) {
  const entries = Object.entries(data || {});
  const max = Math.max(1, ...entries.map(([, v]) => v));
  statusBars.innerHTML = entries.map(([name, value]) => {
    const width = Math.max(3, (value / max) * 100);
    return `<div class="bar-row"><span>${name}</span><div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div><strong>${value}</strong></div>`;
  }).join('') || '<p>No data yet.</p>';
}

function renderWorkers(workers) {
  workersBody.innerHTML = (workers || []).map(w => `
    <tr>
      <td>${w.worker_id}</td>
      <td>${w.ip_address}</td>
      <td><span class="badge ${w.status}">${w.status}</span></td>
      <td>${w.current_load}</td>
      <td>${w.max_capacity}</td>
      <td>${fmtTime(w.last_heartbeat)}</td>
    </tr>
  `).join('') || '<tr><td colspan="6">No workers registered</td></tr>';
}

async function refresh() {
  try {
    const [mRes, wRes] = await Promise.all([
      fetch(`${API}/metrics-summary`),
      fetch(`${API}/workers`)
    ]);
    const m = await mRes.json();
    const w = await wRes.json();

    totalJobs.textContent = m.total_jobs ?? 0;
    queueSize.textContent = m.queue_size ?? 0;
    avgTime.textContent = `${(m.avg_processing_time_seconds ?? 0).toFixed(2)}s`;
    lastUpdated.textContent = new Date().toLocaleTimeString();
    renderStatusBars(m.jobs_by_status);
    renderWorkers(w);
    liveStatus.textContent = '● Live';
    liveStatus.style.color = 'var(--good)';
  } catch (err) {
    liveStatus.textContent = '● Disconnected';
    liveStatus.style.color = 'var(--bad)';
    console.error('dashboard refresh failed', err);
  }
}

refresh();
setInterval(refresh, 2000);
