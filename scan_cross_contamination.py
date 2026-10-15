import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('data/ai_learned_catalysts.json', 'r', encoding='utf-8') as f:
    learned = json.load(f)

# Expanded comprehensive rule check definitions
def check_ticker_catalysts(tk, cats):
    issues = []
    for c in cats:
        cl = c.lower()
        # 1. Dầu khí
        if tk in ["BSR", "PLX", "OIL"]:
            if any(b in cl for b in ["giàn khoan", "jack-up", "điện gió ngoài khơi", "kho cảng lng", "điện khí lng"]):
                issues.append(c)
        elif tk in ["PVD"]:
            if any(b in cl for b in ["lọc dầu", "dung quất", "điện gió ngoài khơi", "kho cảng lng"]):
                issues.append(c)
        elif tk in ["PVS"]:
            if any(b in cl for b in ["lọc dầu", "dung quất", "giàn khoan tự nâng"]):
                issues.append(c)
        elif tk in ["GAS"]:
            if any(b in cl for b in ["lọc dầu", "dung quất", "giàn khoan", "jack-up"]):
                issues.append(c)

        # 2. Thép
        elif tk in ["HSG", "NKG", "TLH", "GDA"]:
            if any(b in cl for b in ["lò cao", "dung quất 2", "tự chủ hrc", "quặng sắt", "than cốc"]):
                issues.append(c)
        elif tk in ["HPG"]:
            if any(b in cl for b in ["tôn đông á", "tôn nam kim", "tôn hoa sen"]):
                issues.append(c)

        # 3. Bán lẻ
        elif tk in ["FRT"]:
            if any(b in cl for b in ["bách hóa xanh", "vàng bạc", "trang sức", "pnj", "erablue"]):
                issues.append(c)
        elif tk in ["MWG"]:
            if any(b in cl for b in ["long châu", "tiêm chủng", "vàng bạc", "trang sức", "pnj"]):
                issues.append(c)
        elif tk in ["PNJ"]:
            if any(b in cl for b in ["long châu", "nhà thuốc", "bách hóa xanh", "điện thoại", "laptop"]):
                issues.append(c)

        # 4. Thủy sản vs Chăn nuôi
        elif tk in ["VHC", "ANV", "IDI", "FMC", "CMX"]:
            if any(b in cl for b in ["heo hơi", "thịt lợn", "chăn nuôi lợn", "dịch tả lợn"]):
                issues.append(c)
        elif tk in ["BAF", "DBC", "HAG", "MLS"]:
            if any(b in cl for b in ["cá tra", "fillet", "tôm thẻ", "thuế chống bán phá giá cá", "por"]):
                issues.append(c)

        # 5. Hóa chất vs Phân bón
        elif tk in ["DCM", "DPM", "BFC", "LAS"]:
            if any(b in cl for b in ["phốt pho vàng", "p4", "nghi sơn", "chip bán dẫn", "pin xe điện"]):
                issues.append(c)
        elif tk in ["DGC", "CSV"]:
            if any(b in cl for b in ["đạm cà mau", "đạm phú mỹ", "hết khấu hao nhà máy đạm"]):
                issues.append(c)

        # 6. BĐS dân dụng vs KCN
        elif tk in ["PDR", "TCH", "DXG", "NVL", "DIG", "NLG", "KDH", "HDC", "CEO"]:
            if any(b in cl for b in ["cho thuê đất kcn", "kcn tràng duệ", "kcn hựu thạnh", "kcn phú mỹ 2", "thu hút fdi nhà xưởng"]):
                issues.append(c)
        elif tk in ["KBC", "IDC", "LHG", "SZC", "BCM", "NTC", "SIP"]:
            if any(b in cl for b in ["bán chung cư", "căn hộ cao cấp", "đại dự án nghỉ dưỡng", "bắc hà thanh", "thuận an 1"]):
                issues.append(c)

        # 7. Hàng không (HVN, VJC)
        elif tk in ["HVN", "VJC"]:
            if any(b in cl for b in ["cảng biển", "container", "đường sắt", "cao tốc"]):
                issues.append(c)

        # 8. Cảng biển (GMD, VSC, HAH)
        elif tk in ["GMD", "VSC"]:
            if any(b in cl for b in ["đội tàu container đóng mới (1,800 teu)", "cước tàu định hạn"]):
                issues.append(c)

    return issues

for tk, data in sorted(learned.items()):
    cats = data.get('catalysts', [])
    bad_cats = check_ticker_catalysts(tk, cats)
    if bad_cats:
        print(f"[{tk}] {len(bad_cats)} issues:")
        for bc in bad_cats:
            print(f"  - {bc}")
