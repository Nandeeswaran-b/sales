
const globalWindow = { location: { hash: '#churn', hostname: 'localhost' }, addEventListener: () => {} };
global.window = globalWindow;
const globalDocument = {
    addEventListener: () => {},
    querySelectorAll: () => ({ forEach: () => {} }),
    getElementById: (id) => ({ 
        getContext: () => ({}),
        classList: { add: () => {}, remove: () => {} },
        addEventListener: () => {},
        textContent: ''
    })
};
global.document = globalDocument;
global.fetch = async () => ({ ok: true, json: async () => ({}) });
global.Chart = class { 
    static defaults = { 
        font: {}, 
        color: '', 
        scale: { grid: {} },
        plugins: { tooltip: {} }
    }; 
};

// Make window assignments global
const proxyHandler = {
    set: function(obj, prop, value) {
        global[prop] = value;
        obj[prop] = value;
        return true;
    }
};
global.window = new Proxy(globalWindow, proxyHandler);

    // ═══════════════════════════════════════════════════════
    // INITIALIZATION & GLOBAL UTILITIES
    // ═══════════════════════════════════════════════════════

    // Set Date in header
    document.getElementById('date-display').textContent = new Date().toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });

    // Indian Currency Formatter (INR)
    const currencyFormatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    });

    // Chart.js Style Defaults
    Chart.defaults.color = '#7d869e';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.borderColor = 'rgba(139, 92, 246, 0.05)';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20, 24, 41, 0.95)';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(139, 92, 246, 0.2)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;

    // Charts objects registry for hot replacement / refresh
    let charts = {
        monthly: null,
        category: null,
        customers: null,
        forecast: null,
        distribution: null,
        rfm: null,
        growth: null,
        cumulative: null
    };

    let allSalesData = [];
    let anomalySet = new Set(); // Stores anomaly IDs for table badges
    let activeTab = 'dashboard';
    let forecastDegree = 1; // Polynomial forecast model degree state
    let rfmCustomerList = []; // RFM cohort lookup data cache
    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:5000' 
        : 'https://sales-backend-k5rw.onrender.com';



    // ═══════════════════════════════════════════════════════
    // TAB ROUTING MANAGEMENT
    // ═══════════════════════════════════════════════════════
    
    function switchTab(tabId) {
        if (tabId === activeTab) return;
        activeTab = tabId;

        // Toggle Buttons active classes
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');

        // Toggle Content Sections
        document.querySelectorAll('.tab-content').forEach(sect => sect.classList.remove('active'));
        document.getElementById(`${tabId}-view`).classList.add('active');

        // Trigger appropriate data fetches
        if (tabId === 'analytics') {
            loadAnalyticsData();
        } else if (tabId === 'churn') {
            loadChurnData();
        } else if (tabId === 'weather') {
            loadWeatherForecast();
        } else if (tabId === 'sql') {
            loadSQLConsoleData();
        } else {
            loadDashboardData();
        }

        
        // Sync hash
        window.location.hash = tabId;
    }

    // Support back/forward browser navigation using hash
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.replace('#', '');
        if (hash === 'analytics' || hash === 'dashboard' || hash === 'sql' || hash === 'churn' || hash === 'weather') {
            switchTab(hash);
        }
    });



    // ═══════════════════════════════════════════════════════
    // CORE SERVICES: FETCH DASHBOARD DATA
    // ═══════════════════════════════════════════════════════

    async function loadDashboardData() {
        try {
            // First fetch summaries & core charts in parallel
            const [summaryRes, monthlyRes, categoryRes, customersRes, salesRes, anomalyRes] = await Promise.all([
                fetch(API_BASE + '/api/summary'),
                fetch(API_BASE + '/api/chart/monthly'),
                fetch(API_BASE + '/api/chart/category'),
                fetch(API_BASE + '/api/chart/customers'),
                fetch(API_BASE + '/api/sales'),
                fetch(API_BASE + '/api/analytics/anomalies')
            ]);

            const summary = await summaryRes.json();
            const monthly = await monthlyRes.json();
            const category = await categoryRes.json();
            const customers = await customersRes.json();
            allSalesData = await salesRes.json();
            const anomaliesData = await anomalyRes.json();

            // Store anomalies for quick lookup mapping
            anomalySet.clear();
            if (anomaliesData.anomalies) {
                anomaliesData.anomalies.forEach(a => anomalySet.add(a.id));
            }

            // Render KPIs with count-up animations
            animateValue('kpi-revenue', summary.total_revenue, true);
            animateValue('kpi-orders', summary.total_orders, false);
            animateValue('kpi-aov', summary.avg_order_value, true);
            document.getElementById('kpi-product').textContent = summary.top_product;

            // MoM Growth Indicator Badge
            const trendBadge = document.getElementById('kpi-revenue-trend');
            trendBadge.style.display = 'inline-flex';
            if (summary.mom_growth > 0) {
                trendBadge.className = 'kpi-badge up';
                trendBadge.innerHTML = `▲ +${summary.mom_growth}% MoM`;
            } else if (summary.mom_growth < 0) {
                trendBadge.className = 'kpi-badge down';
                trendBadge.innerHTML = `▼ ${summary.mom_growth}% MoM`;
            } else {
                trendBadge.className = 'kpi-badge';
                trendBadge.style.background = 'rgba(255,255,255,0.05)';
                trendBadge.style.color = 'var(--text-muted)';
                trendBadge.innerHTML = `● 0.0% MoM`;
            }

            // Render Charts
            renderMonthlyChart(monthly);
            renderCategoryChart(category);
            renderCustomersChart(customers);

            // Render Table log
            renderTable(allSalesData);

        } catch (error) {
            console.error('Error fetching dashboard datasets:', error);
            showToast('⚠️ Failed to load dashboard data. Check database connections.', true);
        }
    }

    // ═══════════════════════════════════════════════════════
    // CORE SERVICES: FETCH ANALYTICS DATA (DS/ML TAB)
    // ═══════════════════════════════════════════════════════

    async function loadAnalyticsData() {
        // Create full overlay spinner
        const targetView = document.getElementById('analytics-view');
        let loader = document.createElement('div');
        loader.className = 'analytics-loading';
        loader.innerHTML = '<div class="spinner"></div><p style="color: var(--text-secondary); font-weight:600; font-size:14px;">Computing metrics & loading models...</p>';
        targetView.appendChild(loader);

        try {
            const [forecastRes, statsRes, rfmRes, anomaliesRes, correlationRes, distributionRes, growthRes, recsRes] = await Promise.all([
                fetch(API_BASE + `/api/analytics/forecast?degree=${forecastDegree}`),
                fetch(API_BASE + '/api/analytics/stats'),
                fetch(API_BASE + '/api/analytics/rfm'),
                fetch(API_BASE + '/api/analytics/anomalies'),
                fetch(API_BASE + '/api/analytics/correlation'),
                fetch(API_BASE + '/api/analytics/distribution'),
                fetch(API_BASE + '/api/analytics/growth'),
                fetch(API_BASE + '/api/analytics/recommendations')
            ]);

            const forecast = await forecastRes.json();
            const stats = await statsRes.json();
            const rfm = await rfmRes.json();
            
            // Cache RFM customer list data for lookup rendering
            rfmCustomerList = rfm;
            const anomalies = await anomaliesRes.json();
            const correlation = await correlationRes.json();
            const distribution = await distributionRes.json();
            const growth = await growthRes.json();
            const recs = await recsRes.json();

            // Populate top KPI cards
            document.getElementById('kpi-r2').textContent = forecast.model.r_squared.toFixed(4);
            document.getElementById('kpi-r2-sub').textContent = `Fit: ${forecast.model.equation}`;
            
            document.getElementById('kpi-anomaly-count').textContent = anomalies.anomaly_count;
            document.getElementById('kpi-anomaly-rate').textContent = `${anomalies.anomaly_rate}% of sales binned`;

            document.getElementById('kpi-skewness').textContent = stats.skewness.toFixed(3);
            const skewType = stats.skewness > 0.5 ? 'Right-skewed (High sales)' : (stats.skewness < -0.5 ? 'Left-skewed' : 'Symmetric density');
            document.getElementById('kpi-skewness-desc').textContent = skewType;

            // Render complex analytics visual modules
            renderForecastChart(forecast);
            renderPriceDistribution(distribution);
            renderStatsGrid(stats);
            renderAnomaliesTable(anomalies.anomalies);
            renderRFMBubbles(rfm);
            renderRFMLookupTable(rfm); // Populate RFM lookup panel
            renderCorrelationHeatmap(correlation);
            renderMoMGrowthChart(growth.monthly);
            renderCumulativeChart(growth.monthly);
            renderRecommendations(recs);

        } catch (e) {
            console.error('Error fetching analytics calculations:', e);
            showToast('⚠️ Statistical computation failed. Check python environment log.', true);
        } finally {
            // Destroy loader
            if (loader.parentNode) {
                loader.parentNode.removeChild(loader);
            }
        }
    }

    window.triggerBundlePromotion = function(itemA, itemB) {
        showToast(`⚡ Created bundle promotion: "${itemA} + ${itemB}" at 10% off!`);
    };

    function renderRecommendations(recs) {
        const tbody = document.getElementById('recTableBody');
        tbody.innerHTML = '';
        
        if (!recs || recs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No association rules found in transaction logs.</td></tr>';
            document.getElementById('top-rec-bundle').textContent = 'No associations found.';
            return;
        }

        // Set Top Recommendation Banner
        const top = recs[0];
        document.getElementById('top-rec-bundle').innerHTML = `
            Customers purchasing <strong>${top.item_a}</strong> are 
            <strong>${top.lift}x</strong> more likely to also buy <strong>${top.item_b}</strong>.<br>
            <span style="color:var(--text-secondary); font-size:12px;">(Confidence: ${top.confidence_a_b}%)</span>
        `;

        recs.forEach(r => {
            const row = `
                <tr>
                    <td><strong>${r.item_a}</strong></td>
                    <td><strong>${r.item_b}</strong></td>
                    <td>${r.support}%</td>
                    <td>${r.confidence_a_b}%</td>
                    <td><span style="font-weight:600; color:var(--accent-orange);">${r.lift}x</span></td>
                    <td>
                        <button class="btn btn-secondary" style="font-size:10px; padding: 4px 8px;" onclick="triggerBundlePromotion('${r.item_a}', '${r.item_b}')">
                            🏷️ Create Bundle
                        </button>
                    </td>
                </tr>
            `;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    }


    function refreshData() {
        if (activeTab === 'dashboard') {
            loadDashboardData();
        } else {
            loadAnalyticsData();
        }
        showToast('🔄 Dataset re-indexed successfully.');
    }

    // ═══════════════════════════════════════════════════════
    // KPI COUNT ANIMATION ENGINE
    // ═══════════════════════════════════════════════════════

    function animateValue(elementId, finalValue, isCurrency) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const duration = 650;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
            const current = Math.floor(eased * finalValue);

            if (isCurrency) {
                el.textContent = currencyFormatter.format(current);
            } else {
                el.textContent = current.toLocaleString('en-IN');
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = isCurrency ? currencyFormatter.format(finalValue) : finalValue.toLocaleString('en-IN');
            }
        }

        requestAnimationFrame(update);
    }

    // ═══════════════════════════════════════════════════════
    // VISUALS: DASHBOARD TAB CHARTS
    // ═══════════════════════════════════════════════════════

    function renderMonthlyChart(data) {
        const ctx = document.getElementById('monthlyChart').getContext('2d');
        const labels = data.map(d => {
            const [y, m] = d.month.split('-');
            return new Date(y, m - 1).toLocaleString('default', { month: 'short', year: '2-digit' });
        });
        const revenues = data.map(d => d.revenue);

        const gradient = ctx.createLinearGradient(0, 0, 0, 260);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.85)');
        gradient.addColorStop(1, 'rgba(6, 182, 212, 0.3)');

        if (charts.monthly) charts.monthly.destroy();

        charts.monthly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Revenue',
                    data: revenues,
                    backgroundColor: gradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.65
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: context => ` Revenue: ${currencyFormatter.format(context.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: {
                            callback: val => val >= 100000 ? 'Rs. ' + (val / 100000).toFixed(1) + 'L' : 'Rs. ' + (val / 1000).toFixed(0) + 'K'
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderCategoryChart(data) {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const labels = data.map(d => d.category);
        const revenues = data.map(d => d.revenue);
        const colors = ['#8b5cf6', '#06b6d4', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#a855f7'];

        if (charts.category) charts.category.destroy();

        charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: revenues,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 3,
                    borderColor: 'var(--bg-card)',
                    hoverBorderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 14,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            color: '#a3adc2'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => ` ${context.label}: ${currencyFormatter.format(context.raw)}`
                        }
                    }
                }
            }
        });
    }

    function renderCustomersChart(data) {
        const ctx = document.getElementById('customersChart').getContext('2d');
        const labels = data.map(d => d.name);
        const revenues = data.map(d => d.revenue);

        const gradient = ctx.createLinearGradient(0, 0, 600, 0);
        gradient.addColorStop(0, 'rgba(236, 72, 153, 0.7)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.75)');

        if (charts.customers) charts.customers.destroy();

        charts.customers = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Spent',
                    data: revenues,
                    backgroundColor: gradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.55
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: context => ` Spend: ${currencyFormatter.format(context.raw)}`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: {
                            callback: val => val >= 100000 ? 'Rs. ' + (val / 100000).toFixed(1) + 'L' : 'Rs. ' + (val / 1000).toFixed(0) + 'K'
                        }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // ═══════════════════════════════════════════════════════
    // VISUALS: ANALYTICS TAB CHARTS
    // ═══════════════════════════════════════════════════════

    function renderForecastChart(data) {
        const ctx = document.getElementById('forecastChart').getContext('2d');
        
        const historicalLabels = data.historical.map(h => {
            const [y, m] = h.month.split('-');
            return new Date(y, m - 1).toLocaleString('default', { month: 'short', year: '2-digit' });
        });
        const forecastLabels = data.forecast.map(f => {
            const [y, m] = f.month.split('-');
            return new Date(y, m - 1).toLocaleString('default', { month: 'short', year: '2-digit' });
        });

        const allLabels = [...historicalLabels, ...forecastLabels];
        const histActuals = data.historical.map(h => h.actual);
        const forecastPredicted = data.forecast.map(f => f.predicted);
        const forecastLower = data.forecast.map(f => f.lower_bound);
        const forecastUpper = data.forecast.map(f => f.upper_bound);

        const lastActualVal = histActuals[histActuals.length - 1];

        // Format data streams aligning the points properly
        const actualData = [...histActuals, ...new Array(forecastLabels.length).fill(null)];
        const fittedData = data.historical.map(h => h.fitted);
        const forecastData = [...new Array(histActuals.length - 1).fill(null), lastActualVal, ...forecastPredicted];
        const upperData = [...new Array(histActuals.length - 1).fill(null), lastActualVal, ...forecastUpper];
        const lowerData = [...new Array(histActuals.length - 1).fill(null), lastActualVal, ...forecastLower];

        if (charts.forecast) charts.forecast.destroy();

        charts.forecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Actual Revenue',
                        data: actualData,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        tension: 0.35
                    },
                    {
                        label: 'Fitted Regression',
                        data: fittedData,
                        borderColor: 'rgba(139, 92, 246, 0.3)',
                        borderWidth: 1.5,
                        borderDash: [3, 4],
                        pointRadius: 0,
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Forecast Trend',
                        data: forecastData,
                        borderColor: '#06b6d4',
                        borderWidth: 3,
                        borderDash: [6, 4],
                        backgroundColor: 'transparent',
                        pointRadius: 4,
                        tension: 0.35
                    },
                    {
                        label: 'Upper Bound',
                        data: upperData,
                        borderColor: 'transparent',
                        borderWidth: 0,
                        pointRadius: 0,
                        fill: false
                    },
                    {
                        label: '95% Confidence Band',
                        data: lowerData,
                        borderColor: 'transparent',
                        borderWidth: 0,
                        pointRadius: 0,
                        fill: 3, // Fill between dataset indices 4 (lower) and 3 (upper)
                        backgroundColor: 'rgba(6, 182, 212, 0.08)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            filter: item => item.text !== 'Upper Bound' && item.text !== 'Fitted Regression'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => ` ${context.dataset.label}: ${currencyFormatter.format(context.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: {
                            callback: val => val >= 100000 ? 'Rs. ' + (val / 100000).toFixed(1) + 'L' : 'Rs. ' + (val / 1000).toFixed(0) + 'K'
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderPriceDistribution(data) {
        const ctx = document.getElementById('distributionChart').getContext('2d');
        const labels = data.bins.map(b => b.label);
        const counts = data.bins.map(b => b.count);

        // Compute normal curve values alignment at each bin center (Scaled to sample size)
        const binCenters = data.bins.map(b => (b.bin_start + b.bin_end) / 2);
        const normValues = binCenters.map(x => {
            const m = data.stats.mean;
            const s = data.stats.std;
            const n = data.stats.n;
            const w = data.bins[0].bin_end - data.bins[0].bin_start;
            const exp = -0.5 * Math.pow((x - m) / s, 2);
            const pdf = (1 / (s * Math.sqrt(2 * Math.PI))) * Math.exp(exp);
            return pdf * n * w;
        });

        if (charts.distribution) charts.distribution.destroy();

        charts.distribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        type: 'line',
                        label: 'Normal distribution overlay',
                        data: normValues,
                        borderColor: '#ec4899',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.45,
                        fill: false
                    },
                    {
                        type: 'bar',
                        label: 'Binned Count',
                        data: counts,
                        backgroundColor: 'rgba(139, 92, 246, 0.4)',
                        borderColor: 'rgba(139, 92, 246, 0.8)',
                        borderWidth: 1.5,
                        borderRadius: 4,
                        barPercentage: 0.95,
                        categoryPercentage: 0.95
                    }
                ]
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
                        grid: { color: 'rgba(255,255,255,0.03)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderRFMBubbles(data) {
        const ctx = document.getElementById('rfmChart').getContext('2d');

        // Group bubble points by RFM Segments for discrete toggling legend
        const groups = {};
        data.forEach(item => {
            const seg = item.segment;
            if (!groups[seg]) groups[seg] = [];
            groups[seg].push({
                x: item.recency_days,
                y: item.frequency,
                r: Math.max(4, Math.min(22, item.monetary / 6000)), // Scale bubble size
                customer: item.customer_name,
                monetary: item.monetary,
                rfm: item.rfm_score
            });
        });

        const segmentColors = {
            'Champions': '#10b981',
            'Loyal Customers': '#06b6d4',
            'Potential Loyalists': '#3b82f6',
            'New Customers': '#8b5cf6',
            'At Risk': '#f59e0b',
            'Cannot Lose': '#ec4899',
            'Lost': '#ef4444'
        };

        const datasets = Object.keys(groups).map(segName => {
            return {
                label: segName,
                data: groups[segName],
                backgroundColor: segmentColors[segName] || 'rgba(255,255,255,0.25)',
                borderColor: 'var(--bg-card)',
                borderWidth: 1.5
            };
        });

        if (charts.rfm) charts.rfm.destroy();

        charts.rfm = new Chart(ctx, {
            type: 'bubble',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 10,
                            usePointStyle: true,
                            color: '#a3adc2'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => {
                                const pt = context.raw;
                                return ` ${pt.customer} (Score: ${pt.rfm}) | Spend: ${currencyFormatter.format(pt.monetary)} | Recency: ${pt.x}d, Freq: ${pt.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Frequency (No. of Orders)', color: 'var(--text-secondary)' },
                        grid: { color: 'rgba(255,255,255,0.03)' }
                    },
                    x: {
                        title: { display: true, text: 'Recency (Days since last purchase)', color: 'var(--text-secondary)' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function renderMoMGrowthChart(monthlyData) {
        const ctx = document.getElementById('growthChart').getContext('2d');
        // Filter out first month since growth is 0
        const items = monthlyData.slice(1);
        const labels = items.map(m => {
            const [y, mm] = m.month.split('-');
            return new Date(y, mm - 1).toLocaleString('default', { month: 'short', year: '2-digit' });
        });
        const rates = items.map(m => m.growth_rate);
        
        // Colors: green for positive, pink for negative MoM contraction
        const colors = rates.map(r => r >= 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(236, 72, 153, 0.7)');

        if (charts.growth) charts.growth.destroy();

        charts.growth = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    data: rates,
                    backgroundColor: colors,
                    borderRadius: 4,
                    barPercentage: 0.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: context => ` Growth rate: ${context.raw}%`
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: { callback: val => val + '%' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderCumulativeChart(monthlyData) {
        const ctx = document.getElementById('cumulativeChart').getContext('2d');
        const labels = monthlyData.map(m => {
            const [y, mm] = m.month.split('-');
            return new Date(y, mm - 1).toLocaleString('default', { month: 'short', year: '2-digit' });
        });
        const cumulativeSum = monthlyData.map(m => m.cumulative_revenue);

        const gradient = ctx.createLinearGradient(0, 0, 0, 260);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        if (charts.cumulative) charts.cumulative.destroy();

        charts.cumulative = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Cumulative Gross',
                    data: cumulativeSum,
                    borderColor: 'var(--accent-violet)',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: context => ` Cumulative: ${currencyFormatter.format(context.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: {
                            callback: val => val >= 100000 ? 'Rs. ' + (val / 100000).toFixed(1) + 'L' : 'Rs. ' + (val / 1000).toFixed(0) + 'K'
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // ═══════════════════════════════════════════════════════
    // VISUALS: DESCRIPTIVE STATISTICS GRID RENDER
    // ═══════════════════════════════════════════════════════

    function renderStatsGrid(stats) {
        const grid = document.getElementById('stats-panel-grid');
        grid.innerHTML = '';

        const statConfigs = [
            { label: 'Sample Size (N)', val: stats.count, meta: 'Total sales generated' },
            { label: 'Mean Revenue', val: currencyFormatter.format(stats.mean), meta: 'Standard arithmetic average' },
            { label: 'Median Revenue', val: currencyFormatter.format(stats.median), meta: '50th percentile checkpoint' },
            { label: 'Mode Class', val: `Rs. ${(stats.mode_range / 1000).toFixed(0)}K`, meta: 'Highest density price range' },
            { label: 'Std. Deviation', val: currencyFormatter.format(stats.std_dev), meta: 'Data dispersion spread' },
            { label: 'IQR Fences', val: currencyFormatter.format(stats.iqr), meta: `Q1-Q3 (${currencyFormatter.format(stats.q1)} - ${currencyFormatter.format(stats.q3)})` },
            { label: 'Variance (S²)', val: stats.variance.toLocaleString('en-IN'), meta: 'Squared deviations sum' },
            { label: 'Coeff. of Variation', val: `${stats.coefficient_of_variation.toFixed(1)}%`, meta: 'Relative dispersion ratio' },
            { label: 'Range Min/Max', val: `Rs. ${(stats.min / 1000).toFixed(0)}K - Rs. ${(stats.max / 1000).toFixed(0)}K`, meta: `Spread: ${currencyFormatter.format(stats.range)}` }
        ];

        statConfigs.forEach(conf => {
            const item = document.createElement('div');
            item.className = 'stats-item';
            item.innerHTML = `
                <div>
                    <div class="stats-label">${conf.label}</div>
                    <div class="stats-value">${conf.val}</div>
                </div>
                <div class="stats-meta">${conf.meta}</div>
            `;
            grid.appendChild(item);
        });
    }

    // ═══════════════════════════════════════════════════════
    // VISUALS: CORRELATION MATRIX HEATMAP TABLE
    // ═══════════════════════════════════════════════════════

    function renderCorrelationHeatmap(data) {
        const container = document.getElementById('correlation-heatmap-container');
        container.innerHTML = '';

        const table = document.createElement('table');
        table.className = 'heatmap-table';

        // Columns headers
        const header = document.createElement('tr');
        header.appendChild(document.createElement('th')); // corner
        data.features.forEach(f => {
            const th = document.createElement('th');
            th.className = 'heatmap-label col-lbl';
            th.textContent = f;
            header.appendChild(th);
        });
        table.appendChild(header);

        // Table Matrix cells
        data.features.forEach((lblY, yIndex) => {
            const row = document.createElement('tr');
            
            // row title header
            const th = document.createElement('th');
            th.className = 'heatmap-label row-lbl';
            th.textContent = lblY;
            row.appendChild(th);

            data.features.forEach((lblX, xIndex) => {
                const val = data.matrix[yIndex][xIndex];
                const td = document.createElement('td');
                td.className = 'heatmap-cell';
                td.textContent = val >= 0 ? `+${val.toFixed(2)}` : val.toFixed(2);

                // Alpha shading: Positive violet, negative pink
                let bg;
                if (val >= 0) {
                    bg = `rgba(139, 92, 246, ${val * 0.8 + 0.08})`;
                } else {
                    bg = `rgba(236, 72, 153, ${Math.abs(val) * 0.8 + 0.08})`;
                }
                td.style.backgroundColor = bg;
                td.style.color = Math.abs(val) > 0.4 ? '#ffffff' : 'var(--text-secondary)';
                td.title = `Pearson Correlation (${lblY} ⇎ ${lblX}): ${val}`;
                
                row.appendChild(td);
            });
            table.appendChild(row);
        });

        container.appendChild(table);
    }

    // ═══════════════════════════════════════════════════════
    // VISUALS: DATA TABLES DRAW & FILTER
    // ═══════════════════════════════════════════════════════

    function renderTable(data) {
        const tbody = document.querySelector('#salesTable tbody');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><div class="icon">🔍</div>No matching transactions logged.</td></tr>';
            return;
        }

        // Show top 60 rows for browser scroll efficiency
        const visible = data.slice(0, 60);

        visible.forEach(item => {
            const tr = document.createElement('tr');
            
            const dateObj = new Date(item.sale_date + 'T00:00:00');
            const formattedDate = dateObj.toLocaleDateString('en-IN', {
                day: '2-digit', month: 'short', year: 'numeric'
            });

            // If transaction was flagged in anomalies, render outlier flag badge
            const isAnomaly = anomalySet.has(item.id);
            const badgeClass = isAnomaly ? 'badge badge-anomaly' : 'badge badge-mobile';
            const badgeText = isAnomaly ? '⚠️ Outlier' : (item.mobile_no || 'N/A');

            tr.innerHTML = `
                <td>${formattedDate}</td>
                <td class="product-cell">${item.product_name}</td>
                <td><span class="badge badge-payment">${item.category}</span></td>
                <td>${item.customer_name}</td>
                <td><span class="${badgeClass}">${badgeText}</span></td>
                <td><span class="badge badge-payment" style="border-radius:4px;">${item.mode_of_payment || 'UPI'}</span></td>
                <td class="money-cell">${currencyFormatter.format(item.total_price)}</td>
            `;
            tbody.appendChild(tr);
        });

        if (data.length > 60) {
            const extra = document.createElement('tr');
            extra.innerHTML = `<td colspan="7" style="text-align:center; color: var(--text-muted); font-size: 12px; padding: 12px;">Showing top 60 of ${data.length} records. Filter to refine query.</td>`;
            tbody.appendChild(extra);
        }
    }

    function renderAnomaliesTable(anomalies) {
        const tbody = document.querySelector('#anomaliesTable tbody');
        tbody.innerHTML = '';

        if (anomalies.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><div class="icon">✅</div>No outliers currently flagged by model.</td></tr>';
            return;
        }

        anomalies.forEach(a => {
            const tr = document.createElement('tr');
            const dObj = new Date(a.sale_date + 'T00:00:00');
            const fDate = dObj.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });

            tr.innerHTML = `
                <td>${fDate}</td>
                <td>${a.customer_name}</td>
                <td class="product-cell">${a.product_name}</td>
                <td class="money-cell" style="color: var(--accent-pink);">${currencyFormatter.format(a.total_price)}</td>
                <td class="zscore-cell high-z">+${a.z_score.toFixed(2)}σ</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Live search filters
    const searchInput = document.getElementById('searchInput');
    const dateFilter = document.getElementById('dateFilter');

    function applyFilters() {
        const q = searchInput.value.toLowerCase();
        const d = dateFilter.value;

        const filtered = allSalesData.filter(item => {
            const matchesText = !q ||
                item.product_name.toLowerCase().includes(q) ||
                item.customer_name.toLowerCase().includes(q) ||
                item.category.toLowerCase().includes(q) ||
                (item.mobile_no && item.mobile_no.includes(q)) ||
                (item.mode_of_payment && item.mode_of_payment.toLowerCase().includes(q));

            const matchesDate = !d || item.sale_date === d;

            return matchesText && matchesDate;
        });

        renderTable(filtered);
    }

    let searchDebouncer;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebouncer);
        searchDebouncer = setTimeout(applyFilters, 200);
    });
    dateFilter.addEventListener('change', applyFilters);

    // ═══════════════════════════════════════════════════════
    // NEW SALE MODAL & FORM INGESTION
    // ═══════════════════════════════════════════════════════

    function openModal() {
        document.getElementById('addModal').classList.add('active');
        document.getElementById('sale_date').valueAsDate = new Date();
    }

    function closeModal() {
        document.getElementById('addModal').classList.remove('active');
    }

    document.getElementById('addModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeModal();
    });

    document.getElementById('addDataForm').addEventListener('submit', async e => {
        e.preventDefault();

        const payload = {
            customer_name: document.getElementById('customer_name').value,
            mobile_no: document.getElementById('mobile_no').value,
            product_name: document.getElementById('product_name').value,
            total_price: parseFloat(document.getElementById('total_price').value),
            sale_date: document.getElementById('sale_date').value,
            mode_of_payment: document.getElementById('mode_of_payment').value
        };

        try {
            const res = await fetch(API_BASE + '/api/sales/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                closeModal();
                document.getElementById('addDataForm').reset();
                showToast('✅ Sale added. Database rebuilt.');
                
                // Reload whatever tab is currently active
                if (activeTab === 'dashboard') {
                    loadDashboardData();
                } else {
                    loadAnalyticsData();
                }
            } else {
                const err = await res.json();
                showToast(`⚠️ Ingestion failed: ${err.error || 'Server rejected request'}`, true);
            }
        } catch (err) {
            showToast('⚠️ Network failure. Verify backend flask server is running.', true);
        }
    });

    // ═══════════════════════════════════════════════════════
    // TOAST NOTIFICATIONS MANAGER
    // ═══════════════════════════════════════════════════════

    function showToast(message, isError = false) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.style.borderColor = isError ? '#ef4444' : 'var(--accent-emerald)';
        toast.style.color = isError ? '#ef4444' : 'var(--accent-emerald)';
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // ═══════════════════════════════════════════════════════
    // POLYNOMIAL MODEL TUNING & DYNAMIC SWITCH
    // ═══════════════════════════════════════════════════════
    async function updateForecastModel(deg) {
        forecastDegree = parseInt(deg);
        showToast(`🔄 Re-fitting regression curve (Degree ${deg})...`);
        
        try {
            const res = await fetch(API_BASE + `/api/analytics/forecast?degree=${forecastDegree}`);
            const forecast = await res.json();
            
            // Re-render Forecast Chart
            renderForecastChart(forecast);
            
            // Re-populate forecast R² metrics card
            document.getElementById('kpi-r2').textContent = forecast.model.r_squared.toFixed(4);
            document.getElementById('kpi-r2-sub').textContent = `Fit: ${forecast.model.equation}`;
        } catch (e) {
            console.error('Failed to update forecast regression degree:', e);
            showToast('⚠️ Model fitting failed.', true);
        }
    }

    // ═══════════════════════════════════════════════════════
    // GOAL SEEK PRESCRIPTIVE MODELING
    // ═══════════════════════════════════════════════════════
    async function calculateGoalSeek() {
        const inputVal = parseFloat(document.getElementById('goalSeekTarget').value);
        const resultPanel = document.getElementById('goalSeekResults');

        if (isNaN(inputVal) || inputVal <= 0) {
            showToast('⚠️ Please enter a valid positive revenue target.', true);
            return;
        }

        resultPanel.innerHTML = '<div class="spinner" style="width:20px; height:20px; margin: 10px auto;"></div>';
        
        try {
            const res = await fetch(API_BASE + `/api/analytics/goalseek?target=${inputVal}`);
            const data = await res.json();

            if (res.ok) {
                const isGrowth = data.percent_change_needed >= 0;
                const trendIcon = isGrowth ? '📈' : '📉';
                const trendColor = isGrowth ? 'var(--accent-emerald)' : 'var(--accent-pink)';

                resultPanel.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:500;">
                        <span>Current Mo. Average:</span>
                        <span style="font-family:'JetBrains Mono';">${currencyFormatter.format(data.avg_monthly_revenue)}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:500;">
                        <span>Target Revenue Goal:</span>
                        <span style="font-family:'JetBrains Mono'; color:var(--accent-violet);">${currencyFormatter.format(data.target_revenue)}</span>
                    </div>
                    <div style="border-top:1px dashed var(--border); margin:6px 0;"></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:2px; color:var(--text-secondary);">
                        <span>Monthly Sales Needed:</span>
                        <strong style="font-family:'JetBrains Mono'; color:var(--text-primary);">${data.orders_needed} orders</strong>
                    </div>
                    <span style="font-size:10px; color:var(--text-muted); margin-bottom:6px; display:block;">(Assuming current AOV of ${currencyFormatter.format(data.current_aov)})</span>
                    
                    <div style="display:flex; justify-content:space-between; margin-bottom:2px; color:var(--text-secondary);">
                        <span>Target AOV Needed:</span>
                        <strong style="font-family:'JetBrains Mono'; color:var(--text-primary);">${currencyFormatter.format(data.aov_needed)}</strong>
                    </div>
                    <span style="font-size:10px; color:var(--text-muted); margin-bottom:6px; display:block;">(Assuming average volume of ${data.avg_monthly_orders} orders)</span>
                    
                    <div style="border-top:1px dashed var(--border); margin:6px 0;"></div>
                    <div style="display:flex; justify-content:space-between; font-weight:700; color:${trendColor};">
                        <span>Required Growth:</span>
                        <span>${trendIcon} ${isGrowth ? '+' : ''}${data.percent_change_needed}%</span>
                    </div>
                `;
            } else {
                resultPanel.innerHTML = `<div style="color:var(--accent-pink); text-align:center;">${data.error}</div>`;
            }
        } catch (e) {
            console.error('Goal seek computation error:', e);
            resultPanel.innerHTML = '<div style="color:var(--accent-pink); text-align:center;">Network request failed.</div>';
        }
    }

    // ═══════════════════════════════════════════════════════
    // EXPLORATORY DATA ANALYSIS (SQL CONSOLE SANDBOX)
    // ═══════════════════════════════════════════════════════
    function loadSQLConsoleData() {
        // Load default template when opening the tab
        loadQueryTemplate(1);
    }

    function loadQueryTemplate(id) {
        const queryText = document.getElementById('sqlQueryText');
        const templates = {
            1: "SELECT category, COUNT(*) as sales_count, ROUND(SUM(total_price), 2) as category_revenue, ROUND(AVG(total_price), 2) as average_ticket\nFROM sales\nGROUP BY category\nORDER BY category_revenue DESC;",
            2: "SELECT mode_of_payment, COUNT(*) as txn_count, ROUND(SUM(total_price), 2) as total_volume\nFROM sales\nGROUP BY mode_of_payment\nORDER BY txn_count DESC;",
            3: "SELECT id, sale_date, product_name, customer_name, total_price\nFROM sales\nWHERE total_price >= 100000\nORDER BY total_price DESC;",
            4: "SELECT customer_name, mobile_no, COUNT(*) as purchase_frequency, ROUND(SUM(total_price), 2) as total_lifetime_value\nFROM sales\nGROUP BY customer_name\nORDER BY total_lifetime_value DESC\nLIMIT 5;",
            5: "SELECT strftime('%Y-%m', sale_date) as sales_month, COUNT(*) as orders_count, ROUND(SUM(total_price), 2) as monthly_revenue\nFROM sales\nGROUP BY sales_month\nORDER BY sales_month ASC;"
        };
        queryText.value = templates[id] || "";
        document.getElementById('sqlErrorLog').style.display = 'none';
    }

    async function runConsoleQuery() {
        const query = document.getElementById('sqlQueryText').value;
        const errLog = document.getElementById('sqlErrorLog');
        const rHeader = document.getElementById('sqlResultHeader');
        const rBody = document.getElementById('sqlResultBody');

        errLog.style.display = 'none';
        rHeader.innerHTML = '<th>No query run</th>';
        rBody.innerHTML = '<tr><td class="empty-state"><div class="spinner" style="width:20px; height:20px; margin:0 auto;"></div> Running query...</td></tr>';

        try {
            const res = await fetch(API_BASE + '/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await res.json();

            if (res.ok) {
                // Render table headers
                rHeader.innerHTML = '';
                data.columns.forEach(col => {
                    const th = document.createElement('th');
                    th.textContent = col;
                    rHeader.appendChild(th);
                });

                // Render table rows
                rBody.innerHTML = '';
                if (data.rows.length === 0) {
                    rBody.innerHTML = `<tr><td colspan="${data.columns.length}" class="empty-state">Query executed successfully. 0 records returned.</td></tr>`;
                    return;
                }

                data.rows.forEach((row, rIdx) => {
                    const tr = document.createElement('tr');
                    data.columns.forEach(col => {
                        const td = document.createElement('td');
                        const val = row[col];
                        
                        // Format currency values dynamically if column looks like revenue/price
                        if (typeof val === 'number' && (col.includes('price') || col.includes('revenue') || col.includes('value') || col.includes('ticket'))) {
                            td.textContent = currencyFormatter.format(val);
                            td.className = 'money-cell';
                        } else {
                            td.textContent = val !== null ? val : 'NULL';
                        }
                        tr.appendChild(td);
                    });
                    rBody.appendChild(tr);
                });
            } else {
                rHeader.innerHTML = '<th>Query Error</th>';
                rBody.innerHTML = '<tr><td class="empty-state" style="color:var(--accent-pink);">SQLite compilation failed. Check diagnostic log above.</td></tr>';
                errLog.style.display = 'block';
                errLog.textContent = data.error || "Unknown server response.";
            }
        } catch (e) {
            console.error('SQL Console execute error:', e);
            rHeader.innerHTML = '<th>Network Error</th>';
            rBody.innerHTML = '<tr><td class="empty-state" style="color:var(--accent-pink);">Request failed. Check backend Flask state.</td></tr>';
        }
    }

    // ═══════════════════════════════════════════════════════
    // RFM COHORT MARKETING LOOKUP TABLES
    // ═══════════════════════════════════════════════════════
    function renderRFMLookupTable(data, segmentName = 'ALL') {
        const tbody = document.querySelector('#rfmLookupTable tbody');
        tbody.innerHTML = '';

        // Calculate cohort profiling statistics
        const size = data.length;
        const totalVal = data.reduce((acc, curr) => acc + curr.monetary, 0);
        const totalOrders = data.reduce((acc, curr) => acc + curr.frequency, 0);
        const avgOrderVal = totalOrders > 0 ? (totalVal / totalOrders) : 0;

        document.getElementById('cohort-size-txt').textContent = size.toLocaleString('en-IN') + ' accounts';
        document.getElementById('cohort-value-txt').textContent = currencyFormatter.format(totalVal);
        document.getElementById('cohort-aov-txt').textContent = currencyFormatter.format(avgOrderVal);

        // Map cohorts to strategic prescriptions
        const strategies = {
            'ALL': "Select a specific cohort segment from the dropdown filter to retrieve business intelligence profiling and data-driven marketing strategy prescriptions.",
            'Champions': "💎 <strong>Prescription</strong>: Best customers. Target with VIP rewards, exclusive early access to new MacBook/iPhone releases, and premium status benefits. Do not offer discount campaigns; focus on luxury service.",
            'Loyal Customers': "⭐ <strong>Prescription</strong>: High-value baseline. Offer bundle accessories (Keychron keyboards, Logitech gaming mice, high-res monitors) or offer bundle pricing to increase average transaction sizes.",
            'Potential Loyalists': "📈 <strong>Prescription</strong>: Promising buyers. Push recommendations for their second/third product orders. Offer short-term vouchers (e.g. Rs. 2,000 off next monitor or accessory) to build retention.",
            'New Customers': "🌱 <strong>Prescription</strong>: Fresh accounts. Trigger a 3-part onboarding email detailing setup guides, warranties, and basic accessories, keeping our brand top of mind.",
            'At Risk': "⚠️ <strong>Prescription</strong>: High churn probability! Automatically trigger a reactivation discount code (e.g., 12% off any new mobile or tablet) to capture attention before competitor acquisition.",
            'Cannot Lose': "🚨 <strong>Prescription</strong>: High-spending historic accounts about to churn. Proactively send a personalized outreach email from customer relations offering a complimentary VIP service package.",
            'Lost': "💤 <strong>Prescription</strong>: Churn confirmed. Minimize direct advertising spend. Re-engage only during seasonal clearance sales or deep-discount holiday catalogs."
        };
        document.getElementById('cohort-strategy-txt').innerHTML = strategies[segmentName] || strategies['ALL'];

        if (size === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><div class="icon">🔍</div>No customers in this cohort matching query.</td></tr>';
            return;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="product-cell">${item.customer_name}</td>
                <td><span class="badge badge-mobile">${item.mobile_no || 'N/A'}</span></td>
                <td><span class="badge" style="background: rgba(245, 158, 11, 0.08); color: var(--accent-amber);">${item.segment}</span></td>
                <td style="font-family: 'JetBrains Mono', monospace;">${item.recency_days.toFixed(0)}d ago</td>
                <td style="font-family: 'JetBrains Mono', monospace;">${item.frequency} orders</td>
                <td class="money-cell">${currencyFormatter.format(item.monetary)}</td>
                <td class="money-cell">${currencyFormatter.format(item.avg_order)}</td>
                <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--accent-violet);">${item.rfm_score}/15</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function filterRFMTable(cohort) {
        if (cohort === 'ALL') {
            renderRFMLookupTable(rfmCustomerList, 'ALL');
        } else {
            const filtered = rfmCustomerList.filter(c => c.segment === cohort);
            renderRFMLookupTable(filtered, cohort);
        }
    }

    // ═══════════════════════════════════════════════════════
    // DATA SIMULATION SANDBOX CONTROLS
    // ═══════════════════════════════════════════════════════
    function openSimModal() {
        document.getElementById('simModal').classList.add('active');
    }

    function closeSimModal() {
        document.getElementById('simModal').classList.remove('active');
    }

    // Modal overlay click listener
    document.getElementById('simModal').addEventListener('click', function(e) {
        if (e.target === this) closeSimModal();
    });

    document.getElementById('simDataForm').addEventListener('submit', async e => {
        e.preventDefault();

        const payload = {
            n_records: parseInt(document.getElementById('sim_records').value),
            trend: document.getElementById('sim_trend').value,
            anomaly_rate: parseFloat(document.getElementById('sim_anomaly').value) / 100
        };

        showToast('⚡ Rebuilding SQLite database and simulating sales...', false);
        closeSimModal();

        try {
            const res = await fetch(API_BASE + '/api/simulation/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const info = await res.json();
                showToast(`✅ Database Rebuilt: simulated ${info.records_count} records!`);
                
                // Refresh active tab views
                if (activeTab === 'dashboard') {
                    loadDashboardData();
                } else {
                    loadAnalyticsData();
                }
            } else {
                showToast('⚠️ Simulation generation failed on server.', true);
            }
        } catch (e) {
            showToast('⚠️ Connection error during data generation sandbox.', true);
        }
    });

    // ═══════════════════════════════════════════════════════
    // AI CHURN PREDICTION ENGINE
    // ═══════════════════════════════════════════════════════
    
    window.triggerRetentionAction = function(customer, action) {
        showToast(`⚡ Retention action "${action}" triggered for ${customer}!`);
    };

    window.loadChurnData = async function() {
        const start = document.getElementById('churn_start_date').value;
        const end = document.getElementById('churn_end_date').value;
        const region = document.getElementById('churn_region').value;
        const salesperson = document.getElementById('churn_salesperson').value;

        let query = `?start_date=${start}&end_date=${end}&region=${region}&salesperson=${salesperson}`;
        
        try {
            const response = await fetch(API_BASE + '/api/analytics/churn' + query);
            const data = await response.json();
            
            if (data.error) {
                showToast('⚠️ Error: ' + data.error, true);
                return;
            }

            // Update Metrics
            document.getElementById('churn-metric-total').textContent = data.summary.total;
            document.getElementById('churn-metric-high').textContent = data.summary.high_risk;
            document.getElementById('churn-metric-med').textContent = data.summary.med_risk;
            document.getElementById('churn-metric-low').textContent = data.summary.low_risk;

            // Render Table Rows
            const tbody = document.getElementById('churnTableBody');
            tbody.innerHTML = '';
            
            if (data.customers.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No customer records match the selected filters.</td></tr>';
            } else {
                data.customers.forEach(c => {
                    let badgeClass = 'badge-secondary';
                    let badgeStyle = '';
                    if (c.risk_category === 'High Risk') {
                        badgeStyle = 'background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.3);';
                    } else if (c.risk_category === 'Medium Risk') {
                        badgeStyle = 'background: rgba(245, 158, 11, 0.15); color: var(--accent-orange); border: 1px solid rgba(245, 158, 11, 0.3);';
                    } else {
                        badgeStyle = 'background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3);';
                    }

                    const row = `
                        <tr>
                            <td><strong>${c.customer_name}</strong></td>
                            <td>${c.last_purchase_date}</td>
                            <td>${c.total_orders}</td>
                            <td>Rs. ${c.lifetime_value.toLocaleString('en-IN')}</td>
                            <td><span style="font-weight:600;">${c.churn_risk_score}%</span></td>
                            <td><span class="badge" style="${badgeStyle}">${c.risk_category}</span></td>
                            <td style="font-size:12px; font-style:italic; max-width:250px; white-space:normal; line-height:1.4;">${c.ai_reason}</td>
                            <td>
                                <button class="btn btn-secondary" style="font-size:10px; padding: 4px 8px;" onclick="triggerRetentionAction('${c.customer_name}', '${c.recommended_action}')">
                                    ⚙️ ${c.recommended_action}
                                </button>
                            </td>
                        </tr>
                    `;
                    tbody.insertAdjacentHTML('beforeend', row);
                });
            }

            // Render Charts
            // 1. Churn Pie Chart
            if (charts.churnPie) charts.churnPie.destroy();
            const ctxPie = document.getElementById('churnPieChart').getContext('2d');
            charts.churnPie = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                    datasets: [{
                        data: data.charts.pie,
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } }
                    }
                }
            });

            // 2. Churn Bar Chart
            if (charts.churnBar) charts.churnBar.destroy();
            const ctxBar = document.getElementById('churnBarChart').getContext('2d');
            charts.churnBar = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                    datasets: [{
                        label: 'Avg LTV (Rs. )',
                        data: data.charts.bar_ltv,
                        backgroundColor: ['rgba(16, 185, 129, 0.4)', 'rgba(245, 158, 11, 0.4)', 'rgba(239, 68, 68, 0.4)'],
                        borderColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // 3. Churn Line Chart
            if (charts.churnLine) charts.churnLine.destroy();
            const ctxLine = document.getElementById('churnLineChart').getContext('2d');
            charts.churnLine = new Chart(ctxLine, {
                type: 'line',
                data: {
                    labels: data.charts.trend.labels,
                    datasets: [{
                        label: 'Average Risk %',
                        data: data.charts.trend.values,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });

        } catch (error) {
            console.error('Error fetching churn analysis:', error);
            showToast('⚠️ Connection error reaching Churn Risk engine.', true);
        }
    };


    // ═══════════════════════════════════════════════════════
    // WEATHER-BASED SALES PREDICTIONS
    // ═══════════════════════════════════════════════════════
    
    window.loadWeatherForecast = async function() {
        const city = document.getElementById('weather_city').value;
        
        try {
            const response = await fetch(API_BASE + `/api/analytics/weather-predict?city=${city}`);
            const data = await response.json();
            
            if (data.error) {
                showToast('⚠️ Error: ' + data.error, true);
                return;
            }

            // Update Weather Information
            document.getElementById('weather-temp').textContent = `${data.temperature}°C`;
            document.getElementById('weather-forecast').textContent = data.forecast;
            document.getElementById('weather-impact').textContent = data.sales_impact;
            document.getElementById('weather-ai-insights').textContent = `"${data.ai_insights}"`;

            // Update Weather Icon
            let icon = '🌦️';
            const cond = data.current_weather;
            if (cond === 'Clear') icon = '☀️';
            else if (cond === 'Rain') icon = '🌧️';
            else if (cond === 'Clouds') icon = '☁️';
            else if (cond === 'Snow') icon = '❄️';
            else if (cond === 'Haze' || cond === 'Mist') icon = '🌫️';
            document.getElementById('weather-icon').textContent = icon;

            // Update Recommended Products badges
            const recsDiv = document.getElementById('weather-recs');
            recsDiv.innerHTML = '';
            data.recommended_products.forEach(p => {
                recsDiv.insertAdjacentHTML('beforeend', `<span class="badge badge-primary" style="font-size:12px; margin-right:6px; background:rgba(139,92,246,0.15); color:var(--accent-purple); border:1px solid rgba(139,92,246,0.3);">${p}</span>`);
            });

            // Render Charts
            // 1. Weather vs Sales Chart
            if (charts.weatherSales) charts.weatherSales.destroy();
            const ctxWS = document.getElementById('weatherSalesChart').getContext('2d');
            charts.weatherSales = new Chart(ctxWS, {
                type: 'bar',
                data: {
                    labels: data.charts.weather_vs_sales.labels,
                    datasets: [{
                        label: 'Revenue (Rs. )',
                        data: data.charts.weather_vs_sales.values,
                        backgroundColor: '#60a5fa',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // 2. Temp vs Revenue Scatter/Line Chart
            if (charts.tempRevenue) charts.tempRevenue.destroy();
            const ctxTR = document.getElementById('tempRevenueChart').getContext('2d');
            charts.tempRevenue = new Chart(ctxTR, {
                type: 'line',
                data: {
                    labels: data.charts.temp_vs_revenue.temps.map(t => `${t}°C`),
                    datasets: [{
                        label: 'Average Revenue (Rs. )',
                        data: data.charts.temp_vs_revenue.revenues,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.08)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // 3. Seasonal Product Demand Chart
            if (charts.seasonalDemand) charts.seasonalDemand.destroy();
            const ctxSD = document.getElementById('seasonalDemandChart').getContext('2d');
            charts.seasonalDemand = new Chart(ctxSD, {
                type: 'bar',
                data: {
                    labels: data.charts.seasonal_demand.seasons,
                    datasets: [
                        {
                            label: 'Electronics',
                            data: data.charts.seasonal_demand.electronics,
                            backgroundColor: '#8b5cf6'
                        },
                        {
                            label: 'Wearables',
                            data: data.charts.seasonal_demand.wearables,
                            backgroundColor: '#10b981'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { stacked: true, grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { stacked: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: true, labels: { color: '#94a3b8' } } }
                }
            });

        } catch (error) {
            console.error('Error fetching weather forecasting:', error);
            showToast('⚠️ Connection error reaching weather forecasting module.', true);
        }
    };

    // APP TRIGGER (STARTUP)
    // ═══════════════════════════════════════════════════════

    // Initial routing setup
    const initialHash = window.location.hash.replace('#', '');
    if (initialHash === 'analytics' || initialHash === 'sql' || initialHash === 'churn' || initialHash === 'weather') {
        switchTab(initialHash);
    } else {
        loadDashboardData();
    }
