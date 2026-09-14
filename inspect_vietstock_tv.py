import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.vietstock.vn/'
}
r = requests.get('https://finance.vietstock.vn/phan-tich-ky-thuat.htm', headers=headers, timeout=10)

lines = r.text.splitlines()
for i, line in enumerate(lines):
    if any(term in line.lower() for term in ['tvwidget', 'tradingview', 'datafeed', 'charting_library', 'symbol:']):
        print(f"L{i}: {line.strip()[:150]}")
