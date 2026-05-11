/* ═══════════════════════════════════════════════════════════════
   Map.js — Leaflet Map Integration (V3 — Real Street Maps)
   Supports: Streets / Satellite / Dark tile layers
   ═══════════════════════════════════════════════════════════════ */

const maps = {};
const mapLayers = {};
const CAIRO_CENTER = [30.00, 31.30];
const CAIRO_ZOOM = 11;

// ─── Greater Cairo Bounds (from Project Data) ───────────────
// SW: south of Helwan (lat 29.75), west of 6th Oct (lon 30.85)
// NE: north of Shubra/Airport (lat 30.20), east of NAC (lon 31.90)
const CAIRO_BOUNDS = L.latLngBounds(
    L.latLng(29.75, 30.85),   // Southwest corner
    L.latLng(30.20, 31.90)    // Northeast corner
);

// ─── Tile Layers ────────────────────────────────────────────
const TILE_LAYERS = {
    streets: {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        name: '🗺️ Streets',
    },
    satellite: {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr: '&copy; Esri, Maxar, Earthstar',
        name: '🛰️ Satellite',
    },
    dark: {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr: '&copy; <a href="https://carto.com/">CARTO</a>',
        name: '🌙 Dark',
    },
    detailed: {
        url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attr: '&copy; <a href="https://carto.com/">CARTO</a> &copy; OSM',
        name: '📍 Detailed',
    },
};

// Default tile layer
let currentTileKey = 'streets';

const NODE_COLORS = {
    Residential: '#0077cc',
    Mixed: '#7c3aed',
    Business: '#e67e22',
    Industrial: '#c0392b',
    Government: '#10b981',
    Airport: '#ec4899',
    'Transit Hub': '#f97316',
    Education: '#06b6d4',
    Tourism: '#9b59b6',
    Sports: '#1abc9c',
    Commercial: '#f1c40f',
    Medical: '#e74c3c',
};

// Outline/stroke colors for visibility on light maps
const NODE_STROKE = '#ffffff';

function createMap(containerId) {
    if (maps[containerId]) {
        maps[containerId].invalidateSize();
        return maps[containerId];
    }

    const map = L.map(containerId, {
        center: CAIRO_CENTER,
        zoom: CAIRO_ZOOM,
        minZoom: 10,           // Can't zoom out past Greater Cairo
        maxZoom: 16,           // Max street-level detail
        maxBounds: CAIRO_BOUNDS,        // Lock to Cairo region
        maxBoundsViscosity: 1.0,        // Hard boundary — no dragging outside
        zoomControl: true,
        attributionControl: true,
    });

    // Add all tile layers
    const baseLayers = {};
    let defaultLayer = null;
    for (const [key, cfg] of Object.entries(TILE_LAYERS)) {
        const layer = L.tileLayer(cfg.url, {
            attribution: cfg.attr,
            maxZoom: 16,
            bounds: CAIRO_BOUNDS,   // Only load tiles for Cairo area
        });
        baseLayers[cfg.name] = layer;
        if (key === currentTileKey) {
            defaultLayer = layer;
        }
    }
    if (defaultLayer) defaultLayer.addTo(map);

    // Layer control (top-right)
    L.control.layers(baseLayers, null, { position: 'topright', collapsed: true }).addTo(map);

    maps[containerId] = map;
    mapLayers[containerId] = L.layerGroup().addTo(map);
    return map;
}

function clearMapLayers(containerId) {
    if (mapLayers[containerId]) mapLayers[containerId].clearLayers();
}

function initMapsForTab(tab) {
    const mapIds = {
        infrastructure: ['map-infrastructure'],
        traffic: ['map-traffic'],
        emergency: ['map-emergency'],
        signals: ['map-signals'],
        simulation: ['map-simulation'],
        race: ['map-race-dijkstra', 'map-race-astar'],
        predict: ['map-predict'],
        transit: ['map-transit'],
    };
    const ids = mapIds[tab] || [];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        const map = createMap(id);
        setTimeout(() => map.invalidateSize(), 200);
        drawBaseNetwork(id);
    });
}

