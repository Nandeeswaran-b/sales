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
                backgroundColor: '#d95d39',
                borderRadius: 4,
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
                borderColor: '#4f8061',
                tension: 0.28,
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
                    '#d95d39', '#4f8061', '#c58a35', '#6f8ca3', '#bd5146'
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
                borderColor: '#4f8061',
                backgroundColor: 'rgba(79, 128, 97, 0.14)',
                fill: true,
                tension: 0.28
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
