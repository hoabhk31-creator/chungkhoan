import subprocess, time, urllib.request, json, os, sys
import websocket

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

user_data = f'E:/Anti/webapp/scratch/edge_prof_load_{int(time.time())}'
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

proc = subprocess.Popen([
    edge_path,
    '--headless',
    '--remote-debugging-port=9227',
    '--remote-allow-origins=*',
    f'--user-data-dir={user_data}',
    'http://127.0.0.1:8000/'
])
time.sleep(3)
try:
    with urllib.request.urlopen('http://127.0.0.1:9227/json') as r:
        pages = json.loads(r.read().decode('utf-8'))
    print("Found pages:")
    target_page = None
    for p in pages:
        print("  - type:", p.get('type'), "url:", p.get('url'))
        if p.get('type') == 'page' and ('8000' in p.get('url') or target_page is None):
            target_page = p
    ws_url = target_page['webSocketDebuggerUrl']
    print("Connecting to target page:", target_page.get('url'))
    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
    ws.send(json.dumps({'id': 2, 'method': 'Log.enable'}))
    ws.send(json.dumps({'id': 3, 'method': 'Page.enable'}))
    ws.send(json.dumps({'id': 4, 'method': 'Network.enable'}))
    # Reload page cleanly to capture all events
    ws.send(json.dumps({'id': 5, 'method': 'Page.reload', 'params': {'ignoreCache': True}}))

    start = time.time()
    while time.time() - start < 5:
        try:
            ws.settimeout(0.5)
            msg = ws.recv()
            data = json.loads(msg)
            m = data.get('method', '')
            if m:
                print("CDP MSG:", m)
            if m == 'Network.loadingFailed':
                print("LOADING FAILED:", json.dumps(data['params'], indent=2))
            elif m == 'Log.entryAdded':
                entry = data['params']['entry']
                print("LOG ENTRY:", entry.get('level'), entry.get('text'))
            elif m == 'Network.responseReceived':
                url = data['params']['response']['url']
                status = data['params']['response']['status']
                print("NETWORK:", status, url[:80])
        except websocket.WebSocketTimeoutException:
            continue
        except Exception as e:
            print("RECV ERROR:", e)

    # Check typeof switchTab
    ws.send(json.dumps({'id': 10, 'method': 'Runtime.evaluate', 'params': {'expression': 'typeof switchTab'}}))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 10:
            break
    print("switchTab result:", res)

    tabs = ['tab-screener', 'tab-matrix', 'tab-industry', 'tab-bctc', 'tab-overview', 'tab-technical', 'tab-valuation']
    for t in tabs:
        cmd = f'''
        (() => {{
            switchTab("{t}");
            const el = document.getElementById("{t}");
            const isVisible = el && !el.classList.contains("hidden");
            return "{t} visible: " + isVisible;
        }})()
        '''
        ws.send(json.dumps({'id': 20, 'method': 'Runtime.evaluate', 'params': {'expression': cmd}}))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == 20:
                break
        print("Tab switch test:", res.get('result', {}).get('result', {}).get('value'))

    # Also test openIndicatorsModal and closeIndicatorsModal
    cmd_modal = '''
    (() => {
        openIndicatorsModal();
        const m = document.getElementById("modal-indicators-search");
        const isOpen = m && !m.classList.contains("hidden");
        closeIndicatorsModal();
        const isClosed = m && m.classList.contains("hidden");
        return "Modal open/close test: open=" + isOpen + ", closed=" + isClosed;
    })()
    '''
    ws.send(json.dumps({'id': 30, 'method': 'Runtime.evaluate', 'params': {'expression': cmd_modal}}))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 30:
            break
    print("Modal test:", res.get('result', {}).get('result', {}).get('value'))
    ws.close()
finally:
    proc.terminate()
