import sys
import urllib.request
import re
import html as html_lib

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

test_tickers = ['LHG', 'SZC', 'KBC', 'VIX', 'DBC', 'HAH', 'PVD', 'VHC', 'NTL']

for ticker in test_tickers:
    url = f'https://finance.vietstock.vn/{ticker}/ho-so-doanh-nghiep.htm'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            
            # 1. Company Name
            # Method a: "name": "LHG: CTCP Long Hậu"
            name_m = re.search(r'"name":\s*"' + ticker + r':\s*([^"]+)"', content)
            if not name_m:
                # Method b: from title
                name_m = re.search(r'<title>\s*' + ticker + r':\s*([^-|]+)', content)
            
            comp_name = name_m.group(1).strip() if name_m else f"CTCP {ticker}"
            
            # 2. Sector
            # Look for _gicsNameLevel4 or _gicsNameLevel2
            gics4_m = re.search(r'_gicsNameLevel4\s*=\s*"([^"]+)"', content)
            gics2_m = re.search(r'_gicsNameLevel2\s*=\s*"([^"]+)"', content)
            
            sector = gics4_m.group(1).strip() if gics4_m else (gics2_m.group(1).strip() if gics2_m else "Doanh nghiệp niêm yết")
            # Decode HTML entities if any
            comp_name = html_lib.unescape(comp_name)
            sector = html_lib.unescape(sector)
            
            print(f"[{ticker}] Name: '{comp_name}' | Sector: '{sector}'")
    except Exception as e:
        print(f"[{ticker}] Error: {e}")
