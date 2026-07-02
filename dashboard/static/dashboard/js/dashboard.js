/**
 * InfraTech Enterprise Dashboard — dashboard.js
 * Extracted from home.html inline <script> block.
 *
 * Depends on:
 *   - Chart.js (loaded before this file in the HTML)
 *   - vm_manager.js (loaded after this file)
 *   - Django json_script tags: #chart-labels, #cpu-data, #ram-data, #disk-data
 */

/* ===================================================================
   NOTE EDITING
   =================================================================== */

/**
 * Show the inline edit form for a metric note row.
 * @param {string} id - The metric record primary key.
 */
function showEditForm(id) {
    document.getElementById('note-display-' + id).style.display = 'none';
    const form = document.getElementById('note-form-' + id);
    form.style.display = 'flex';
    form.querySelector('.note-input').focus();
}

/**
 * Hide the inline edit form and restore the display view.
 * @param {string} id - The metric record primary key.
 */
function hideEditForm(id) {
    document.getElementById('note-display-' + id).style.display = 'flex';
    document.getElementById('note-form-' + id).style.display = 'none';
}

/* ===================================================================
   TABLE FILTER
   =================================================================== */

/**
 * Live-filter the metric capture history table rows.
 * Called on keyup from the search input in the template.
 */
function filterTable() {
    const filter = document.getElementById('table-search-input').value.toLowerCase();
    const rows = document.querySelectorAll('#metrics-table-body tr');
    rows.forEach(tr => {
        tr.style.display = tr.textContent.toLowerCase().includes(filter) ? '' : 'none';
    });
}

/* ===================================================================
   CHART DATA  (parsed from Django json_script elements)
   =================================================================== */

const labels   = JSON.parse(document.getElementById('chart-labels').textContent);
const cpuData  = JSON.parse(document.getElementById('cpu-data').textContent);
const ramData  = JSON.parse(document.getElementById('ram-data').textContent);
const diskData = JSON.parse(document.getElementById('disk-data').textContent);

/* Shared scale/interaction defaults for main charts */
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', font: { size: 9 }, maxRotation: 0, autoSkipPadding: 20 }
        },
        y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', font: { size: 9 } },
            min: 0,
            max: 100
        }
    },
    interaction: { intersect: false, mode: 'index' },
    elements: { point: { radius: 0, hoverRadius: 3 } }
};

/* ===================================================================
   RESOURCE UTILIZATION CHART  (multi-line)
   =================================================================== */

new Chart(document.getElementById('resourceChart'), {
    type: 'line',
    data: {
        labels: labels,
        datasets: [
            {
                label: 'CPU (%)',
                data: cpuData,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59,130,246,0.05)',
                fill: true,
                tension: 0.3,
                borderWidth: 1.5
            },
            {
                label: 'Memory (%)',
                data: ramData,
                borderColor: '#10B981',
                backgroundColor: 'transparent',
                fill: false,
                tension: 0.3,
                borderWidth: 1.5
            },
            {
                label: 'Disk (%)',
                data: diskData,
                borderColor: '#F59E0B',
                backgroundColor: 'transparent',
                fill: false,
                tension: 0.3,
                borderWidth: 1.5
            },
            {
                label: 'Network (Mbps)',
                data: cpuData.map(() => Math.random() * 5),
                borderColor: '#8B5CF6',
                backgroundColor: 'transparent',
                fill: false,
                tension: 0.3,
                borderWidth: 1,
                borderDash: [3, 3]
            }
        ]
    },
    options: chartDefaults
});

/* ===================================================================
   KPI SPARKLINES
   =================================================================== */

/**
 * Render a mini sparkline chart into a canvas element.
 * @param {string} canvasId - Target canvas element ID.
 * @param {number[]} data    - Data array (uses last 15 points).
 * @param {string} color     - CSS hex colour for the line.
 */
function makeSparkline(canvasId, data, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data.length) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                data: data.slice(-15),
                borderColor: color,
                backgroundColor: color + '15',
                fill: true,
                tension: 0.4,
                borderWidth: 1.5,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            elements: { point: { radius: 0 } }
        }
    });
}

makeSparkline('sparkCpu',  cpuData,  '#3B82F6');
makeSparkline('sparkRam',  ramData,  '#10B981');
makeSparkline('sparkDisk', diskData, '#F59E0B');

/* ===================================================================
   SYSTEM OVERVIEW — DONUT CHART
   =================================================================== */

