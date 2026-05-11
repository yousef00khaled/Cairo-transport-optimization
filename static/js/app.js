/* ═══════════════════════════════════════════════════════════════
   App.js — Main Controller (V3)
   ═══════════════════════════════════════════════════════════════ */

let networkData = null;
let lastSimData = null;  // Cache simulation results
const state = { currentTab: 'dashboard' };

document.addEventListener('DOMContentLoaded', async () => {
    setupNavigation();
    await loadNetworkData();
    populateDropdowns();
    setupButtonHandlers();
});

// ─── Navigation ─────────────────────────────────────────────
function setupNavigation() {
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tab) {
    state.currentTab = tab;
    document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
    const navBtn = document.querySelector(`[data-tab="${tab}"]`);
    if (navBtn) navBtn.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const tabEl = document.getElementById(`tab-${tab}`);
    if (tabEl) tabEl.classList.add('active');
    setTimeout(() => initMapsForTab(tab), 150);
}

// ─── Load Data ──────────────────────────────────────────────
async function loadNetworkData() {
    try {
        const res = await fetch('/api/data');
        networkData = await res.json();
        showToast('Network data loaded', 'success');
    } catch (e) {
        showToast('Failed to load data', 'error');
    }
}

// ─── Populate Dropdowns ─────────────────────────────────────
function populateDropdowns() {
    if (!networkData) return;
    const ids = ['dijkstra-source','dijkstra-target','emergency-source','race-source','race-target'];
    const nodes = networkData.nodes.sort((a, b) => a.name.localeCompare(b.name));
    ids.forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = '';
        nodes.forEach(n => {
            const opt = document.createElement('option');
            opt.value = n.id;
            opt.textContent = `${n.name} (${n.id})`;
            sel.appendChild(opt);
        });
    });
    setDefault('dijkstra-source','1');
    setDefault('dijkstra-target','4');
    setDefault('emergency-source','7');
    setDefault('race-source','7');
    setDefault('race-target','F9');
}

function setDefault(id, val) { const el = document.getElementById(id); if (el) el.value = val; }

// ─── Button Handlers ────────────────────────────────────────
function setupButtonHandlers() {
    document.getElementById('btn-compute-mst').addEventListener('click', computeMST);
    document.getElementById('btn-find-path').addEventListener('click', findPath);
    document.getElementById('btn-emergency-route').addEventListener('click', emergencyRoute);
    document.getElementById('btn-optimize-transit').addEventListener('click', optimizeTransit);
    document.getElementById('btn-optimize-signals').addEventListener('click', optimizeSignals);
    document.getElementById('btn-start-race').addEventListener('click', startRace);
    document.getElementById('btn-predict').addEventListener('click', predictTraffic);
    document.getElementById('btn-simulate').addEventListener('click', simulateTraffic);
    document.getElementById('btn-show-transit-map').addEventListener('click', () => drawTransitOnMap());

    // Update simulation map when period changes
    document.getElementById('sim-period').addEventListener('change', () => {
        if (lastSimData) {
            const period = document.getElementById('sim-period').value;
            drawSimulationOnMap(lastSimData, period);
        }
    });
}

// ─── Generic API call wrapper ───────────────────────────────
async function apiCall(btn, url, body, onSuccess, label) {
    const origHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        onSuccess(data);
        showToast(label + ' complete', 'success');
    } catch (e) {
        showToast(label + ' failed', 'error');
    }
    btn.disabled = false;
    btn.innerHTML = origHTML;
}

async function computeMST() {
    const btn = document.getElementById('btn-compute-mst');
    await apiCall(btn, '/api/mst', {
        algorithm: document.getElementById('mst-algorithm').value,
        prioritize_critical: document.getElementById('mst-prioritize').checked,
    }, (data) => { displayMSTResults(data); drawMSTOnMap(data); }, 'MST');
}

async function findPath() {
    const btn = document.getElementById('btn-find-path');
    await apiCall(btn, '/api/shortest-path', {
        source: document.getElementById('dijkstra-source').value,
        target: document.getElementById('dijkstra-target').value,
        time_period: document.getElementById('dijkstra-time').value || null,
        k_paths: parseInt(document.getElementById('dijkstra-k').value),
    }, (data) => { displayPathResults(data); drawPathOnMap(data); }, 'Path');
}

async function emergencyRoute() {
    const btn = document.getElementById('btn-emergency-route');
    await apiCall(btn, '/api/emergency-route', {
        source: document.getElementById('emergency-source').value,
        target: document.getElementById('emergency-target').value || null,
        time_period: document.getElementById('emergency-time').value || null,
    }, (data) => { displayEmergencyResults(data); drawEmergencyOnMap(data); }, 'Emergency');
}

async function optimizeTransit() {
    const btn = document.getElementById('btn-optimize-transit');
    await apiCall(btn, '/api/transit-optimize', {
        extra_vehicles: parseInt(document.getElementById('dp-vehicles').value),
        budget: parseInt(document.getElementById('dp-budget').value),
    }, (data) => { displayTransitResults(data); }, 'Transit');
}

async function optimizeSignals() {
    const btn = document.getElementById('btn-optimize-signals');
    await apiCall(btn, '/api/signal-optimize', {
        time_period: document.getElementById('greedy-time').value,
        cycle_length: parseInt(document.getElementById('greedy-cycle').value),
    }, (data) => { displaySignalResults(data); drawSignalsOnMap(data); }, 'Signals');
}

async function simulateTraffic() {
    const btn = document.getElementById('btn-simulate');
    const scenario = document.getElementById('sim-scenario').value;
    await apiCall(btn, '/api/simulate', {
        scenario: scenario,
    }, (data) => {
        lastSimData = data;
        displaySimulationResults(data);
        const period = document.getElementById('sim-period').value;
        drawSimulationOnMap(data, period);
    }, 'Simulation');
}

async function startRace() {
    const btn = document.getElementById('btn-start-race');
    const origHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';
    try {
        const res = await fetch('/api/race', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: document.getElementById('race-source').value,
                target: document.getElementById('race-target').value,
            }),
        });
        const data = await res.json();
        const speed = parseInt(document.getElementById('race-speed').value);
        await animateRace(data, speed);
    } catch (e) { showToast('Race failed', 'error'); }
    btn.disabled = false;
    btn.innerHTML = origHTML;
}

async function predictTraffic() {
    const btn = document.getElementById('btn-predict');
    await apiCall(btn, '/api/traffic-predict', {
        time_period: document.getElementById('ml-time').value,
        day_of_week: parseInt(document.getElementById('ml-day').value),
    }, (data) => { displayPredictionResults(data); drawPredictionsOnMap(data); }, 'Prediction');
}

// ─── Toast ──────────────────────────────────────────────────
function showToast(msg, type='info') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    const icons = {success:'✓',error:'✕',info:'ℹ'};
    t.innerHTML = `<strong>${icons[type]||''}</strong> ${msg}`;
    c.appendChild(t);
    setTimeout(() => { t.style.opacity='0'; setTimeout(() => t.remove(), 300); }, 3000);
}

function getNodeName(id) {
    if (!networkData) return id;
    const n = networkData.nodes.find(n => n.id === id);
    return n ? n.name : id;
}
