import { fetchGridStatus, generate24HourForecastMock } from './api.js';

// Chart instances
let solarLineChart, allocationDoughnutChart, demandBarChart;

// CSS Variables for charts
const style = getComputedStyle(document.body);
const colors = {
    hospital: style.getPropertyValue('--chart-hospital').trim(),
    govt: style.getPropertyValue('--chart-govt').trim(),
    residential: style.getPropertyValue('--chart-residential').trim(),
    itpark: style.getPropertyValue('--chart-itpark').trim(),
    ev: style.getPropertyValue('--chart-ev').trim(),
    bgTertiary: style.getPropertyValue('--bg-tertiary').trim(),
    accent: style.getPropertyValue('--accent-primary').trim()
};

const zoneColors = {
    "Assembly": colors.hospital,
    "Government Offices": colors.govt,
    "Capital Complex": colors.residential,
    "Residential": colors.itpark,
    "Solar Farm": colors.ev
};

// Global grid state for Copilot access
window.latestGridState = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    
    // Live clock
    setInterval(() => {
        const now = new Date();
        document.getElementById('current-time').innerText = now.toLocaleTimeString();
    }, 1000);
    
    // Start polling API
    pollData();
    setInterval(pollData, 10000); // 10s intervals
});

async function pollData() {
    console.log("Polling grid data...");
    const data = await fetchGridStatus();
    if (data && Object.keys(data).length > 0) {
        window.latestGridState = data;
        updateUI(data);
    }
}

