import requests, time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://stockchart.vietstock.vn/'
}

now = int(time.time())
start = now - 86400 * 15

urls = [
    f'https://api.vietstock.vn/tvnew/history?symbol=HPG&resolution=D&from={start}&to={now}',
    f'https://stockchart.vietstock.vn/api/history?symbol=HPG&resolution=D&from={start}&to={now}',
    f'https://dchart-api.vndirect.com.vn/dchart/history?resolution=D&symbol=HPG&from={start}&to={now}',
    f'https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from={start}&to={now}&symbol=HPG&resolution=1D'
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=5)
        print("URL:", u.split("?")[0])
        print("Status:", r.status_code)
        if r.status_code == 200:
            print("Response:", str(r.json())[:200])
    except Exception as e:
        print("Error for", u.split("?")[0], ":", e)
