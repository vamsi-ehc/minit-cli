"""HTML source for the minit real-time web dashboard."""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>minit — system monitor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
  <style>
    :root { --hdr: 44px; --sb: 180px; }
    body {
      background: #040b04; color: #c8d8c8;
      font-family: ui-monospace,'Cascadia Code','JetBrains Mono',monospace;
      font-size: 13px;
    }
    .card  { background:#0a150a; border:1px solid #1a3a1a; border-radius:12px; }
    .card2 { background:#0a150a; border:1px solid #1a3a1a; border-radius:8px; }

    /* ── Scrollbar ─────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width:4px; height:4px; }
    ::-webkit-scrollbar-track { background:#040b04; }
    ::-webkit-scrollbar-thumb { background:#22c55e44; border-radius:2px; }

    /* ── Gauges ────────────────────────────────────────────────────────── */
    .gauge-track { fill:none; stroke:#162816; stroke-width:10; stroke-linecap:round; }
    .gauge-fill  { fill:none; stroke-width:10; stroke-linecap:round;
                   transition: stroke-dashoffset .7s cubic-bezier(.4,0,.2,1), stroke .4s; }

    /* ── Sidebar ───────────────────────────────────────────────────────── */
    #sidebar {
      position: fixed; left:0; top: var(--hdr);
      height: calc(100vh - var(--hdr)); width: var(--sb);
      background: #040b04; border-right:1px solid #1a3a1a;
      display: flex; flex-direction: column; z-index:10;
      overflow-y: auto; transition: transform .25s ease;
    }
    #sidebar.sb-hidden { transform: translateX(-100%); }
    @media (min-width:1024px) {
      #sidebar { transform: translateX(0) !important; }
      #main-content { margin-left: var(--sb); }
    }
    .nav-link {
      display:flex; align-items:center; gap:10px;
      padding:9px 16px; font-size:12px; color:#4b5563; cursor:pointer;
      user-select:none; border-left:2px solid transparent;
      transition: all .15s;
    }
    .nav-link:hover  { color:#4ade80; background:#0a150a; }
    .nav-link.active { color:#22c55e; border-left-color:#22c55e; background:#0a150a; }
    .nav-dot { width:6px; height:6px; border-radius:50%; background:currentColor; flex-shrink:0; }
    .nav-section { padding:6px 16px 2px; font-size:10px; color:#1a3a1a;
                   text-transform:uppercase; letter-spacing:.08em; }

    /* ── Animations ────────────────────────────────────────────────────── */
    .pulse { animation: pulse 2.4s ease-in-out infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.2} }
    .bar-fill { transition: width .6s ease, background .4s; }

    /* ── Section collapse ──────────────────────────────────────────────── */
    .sec-header { cursor:pointer; user-select:none; transition:background .15s; }
    .sec-header:hover { background:#0d1a0d; }
    .sec-arrow { transition:transform .25s; display:inline-block; }
    .sec-body  { overflow:hidden; transition:max-height .3s ease; }

    /* ── Disk cards ────────────────────────────────────────────────────── */
    .disk-card { border-bottom:1px solid #1a3a1a; }
    .disk-card:last-child { border-bottom:none; }
    .disk-hdr { cursor:pointer; transition:background .15s; }
    .disk-hdr:hover { background:#0d1a0d; }
    .disk-detail { overflow:hidden; transition:max-height .3s ease; max-height:0; }
    .disk-detail.open { max-height:200px; }

    /* ── Misc ──────────────────────────────────────────────────────────── */
    tr:hover td { background:#0d1a0d; }
    td,th { padding:5px 10px; }
    .tag { display:inline-block; padding:1px 7px; border-radius:4px;
           font-size:10px; border:1px solid #1a3a1a; color:#4ade80; background:#0a150a;
           cursor:pointer; }
    .active-tag { background:#14532d; border-color:#4ade80; color:#86efac; font-weight:600; }
    .chart-wrap { position:relative; height:120px; }
    .kv-label { font-size:10px; color:#4b5563; }
    .kv-value { font-size:12px; color:#c8d8c8; }
  </style>
</head>
<body class="min-h-screen">

<!-- ══ Header ════════════════════════════════════════════════════════════════ -->
<header id="hdr" class="sticky top-0 z-20 flex items-center justify-between
               px-3 md:px-4 border-b border-green-900/40"
        style="height:var(--hdr);background:#040b04ee;backdrop-filter:blur(6px)">
  <div class="flex items-center gap-3">
    <!-- mobile sidebar toggle -->
    <button class="lg:hidden text-green-700 hover:text-green-400 text-xl leading-none mr-1"
            onclick="toggleSidebar()">☰</button>
    <!-- Logo SVG -->
    <svg width="28" height="28" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" fill="none" style="flex-shrink:0;">
      <rect width="256" height="256" rx="40" fill="#0f172a"/>
      <circle cx="128" cy="128" r="80" stroke="#22c55e" stroke-width="10" stroke-linecap="round" stroke-dasharray="420 120"/>
      <path d="M64 140 L96 120 L120 140 L152 100 L192 120" stroke="#22c55e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M120 60 L90 140 H120 L105 196 L170 110 H130 L150 60 Z" fill="#22c55e"/>
    </svg>
    <span class="text-green-400 font-bold text-base tracking-widest">minit</span>
    <span class="text-green-900">/</span>
    <span id="hdr-hostname" class="text-slate-300 text-sm hidden sm:inline">—</span>
  </div>
  <div class="flex items-center gap-4 text-xs text-slate-500">
    <span id="hdr-os" class="hidden md:inline">—</span>
    <span id="hdr-uptime" class="text-green-600 hidden sm:inline">up —</span>
    <span id="hdr-updated" class="text-slate-600 hidden sm:inline">—</span>
    <span id="hdr-clock" class="text-green-400 font-bold tabular-nums">—</span>
    <!-- Website link -->
    <a href="https://minit-cli.vamsi-tech.org/" target="_blank" rel="noopener noreferrer"
       class="hidden md:inline text-green-500 hover:text-green-300 transition-colors">docs ↗</a>
    <!-- Refresh slider -->
    <div class="flex items-center gap-2 border-l border-green-900/50 pl-3">
      <span class="text-slate-600 hidden sm:inline">Refresh</span>
      <input id="refresh-slider" type="range" min="0" max="6" step="1" value="3"
             style="width:72px;accent-color:#22c55e;cursor:pointer"/>
      <span id="refresh-label" class="text-green-400 font-bold tabular-nums w-8 text-right">3s</span>
    </div>
  </div>
</header>

<!-- ══ Sidebar ════════════════════════════════════════════════════════════════ -->
<nav id="sidebar" class="sb-hidden">
  <div class="px-4 py-4 border-b border-green-900/30">
    <div class="text-green-400 font-bold text-xs tracking-widest">NAVIGATION</div>
    <div class="text-slate-600 text-xs mt-0.5" id="sb-hostname">—</div>
  </div>

  <div class="py-2 flex-1">
    <div class="nav-section">Dashboard</div>
    <div class="nav-link active" id="nav-overview" onclick="navTo('overview')">
      <span class="nav-dot"></span>Overview
    </div>

    <div class="nav-section mt-2">Metrics</div>
    <div class="nav-link" id="nav-cpu" onclick="navTo('cpu')">
      <span class="nav-dot"></span>CPU
      <span class="ml-auto text-xs tabular-nums" id="sb-cpu">—</span>
    </div>
    <div class="nav-link" id="nav-mem" onclick="navTo('mem')">
      <span class="nav-dot"></span>Memory
      <span class="ml-auto text-xs tabular-nums" id="sb-mem">—</span>
    </div>
    <div class="nav-link" id="nav-net" onclick="navTo('net')">
      <span class="nav-dot"></span>Network
    </div>
    <div class="nav-link" id="nav-disk" onclick="navTo('disk')">
      <span class="nav-dot"></span>Disk
    </div>

    <div class="nav-section mt-2">System</div>
    <div class="nav-link" id="nav-proc" onclick="navTo('proc')">
      <span class="nav-dot"></span>Processes
    </div>
  </div>

  <!-- mini stats at bottom -->
  <div class="border-t border-green-900/30 px-4 py-3 space-y-1.5 text-xs">
    <div class="flex justify-between">
      <span class="text-slate-600">Disk R</span>
      <span class="text-green-400 tabular-nums" id="sb-disk-r">— MiB/s</span>
    </div>
    <div class="flex justify-between">
      <span class="text-slate-600">Disk W</span>
      <span class="text-green-400 tabular-nums" id="sb-disk-w">— MiB/s</span>
    </div>
    <div class="flex justify-between">
      <span class="text-slate-600">Net ↑</span>
      <span class="text-teal-400 tabular-nums" id="sb-net-tx">— Mbit/s</span>
    </div>
    <div class="flex justify-between">
      <span class="text-slate-600">Net ↓</span>
      <span class="text-green-400 tabular-nums" id="sb-net-rx">— Mbit/s</span>
    </div>
  </div>
</nav>

<!-- ══ Main content ═══════════════════════════════════════════════════════════ -->
<div id="main-content" class="p-3 md:p-4 space-y-3 max-w-screen-2xl mx-auto">

  <!-- Sysinfo bar -->
  <div class="card2 px-4 py-2 flex flex-wrap gap-x-8 gap-y-1 text-xs">
    <span class="text-slate-600">Proc  <span id="si-proc"  class="text-slate-300">—</span></span>
    <span class="text-slate-600">Cores <span id="si-cores" class="text-slate-300">—</span></span>
    <span class="text-slate-600">RAM   <span id="si-ram"   class="text-slate-300">—</span></span>
    <span class="text-slate-600">Arch  <span id="si-arch"  class="text-slate-300">—</span></span>
    <span class="text-slate-600">Boot  <span id="si-boot"  class="text-slate-300">—</span></span>
    <span class="ml-auto text-slate-600">Last&nbsp;reading
      <span id="si-updated" class="text-green-500">—</span></span>
  </div>

  <!-- ══ Overview ═══════════════════════════════════════════════════════════ -->
  <div id="section-overview" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">

    <div class="card p-4 flex flex-col items-center">
      <span class="text-xs text-slate-500 uppercase tracking-widest mb-1">CPU</span>
      <svg viewBox="0 0 120 72" class="w-32">
        <path d="M15,67 A50,50 0 0,1 105,67" class="gauge-track"/>
        <path id="g-cpu" d="M15,67 A50,50 0 0,1 105,67" class="gauge-fill"
              stroke="#22c55e" style="stroke-dasharray:157.08;stroke-dashoffset:157.08"/>
        <text x="60" y="63" text-anchor="middle" fill="#e2e8f0"
              font-size="17" font-weight="600" id="g-cpu-txt">0%</text>
      </svg>
      <span id="g-cpu-freq" class="text-xs text-slate-600 -mt-1">— MHz</span>
    </div>

    <div class="card p-4 flex flex-col items-center">
      <span class="text-xs text-slate-500 uppercase tracking-widest mb-1">RAM</span>
      <svg viewBox="0 0 120 72" class="w-32">
        <path d="M15,67 A50,50 0 0,1 105,67" class="gauge-track"/>
        <path id="g-ram" d="M15,67 A50,50 0 0,1 105,67" class="gauge-fill"
              stroke="#4ade80" style="stroke-dasharray:157.08;stroke-dashoffset:157.08"/>
        <text x="60" y="63" text-anchor="middle" fill="#e2e8f0"
              font-size="17" font-weight="600" id="g-ram-txt">0%</text>
      </svg>
      <span id="g-ram-sub" class="text-xs text-slate-600 -mt-1">— / — GB</span>
    </div>

    <div class="card p-4 flex flex-col items-center">
      <span class="text-xs text-slate-500 uppercase tracking-widest mb-1">Swap</span>
      <svg viewBox="0 0 120 72" class="w-32">
        <path d="M15,67 A50,50 0 0,1 105,67" class="gauge-track"/>
        <path id="g-swap" d="M15,67 A50,50 0 0,1 105,67" class="gauge-fill"
              stroke="#86efac" style="stroke-dasharray:157.08;stroke-dashoffset:157.08"/>
        <text x="60" y="63" text-anchor="middle" fill="#e2e8f0"
              font-size="17" font-weight="600" id="g-swap-txt">0%</text>
      </svg>
      <span id="g-swap-sub" class="text-xs text-slate-600 -mt-1">— / — GB</span>
    </div>

    <div class="card p-4 flex flex-col justify-between">
      <span class="text-xs text-slate-500 uppercase tracking-widest">Disk Read</span>
      <div class="text-3xl font-bold text-green-400 tabular-nums mt-2" id="stat-disk-r">—</div>
      <span class="text-xs text-slate-600">MiB/s</span>
    </div>

    <div class="card p-4 flex flex-col justify-between">
      <span class="text-xs text-slate-500 uppercase tracking-widest">Disk Write</span>
      <div class="text-3xl font-bold text-green-400 tabular-nums mt-2" id="stat-disk-w">—</div>
      <span class="text-xs text-slate-600">MiB/s</span>
    </div>

    <div class="card p-4 flex flex-col justify-between">
      <span class="text-xs text-slate-500 uppercase tracking-widest">Network</span>
      <div class="mt-2 space-y-1.5">
        <div class="flex justify-between items-center">
          <span class="text-slate-600 text-xs">↑ TX</span>
          <span class="text-green-400 font-bold tabular-nums" id="stat-net-tx">—</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-slate-600 text-xs">↓ RX</span>
          <span class="text-green-300 font-bold tabular-nums" id="stat-net-rx">—</span>
        </div>
      </div>
      <span class="text-xs text-slate-600">Mbit/s</span>
    </div>
  </div>

  <!-- ══ CPU ════════════════════════════════════════════════════════════════ -->
  <div id="section-cpu" class="card overflow-hidden">
    <div class="sec-header flex items-center justify-between px-4 py-3 border-b border-green-900/40"
         onclick="toggle('sb-cpu-body','arr-cpu')">
      <div class="flex items-center gap-2">
        <span class="sec-arrow text-green-600 text-xs" id="arr-cpu">▼</span>
        <span class="text-green-400 font-semibold text-sm tracking-wide">CPU</span>
        <span class="tag ml-2" id="cpu-cores-tag">—</span>
      </div>
      <div class="flex flex-wrap gap-4 overflow-hidden" id="cpu-legend"
           style="max-width:60%"></div>
    </div>
    <div class="sec-body" id="sb-cpu-body" style="max-height:600px">
      <div class="px-4 pt-3 pb-1 chart-wrap">
        <canvas id="chart-cpu"></canvas>
      </div>
      <div id="per-core-grid"
           class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2 px-4 py-3"></div>
    </div>
  </div>

  <!-- ══ Memory ═════════════════════════════════════════════════════════════ -->
  <div id="section-mem" class="card overflow-hidden">
    <div class="sec-header flex items-center justify-between px-4 py-3 border-b border-green-900/40"
         onclick="toggle('sb-mem-body','arr-mem')">
      <div class="flex items-center gap-2">
        <span class="sec-arrow text-green-600 text-xs" id="arr-mem">▼</span>
        <span class="text-green-400 font-semibold text-sm tracking-wide">Memory and Swap</span>
      </div>
      <div class="flex gap-6 text-xs text-slate-400" id="mem-stats">—</div>
    </div>
    <div class="sec-body" id="sb-mem-body" style="max-height:400px">
      <div class="px-4 pt-3 pb-3 chart-wrap">
        <canvas id="chart-mem"></canvas>
      </div>
    </div>
  </div>

  <!-- ══ Network ════════════════════════════════════════════════════════════ -->
  <div id="section-net" class="card overflow-hidden">
    <div class="sec-header flex items-center justify-between px-4 py-3 border-b border-green-900/40"
         onclick="toggle('sb-net-body','arr-net')">
      <div class="flex items-center gap-2">
        <span class="sec-arrow text-green-600 text-xs" id="arr-net">▼</span>
        <span class="text-green-400 font-semibold text-sm tracking-wide">Network</span>
      </div>
      <div class="flex gap-6 text-xs text-slate-400" id="net-stats">—</div>
    </div>
    <div class="sec-body" id="sb-net-body" style="max-height:500px">
      <div class="px-4 pt-3 pb-1 chart-wrap">
        <canvas id="chart-net"></canvas>
      </div>
      <div class="px-4 pb-3 overflow-x-auto mt-2">
        <table class="w-full text-xs">
          <thead>
            <tr class="text-slate-600 border-b border-green-900/30 text-right">
              <th class="text-left pb-1">Interface</th>
              <th class="pb-1">Sent MB</th><th class="pb-1">Recv MB</th>
              <th class="pb-1">Pkts Sent</th><th class="pb-1">Pkts Recv</th>
              <th class="pb-1">Errors</th><th class="pb-1">Drops</th>
            </tr>
          </thead>
          <tbody id="net-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ══ Disk ═══════════════════════════════════════════════════════════════ -->
  <div id="section-disk" class="card overflow-hidden">
    <div class="sec-header flex items-center justify-between px-4 py-3 border-b border-green-900/40"
         onclick="toggle('sb-disk-body','arr-disk')">
      <div class="flex items-center gap-2">
        <span class="sec-arrow text-green-600 text-xs" id="arr-disk">▼</span>
        <span class="text-green-400 font-semibold text-sm tracking-wide">Disk</span>
      </div>
      <div class="flex gap-6 text-xs text-slate-400" id="disk-io-stats">—</div>
    </div>
    <div class="sec-body" id="sb-disk-body" style="max-height:900px">
      <!-- I/O chart -->
      <div class="px-4 pt-3 pb-1 chart-wrap">
        <canvas id="chart-disk"></canvas>
      </div>
      <!-- hint -->
      <p class="px-4 pt-2 pb-1 text-xs text-slate-600">
        Click a disk to see partition details.
      </p>
      <!-- disk cards -->
      <div id="disk-cards" class="border-t border-green-900/30 mt-1"></div>
    </div>
  </div>

  <!-- ══ Processes ══════════════════════════════════════════════════════════ -->
  <div id="section-proc" class="card overflow-hidden">
    <div class="sec-header flex items-center justify-between px-4 py-3 border-b border-green-900/40">
      <div class="flex items-center gap-2 cursor-pointer" onclick="toggle('sb-proc-body','arr-proc')">
        <span class="sec-arrow text-green-600 text-xs" id="arr-proc">▼</span>
        <span class="text-green-400 font-semibold text-sm tracking-wide">Top Processes</span>
      </div>
      <div class="flex items-center gap-2">
        <span id="proc-tab-cpu" class="tag active-tag" onclick="switchProcTab('cpu')">by CPU</span>
        <span id="proc-tab-ram" class="tag" onclick="switchProcTab('ram')">by RAM</span>
      </div>
    </div>
    <div class="sec-body" id="sb-proc-body" style="max-height:700px">
      <div class="px-4 py-3 overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="text-slate-600 border-b border-green-900/30">
              <th class="text-right pb-1 pr-4">PID</th>
              <th class="text-left pb-1">Name</th>
              <th class="text-left pb-1">User</th>
              <th class="text-left pb-1">Status</th>
              <th class="text-right pb-1">CPU%</th>
              <th class="text-right pb-1">Mem%</th>
            </tr>
          </thead>
          <tbody id="proc-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

</div><!-- #main-content -->

<script>
// ── Constants ─────────────────────────────────────────────────────────────────
const MAX_PTS    = 60;
const INTERVAL_S = 10;
const ARC        = 157.08;

const CORE_COLORS = [
  '#f87171','#fb923c','#facc15','#4ade80','#2dd4bf',
  '#60a5fa','#818cf8','#c084fc','#e879f9','#f472b6',
  '#34d399','#22d3ee','#38bdf8','#a78bfa','#a3e635','#86efac'
];

const $  = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

// ── Sidebar ───────────────────────────────────────────────────────────────────
const SECTIONS = ['overview','cpu','mem','net','disk','proc'];

function toggleSidebar(force) {
  const sb = $('sidebar');
  const hidden = typeof force !== 'undefined' ? !force : !sb.classList.contains('sb-hidden');
  sb.classList.toggle('sb-hidden', hidden);
}

function navTo(id) {
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  const link = $('nav-' + id);
  if (link) link.classList.add('active');
  const sec = $('section-' + id);
  if (sec) {
    const top = sec.getBoundingClientRect().top + window.scrollY - 56;
    window.scrollTo({ top, behavior: 'smooth' });
  }
  if (window.innerWidth < 1024) toggleSidebar(false);
}

// Auto-highlight active nav item on scroll
window.addEventListener('scroll', () => {
  let current = SECTIONS[0];
  SECTIONS.forEach(id => {
    const el = $('section-' + id);
    if (el && el.getBoundingClientRect().top <= 80) current = id;
  });
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  const link = $('nav-' + current);
  if (link) link.classList.add('active');
}, { passive: true });

// ── Section collapse ──────────────────────────────────────────────────────────
function toggle(bodyId, arrowId) {
  const body = $(bodyId), arrow = $(arrowId);
  const open = body.style.maxHeight !== '0px';
  body.style.maxHeight  = open ? '0px' : '900px';
  arrow.style.transform = open ? 'rotate(-90deg)' : 'rotate(0deg)';
}

// ── Gauge ─────────────────────────────────────────────────────────────────────
function setGauge(pathId, txtId, pct, baseColor) {
  const el = $(pathId), tx = $(txtId);
  const v  = Math.min(Math.max(pct || 0, 0), 100);
  const c  = v > 85 ? '#f87171' : v > 65 ? '#facc15' : baseColor;
  el.style.strokeDashoffset = ARC * (1 - v / 100);
  el.style.stroke = c;
  tx.textContent  = v.toFixed(1) + '%';
  tx.style.fill   = c;
}

// ── Clock ─────────────────────────────────────────────────────────────────────
function tickClock() { $('hdr-clock').textContent = new Date().toLocaleTimeString(); }
tickClock(); setInterval(tickClock, 1000);

// ── Uptime ────────────────────────────────────────────────────────────────────
function fmtUptime(s) {
  const d=Math.floor(s/86400), h=Math.floor((s%86400)/3600), m=Math.floor((s%3600)/60);
  return d ? `up ${d}d ${h}h ${m}m` : h ? `up ${h}h ${m}m` : `up ${m}m`;
}

// ── X-axis time labels ────────────────────────────────────────────────────────
const X_LABELS = Array.from({length: MAX_PTS}, (_, i) => {
  const ago = (MAX_PTS - 1 - i) * INTERVAL_S;
  if (ago === 0)                  return 'now';
  if (ago < 60 && ago % 20 === 0) return ago + 's';
  if (ago >= 60 && ago % 60 === 0) return (ago/60) + 'm';
  return '';
});

// ── Chart factory ─────────────────────────────────────────────────────────────
function chartOpts(yExtra = {}) {
  return {
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{ legend:{ display:false } },
    scales:{
      x:{
        display:true,
        ticks:{ color:'#374151', maxRotation:0, autoSkip:false,
                font:{size:9, family:'ui-monospace,monospace'} },
        grid:{ color:'#162816' }, border:{ color:'#1a3a1a' }
      },
      y:{
        min:0,
        ticks:{ color:'#374151', font:{size:9, family:'ui-monospace,monospace'} },
        grid:{ color:'#162816' }, border:{ color:'#1a3a1a' },
        ...yExtra
      }
    }
  };
}

function blankDS(label, color, dashed) {
  return {
    label, borderColor:color, backgroundColor: color + '18',
    fill:!dashed, tension:.35, pointRadius:0, borderWidth:1.5,
    data: Array(MAX_PTS).fill(null),
    ...(dashed ? {borderDash:[5,3], fill:false} : {})
  };
}

function pushDS(chart, idx, val) {
  const d = chart.data.datasets[idx].data;
  d.push(val); if (d.length > MAX_PTS) d.shift();
}

// ── Charts ────────────────────────────────────────────────────────────────────
let cpuChart = null, _coreCount = 0;

function initCpuChart(n) {
  if (cpuChart) { cpuChart.destroy(); cpuChart = null; }
  _coreCount = n;
  cpuChart = new Chart($('chart-cpu'), {
    type: 'line',
    data: {
      labels: [...X_LABELS],
      datasets: Array.from({length:n}, (_, i) => ({
        label: 'CPU' + i,
        borderColor: CORE_COLORS[i % CORE_COLORS.length],
        backgroundColor: 'transparent',
        fill:false, tension:.35, pointRadius:0, borderWidth:1.3,
        data: Array(MAX_PTS).fill(null)
      }))
    },
    options: chartOpts({ max:100, ticks:{ callback: v => v+'%' } })
  });
  // legend
  $('cpu-legend').innerHTML = Array.from({length:n}, (_, i) => {
    const c = CORE_COLORS[i % CORE_COLORS.length];
    return `<span class="flex items-center gap-1 text-xs whitespace-nowrap">
      <span style="display:inline-block;width:10px;height:2px;background:${c}"></span>
      <span style="color:${c}" id="leg${i}">CPU${i} —</span>
    </span>`;
  }).join('');
}

const memChart = new Chart($('chart-mem'), {
  type:'line',
  data:{ labels:[...X_LABELS], datasets:[
    blankDS('RAM%','#4ade80',false), blankDS('Swap%','#86efac',true) ] },
  options: chartOpts({ max:100, ticks:{ callback: v => v+'%' } })
});

const netChart = new Chart($('chart-net'), {
  type:'line',
  data:{ labels:[...X_LABELS], datasets:[
    blankDS('Recv ↓','#22c55e',false), blankDS('Send ↑','#2dd4bf',true) ] },
  options: chartOpts({ suggestedMax:1, ticks:{ callback: v => v.toFixed(2) } })
});

const diskChart = new Chart($('chart-disk'), {
  type:'line',
  data:{ labels:[...X_LABELS], datasets:[
    blankDS('Read','#38bdf8',false), blankDS('Write','#818cf8',true) ] },
  options: chartOpts({ suggestedMax:.1, ticks:{ callback: v => v.toFixed(2) } })
});

// ── Per-core mini bars ────────────────────────────────────────────────────────
function updateCores(perCore) {
  const grid = $('per-core-grid');
  if (perCore.length !== _coreCount || grid.children.length !== perCore.length) {
    grid.innerHTML = perCore.map((_, i) => {
      const c = CORE_COLORS[i % CORE_COLORS.length];
      return `<div>
        <div class="flex justify-between text-xs mb-0.5">
          <span style="color:${c}">C${i}</span>
          <span id="cv${i}" class="text-slate-400">0%</span>
        </div>
        <div class="h-1.5 rounded-full" style="background:#162816">
          <div id="cb${i}" class="h-1.5 rounded-full bar-fill"
               style="background:${c};width:0%"></div>
        </div>
      </div>`;
    }).join('');
  }
  perCore.forEach((v, i) => {
    const pct = Math.min(v, 100);
    const bar = $('cb'+i), val = $('cv'+i);
    if (bar) bar.style.width = pct + '%';
    if (val) val.textContent = pct.toFixed(0) + '%';
    const leg = $('leg'+i);
    if (leg) leg.textContent = `CPU${i} ${pct.toFixed(1)}%`;
  });
}

// ── Disk cards ────────────────────────────────────────────────────────────────
let _diskState = {}; // track open/closed per index

function updateDisks(partitions) {
  const container = $('disk-cards');
  // Preserve open state
  const newState = {};
  Object.keys(_diskState).forEach(k => { newState[k] = _diskState[k]; });

  container.innerHTML = partitions.map((p, i) => {
    const color = p.percent > 90 ? '#f87171' : p.percent > 75 ? '#facc15' : '#22c55e';
    const isOpen = !!_diskState[i];
    const arrowRot = isOpen ? '90deg' : '0deg';
    const detailH  = isOpen ? '200px' : '0';
    return `
    <div class="disk-card">
      <div class="disk-hdr flex items-center gap-3 px-4 py-3"
           onclick="toggleDisk(${i})">
        <!-- disk icon -->
        <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
             style="background:#162816">
          <svg viewBox="0 0 16 16" class="w-4 h-4" fill="none" stroke="#22c55e" stroke-width="1.5">
            <rect x="2" y="3" width="12" height="10" rx="2"/>
            <circle cx="8" cy="8" r="1.5" fill="#22c55e" stroke="none"/>
            <line x1="5" y1="5.5" x2="7" y2="5.5"/>
          </svg>
        </div>
        <!-- info -->
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap justify-between gap-2 mb-1.5 items-baseline">
            <div>
              <span class="text-green-300 font-medium">${p.mountpoint}</span>
              <span class="text-slate-600 text-xs ml-2">${p.device}</span>
            </div>
            <span class="text-xs font-bold" style="color:${color}">
              ${p.used_gb} / ${p.total_gb} GB &nbsp; ${p.percent.toFixed(1)}%
            </span>
          </div>
          <div class="h-2 rounded-full" style="background:#162816">
            <div class="h-2 rounded-full bar-fill"
                 style="background:${color};width:${p.percent}%"></div>
          </div>
        </div>
        <!-- expand arrow -->
        <span class="text-green-900 text-xs transition-transform duration-200 flex-shrink-0"
              style="transform:rotate(${arrowRot})"
              id="darr-${i}">▶</span>
      </div>
      <!-- expanded detail -->
      <div class="disk-detail ${isOpen ? 'open' : ''}" id="ddetail-${i}"
           style="max-height:${detailH}">
        <div class="px-4 pb-4 border-t border-green-900/20 bg-[#060f06]">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-3">
            <div><div class="kv-label">Filesystem</div>
                 <div class="kv-value">${p.fstype}</div></div>
            <div><div class="kv-label">Total</div>
                 <div class="kv-value">${p.total_gb} GB</div></div>
            <div><div class="kv-label">Used</div>
                 <div class="kv-value" style="color:${color}">${p.used_gb} GB</div></div>
            <div><div class="kv-label">Free</div>
                 <div class="kv-value text-green-400">${p.free_gb} GB</div></div>
          </div>
          <!-- mini usage bar with labels -->
          <div class="mt-3">
            <div class="h-3 rounded-full flex overflow-hidden" style="background:#162816">
              <div style="width:${p.percent}%;background:${color}" class="h-full rounded-l-full"></div>
            </div>
            <div class="flex justify-between text-xs mt-1 text-slate-600">
              <span>Used: ${p.used_gb} GB</span>
              <span>Free: ${p.free_gb} GB</span>
            </div>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleDisk(i) {
  _diskState[i] = !_diskState[i];
  const detail = $('ddetail-' + i), arrow = $('darr-' + i);
  if (!detail) return;
  const open = _diskState[i];
  detail.classList.toggle('open', open);
  detail.style.maxHeight = open ? '200px' : '0';
  if (arrow) arrow.style.transform = open ? 'rotate(90deg)' : 'rotate(0deg)';
}

// ── Network table ─────────────────────────────────────────────────────────────
function updateNetTable(interfaces) {
  $('net-tbody').innerHTML = Object.entries(interfaces).map(([nic, s]) => {
    const errs  = s.errin + s.errout, drops = s.dropin + s.dropout;
    return `<tr class="border-b border-green-900/20">
      <td class="text-green-400 font-medium">${nic}</td>
      <td class="text-right tabular-nums">${s.bytes_sent_mb.toFixed(2)}</td>
      <td class="text-right tabular-nums">${s.bytes_recv_mb.toFixed(2)}</td>
      <td class="text-right tabular-nums">${s.packets_sent.toLocaleString()}</td>
      <td class="text-right tabular-nums">${s.packets_recv.toLocaleString()}</td>
      <td class="text-right tabular-nums ${errs  > 0 ? 'text-red-400':'text-slate-600'}">${errs}</td>
      <td class="text-right tabular-nums ${drops > 0 ? 'text-yellow-400':'text-slate-600'}">${drops}</td>
    </tr>`;
  }).join('');
}

// ── Process table ─────────────────────────────────────────────────────────────
let _allProcs = [];
let _procTab = 'cpu';

function switchProcTab(tab) {
  _procTab = tab;
  $('proc-tab-cpu').className = tab === 'cpu' ? 'tag active-tag' : 'tag';
  $('proc-tab-ram').className = tab === 'ram' ? 'tag active-tag' : 'tag';
  renderProcs();
}

function renderProcs() {
  const sorted = [..._allProcs].sort((a, b) =>
    _procTab === 'ram' ? b.memory_percent - a.memory_percent : b.cpu_percent - a.cpu_percent
  );
  $('proc-tbody').innerHTML = sorted.slice(0, 15).map(p => {
    const cc = p.cpu_percent > 50 ? '#f87171' : p.cpu_percent > 20 ? '#facc15' : '#c8d8c8';
    const mc = p.memory_percent > 5 ? '#f87171' : p.memory_percent > 2 ? '#facc15' : '#94a3b8';
    return `<tr class="border-b border-green-900/20">
      <td class="text-right pr-4 text-slate-500">${p.pid}</td>
      <td class="text-green-300 font-medium">${p.name}</td>
      <td class="text-slate-500">${p.username}</td>
      <td class="text-slate-500">${p.status}</td>
      <td class="text-right tabular-nums font-bold" style="color:${cc}">${p.cpu_percent.toFixed(1)}%</td>
      <td class="text-right tabular-nums font-bold" style="color:${mc}">${p.memory_percent.toFixed(2)}%</td>
    </tr>`;
  }).join('');
}

function updateProcs(procs) {
  _allProcs = procs;
  renderProcs();
}

// ── I/O delta helpers ─────────────────────────────────────────────────────────
let prevSnap = null;

function diskSpeed(curr, prev, dt) {
  if (!prev || dt <= 0) return {r:0, w:0};
  let dr=0, dw=0;
  for (const d of Object.keys(curr.io)) {
    if (prev.io[d]) {
      dr += curr.io[d].read_mb  - prev.io[d].read_mb;
      dw += curr.io[d].write_mb - prev.io[d].write_mb;
    }
  }
  return { r: Math.max(0, dr/dt), w: Math.max(0, dw/dt) };
}

function netSpeed(curr, prev, dt) {
  if (!prev || dt <= 0) return {tx:0, rx:0};
  let dtx=0, drx=0;
  for (const n of Object.keys(curr.interfaces)) {
    if (prev.interfaces[n]) {
      dtx += curr.interfaces[n].bytes_sent_mb - prev.interfaces[n].bytes_sent_mb;
      drx += curr.interfaces[n].bytes_recv_mb - prev.interfaces[n].bytes_recv_mb;
    }
  }
  const f = 8/dt;
  return { tx: Math.max(0, dtx*f), rx: Math.max(0, drx*f) };
}

// ── Apply snapshot ────────────────────────────────────────────────────────────
function applySnapshot(snap, chartPush = true) {
  const cpu=snap.cpu, mem=snap.memory, disk=snap.disk, net=snap.network, proc=snap.processes;

  // Last-reading timestamp
  const t = new Date(snap.timestamp);
  $('si-updated').textContent = t.toLocaleTimeString();
  $('hdr-updated').textContent = 'updated ' + t.toLocaleTimeString();

  // Gauges + sidebar
  setGauge('g-cpu','g-cpu-txt', cpu.overall_percent, '#22c55e');
  $('g-cpu-freq').textContent = cpu.freq_mhz ? cpu.freq_mhz + ' MHz' : '—';
  $('cpu-cores-tag').textContent =
    (cpu.count_physical||cpu.count_logical) + 'P / ' + cpu.count_logical + 'L';
  $('sb-cpu').textContent = cpu.overall_percent.toFixed(1) + '%';

  setGauge('g-ram','g-ram-txt', mem.virtual.percent, '#4ade80');
  $('g-ram-sub').textContent =
    (mem.virtual.used_mb/1024).toFixed(1) + ' / ' + (mem.virtual.total_mb/1024).toFixed(1) + ' GB';
  $('sb-mem').textContent = mem.virtual.percent.toFixed(1) + '%';

  setGauge('g-swap','g-swap-txt', mem.swap.percent, '#86efac');
  $('g-swap-sub').textContent =
    (mem.swap.used_mb/1024).toFixed(1) + ' / ' + (mem.swap.total_mb/1024).toFixed(1) + ' GB';

  $('mem-stats').innerHTML =
    `<span>RAM <b class="text-slate-300">${(mem.virtual.used_mb/1024).toFixed(2)} GB</b>` +
    ` (${mem.virtual.percent.toFixed(1)}%) of ${(mem.virtual.total_mb/1024).toFixed(1)} GB</span>` +
    `<span>Swap <b class="text-slate-300">${mem.swap.used_mb.toFixed(0)} MB</b>` +
    ` (${mem.swap.percent.toFixed(1)}%)</span>`;

  // I/O speeds
  const dt = prevSnap ? (new Date(snap.timestamp) - new Date(prevSnap.timestamp))/1000 : 0;
  const ds = diskSpeed(disk, prevSnap?.disk, dt);
  const ns = netSpeed(net,  prevSnap?.network, dt);

  $('stat-disk-r').textContent = ds.r.toFixed(2);
  $('stat-disk-w').textContent = ds.w.toFixed(2);
  $('stat-net-tx').textContent = ns.tx.toFixed(3);
  $('stat-net-rx').textContent = ns.rx.toFixed(3);
  $('sb-disk-r').textContent   = ds.r.toFixed(2) + ' MiB/s';
  $('sb-disk-w').textContent   = ds.w.toFixed(2) + ' MiB/s';
  $('sb-net-tx').textContent   = ns.tx.toFixed(3) + ' Mbit/s';
  $('sb-net-rx').textContent   = ns.rx.toFixed(3) + ' Mbit/s';

  $('disk-io-stats').innerHTML =
    `<span>Read <b class="text-sky-400">${ds.r.toFixed(2)} MiB/s</b></span>` +
    `<span>Write <b class="text-indigo-400">${ds.w.toFixed(2)} MiB/s</b></span>`;
  $('net-stats').innerHTML =
    `<span>↓ <b class="text-green-400">${ns.rx.toFixed(3)} Mbit/s</b></span>` +
    `<span>↑ <b class="text-teal-400">${ns.tx.toFixed(3)} Mbit/s</b></span>`;

  if (chartPush) {
    if (!cpuChart || cpu.per_core_percent.length !== _coreCount) initCpuChart(cpu.per_core_percent.length);
    cpu.per_core_percent.forEach((v, i) => pushDS(cpuChart, i, v));
    cpuChart.update('none');
    pushDS(memChart, 0, mem.virtual.percent); pushDS(memChart, 1, mem.swap.percent);
    memChart.update('none');
    pushDS(netChart, 0, ns.rx); pushDS(netChart, 1, ns.tx);
    netChart.update('none');
    pushDS(diskChart, 0, ds.r); pushDS(diskChart, 1, ds.w);
    diskChart.update('none');
  }

  prevSnap = snap;

  updateCores(cpu.per_core_percent);
  updateDisks(disk.partitions);
  updateNetTable(net.interfaces);
  updateProcs(proc.processes);
}

// ── Sysinfo ───────────────────────────────────────────────────────────────────
async function loadSysinfo() {
  try {
    const d = await fetch('/sysinfo').then(r => r.json());
    $('hdr-hostname').textContent = d.hostname;
    $('sb-hostname').textContent  = d.hostname;
    $('hdr-os').textContent  = d.os + ' · ' + d.machine;
    $('si-proc').textContent = d.processor || d.machine;
    $('si-cores').textContent = (d.physical_cores||'?') + 'P / ' + (d.logical_cores||'?') + 'L';
    $('si-ram').textContent  = d.total_ram_gb + ' GB';
    $('si-arch').textContent = d.machine;
    $('si-boot').textContent = new Date(d.boot_time).toLocaleString();
    let up = d.uptime_seconds;
    $('hdr-uptime').textContent = fmtUptime(up);
    setInterval(() => { up++; $('hdr-uptime').textContent = fmtUptime(up); }, 1000);
  } catch(e) { console.error('sysinfo:', e); }
}

// ── History prefill ────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const snaps = await fetch('/stats').then(r => r.json());
    if (!snaps.length) return;
    const recent = snaps.slice(-MAX_PTS);
    if (recent[0]) initCpuChart(recent[0].cpu.per_core_percent.length);
    let pp = null;
    recent.slice(0, -1).forEach((s, i) => {
      const prev = i > 0 ? recent[i-1] : null;
      const dt2  = prev ? (new Date(s.timestamp) - new Date(prev.timestamp))/1000 : 0;
      const ds2  = diskSpeed(s.disk, prev?.disk, dt2);
      const ns2  = netSpeed(s.network, prev?.network, dt2);
      s.cpu.per_core_percent.forEach((v, j) => pushDS(cpuChart, j, v));
      pushDS(memChart,  0, s.memory.virtual.percent);
      pushDS(memChart,  1, s.memory.swap.percent);
      pushDS(netChart,  0, ns2.rx); pushDS(netChart,  1, ns2.tx);
      pushDS(diskChart, 0, ds2.r);  pushDS(diskChart, 1, ds2.w);
    });
    cpuChart.update('none'); memChart.update('none');
    netChart.update('none'); diskChart.update('none');
    prevSnap = recent.length > 1 ? recent[recent.length - 2] : null;
    applySnapshot(recent[recent.length - 1]);
  } catch(e) { console.error('history:', e); }
}

// ── Refresh slider ────────────────────────────────────────────────────────────
const REFRESH_STEPS  = [500, 1000, 2000, 3000, 5000, 10000, 30000];
const REFRESH_LABELS = ['0.5s','1s','2s','3s','5s','10s','30s'];
let _pollTimer = null;

function startPolling(ms) {
  if (_pollTimer) clearInterval(_pollTimer);
  _pollTimer = setInterval(poll, ms);
}

$('refresh-slider').addEventListener('input', () => {
  const idx = parseInt($('refresh-slider').value);
  $('refresh-label').textContent = REFRESH_LABELS[idx];
  startPolling(REFRESH_STEPS[idx]);
});

// ── Poll ──────────────────────────────────────────────────────────────────────
async function poll() {
  try {
    const snap = await fetch('/stats/latest').then(r => r.ok ? r.json() : null);
    if (snap) applySnapshot(snap);
  } catch(e) { console.error('poll error:', e); }
}

// ── Boot ──────────────────────────────────────────────────────────────────────
loadSysinfo();
loadHistory().then(() => {
  const idx = parseInt($('refresh-slider').value);
  $('refresh-label').textContent = REFRESH_LABELS[idx];
  startPolling(REFRESH_STEPS[idx]);
});
</script>
</body>
</html>
"""
