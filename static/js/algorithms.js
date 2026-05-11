/* ═══════════════════════════════════════════════════════════════
   Algorithms.js — Result Display Functions (V3)
   ═══════════════════════════════════════════════════════════════ */

const ROUTE_COLORS = ['#00d4ff', '#a855f7', '#f59e0b', '#10b981', '#ec4899'];

// ─── MST Results ────────────────────────────────────────────
function displayMSTResults(data) {
    const panel = document.getElementById('results-infrastructure');
    const a = data.analysis || {};
    panel.innerHTML = `
        <div class="result-section">
            <h3>${data.algorithm} — Results</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Total Distance</div><div class="value accent">${data.total_distance} km</div></div>
                <div class="metric-card"><div class="label">Total Edges</div><div class="value">${data.num_edges}</div></div>
                <div class="metric-card"><div class="label">New Roads Needed</div><div class="value warning">${data.num_new_roads}</div></div>
                <div class="metric-card"><div class="label">Construction Cost</div><div class="value danger">${data.total_construction_cost}M EGP</div></div>
            </div>
        </div>
        <div class="result-section">
            <h3>Network Edges</h3>
            <table class="result-table">
                <thead><tr><th>From</th><th>To</th><th>Dist</th><th>Type</th></tr></thead>
                <tbody>
                    ${data.mst_edges.map(e => `<tr>
                        <td>${getNodeName(e.from)}</td>
                        <td>${getNodeName(e.to)}</td>
                        <td>${e.distance} km</td>
                        <td>${e.is_existing ? '<span class="tag tag-green">Existing</span>' : '<span class="tag tag-yellow">New • ' + e.construction_cost + 'M</span>'}</td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
        <div class="result-section">
            <h3>Complexity Analysis</h3>
            <div class="metric-card" style="margin-bottom:8px"><div class="label">Time Complexity</div><div class="value" style="font-size:0.9rem">O(E log E) — Edge sorting dominates</div></div>
            <div class="metric-card"><div class="label">Space Complexity</div><div class="value" style="font-size:0.9rem">O(V) — Union-Find structure</div></div>
        </div>
    `;
}

// ─── Path Results ───────────────────────────────────────────
function displayPathResults(data) {
    const panel = document.getElementById('results-traffic');

    if (data.routes) {
        // K-shortest paths - show each route with its own color
        panel.innerHTML = `
            <div class="result-section">
                <h3>K-Shortest Paths (Yen's Algorithm)</h3>
                <div class="metric-grid">
                    <div class="metric-card"><div class="label">Routes Found</div><div class="value accent">${data.routes.length}</div></div>
                    <div class="metric-card"><div class="label">Time Period</div><div class="value">${data.time_period || 'none'}</div></div>
                </div>
                <div class="routes-list">
                    ${data.routes.map((r, i) => `
                        <div class="route-card" style="--route-color: ${ROUTE_COLORS[i % ROUTE_COLORS.length]}">
                            <div class="route-header">
                                <div class="route-badge" style="background: ${ROUTE_COLORS[i % ROUTE_COLORS.length]}">R${i + 1}</div>
                                <div class="route-meta">
                                    <span class="route-dist">${r.distance} km</span>
                                    ${i === 0 ? '<span class="tag tag-green">Best</span>' : `<span class="tag tag-yellow">+${(r.distance - data.routes[0].distance).toFixed(1)} km</span>`}
                                </div>
                            </div>
                            <div class="path-display">${r.path.map(n => `<span class="path-node">${getNodeName(n)}</span>`).join('<span class="path-arrow">→</span>')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="result-section">
                <h3>Complexity</h3>
                <div class="metric-card"><div class="label">Yen's Algorithm</div><div class="value" style="font-size:0.9rem">O(kV(V+E)log V)</div></div>
            </div>
        `;
    } else {
        panel.innerHTML = `
            <div class="result-section">
                <h3>Dijkstra's Shortest Path</h3>
                <div class="metric-grid">
                    <div class="metric-card"><div class="label">Distance</div><div class="value accent">${data.distance ?? '—'} km</div></div>
                    <div class="metric-card"><div class="label">Nodes Explored</div><div class="value">${data.nodes_explored}</div></div>
                    <div class="metric-card"><div class="label">Path Length</div><div class="value">${data.path.length} nodes</div></div>
                    <div class="metric-card"><div class="label">Time Period</div><div class="value">${data.time_period}</div></div>
                </div>
            </div>
            ${data.path.length ? `
            <div class="result-section">
                <h3>Route</h3>
                <div class="path-display">${data.path.map(n => `<span class="path-node">${getNodeName(n)}</span>`).join('<span class="path-arrow">→</span>')}</div>
            </div>` : '<p style="color:var(--danger)">No path found!</p>'}
            <div class="result-section">
                <h3>Complexity</h3>
                <div class="metric-card"><div class="label">Time Complexity</div><div class="value" style="font-size:0.9rem">O((V+E) log V)</div></div>
            </div>
        `;
    }
}

// ─── Emergency Results ──────────────────────────────────────
function displayEmergencyResults(data) {
    const panel = document.getElementById('results-emergency');
    panel.innerHTML = `
        <div class="result-section">
            <h3>A* Emergency Route</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Distance</div><div class="value danger">${data.distance ?? '—'} km</div></div>
                <div class="metric-card"><div class="label">Nodes Explored</div><div class="value accent">${data.nodes_explored}</div></div>
                <div class="metric-card"><div class="label">Target Hospital</div><div class="value green">${data.target_name || data.target}</div></div>
                <div class="metric-card"><div class="label">Emergency Mode</div><div class="value">${data.emergency_mode ? 'Active' : 'Off'}</div></div>
            </div>
        </div>
        ${data.path.length ? `
        <div class="result-section">
            <h3>Route</h3>
            <div class="path-display">${data.path.map(n => `<span class="path-node">${getNodeName(n)}</span>`).join('<span class="path-arrow">→</span>')}</div>
        </div>` : ''}
        ${data.preemption ? `
        <div class="result-section">
            <h3>Signal Preemption</h3>
            <div class="metric-card" style="margin-bottom:8px"><div class="label">Total Time Saved</div><div class="value green">${data.preemption.total_time_saved_minutes} min</div></div>
            <table class="result-table">
                <thead><tr><th>Intersection</th><th>Queue</th><th>Saved</th></tr></thead>
                <tbody>${data.preemption.preemption_schedule.map(p => `
                    <tr><td>${p.intersection_name}</td><td>${p.vehicles_in_queue} vehicles</td><td>${p.time_saved_seconds}s</td></tr>
                `).join('')}</tbody>
            </table>
        </div>` : ''}
        <div class="result-section">
            <h3>Complexity</h3>
            <div class="metric-card"><div class="label">A* Time Complexity</div><div class="value" style="font-size:0.9rem">O((V+E) log V) with heuristic</div></div>
        </div>
    `;
}

// ─── Transit Results ────────────────────────────────────────
function displayTransitResults(data) {
    const panel = document.getElementById('results-transit');
    const sched = data.schedule_optimization;
    const maint = data.road_maintenance;

    panel.innerHTML = `
        <div class="result-section">
            <h3>Transit Schedule (DP)</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Extra Vehicles</div><div class="value accent">${sched.vehicles_used}</div></div>
                <div class="metric-card"><div class="label">Lines Improved</div><div class="value green">${sched.lines_improved}</div></div>
            </div>
            <table class="result-table">
                <thead><tr><th>Line</th><th>Type</th><th>Cur</th><th>+Extra</th><th>Pass.</th></tr></thead>
                <tbody>${sched.allocation.map(a => `
                    <tr>
                        <td>${a.line_name}</td>
                        <td><span class="tag tag-blue">${a.type}</span></td>
                        <td>${a.current_vehicles}</td>
                        <td style="color:var(--green)">+${a.extra_allocated}</td>
                        <td>${(a.daily_passengers/1000).toFixed(0)}K</td>
                    </tr>
                `).join('')}</tbody>
            </table>
            <div class="metric-card" style="margin-top:8px"><div class="label">Complexity</div><div class="value" style="font-size:0.85rem">${sched.complexity}</div></div>
        </div>
        <div class="result-section">
            <h3>Road Maintenance (Knapsack DP)</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Budget Used</div><div class="value warning">${maint.budget_utilization_pct}%</div></div>
                <div class="metric-card"><div class="label">Roads Selected</div><div class="value accent">${maint.roads_selected}/${maint.total_roads_considered}</div></div>
            </div>
            <table class="result-table">
                <thead><tr><th>Road</th><th>Cond.</th><th>Cost</th><th>Value</th></tr></thead>
                <tbody>${maint.selected_roads.map(r => `
                    <tr>
                        <td>${getNodeName(r.from)} → ${getNodeName(r.to)}</td>
                        <td><span class="tag ${r.current_condition <= 6 ? 'tag-red' : 'tag-green'}">${r.current_condition}/10</span></td>
                        <td>${r.maintenance_cost}M</td>
                        <td>${r.improvement_value}</td>
                    </tr>
                `).join('')}</tbody>
            </table>
            <div class="metric-card" style="margin-top:8px"><div class="label">Complexity</div><div class="value" style="font-size:0.85rem">${maint.complexity}</div></div>
        </div>
    `;
}

// ─── Signal Results ─────────────────────────────────────────
function displaySignalResults(data) {
    const panel = document.getElementById('results-signals');
    panel.innerHTML = `
        <div class="result-section">
            <h3>Greedy Signal Optimization</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Intersections</div><div class="value accent">${data.intersections_optimized}</div></div>
                <div class="metric-card"><div class="label">Total Improvement</div><div class="value green">+${data.total_throughput_improvement} veh/h</div></div>
            </div>
        </div>
        <div class="result-section">
            <h3>Signal Timings</h3>
            <table class="result-table">
                <thead><tr><th>Intersection</th><th>Phases</th><th>Greedy</th><th>Equal</th><th>Gain</th></tr></thead>
                <tbody>${data.signal_timings.map(s => `
                    <tr>
                        <td>${s.intersection_name}</td>
                        <td>${s.num_phases}</td>
                        <td>${s.greedy_throughput}</td>
                        <td>${s.equal_throughput}</td>
                        <td><span class="tag tag-green">+${s.improvement_pct}%</span></td>
                    </tr>
                `).join('')}</tbody>
            </table>
        </div>
        ${data.optimality_analysis ? `
        <div class="result-section">
            <h3>Optimality Analysis</h3>
            <div class="metric-card" style="margin-bottom:8px"><div class="label">Optimal When</div><div class="value" style="font-size:0.8rem;color:var(--green)">${data.optimality_analysis.optimal_cases.map(c => c.scenario).join('; ')}</div></div>
            <div class="metric-card"><div class="label">Suboptimal When</div><div class="value" style="font-size:0.8rem;color:var(--amber)">${data.optimality_analysis.suboptimal_cases.map(c => c.scenario).join('; ')}</div></div>
        </div>` : ''}
    `;
}

// ─── Simulation Results ─────────────────────────────────────
function displaySimulationResults(data) {
    const panel = document.getElementById('results-simulation');
    const summary = data.summary || {};
    const periods = data.time_periods || {};

    // Build period comparison table
    const periodRows = Object.entries(periods).map(([period, pd]) => {
        const icon = period === summary.worst_period ? '🔴' : period === summary.best_period ? '🟢' : '🟡';
        return `<tr>
            <td>${icon} ${period.charAt(0).toUpperCase() + period.slice(1)}</td>
            <td>${(pd.overall_congestion * 100).toFixed(0)}%</td>
            <td>${pd.num_congested}</td>
            <td>${pd.total_flow.toLocaleString()}</td>
        </tr>`;
    }).join('');

    // Worst roads
    const worstRoads = summary.most_congested_roads || [];

    panel.innerHTML = `
        <div class="result-section">
            <h3>🚗 Simulation: ${data.scenario.toUpperCase()}</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">Worst Period</div>
                    <div class="value danger">${summary.worst_period || '—'}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Peak Congestion</div>
                    <div class="value danger">${summary.worst_congestion ? (summary.worst_congestion * 100).toFixed(0) + '%' : '—'}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Best Period</div>
                    <div class="value green">${summary.best_period || '—'}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Min Congestion</div>
                    <div class="value green">${summary.best_congestion ? (summary.best_congestion * 100).toFixed(0) + '%' : '—'}</div>
                </div>
            </div>
        </div>
        <div class="result-section">
            <h3>Period Comparison</h3>
            <table class="result-table">
                <thead><tr><th>Period</th><th>Congestion</th><th>Roads</th><th>Flow</th></tr></thead>
                <tbody>${periodRows}</tbody>
            </table>
        </div>
        ${worstRoads.length > 0 ? `
        <div class="result-section">
            <h3>Most Congested Roads</h3>
            <table class="result-table">
                <thead><tr><th>Road</th><th>Ratio</th><th>Status</th></tr></thead>
                <tbody>${worstRoads.slice(0, 8).map(r => {
                    const tagClass = r.status === 'severe' ? 'tag-red' : 'tag-yellow';
                    return `<tr>
                        <td>${r.from_name} → ${r.to_name}</td>
                        <td>${(r.congestion_ratio * 100).toFixed(0)}%</td>
                        <td><span class="tag ${tagClass}">${r.status}</span></td>
                    </tr>`;
                }).join('')}</tbody>
            </table>
        </div>` : ''}
    `;
}

// ─── Prediction Results ─────────────────────────────────────
function displayPredictionResults(data) {
    const panel = document.getElementById('results-predict');
    if (data.error) {
        panel.innerHTML = `<div class="result-section"><h3>Error</h3><p style="color:var(--danger)">${data.error}</p></div>`;
        return;
    }

    const preds = data.predictions || [];
    const high = preds.filter(p => p.congestion_level === 'High' || p.congestion_level === 'Severe');

    panel.innerHTML = `
        <div class="result-section">
            <h3>ML Predictions</h3>
            <div class="metric-grid">
                <div class="metric-card"><div class="label">Roads Analyzed</div><div class="value accent">${preds.length}</div></div>
                <div class="metric-card"><div class="label">High Congestion</div><div class="value danger">${data.high_congestion_count}</div></div>
            </div>
            ${data.model_metrics ? `
            <div class="metric-grid" style="margin-top:8px">
                <div class="metric-card"><div class="label">Model R2 Score</div><div class="value green">${data.model_metrics.r2_score}</div></div>
                <div class="metric-card"><div class="label">MAE</div><div class="value">${data.model_metrics.mae}</div></div>
            </div>` : ''}
        </div>
        <div class="result-section">
            <h3>Road Predictions</h3>
            <table class="result-table">
                <thead><tr><th>Road</th><th>Flow</th><th>Ratio</th><th>Level</th></tr></thead>
                <tbody>${preds.slice(0, 15).map(p => {
                    const tagClass = p.congestion_level === 'Severe' ? 'tag-red' : p.congestion_level === 'High' ? 'tag-yellow' : p.congestion_level === 'Moderate' ? 'tag-blue' : 'tag-green';
                    return `<tr>
                        <td>${p.road}</td>
                        <td>${p.predicted_flow}</td>
                        <td>${p.congestion_ratio}</td>
                        <td><span class="tag ${tagClass}">${p.congestion_level}</span></td>
                    </tr>`;
                }).join('')}</tbody>
            </table>
        </div>
    `;
}
