// charts.js - Chart.js initialization and updates

const charts = {};

function initCharts() {
    const ctxMonthly = document.getElementById('monthly-sales-chart').getContext('2d');
    const ctxTrend = document.getElementById('sales-trend-chart').getContext('2d');
    const ctxCategory = document.getElementById('category-chart').getContext('2d');
    const ctxGrowth = document.getElementById('growth-chart').getContext('2d');

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(200, 200, 200, 0.1)',
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        }
    };

    // Monthly Sales Chart (Bar)
    charts.monthly = new Chart(ctxMonthly, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Revenue',
                data: [],
                backgroundColor: 'rgba(99, 102, 241, 0.8)',
                borderRadius: 8,
            }]
        },
        options: commonOptions
    });

    // Sales Trend Chart (Line)
    charts.trend = new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Orders',
                data: [],
                borderColor: '#8b5cf6',
                tension: 0.4,
                fill: false
            }]
        },
        options: commonOptions
    });

    // Category Chart (Doughnut)
    charts.category = new Chart(ctxCategory, {
        type: 'doughnut',
        data: {
            labels: ['Electronics', 'Clothing', 'Food', 'Furniture', 'Sports'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'
                ],
                borderWidth: 0
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });

    // Growth Chart (Area)
    charts.growth = new Chart(ctxGrowth, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cumulative Revenue',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: commonOptions
    });
}

function updateCharts(data) {
    if (!charts.monthly) return;

    // Monthly Update
    charts.monthly.data.labels = data.monthly.labels;
    charts.monthly.data.datasets[0].data = data.monthly.values;
    charts.monthly.update();

    // Trend Update
    charts.trend.data.labels = data.trend.labels;
    charts.trend.data.datasets[0].data = data.trend.values;
    charts.trend.update();

    // Category Update
    charts.category.data.datasets[0].data = data.categories;
    charts.category.update();

    // Growth Update
    charts.growth.data.labels = data.growth.labels;
    charts.growth.data.datasets[0].data = data.growth.values;
    charts.growth.update();
}

window.initCharts = initCharts;
window.updateCharts = updateCharts;
