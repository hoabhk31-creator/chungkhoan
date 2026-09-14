import requests, re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.vietstock.vn/'
}
r = requests.get('https://finance.vietstock.vn/phan-tich-ky-thuat.htm', headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
for ifr in soup.find_all('iframe'):
    print("iframe:", ifr.get('src'))

# also check all script tags content
for s in soup.find_all('script'):
    if s.string and any(k in s.string.lower() for k in ['chart', 'tradingview', 'st-api', 'vietstock']):
        for line in s.string.splitlines():
            if any(k in line.lower() for k in ['chart', 'tradingview', 'api', 'history', 'token']):
                print("script line:", line.strip()[:140])
