// QuaNet Vision - Dashboard Real-Time Charts & Monitoring
document.addEventListener('DOMContentLoaded', () => {
    if (typeof chartConfigData === 'undefined') return;

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleColor: '#38bdf8',
                bodyColor: '#f8fafc',
                borderColor: 'rgba(56, 189, 248, 0.3)',
                borderWidth: 1,
                padding: 10,
                displayColors: false
            }
        },
        scales: {
            x: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 45 }
            },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#94a3b8', font: { size: 10 } }
            }
        },
        elements: {
            line: { tension: 0.35, borderWidth: 2 },
            point: { radius: 2.5, hoverRadius: 5 }
        }
    };

    // 1. pH Chart
    const phCtx = document.getElementById('chartPH');
    if (phCtx) {
        new Chart(phCtx, {
            type: 'line',
            data: {
                labels: chartConfigData.labels,
                datasets: [{
                    data: chartConfigData.ph,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.12)',
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // 2. Temperature Chart
    const tempCtx = document.getElementById('chartTemp');
    if (tempCtx) {
        new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: chartConfigData.labels,
                datasets: [{
                    data: chartConfigData.temperature,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.12)',
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // 3. Turbidity Chart
    const turbCtx = document.getElementById('chartTurbidity');
    if (turbCtx) {
        new Chart(turbCtx, {
            type: 'line',
            data: {
                labels: chartConfigData.labels,
                datasets: [{
                    data: chartConfigData.turbidity,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.12)',
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // 4. Dissolved Oxygen Chart
    const doCtx = document.getElementById('chartDO');
    if (doCtx) {
        new Chart(doCtx, {
            type: 'line',
            data: {
                labels: chartConfigData.labels,
                datasets: [{
                    data: chartConfigData.dissolved_oxygen,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.12)',
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // 5. TDS & Conductivity Chart
    const tdsCtx = document.getElementById('chartTDS');
    if (tdsCtx) {
        new Chart(tdsCtx, {
            type: 'line',
            data: {
                labels: chartConfigData.labels,
                datasets: [
                    {
                        label: 'TDS (mg/L)',
                        data: chartConfigData.tds,
                        borderColor: '#818cf8',
                        backgroundColor: 'transparent',
                        yAxisID: 'y'
                    },
                    {
                        label: 'Conductivity (µS/cm)',
                        data: chartConfigData.conductivity,
                        borderColor: '#06b6d4',
                        backgroundColor: 'transparent',
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                ...commonOptions,
                plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 10 } } } },
                scales: {
                    x: commonOptions.scales.x,
                    y: { ...commonOptions.scales.y, title: { display: true, text: 'TDS (mg/L)', color: '#818cf8', font: { size: 10 } } },
                    y1: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#06b6d4', font: { size: 10 } },
                        title: { display: true, text: 'EC (µS/cm)', color: '#06b6d4', font: { size: 10 } }
                    }
                }
            }
        });
    }
});
