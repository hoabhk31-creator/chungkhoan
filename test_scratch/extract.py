import subprocess
import base64
import os
from pypdf import PdfReader

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", "--dump-dom", "http://localhost:8000/static/test_pdf_exact.html"]
p = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=20)
s = p.stdout
start = s.find('<pre id="pdf_data">')
if start != -1:
    end = s.find("</pre>", start)
    raw = s[start + len('<pre id="pdf_data">'):end]
    b64 = raw.split("base64,")[1]
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