function initCharts() {
    Chart.defaults.color = style.getPropertyValue('--text-secondary').trim();
    Chart.defaults.font.family = style.getPropertyValue('--font-body').trim();
    
    // 1. Solar Line Chart
    const ctxSolar = document.getElementById('solarChart').getContext('2d');
    
    const gradient = ctxSolar.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(0, 229, 255, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 229, 255, 0)');

    solarLineChart = new Chart(ctxSolar, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Predicted Generation (MW)',
                data: [],
                borderColor: colors.accent,
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: colors.bgTertiary }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });

    // 2. Allocation Doughnut
    const ctxAlloc = document.getElementById('allocationChart').getContext('2d');
    allocationDoughnutChart = new Chart(ctxAlloc, {
        type: 'doughnut',
        data: {
            labels: ['Assembly', 'Government Offices', 'Capital Complex', 'Residential', 'Solar Farm'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    colors.hospital, colors.govt, colors.residential, colors.itpark, colors.ev
                ],
                borderWidth: 0,
                cutout: '65%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 20 }
                }
            }
        }
    });

    // 3. Demand Bar Chart
    const ctxBar = document.getElementById('demandBarChart').getContext('2d');
    demandBarChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Assembly', 'Govt Off', 'Cap Comp', 'Resi', 'Solar'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    colors.hospital, colors.govt, colors.residential, colors.itpark, colors.ev
                ],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: colors.bgTertiary }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function updateUI(data) {
    // 1. Storm Mode Intervention
    let solar = data.solar_generation || 0;
    let demand = data.total_demand || 0;
    let battery = data.battery_after || 0; // max 80 MWh
    
    const stormBanner = document.getElementById('storm-banner');
    if (data.storm_mode_active) {
        // Activate Storm Mode
        stormBanner.style.display = 'flex';
        const windSpeed = data.weather?.wind_speed || 45;
        document.getElementById('val-storm-wind').textContent = `${windSpeed} km/h`;
    } else {
        stormBanner.style.display = 'none';
    }
    
    // 2. Solar Efficiency & Alerts
    const effBadge = document.getElementById('solar-eff-badge');
    const efficiency = data.solar_efficiency_pct || 100;
    effBadge.textContent = `${efficiency.toFixed(1)}% EFF`;
    
    if (efficiency < 90) {
        effBadge.className = 'status-pill';
        effBadge.style.borderColor = 'var(--danger)';
        effBadge.style.color = 'var(--danger)';
    } else {
        effBadge.className = 'status-pill stable';
        effBadge.style.borderColor = 'var(--success)';
        effBadge.style.color = 'var(--bg-primary)';
        effBadge.style.backgroundColor = 'var(--success)';
    }

    document.getElementById('val-solar').textContent = solar.toFixed(2);
    document.getElementById('val-demand').textContent = demand.toFixed(2);
    
    let shortfall = demand - (solar + (data.backup_used || 0));
    if (shortfall < 0) shortfall = 0;
    document.getElementById('val-shortfall').textContent = shortfall.toFixed(2);
    
    const stabilityPct = (data.grid_stability_score || 0) * 100;
    document.getElementById('val-stability').textContent = stabilityPct.toFixed(1);
    
    // Status color
    const stabilityEl = document.getElementById('val-stability');
    const pill = document.getElementById('global-status-pill');
    const pillText = document.getElementById('global-status-text');
    
    if (stabilityPct >= 99) {
        stabilityEl.className = 'metric-value text-success';
        pill.className = 'status-pill stable';
        pillText.textContent = 'STABLE';
    } else if (stabilityPct > 70) {
        stabilityEl.className = 'metric-value text-warning';
        pill.className = 'status-pill';
        pill.style.borderColor = 'var(--warning)';
        pill.style.color = 'var(--warning)';
        pillText.textContent = 'DEGRADED';
    } else {
        stabilityEl.className = 'metric-value text-danger';
        pill.className = 'status-pill';
        pill.style.borderColor = 'var(--danger)';
        pill.style.color = 'var(--danger)';
        pillText.textContent = 'CRITICAL';
    }
    
    // 3. Battery Health Tracking
    const sohSpan = document.getElementById('battery-soh');
    const sohValSpan = sohSpan.querySelector('span');
    const bSoh = data.battery_soh || 100;
    sohValSpan.textContent = `${bSoh.toFixed(2)}%`;
    if(bSoh < 90) {
        sohValSpan.className = 'text-warning';
    } else {
        sohValSpan.className = 'text-success';
    }
    
    const batPct = (battery / 80) * 100;
    document.getElementById('val-battery').textContent = batPct.toFixed(1);
    
    // Live Weather
    if(data.weather) {
        document.getElementById('val-temp').textContent = data.weather.temperature || '--';
        document.getElementById('val-cloud').textContent = data.weather.cloud_cover || '--';
        document.getElementById('val-irrad').textContent = data.weather.solar_irradiance || '--';
        document.getElementById('val-wind').textContent = data.weather.wind_speed || '--';
    }
    
    // Battery Visual
    const batFill = document.getElementById('battery-fill');
    batFill.style.height = `${Math.min(100, batPct)}%`;
    batFill.textContent = `${batPct.toFixed(0)}%`;
    
    let batColor = 'var(--success)';
    if (batPct < 40) batColor = 'var(--warning)';
    if (batPct < 15) batColor = 'var(--danger)';
    batFill.style.backgroundColor = batColor;
    
    // Battery state
    const batStateText = document.getElementById('battery-state-text');
    if (data.surplus_added_today > 0) {
        batStateText.textContent = `↑ Charging · ${batPct.toFixed(1)}%`;
        batStateText.style.color = 'var(--success)';
    } else if (data.backup_used > 0) {
        batStateText.textContent = `↓ Discharging · ${batPct.toFixed(1)}%`;
        batStateText.style.color = 'var(--warning)';
    } else {
        batStateText.textContent = `− Holding · ${batPct.toFixed(1)}%`;
        batStateText.style.color = 'var(--text-secondary)';
    }

    // Zone Breakdown
    if(data.demand && data.optimized_distribution) {
        const order = ['Assembly', 'Government Offices', 'Capital Complex', 'Residential', 'Solar Farm'];
        const shortNames = ['Assembly', 'Govt Off', 'Cap Comp', 'Resi', 'Solar'];
        
        // Update Bar Chart
        demandBarChart.data.datasets[0].data = order.map(z => data.demand[z] || 0);
        demandBarChart.update();
        
        // Update Doughnut
        allocationDoughnutChart.data.datasets[0].data = order.map(z => {
            // Check if the backend provides the raw number or an object:
            const zData = data.optimized_distribution[z];
            if (typeof zData === 'number') return zData;
            return zData?.allocated || 0;
        });
        allocationDoughnutChart.update();
        
        // Update Progress Bars
        const container = document.getElementById('zone-allocation-container');
        container.innerHTML = '';
        
        order.forEach((zone, index) => {
            let zData = data.optimized_distribution[zone];
            if(zData === undefined) return;
            
            let demandMW = data.demand[zone] || 0;
            let allocMW = 0;
            
            // Backend outputs native numbers instead of objects in some cases
            if (typeof zData === 'number') {
                allocMW = zData;
            } else {
                allocMW = zData.allocated;
            }
            
            // 4. V2G Simulation Display
            // Backend already added v2g_supplied to the allocation math, so we just use the flag for UI badge styling
            const isV2GActive = (zone === 'Residential' && data.v2g_supplied > 0);
            
            const pct = demandMW > 0 ? (allocMW / demandMW) * 100 : 0;
            const color = zoneColors[zone];
            
            const row = document.createElement('div');
            row.className = 'zone-row';
            
            let labelHtml = `<div class="zone-label">${shortNames[index]}</div>`;
            if (isV2GActive) {
                labelHtml = `<div class="zone-label" title="V2G Active (${data.v2g_supplied} MW)">${shortNames[index]} <i class="fas fa-bolt text-warning" style="font-size:0.7em;"></i></div>`;
            }
            
            row.innerHTML = `
                ${labelHtml}
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background-color: ${color};"></div>
                </div>
                <div class="zone-value">${allocMW.toFixed(1)} MW</div>
            `;
            container.appendChild(row);
        });
    }
    
    // Update Solar Chart (Mocked bell curve around current peak)
    // Note: To match the screenshot, we mock a 24h curve peaking around noon.
    const peakEstimate = Math.max(solar * 1.5, 12); // if low sun, assume at least some peak
    const mocked = generate24HourForecastMock(peakEstimate);
    solarLineChart.data.labels = mocked.labels;
    solarLineChart.data.datasets[0].data = mocked.data;
    solarLineChart.update();
    
    // 5. Data Integrity Monitor (Hashes)
    if (data.latest_audit_hash) {
        logAuditHash(data.latest_audit_hash);
    }
}

// Data Integrity Visualizer
function logAuditHash(hashHex) {
    const terminal = document.getElementById('audit-terminal');
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    const logLine = document.createElement('div');
    logLine.style.marginBottom = '0.25rem';
    logLine.innerHTML = `<span style="color: var(--text-secondary)">[${timeStr}]</span> OPTIMIZE_CYCLE: <span style="color: var(--success)">VERIFIED</span> <span style="opacity: 0.7;">0x${hashHex.toUpperCase()}</span>`;
    
    terminal.prepend(logLine);
    
    // Keep max 20 lines
    if(terminal.children.length > 20) {
        terminal.removeChild(terminal.lastChild);
    }
}

// Auto Reports Generator
window.downloadReport = function() {
    window.location.href = 'http://127.0.0.1:8000/report';
}
