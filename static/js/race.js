/* ═══════════════════════════════════════════════════════════════
   Race.js — Dijkstra vs A* Race Animation
   ═══════════════════════════════════════════════════════════════ */

async function animateRace(data, speed = 200) {
    const dijkstraSteps = data.dijkstra.steps.filter(s => s.action === 'visit');
    const astarSteps = data.astar.steps.filter(s => s.action === 'visit');

    // Reset maps
    drawBaseNetwork('map-race-dijkstra');
    drawBaseNetwork('map-race-astar');

    // Reset counters
    document.getElementById('dijkstra-nodes').textContent = '0';
    document.getElementById('dijkstra-dist').textContent = '—';
    document.getElementById('astar-nodes').textContent = '0';
    document.getElementById('astar-dist').textContent = '—';
    document.getElementById('race-result').style.display = 'none';

    const maxSteps = Math.max(dijkstraSteps.length, astarSteps.length);
    let dijkDone = false, astarDone = false;

    for (let i = 0; i < maxSteps; i++) {
        // Dijkstra step
        if (i < dijkstraSteps.length) {
            const step = dijkstraSteps[i];
            addExploredNode('map-race-dijkstra', step.node, '#00d4ff');
            document.getElementById('dijkstra-nodes').textContent = step.nodes_explored;
            if (i === dijkstraSteps.length - 1) {
                dijkDone = true;
                document.getElementById('dijkstra-dist').textContent = data.dijkstra.distance + ' km';
                drawRacePath('map-race-dijkstra', data.dijkstra.path, '#00d4ff');
            }
        }

        // A* step
        if (i < astarSteps.length) {
            const step = astarSteps[i];
            addExploredNode('map-race-astar', step.node, '#7c3aed');
            document.getElementById('astar-nodes').textContent = step.nodes_explored;
            if (i === astarSteps.length - 1) {
                astarDone = true;
                document.getElementById('astar-dist').textContent = data.astar.distance + ' km';
                drawRacePath('map-race-astar', data.astar.path, '#7c3aed');
            }
        }

        await sleep(speed);
    }

    // Show result
    const comp = data.comparison;
    const winner = comp.astar_nodes_explored <= comp.dijkstra_nodes_explored ? 'A*' : 'Dijkstra';
    const resultEl = document.getElementById('race-result');
    resultEl.style.display = 'block';
    document.getElementById('race-winner').innerHTML =
        `🏆 <strong>${winner}</strong> wins! A* explored <strong>${comp.efficiency_gain_pct}%</strong> fewer nodes. ` +
        `(${comp.astar_nodes_explored} vs ${comp.dijkstra_nodes_explored})` +
        `${comp.same_distance ? ' — Same optimal distance!' : ''}`;
}

function addExploredNode(mapId, nodeId, color) {
    const lg = mapLayers[mapId];
    if (!lg || !networkData) return;
    const node = networkData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    L.circleMarker([node.y, node.x], {
        radius: 7,
        fillColor: color,
        color: color,
        weight: 2,
        fillOpacity: 0.4,
        opacity: 0.8,
    }).addTo(lg);
}

function drawRacePath(mapId, path, color) {
    const lg = mapLayers[mapId];
    if (!lg || !networkData || !path || path.length < 2) return;

    const coords = path.map(nid => {
        const n = networkData.nodes.find(nd => nd.id === nid);
        return n ? [n.y, n.x] : null;
    }).filter(Boolean);

    L.polyline(coords, { color: color, weight: 4, opacity: 1 }).addTo(lg);

    // Start/End markers
    const startN = networkData.nodes.find(n => n.id === path[0]);
    const endN = networkData.nodes.find(n => n.id === path[path.length - 1]);
    if (startN) L.circleMarker([startN.y, startN.x], { radius: 10, fillColor: '#10b981', color: '#10b981', fillOpacity: 0.9 }).addTo(lg);
    if (endN) L.circleMarker([endN.y, endN.x], { radius: 10, fillColor: '#ef4444', color: '#ef4444', fillOpacity: 0.9 }).addTo(lg);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
