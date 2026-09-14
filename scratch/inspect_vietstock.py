import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.vietstock.vn/'
}
r = requests.get('https://finance.vietstock.vn/phan-tich-ky-thuat.htm', headers=headers, timeout=10)
print("Status:", r.status_code)

# Check scripts and iframes
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', r.text)
for s in scripts:
    if any(k in s.lower() for k in ['chart', 'tradingview', 'datafeed', 'ptkt']):
        print("Script:", s)

# Check inline config or api endpoints
endpoints = re.findall(r'["\'](/datafeed[^\'"]*|https?://[^\'"]+datafeed[^\'"]*|/api/[^\'"]*|https?://[^\'"]+api[^\'"]*)["\']', r.text)
for ep in set(endpoints):
    print("Endpoint:", ep)
