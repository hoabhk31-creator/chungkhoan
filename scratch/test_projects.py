import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import financial_data

sys.stdout.reconfigure(encoding='utf-8')

for sym in ['VHM', 'HPG', 'KDH', 'NVL', 'PDR', 'DXG', 'DIG', 'NLG', 'KBC', 'IDC', 'SZC', 'BCM', 'PVS', 'GAS', 'FPT', 'MWG', 'TCH', 'UNKNOWN_ABC']:
    res = financial_data.get_company_catalysts_and_projects(sym)
    projs = res.get('projects', [])
    print(f"=== {sym} ({res.get('sector')}) ===")
    print(f"Tổng số dự án: {res.get('total_projects')} | Tổng vốn đầu tư: {res.get('total_investment_bil'):,} tỷ đ")
    for p in projs:
        print(f"  • [{p.get('phase_tag')}] {p.get('name')} | Vốn: {p.get('investment_bil'):,} tỷ | Tiến độ: {p.get('progress_pct')}% | Lấp đầy: {p.get('occupancy_rate')}%")
        print(f"    ⚖️ Pháp lý: {p.get('legal_status')}")
    print()
