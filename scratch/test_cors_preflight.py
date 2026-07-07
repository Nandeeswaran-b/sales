import requests

base_url = 'https://sales-backend-k5rw.onrender.com'

# Test OPTIONS preflight for /api/query
try:
    headers = {
        'Origin': 'https://sales-henna-beta.vercel.app',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    r = requests.options(base_url + '/api/query', headers=headers, timeout=10)
    print("OPTIONS /api/query status:", r.status_code)
    print("Headers:")
    for k, v in r.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print("OPTIONS /api/query error:", e)

# Test OPTIONS preflight for /api/simulation/generate
try:
    headers = {
        'Origin': 'https://sales-henna-beta.vercel.app',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    r = requests.options(base_url + '/api/simulation/generate', headers=headers, timeout=10)
    print("\nOPTIONS /api/simulation/generate status:", r.status_code)
    print("Headers:")
    for k, v in r.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print("OPTIONS /api/simulation/generate error:", e)