function drawBaseNetwork(containerId) {
    if (!networkData) return;
    clearMapLayers(containerId);
    const lg = mapLayers[containerId];

    // Draw existing roads as subtle lines
    networkData.edges.forEach(edge => {
        if (!edge.is_existing) return;
        const fromNode = networkData.nodes.find(n => n.id === edge.from);
        const toNode = networkData.nodes.find(n => n.id === edge.to);
        if (!fromNode || !toNode) return;

        L.polyline(
            [[fromNode.y, fromNode.x], [toNode.y, toNode.x]],
            { color: '#3388ff', weight: 2, opacity: 0.35, dashArray: null }
        ).addTo(lg);
    });

    // Draw potential roads as dashed lines
    networkData.edges.forEach(edge => {
        if (edge.is_existing) return;
        const fromNode = networkData.nodes.find(n => n.id === edge.from);
        const toNode = networkData.nodes.find(n => n.id === edge.to);
        if (!fromNode || !toNode) return;

        L.polyline(
            [[fromNode.y, fromNode.x], [toNode.y, toNode.x]],
            { color: '#f59e0b', weight: 1.5, opacity: 0.2, dashArray: '6 4' }
        ).addTo(lg);
    });

    // Draw nodes
    networkData.nodes.forEach(node => {
        const color = NODE_COLORS[node.type] || '#64748b';
        const isFacility = String(node.id).startsWith('F');
        const radius = isFacility ? 7 : Math.max(5, Math.min(10, node.population / 80000));

        L.circleMarker([node.y, node.x], {
            radius: radius,
            fillColor: color,
            color: NODE_STROKE,
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85,
        }).bindTooltip(
            `<strong>${node.name}</strong><br>Type: ${node.type}${node.population ? '<br>Pop: ' + node.population.toLocaleString() : ''}`,
            { className: 'map-tooltip' }
        ).addTo(lg);

        // Permanent label
        const shortName = node.name
            .replace('Cairo International ', '')
            .replace('Cairo ', '')
            .replace('International ', '');
        L.tooltip({
            permanent: true,
            direction: 'right',
            offset: [10, 0],
            className: 'node-label',
        }).setContent(shortName)
         .setLatLng([node.y, node.x])
         .addTo(lg);
    });
}

// ─── Offset polyline for multiple routes ────────────────────
function offsetCoords(coords, offsetPx, mapObj) {
    if (!mapObj || coords.length < 2 || offsetPx === 0) return coords;
    const result = [];
    for (let i = 0; i < coords.length; i++) {
        if (i === 0) {
            const p1 = mapObj.latLngToLayerPoint(L.latLng(coords[0]));
            const p2 = mapObj.latLngToLayerPoint(L.latLng(coords[1]));
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const len = Math.sqrt(dx * dx + dy * dy) || 1;
            const nx = -dy / len * offsetPx;
            const ny = dx / len * offsetPx;
            const op = L.point(p1.x + nx, p1.y + ny);
            result.push(mapObj.layerPointToLatLng(op));
        } else if (i === coords.length - 1) {
            const p1 = mapObj.latLngToLayerPoint(L.latLng(coords[i - 1]));
            const p2 = mapObj.latLngToLayerPoint(L.latLng(coords[i]));
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const len = Math.sqrt(dx * dx + dy * dy) || 1;
            const nx = -dy / len * offsetPx;
            const ny = dx / len * offsetPx;
            const op = L.point(p2.x + nx, p2.y + ny);
            result.push(mapObj.layerPointToLatLng(op));
        } else {
            const p0 = mapObj.latLngToLayerPoint(L.latLng(coords[i - 1]));
            const p1 = mapObj.latLngToLayerPoint(L.latLng(coords[i]));
            const p2 = mapObj.latLngToLayerPoint(L.latLng(coords[i + 1]));
            const dx1 = p1.x - p0.x, dy1 = p1.y - p0.y;
            const dx2 = p2.x - p1.x, dy2 = p2.y - p1.y;
            const len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1) || 1;
            const len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2) || 1;
            const nx = (-dy1 / len1 + -dy2 / len2) / 2 * offsetPx;
            const ny = (dx1 / len1 + dx2 / len2) / 2 * offsetPx;
            const op = L.point(p1.x + nx, p1.y + ny);
            result.push(mapObj.layerPointToLatLng(op));
        }
    }
    return result;
}

