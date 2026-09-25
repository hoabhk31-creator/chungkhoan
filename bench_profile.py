import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

ticker = 'NLG'
base_url = 'http://127.0.0.1:8000'

print(f'=== PROFILING ENDPOINTS FOR TICKER {ticker} ===')

for ep in [
    f'/api/technical/{ticker}?resolution=D&count=150',
    f'/api/preset/{ticker}?refresh=true',
    f'/api/financial-overview/{ticker}',
    f'/api/company-reports?ticker={ticker}',
    f'/api/corporate-actions/{ticker}'
]:
    t0 = time.time()
    try:
        r = requests.get(base_url + ep, timeout=45)
        dt = time.time() - t0
        print(f'{ep} -> Status: {r.status_code} | Time: {dt:.2f}s | Size: {len(r.content)} bytes')
    except Exception as e:
        dt = time.time() - t0
        print(f'{ep} -> Error: {e} | Time: {dt:.2f}s')