const donutCtx = document.getElementById('donutChart');
if (donutCtx) {
    new Chart(donutCtx, {
        type: 'doughnut',
        data: {
            labels: ['Offline', 'Online', 'Warning'],
            datasets: [{
                data: [1, 2, 1],
                backgroundColor: ['#EF4444', '#10B981', '#F59E0B'],
                borderWidth: 0,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '70%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

/* ===================================================================
   PLATFORM STATUS SYNC
   Syncs the dashboard UI (header dot, donut label, VM table row,
   and system overview status rows) with the live VM state polled
   by vm_manager.js via the hidden #vm-status-text element.
   =================================================================== */

/**
 * Update all status-related elements based on current VM state.
 * @param {string} vmStatus      - 'Running' | 'Starting' | 'Stopping' | 'Restarting' | 'Stopped' | 'Unknown'
 * @param {string} vmName        - Display name of the VM.
 * @param {string} resourceGroup - Azure resource group name.
 */
function updateDashboardStatus(vmStatus, vmName, resourceGroup) {
    const dot        = document.getElementById('platform-dot');
    const text       = document.getElementById('platform-status-text');
    const donutLabel = document.getElementById('donut-status');
    const stVmDot    = document.getElementById('st-vm-dot');
    const stVmVal    = document.getElementById('st-vm-val');

    // Reveal and populate the VM table row when a VM name is known
    if (vmName) {
        const vmRow   = document.getElementById('vm-row');
        const vmEmpty = document.getElementById('vm-empty-row');
        vmRow.style.display   = '';
        vmEmpty.style.display = 'none';
        document.getElementById('vm-row-name').textContent = vmName;
        document.getElementById('vm-row-rg').textContent   = resourceGroup || '—';
        document.getElementById('kpi-vm-count').textContent = '1';
    }

    // Reset badge class before applying new one
    const vmRowStatus = document.getElementById('vm-row-status');
    vmRowStatus.className = 'badge';

    // Reset status dot class
    dot.className = 'status-dot';

    if (vmStatus === 'Running') {
        dot.classList.add('healthy');
        text.textContent         = 'System Status: Healthy';
        donutLabel.textContent   = 'Healthy';
        donutLabel.className     = 'value healthy';
        vmRowStatus.classList.add('badge-success');
        vmRowStatus.innerHTML    = '<span class="bdot"></span> Running';
        stVmDot.style.background = 'var(--success)';
        stVmVal.textContent      = 'Online';
        stVmVal.className        = 'status-value online';
    } else if (['Starting', 'Stopping', 'Restarting'].includes(vmStatus)) {
        dot.classList.add('warning');
        text.textContent         = 'System Status: ' + vmStatus;
        donutLabel.textContent   = vmStatus;
        donutLabel.className     = 'value warning';
        vmRowStatus.classList.add('badge-warning');
        vmRowStatus.innerHTML    = '<span class="bdot"></span> ' + vmStatus;
        stVmDot.style.background = 'var(--warning)';
        stVmVal.textContent      = vmStatus;
        stVmVal.className        = 'status-value warn';
    } else {
        dot.classList.add('offline');
        text.textContent         = 'System Status: Offline';
        donutLabel.textContent   = 'Offline';
        donutLabel.className     = 'value offline';
        vmRowStatus.classList.add('badge-danger');
        vmRowStatus.innerHTML    = '<span class="bdot"></span> Stopped';
        stVmDot.style.background = 'var(--danger)';
        stVmVal.textContent      = 'Offline';
        stVmVal.className        = 'status-value offline';
    }

    // Mirror latest metric values into the VM table row
    if (cpuData.length)  document.getElementById('vm-row-cpu').textContent = cpuData[cpuData.length - 1] + '%';
    if (ramData.length)  document.getElementById('vm-row-ram').textContent = ramData[ramData.length - 1] + '%';
}

/**
 * Parse the status string from the vm-status-text element.
 * @param {string} html - innerHTML of the status badge element.
 * @returns {string} Normalised status string.
 */
function parseVmStatus(html) {
    if (html.includes('Running'))                         return 'Running';
    if (html.includes('Starting'))                        return 'Starting';
    if (html.includes('Stopping'))                        return 'Stopping';
    if (html.includes('Stopped') || html.includes('deallocated')) return 'Stopped';
    if (html.includes('Restarting'))                      return 'Restarting';
    return 'Unknown';
}

/* Watch for DOM mutations on the hidden vm-status-text span
   (written by vm_manager.js on every poll cycle) */
const vmStatusObserver = new MutationObserver(() => {
    const statusHtml   = document.getElementById('vm-status-text')?.innerHTML || '';
    const resourceInfo = document.getElementById('vm-resource-info')?.textContent || '';
    const parts        = resourceInfo.match(/^(.+?)\s*\((.+?)\)$/);

    updateDashboardStatus(
        parseVmStatus(statusHtml),
        parts?.[1] || resourceInfo,
        parts?.[2] || ''
    );
});

/* ===================================================================
   DOM READY
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Start observing the hidden status element written by vm_manager.js
    const target = document.getElementById('vm-status-text');
    if (target) {
        vmStatusObserver.observe(target, { childList: true, characterData: true, subtree: true });
    }

    // Run an initial status sync after vm_manager.js has had time to fire its first poll
    setTimeout(() => {
        const statusHtml   = document.getElementById('vm-status-text')?.innerHTML || '';
        const resourceInfo = document.getElementById('vm-resource-info')?.textContent || '';
        const parts        = resourceInfo.match(/^(.+?)\s*\((.+?)\)$/);

        updateDashboardStatus(
            parseVmStatus(statusHtml),
            parts?.[1] || resourceInfo,
            parts?.[2] || ''
        );
    }, 1500);
});
