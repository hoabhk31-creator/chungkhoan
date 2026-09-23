import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_pdf():
    # 1. Lấy dữ liệu PVS
    url_p = 'http://127.0.0.1:8000/api/preset/PVS'
    with urllib.request.urlopen(url_p, timeout=10) as res:
        report_data = json.loads(res.read().decode('utf-8'))
    
    # 2. Gửi request xuất PDF
    url_pdf = 'http://127.0.0.1:8000/api/export-matrix-pdf'
    req = urllib.request.Request(
        url_pdf,
        data=json.dumps({"report_data": report_data}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        pdf_bytes = res.read()
        print('PDF Export Status:', res.status)
        print('PDF Bytes length:', len(pdf_bytes))
        with open('scratch/test_PVS_matrix.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print('Saved to scratch/test_PVS_matrix.pdf successfully!')

if __name__ == '__main__':
    test_pdf()
