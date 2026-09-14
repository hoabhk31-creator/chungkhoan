import sys
import urllib.request
import re
import html

sys.stdout.reconfigure(encoding='utf-8')

def fetch_profile(ticker):
    url = f'https://finance.vietstock.vn/{ticker}/ho-so-doanh-nghiep.htm'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
    
    # Name
    m_name = re.search(r'"name":\s*"' + ticker + r':\s*([^"]+)"', content)
    if not m_name:
        m_name = re.search(r'<title>\s*' + ticker + r':\s*([^-|]+)', content)
    name = html.unescape(m_name.group(1).strip()) if m_name else f'CTCP {ticker}'
    
    # Sector
    m_gics4 = re.search(r'_gicsNameLevel4\s*=\s*"([^"]+)"', content)
    m_gics2 = re.search(r'_gicsNameLevel2\s*=\s*"([^"]+)"', content)
    raw_sec = m_gics4.group(1) if m_gics4 else (m_gics2.group(1) if m_gics2 else 'Doanh nghiệp niêm yết')
    raw_sec = html.unescape(raw_sec.strip())
    
    if 'BĐS công nghiệp' in raw_sec or 'khu công nghiệp' in raw_sec.lower():
        sector = 'Bất động sản Khu công nghiệp'
    elif 'BĐS nhà ở' in raw_sec or 'bất động sản nhà ở' in raw_sec.lower():
        sector = 'Bất động sản Nhà ở'
    elif 'Bất động sản' in raw_sec:
        sector = 'Bất động sản'
    elif 'ngân hàng đầu tư' in raw_sec.lower() or 'môi giới' in raw_sec.lower():
        sector = 'Dịch vụ Tài chính & Chứng khoán'
    elif 'ngân hàng' in raw_sec.lower():
        sector = 'Ngân hàng & Dịch vụ Tài chính'
    else:
        sector = raw_sec
    return {'name': name, 'sector': sector}

print(fetch_profile('LHG'))
print(fetch_profile('SZC'))
print(fetch_profile('IDC'))
print(fetch_profile('VIX'))
