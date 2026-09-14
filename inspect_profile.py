import sys
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

req = urllib.request.Request('https://finance.vietstock.vn/LHG/ho-so-doanh-nghiep.htm', headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for any JSON data or text
for m in re.finditer(r'(ICB|Khu công nghiệp|Bất động sản|KCN|Long Hậu|Hạ tầng)[\s\S]{1,100}', html, re.IGNORECASE):
    clean = re.sub(r'<[^>]+>', ' ', m.group(0))
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 10:
        print('FOUND:', clean[:120])
