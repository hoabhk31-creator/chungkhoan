import subprocess
import base64
import os
from pypdf import PdfReader

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
    container.style.width = '1060px';
    container.style.maxWidth = '1060px';
    container.style.padding = '18px 22px';
    container.style.background = '#ffffff';
    container.style.color = '#0f172a';
    container.style.fontFamily = 'sans-serif';
    container.style.boxSizing = 'border-box';
    container.style.margin = '0 auto';

    container.innerHTML = `
        <div style="border-bottom: 2px solid #0284c7; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between;">
            <div>
                <div style="font-size: 11px; font-weight: bold; color: #0284c7;">IERM PLATFORM | INSTITUTIONAL RESEARCH</div>
                <div style="font-size: 18px; font-weight: bold; color: #0f172a;">BÁO CÁO TÍN HIỆU KỸ THUẬT & DANH MỤC LỌC</div>
            </div>
            <div style="text-align: right; font-size: 10px; color: #64748b;">
                <div>Thời gian quét: 10:45 05/10/2026</div>
                <div style="color: #059669; font-weight: bold;">● Realtime trong phiên</div>
            </div>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
            <thead>
                <tr style="background: #ecfdf5;">
                    <th style="padding: 5px; border-bottom: 2px solid #059669; width: 35px; text-align: center;">STT</th>
                    <th style="padding: 5px; border-bottom: 2px solid #059669; width: 80px; text-align: left;">Mã CP</th>
                    <th style="padding: 5px; border-bottom: 2px solid #059669; text-align: left;">Tên Doanh Nghiệp</th>
                    <th style="padding: 5px; border-bottom: 2px solid #059669; width: 75px; text-align: right;">Thị Giá</th>
                    <th style="padding: 5px; border-bottom: 2px solid #059669; width: 65px; text-align: right;">% Ngày</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 5px; text-align: center;">1</td>
                    <td style="padding: 5px; font-weight: bold; color: #047857;">HSG (HOSE)</td>
                    <td style="padding: 5px;">Tập đoàn Hoa Sen</td>
                    <td style="padding: 5px; text-align: right; font-weight: bold;">10.200</td>
                    <td style="padding: 5px; text-align: right; color: #059669;">+2.20%</td>
                </tr>
            </tbody>
        </table>
    `;

    wrapper.appendChild(container);
    document.body.appendChild(wrapper);

    const opt = {
        margin: [6, 6, 6, 6],
        filename: 'test_screener.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff', scrollX: 0, scrollY: 0 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };

    try {
        const worker = html2pdf().set(opt).from(container);
        const pdfBase64 = await worker.outputPdf('datauristring');
        const pre = document.createElement('pre');
        pre.id = 'pdf_data';
        pre.textContent = pdfBase64;
        document.body.appendChild(pre);
        document.getElementById('status').textContent = 'DONE: len=' + pdfBase64.length;
    } catch(e) {
        document.getElementById('status').textContent = 'ERROR: ' + e.message;
    }
};
</script>
</body>
</html>"""

with open("static/test_pdf_exact.html", "w", encoding="utf-8") as f:
    f.write(html_test)

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", "--dump-dom", "http://localhost:8000/static/test_pdf_exact.html"]
p = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=20)
s = p.stdout
start = s.find('<pre id="pdf_data">')
if start != -1:
    end = s.find("</pre>", start)
    raw = s[start + len('<pre id="pdf_data">'):end]
    header = "data:application/pdf;base64,"
    if header in raw:
        b64 = raw.split(header)[1]
        pdf_bytes = base64.b64decode(b64)
        out_pdf = "test_scratch/test_exact.pdf"
        with open(out_pdf, "wb") as pf:
            pf.write(pdf_bytes)
        print("Successfully generated and saved:", out_pdf)
        print("PDF byte size:", len(pdf_bytes))
        reader = PdfReader(out_pdf)
        print("Total pages:", len(reader.pages))
        page = reader.pages[0]
        print("Page MediaBox:", page.mediabox)
        print("Images found on page:", len(page.images))
        for img in page.images:
            print("Extracted image:", img.name, "size:", img.image.size)
            img.image.save("test_scratch/extracted_page.png")
            print("Saved image to test_scratch/extracted_page.png")
else:
    print("Could not find pre tag in DOM:", s[:500])
