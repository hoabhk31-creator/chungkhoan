import subprocess, time, urllib.request, json, os, sys
import websocket

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

user_data = 'E:/Anti/webapp/scratch/edge_prof_unique'
os.makedirs(user_data, exist_ok=True)

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

print("Edge path:", edge_path, "exists:", os.path.exists(edge_path))

proc = subprocess.Popen([
    edge_path,
    '--headless',
    '--remote-debugging-port=9225',
    '--remote-allow-origins=*',
    f'--user-data-dir={user_data}',
    'about:blank'
])
time.sleep(2)
try:
    with urllib.request.urlopen('http://127.0.0.1:9225/json') as r:
        pages = json.loads(r.read().decode('utf-8'))
    ws_url = pages[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
    
    # Read app.js
    with open('static/app.js', 'r', encoding='utf-8') as f:
        js_code = f.read()

    # Let's test binary search to find the exact line causing syntax error!
    lines = js_code.split('\n')
    print("Total lines in app.js:", len(lines))

    # Test full script first
    expr = 'try { new Function(' + json.dumps(js_code) + '); "OK"; } catch(e) { "ERR: " + e.message + " | " + e.stack; }'
    ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': expr}}))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 2:
            break
    print("Full response:", res)
    result_val = res.get('result', {}).get('result', {}).get('value', '')
    print("Full parse result:", result_val)

    if result_val != "OK":
        # Binary search or scan to find where syntax error begins
        # We can test parsing functions or chunks
        print("Finding exact error location...")
    ws.close()
finally:
    proc.terminate()
