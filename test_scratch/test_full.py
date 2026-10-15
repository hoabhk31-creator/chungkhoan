import subprocess
import base64
import os
from pypdf import PdfReader

# Build full HTML test
html_test = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body style="height: 3500px; padding-top: 1800px; background: #090d16;">
<div id="status">INIT</div>
<script>
window.onload = async function() {
    window.scrollTo(0, 1800);

    const stratName = "FANSI T+ ROBOT";
    const exName = "Tất cả sàn (HOSE, HNX, UPCOM)";
    const timingName = "Mới hôm nay (T+0)";
    const volName = "> 100.000 CP/phiên";
    const formattedDate = "10:45 05/10/2026";
    const filename = "Tin_Hieu_Ky_Thuat_FANSI_2026-10-05.pdf";

    const wrapper = document.createElement("div");
    wrapper.style.position = "fixed";
    wrapper.style.left = "0";
    wrapper.style.top = "0";
    wrapper.style.width = "100%";
    wrapper.style.height = "0";
    wrapper.style.overflow = "hidden";
    wrapper.style.zIndex = "-9999";
    wrapper.style.pointerEvents = "none";

    const container = document.createElement("div");
    container.style.width = "1060px";
    container.style.maxWidth = "1060px";
    container.style.padding = "16px 20px";
    container.style.background = "#ffffff";
    container.style.color = "#0f172a";
    container.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    container.style.boxSizing = "border-box";
    container.style.margin = "0 auto";

    container.innerHTML = `
        <!-- HEADER BÁO CÁO -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0284c7; padding-bottom: 10px; margin-bottom: 12px;">
            <div>
                <div style="font-size: 11px; font-weight: 800; color: #0284c7; letter-spacing: 0.5px; text-transform: uppercase;">
                    IERM PLATFORM | INSTITUTIONAL EQUITY RESEARCH MATRIX
                </div>
                <div style="font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 2px;">
                    BÁO CÁO TÍN HIỆU KỸ THUẬT & DANH MỤC LỌC THỊ TRƯỜNG
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 3px;">
                    Chiến lược: <strong style="color: #047857; font-size: 12px;">${stratName}</strong> | 
                    Phạm vi: <strong>${exName}</strong> | 
                    Khung phiên: <strong>${timingName}</strong> | 
                    Thanh khoản: <strong>${volName}</strong>
                </div>
            </div>
            <div style="text-align: right; font-size: 10px; color: #64748b; line-height: 1.5;">
                <div>Thời gian quét: <strong>${formattedDate}</strong></div>
                <div style="color: #059669; font-weight: bold; margin-top: 2px;">● Dữ liệu Realtime trong phiên</div>
            </div>
        </div>

        <!-- KPI SUMMARY CARDS -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 12px; text-align: center;">
                <div style="font-size: 9px; color: #64748b; font-weight: 600; text-transform: uppercase;">Tổng mã thỏa mãn</div>
                <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 2px;">5 mã</div>
            </div>
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; padding: 8px 12px; text-align: center;">
                <div style="font-size: 9px; color: #047857; font-weight: 600; text-transform: uppercase;">Tín hiệu MUA (BUY)</div>
                <div style="font-size: 16px; font-weight: 800; color: #047857; margin-top: 2px;">2 mã</div>
            </div>
            <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 6px; padding: 8px 12px; text-align: center;">
                <div style="font-size: 9px; color: #be123c; font-weight: 600; text-transform: uppercase;">Tín hiệu BÁN (SELL)</div>
                <div style="font-size: 16px; font-weight: 800; color: #be123c; margin-top: 2px;">3 mã</div>
            </div>
            <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 6px; padding: 8px 12px; text-align: center;">
                <div style="font-size: 9px; color: #15803d; font-weight: 600; text-transform: uppercase;">Nổ mới hôm nay (T+0)</div>
                <div style="font-size: 16px; font-weight: 800; color: #15803d; margin-top: 2px;">5 mã</div>
            </div>
        </div>

        <!-- BẢNG TÍN HIỆU MUA -->
        <div style="margin-bottom: 14px;">
            <div style="font-size: 12px; font-weight: bold; color: #047857; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span>🟢 DANH MỤC CỔ PHIẾU CÓ TÍN HIỆU MUA (2 MÃ)</span>
                <span style="font-size: 9px; font-weight: normal; color: #64748b;">Đơn vị: VNĐ / Tỷ lệ (%) / CP</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1; font-size: 10px;">
                <thead>
                    <tr style="background: #ecfdf5;">
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: center; width: 35px;">STT</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: left; width: 80px;">Mã CP</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: left;">Tên Doanh Nghiệp</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: right; width: 75px;">Thị Giá</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: right; width: 65px;">% Ngày</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: right; width: 80px;">Giá Báo Mua</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: right; width: 75px;">Hiệu Suất</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: center; width: 60px;">Phiên T+</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: center; width: 80px;">Ngày Tín Hiệu</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: center; width: 45px;">RS</th>
                        <th style="padding: 5px 6px; border-bottom: 2px solid #059669; color: #065f46; font-size: 10px; text-align: right; width: 95px;">KL Khớp Hôm Nay</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: #ffffff; border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 5px 6px; text-align: center; color: #64748b;">1</td>
                        <td style="padding: 5px 6px; font-weight: bold; color: #047857;">HSG (HOSE)</td>
                        <td style="padding: 5px 6px;">Tập đoàn Hoa Sen</td>
                        <td style="padding: 5px 6px; text-align: right; font-weight: 600;">10.200</td>
                        <td style="padding: 5px 6px; text-align: right; font-weight: 600; color: #059669;">+2.20%</td>
                        <td style="padding: 5px 6px; text-align: right;">10.200</td>
                        <td style="padding: 5px 6px; text-align: right; font-weight: bold; color: #059669;">+0.00%</td>
                        <td style="padding: 5px 6px; text-align: center;">⚡ T+0</td>
                        <td style="padding: 5px 6px; text-align: center;">05/10/2026</td>
                        <td style="padding: 5px 6px; text-align: center; font-weight: bold; color: #0369a1;">68</td>
                        <td style="padding: 5px 6px; text-align: right;">1.43M</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- FOOTER -->
        <div style="margin-top: 14px; padding-top: 6px; border-top: 1px solid #cbd5e1; display: flex; justify-content: space-between; font-size: 8px; color: #94a3b8;">
            <span>Hệ thống Nghiên cứu & Định lượng Đầu tư IERM • Báo cáo tự động hóa</span>
            <span>Báo cáo lưu hành nội bộ</span>
        </div>
    `;

    wrapper.appendChild(container);
    document.body.appendChild(wrapper);

    const opt = {
        margin: [6, 6, 6, 6],
        filename: filename,
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

with open("static/test_pdf_full.html", "w", encoding="utf-8") as f:
    f.write(html_test)

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", "--dump-dom", "http://localhost:8000/static/test_pdf_full.html"]
p = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=20)
s = p.stdout
start = s.find('<pre id="pdf_data">')
if start != -1:
    end = s.find("</pre>", start)
    raw = s[start + len('<pre id="pdf_data">'):end]
    b64 = raw.split("base64,")[1]
    pdf_bytes = base64.b64decode(b64)
    out_pdf = "test_scratch/test_full.pdf"
    with open(out_pdf, "wb") as pf:
        pf.write(pdf_bytes)
    print("Full PDF size:", len(pdf_bytes))
    reader = PdfReader(out_pdf)
    page = reader.pages[0]
    for img in page.images:
        print("Image:", img.name, "size:", img.image.size)
        img.image.save("test_scratch/extracted_full.png")
        print("Saved test_scratch/extracted_full.png")
