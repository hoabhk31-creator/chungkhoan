import requests, time, datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://stockchart.vietstock.vn/'
}
now = int(time.time())
start = now - 86400 * 30

# 1. Vietstock Chart API
r_vs = requests.get(f'https://api.vietstock.vn/tvnew/history?symbol=HPG&resolution=D&from={start}&to={now}', headers=headers, timeout=5)
data_vs = r_vs.json()
print("Vietstock count:", len(data_vs.get('t', [])))
if data_vs.get('t'):
    last_t_vs = data_vs['t'][-1]
    last_c_vs = data_vs['c'][-1]
    dt_vs = datetime.datetime.fromtimestamp(last_t_vs)
    print(f"Vietstock Latest: Time={dt_vs} (ts={last_t_vs}), Close={last_c_vs}")

# 2. VNDirect Chart API
r_vnd = requests.get(f'https://dchart-api.vndirect.com.vn/dchart/history?resolution=D&symbol=HPG&from={start}&to={now}', headers=headers, timeout=5)
data_vnd = r_vnd.json()
if data_vnd.get('t'):
    last_t_vnd = data_vnd['t'][-1]
    last_c_vnd = data_vnd['c'][-1] * 1000 if data_vnd['c'][-1] < 1000 else data_vnd['c'][-1]
    dt_vnd = datetime.datetime.fromtimestamp(last_t_vnd)
    print(f"VNDirect Latest: Time={dt_vnd} (ts={last_t_vnd}), Close={last_c_vnd}")

# 3. DNSE/Entrade
r_dnse = requests.get(f'https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from={start}&to={now}&symbol=HPG&resolution=1D', headers=headers, timeout=5)
data_dnse = r_dnse.json()
if data_dnse.get('t'):
    last_t_dnse = data_dnse['t'][-1]
    last_c_dnse = data_dnse['c'][-1] * 1000 if data_dnse['c'][-1] < 1000 else data_dnse['c'][-1]
    dt_dnse = datetime.datetime.fromtimestamp(last_t_dnse)
    print(f"DNSE Latest: Time={dt_dnse} (ts={last_t_dnse}), Close={last_c_dnse}")
