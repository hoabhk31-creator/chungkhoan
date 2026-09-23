import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

tickers = ['VHM', 'HPG', 'KDH', 'NVL', 'PVS', 'MWG', 'TLG', 'VNM', 'MSN', 'REE', 'VRE', 'DGW']
print("=== KIEM TRA DANH MUC DU AN TRONG DIEM & DISCOVERY ENGINE ===")
for t in tickers:
    url = f"http://127.0.0.1:8000/api/company-catalysts-insights/{t}"
    try:
        with urllib.request.urlopen(url) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            projs = d.get('projects', [])
            total_inv = sum(float(p.get('investment_bil', 0) or 0) for p in projs)
            sample = projs[0].get("name", "N/A") if projs else "Chua co"
            source = projs[0].get("source", "N/A") if projs else "N/A"
            print(f"[{t}] So luong: {len(projs):2} du an | Tong von: {total_inv:>12,.0f} ty | Nguon mau: {source} | Du an: {sample[:40]}")
    except Exception as e:
        print(f"[{t}] Error: {e}")