// ─── Draw MST ───────────────────────────────────────────────
function drawMSTOnMap(data) {
    const id = 'map-infrastructure';
    drawBaseNetwork(id);
    const lg = mapLayers[id];

    data.mst_edges.forEach((edge, i) => {
        const from = networkData.nodes.find(n => n.id === edge.from);
        const to = networkData.nodes.find(n => n.id === edge.to);
        if (!from || !to) return;

        const color = edge.is_existing ? '#10b981' : '#f59e0b';
        const dash = edge.is_existing ? null : '10 5';

        // Glow
        L.polyline(
            [[from.y, from.x], [to.y, to.x]],
            { color: color, weight: 8, opacity: 0.2 }
        ).addTo(lg);

        // Line
        L.polyline(
            [[from.y, from.x], [to.y, to.x]],
            { color: color, weight: 3.5, opacity: 0.9, dashArray: dash }
        ).bindTooltip(
            `${getNodeName(edge.from)} → ${getNodeName(edge.to)}<br>Distance: ${edge.distance} km${edge.is_existing ? '' : '<br>🆕 New Road • Cost: ' + edge.construction_cost + 'M EGP'}`
        ).addTo(lg);
    });
}

// ─── Draw Path (with offset for multiple routes) ────────────
function drawPathOnMap(data) {
    const id = 'map-traffic';
    drawBaseNetwork(id);
    const lg = mapLayers[id];
    const mapObj = maps[id];
    const ROUTE_COLORS_MAP = ['#e74c3c', '#3498db', '#f39c12', '#2ecc71', '#9b59b6'];
    const offsets = [0, 6, -6, 12, -12];

    const paths = data.routes || [{ path: data.path, distance: data.distance }];
    const allCoords = [];

    paths.forEach((route, ri) => {
        const path = route.path;
        if (!path || path.length < 2) return;

        const coords = path.map(nid => {
            const n = networkData.nodes.find(nd => nd.id === nid);
            return n ? [n.y, n.x] : null;
        }).filter(Boolean);

        allCoords.push(...coords);

        const drawCoords = paths.length > 1 ? offsetCoords(coords, offsets[ri] || 0, mapObj) : coords;
        const color = ROUTE_COLORS_MAP[ri % ROUTE_COLORS_MAP.length];

        // Route glow
        L.polyline(drawCoords, {
            color: color,
            weight: ri === 0 ? 10 : 7,
            opacity: 0.2,
            lineCap: 'round', lineJoin: 'round',
        }).addTo(lg);

        // Route line
        L.polyline(drawCoords, {
            color: color,
            weight: ri === 0 ? 5 : 3.5,
            opacity: ri === 0 ? 1 : 0.85,
            lineCap: 'round', lineJoin: 'round',
            dashArray: ri > 0 ? '12 6' : null,
        }).bindTooltip(`<strong>Route ${ri + 1}</strong><br>Distance: ${route.distance} km<br>Path: ${path.map(n => getNodeName(n)).join(' → ')}`).addTo(lg);
    });

    // Highlight start/end
    if (paths.length > 0 && paths[0].path && paths[0].path.length >= 2) {
        const firstPath = paths[0].path;
        const startN = networkData.nodes.find(n => n.id === firstPath[0]);
        const endN = networkData.nodes.find(n => n.id === firstPath[firstPath.length - 1]);

        if (startN) {
            L.circleMarker([startN.y, startN.x], {
                radius: 14, fillColor: '#2ecc71', color: '#fff', weight: 3, fillOpacity: 0.9
            }).bindTooltip('<strong>📍 START</strong><br>' + startN.name).addTo(lg);
        }
        if (endN) {
            L.circleMarker([endN.y, endN.x], {
                radius: 14, fillColor: '#e74c3c', color: '#fff', weight: 3, fillOpacity: 0.9
            }).bindTooltip('<strong>🏁 END</strong><br>' + endN.name).addTo(lg);
        }
    }

    if (allCoords.length > 0) {
        const bounds = L.latLngBounds(allCoords);
        mapObj.fitBounds(bounds, { padding: [80, 80], maxZoom: 13 });
    }
}

