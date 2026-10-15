import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# 1. Tải danh mục âm tiết chuẩn tiếng Việt
SYLLABLES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'vietnamese_syllables.txt')
syllables = set()
if os.path.exists(SYLLABLES_FILE):
    with open(SYLLABLES_FILE, encoding='utf-8') as f:
        syllables = set(line.strip().lower() for line in f if line.strip())

# Các từ viết tắt, tên riêng quốc gia, thuật ngữ tài chính tiếng Anh không chia tách
ENGLISH_ACRONYMS = {
    'eudr', 'fsc', 'svr10', 'svr', 'anrpc', 'yoy', 'qoq', 'cagr', 'dcf', 'pe', 'pb', 'roe', 'roa',
    'vnd', 'usd', 'mas', 'dri', 'hpg', 'vnm', 'vcb', 'mbb', 'tcb', 'fpt', 'mwg', 'vhm', 'vic',
    'indonesia', 'malaysia', 'thailand', 'vietnam', 'laos', 'cambodia', 'china',
    'research', 'company', 'note', 'update', 'target', 'price', 'hold', 'buy', 'sell'
}

# Danh mục từ ghép tiếng Việt bị dính từ PDF gốc (ưu tiên replace chính xác)
MERGED_PAIRS = [
    ('giáchủ', 'giá chủ'),
    ('chủyếu', 'chủ yếu'),
    ('yếutại', 'yếu tại'),
    ('suygiảm', 'suy giảm'),
    ('giảmchủ', 'giảm chủ'),
    ('suở', 'su ở'),
    ('Rủiro', 'Rủi ro'),
    ('rocần', 'ro cần'),
    ('thuhoạch', 'thu hoạch'),
    ('thâmhụtước', 'thâm hụt ước'),
    ('hụtước', 'hụt ước'),
    ('thâmhụt', 'thâm hụt'),
    ('hụtcước', 'hụt ước'),
    ('từsản', 'từ sản'),
    ('sảnlượng', 'sản lượng'),
    ('lượngnên', 'lượng nên'),
    ('thuhoạt', 'thu hoạt'),
    ('hoạtđộng', 'hoạt động'),
    ('chínhtăng', 'chính tăng'),
    ('tăngmạnh', 'tăng mạnh'),
    ('tănggấp', 'tăng gấp'),
    ('gấpđôi', 'gấp đôi'),
    ('vàsản', 'và sản'),
    ('củngcố', 'củng cố'),
    ('vịthế', 'vị thế'),
    ('hưởnglợi', 'hưởng lợi'),
    ('hấpdẫn', 'hấp dẫn'),
    ('giáhấpdẫn', 'giá hấp dẫn'),
    ('Định giáhấpdẫn', 'Định giá hấp dẫn'),
    ('hạngắn', 'hạn gắn'),
    ('gắnvới', 'gắn với'),
    ('dàihạn', 'dài hạn'),
    ('ngắnhạn', 'ngắn hạn'),
    ('lượngmủ', 'lượng mủ'),
    ('mủdự', 'mủ dự'),
    ('dựkiến', 'dự kiến'),
    ('kiếngiảm', 'kiến giảm'),
    ('vàsầu', 'và sầu'),
    ('sầuriêng', 'sầu riêng'),
    ('riêngtrước', 'riêng trước'),
    ('trướckhi', 'trước khi'),
    ('khibước', 'khi bước'),
    ('bướcvào', 'bước vào'),
    ('chukỳ', 'chu kỳ'),
    ('kỳtăng', 'kỳ tăng'),
    ('mớitừ', 'mới từ'),
    ('từnăm', 'từ năm'),
    ('nhờvườn', 'nhờ vườn'),
    ('xuhướng', 'xu hướng'),
    ('hướngtăng', 'hướng tăng'),
    ('tăngngắn', 'tăng ngắn'),
    ('hạnmạnh', 'hạn mạnh'),
    ('mạnhmẽ', 'mạnh mẽ'),
    ('khibứt', 'khi bứt'),
    ('bứtphá', 'bứt phá'),
    ('dứtkhoát', 'dứt khoát'),
    ('caocủa', 'cao của'),
    ('thanhkhoản', 'thanh khoản'),
    ('Độnglực', 'Động lực'),
    ('chínhđến', 'chính đến'),
    ('đếntừ', 'đến từ'),
    ('tiêuthụ', 'tiêu thụ'),
    ('thụtăng', 'thụ tăng'),
    ('baogồm', 'bao gồm'),
    ('hàngtồn', 'hàng tồn'),
    ('tồnkho', 'tồn kho'),
    ('tíchlũy', 'tích lũy'),
    ('lũycuối', 'lũy cuối'),
    ('trongbối', 'trong bối'),
    ('bốicảnh', 'bối cảnh'),
    ('biênlợi', 'biên lợi'),
    ('lợinhuận', 'lợi nhuận'),
    ('nhuậngộp', 'nhuận gộp'),
    ('gộpcải', 'gộp cải'),
    ('cảithiện', 'cải thiện'),
    ('cùngkỳ', 'cùng kỳ'),
    ('kếthợp', 'kết hợp'),
    ('tổngdiện', 'tổng diện'),
    ('diệntích', 'diện tích'),
    ('sẽđược', 'sẽ được'),
    ('đượctrình', 'được trình'),
    ('sẽcòn', 'sẽ còn'),
    ('hỗtrợ', 'hỗ trợ'),
    ('cơcấu', 'cơ cấu'),
    ('cấunăm', 'cấu năm'),
    ('nămthứ', 'năm thứ'),
    ('liêntiếp', 'liên tiếp'),
    ('nghìntấn', 'nghìn tấn'),
    ('câytrồng', 'cây trồng'),
    ('trồngmới', 'trồng mới'),
    ('mớicần', 'mới cần'),
    ('nămmới', 'năm mới'),
    ('khóphục', 'khó phục'),
    ('phụchồi', 'phục hồi'),
    ('dùgiá', 'dù giá'),
    ('giáđã', 'giá đã'),
    ('Cầutăng', 'Cầu tăng'),
    ('tăngvừa', 'tăng vừa'),
    ('vừaphải', 'vừa phải'),
    ('phảinhưng', 'phải nhưng'),
    ('nhưngít', 'nhưng ít'),
    ('cungquyết', 'cung quyết'),
    ('quyếtđịnh', 'quyết định'),
    ('nguyênmức', 'nguyên mức'),
    ('mứccộng', 'mức cộng'),
    ('cộngthêm', 'cộng thêm'),
    ('thêmtối', 'thêm tối'),
    ('tốithiểu', 'tối thiểu'),
    ('đạtchứng', 'đạt chứng'),
    ('chứngchỉ', 'chứng chỉ'),
    ('đạtchuẩn', 'đạt chuẩn'),
    ('chuẩnvới', 'chuẩn với'),
    ('nhưngmới', 'nhưng mới'),
    ('mớichiếm', 'mới chiếm'),
    ('Dưđịa', 'Dư địa'),
    ('địanằm', 'địa nằm'),
    ('nằmở', 'nằm ở'),
    ('tỷtrọng', 'tỷ trọng'),
    ('ápdụng', 'áp dụng'),
    ('dụngtừ', 'dụng từ'),
    ('chúngtôi', 'chúng tôi'),
    ('tôidự', 'tôi dự'),
    ('tôigiả', 'tôi giả'),
    ('dựphóng', 'dự phóng'),
    ('doanhthu', 'doanh thu'),
    ('thucủa', 'thu của'),
    ('vàlãi', 'và lãi'),
    ('lãiròng', 'lãi ròng'),
    ('đạtkhoảng', 'đạt khoảng'),
    ('giảđịnh', 'giả định'),
    ('tíchcực', 'tích cực'),
    ('sovới', 'so với'),
    ('trungbình', 'trung bình'),
    ('Triểnvọng', 'Triển vọng'),
    ('đượcbù', 'được bù'),
    ('bùđắp', 'bù đắp'),
    ('đắpbởi', 'đắp bởi'),
    ('bởinguồn', 'bởi nguồn'),
    ('nguồnthu', 'nguồn thu'),
    ('thutừ', 'thu từ'),
    ('tăngtrưởngmới', 'tăng trưởng mới'),
    ('Nhàmáy', 'Nhà máy'),
    ('chếbiến', 'chế biến'),
    ('từda', 'từ da'),
    ('khótính', 'khó tính'),
    ('giátrị', 'giá trị'),
    ('mởrộng', 'mở rộng'),
    ('phágiá', 'phá giá'),
    ('kỳrà', 'rà soát'),
    ('ràsoát', 'rà soát'),
    ('BộThương', 'Bộ Thương'),
    ('thứcăn', 'thức ăn'),
    ('khôdầu', 'khô dầu'),
    ('giávốn', 'giá vốn'),
    ('tiêuthụthủy', 'tiêu thụ thủy'),
    ('thụthủy', 'thụ thủy'),
    ('lễhội', 'lễ hội'),
    ('Giáxuất', 'Giá xuất'),
    ('vàtôm', 'và tôm'),
    ('mẽtại', 'mẽ tại'),
    ('thịtrường', 'thị trường'),
    ('thịphần', 'thị phần'),
    ('thuếchống', 'thuế chống'),
    ('vàdịch', 'và dịch'),
    ('Tốiưu', 'Tối ưu'),
    ('phảnánh', 'phản ánh'),
    ('dựán', 'dự án'),
    ('Địnhgiá', 'Định giá'),
    ('ĐịnhgiáP', 'Định giá P'),
    ('lợiích', 'lợi ích'),
    ('hànghóa', 'hàng hóa'),
    ('kếhoạch', 'kế hoạch'),
    ('doanhnghiệp', 'doanh nghiệp'),
    ('quặngsắt', 'quặng sắt'),
    ('lòcao', 'lò cao'),
    ('cổtức', 'cổ tức'),
    ('tiềnmặt', 'tiền mặt'),
    ('chíphí', 'chi phí'),
    ('bánhàng', 'bán hàng'),
    ('quảnlý', 'quản lý'),
    ('giáthép', 'giá thép'),
    ('tăngtrưởng', 'tăng trưởng'),
    ('hồiphục', 'hồi phục'),
    ('sảnxuất', 'sản xuất'),
    ('kiểmsoát', 'kiểm soát'),
    ('giáthành', 'giá thành'),
    ('phânphối', 'phân phối'),
    ('chínhsách', 'chính sách'),
    ('bảohộ', 'bảo hộ'),
    ('thuếtựvệ', 'thuế tự vệ'),
    ('chốngbánphágiá', 'chống bán phá giá'),
    ('nhậpkhẩu', 'nhập khẩu'),
    ('xuấtkhẩu', 'xuất khẩu'),
    ('thựchiện', 'thực hiện'),
    ('xâydựng', 'xây dựng'),
    ('pháthành', 'phát hành')
]

