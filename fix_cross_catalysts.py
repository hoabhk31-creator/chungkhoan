import json

with open("data/ai_learned_catalysts.json", "r", encoding="utf-8") as f:
    learned = json.load(f)

# Fix DGC
if "DGC" in learned:
    cats = learned["DGC"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "đạm cà mau" in c.lower() or "nhà máy đạm" in c.lower():
            new_cats.append("Thương vụ M&A và sở hữu các mỏ quặng Apatit mới bảo đảm nguồn nguyên liệu phục vụ chuỗi sản xuất hóa chất phốt pho giá rẻ trong 20 năm tới.")
        else:
            new_cats.append(c)
    learned["DGC"]["catalysts"] = new_cats

# Fix DPM
if "DPM" in learned:
    cats = learned["DPM"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "nghi sơn" in c.lower() or "xút - clo" in c.lower():
            new_cats.append("Tối ưu hóa nguồn nguyên liệu khí thiên nhiên đầu vào và nâng cao sản lượng các dòng phân bón NPK Phú Mỹ chất lượng cao phục vụ thị trường nội địa.")
        else:
            new_cats.append(c)
    learned["DPM"]["catalysts"] = new_cats

# Fix HSG
if "HSG" in learned:
    cats = learned["HSG"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "lò cao" in c.lower() or "dung quất 2" in c.lower():
            new_cats.append("Tối ưu hóa mạng lưới phân phối hơn 500 chi nhánh Hoa Sen Home toàn quốc giúp gia tăng biên lợi nhuận mảng vật liệu xây dựng.")
        elif "than mỡ" in c.lower() or "quặng sắt" in c.lower():
            new_cats.append("Biên lợi nhuận xuất khẩu tôn mạ sang các thị trường phát triển (Mỹ, Châu Âu) phục hồi khi chu kỳ tồn kho thép toàn cầu chạm đáy.")
        else:
            new_cats.append(c)
    learned["HSG"]["catalysts"] = new_cats

# Fix NKG
if "NKG" in learned:
    cats = learned["NKG"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "lò cao" in c.lower() or "dung quất 2" in c.lower():
            new_cats.append("Dự án Nhà máy Tôn Nam Kim Phú Mỹ (Bà Rịa - Vũng Tàu) quy mô 1.2 triệu tấn/năm mở rộng mạnh mẽ công suất tôn mạ chất lượng cao.")
        elif "quặng sắt" in c.lower() or "than coke" in c.lower():
            new_cats.append("Lợi thế cạnh tranh xuất khẩu tôn mạ sang thị trường Bắc Mỹ và châu Âu nhờ tiêu chuẩn chất lượng cao và khả năng phòng vệ thương mại chủ động.")
        else:
            new_cats.append(c)
    learned["NKG"]["catalysts"] = new_cats

# Fix PNJ
if "PNJ" in learned:
    cats = learned["PNJ"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "bách hóa xanh" in c.lower() or "long châu" in c.lower():
            new_cats.append("Mở rộng mạng lưới bán lẻ trang sức PNJ Gold và PNJ Silver chuẩn Flagship thêm 35-45 cửa hàng mới tại các đô thị loại 1 và loại 2.")
        else:
            new_cats.append(c)
    learned["PNJ"]["catalysts"] = new_cats

# Fix VSC
if "VSC" in learned:
    cats = learned["VSC"].get("catalysts", [])
    new_cats = []
    for c in cats:
        if "đội tàu container đóng mới" in c.lower():
            new_cats.append("Thâu tóm thành công Cảng Nam Hải Đình Vũ giúp VSC thống lĩnh cụm cảng hạ lưu sông Cấm (Hải Phòng), tối ưu hóa công suất xếp dỡ container.")
        else:
            new_cats.append(c)
    learned["VSC"]["catalysts"] = new_cats

with open("data/ai_learned_catalysts.json", "w", encoding="utf-8") as f:
    json.dump(learned, f, ensure_ascii=False, indent=2)

print("Updated data/ai_learned_catalysts.json successfully.")
