/* ═══════════════════════════════════════════════════════════════
   Charts.js — Chart.js Analytics (placeholder for future charts)
   Charts are rendered inline within result panels as needed.
   ═══════════════════════════════════════════════════════════════ */

// Chart utility functions
function createBarChart(canvasId, labels, datasets, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    return new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: title, color: '#e2e8f0', font: { family: 'Inter', size: 14 } },
                legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
            },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
                y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
            },
        },
    });
}

function createDoughnutChart(canvasId, labels, data, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const colors = ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4'];

    return new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data, backgroundColor: colors.slice(0, data.length), borderWidth: 0 }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: title, color: '#e2e8f0', font: { family: 'Inter', size: 14 } },
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 }, padding: 12 } },
            },
        },
    });
}