def clean_text_advanced(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    
    # 1. Chuẩn hóa viết tắt HĐQT
    text = re.sub(r'H\s+ĐQT', 'HĐQT', text)
    
    # 2. Tách dấu câu dính chữ
    text = re.sub(r'([\)\%\,\;\:\/])([a-zA-ZáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])', r'\1 \2', text)
    text = re.sub(r'(\.)([A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ])', r'\1 \2', text)
    text = re.sub(r'([a-zà-ỹ])([A-ZĐ][a-zà-ỹ]+)', r'\1 \2', text)
    text = re.sub(r'([A-ZĐ]{2,})([a-zà-ỹ]{2,})', r'\1 \2', text)
    text = re.sub(r'([a-zà-ỹ]{2,})([A-ZĐ]{2,})', r'\1 \2', text)
    text = re.sub(r'([a-zA-ZáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-ZáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])', r'\1 \2', text)
    text = re.sub(r'([a-zA-ZáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ])([đĐ][a-zà-ỹ]+)', r'\1 \2', text)

    # 3. Áp dụng bảng từ ghép ưu tiên
    for p, r in MERGED_PAIRS:
        text = re.sub(re.escape(p), r, text, flags=re.IGNORECASE)

    # 4. Khôi phục số thập phân và %
    text = re.sub(r'(\d)\s*([\.,])\s*(\d)', r'\1\2\3', text)
    text = re.sub(r'(\d)\s*%', r'\1%', text)
    
    # 5. Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text


if __name__ == '__main__':
    CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'pdf_catalysts_cache.json')
    if not os.path.exists(CACHE_FILE):
        print("Cache file not found:", CACHE_FILE)
        sys.exit(1)

    with open(CACHE_FILE, encoding='utf-8') as f:
        cache_data = json.load(f)

    print(f"Total cache entries: {len(cache_data)}")

    cleaned_count = 0
    for url, item in cache_data.items():
        if not isinstance(item, dict):
            continue
        new_cats = []
        for c in item.get('cats', []):
            new_cats.append(clean_text_advanced(c))
        item['cats'] = new_cats

        new_risks = []
        for r in item.get('risks', []):
            new_risks.append(clean_text_advanced(r))
        item['risks'] = new_risks
        cleaned_count += 1

    # Lưu lại file cache
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully cleaned and updated {cleaned_count} entries in {CACHE_FILE}!")

    # In kết quả của DRI để kiểm tra
    dri_mas = cache_data.get('http://static1.vietstock.vn/edocs/22384/1791189030604_DRI_Companynote_MAS05.pdf')
    if dri_mas:
        print("\n=== DRI MAS RESULTS AFTER CLEANING ===")
        for i, c in enumerate(dri_mas.get('cats', [])):
            print(f"{i+1}. {c}")
        print("\nRisks:")
        for i, r in enumerate(dri_mas.get('risks', [])):
            print(f"- {r}")
