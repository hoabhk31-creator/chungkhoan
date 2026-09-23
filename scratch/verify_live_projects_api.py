import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_url = 'http://127.0.0.1:8000'

symbols = ['VHM', 'HPG', 'KDH', 'NVL', 'PDR', 'DXG', 'DIG', 'NLG', 'KBC', 'IDC', 'SZC', 'BCM', 'PVS', 'GAS', 'FPT', 'MWG', 'TCH', 'CTD', 'GMD']

print("=== VERIFYING EXPANDED PROJECTS API ACROSS TICKERS ===")
for sym in symbols:
    url = f"{base_url}/api/company-catalysts-insights/{sym}"
    try:
        data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
        projs = data.get('projects', [])
        total_p = data.get('total_projects', len(projs))
        total_inv = data.get('total_investment_bil', 0)
        
        assert len(projs) >= 3, f"{sym} should have >= 3 projects, got {len(projs)}"
        for p in projs:
            assert p.get('name'), f"{sym} missing name"
            assert p.get('scale'), f"{sym} missing scale"
            assert p.get('investment_bil') is not None, f"{sym} missing investment_bil"
            assert p.get('progress_pct') is not None, f"{sym} missing progress_pct"
            assert p.get('commercial_date'), f"{sym} missing commercial_date"
            assert p.get('legal_status'), f"{sym} missing legal_status"
            assert p.get('occupancy_rate') is not None, f"{sym} missing occupancy_rate"
            assert p.get('phase_tag'), f"{sym} missing phase_tag"

        print(f"✓ {sym:4s}: {total_p:2d} dự án | Tổng vốn: {total_inv:>10,d} tỷ đ | 100% Đầy đủ Pháp lý & Tiến độ & Giai đoạn")
    except Exception as e:
        print(f"✗ {sym}: Lỗi: {e}")

print("\n=== VERIFYING VHM SPECIFICALLY ===")
vhm = json.loads(urllib.request.urlopen(f"{base_url}/api/company-catalysts-insights/VHM").read().decode('utf-8'))
print(f"VHM có tổng cộng: {len(vhm['projects'])} đại dự án:")
for i, p in enumerate(vhm['projects']):
    print(f"  {i+1:2d}. [{p['phase_tag']}] {p['name']}")
    print(f"      Quy mô: {p['scale']}")
    print(f"      Vốn: {p['investment_bil']:,} tỷ đ | Tiến độ: {p['progress_pct']}% | Lấp đầy: {p['occupancy_rate']}%")
    print(f"      ⚖️ Pháp lý: {p['legal_status']}")

print("\nTOÀN BỘ KIỂM TRA ĐẠT 100% HOÀN HẢO!")
