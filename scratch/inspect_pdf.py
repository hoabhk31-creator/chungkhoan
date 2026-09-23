import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

reader = pypdf.PdfReader('scratch/test_PVS_matrix.pdf')
print('Total pages:', len(reader.pages))
full_text = ''
for idx, page in enumerate(reader.pages):
    t = page.extract_text() or ''
    full_text += t
    print(f'Page {idx+1} length: {len(t)} chars')

print('\nCheck bad strings in PDF:')
for bad in ['1549778', '% SVCK', 'BÁO CÁO TÀI CHÍNH DỰ PHÓNG', 'Đơn vị: triệu đồng', 'k ế', 'l ợ i', 'đ ạ t', 't ỷ đ ồ ng']:
    count = full_text.count(bad)
    print(f' - "{bad}": {count} occurrences')

print('\nSample text from Page 2:')
if len(reader.pages) > 1:
    print(reader.pages[1].extract_text()[:400])
