import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test():
    try:
        url = 'http://127.0.0.1:8000/api/preset/PVS'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            print('SUCCESS! Status:', res.status)
            print('Ticker:', data.get('ticker'))
            reports = data.get('matrix_table', [])
            print('Matrix table reports:', len(reports))
            for r in reports:
                inst = r.get('institution')
                cats = r.get('key_catalysts', [])
                risks = r.get('key_risks', [])
                print(f'-- CTCK: {inst}')
                print(f'   Catalysts count: {len(cats)}')
                for c in cats[:2]:
                    print('     cat:', c[:80])
                print(f'   Risks count: {len(risks)}')
                for k in risks[:2]:
                    print('     risk:', k[:80])
            cs = data.get('consensus_summary', {})
            cCats = cs.get('consensual_catalysts', [])
            cRisks = cs.get('consensual_risks', [])
            print(f'Consensus catalysts count: {len(cCats)}')
            for c in cCats[:3]:
                print('   cons cat:', c[:80])
            print(f'Consensus risks count: {len(cRisks)}')
            for rk in cRisks[:3]:
                print('   cons risk:', rk[:80])
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    test()
