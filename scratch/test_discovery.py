import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import project_discovery_engine

async def main():
    for sym in ['VHM', 'HPG', 'KDH', 'DIG']:
        print(f"=== DISCOVERING PROJECTS FOR {sym} ===")
        res = await project_discovery_engine.discover_company_projects_master(sym, force_refresh=True)
        print(f"Doanh nghiệp: {res.get('company_name')} | Website: {res.get('official_website')}")
        print(f"Tổng số dự án: {res.get('total_projects')} | Tổng vốn đầu tư: {res.get('total_investment_bil'):,} tỷ đ")
        for i, p in enumerate(res.get('projects', [])[:4]):
            print(f"  {i+1}. {p.get('name')}")
            print(f"     Nguồn: {p.get('source')} | Giai đoạn: {p.get('phase_tag')}")
        print()

asyncio.run(main())
