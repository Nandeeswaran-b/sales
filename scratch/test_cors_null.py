import requests

base_url = 'https://sales-backend-k5rw.onrender.com'

# Test OPTIONS preflight for Origin: null (local file:// protocol)
try:
    headers = {
        'Origin': 'null',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    r = requests.options(base_url + '/api/query', headers=headers, timeout=10)
    print("OPTIONS /api/query (null origin) status:", r.status_code)
    print("Headers:")
    for k, v in r.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print("OPTIONS error:", e)
