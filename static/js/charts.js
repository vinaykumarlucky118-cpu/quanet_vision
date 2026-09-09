// QuaNet Vision - Analytics Charts & Correlation Visualizations
document.addEventListener('DOMContentLoaded', () => {
    // Quality Distribution Doughnut Chart
    const distCanvas = document.getElementById('qualityDoughnutChart');
    if (distCanvas && typeof qualityDistData !== 'undefined') {
        new Chart(distCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Good Quality', 'Moderate Quality', 'Poor Quality'],
                datasets: [{
                    data: [qualityDistData.GOOD.count, qualityDistData.MODERATE.count, qualityDistData.POOR.count],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderColor: '#0b1329',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { size: 11 }, padding: 15 }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Analytics Timeline Trends
    const trendCanvas = document.getElementById('analyticsTrendChart');
    if (trendCanvas && typeof trendChartData !== 'undefined') {
        new Chart(trendCanvas, {
            type: 'line',
            data: {
                labels: trendChartData.timestamps,
                datasets: [
                    {
                        label: 'pH (Scaled x10)',
                        data: trendChartData.ph.map(v => v * 10),
                        borderColor: '#38bdf8',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.3
                    },
                    {
                        label: 'Turbidity (NTU)',
                        data: trendChartData.turbidity,
                        borderColor: '#ef4444',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.3
                    },
                    {
                        label: 'DO (mg/L x5)',
                        data: trendChartData.dissolved_oxygen.map(v => v * 5),
                        borderColor: '#10b981',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#94a3b8', font: { size: 11 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { size: 10 } }
                    }
                }
            }
        });
    }
});