// ─── Draw Emergency ─────────────────────────────────────────
function drawEmergencyOnMap(data) {
    const id = 'map-emergency';
    drawBaseNetwork(id);
    const lg = mapLayers[id];
    const mapObj = maps[id];

    if (!data.path || data.path.length < 2) return;
    const coords = data.path.map(nid => {
        const n = networkData.nodes.find(nd => nd.id === nid);
        return n ? [n.y, n.x] : null;
    }).filter(Boolean);

    // Pulsing emergency route layers
    L.polyline(coords, { color: '#e74c3c', weight: 10, opacity: 0.2 }).addTo(lg);
    L.polyline(coords, { color: '#e74c3c', weight: 5, opacity: 1, lineCap: 'round' }).addTo(lg);
    L.polyline(coords, { color: '#fbbf24', weight: 2, opacity: 0.8, dashArray: '8 12' }).addTo(lg);

    // Start marker (ambulance)
    const startN = networkData.nodes.find(n => n.id === data.path[0]);
    const endN = networkData.nodes.find(n => n.id === data.path[data.path.length - 1]);
    if (startN) L.circleMarker([startN.y, startN.x], { radius: 16, fillColor: '#f59e0b', color: '#fff', weight: 3, fillOpacity: 0.9 }).bindTooltip('🚑 Emergency Origin: ' + startN.name).addTo(lg);
    if (endN) L.circleMarker([endN.y, endN.x], { radius: 16, fillColor: '#e74c3c', color: '#fff', weight: 3, fillOpacity: 0.9 }).bindTooltip('🏥 Hospital: ' + endN.name).addTo(lg);

    const bounds = L.latLngBounds(coords);
    mapObj.fitBounds(bounds, { padding: [80, 80], maxZoom: 13 });
}

// ─── Draw Signals ───────────────────────────────────────────
function drawSignalsOnMap(data) {
    const id = 'map-signals';
    drawBaseNetwork(id);
    const lg = mapLayers[id];

    data.signal_timings.forEach(sig => {
        const n = networkData.nodes.find(nd => nd.id === sig.intersection);
        if (!n) return;
        const imp = sig.improvement_pct;
        const color = imp > 10 ? '#27ae60' : imp > 5 ? '#f39c12' : '#7f8c8d';
        L.circleMarker([n.y, n.x], {
            radius: 9 + imp / 3,
            fillColor: color,
            color: '#fff',
            weight: 2,
            fillOpacity: 0.8,
        }).bindTooltip(`<strong>🚦 ${sig.intersection_name}</strong><br>Improvement: ${imp}%<br>Phases: ${sig.num_phases}`).addTo(lg);
    });
}

// ─── Draw Predictions ───────────────────────────────────────
function drawPredictionsOnMap(data) {
    const id = 'map-predict';
    drawBaseNetwork(id);
    const lg = mapLayers[id];

    if (!data.predictions) return;
    data.predictions.forEach(pred => {
        const parts = pred.road.split('-');
        const from = networkData.nodes.find(n => n.id === parts[0]);
        const to = networkData.nodes.find(n => n.id === parts[1]);
        if (!from || !to) return;

        const ratio = pred.congestion_ratio;
        const color = ratio > 1.0 ? '#e74c3c' : ratio > 0.8 ? '#f39c12' : ratio > 0.5 ? '#f1c40f' : '#27ae60';
        const weight = 3 + ratio * 3;

        L.polyline([[from.y, from.x], [to.y, to.x]], {
            color: color, weight: weight, opacity: 0.85,
        }).bindTooltip(`<strong>${pred.road}</strong><br>Flow: ${pred.predicted_flow} veh/h<br>Congestion: ${pred.congestion_level}`).addTo(lg);
    });
}

// ─── Draw Simulation Congestion ─────────────────────────────
function drawSimulationOnMap(data, period) {
    const id = 'map-simulation';
    drawBaseNetwork(id);
    const lg = mapLayers[id];

    const periodData = data.time_periods[period];
    if (!periodData || !periodData.congested_roads) return;

    // Draw ALL roads with congestion coloring for this period
    networkData.edges.forEach(edge => {
        if (!edge.is_existing) return;
        const fromNode = networkData.nodes.find(n => n.id === edge.from);
        const toNode = networkData.nodes.find(n => n.id === edge.to);
        if (!fromNode || !toNode) return;

        const congested = periodData.congested_roads.find(
            r => r.road === `${edge.from}-${edge.to}` || r.road === `${edge.to}-${edge.from}`
        );

        if (congested) {
            const ratio = congested.congestion_ratio;
            const color = ratio > 1.0 ? '#e74c3c' : ratio > 0.9 ? '#e67e22' : '#f39c12';
            const weight = 3 + ratio * 3;

            // Glow
            L.polyline([[fromNode.y, fromNode.x], [toNode.y, toNode.x]], {
                color: color, weight: weight + 4, opacity: 0.15,
            }).addTo(lg);

            // Line
            L.polyline([[fromNode.y, fromNode.x], [toNode.y, toNode.x]], {
                color: color, weight: weight, opacity: 0.9,
            }).bindTooltip(
                `<strong>${congested.from_name} → ${congested.to_name}</strong><br>` +
                `Flow: ${congested.flow} veh/h<br>Capacity: ${congested.capacity}<br>` +
                `Congestion: ${(congested.congestion_ratio * 100).toFixed(0)}%<br>` +
                `Status: <strong>${congested.status.toUpperCase()}</strong>`
            ).addTo(lg);
        }
    });
}

