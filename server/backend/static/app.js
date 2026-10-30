// RouterLink Web Administration Panel (Single-Page Application)
(function () {
  const API_BASE = '/api/v1';

  // State
  const state = {
    token: localStorage.getItem('routerlink_token') || null,
    adminUser: localStorage.getItem('routerlink_username') || null,
    currentTab: 'dashboard',
    theme: localStorage.getItem('routerlink_theme') || 'dark',
    setupRequired: false,
    stats: null,
    users: [],
    protocols: [],
    sessions: [],
    backups: [],
    auditLogs: [],
    activeModal: null, // 'createUser', 'editQuota', 'qrCode', 'logs'
    selectedUser: null,
    selectedProtocol: null,
    protocolLogs: [],
    throughputHistory: [],
    pollTimer: null,
  };

  // Helper Functions
  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function formatDuration(seconds) {
    if (!seconds) return '0s';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  }

  async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (res.status === 401 && !path.includes('/auth/')) {
      logout();
      throw new Error('Unauthorized');
    }
    if (res.status === 204) return null;
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      throw new Error((data && (data.detail || data.message)) || `HTTP ${res.status}`);
    }
    return data;
  }

  function logout() {
    state.token = null;
    state.adminUser = null;
    localStorage.removeItem('routerlink_token');
    localStorage.removeItem('routerlink_username');
    if (state.pollTimer) clearInterval(state.pollTimer);
    render();
  }

  // Initial Boot
  async function init() {
    try {
      const setup = await api('/auth/setup/status');
      state.setupRequired = setup.is_setup_required;
      if (!state.setupRequired && state.token) {
        startPolling();
      }
    } catch (e) {
      console.error('Initialization error:', e);
    }
    render();
  }

  function startPolling() {
    fetchDashboardData();
    if (state.pollTimer) clearInterval(state.pollTimer);
    state.pollTimer = setInterval(fetchDashboardData, 4000);
  }

  async function fetchDashboardData() {
    if (!state.token) return;
    try {
      if (state.currentTab === 'dashboard') {
        const stats = await api('/admin/system/stats');
        state.stats = stats;
        // Keep 20 throughput data points
        const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        state.throughputHistory.push({
          time: nowStr,
          upload: stats.total_upload_bytes,
          download: stats.total_download_bytes
        });
        if (state.throughputHistory.length > 15) state.throughputHistory.shift();

        const protos = await api('/admin/protocols');
        state.protocols = protos;
      } else if (state.currentTab === 'users') {
        state.users = await api('/admin/users');
      } else if (state.currentTab === 'protocols') {
        state.protocols = await api('/admin/protocols');
      } else if (state.currentTab === 'sessions') {
        state.sessions = await api('/admin/sessions');
      } else if (state.currentTab === 'settings') {
        state.backups = await api('/admin/system/backups');
        state.auditLogs = await api('/admin/system/audit-logs');
      }
      render();
    } catch (e) {
      console.error('Polling error:', e);
    }
  }

  // Views & Components
  function render() {
    const app = document.getElementById('app');
    if (!app) return;

    if (state.setupRequired) {
      app.innerHTML = renderSetupView();
      bindSetupEvents();
      return;
    }

    if (!state.token) {
      app.innerHTML = renderLoginView();
      bindLoginEvents();
      return;
    }

    app.innerHTML = `
      <div class="flex h-screen overflow-hidden">
        ${renderSidebar()}
        <div class="flex-1 flex flex-col min-w-0 overflow-y-auto">
          ${renderNavbar()}
          <main class="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
            ${renderCurrentTab()}
          </main>
        </div>
      </div>
      ${renderModal()}
    `;

    bindAppEvents();
  }

  function renderSidebar() {
    const navItems = [
      { id: 'dashboard', label: 'Dashboard', icon: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>' },
      { id: 'users', label: 'Users & Quotas', icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>' },
      { id: 'protocols', label: 'Protocols', icon: '<rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>' },
      { id: 'sessions', label: 'Active Sessions', icon: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>' },
      { id: 'settings', label: 'System & Backup', icon: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>' }
    ];

    return `
      <aside class="w-64 glass border-r border-dark-border flex flex-col justify-between shrink-0">
        <div>
          <div class="h-16 flex items-center px-6 border-b border-dark-border gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/30">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>
            </div>
            <div>
              <div class="font-bold tracking-tight text-white flex items-center gap-1.5">
                RouterLink
                <span class="text-[10px] uppercase font-bold bg-brand-500/20 text-brand-400 px-1.5 py-0.5 rounded border border-brand-500/30">ROS 7</span>
              </div>
              <div class="text-xs text-slate-400">MikroTik Gateway</div>
            </div>
          </div>
          <nav class="p-4 space-y-1.5">
            ${navItems.map(item => `
              <button data-tab="${item.id}" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${state.currentTab === item.id ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">${item.icon}</svg>
                ${item.label}
              </button>
            `).join('')}
          </nav>
        </div>
        <div class="p-4 border-t border-dark-border">
          <div class="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center text-slate-300 font-semibold text-xs uppercase">
                ${(state.adminUser || 'AD').substring(0, 2)}
              </div>
              <div class="overflow-hidden">
                <div class="text-xs font-semibold text-slate-200 truncate">${state.adminUser || 'Admin'}</div>
                <div class="text-[10px] text-emerald-400 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>Online</div>
              </div>
            </div>
            <button id="logoutBtn" title="Logout" class="p-1.5 hover:bg-slate-700/60 rounded-lg text-slate-400 hover:text-rose-400 transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            </button>
          </div>
        </div>
      </aside>
    `;
  }

  function renderNavbar() {
    return `
      <header class="h-16 glass border-b border-dark-border flex items-center justify-between px-6 shrink-0 sticky top-0 z-10">
        <div class="flex items-center gap-2">
          <h1 class="text-lg font-bold text-white capitalize">${state.currentTab}</h1>
          <span class="text-xs text-slate-500 font-medium">/ RouterLink Core Engine</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="hidden sm:flex items-center gap-2 text-xs bg-slate-800/60 border border-slate-700/60 px-3 py-1.5 rounded-lg text-slate-300">
            <span class="text-slate-400">Gateway:</span>
            <code class="font-mono text-brand-400 font-semibold">172.28.0.2</code>
          </div>
          <button id="refreshDataBtn" class="flex items-center gap-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
            Sync
          </button>
        </div>
      </header>
    `;
  }

  function renderCurrentTab() {
    switch (state.currentTab) {
      case 'dashboard': return renderDashboard();
      case 'users': return renderUsers();
      case 'protocols': return renderProtocols();
      case 'sessions': return renderSessions();
      case 'settings': return renderSettings();
      default: return renderDashboard();
    }
  }

  function renderDashboard() {
    const s = state.stats || {
      cpu_percent: 0, ram_percent: 0, ram_used_mb: 0, ram_total_mb: 0,
      total_users: 0, online_users: 0, active_sessions: 0,
      total_upload_bytes: 0, total_download_bytes: 0, total_traffic_bytes: 0
    };

    return `
      <div class="space-y-6">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="glass p-5 rounded-2xl border border-dark-border">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">System Load</span>
              <div class="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>
              </div>
            </div>
            <div class="text-2xl font-bold text-white mb-2">CPU: ${s.cpu_percent}%</div>
            <div class="w-full bg-slate-800 rounded-full h-1.5 mb-1.5 overflow-hidden">
              <div class="bg-indigo-500 h-1.5 rounded-full" style="width: ${s.cpu_percent}%"></div>
            </div>
            <div class="text-xs text-slate-400">RAM: ${s.ram_used_mb}MB / ${s.ram_total_mb}MB (${s.ram_percent}%)</div>
          </div>

          <div class="glass p-5 rounded-2xl border border-dark-border">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Online Users</span>
              <div class="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
              </div>
            </div>
            <div class="text-2xl font-bold text-white mb-2">${s.online_users} <span class="text-xs font-normal text-slate-400">active now</span></div>
            <div class="text-xs text-slate-400">Total Registered Users: <strong class="text-slate-200">${s.total_users}</strong></div>
          </div>

          <div class="glass p-5 rounded-2xl border border-dark-border">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Tunnels</span>
              <div class="p-2 rounded-xl bg-amber-500/10 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              </div>
            </div>
            <div class="text-2xl font-bold text-white mb-2">${s.active_sessions}</div>
            <div class="text-xs text-slate-400">OpenVPN & WireGuard Sessions</div>
          </div>

          <div class="glass p-5 rounded-2xl border border-dark-border">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Bandwidth</span>
              <div class="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </div>
            </div>
            <div class="text-2xl font-bold text-white mb-2">${formatBytes(s.total_traffic_bytes)}</div>
            <div class="text-xs text-slate-400 flex justify-between">
              <span>↓ ${formatBytes(s.total_download_bytes)}</span>
              <span>↑ ${formatBytes(s.total_upload_bytes)}</span>
            </div>
          </div>
        </div>

        <!-- Live Waveform Chart & Protocols -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 glass p-6 rounded-2xl border border-dark-border">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="font-bold text-white text-base">Live Throughput Monitor</h3>
                <p class="text-xs text-slate-400">Real-time aggregate data flow across active tunnels</p>
              </div>
              <span class="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Live Poll (4s)
              </span>
            </div>
            <div class="h-56 w-full flex items-end justify-between gap-1 pt-6 pb-2 px-2 border-b border-dark-border bg-slate-900/40 rounded-xl relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-t from-brand-600/10 to-transparent pointer-events-none"></div>
              ${renderThroughputChart()}
            </div>
          </div>

          <div class="glass p-6 rounded-2xl border border-dark-border flex flex-col justify-between">
            <div>
              <h3 class="font-bold text-white text-base mb-1">Protocol Daemon Health</h3>
              <p class="text-xs text-slate-400 mb-4">Active VPN services running in container</p>
              <div class="space-y-3">
                ${state.protocols.map(p => `
                  <div class="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-center justify-between">
                    <div>
                      <div class="font-semibold text-sm text-slate-200 capitalize">${p.protocol_name.replace('_', ' ')}</div>
                      <div class="text-xs text-slate-400 font-mono">Port: ${p.listen_port}/${p.transport_type.toUpperCase()}</div>
                    </div>
                    <span class="px-2.5 py-1 text-[11px] font-semibold rounded-full ${p.status === 'running' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'}">
                      ${p.status}
                    </span>
                  </div>
                `).join('')}
              </div>
            </div>
            <button data-tab="protocols" class="mt-4 w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition">
              Manage Protocols →
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function renderThroughputChart() {
    if (state.throughputHistory.length < 2) {
      return `<div class="w-full h-full flex items-center justify-center text-xs text-slate-500">Collecting live network metrics...</div>`;
    }
    const maxVal = Math.max(...state.throughputHistory.map(h => Math.max(h.upload, h.download)), 1024 * 1024);
    return state.throughputHistory.map(h => {
      const hDown = Math.min(100, Math.max(8, (h.download / maxVal) * 100));
      const hUp = Math.min(100, Math.max(8, (h.upload / maxVal) * 100));
      return `
        <div class="flex-1 flex flex-col items-center gap-1 group relative">
          <div class="w-full flex items-end justify-center gap-0.5 h-44">
            <div class="w-2 rounded-t bg-brand-500 hover:bg-brand-400 transition-all" style="height: ${hDown}%" title="Download: ${formatBytes(h.download)}"></div>
            <div class="w-2 rounded-t bg-emerald-500 hover:bg-emerald-400 transition-all" style="height: ${hUp}%" title="Upload: ${formatBytes(h.upload)}"></div>
          </div>
          <span class="text-[9px] text-slate-500 truncate w-10 text-center">${h.time}</span>
        </div>
      `;
    }).join('');
  }

  function renderUsers() {
    return `
      <div class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">VPN Accounts & Quotas</h2>
            <p class="text-xs text-slate-400">Create, manage, and monitor client connection credentials</p>
          </div>
          <button id="openCreateUserModal" class="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm px-4 py-2.5 rounded-xl shadow-lg shadow-brand-600/30 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Create User
          </button>
        </div>

        <div class="glass rounded-2xl border border-dark-border overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-300">
              <thead class="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-dark-border">
                <tr>
                  <th class="py-3.5 px-4">User</th>
                  <th class="py-3.5 px-4">Status</th>
                  <th class="py-3.5 px-4">Traffic Usage / Limit</th>
                  <th class="py-3.5 px-4">Expiration</th>
                  <th class="py-3.5 px-4">Max Devices</th>
                  <th class="py-3.5 px-4">Allowed Protocols</th>
                  <th class="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-dark-border">
                ${state.users.length === 0 ? `
                  <tr><td colspan="7" class="py-8 text-center text-slate-500">No users found. Click "Create User" to add one.</td></tr>
                ` : state.users.map(u => `
                  <tr class="hover:bg-slate-800/30 transition">
                    <td class="py-3.5 px-4">
                      <div class="font-bold text-white">${u.username}</div>
                      ${u.email ? `<div class="text-xs text-slate-500">${u.email}</div>` : ''}
                    </td>
                    <td class="py-3.5 px-4">
                      ${u.can_connect 
                        ? `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Active</span>`
                        : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">${u.is_quota_depleted ? 'Quota Exhausted' : (u.is_expired ? 'Expired' : 'Disabled')}</span>`}
                    </td>
                    <td class="py-3.5 px-4">
                      <div class="font-semibold text-slate-200">${formatBytes(u.used_traffic_bytes)} / ${u.traffic_limit_bytes > 0 ? formatBytes(u.traffic_limit_bytes) : 'Unlimited'}</div>
                      ${u.traffic_limit_bytes > 0 ? `
                        <div class="w-32 bg-slate-800 rounded-full h-1 mt-1 overflow-hidden">
                          <div class="bg-brand-500 h-1 rounded-full" style="width: ${Math.min(100, (u.used_traffic_bytes / u.traffic_limit_bytes) * 100)}%"></div>
                        </div>
                      ` : ''}
                    </td>
                    <td class="py-3.5 px-4 text-xs font-mono">
                      ${u.expires_at ? new Date(u.expires_at).toLocaleDateString() : '<span class="text-slate-500">Lifetime</span>'}
                    </td>
                    <td class="py-3.5 px-4 font-mono text-xs">
                      ${u.active_sessions_count} / ${u.max_concurrent_connections}
                    </td>
                    <td class="py-3.5 px-4 text-xs font-mono text-slate-400">
                      ${u.allowed_protocols.split(',').map(p => `<span class="inline-block bg-slate-800 px-1.5 py-0.5 rounded text-[10px] mr-1">${p}</span>`).join('')}
                    </td>
                    <td class="py-3.5 px-4 text-right space-x-1.5">
                      <button data-action="qr" data-id="${u.id}" class="p-1.5 hover:bg-slate-700/60 rounded-lg text-slate-300 hover:text-brand-400 transition" title="Show QR Code for Android">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                      </button>
                      <button data-action="quota" data-id="${u.id}" class="p-1.5 hover:bg-slate-700/60 rounded-lg text-slate-300 hover:text-amber-400 transition" title="Add / Reset Quota">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                      </button>
                      <button data-action="delete" data-id="${u.id}" class="p-1.5 hover:bg-slate-700/60 rounded-lg text-slate-300 hover:text-rose-400 transition" title="Delete User">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  function renderProtocols() {
    return `
      <div class="space-y-6">
        <div>
          <h2 class="text-xl font-bold text-white">VPN Protocol Engines</h2>
          <p class="text-xs text-slate-400">Configure ports, ciphers, and control service daemons</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          ${state.protocols.map(p => `
            <div class="glass p-6 rounded-2xl border border-dark-border flex flex-col justify-between space-y-4">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <div class="font-bold text-lg text-white capitalize">${p.protocol_name.replace('_', ' ')}</div>
                  <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full ${p.status === 'running' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'}">
                    ${p.status}
                  </span>
                </div>
                <div class="space-y-2 text-xs text-slate-400">
                  <div class="flex justify-between py-1 border-b border-dark-border">
                    <span>Transport:</span>
                    <strong class="text-slate-200 uppercase font-mono">${p.transport_type}</strong>
                  </div>
                  <div class="flex justify-between py-1 border-b border-dark-border">
                    <span>Listen Port:</span>
                    <strong class="text-brand-400 font-mono">${p.listen_port}</strong>
                  </div>
                  <div class="flex justify-between py-1 border-b border-dark-border">
                    <span>Connected Clients:</span>
                    <strong class="text-slate-200 font-mono">${p.connected_clients}</strong>
                  </div>
                  <div class="flex justify-between py-1">
                    <span>Cipher Suite:</span>
                    <span class="text-slate-300 font-mono truncate max-w-[150px]">${p.cipher_settings || 'Default'}</span>
                  </div>
                </div>
              </div>

              <div class="pt-4 border-t border-dark-border flex items-center gap-2">
                <button data-proto-action="restart" data-name="${p.protocol_name}" class="flex-1 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition">
                  Restart
                </button>
                <button data-proto-action="logs" data-name="${p.protocol_name}" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition" title="View Logs">
                  Logs
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  function renderSessions() {
    return `
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Live Connected Sessions</h2>
            <p class="text-xs text-slate-400">Active tunnel connections with remote IPs, durations, and transfer rates</p>
          </div>
          <span class="text-xs bg-slate-800 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-lg font-mono">
            Active: <strong>${state.sessions.length}</strong>
          </span>
        </div>

        <div class="glass rounded-2xl border border-dark-border overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-300">
              <thead class="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-dark-border">
                <tr>
                  <th class="py-3.5 px-4">User & Device</th>
                  <th class="py-3.5 px-4">Protocol</th>
                  <th class="py-3.5 px-4">Client IP</th>
                  <th class="py-3.5 px-4">Assigned VPN IP</th>
                  <th class="py-3.5 px-4">Duration</th>
                  <th class="py-3.5 px-4">Transferred</th>
                  <th class="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-dark-border">
                ${state.sessions.length === 0 ? `
                  <tr><td colspan="7" class="py-8 text-center text-slate-500">No active client sessions connected.</td></tr>
                ` : state.sessions.map(s => `
                  <tr class="hover:bg-slate-800/30 transition">
                    <td class="py-3.5 px-4">
                      <div class="font-bold text-white">${s.username || 'Unknown'}</div>
                      <div class="text-xs text-slate-500">${s.device_name}</div>
                    </td>
                    <td class="py-3.5 px-4 text-xs font-mono uppercase text-brand-400">
                      ${s.protocol}
                    </td>
                    <td class="py-3.5 px-4 font-mono text-xs text-slate-300">
                      ${s.client_ip || '172.28.0.x'}
                    </td>
                    <td class="py-3.5 px-4 font-mono text-xs text-emerald-400">
                      ${s.assigned_vpn_ip || '10.8.0.x'}
                    </td>
                    <td class="py-3.5 px-4 text-xs font-mono">
                      ${formatDuration(s.duration_seconds)}
                    </td>
                    <td class="py-3.5 px-4 text-xs">
                      <div>↓ ${formatBytes(s.download_bytes)}</div>
                      <div class="text-slate-500">↑ ${formatBytes(s.upload_bytes)}</div>
                    </td>
                    <td class="py-3.5 px-4 text-right">
                      <button data-terminate-session="${s.id}" class="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 font-semibold text-xs transition">
                        Terminate
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  function renderSettings() {
    return `
      <div class="space-y-6">
        <div>
          <h2 class="text-xl font-bold text-white">System Settings & Data Backups</h2>
          <p class="text-xs text-slate-400">Database archives, security audit trail, and persistent storage management</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Backup Card -->
          <div class="glass p-6 rounded-2xl border border-dark-border space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-bold text-white text-base">Persistent Database Backups</h3>
                <p class="text-xs text-slate-400">Instant snapshot of users, quotas, and certificates</p>
              </div>
              <button id="createBackupBtn" class="px-3.5 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-semibold transition">
                Create Backup
              </button>
            </div>
            <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
              ${state.backups.length === 0 ? `
                <div class="text-xs text-slate-500 py-4 text-center">No backup snapshots created yet.</div>
              ` : state.backups.map(b => `
                <div class="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-center justify-between text-xs">
                  <div>
                    <div class="font-mono text-slate-200 font-semibold">${b.filename}</div>
                    <div class="text-[10px] text-slate-500">${formatBytes(b.size_bytes)} • ${new Date(b.created_at).toLocaleString()}</div>
                  </div>
                  <a href="${API_BASE}/admin/system/backups/${b.filename}/download" download class="p-1.5 hover:bg-slate-700 rounded-lg text-brand-400 transition" title="Download">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  </a>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Audit Log Card -->
          <div class="glass p-6 rounded-2xl border border-dark-border space-y-4">
            <div>
              <h3 class="font-bold text-white text-base">Security & Quota Audit Trail</h3>
              <p class="text-xs text-slate-400">Recorded administrator actions and automated cutoff events</p>
            </div>
            <div class="space-y-2 max-h-56 overflow-y-auto pr-1 font-mono text-[11px]">
              ${state.auditLogs.length === 0 ? `
                <div class="text-xs text-slate-500 py-4 text-center font-sans">No audit logs recorded yet.</div>
              ` : state.auditLogs.map(l => `
                <div class="p-2.5 rounded-lg bg-slate-800/30 border border-slate-800 flex items-start justify-between">
                  <div>
                    <span class="text-brand-400 font-semibold">[${l.action}]</span>
                    <span class="text-slate-300 ml-1">${l.target_entity || ''}</span>
                    <div class="text-[9px] text-slate-500 mt-0.5">By: ${l.actor_id || l.actor_type} • ${new Date(l.created_at).toLocaleTimeString()}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // Modals
  function renderModal() {
    if (!state.activeModal) return '';

    if (state.activeModal === 'createUser') {
      return `
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div class="glass max-w-md w-full p-6 rounded-2xl border border-dark-border space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-white text-base">Create VPN Account</h3>
              <button class="closeModal text-slate-400 hover:text-white">✕</button>
            </div>
            <form id="createUserForm" class="space-y-3.5 text-xs">
              <div>
                <label class="block text-slate-400 mb-1">Username *</label>
                <input type="text" name="username" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500" placeholder="e.g. john_doe">
              </div>
              <div>
                <label class="block text-slate-400 mb-1">Password *</label>
                <input type="password" name="password" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500" placeholder="Min 6 characters">
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-slate-400 mb-1">Traffic Limit (GB)</label>
                  <input type="number" name="traffic_gb" min="0" value="10" class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500" placeholder="0 = Unlimited">
                </div>
                <div>
                  <label class="block text-slate-400 mb-1">Days Valid</label>
                  <input type="number" name="days_valid" min="0" value="30" class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500" placeholder="0 = Unlimited">
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-slate-400 mb-1">Max Devices</label>
                  <input type="number" name="max_connections" min="1" max="10" value="1" class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500">
                </div>
                <div>
                  <label class="block text-slate-400 mb-1">Protocols</label>
                  <select name="allowed_protocols" class="w-full bg-dark-input border border-dark-border rounded-xl px-3 py-2 text-white outline-none focus:border-brand-500">
                    <option value="openvpn_tcp,wireguard">OpenVPN & WireGuard</option>
                    <option value="openvpn_tcp">OpenVPN TCP Only</option>
                    <option value="wireguard">WireGuard Only</option>
                  </select>
                </div>
              </div>
              <div class="pt-2 flex justify-end gap-2">
                <button type="button" class="closeModal px-4 py-2 rounded-xl bg-slate-800 text-slate-300 font-semibold hover:bg-slate-700">Cancel</button>
                <button type="submit" class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold">Create</button>
              </div>
            </form>
          </div>
        </div>
      `;
    }

    if (state.activeModal === 'qrCode' && state.selectedUser) {
      const u = state.selectedUser;
      const setupPayload = JSON.stringify({
        server: window.location.hostname || '127.0.0.1',
        port: window.location.port || 8080,
        username: u.username,
        protocols: u.allowed_protocols
      });

      setTimeout(() => {
        const qrEl = document.getElementById('qrCanvas');
        if (qrEl) {
          qrEl.innerHTML = '';
          new QRCode(qrEl, { text: setupPayload, width: 190, height: 190, colorDark: '#0f172a', colorLight: '#ffffff' });
        }
      }, 50);

      return `
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div class="glass max-w-sm w-full p-6 rounded-2xl border border-dark-border space-y-4 text-center">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-white text-base">Android 1-Tap Setup</h3>
              <button class="closeModal text-slate-400 hover:text-white">✕</button>
            </div>
            <p class="text-xs text-slate-400">Scan this QR code inside the RouterLink Android app to configure server connection instantly</p>
            <div class="p-3 bg-white rounded-xl inline-block shadow-inner mx-auto">
              <div id="qrCanvas"></div>
            </div>
            <div class="text-xs font-mono text-slate-300 bg-slate-800/80 p-2.5 rounded-xl border border-slate-700">
              User: <strong class="text-brand-400">${u.username}</strong>
            </div>
            <button class="closeModal w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-200">Done</button>
          </div>
        </div>
      `;
    }

    if (state.activeModal === 'logs') {
      return `
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div class="glass max-w-2xl w-full p-6 rounded-2xl border border-dark-border space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-white text-base">Daemon Logs: ${state.selectedProtocol}</h3>
              <button class="closeModal text-slate-400 hover:text-white">✕</button>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 h-80 overflow-y-auto font-mono text-xs text-emerald-400 space-y-1">
              ${state.protocolLogs.map(l => `<div>${l}</div>`).join('')}
            </div>
            <div class="flex justify-end">
              <button class="closeModal px-4 py-2 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs hover:bg-slate-700">Close</button>
            </div>
          </div>
        </div>
      `;
    }

    return '';
  }

  function renderLoginView() {
    return `
      <div class="min-h-screen flex items-center justify-center p-4">
        <div class="glass max-w-md w-full p-8 rounded-3xl border border-dark-border space-y-6 shadow-2xl">
          <div class="text-center space-y-2">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center text-white shadow-xl shadow-brand-500/30">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>
            </div>
            <h2 class="text-2xl font-bold text-white tracking-tight">RouterLink Gateway</h2>
            <p class="text-xs text-slate-400">Sign in to manage MikroTik RouterOS 7 VPN services</p>
          </div>
          <form id="loginForm" class="space-y-4 text-xs">
            <div id="loginError" class="hidden p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-medium"></div>
            <div>
              <label class="block text-slate-400 mb-1 font-semibold">Administrator Username</label>
              <input type="text" name="username" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3.5 py-2.5 text-white outline-none focus:border-brand-500 transition" placeholder="admin">
            </div>
            <div>
              <label class="block text-slate-400 mb-1 font-semibold">Password</label>
              <input type="password" name="password" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3.5 py-2.5 text-white outline-none focus:border-brand-500 transition" placeholder="••••••••">
            </div>
            <button type="submit" class="w-full py-3 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-brand-600/30 transition">
              Sign In to WebUI
            </button>
          </form>
        </div>
      </div>
    `;
  }

  function renderSetupView() {
    return `
      <div class="min-h-screen flex items-center justify-center p-4">
        <div class="glass max-w-md w-full p-8 rounded-3xl border border-dark-border space-y-6 shadow-2xl">
          <div class="text-center space-y-2">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-xl shadow-emerald-500/30">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </div>
            <h2 class="text-2xl font-bold text-white tracking-tight">First-Run Setup Wizard</h2>
            <p class="text-xs text-slate-400">Initialize master administrator credentials for RouterLink</p>
          </div>
          <form id="setupForm" class="space-y-4 text-xs">
            <div id="setupError" class="hidden p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-medium"></div>
            <div>
              <label class="block text-slate-400 mb-1 font-semibold">Master Admin Username</label>
              <input type="text" name="username" value="admin" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3.5 py-2.5 text-white outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-slate-400 mb-1 font-semibold">New Password</label>
              <input type="password" name="password" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3.5 py-2.5 text-white outline-none focus:border-brand-500" placeholder="Minimum 8 characters">
            </div>
            <div>
              <label class="block text-slate-400 mb-1 font-semibold">Confirm Password</label>
              <input type="password" name="confirm_password" required class="w-full bg-dark-input border border-dark-border rounded-xl px-3.5 py-2.5 text-white outline-none focus:border-brand-500" placeholder="Repeat password">
            </div>
            <button type="submit" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition">
              Initialize RouterLink Gateway
            </button>
          </form>
        </div>
      </div>
    `;
  }

  // Event Handlers
  function bindSetupEvents() {
    const form = document.getElementById('setupForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const username = fd.get('username');
      const password = fd.get('password');
      const confirm_password = fd.get('confirm_password');
      const errEl = document.getElementById('setupError');

      try {
        const res = await api('/auth/setup', {
          method: 'POST',
          body: JSON.stringify({ username, password, confirm_password })
        });
        state.token = res.access_token;
        state.adminUser = res.username;
        state.setupRequired = false;
        localStorage.setItem('routerlink_token', res.access_token);
        localStorage.setItem('routerlink_username', res.username);
        startPolling();
        render();
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
      }
    });
  }

  function bindLoginEvents() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const username = fd.get('username');
      const password = fd.get('password');
      const errEl = document.getElementById('loginError');

      try {
        const res = await api('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ username, password })
        });
        state.token = res.access_token;
        state.adminUser = res.username;
        localStorage.setItem('routerlink_token', res.access_token);
        localStorage.setItem('routerlink_username', res.username);
        startPolling();
        render();
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
      }
    });
  }

  function bindAppEvents() {
    // Tab Switching
    document.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.currentTab = btn.getAttribute('data-tab');
        fetchDashboardData();
        render();
      });
    });

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', logout);

    // Refresh Sync
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (refreshBtn) refreshBtn.addEventListener('click', fetchDashboardData);

    // Modals
    const createBtn = document.getElementById('openCreateUserModal');
    if (createBtn) {
      createBtn.addEventListener('click', () => {
        state.activeModal = 'createUser';
        render();
      });
    }

    document.querySelectorAll('.closeModal').forEach(btn => {
      btn.addEventListener('click', () => {
        state.activeModal = null;
        render();
      });
    });

    // Create User Form Submit
    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
      createUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(createUserForm);
        const gb = parseInt(fd.get('traffic_gb')) || 0;
        const days = parseInt(fd.get('days_valid')) || 0;
        const payload = {
          username: fd.get('username'),
          password: fd.get('password'),
          traffic_limit_bytes: gb * 1024 * 1024 * 1024,
          expires_at: days > 0 ? new Date(Date.now() + days * 86400000).toISOString() : null,
          max_concurrent_connections: parseInt(fd.get('max_connections')) || 1,
          allowed_protocols: fd.get('allowed_protocols')
        };
        try {
          await api('/admin/users', { method: 'POST', body: JSON.stringify(payload) });
          state.activeModal = null;
          fetchDashboardData();
        } catch (err) {
          alert('Failed to create user: ' + err.message);
        }
      });
    }

    // User Table Actions (QR, Delete)
    document.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const action = btn.getAttribute('data-action');
        const id = parseInt(btn.getAttribute('data-id'));
        const user = state.users.find(u => u.id === id);

        if (action === 'qr') {
          state.selectedUser = user;
          state.activeModal = 'qrCode';
          render();
        } else if (action === 'delete') {
          if (confirm(`Are you sure you want to delete user "${user.username}"?`)) {
            await api(`/admin/users/${id}`, { method: 'DELETE' });
            fetchDashboardData();
          }
        }
      });
    });

    // Terminate Session
    document.querySelectorAll('[data-terminate-session]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-terminate-session');
        if (confirm('Disconnect this client session?')) {
          await api(`/admin/sessions/${id}/terminate`, { method: 'POST' });
          fetchDashboardData();
        }
      });
    });

    // Protocol Actions (Restart, Logs)
    document.querySelectorAll('[data-proto-action]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const action = btn.getAttribute('data-proto-action');
        const name = btn.getAttribute('data-name');
        if (action === 'restart') {
          await api(`/admin/protocols/${name}/action`, {
            method: 'POST',
            body: JSON.stringify({ action: 'restart' })
          });
          alert(`Protocol ${name} restarted.`);
          fetchDashboardData();
        } else if (action === 'logs') {
          const res = await api(`/admin/protocols/${name}/logs`);
          state.selectedProtocol = name;
          state.protocolLogs = res.lines;
          state.activeModal = 'logs';
          render();
        }
      });
    });

    // Create Backup Button
    const backupBtn = document.getElementById('createBackupBtn');
    if (backupBtn) {
      backupBtn.addEventListener('click', async () => {
        await api('/admin/system/backups', { method: 'POST' });
        fetchDashboardData();
      });
    }
  }

  // Start app
  init();
})();

