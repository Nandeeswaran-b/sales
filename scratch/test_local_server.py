import requests, time

# Wait a moment for server to start
time.sleep(2)

base_url = 'http://localhost:5000'

print("Testing local endpoints...")

# 1. GET summary
try:
    r = requests.get(base_url + '/api/summary', timeout=5)
    print("  Local Summary status:", r.status_code)
    print("  Local Summary response:", r.text[:150])
except Exception as e:
    print("  Local Summary error:", e)

# 2. POST query
try:
    q = "SELECT category, COUNT(*) as sales_count, SUM(total_price) as category_revenue FROM sales GROUP BY category;"
    r = requests.post(base_url + '/api/query', json={'query': q}, timeout=5)
    print("  Local Query status:", r.status_code)
    print("  Local Query response:", r.text[:150])
except Exception as e:
    print("  Local Query error:", e)

# 3. POST simulation/generate
try:
    payload = {
        'n_records': 100,
        'trend': 'positive',
        'anomaly_rate': 0.05
    }
    r = requests.post(base_url + '/api/simulation/generate', json=payload, timeout=10)
    print("  Local Simulation status:", r.status_code)
    print("  Local Simulation response:", r.text[:150])
except Exception as e:
    print("  Local Simulation error:", e)
