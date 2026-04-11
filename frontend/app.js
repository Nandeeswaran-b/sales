// app.js - Main Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
    const supabase = window.supabaseClient;
    
    // State
    const state = {
        theme: localStorage.getItem('theme') || 'light',
        dateRange: '30',
        searchQuery: '',
        searchDate: '',
        customers: [],
        orders: [],
        dailyCustomersCount: 0
    };

    // DOM Elements
    const themeToggle = document.getElementById('theme-toggle');
    const clockEl = document.getElementById('clock');
    const openModalBtn = document.getElementById('open-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    const addCustomerForm = document.getElementById('add-customer-form');
    const dateRangeFilter = document.getElementById('date-range-filter');
    const customerSearch = document.getElementById('customer-search');
    const customerDateSearch = document.getElementById('customer-date-search');
    const clearDateBtn = document.getElementById('clear-date');
    const profileModalOverlay = document.getElementById('profile-modal-overlay');
    const closeProfileModalBtn = document.getElementById('close-profile-modal');
    const profileContent = document.getElementById('profile-content');
    const exportCsvBtn = document.getElementById('export-csv');
    const toastContainer = document.getElementById('toast-container');
    const kpiRevenue = document.getElementById('kpi-revenue');
    const kpiOrders = document.getElementById('kpi-orders');
    const kpiCustomers = document.getElementById('kpi-customers');
    const kpiAov = document.getElementById('kpi-aov');
    const dailyCountEl = document.getElementById('daily-customers-count');

    // --- Core Functions ---

    function init() {
        applyTheme();
        updateClock();
        setInterval(updateClock, 1000);
        window.initCharts();
        fetchData();
        setupEventListeners();
    }

    // Theme logic
    function applyTheme() {
        document.documentElement.setAttribute('data-theme', state.theme);
        const icon = themeToggle.querySelector('i');
        if (state.theme === 'dark') {
            icon.classList.replace('fa-moon', 'fa-sun');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
        }
    }

    function toggleTheme() {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', state.theme);
        applyTheme();
    }

    // Clock
    function updateClock() {
        const now = new Date();
        clockEl.textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
    }

    // Toast
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
            <span>${message}</span>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- Data Fetching ---

    async function fetchData() {
        showSkeletons(true);
        try {
            // Calculate date threshold for filtering
            let dateThreshold = null;
            if (state.dateRange !== 'all') {
                const d = new Date();
                d.setDate(d.getDate() - parseInt(state.dateRange));
                dateThreshold = d.toISOString().split('T')[0];
            }

            // Fetch Customers (with search)
            let query = supabase.from('customers').select('*');
            if (state.searchQuery) {
                query = query.or(`name.ilike.%${state.searchQuery}%,city.ilike.%${state.searchQuery}%,phone.ilike.%${state.searchQuery}%`);
            }
            if (state.searchDate) {
                query = query.eq('date_joined', state.searchDate);
            }
            const { data: customers, error: custError } = await query.order('total_purchase_amount', { ascending: false });
            if (custError) throw custError;

            // Fetch Orders (with date range)
            let orderQuery = supabase.from('orders').select('*');
            if (dateThreshold) {
                orderQuery = orderQuery.gte('order_date', dateThreshold);
            }
            const { data: orders, error: orderError } = await orderQuery.order('order_date', { ascending: false });
            if (orderError) throw orderError;

            // Update State
            state.customers = customers;
            state.orders = orders;

            // Update Daily Count (customers added today)
            const today = new Date().toISOString().split('T')[0];
            const { count } = await supabase.from('customers')
                .select('*', { count: 'exact', head: true })
                .gte('created_at', today);
            state.dailyCustomersCount = count || 0;

            updateUI();
        } catch (err) {
            console.error('Fetch error:', err);
            showToast('Error loading data: ' + err.message, 'error');
        } finally {
            showSkeletons(false);
        }
    }

    // --- UI Updates ---

    function updateUI() {
        updateKPIs();
        updateTables();
        updateDailyBadge();
        
        // Prepare data for charts (simplified logic)
        const chartData = prepareChartData();
        window.updateCharts(chartData);

        // Notify if no results
        if (state.customers.length === 0 && state.searchQuery) {
            showToast('No customers found matching your search', 'error');
        }
    }

    function updateKPIs() {
        const revenue = state.orders.reduce((sum, o) => sum + parseFloat(o.order_amount), 0);
        const count = state.orders.length;
        const avg = count > 0 ? revenue / count : 0;

        kpiRevenue.textContent = `$${revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
        kpiOrders.textContent = count.toLocaleString();
        kpiCustomers.textContent = state.customers.length.toLocaleString();
        kpiAov.textContent = `$${avg.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
    }

    function updateTables() {
        // Top 5 Customers
        const topBody = document.getElementById('top-customers-body');
        topBody.innerHTML = state.customers.slice(0, 5).map(c => `
            <tr class="clickable-row" data-id="${c.id}" title="Click to view profile">
                <td><strong>${c.name}</strong></td>
                <td>${c.phone}</td>
                <td title="${c.purchase_category || 'N/A'}">${(c.purchase_category || 'N/A').substring(0, 15)}${(c.purchase_category || '').length > 15 ? '...' : ''}</td>
                <td>${c.payment_mode || 'Cash'}</td>
                <td><span class="status-badge ${c.payment_plan === 'EMI' ? 'status-pending' : 'status-completed'}">${c.payment_plan || 'Ready Cash'}</span></td>
                <td>$${parseFloat(c.total_purchase_amount).toLocaleString()}</td>
            </tr>
        `).join('');

        // Recent Orders
        const recentBody = document.getElementById('recent-orders-body');
        recentBody.innerHTML = state.orders.slice(0, 10).map(o => {
            const custName = state.customers.find(c => c.id === o.customer_id)?.name || 'Unknown';
            return `
                <tr>
                    <td>${new Date(o.order_date).toLocaleDateString()}</td>
                    <td>${custName}</td>
                    <td>${o.product_category}</td>
                    <td>$${parseFloat(o.order_amount).toLocaleString()}</td>
                    <td><span class="status-badge status-${o.status.toLowerCase()}">${o.status}</span></td>
                </tr>
            `;
        }).join('');
    }

    function updateDailyBadge() {
        dailyCountEl.textContent = state.dailyCustomersCount;
    }

    function prepareChartData() {
        // This would ideally call the Flask API for complex growth metrics,
        // but for now we calculate basic stats for visualization.
        
        const categories = {
            'Electronics': 0, 'Clothing': 0, 'Food': 0, 'Furniture': 0, 'Sports': 0
        };
        state.orders.forEach(o => {
            if (categories.hasOwnProperty(o.product_category)) {
                categories[o.product_category] += parseFloat(o.order_amount);
            }
        });

        // Group by day for simple trend
        const dailyOrders = {};
        state.orders.forEach(o => {
            const date = o.order_date;
            dailyOrders[date] = (dailyOrders[date] || 0) + 1;
        });

        return {
            monthly: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                values: [1200, 1900, 3000, 5000, 2000, 3000] // Mock monthly
            },
            trend: {
                labels: Object.keys(dailyOrders).sort(),
                values: Object.keys(dailyOrders).sort().map(k => dailyOrders[k])
            },
            categories: Object.values(categories),
            growth: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                values: [1000, 2500, 3800, 5200] // Mock growth
            }
        };
    }

    function showSkeletons(show) {
        const cards = document.querySelectorAll('.kpi-card, .chart-card, .table-card');
        cards.forEach(c => {
            if (show) c.classList.add('skeleton');
            else c.classList.remove('skeleton');
        });
    }

    // --- Form Handling & Validation ---

    function validateForm(data) {
        let isValid = true;
        const errs = document.querySelectorAll('.error-msg');
        errs.forEach(e => e.style.display = 'none');

        if (!data.name) {
            document.getElementById('err-name').style.display = 'block';
            isValid = false;
        }
        if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
            document.getElementById('err-email').style.display = 'block';
            isValid = false;
        }
        if (!data.phone || data.phone.length !== 10) {
            document.getElementById('err-phone').style.display = 'block';
            isValid = false;
        }
        if (!data.city) {
            document.getElementById('err-city').style.display = 'block';
            isValid = false;
        }

        return isValid;
    }

    async function handleAddCustomer(e) {
        e.preventDefault();

        // Get selected categories
        const selectedCategories = Array.from(document.querySelectorAll('#cust-categories input:checked'))
            .map(cb => cb.value)
            .join(', ');

        const data = {
            name: document.getElementById('cust-name').value,
            email: document.getElementById('cust-email').value,
            phone: document.getElementById('cust-phone').value,
            city: document.getElementById('cust-city').value,
            total_purchase_amount: parseFloat(document.getElementById('cust-amount').value) || 0,
            date_joined: document.getElementById('cust-date').value || new Date().toISOString().split('T')[0],
            purchase_category: selectedCategories || 'Other',
            payment_mode: document.getElementById('cust-payment-mode').value,
            payment_plan: document.querySelector('input[name="payment-plan"]:checked').value
        };

        if (!validateForm(data)) return;

        try {
            const { error } = await supabase.from('customers').insert([data]);
            if (error) throw error;

            showToast('Customer added successfully ✓');
            addCustomerForm.reset();
            modalOverlay.classList.remove('active');
            fetchData(); // Refresh
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // --- Profile Logic ---

    async function showCustomerProfile(customerId) {
        const customer = state.customers.find(c => c.id === customerId);
        if (!customer) return;

        showSkeletons(true);
        try {
            const { data: customerOrders, error } = await supabase
                .from('orders')
                .select('*')
                .eq('customer_id', customerId)
                .order('order_date', { ascending: false });

            if (error) throw error;

            profileContent.innerHTML = `
                <div class="profile-grid">
                    <div class="profile-card">
                        <h4>Contact Details</h4>
                        <p><i class="fa-solid fa-user"></i> ${customer.name}</p>
                        <p><i class="fa-solid fa-envelope"></i> ${customer.email}</p>
                        <p><i class="fa-solid fa-phone"></i> ${customer.phone || 'N/A'}</p>
                        <p><i class="fa-solid fa-location-dot"></i> ${customer.city || 'N/A'}</p>
                    </div>
                    <div class="profile-card">
                        <h4>Payment Summary</h4>
                        <p><i class="fa-solid fa-indian-rupee-sign"></i> Total: $${parseFloat(customer.total_purchase_amount).toLocaleString()}</p>
                        <p><i class="fa-solid fa-credit-card"></i> Mode: ${customer.payment_mode || 'Cash'}</p>
                        <p><i class="fa-solid fa-money-bill-transfer"></i> Plan: ${customer.payment_plan || 'Ready Cash'}</p>
                        <p><i class="fa-solid fa-calendar"></i> Joined: ${new Date(customer.date_joined).toLocaleDateString()}</p>
                    </div>
                </div>
                <h4>Recent Orders</h4>
                <div class="order-history-container">
                    <table style="width:100%; text-align:left; font-size:0.875rem;">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Category</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${customerOrders.length > 0 ? customerOrders.map(o => `
                                <tr>
                                    <td>${new Date(o.order_date).toLocaleDateString()}</td>
                                    <td>${o.product_category}</td>
                                    <td>$${parseFloat(o.order_amount).toLocaleString()}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="3" style="text-align:center;">No orders found</td></tr>'}
                        </tbody>
                    </table>
                </div>
            `;
            
            profileModalOverlay.style.display = 'flex';
            setTimeout(() => profileModalOverlay.classList.add('active'), 0);
        } catch (err) {
            showToast('Error fetching profile: ' + err.message, 'error');
        } finally {
            showSkeletons(false);
        }
    }

    // --- Utils ---

    function exportToCSV() {
        const headers = ['Name', 'Email', 'Phone', 'City', 'Total Purchase', 'Date Joined'];
        const rows = state.customers.map(c => [
            c.name, c.email, c.phone, c.city, c.total_purchase_amount, c.date_joined
        ]);

        const csvContent = "data:text/csv;charset=utf-8," 
            + headers.join(",") + "\n"
            + rows.map(r => r.join(",")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `customers_export_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // --- Events ---

    function setupEventListeners() {
        themeToggle.addEventListener('click', toggleTheme);
        
        openModalBtn.addEventListener('click', () => {
            modalOverlay.style.display = 'flex';
            setTimeout(() => modalOverlay.classList.add('active'), 0);
            document.getElementById('cust-date').value = new Date().toISOString().split('T')[0];
        });

        closeModalBtn.addEventListener('click', () => {
            modalOverlay.classList.remove('active');
            setTimeout(() => modalOverlay.style.display = 'none', 300);
        });

        window.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('active');
                setTimeout(() => modalOverlay.style.display = 'none', 300);
            }
        });

        addCustomerForm.addEventListener('submit', handleAddCustomer);

        dateRangeFilter.addEventListener('change', (e) => {
            state.dateRange = e.target.value;
            fetchData();
        });

        let searchTimeout;
        customerSearch.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            state.searchQuery = e.target.value;
            searchTimeout = setTimeout(fetchData, 500); // Debounce
        });

        customerDateSearch.addEventListener('change', (e) => {
            state.searchDate = e.target.value;
            clearDateBtn.style.display = state.searchDate ? 'inline-block' : 'none';
            fetchData();
        });

        clearDateBtn.addEventListener('click', () => {
            customerDateSearch.value = '';
            state.searchDate = '';
            clearDateBtn.style.display = 'none';
            fetchData();
        });

        closeProfileModalBtn.addEventListener('click', () => {
            profileModalOverlay.classList.remove('active');
            setTimeout(() => profileModalOverlay.style.display = 'none', 300);
        });

        profileModalOverlay.addEventListener('click', (e) => {
            if (e.target === profileModalOverlay) {
                profileModalOverlay.classList.remove('active');
                setTimeout(() => profileModalOverlay.style.display = 'none', 300);
            }
        });

        document.getElementById('top-customers-body').addEventListener('click', (e) => {
            const row = e.target.closest('.clickable-row');
            if (row) {
                showCustomerProfile(row.dataset.id);
            }
        });

        exportCsvBtn.addEventListener('click', exportToCSV);
    }

    init();
});
