import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("1. Testing GET /api/company-catalysts-insights/VSC...")
with urllib.request.urlopen('http://127.0.0.1:8000/api/company-catalysts-insights/VSC') as resp:
    d = json.loads(resp.read().decode('utf-8'))
    projs = d.get('projects', [])
    print(f"Projects count: {len(projs)}")
    for p in projs:
        print(f" - {p.get('name')}: {p.get('investment_bil')} ty | Phase: {p.get('phase_tag')}")

print("\n2. Testing POST /api/discover-company-projects/VSC?force_refresh=true...")
req = urllib.request.Request('http://127.0.0.1:8000/api/discover-company-projects/VSC?force_refresh=true', method='POST')
with urllib.request.urlopen(req) as resp:
    disc = json.loads(resp.read().decode('utf-8'))
    print(f"Total projects discovered: {disc.get('total_projects')}")
    print(f"Official website: {disc.get('official_website')}")
    print(f"SSC portal URL: {disc.get('ssc_portal_url')}")
    for p in disc.get('projects', [])[:4]:
        print(f" * {p.get('name')}: {p.get('investment_bil')} ty | Source: {p.get('source')}")
