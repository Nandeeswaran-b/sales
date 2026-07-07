import requests

base_url = 'https://sales-backend-k5rw.onrender.com'

# Test 1: GET summary
try:
    r = requests.get(base_url + '/api/summary', timeout=10)
    print("Summary status:", r.status_code)
    print("Summary text:", r.text[:200])
except Exception as e:
    print("Summary error:", e)

# Test 2: POST query
try:
    q = "SELECT category, COUNT(*) as sales_count, SUM(total_price) as category_revenue FROM sales GROUP BY category;"
    r = requests.post(base_url + '/api/query', json={'query': q}, timeout=10)
    print("\nQuery status:", r.status_code)
    print("Query response:", r.text[:300])
except Exception as e:
    print("Query error:", e)

# Test 3: POST simulation generate
try:
    payload = {
        'n_records': 100,
        'trend': 'positive',
        'anomaly_rate': 0.05
    }
    r = requests.post(base_url + '/api/simulation/generate', json=payload, timeout=15)
    print("\nSimulation status:", r.status_code)
    print("Simulation response:", r.text[:300])
except Exception as e:
    print("Simulation error:", e)
