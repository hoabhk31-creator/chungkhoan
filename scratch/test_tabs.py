import subprocess, time, urllib.request, json, os, sys
import websocket

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

user_data = 'E:/Anti/webapp/scratch/edge_prof_unique'
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

proc = subprocess.Popen([
    edge_path,
    '--headless',
    '--remote-debugging-port=9226',
    '--remote-allow-origins=*',
    f'--user-data-dir={user_data}',
    'http://127.0.0.1:8000/'
])
time.sleep(2.5)
try:
    with urllib.request.urlopen('http://127.0.0.1:9226/json') as r:
        pages = json.loads(r.read().decode('utf-8'))
    ws_url = pages[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
    time.sleep(1)

    # 1. Check switchTab
    ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': 'typeof switchTab'}}))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 2:
            break
    print("switchTab type:", res.get('result', {}).get('result', {}).get('value'))

    # 2. Try switching tabs
    tabs_to_test = ['screener', 'multi-report', 'peer', 'financial', 'overview', 'technical', 'valuation']
    for t in tabs_to_test:
        ws.send(json.dumps({
            'id': 100,
            'method': 'Runtime.evaluate',
            'params': {'expression': f'try {{ switchTab("{t}"); "Switched to {t} OK"; }} catch(e) {{ "ERR: " + e.message; }}'}
        }))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == 100:
                break
        val = res.get('result', {}).get('result', {}).get('value')
        print(f"Tab {t}: {val}")

    # 3. Check openIndicatorsModal
    ws.send(json.dumps({
        'id': 200,
        'method': 'Runtime.evaluate',
        'params': {'expression': 'try { openIndicatorsModal(); "openIndicatorsModal OK"; } catch(e) { "ERR: " + e.message; }'}
    }))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 200:
            break
    print("openIndicatorsModal:", res.get('result', {}).get('result', {}).get('value'))

    ws.close()
finally:
    proc.terminate()
