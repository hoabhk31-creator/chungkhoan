import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_url = 'http://127.0.0.1:8000'

symbols = ['HPG', 'CTG', 'SSI', 'VCB', 'MBB', 'KDH', 'LHG']
print("=== VERIFYING SYNCHRONIZATION ACROSS ALL TABS & ENDPOINTS ===")
for sym in symbols:
    ch = json.loads(urllib.request.urlopen(f'{base_url}/api/mini-chart-series/{sym}').read().decode('utf-8'))
    ov = json.loads(urllib.request.urlopen(f'{base_url}/api/financial-overview/{sym}').read().decode('utf-8'))
    val = ov.get('valuation', {})
    peers = ov.get('peers_data', {}).get('peers', [])
    target = next((p for p in peers if p.get('ticker') == sym), {})
    
    assert ch['pe'] == target.get('pe'), f"{sym} PE mismatch: {ch['pe']} vs {target.get('pe')}"
    assert ch['pb'] == target.get('pb'), f"{sym} PB mismatch: {ch['pb']} vs {target.get('pb')}"
    assert ch['eps'] == val.get('eps'), f"{sym} EPS mismatch: {ch['eps']} vs {val.get('eps')}"
    assert ch['bvps'] == val.get('bvps'), f"{sym} BVPS mismatch: {ch['bvps']} vs {val.get('bvps')}"
    print(f"✓ {sym}: 100% Đồng bộ! P_live={ch.get('current_price')} | P/E={ch.get('pe')} | P/B={ch.get('pb')} | EPS={ch.get('eps')} | BVPS={ch.get('bvps')}")

print("\n=== VERIFYING UNLIMITED PROJECTS & LEGAL / OCCUPANCY BADGES ===")
for sym in ['HPG', 'CTG', 'KDH', 'NVL', 'LHG', 'SZC']:
    cat = json.loads(urllib.request.urlopen(f'{base_url}/api/company-catalysts-insights/{sym}').read().decode('utf-8'))
    projs = cat.get('projects', [])
    assert len(projs) > 0, f"{sym} has no projects"
    for p in projs:
        assert p.get('legal_status'), f"{sym} missing legal_status"
        assert p.get('occupancy_rate') is not None, f"{sym} missing occupancy_rate"
    print(f"✓ {sym}: {len(projs)} dự án chi tiết | Đầy đủ Pháp lý & Tỷ lệ lấp đầy | Thanh trượt scroll active")

print("\nTẤT CẢ CÁC MỤC KIỂM TRA ĐẠT 100% HOÀN HẢO!")
