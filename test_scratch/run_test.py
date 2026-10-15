import subprocess
import os

html_test = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body style="height: 3000px; padding-top: 1500px;">
<div id="status">INIT</div>
<script>
window.onload = async function() {
    window.scrollTo(0, 1500);
    const wrapper = document.createElement('div');
    wrapper.style.position = 'fixed';
    wrapper.style.left = '0';
    wrapper.style.top = '0';
    wrapper.style.width = '100%';
    wrapper.style.height = '0';
    wrapper.style.overflow = 'hidden';
    wrapper.style.zIndex = '-9999';
    wrapper.style.pointerEvents = 'none';

    const container = document.createElement('div');
    container.style.width = '100%';
    container.style.padding = '14px 18px';
    container.style.background = '#ffffff';
    container.style.color = '#0f172a';
    container.style.fontFamily = 'sans-serif';
    container.style.boxSizing = 'border-box';
    container.innerHTML = '<div style="font-size: 20px; font-weight: bold; color: red;">TEST BAO CAO TIN HIEU KY THUAT</div><p>Noi dung kiem tra xuat PDF</p><table border="1" style="width: 100%;"><tr><th>STT</th><th>Ma</th><th>Gia</th></tr><tr><td>1</td><td>HSG</td><td>10.200</td></tr></table>';

    wrapper.appendChild(container);
    document.body.appendChild(wrapper);

    const opt = {
        margin: [6, 6, 6, 6],
        filename: 'test_output.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff', scrollX: 0, scrollY: 0 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };

    try {
        const worker = html2pdf().set(opt).from(container);
        const pdfBase64 = await worker.outputPdf('datauristring');
        document.getElementById('status').textContent = 'DONE: len=' + pdfBase64.length;
    } catch(e) {
        document.getElementById('status').textContent = 'ERROR: ' + e.message;
    }
};
</script>
</body>
</html>"""

with open("static/test_pdf.html", "w", encoding="utf-8") as f:
    f.write(html_test)

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", "--dump-dom", "http://localhost:8000/static/test_pdf.html"]
p = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=20)
print("DOM Output with status:")
for line in p.stdout.splitlines():
    if "status" in line:
        print(line)