// ─── Draw Transit Routes (Metro + Bus) ──────────────────────
function drawTransitOnMap(data) {
    const id = 'map-transit';
    const el = document.getElementById(id);
    if (!el) return;
    const map = createMap(id);
    setTimeout(() => map.invalidateSize(), 200);
    drawBaseNetwork(id);
    const lg = mapLayers[id];

    // Metro line colors
    const METRO_COLORS = {
        'M1': '#e74c3c',   // Red line
        'M2': '#f39c12',   // Orange line
        'M3': '#2ecc71',   // Green line
    };

    // Draw metro lines
    const metroLines = [
        { id: 'M1', name: 'Line 1 (Helwan-New Marg)', stations: ['12', '1', '3', 'F2', '11'] },
        { id: 'M2', name: 'Line 2 (Shubra-Giza)',     stations: ['11', 'F2', '3', '10', '8'] },
        { id: 'M3', name: 'Line 3 (Airport-Imbaba)',   stations: ['F1', '5', '2', '3', '9'] },
    ];

    metroLines.forEach(line => {
        const color = METRO_COLORS[line.id] || '#888';
        const coords = line.stations.map(sid => {
            const n = networkData.nodes.find(nd => nd.id === sid);
            return n ? [n.y, n.x] : null;
        }).filter(Boolean);

        if (coords.length < 2) return;

        // Glow
        L.polyline(coords, { color: color, weight: 10, opacity: 0.15 }).addTo(lg);
        // Line
        L.polyline(coords, { color: color, weight: 5, opacity: 0.9, lineCap: 'round' })
            .bindTooltip(`<strong>🚇 ${line.name}</strong>`)
            .addTo(lg);

        // Station markers
        line.stations.forEach((sid, idx) => {
            const n = networkData.nodes.find(nd => nd.id === sid);
            if (!n) return;
            L.circleMarker([n.y, n.x], {
                radius: 8,
                fillColor: '#fff',
                color: color,
                weight: 3,
                fillOpacity: 0.95,
            }).bindTooltip(`<strong>🚇 ${n.name}</strong><br>${line.id}: ${line.name}<br>Station ${idx + 1} of ${line.stations.length}`).addTo(lg);
        });
    });

    // Draw bus routes (lighter)
    const BUS_COLORS = ['#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6', '#2c3e50', '#16a085', '#d35400', '#8e44ad', '#c0392b'];
    const busRoutes = [
        { id: 'B1',  stops: ['1', '3', '6', '9'] },
        { id: 'B2',  stops: ['7', '15', '8', '10', '3'] },
        { id: 'B3',  stops: ['2', '5', 'F1'] },
        { id: 'B4',  stops: ['4', '14', '2', '3'] },
        { id: 'B5',  stops: ['8', '12', '1'] },
        { id: 'B6',  stops: ['11', '5', '2'] },
        { id: 'B7',  stops: ['13', '4', '14'] },
        { id: 'B8',  stops: ['F7', '15', '7'] },
        { id: 'B9',  stops: ['1', '8', '10', '9', '6'] },
        { id: 'B10', stops: ['F8', '4', '2', '5'] },
    ];

    busRoutes.forEach((route, ri) => {
        const color = BUS_COLORS[ri % BUS_COLORS.length];
        const coords = route.stops.map(sid => {
            const n = networkData.nodes.find(nd => nd.id === sid);
            return n ? [n.y, n.x] : null;
        }).filter(Boolean);

        if (coords.length < 2) return;

        L.polyline(coords, {
            color: color, weight: 2.5, opacity: 0.5, dashArray: '8 5',
        }).bindTooltip(`<strong>🚌 ${route.id}</strong><br>Stops: ${route.stops.map(s => getNodeName(s)).join(' → ')}`).addTo(lg);
    });
}
