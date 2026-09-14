import requests, time, datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://stockchart.vietstock.vn/'
}
now = int(time.time())
start = now - 86400 * 20

def get_latest_price(symbol):
    # 1. Vietstock
    vs_price = None
    vs_time = 0
    try:
        r = requests.get(f'https://api.vietstock.vn/tvnew/history?symbol={symbol}&resolution=D&from={start}&to={now}', headers=headers, timeout=5)
        d = r.json()
        if d and 't' in d and len(d['t']) > 0:
            vs_time = d['t'][-1]
            vs_price = float(d['c'][-1])
    except Exception as e:
        print(f"Vietstock error for {symbol}:", e)

    # 2. Broker: VNDirect
    vnd_price = None
    vnd_time = 0
    try:
        r = requests.get(f'https://dchart-api.vndirect.com.vn/dchart/history?resolution=D&symbol={symbol}&from={start}&to={now}', headers=headers, timeout=5)
        d = r.json()
        if d and 't' in d and len(d['t']) > 0:
            vnd_time = d['t'][-1]
            raw_c = float(d['c'][-1])
            vnd_price = raw_c * 1000 if raw_c < 1000 else raw_c
    except Exception as e:
        print(f"VNDirect error for {symbol}:", e)

    # 3. Broker: DNSE
    dnse_price = None
    dnse_time = 0
    try:
        r = requests.get(f'https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from={start}&to={now}&symbol={symbol}&resolution=1D', headers=headers, timeout=5)
        d = r.json()
        if d and 't' in d and len(d['t']) > 0:
            dnse_time = d['t'][-1]
            raw_c = float(d['c'][-1])
            dnse_price = raw_c * 1000 if raw_c < 1000 else raw_c
    except Exception as e:
        print(f"DNSE error for {symbol}:", e)

    print(f"Symbol: {symbol}")
    print(f"  Vietstock: price={vs_price}, ts={vs_time} ({datetime.datetime.fromtimestamp(vs_time) if vs_time else 'N/A'})")
    print(f"  VNDirect:  price={vnd_price}, ts={vnd_time} ({datetime.datetime.fromtimestamp(vnd_time) if vnd_time else 'N/A'})")
    print(f"  DNSE:      price={dnse_price}, ts={dnse_time} ({datetime.datetime.fromtimestamp(dnse_time) if dnse_time else 'N/A'})")

    # Compare timestamps and select the newest data
    candidates = []
    if vs_price is not None:
        candidates.append({"source": "Vietstock Chart", "price": vs_price, "timestamp": vs_time})
    if vnd_price is not None:
        candidates.append({"source": "VNDirect Bảng giá/Chart", "price": vnd_price, "timestamp": vnd_time})
    if dnse_price is not None:
        candidates.append({"source": "DNSE Bảng giá/Chart", "price": dnse_price, "timestamp": dnse_time})

    if not candidates:
        return None

    # Sort by timestamp desc
    candidates.sort(key=lambda x: x["timestamp"], reverse=True)
    best = candidates[0]
    print(f"  -> SELECTED NEWEST: {best['source']} | Price = {best['price']:,.0f} VND | Date = {datetime.datetime.fromtimestamp(best['timestamp']).strftime('%d/%m/%Y')}")
    return best

for s in ['HPG', 'FPT', 'MWG']:
    get_latest_price(s)
