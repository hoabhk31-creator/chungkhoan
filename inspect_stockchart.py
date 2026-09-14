import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.vietstock.vn/phan-tich-ky-thuat.htm'
}
try:
    r = requests.get('https://stockchart.vietstock.vn/?stockcode=HPG&lang=vi&isDark=1&isIframe=1', headers=headers, timeout=10)
    print("Stockchart status:", r.status_code)
    matches = re.findall(r'https?://[^\s"\'<>]+|datafeed[^\s"\'<>]+', r.text)
    for m in set(matches):
        if any(k in m.lower() for k in ['chart', 'api', 'data', 'history', 'vietstock', 'feed']):
            print("Match:", m)
except Exception as e:
    print("Error:", e)
