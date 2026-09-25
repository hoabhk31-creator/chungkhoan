# -*- coding: utf-8 -*-
"""Script kiến tạo UNIVERSAL_SECTOR_PEERS_CONFIG cho 23 nhóm ngành."""

import json
from typing import Dict, Any, List, Optional

UNIVERSAL_SECTOR_PEERS_CONFIG = {
    # 1. BĐS Dân dụng
    "REAL_ESTATE_RESIDENTIAL": {
        "sector_name": "Bất động sản Dân dụng & Đô thị",
        "cycle": "Phục hồi nguồn cung nhờ tháo gỡ điểm nghẽn Pháp lý (Luật Đất đai, Nhà ở, KDBĐS mới)",
        "sector_kpi_columns": [
            {"field": "advance_from_buyers_bil", "label": "Tiền trả trước (tỷ)", "unit": "tỷ VND", "color": "emerald"},
            {"field": "backlog_bil", "label": "Backlog (tỷ VND)", "unit": "tỷ VND", "color": "amber"},
            {"field": "land_bank_ha", "label": "Quỹ đất (ha)", "unit": "ha", "color": "sky"}
        ],
        "peers": [
            {"ticker": "VHM", "name": "CTCP Vinhomes", "market_cap_bil": 185000.0, "pe": 8.5, "pb": 1.05, "roe": 19.5, "roa": 8.2, "net_margin": 28.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 15.0, "advance_from_buyers_bil": 85000.0, "backlog_bil": 120000.0, "land_bank_ha": 18500.0},
            {"ticker": "KDH", "name": "CTCP Nhà Khang Điền", "market_cap_bil": 28500.0, "pe": 22.0, "pb": 1.85, "roe": 8.5, "roa": 4.5, "net_margin": 18.2, "debt_to_equity": 0.42, "revenue_growth_yoy": 14.5, "advance_from_buyers_bil": 8500.0, "backlog_bil": 12000.0, "land_bank_ha": 1250.0},
            {"ticker": "NLG", "name": "CTCP Nam Long", "market_cap_bil": 15600.0, "pe": 18.5, "pb": 1.45, "roe": 9.2, "roa": 4.1, "net_margin": 16.5, "debt_to_equity": 0.48, "revenue_growth_yoy": 16.8, "advance_from_buyers_bil": 5200.0, "backlog_bil": 7800.0, "land_bank_ha": 850.0},
            {"ticker": "PDR", "name": "Bất động sản Phát Đạt", "market_cap_bil": 19500.0, "pe": 11.5, "pb": 1.10, "roe": 11.8, "roa": 5.2, "net_margin": 17.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 25.0, "advance_from_buyers_bil": 3800.0, "backlog_bil": 6500.0, "land_bank_ha": 620.0},
            {"ticker": "DXG", "name": "Tập đoàn Đất Xanh", "market_cap_bil": 12800.0, "pe": 18.5, "pb": 0.95, "roe": 6.8, "roa": 3.1, "net_margin": 8.5, "debt_to_equity": 0.62, "revenue_growth_yoy": 12.0, "advance_from_buyers_bil": 2500.0, "backlog_bil": 4200.0, "land_bank_ha": 480.0},
            {"ticker": "DIG", "name": "Tổng CTCP DIC Corp", "market_cap_bil": 13500.0, "pe": 35.0, "pb": 1.65, "roe": 5.2, "roa": 2.5, "net_margin": 7.2, "debt_to_equity": 0.55, "revenue_growth_yoy": 10.5, "advance_from_buyers_bil": 1800.0, "backlog_bil": 3500.0, "land_bank_ha": 380.0},
            {"ticker": "HDC", "name": "CTCP Phát triển Nhà BR-VT", "market_cap_bil": 4600.0, "pe": 14.5, "pb": 1.35, "roe": 11.5, "roa": 5.5, "net_margin": 19.5, "debt_to_equity": 0.72, "revenue_growth_yoy": 15.0, "advance_from_buyers_bil": 1200.0, "backlog_bil": 2800.0, "land_bank_ha": 400.0},
            {"ticker": "CKG", "name": "CTCP Tư vấn Đầu tư CKG", "market_cap_bil": 2100.0, "pe": 9.5, "pb": 1.15, "roe": 14.5, "roa": 6.5, "net_margin": 18.0, "debt_to_equity": 0.65, "revenue_growth_yoy": 12.0, "advance_from_buyers_bil": 850.0, "backlog_bil": 1500.0, "land_bank_ha": 250.0},
            {"ticker": "TCH", "name": "Tài chính Hoàng Huy", "market_cap_bil": 12500.0, "pe": 10.5, "pb": 0.95, "roe": 12.5, "roa": 7.5, "net_margin": 24.5, "debt_to_equity": 0.15, "revenue_growth_yoy": 18.0, "advance_from_buyers_bil": 2400.0, "backlog_bil": 4500.0, "land_bank_ha": 350.0},
            {"ticker": "NVL", "name": "CTCP Tập đoàn Novaland", "market_cap_bil": 25500.0, "pe": 45.0, "pb": 0.65, "roe": 2.5, "roa": 0.8, "net_margin": 5.5, "debt_to_equity": 1.85, "revenue_growth_yoy": 8.0, "advance_from_buyers_bil": 28000.0, "backlog_bil": 35000.0, "land_bank_ha": 2850.0}
        ],
        "catalysts": [
            "Bộ ba Luật Đất đai, Nhà ở, KDBĐS mới tháo gỡ điểm nghẽn pháp lý dự án và rút ngắn thời gian cấp phép 1/500.",
            "Lãi suất cho vay mua nhà duy trì ở vùng thấp lịch sử kích thích nhu cầu nhà ở thực và đầu tư dài hạn.",
            "Điểm rơi bàn giao các đại dự án đô thị ghi nhận doanh thu và lợi nhuận đột biến giai đoạn 2026 - 2027.",
            "Doanh số bán hàng chưa ghi nhận (Unbilled Bookings) và người mua trả tiền trước đạt mức cao kỷ lục."
        ],
        "risks": [
            "Tiến độ giải phóng mặt bằng và tính tiền sử dụng đất mới có thể kéo dài hơn dự kiến.",
            "Áp lực trái phiếu đáo hạn đối với các doanh nghiệp có tỷ lệ đòn bẩy nợ cao.",
            "Sự phân hóa thanh khoản sâu sắc giữa phân khúc nhà ở thực và bất động sản nghỉ dưỡng cao cấp."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh về phân khúc nhà ở thực, uy tín tiến độ và chính sách chiết khấu thanh toán."},
            "supplier_power": {"score": 3, "desc": "Chi phí GPMB và tiền sử dụng đất mới tăng theo bảng giá đất địa phương."},
            "buyer_power": {"score": 4, "desc": "Khách hàng cân nhắc kỹ lưỡng pháp lý sở hữu sổ hồng và chính sách hỗ trợ lãi suất."},
            "substitution_threat": {"score": 2, "desc": "Nhà đất thổ cư cạnh tranh nhưng căn hộ chung cư compound có sức hút riêng."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản tích lũy quỹ đất sạch và năng lực hoàn thiện thủ tục 1/500."}
        },
        "recommended_valuation": {
            "method": "RNAV & P/B Dự án",
            "badge": "Khuyên dùng: RNAV & P/B",
            "rationale": "Doanh nghiệp BĐS phụ thuộc vào quỹ đất và tiến độ bàn giao; phương pháp RNAV (Giá trị tài sản ròng theo dự án) phản ánh trung thực nhất giá trị doanh nghiệp.",
            "priority_tab": "rnav"
        }
    },

    # 2. BĐS KCN
    "REAL_ESTATE_INDUSTRIAL": {
        "sector_name": "BĐS Khu công nghiệp",
        "cycle": "Làn sóng Dịch chuyển Chuỗi Cung ứng Toàn cầu & Dòng vốn FDI Kỷ lục vào Việt Nam",
        "sector_kpi_columns": [
            {"field": "leasable_area_ha", "label": "Đất cho thuê (ha)", "unit": "ha", "color": "emerald"},
            {"field": "fdi_attraction_mil", "label": "Thu hút FDI ($m)", "unit": "$m", "color": "sky"},
            {"field": "occupancy_rate", "label": "Lấp đầy (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "BCM", "name": "Becamex IDC", "market_cap_bil": 72500.0, "pe": 28.5, "pb": 3.85, "roe": 14.5, "roa": 5.2, "net_margin": 26.5, "debt_to_equity": 1.25, "revenue_growth_yoy": 16.5, "leasable_area_ha": 1250.0, "fdi_attraction_mil": 2400.0, "occupancy_rate": 88.0},
            {"ticker": "KBC", "name": "Đô thị Kinh Bắc", "market_cap_bil": 24500.0, "pe": 16.5, "pb": 1.25, "roe": 12.8, "roa": 6.8, "net_margin": 28.0, "debt_to_equity": 0.35, "revenue_growth_yoy": 22.0, "leasable_area_ha": 650.0, "fdi_attraction_mil": 1800.0, "occupancy_rate": 82.0},
            {"ticker": "IDC", "name": "Tổng Công ty IDICO", "market_cap_bil": 19500.0, "pe": 11.2, "pb": 2.45, "roe": 24.5, "roa": 11.5, "net_margin": 25.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 15.0, "leasable_area_ha": 580.0, "fdi_attraction_mil": 1200.0, "occupancy_rate": 85.0},
            {"ticker": "SZC", "name": "Sonadezi Châu Đức", "market_cap_bil": 7800.0, "pe": 15.5, "pb": 2.15, "roe": 16.2, "roa": 7.8, "net_margin": 32.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 18.0, "leasable_area_ha": 450.0, "fdi_attraction_mil": 850.0, "occupancy_rate": 78.0},
            {"ticker": "NTC", "name": "KCN Nam Tân Uyên", "market_cap_bil": 5400.0, "pe": 14.2, "pb": 4.10, "roe": 30.5, "roa": 14.2, "net_margin": 45.0, "debt_to_equity": 0.12, "revenue_growth_yoy": 12.5, "leasable_area_ha": 346.0, "fdi_attraction_mil": 950.0, "occupancy_rate": 90.0},
            {"ticker": "LHG", "name": "Long Hậu", "market_cap_bil": 2200.0, "pe": 10.5, "pb": 1.35, "roe": 14.8, "roa": 8.5, "net_margin": 28.5, "debt_to_equity": 0.15, "revenue_growth_yoy": 14.0, "leasable_area_ha": 180.0, "fdi_attraction_mil": 450.0, "occupancy_rate": 86.0},
            {"ticker": "SIP", "name": "Đầu tư Sài Gòn VRG", "market_cap_bil": 16800.0, "pe": 13.5, "pb": 2.65, "roe": 22.5, "roa": 9.5, "net_margin": 22.0, "debt_to_equity": 0.25, "revenue_growth_yoy": 15.5, "leasable_area_ha": 520.0, "fdi_attraction_mil": 1100.0, "occupancy_rate": 84.0},
            {"ticker": "VGC", "name": "Tổng Công ty Viglacera", "market_cap_bil": 21500.0, "pe": 14.8, "pb": 2.10, "roe": 16.5, "roa": 7.2, "net_margin": 14.5, "debt_to_equity": 0.58, "revenue_growth_yoy": 11.5, "leasable_area_ha": 600.0, "fdi_attraction_mil": 1300.0, "occupancy_rate": 80.0}
        ],
        "catalysts": [
            "Dòng vốn FDI giải ngân mạnh mẽ từ các tập đoàn công nghệ toàn cầu (Foxconn, Amkor, Hana Micron, Luxshare).",
            "Giá thuê đất KCN duy trì đà tăng 5-10%/năm tại cả miền Bắc và miền Nam nhờ nguồn cung quỹ đất sạch có hạn.",
            "Mô hình tích hợp KCN - Đô thị - Dịch vụ và nhà xưởng xây sẵn (RBF/RBW) tạo dòng tiền cho thuê đều đặn.",
            "Tỷ lệ cổ tức tiền mặt chi trả đều đặn ở mức cao nhờ dòng tiền doanh thu chưa thực hiện (tiền thuê đất trả một lần)."
        ],
        "risks": [
            "Tiến độ giải phóng mặt bằng và cấp phép mở rộng phân kỳ KCN mới kéo dài.",
            "Áp lực thuế tối thiểu toàn cầu (GMT) có thể ảnh hưởng đến biên độ ưu đãi thuế thu hút nhà đầu tư lớn.",
            "Hạ tầng điện năng và giao thông kết nối tại một số địa phương còn thiếu đồng bộ."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh vị trí địa lý kết nối cảng biển/sân bay và hệ sinh thái dịch vụ đi kèm."},
            "supplier_power": {"score": 3, "desc": "Tiền đền bù giải tỏa đất nông nghiệp tăng theo bảng giá đất mới."},
            "buyer_power": {"score": 3, "desc": "Tập đoàn FDI đa quốc gia có quyền đàm phán hợp đồng thuê quy mô lớn trên 20-50 ha."},
            "substitution_threat": {"score": 1, "desc": "Đất KCN quy hoạch đạt chuẩn xử lý nước thải là yêu cầu bắt buộc của nhà đầu tư FDI."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản quy hoạch đất công nghiệp quốc gia và năng lực phát triển hạ tầng kỹ thuật."}
        },
        "recommended_valuation": {
            "method": "RNAV Đất KCN & P/B",
            "badge": "Khuyên dùng: RNAV & P/B",
            "rationale": "Doanh nghiệp KCN có doanh thu chưa thực hiện lớn và quỹ đất cho thuê dài hạn; phương pháp RNAV định giá quỹ đất thương phẩm kết hợp P/B là tối ưu.",
            "priority_tab": "rnav"
        }
    },

    # 3. Bán lẻ & Chuỗi
    "RETAIL_DISTRIBUTION": {
        "sector_name": "Bán lẻ & Chuỗi phân phối",
        "cycle": "Phục hồi Tiêu dùng Nội địa & Xu hướng Hợp nhất Thị phần Bán lẻ Hiện đại",
        "sector_kpi_columns": [
            {"field": "store_count", "label": "Cửa hàng (điểm)", "unit": "điểm", "color": "emerald"},
            {"field": "same_store_sales_growth", "label": "SSSG (%)", "unit": "%", "color": "sky"},
            {"field": "online_revenue_pct", "label": "Online (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "MWG", "name": "Thế Giới Di Động", "market_cap_bil": 98500.0, "pe": 18.5, "pb": 3.45, "roe": 22.5, "roa": 8.5, "net_margin": 4.2, "debt_to_equity": 0.45, "revenue_growth_yoy": 15.0, "store_count": 5600.0, "same_store_sales_growth": 12.5, "online_revenue_pct": 18.5},
            {"ticker": "FRT", "name": "FPT Retail (Long Châu)", "market_cap_bil": 24500.0, "pe": 32.0, "pb": 6.80, "roe": 20.5, "roa": 5.8, "net_margin": 3.2, "debt_to_equity": 1.25, "revenue_growth_yoy": 28.0, "store_count": 2200.0, "same_store_sales_growth": 18.0, "online_revenue_pct": 15.0},
            {"ticker": "PNJ", "name": "Vàng bạc Đá quý Phú Nhuận", "market_cap_bil": 32500.0, "pe": 16.5, "pb": 3.15, "roe": 24.5, "roa": 14.5, "net_margin": 6.8, "debt_to_equity": 0.25, "revenue_growth_yoy": 14.0, "store_count": 420.0, "same_store_sales_growth": 10.5, "online_revenue_pct": 8.5},
            {"ticker": "DGW", "name": "Digiworld", "market_cap_bil": 9200.0, "pe": 15.2, "pb": 2.85, "roe": 19.5, "roa": 7.8, "net_margin": 3.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 16.5, "store_count": 0.0, "same_store_sales_growth": 12.0, "online_revenue_pct": 22.0},
            {"ticker": "PET", "name": "Dịch vụ Tổng hợp Dầu khí", "market_cap_bil": 3100.0, "pe": 12.5, "pb": 1.25, "roe": 10.5, "roa": 3.5, "net_margin": 1.8, "debt_to_equity": 1.15, "revenue_growth_yoy": 9.5, "store_count": 0.0, "same_store_sales_growth": 6.5, "online_revenue_pct": 14.0},
            {"ticker": "DMX", "name": "Điện máy Xanh (Chuỗi MWG)", "market_cap_bil": 98500.0, "pe": 18.5, "pb": 3.45, "roe": 22.5, "roa": 8.5, "net_margin": 4.2, "debt_to_equity": 0.45, "revenue_growth_yoy": 15.0, "store_count": 2100.0, "same_store_sales_growth": 11.5, "online_revenue_pct": 16.5}
        ],
        "catalysts": [
            "Tăng trưởng doanh thu cùng cửa hàng (SSSG) phục hồi mạnh mẽ sau giai đoạn tái cấu trúc.",
            "Chuỗi Bách Hóa Xanh và Long Châu bước vào giai đoạn đóng góp lợi nhuận ròng bền vững.",
            "Chuyển đổi số bán lẻ đa kênh (Omnichannel) tối ưu hóa trải nghiệm khách hàng và chi phí vận hành kho vận Logistics."
        ],
        "risks": [
            "Tâm lý người tiêu dùng nhạy cảm với biến động thu nhập và việc làm.",
            "Cạnh tranh gay gắt từ các sàn thương mại điện tử quốc tế (Shopee, TikTok Shop)."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh gay gắt về giá, khuyến mãi và trải nghiệm bảo hành dịch vụ hậu mãi."},
            "supplier_power": {"score": 3, "desc": "Các hãng công nghệ lớn (Apple, Samsung) kiểm soát nguồn hàng và biên lợi nhuận phân phối."},
            "buyer_power": {"score": 4, "desc": "Người tiêu dùng dễ dàng so sánh giá bán trên các nền tảng trực tuyến chỉ bằng một click."},
            "substitution_threat": {"score": 3, "desc": "Thương mại điện tử livestream và mua sắm trực tuyến phát triển vũ bão."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản quy mô chuỗi hàng nghìn cửa hàng, chuỗi cung ứng lạnh và hệ thống ERP bán lẻ."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền & P/E Forward",
            "badge": "Khuyên dùng: DCF & P/E",
            "rationale": "Doanh nghiệp bán lẻ có dòng tiền kinh doanh (CFO) tiền mặt thặng dư rất lớn; DCF kết hợp P/E forward phản ánh sát thực tế.",
            "priority_tab": "dcf"
        }
    },

    # 4. Ngân hàng
    "BANKING": {
        "sector_name": "Ngân hàng Thương mại",
        "cycle": "Tăng trưởng Tín dụng Cao & Kiểm soát Chất lượng Tài sản (Xử lý Nợ xấu)",
        "sector_kpi_columns": [
            {"field": "nim_ratio", "label": "NIM (%)", "unit": "%", "color": "emerald"},
            {"field": "casa_ratio", "label": "CASA (%)", "unit": "%", "color": "sky"},
            {"field": "npl_ratio", "label": "Nợ xấu NPL (%)", "unit": "%", "color": "rose"}
        ],
        "peers": [
            {"ticker": "VCB", "name": "Vietcombank", "market_cap_bil": 512000.0, "pe": 14.5, "pb": 2.85, "roe": 22.5, "roa": 2.1, "net_margin": 42.5, "debt_to_equity": 8.5, "revenue_growth_yoy": 12.5, "nim_ratio": 3.2, "casa_ratio": 38.5, "npl_ratio": 1.05},
            {"ticker": "BID", "name": "BIDV", "market_cap_bil": 285000.0, "pe": 11.5, "pb": 2.10, "roe": 19.5, "roa": 1.4, "net_margin": 35.0, "debt_to_equity": 12.0, "revenue_growth_yoy": 14.0, "nim_ratio": 2.7, "casa_ratio": 22.5, "npl_ratio": 1.45},
            {"ticker": "CTG", "name": "VietinBank", "market_cap_bil": 195000.0, "pe": 9.5, "pb": 1.45, "roe": 18.0, "roa": 1.3, "net_margin": 32.5, "debt_to_equity": 11.5, "revenue_growth_yoy": 13.5, "nim_ratio": 2.8, "casa_ratio": 24.0, "npl_ratio": 1.40},
            {"ticker": "TCB", "name": "Techcombank", "market_cap_bil": 175000.0, "pe": 8.5, "pb": 1.25, "roe": 17.5, "roa": 2.5, "net_margin": 45.0, "debt_to_equity": 5.8, "revenue_growth_yoy": 18.5, "nim_ratio": 4.1, "casa_ratio": 41.5, "npl_ratio": 1.25},
            {"ticker": "MBB", "name": "MBBank", "market_cap_bil": 135000.0, "pe": 6.8, "pb": 1.15, "roe": 21.5, "roa": 2.4, "net_margin": 40.0, "debt_to_equity": 6.8, "revenue_growth_yoy": 16.5, "nim_ratio": 4.4, "casa_ratio": 39.0, "npl_ratio": 1.55},
            {"ticker": "ACB", "name": "Á Châu (ACB)", "market_cap_bil": 110000.0, "pe": 7.2, "pb": 1.35, "roe": 23.5, "roa": 2.4, "net_margin": 42.0, "debt_to_equity": 7.2, "revenue_growth_yoy": 15.0, "nim_ratio": 3.8, "casa_ratio": 25.5, "npl_ratio": 1.20},
            {"ticker": "VPB", "name": "VPBank", "market_cap_bil": 155000.0, "pe": 10.5, "pb": 1.10, "roe": 13.5, "roa": 1.8, "net_margin": 30.0, "debt_to_equity": 5.5, "revenue_growth_yoy": 22.0, "nim_ratio": 5.8, "casa_ratio": 18.5, "npl_ratio": 3.20},
            {"ticker": "HDB", "name": "HDBank", "market_cap_bil": 78000.0, "pe": 6.5, "pb": 1.30, "roe": 24.5, "roa": 2.2, "net_margin": 38.0, "debt_to_equity": 8.5, "revenue_growth_yoy": 25.0, "nim_ratio": 4.8, "casa_ratio": 14.5, "npl_ratio": 1.65},
            {"ticker": "STB", "name": "Sacombank", "market_cap_bil": 62000.0, "pe": 7.8, "pb": 1.15, "roe": 18.5, "roa": 1.6, "net_margin": 34.0, "debt_to_equity": 9.2, "revenue_growth_yoy": 16.0, "nim_ratio": 3.6, "casa_ratio": 21.0, "npl_ratio": 1.80}
        ],
        "catalysts": [
            "Hạn mức tăng trưởng tín dụng (Credit Room) toàn hệ thống được Ngân hàng Nhà nước phân bổ tích cực 15-16%.",
            "Biên lãi thuần (NIM) duy trì phục hồi nhờ chi phí huy động vốn (COF) thấp và tỷ lệ CASA tăng.",
            "Tỷ lệ bao phủ nợ xấu (LLR) dày dặn tạo bộ đệm an toàn vững chắc giúp giảm áp lực trích lập dự phòng rủi ro."
        ],
        "risks": [
            "Rủi ro nợ xấu tiềm ẩn từ phân khúc cho vay bất động sản và các dự án năng lượng chuyển tiếp.",
            "Cạnh tranh lãi suất huy động vốn trong các thời điểm cao điểm thanh khoản hệ thống."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh thị phần tín dụng bán lẻ, CASA và dịch vụ ngân hàng số (Digital Banking)."},
            "supplier_power": {"score": 3, "desc": "Người gửi tiền cá nhân và tổ chức có nhiều lựa chọn đầu tư thay thế (chứng khoán, BĐS)."},
            "buyer_power": {"score": 3, "desc": "Khách hàng doanh nghiệp lớn có vị thế đàm phán lãi suất cho vay ưu đãi."},
            "substitution_threat": {"score": 2, "desc": "Ví điện tử và công ty Fintech phát triển nhưng vẫn phải liên kết tài khoản ngân hàng."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản giấy phép thành lập ngân hàng mới của NHNN cực kỳ khắt khe."}
        },
        "recommended_valuation": {
            "method": "P/B, Residual Income & Graham",
            "badge": "Khuyên dùng: P/B & Residual Income",
            "rationale": "Ngân hàng là định chế tài chính có đòn bẩy huy động tiền gửi cao; mô hình P/B kết hợp Thu nhập thặng dư (Residual Income) là phương pháp chuẩn mực toàn cầu.",
            "priority_tab": "pb"
        }
    },

    # 5. Chứng khoán
    "SECURITIES": {
        "sector_name": "Chứng khoán & Đầu tư",
        "cycle": "Vận hành Hệ thống Giao dịch Mới (KRX) & Triển vọng Nâng hạng Thị trường Mới nổi FTSE",
        "sector_kpi_columns": [
            {"field": "margin_balance_bil", "label": "Dư nợ Margin (tỷ)", "unit": "tỷ VND", "color": "emerald"},
            {"field": "brokerage_market_share", "label": "Thị phần (%)", "unit": "%", "color": "sky"},
            {"field": "proprietary_trading_roi", "label": "Lãi Tự doanh (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "SSI", "name": "Chứng khoán SSI", "market_cap_bil": 58000.0, "pe": 16.5, "pb": 2.15, "roe": 14.5, "roa": 5.2, "net_margin": 32.5, "debt_to_equity": 1.85, "revenue_growth_yoy": 22.0, "margin_balance_bil": 22500.0, "brokerage_market_share": 9.8, "proprietary_trading_roi": 16.5},
            {"ticker": "VND", "name": "Chứng khoán VNDIRECT", "market_cap_bil": 28500.0, "pe": 13.5, "pb": 1.45, "roe": 12.8, "roa": 4.5, "net_margin": 28.5, "debt_to_equity": 1.65, "revenue_growth_yoy": 18.0, "margin_balance_bil": 12800.0, "brokerage_market_share": 6.8, "proprietary_trading_roi": 14.0},
            {"ticker": "VCI", "name": "Chứng khoán Vietcap", "market_cap_bil": 22500.0, "pe": 18.0, "pb": 2.45, "roe": 15.2, "roa": 6.5, "net_margin": 38.0, "debt_to_equity": 1.45, "revenue_growth_yoy": 25.0, "margin_balance_bil": 9800.0, "brokerage_market_share": 5.5, "proprietary_trading_roi": 22.5},
            {"ticker": "HCM", "name": "Chứng khoán TP.HCM (HSC)", "market_cap_bil": 21500.0, "pe": 15.5, "pb": 2.10, "roe": 14.8, "roa": 5.8, "net_margin": 30.5, "debt_to_equity": 1.95, "revenue_growth_yoy": 24.0, "margin_balance_bil": 14500.0, "brokerage_market_share": 6.5, "proprietary_trading_roi": 15.0},
            {"ticker": "MBS", "name": "Chứng khoán MB", "market_cap_bil": 12800.0, "pe": 14.8, "pb": 2.25, "roe": 16.5, "roa": 5.5, "net_margin": 31.0, "debt_to_equity": 2.15, "revenue_growth_yoy": 26.0, "margin_balance_bil": 10500.0, "brokerage_market_share": 5.2, "proprietary_trading_roi": 16.0},
            {"ticker": "FTS", "name": "Chứng khoán FPT", "market_cap_bil": 11500.0, "pe": 16.2, "pb": 2.85, "roe": 18.5, "roa": 7.5, "net_margin": 42.0, "debt_to_equity": 1.15, "revenue_growth_yoy": 20.0, "margin_balance_bil": 6800.0, "brokerage_market_share": 3.5, "proprietary_trading_roi": 19.5},
            {"ticker": "BSI", "name": "Chứng khoán BIDV", "market_cap_bil": 10800.0, "pe": 15.0, "pb": 2.35, "roe": 17.0, "roa": 6.2, "net_margin": 35.0, "debt_to_equity": 1.35, "revenue_growth_yoy": 22.5, "margin_balance_bil": 6200.0, "brokerage_market_share": 3.2, "proprietary_trading_roi": 18.0}
        ],
        "catalysts": [
            "Triển vọng thị trường chứng khoán Việt Nam được nâng hạng lên Thị trường Mới nổi FTSE Russell.",
            "Vận hành chính thức hệ thống giao dịch mới KRX hỗ trợ giao dịch T+0 và đa dạng hóa sản phẩm phái sinh.",
            "Dư nợ Margin tăng trưởng bứt phá cùng với làn sóng tăng vốn điều lệ quy mô hàng chục nghìn tỷ đồng."
        ],
        "risks": [
            "Biến động điều chỉnh của thị trường chứng khoán ảnh hưởng trực tiếp đến danh mục tự doanh cổ phiếu.",
            "Cạnh tranh chính sách phí giao dịch (Zero Fee) làm xói mòn biên lợi nhuận mảng môi giới."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh gay gắt về lãi suất cho vay Margin và chính sách Zero-Fee giữa các CTCK."},
            "supplier_power": {"score": 2, "desc": "Nguồn vốn huy động từ ngân hàng mẹ và phát hành trái phiếu thuận lợi."},
            "buyer_power": {"score": 3, "desc": "Nhà đầu tư cá nhân năng động, dễ dàng chuyển đổi tài khoản giữa các công ty chứng khoán."},
            "substitution_threat": {"score": 2, "desc": "Kênh đầu tư vàng, bất động sản và tiết kiệm cạnh tranh dòng tiền nhàn rỗi."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản vốn điều lệ tối thiểu và yêu cầu hệ thống hạ tầng an ninh mạng khắt khe."}
        },
        "recommended_valuation": {
            "method": "P/B & P/E Theo Chu kỳ Thanh khoản",
            "badge": "Khuyên dùng: P/B & P/E",
            "rationale": "Lợi nhuận CTCK biến động rất mạnh theo chu kỳ thanh khoản; định giá P/B kết hợp P/E theo thanh khoản giả định là chuẩn xác nhất.",
            "priority_tab": "pb"
        }
    },

    # 6. Bảo hiểm
    "INSURANCE": {
        "sector_name": "Bảo hiểm",
        "cycle": "Lãi suất Trái phiếu Chính phủ & Tái cơ cấu Chuỗi Phân phối Bancassurance Minh bạch",
        "sector_kpi_columns": [
            {"field": "gross_premium_bil", "label": "Phí bảo hiểm gốc (tỷ)", "unit": "tỷ VND", "color": "emerald"},
            {"field": "loss_ratio_pct", "label": "Tỷ lệ bồi thường (%)", "unit": "%", "color": "rose"},
            {"field": "investment_yield_pct", "label": "Lợi suất đầu tư (%)", "unit": "%", "color": "sky"}
        ],
        "peers": [
            {"ticker": "BVH", "name": "Tập đoàn Bảo Việt", "market_cap_bil": 32500.0, "pe": 16.5, "pb": 1.45, "roe": 10.2, "roa": 1.5, "net_margin": 5.2, "debt_to_equity": 0.15, "revenue_growth_yoy": 8.5, "gross_premium_bil": 42000.0, "loss_ratio_pct": 52.0, "investment_yield_pct": 6.8},
            {"ticker": "MIG", "name": "Bảo hiểm Quân đội (MIC)", "market_cap_bil": 3200.0, "pe": 11.5, "pb": 1.35, "roe": 12.8, "roa": 3.8, "net_margin": 6.8, "debt_to_equity": 0.22, "revenue_growth_yoy": 14.0, "gross_premium_bil": 5200.0, "loss_ratio_pct": 42.0, "investment_yield_pct": 7.2},
            {"ticker": "PVI", "name": "CTCP PVI", "market_cap_bil": 11500.0, "pe": 10.2, "pb": 1.55, "roe": 16.5, "roa": 4.5, "net_margin": 8.5, "debt_to_equity": 0.18, "revenue_growth_yoy": 12.0, "gross_premium_bil": 14500.0, "loss_ratio_pct": 46.0, "investment_yield_pct": 7.5},
            {"ticker": "BMI", "name": "Bảo hiểm Bảo Minh", "market_cap_bil": 2800.0, "pe": 9.8, "pb": 1.15, "roe": 12.5, "roa": 3.5, "net_margin": 6.2, "debt_to_equity": 0.12, "revenue_growth_yoy": 10.5, "gross_premium_bil": 5800.0, "loss_ratio_pct": 48.0, "investment_yield_pct": 6.9},
            {"ticker": "BIC", "name": "Bảo hiểm BIDV", "market_cap_bil": 3500.0, "pe": 8.5, "pb": 1.25, "roe": 15.5, "roa": 4.2, "net_margin": 9.2, "debt_to_equity": 0.10, "revenue_growth_yoy": 16.0, "gross_premium_bil": 4500.0, "loss_ratio_pct": 39.0, "investment_yield_pct": 7.8}
        ],
        "catalysts": [
            "Danh mục tiền gửi và trái phiếu chính phủ hưởng lợi từ mặt bằng lãi suất duy trì ổn định.",
            "Luật Kinh doanh Bảo hiểm mới thúc đẩy chuẩn hóa quy trình phân phối, minh bạch hóa hợp đồng.",
            "Tỷ lệ thâm nhập bảo hiểm tại Việt Nam còn ở mức thấp (<3% GDP), tiềm năng tăng trưởng dài hạn vượt bậc."
        ],
        "risks": [
            "Tỷ lệ bồi thường rủi ro thiên tai, bão lũ bất thường tác động ngắn hạn tới mảng tài sản kỹ thuật.",
            "Quy định chặt chẽ hơn về kiểm soát kênh bán chéo qua ngân hàng (Bancassurance)."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh thị phần phi nhân thọ giữa các thương hiệu bảo hiểm thuộc tập đoàn/ngân hàng lớn."},
            "supplier_power": {"score": 2, "desc": "Thị trường tái bảo hiểm quốc tế cung cấp năng lực nhận tái bảo hiểm dồi dào."},
            "buyer_power": {"score": 3, "desc": "Khách hàng doanh nghiệp bảo hiểm công nghiệp có khả năng đấu thầu giá phí cạnh tranh."},
            "substitution_threat": {"score": 1, "desc": "Bảo hiểm rủi ro tài sản và y tế sức khỏe là giải pháp bảo vệ tài chính không thể thay thế."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản vốn pháp định tối thiểu và yêu cầu biên khả năng thanh toán nghiêm ngặt của Bộ Tài chính."}
        },
        "recommended_valuation": {
            "method": "P/B & Lợi suất Danh mục Đầu tư",
            "badge": "Khuyên dùng: P/B & Đầu tư",
            "rationale": "Doanh nghiệp bảo hiểm sở hữu danh mục đầu tư tài chính thanh khoản cực cao; định giá P/B kết hợp lợi suất danh mục đầu tư là thước đo tối ưu.",
            "priority_tab": "pb"
        }
    },

    # 7. Thép & Luyện kim
    "STEEL_METALLURGY": {
        "sector_name": "Thép & Luyện kim",
        "cycle": "Phục hồi Tiêu thụ Thép Hạ tầng Xây dựng & Đại Dự án Dung Quất 2 Đi vào Hoạt động",
        "sector_kpi_columns": [
            {"field": "capacity_kton", "label": "Công suất (kt)", "unit": "kt", "color": "emerald"},
            {"field": "hrc_volume_kton", "label": "SL HRC (kt)", "unit": "kt", "color": "sky"},
            {"field": "gross_margin", "label": "Biên gộp (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "HPG", "name": "Tập đoàn Hòa Phát", "market_cap_bil": 178000.0, "pe": 11.5, "pb": 1.55, "roe": 14.8, "roa": 8.5, "net_margin": 10.5, "debt_to_equity": 0.55, "revenue_growth_yoy": 18.0, "capacity_kton": 8500.0, "hrc_volume_kton": 3000.0, "gross_margin": 16.5},
            {"ticker": "HSG", "name": "Tập đoàn Hoa Sen", "market_cap_bil": 13500.0, "pe": 12.8, "pb": 1.15, "roe": 9.5, "roa": 4.5, "net_margin": 3.8, "debt_to_equity": 0.45, "revenue_growth_yoy": 12.0, "capacity_kton": 2500.0, "hrc_volume_kton": 0.0, "gross_margin": 12.0},
            {"ticker": "NKG", "name": "Thép Nam Kim", "market_cap_bil": 6200.0, "pe": 13.5, "pb": 1.05, "roe": 8.2, "roa": 3.8, "net_margin": 3.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 10.5, "capacity_kton": 1200.0, "hrc_volume_kton": 0.0, "gross_margin": 10.5},
            {"ticker": "VGS", "name": "Ống thép Việt Đức", "market_cap_bil": 1850.0, "pe": 14.2, "pb": 1.35, "roe": 10.5, "roa": 4.8, "net_margin": 4.5, "debt_to_equity": 0.75, "revenue_growth_yoy": 15.0, "capacity_kton": 650.0, "hrc_volume_kton": 0.0, "gross_margin": 11.2},
            {"ticker": "TLH", "name": "Thép Tiến Lên", "market_cap_bil": 850.0, "pe": 16.0, "pb": 0.65, "roe": 4.5, "roa": 1.8, "net_margin": 1.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 8.0, "capacity_kton": 350.0, "hrc_volume_kton": 0.0, "gross_margin": 7.5}
        ],
        "catalysts": [
            "Khu liên hợp Gang thép Dung Quất 2 nâng gấp đôi công suất HRC lên trên 14 triệu tấn thép/năm.",
            "Bộ Công Thương điều tra áp thuế chống bán phá giá thép HRC và tôn mạ nhập khẩu từ Trung Quốc.",
            "Giải ngân đầu tư công các siêu dự án hạ tầng (sân bay Long Thành, cao tốc, cầu vượt) thúc đẩy tiêu thụ thép xây dựng."
        ],
        "risks": [
            "Áp lực thép giá rẻ dư thừa từ Trung Quốc tràn vào thị trường Đông Nam Á.",
            "Biến động giá quặng sắt và than cốc thế giới làm co hẹp biên lợi nhuận gộp luyện kim."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Hòa Phát nắm vị thế chi phối sản xuất thép thô; cạnh tranh phân khúc tôn mạ giữa Hoa Sen và Nam Kim."},
            "supplier_power": {"score": 3, "desc": "Giá quặng sắt trên sàn Singapore và than mỡ luyện thép biến động theo chu kỳ hàng hóa."},
            "buyer_power": {"score": 3, "desc": "Nhà thầu xây dựng và đại lý phân phối thép có tính nhạy cảm cao về giá thép thành phẩm."},
            "substitution_threat": {"score": 1, "desc": "Thép xây dựng và cuộn cán nóng HRC là vật liệu cốt lõi không thể thay thế."},
            "new_entrants_threat": {"score": 1, "desc": "Suất đầu tư tổ hợp luyện thép lò cao BOF hàng tỷ USD là rào cản độc quyền tự nhiên."}
        },
        "recommended_valuation": {
            "method": "P/E & P/B Chu kỳ Thép",
            "badge": "Khuyên dùng: P/E & P/B",
            "rationale": "Ngành thép là ngành mang tính chu kỳ cao; định giá P/B ở vùng đáy chu kỳ và P/E bình quân chu kỳ đem lại tỷ lệ an toàn cao nhất.",
            "priority_tab": "pe"
        }
    },

    # 8. Dầu khí & Dịch vụ E&P
    "OIL_GAS_SERVICES": {
        "sector_name": "Dầu khí & Dịch vụ",
        "cycle": "Chu kỳ Đầu tư Thượng nguồn Mới & Đại Dự án Khí Điện Lô B Ô Môn 12 Tỷ USD",
        "sector_kpi_columns": [
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "emerald"},
            {"field": "capex_rev_ratio", "label": "Capex/DT (%)", "unit": "%", "color": "amber"},
            {"field": "output_volume", "label": "SL (tr.m³/tấn)", "unit": "tr.đv", "color": "sky"}
        ],
        "peers": [
            {"ticker": "GAS", "name": "PV GAS", "market_cap_bil": 165000.0, "pe": 15.2, "pb": 2.65, "roe": 18.5, "roa": 12.2, "net_margin": 14.5, "debt_to_equity": 0.15, "revenue_growth_yoy": 10.5, "ebitda_margin": 22.5, "capex_rev_ratio": 8.5, "output_volume": 9.8},
            {"ticker": "PLX", "name": "Petrolimex", "market_cap_bil": 68500.0, "pe": 18.5, "pb": 2.10, "roe": 12.5, "roa": 5.2, "net_margin": 2.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 8.5, "ebitda_margin": 5.8, "capex_rev_ratio": 3.5, "output_volume": 0.0},
            {"ticker": "BSR", "name": "Lọc hóa dầu Bình Sơn", "market_cap_bil": 68000.0, "pe": 9.2, "pb": 1.10, "roe": 14.8, "roa": 8.5, "net_margin": 6.2, "debt_to_equity": 0.22, "revenue_growth_yoy": 8.2, "ebitda_margin": 10.5, "capex_rev_ratio": 5.2, "output_volume": 0.0},
            {"ticker": "PVS", "name": "Kỹ thuật Dầu khí (PTSC)", "market_cap_bil": 19500.0, "pe": 18.5, "pb": 1.45, "roe": 10.2, "roa": 4.5, "net_margin": 5.8, "debt_to_equity": 0.28, "revenue_growth_yoy": 18.0, "ebitda_margin": 12.5, "capex_rev_ratio": 4.5, "output_volume": 0.0},
            {"ticker": "PVD", "name": "Khoan Dầu khí (PV Drilling)", "market_cap_bil": 15800.0, "pe": 24.5, "pb": 1.20, "roe": 7.5, "roa": 3.8, "net_margin": 8.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 16.5, "ebitda_margin": 35.0, "capex_rev_ratio": 22.0, "output_volume": 0.0},
            {"ticker": "PVT", "name": "PV Trans", "market_cap_bil": 10500.0, "pe": 8.2, "pb": 1.15, "roe": 16.5, "roa": 7.8, "net_margin": 12.8, "debt_to_equity": 0.58, "revenue_growth_yoy": 12.5, "ebitda_margin": 24.5, "capex_rev_ratio": 14.5, "output_volume": 0.0}
        ],
        "catalysts": [
            "Đại dự án Khí - Điện Lô B Ô Môn (12 tỷ USD) bước vào giai đoạn thi công cao điểm đem lại lượng backlog khổng lồ cho PVS, PVD.",
            "Thị trường giàn khoan tự nâng khu vực Đông Nam Á khan hiếm nguồn cung, đẩy đơn giá thuê ngày (Day Rate) lên đỉnh chu kỳ.",
            "Các dự án mỏ mới (Lạc Đà Vàng, Đại Hùng pha 3) được triển khai đảm bảo sản lượng khai thác dầu khí dài hạn."
        ],
        "risks": [
            "Biến động giá dầu thô Brent thế giới theo chính sách sản lượng của OPEC+.",
            "Tiến độ giải ngân các gói thầu dự án dầu khí thượng nguồn có thể bị ảnh hưởng bởi thủ tục pháp lý."
        ],
        "forces": {
            "rivalry": {"score": 2, "desc": "Hệ sinh thái kỹ thuật ngoài khơi Việt Nam có tính tập trung cao vào các đơn vị chủ chốt của Petrovietnam."},
            "supplier_power": {"score": 3, "desc": "Phụ thuộc vào các nhà sản xuất giàn khoan, máy móc chuyên dụng và biến động giá dầu thế giới."},
            "buyer_power": {"score": 3, "desc": "Các nhà điều hành dầu khí quốc tế (IOCs) có quy chuẩn an toàn kỹ thuật khắt khe."},
            "substitution_threat": {"score": 2, "desc": "Năng lượng tái tạo đang phát triển nhưng khí và xăng dầu vẫn là năng lượng nền tảng."},
            "new_entrants_threat": {"score": 1, "desc": "Yêu cầu kinh nghiệm thi công ngoài khơi (offshore) và chứng chỉ an toàn mỏ quốc tế."}
        },
        "recommended_valuation": {
            "method": "EV/EBITDA & P/E Chu kỳ Hàng hóa",
            "badge": "Khuyên dùng: EV/EBITDA",
            "rationale": "Doanh nghiệp dầu khí có chi phí khấu hao TSCĐ giàn khoan/tàu dầu rất lớn; chỉ số EV/EBITDA phản ánh dòng tiền cốt lõi trung thực nhất.",
            "priority_tab": "pe"
        }
    },

    # 9. Điện & Năng lượng
    "POWER_UTILITIES": {
        "sector_name": "Điện & Năng lượng",
        "cycle": "Triển khai Quy hoạch Điện VIII & Nhu cầu Phụ tải Công nghiệp Tăng trưởng Cao",
        "sector_kpi_columns": [
            {"field": "installed_capacity_mw", "label": "Công suất (MW)", "unit": "MW", "color": "emerald"},
            {"field": "ppa_output_mil_kwh", "label": "Sản lượng (tr.kWh)", "unit": "tr.kWh", "color": "sky"},
            {"field": "debt_to_equity", "label": "Đòn bẩy D/E", "unit": "x", "color": "rose"}
        ],
        "peers": [
            {"ticker": "POW", "name": "Tổng Công ty Điện lực Dầu khí (PV Power)", "market_cap_bil": 31500.0, "pe": 15.5, "pb": 0.95, "roe": 6.8, "roa": 3.5, "net_margin": 5.8, "debt_to_equity": 0.35, "revenue_growth_yoy": 12.0, "installed_capacity_mw": 4205.0, "ppa_output_mil_kwh": 16500.0},
            {"ticker": "PGV", "name": "Tổng Công ty Phát điện 3 (EVNGENCO3)", "market_cap_bil": 25500.0, "pe": 11.2, "pb": 1.65, "roe": 15.5, "roa": 4.8, "net_margin": 6.5, "debt_to_equity": 1.85, "revenue_growth_yoy": 10.5, "installed_capacity_mw": 6560.0, "ppa_output_mil_kwh": 31000.0},
            {"ticker": "REE", "name": "Cơ Điện Lạnh (REE Corp)", "market_cap_bil": 30500.0, "pe": 11.8, "pb": 1.45, "roe": 14.5, "roa": 8.5, "net_margin": 28.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 14.0, "installed_capacity_mw": 1150.0, "ppa_output_mil_kwh": 4800.0},
            {"ticker": "PC1", "name": "Tập đoàn PC1", "market_cap_bil": 9800.0, "pe": 16.8, "pb": 1.25, "roe": 8.2, "roa": 3.1, "net_margin": 6.2, "debt_to_equity": 1.45, "revenue_growth_yoy": 15.5, "installed_capacity_mw": 450.0, "ppa_output_mil_kwh": 1850.0},
            {"ticker": "HDG", "name": "Tập đoàn Hà Đô", "market_cap_bil": 12500.0, "pe": 14.5, "pb": 1.25, "roe": 9.5, "roa": 3.8, "net_margin": 18.5, "debt_to_equity": 0.85, "revenue_growth_yoy": 18.5, "installed_capacity_mw": 462.0, "ppa_output_mil_kwh": 1500.0},
            {"ticker": "VSH", "name": "Thủy điện Vĩnh Sơn Sông Hinh", "market_cap_bil": 10500.0, "pe": 12.5, "pb": 1.85, "roe": 16.5, "roa": 7.2, "net_margin": 38.5, "debt_to_equity": 0.95, "revenue_growth_yoy": 11.5, "installed_capacity_mw": 356.0, "ppa_output_mil_kwh": 2100.0},
            {"ticker": "GEG", "name": "Điện Gia Lai", "market_cap_bil": 4200.0, "pe": 18.5, "pb": 1.05, "roe": 6.5, "roa": 2.2, "net_margin": 8.5, "debt_to_equity": 1.95, "revenue_growth_yoy": 14.0, "installed_capacity_mw": 480.0, "ppa_output_mil_kwh": 1200.0}
        ],
        "catalysts": [
            "Nhu cầu tiêu thụ điện toàn quốc tăng trưởng trên 10-12%/năm song hành cùng làn sóng vốn FDI sản xuất công nghiệp.",
            "Cơ chế mua bán điện trực tiếp (DPPA) và khung giá mới cho các dự án chuyển tiếp năng lượng tái tạo.",
            "Dự án Nhà máy điện Nhơn Trạch 3 & 4 (LNG) hoàn thành và phát điện thương mại, mở ra nguồn doanh thu lớn cho POW."
        ],
        "risks": [
            "Hiện tượng thời tiết El Nino/La Nina làm giảm sản lượng nước về các hồ thủy điện.",
            "Áp lực thanh toán tiền điện từ phía EVN trong các giai đoạn căng thẳng dòng tiền."
        ],
        "forces": {
            "rivalry": {"score": 2, "desc": "Sản lượng phát điện huy động theo hợp đồng PPA dài hạn và điều độ lưới điện quốc gia A0."},
            "supplier_power": {"score": 3, "desc": "Giá than, khí đầu vào và biến động thủy văn mùa mưa/khô tác động trực tiếp tới biên lợi nhuận."},
            "buyer_power": {"score": 4, "desc": "EVN là khách hàng mua điện độc quyền duy nhất."},
            "substitution_threat": {"score": 1, "desc": "Năng lượng điện là huyết mạch cơ sở hạ tầng thiết yếu không thể thay thế."},
            "new_entrants_threat": {"score": 2, "desc": "Chi phí đầu tư Capex nhà máy điện rất lớn và quy hoạch pháp lý nguồn điện chặt chẽ."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền Dự án & Tỷ suất Cổ tức",
            "badge": "Khuyên dùng: DCF & Cổ tức",
            "rationale": "Các nhà máy điện có hợp đồng PPA bao tiêu sản lượng nhiều năm đem lại dòng tiền tự do (FCFE) cực kỳ ổn định, chi trả cổ tức tiền mặt đều đặn.",
            "priority_tab": "dcf"
        }
    },

    # 10. Hóa chất & Phân bón
    "CHEMICALS_FERTILIZERS": {
        "sector_name": "Hóa chất & Phân bón",
        "cycle": "Chu kỳ Giá Phốt pho Vàng & Đột phá Chuỗi Bán dẫn Toàn cầu",
        "sector_kpi_columns": [
            {"field": "net_margin", "label": "Biên ròng (%)", "unit": "%", "color": "emerald"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "sky"},
            {"field": "export_ratio_percent", "label": "Tỷ lệ XK (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "DGC", "name": "Tập đoàn Hóa chất Đức Giang", "market_cap_bil": 42500.0, "pe": 12.8, "pb": 3.10, "roe": 26.5, "roa": 19.5, "net_margin": 31.5, "debt_to_equity": 0.08, "revenue_growth_yoy": 14.2, "export_ratio_percent": 68.0, "ebitda_margin": 38.5},
            {"ticker": "DCM", "name": "Phân bón Dầu khí Cà Mau", "market_cap_bil": 21500.0, "pe": 11.5, "pb": 1.75, "roe": 17.5, "roa": 11.2, "net_margin": 12.8, "debt_to_equity": 0.12, "revenue_growth_yoy": 9.5, "export_ratio_percent": 32.0, "ebitda_margin": 18.5},
            {"ticker": "DPM", "name": "Đạm Phú Mỹ (PVFCCo)", "market_cap_bil": 18500.0, "pe": 10.8, "pb": 1.65, "roe": 16.2, "roa": 10.5, "net_margin": 11.5, "debt_to_equity": 0.08, "revenue_growth_yoy": 8.8, "export_ratio_percent": 25.0, "ebitda_margin": 17.0},
            {"ticker": "BFC", "name": "Phân bón Bình Điền", "market_cap_bil": 3800.0, "pe": 11.2, "pb": 1.55, "roe": 15.5, "roa": 6.8, "net_margin": 5.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 12.0, "export_ratio_percent": 15.0, "ebitda_margin": 9.5},
            {"ticker": "CSV", "name": "Hóa chất Cơ bản Miền Nam", "market_cap_bil": 4500.0, "pe": 12.5, "pb": 2.25, "roe": 18.5, "roa": 12.5, "net_margin": 16.8, "debt_to_equity": 0.15, "revenue_growth_yoy": 11.5, "export_ratio_percent": 18.0, "ebitda_margin": 24.5},
            {"ticker": "LAS", "name": "Supe Phốt phát Lâm Thao", "market_cap_bil": 2400.0, "pe": 10.5, "pb": 1.45, "roe": 14.2, "roa": 7.5, "net_margin": 6.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 10.0, "export_ratio_percent": 12.0, "ebitda_margin": 11.5}
        ],
        "catalysts": [
            "Nhu cầu Phốt pho vàng (P4) và Axit Photphoric điện tử tăng vọt phục vụ các nhà máy chip bán dẫn và pin xe điện.",
            "Tổ hợp Hóa chất Đức Giang Nghi Sơn (12.000 tỷ) bước vào giai đoạn xây dựng mở ra động lực tăng trưởng dài hạn.",
            "Luật Thuế VAT sửa đổi áp thuế VAT 5% cho mặt hàng phân bón giúp doanh nghiệp được hoàn thuế đầu vào hàng trăm tỷ đồng."
        ],
        "risks": [
            "Biến động giá nguyên liệu khí tự nhiên đầu vào cho các nhà máy đạm urê.",
            "Rủi ro suy giảm giá phân bón và hóa chất trên thị trường thế giới khi nguồn cung Trung Quốc mở rộng."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh phân khúc phân bón nội địa; DGC nắm độc quyền tự nhiên mảng phốt pho vàng xuất khẩu."},
            "supplier_power": {"score": 3, "desc": "Phụ thuộc vào quặng apatit tuyển và nguồn cung khí tự nhiên ngoài khơi."},
            "buyer_power": {"score": 3, "desc": "Nông dân và đại lý phân phối nhạy cảm với mùa vụ nông nghiệp."},
            "substitution_threat": {"score": 1, "desc": "Hóa chất cơ bản và phân bón NPK là vật tư nông nghiệp thiết yếu không thể thay thế."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản giấy phép môi trường hóa chất, dây chuyền nhiệt điện lò phốt pho và quy hoạch hóa chất quốc gia."}
        },
        "recommended_valuation": {
            "method": "EV/EBITDA & P/E Chu kỳ Hàng hóa",
            "badge": "Khuyên dùng: EV/EBITDA",
            "rationale": "Doanh nghiệp hóa chất có biên lợi nhuận gộp phụ thuộc vào chu kỳ hàng hóa quốc tế và sở hữu lượng tiền mặt ròng dồi dào.",
            "priority_tab": "pe"
        }
    },

    # 11. Xây dựng & Hạ tầng
    "CONSTRUCTION_INFRA": {
        "sector_name": "Xây dựng & Hạ tầng",
        "cycle": "Giai đoạn Đỉnh điểm Giải ngân Siêu dự án Hạ tầng & Đầu tư công Quốc gia",
        "sector_kpi_columns": [
            {"field": "order_backlog_bil", "label": "Backlog (tỷ VND)", "unit": "tỷ VND", "color": "amber"},
            {"field": "days_receivable", "label": "Chu kỳ thu (ngày)", "unit": "ngày", "color": "rose"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "emerald"}
        ],
        "peers": [
            {"ticker": "CTD", "name": "CTCP Xây dựng Coteccons", "market_cap_bil": 7200.0, "pe": 16.5, "pb": 0.85, "roe": 6.8, "roa": 2.5, "net_margin": 2.2, "debt_to_equity": 0.35, "revenue_growth_yoy": 18.5, "order_backlog_bil": 35000.0, "days_receivable": 95.0, "ebitda_margin": 4.5},
            {"ticker": "VCG", "name": "Tổng CTCP Vinaconex", "market_cap_bil": 12500.0, "pe": 14.2, "pb": 1.10, "roe": 9.5, "roa": 3.2, "net_margin": 4.5, "debt_to_equity": 1.20, "revenue_growth_yoy": 16.0, "order_backlog_bil": 22000.0, "days_receivable": 120.0, "ebitda_margin": 8.5},
            {"ticker": "HHV", "name": "Hạ tầng Giao thông Đèo Cả", "market_cap_bil": 5600.0, "pe": 13.5, "pb": 0.95, "roe": 8.5, "roa": 2.8, "net_margin": 12.5, "debt_to_equity": 1.85, "revenue_growth_yoy": 14.0, "order_backlog_bil": 18000.0, "days_receivable": 145.0, "ebitda_margin": 28.5},
            {"ticker": "PC1", "name": "Tập đoàn PC1", "market_cap_bil": 9800.0, "pe": 16.8, "pb": 1.25, "roe": 8.2, "roa": 3.1, "net_margin": 6.2, "debt_to_equity": 1.45, "revenue_growth_yoy": 15.5, "order_backlog_bil": 28000.0, "days_receivable": 110.0, "ebitda_margin": 12.5},
            {"ticker": "CII", "name": "Đầu tư Hạ tầng Kỹ thuật TPHCM", "market_cap_bil": 8500.0, "pe": 18.5, "pb": 1.15, "roe": 7.5, "roa": 2.2, "net_margin": 15.5, "debt_to_equity": 2.15, "revenue_growth_yoy": 12.0, "order_backlog_bil": 15000.0, "days_receivable": 185.0, "ebitda_margin": 32.0},
            {"ticker": "FCN", "name": "CTCP FECON", "market_cap_bil": 3800.0, "pe": 12.5, "pb": 0.85, "roe": 7.2, "roa": 2.8, "net_margin": 5.5, "debt_to_equity": 0.95, "revenue_growth_yoy": 19.5, "order_backlog_bil": 8500.0, "days_receivable": 88.0, "ebitda_margin": 9.5}
        ],
        "catalysts": [
            "Đẩy mạnh giải ngân vốn đầu tư công hạ tầng giao thông quy mô kỷ lục (Sân bay Long Thành, Cao tốc Bắc - Nam).",
            "Giá trị hợp đồng ký mới (Backlog) của các tổng thầu xây dựng hàng đầu đạt mức kỷ lục hàng chục nghìn tỷ đồng.",
            "Mô hình thu phí giao thông tự động (ETC) tại các dự án BOT mang lại dòng tiền mặt dồi dào, ổn định."
        ],
        "risks": [
            "Rủi ro biến động giá nguyên vật liệu xây dựng (thép, xi măng, đá, cát san lấp) đối với các hợp đồng đơn giá cố định.",
            "Áp lực thu hồi công nợ và thời gian quyết toán nghiệm thu kéo dài."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh hồ sơ năng lực và giá thầu trong các liên danh xây lắp dự án trọng điểm quốc gia."},
            "supplier_power": {"score": 3, "desc": "Giá cát, đá xây dựng và xi măng phụ thuộc vào cự ly vận chuyển và mỏ khai thác địa phương."},
            "buyer_power": {"score": 4, "desc": "Chủ đầu tư Ban quản lý dự án nhà nước có quy chuẩn nghiệm thu thanh quyết toán chặt chẽ."},
            "substitution_threat": {"score": 1, "desc": "Hạ tầng cầu đường, cao tốc là công trình độc quyền tự nhiên không thể thay thế."},
            "new_entrants_threat": {"score": 2, "desc": "Yêu cầu máy móc cơ giới hiện đại, vốn ứng trước và kinh nghiệm hoàn thành gói thầu tương đương."}
        },
        "recommended_valuation": {
            "method": "P/E & P/B Theo Backlog Hợp đồng",
            "badge": "Khuyên dùng: P/E & Backlog",
            "rationale": "Doanh thu tương lai của nhà thầu xây lắp được bảo chứng bằng khối lượng hợp đồng đã ký (Backlog); P/E kết hợp P/B phản ánh đúng giá trị doanh nghiệp.",
            "priority_tab": "pe"
        }
    },

    # 12. Vật liệu Xây dựng
    "BUILDING_MATERIALS": {
        "sector_name": "Vật liệu Xây dựng",
        "cycle": "Hưởng lợi từ Siêu dự án Hạ tầng & Giải ngân Đầu tư công trọng điểm",
        "sector_kpi_columns": [
            {"field": "sales_volume_kton", "label": "Sản lượng (kt)", "unit": "kt", "color": "emerald"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "sky"},
            {"field": "debt_to_equity", "label": "Đòn bẩy D/E", "unit": "x", "color": "rose"}
        ],
        "peers": [
            {"ticker": "KSB", "name": "Khoáng sản Bình Dương", "market_cap_bil": 3800.0, "pe": 14.5, "pb": 1.25, "roe": 9.5, "roa": 4.8, "net_margin": 14.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 15.0, "sales_volume_kton": 4500.0, "ebitda_margin": 28.5},
            {"ticker": "HT1", "name": "Xi măng Hà Tiên 1", "market_cap_bil": 5200.0, "pe": 16.5, "pb": 1.05, "roe": 6.8, "roa": 3.5, "net_margin": 3.8, "debt_to_equity": 0.45, "revenue_growth_yoy": 10.5, "sales_volume_kton": 6200.0, "ebitda_margin": 12.5},
            {"ticker": "BMP", "name": "Nhựa Bình Minh", "market_cap_bil": 10500.0, "pe": 9.8, "pb": 3.65, "roe": 36.5, "roa": 28.5, "net_margin": 22.5, "debt_to_equity": 0.08, "revenue_growth_yoy": 12.0, "sales_volume_kton": 110.0, "ebitda_margin": 28.0},
            {"ticker": "NTP", "name": "Nhựa Tiền Phong", "market_cap_bil": 6800.0, "pe": 10.5, "pb": 2.15, "roe": 22.5, "roa": 14.5, "net_margin": 12.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 11.5, "sales_volume_kton": 95.0, "ebitda_margin": 18.5},
            {"ticker": "VCS", "name": "Vicostone", "market_cap_bil": 9800.0, "pe": 11.2, "pb": 2.25, "roe": 22.0, "roa": 16.5, "net_margin": 18.5, "debt_to_equity": 0.22, "revenue_growth_yoy": 9.5, "sales_volume_kton": 450.0, "ebitda_margin": 24.5},
            {"ticker": "PTB", "name": "Phú Tài", "market_cap_bil": 4200.0, "pe": 10.8, "pb": 1.45, "roe": 14.5, "roa": 7.2, "net_margin": 6.8, "debt_to_equity": 0.58, "revenue_growth_yoy": 12.5, "sales_volume_kton": 250.0, "ebitda_margin": 14.0}
        ],
        "catalysts": [
            "Nhu cầu đá xây dựng và vật liệu tăng vọt từ các đại dự án Sân bay Long Thành, Vành đai 3, Cao tốc Bắc - Nam.",
            "Các doanh nghiệp sở hữu mỏ đá trữ lượng lớn và thời hạn cấp phép dài có lợi thế cạnh tranh độc quyền tự nhiên.",
            "Giá hạt nhựa PVC nguyên liệu duy trì ở mức thấp giúp nới rộng biên lợi nhuận ròng của BMP, NTP."
        ],
        "risks": [
            "Bán kính vận chuyển vật liệu đá bị giới hạn (dưới 50-70km để tối ưu chi phí vận chuyển đường bộ).",
            "Quy định nghiêm ngặt về đánh giá tác động môi trường mỏ khai thác và thủ tục cấp phép gia hạn mỏ mới."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh theo bán kính địa lý vận chuyển; các doanh nghiệp gần công trình hưởng lợi thế tuyệt đối."},
            "supplier_power": {"score": 2, "desc": "Thiết bị nghiền sàng và vật liệu nổ công nghiệp nguồn cung dồi dào, ổn định."},
            "buyer_power": {"score": 3, "desc": "Các nhà thầu xây dựng ưu tiên đơn vị có sản lượng cung ứng liên tục và chất lượng đá ổn định."},
            "substitution_threat": {"score": 1, "desc": "Đá xây dựng và cát nhân tạo là vật liệu nền tảng không thể thay thế trong bê tông."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản pháp lý cấp phép khai thác mỏ mới kéo dài nhiều năm rất khó thâm nhập."}
        },
        "recommended_valuation": {
            "method": "EV/EBITDA & P/E Theo Giải ngân Đầu tư công",
            "badge": "Khuyên dùng: EV/EBITDA",
            "rationale": "Doanh nghiệp vật liệu xây dựng có dòng tiền kinh doanh tốt và khấu hao mỏ/nhà máy lớn; EV/EBITDA là phương pháp tối ưu.",
            "priority_tab": "pe"
        }
    },

    # 13. Cảng biển & Cầu bến nước sâu
    "PORTS_MARITIME": {
        "sector_name": "Cảng biển & Bến bãi",
        "cycle": "Phục hồi Xuất nhập khẩu & Xu hướng Dịch chuyển Hàng hóa ra Cảng Nước sâu",
        "sector_kpi_columns": [
            {"field": "throughput_teu", "label": "Thông lượng (k TEU)", "unit": "k TEU", "color": "sky"},
            {"field": "utilization_rate", "label": "Lấp đầy bến (%)", "unit": "%", "color": "emerald"},
            {"field": "berth_length_m", "label": "Cầu bến (m)", "unit": "m", "color": "amber"}
        ],
        "peers": [
            {"ticker": "GMD", "name": "CTCP Gemadept", "market_cap_bil": 24500.0, "pe": 13.8, "pb": 2.40, "roe": 19.2, "roa": 11.5, "net_margin": 24.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 15.0, "throughput_teu": 1850.0, "utilization_rate": 85.0, "berth_length_m": 1500.0},
            {"ticker": "DVP", "name": "Cảng Đình Vũ", "market_cap_bil": 5200.0, "pe": 10.5, "pb": 2.80, "roe": 28.5, "roa": 16.5, "net_margin": 42.5, "debt_to_equity": 0.18, "revenue_growth_yoy": 9.5, "throughput_teu": 680.0, "utilization_rate": 92.0, "berth_length_m": 425.0},
            {"ticker": "PHP", "name": "Cảng Hải Phòng", "market_cap_bil": 8500.0, "pe": 12.5, "pb": 2.20, "roe": 19.5, "roa": 10.5, "net_margin": 28.5, "debt_to_equity": 0.42, "revenue_growth_yoy": 11.5, "throughput_teu": 1200.0, "utilization_rate": 88.0, "berth_length_m": 1200.0},
            {"ticker": "SGP", "name": "Cảng Sài Gòn", "market_cap_bil": 3200.0, "pe": 12.8, "pb": 2.45, "roe": 20.5, "roa": 11.5, "net_margin": 32.0, "debt_to_equity": 0.28, "revenue_growth_yoy": 10.5, "throughput_teu": 980.0, "utilization_rate": 87.0, "berth_length_m": 850.0},
            {"ticker": "CLL", "name": "Cảng Cát Lái", "market_cap_bil": 4800.0, "pe": 11.2, "pb": 3.10, "roe": 30.5, "roa": 18.2, "net_margin": 38.5, "debt_to_equity": 0.12, "revenue_growth_yoy": 8.2, "throughput_teu": 5200.0, "utilization_rate": 95.0, "berth_length_m": 900.0},
            {"ticker": "VSC", "name": "Viconship", "market_cap_bil": 6800.0, "pe": 14.5, "pb": 1.45, "roe": 11.5, "roa": 6.8, "net_margin": 16.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 18.0, "throughput_teu": 1150.0, "utilization_rate": 85.0, "berth_length_m": 1100.0}
        ],
        "catalysts": [
            "Kim ngạch xuất nhập khẩu của Việt Nam tăng trưởng tích cực hỗ trợ sản lượng hàng hóa thông qua cảng biển toàn quốc.",
            "Cụm cảng nước sâu Cái Mép - Thị Vải và Lạch Huyện đón trọn các tuyến tàu mẹ trực tiếp đi Mỹ và Châu Âu.",
            "Dự án Cảng Gemalink giai đoạn 2 và Nam Đình Vũ mở rộng công suất tiếp nhận hàng triệu TEU mỗi năm."
        ],
        "risks": [
            "Rủi ro suy giảm sản lượng hàng hóa xuất nhập khẩu nếu các nền kinh tế đối tác lớn (Mỹ, EU) suy giảm tiêu dùng.",
            "Cạnh tranh công suất cầu cảng tại các khu vực cảng sông nội địa."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh thị phần xếp dỡ tại các cụm cảng sông nội địa; cảng nước sâu giữ lợi thế vượt trội."},
            "supplier_power": {"score": 2, "desc": "Nguồn cung thiết bị cẩu bốc dỡ chuyên dụng và tàu lai dắt dồi dào."},
            "buyer_power": {"score": 3, "desc": "Các hãng tàu quốc tế (Maersk, MSC, CMA CGM) có quyền đàm phán khung giá xếp dỡ."},
            "substitution_threat": {"score": 1, "desc": "Cảng biển là cửa ngõ giao thương xuất nhập khẩu hàng hóa duy nhất có chi phí tối ưu."},
            "new_entrants_threat": {"score": 1, "desc": "Chi phí đầu tư nạo vét luồng hàng hải và cấp phép cầu cảng nước sâu cực kỳ khó khăn."}
        },
        "recommended_valuation": {
            "method": "DCF Chiết khấu Cầu cảng & EV/EBITDA",
            "badge": "Khuyên dùng: DCF & EV/EBITDA",
            "rationale": "Cảng biển là tài sản cơ sở hạ tầng có vòng đời khai thác hàng chục năm và dòng tiền tiền mặt thặng dư đều đặn; DCF và EV/EBITDA là tối ưu.",
            "priority_tab": "dcf"
        }
    },

    # 14. Vận tải & Logistics
    "SHIPPING_LOGISTICS": {
        "sector_name": "Vận tải & Logistics",
        "cycle": "Tăng trưởng Quy mô Đội tàu & Diễn biến Cước Vận tải Biển Toàn cầu",
        "sector_kpi_columns": [
            {"field": "fleet_count", "label": "Đội tàu (chiếc)", "unit": "chiếc", "color": "amber"},
            {"field": "freight_rate_index", "label": "Chỉ số cước", "unit": "pts", "color": "sky"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "emerald"}
        ],
        "peers": [
            {"ticker": "HAH", "name": "Vận tải Xếp dỡ Hải An", "market_cap_bil": 5800.0, "pe": 9.5, "pb": 1.55, "roe": 18.5, "roa": 10.2, "net_margin": 18.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 14.2, "fleet_count": 15.0, "freight_rate_index": 125.0, "ebitda_margin": 32.0},
            {"ticker": "PVT", "name": "PV Trans", "market_cap_bil": 10500.0, "pe": 8.2, "pb": 1.15, "roe": 16.5, "roa": 7.8, "net_margin": 12.8, "debt_to_equity": 0.58, "revenue_growth_yoy": 12.5, "fleet_count": 52.0, "freight_rate_index": 115.0, "ebitda_margin": 26.5},
            {"ticker": "VOS", "name": "Vận tải Biển Việt Nam", "market_cap_bil": 2100.0, "pe": 11.5, "pb": 1.25, "roe": 12.2, "roa": 6.5, "net_margin": 9.5, "debt_to_equity": 0.42, "revenue_growth_yoy": 8.5, "fleet_count": 14.0, "freight_rate_index": 105.0, "ebitda_margin": 18.0},
            {"ticker": "VJC", "name": "Vietjet Air", "market_cap_bil": 62000.0, "pe": 22.0, "pb": 2.95, "roe": 14.5, "roa": 3.8, "net_margin": 3.5, "debt_to_equity": 2.45, "revenue_growth_yoy": 24.0, "fleet_count": 105.0, "freight_rate_index": 110.0, "ebitda_margin": 14.5},
            {"ticker": "HVN", "name": "Vietnam Airlines", "market_cap_bil": 55000.0, "pe": 16.5, "pb": 3.10, "roe": 12.5, "roa": 2.5, "net_margin": 2.8, "debt_to_equity": 3.85, "revenue_growth_yoy": 18.5, "fleet_count": 100.0, "freight_rate_index": 108.0, "ebitda_margin": 12.0},
            {"ticker": "VIP", "name": "Vận tải Xăng dầu VIPCO", "market_cap_bil": 1250.0, "pe": 8.5, "pb": 0.95, "roe": 12.0, "roa": 6.8, "net_margin": 11.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 9.0, "fleet_count": 8.0, "freight_rate_index": 112.0, "ebitda_margin": 22.0},
            {"ticker": "VTO", "name": "Vận tải Xăng dầu VITACO", "market_cap_bil": 1100.0, "pe": 8.8, "pb": 0.90, "roe": 11.5, "roa": 6.5, "net_margin": 10.8, "debt_to_equity": 0.28, "revenue_growth_yoy": 8.5, "fleet_count": 7.0, "freight_rate_index": 110.0, "ebitda_margin": 21.5}
        ],
        "catalysts": [
            "Giá cước vận tải biển container và cước tàu chở dầu/khí duy trì mức cao do lộ trình vận tải biển kéo dài.",
            "Chiến lược đầu tư trẻ hóa đội tàu viễn dương quy mô lớn giúp tăng năng lực chuyên chở trên các tuyến quốc tế.",
            "Phục hồi mạnh mẽ của lưu lượng hành khách và hàng hóa hàng không quốc tế."
        ],
        "risks": [
            "Biến động giá dầu nhiên liệu hàng hải (Bunker Fuel / Jet A1) tác động trực tiếp tới chi phí vận hành.",
            "Cạnh tranh thị phần cước vận chuyển từ các liên minh hãng tàu quốc tế lớn."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh về giá cước trên các tuyến vận tải nội địa và nội Á."},
            "supplier_power": {"score": 3, "desc": "Chi phí đóng mới tàu biển và giá nhiên liệu biến động theo thị trường toàn cầu."},
            "buyer_power": {"score": 3, "desc": "Chủ hàng có thể lựa chọn linh hoạt giữa các hãng vận chuyển tùy vào lịch trình chuyến."},
            "substitution_threat": {"score": 2, "desc": "Vận tải đường bộ và đường sắt cạnh tranh các cung đường ngắn nội địa."},
            "new_entrants_threat": {"score": 2, "desc": "Chi phí vốn mua sắm đội tàu và yêu cầu chứng nhận an toàn hàng hải quốc tế."}
        },
        "recommended_valuation": {
            "method": "P/B Đội tàu & EV/EBITDA Cước vận tải",
            "badge": "Khuyên dùng: P/B & EV/EBITDA",
            "rationale": "Doanh nghiệp vận tải có giá trị đội tàu chi phối phần lớn tổng tài sản; định giá P/B và EV/EBITDA bám sát chu kỳ cước vận tải là thích hợp nhất.",
            "priority_tab": "pb"
        }
    },

    # 15. Thực phẩm, Đồ uống & FMCG
    "FOOD_BEVERAGE": {
        "sector_name": "Thực phẩm & Đồ uống",
        "cycle": "Mở rộng Thị phần Hàng Tiêu dùng Nhanh & Tối ưu Biên Lợi nhuận Chuỗi Giá trị",
        "sector_kpi_columns": [
            {"field": "gross_margin", "label": "Biên gộp (%)", "unit": "%", "color": "emerald"},
            {"field": "net_margin", "label": "Biên ròng (%)", "unit": "%", "color": "sky"},
            {"field": "inventory_turnover", "label": "Vòng quay tồn kho", "unit": "vòng", "color": "amber"}
        ],
        "peers": [
            {"ticker": "VNM", "name": "Vinamilk", "market_cap_bil": 142000.0, "pe": 16.5, "pb": 4.10, "roe": 28.5, "roa": 18.5, "net_margin": 17.5, "debt_to_equity": 0.18, "revenue_growth_yoy": 6.5, "gross_margin": 42.5, "inventory_turnover": 6.8},
            {"ticker": "MSN", "name": "Tập đoàn Masan", "market_cap_bil": 115000.0, "pe": 26.5, "pb": 2.95, "roe": 10.5, "roa": 3.8, "net_margin": 4.8, "debt_to_equity": 1.45, "revenue_growth_yoy": 12.0, "gross_margin": 28.5, "inventory_turnover": 7.2},
            {"ticker": "SAB", "name": "Sabeco (Bia Sài Gòn)", "market_cap_bil": 75000.0, "pe": 17.5, "pb": 3.10, "roe": 19.5, "roa": 14.5, "net_margin": 15.5, "debt_to_equity": 0.12, "revenue_growth_yoy": 5.5, "gross_margin": 32.5, "inventory_turnover": 8.5},
            {"ticker": "QNS", "name": "Đường Quảng Ngãi", "market_cap_bil": 17500.0, "pe": 8.2, "pb": 1.85, "roe": 24.2, "roa": 14.5, "net_margin": 18.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 12.4, "gross_margin": 32.0, "inventory_turnover": 6.2},
            {"ticker": "KDC", "name": "Tập đoàn KIDO", "market_cap_bil": 14500.0, "pe": 18.5, "pb": 1.65, "roe": 9.5, "roa": 5.2, "net_margin": 6.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 10.5, "gross_margin": 24.5, "inventory_turnover": 7.8},
            {"ticker": "MCH", "name": "Masan Consumer", "market_cap_bil": 145000.0, "pe": 20.5, "pb": 6.80, "roe": 35.0, "roa": 22.5, "net_margin": 24.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 15.0, "gross_margin": 45.0, "inventory_turnover": 8.2}
        ],
        "catalysts": [
            "Giá nguyên liệu sữa bột, đường và lúa mì thế giới hạ nhiệt giúp cải thiện mạnh biên lợi nhuận gộp.",
            "Tái định vị nhận diện thương hiệu và mở rộng danh mục sản phẩm cao cấp, hữu cơ, ít đường.",
            "Hệ sinh thái phân phối bán lẻ hiện đại (WinCommerce) cộng hưởng mạnh mẽ giúp tối ưu hóa chi phí bán hàng."
        ],
        "risks": [
            "Nghị định 100 kiểm soát nồng độ cồn tác động đến sản lượng tiêu thụ ngành bia.",
            "Cạnh tranh gay gắt từ các thương hiệu thực phẩm nhập khẩu và xu hướng ăn uống lành mạnh thay thế."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh thị phần gay gắt về ngân sách quảng cáo, khuyến mại và chiếm giữ vị trí kệ hàng."},
            "supplier_power": {"score": 2, "desc": "Nguồn cung nguyên liệu sữa tươi, đường, dầu cọ dồi dào trên thị trường thế giới."},
            "buyer_power": {"score": 3, "desc": "Người tiêu dùng có lòng trung thành cao với các thương hiệu quốc dân lâu năm (Vinamilk, Chinsu)."},
            "substitution_threat": {"score": 2, "desc": "Sản phẩm thực phẩm thay thế đa dạng nhưng thói quen ẩm thực có tính bền vững cao."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản hệ thống phân phối hàng trăm nghìn điểm bán lẻ trên toàn quốc."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền & P/E Hàng tiêu dùng",
            "badge": "Khuyên dùng: DCF & P/E",
            "rationale": "Doanh nghiệp thực phẩm FMCG có dòng tiền tiền mặt thặng dư đều đặn và ROE vượt trội; mô hình DCF và P/E là phương pháp chuẩn xác.",
            "priority_tab": "dcf"
        }
    },

    # 17. Dệt may & Da giày
    "TEXTILES_FOOTWEAR": {
        "sector_name": "Dệt may & Da giày",
        "cycle": "Phục hồi Đơn hàng Xuất khẩu Mỹ & EU kèm Tiêu chuẩn Xanh hóa ESG",
        "sector_kpi_columns": [
            {"field": "order_backlog_bil", "label": "Đơn hàng (tỷ VND)", "unit": "tỷ VND", "color": "amber"},
            {"field": "export_ratio_percent", "label": "Tỷ lệ XK (%)", "unit": "%", "color": "sky"},
            {"field": "gross_margin", "label": "Biên gộp (%)", "unit": "%", "color": "emerald"}
        ],
        "peers": [
            {"ticker": "TNG", "name": "Đầu tư và Thương mại TNG", "market_cap_bil": 3100.0, "pe": 10.5, "pb": 1.45, "roe": 16.5, "roa": 6.5, "net_margin": 4.5, "debt_to_equity": 0.95, "revenue_growth_yoy": 14.5, "order_backlog_bil": 7500.0, "export_ratio_percent": 95.0, "gross_margin": 14.8},
            {"ticker": "VGT", "name": "Tập đoàn Dệt May Việt Nam", "market_cap_bil": 6800.0, "pe": 14.5, "pb": 0.85, "roe": 6.5, "roa": 2.8, "net_margin": 3.2, "debt_to_equity": 0.85, "revenue_growth_yoy": 8.0, "order_backlog_bil": 16500.0, "export_ratio_percent": 88.0, "gross_margin": 10.5},
            {"ticker": "MSH", "name": "May Sông Hồng", "market_cap_bil": 3600.0, "pe": 9.5, "pb": 1.75, "roe": 20.5, "roa": 10.5, "net_margin": 7.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 15.0, "order_backlog_bil": 4800.0, "export_ratio_percent": 92.0, "gross_margin": 16.5},
            {"ticker": "STK", "name": "Sợi Thế Kỷ", "market_cap_bil": 2800.0, "pe": 18.5, "pb": 1.55, "roe": 8.5, "roa": 4.2, "net_margin": 5.2, "debt_to_equity": 0.75, "revenue_growth_yoy": 12.0, "order_backlog_bil": 2200.0, "export_ratio_percent": 65.0, "gross_margin": 13.5},
            {"ticker": "TCM", "name": "Dệt may - Đầu tư Thành Công", "market_cap_bil": 4500.0, "pe": 15.2, "pb": 1.95, "roe": 13.5, "roa": 6.8, "net_margin": 6.2, "debt_to_equity": 0.55, "revenue_growth_yoy": 11.5, "order_backlog_bil": 3800.0, "export_ratio_percent": 85.0, "gross_margin": 15.2},
            {"ticker": "GIL", "name": "Sản xuất Kinh doanh XNK Bình Thạnh", "market_cap_bil": 2100.0, "pe": 16.0, "pb": 0.85, "roe": 5.5, "roa": 2.8, "net_margin": 4.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 9.0, "order_backlog_bil": 1800.0, "export_ratio_percent": 80.0, "gross_margin": 12.0}
        ],
        "catalysts": [
            "Hồi phục nhu cầu đơn hàng xuất khẩu và tái tích lũy hàng tồn kho tại các thị trường bán lẻ chủ lực Mỹ, EU, Nhật Bản.",
            "Lợi thế cạnh tranh từ các hiệp định thương mại tự do EVFTA, CPTPP với thuế quan ưu đãi 0%.",
            "Đẩy mạnh chuyển đổi phương thức sản xuất FOB, ODM nâng cao biên lợi nhuận thay thế gia công CMT truyền thống."
        ],
        "risks": [
            "Cạnh tranh gay gắt về đơn giá đơn hàng với các đối thủ Bangladesh, Ấn Độ, Indonesia.",
            "Yêu cầu khắt khe về chứng chỉ xanh hóa nhà máy, tiết kiệm năng lượng và truy xuất nguồn gốc sợi bông."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh gay gắt về đơn giá đơn hàng và thời gian giao hàng (Lead Time)."},
            "supplier_power": {"score": 3, "desc": "Chi phí bông, sợi và điện năng biến động theo thị trường toàn cầu."},
            "buyer_power": {"score": 4, "desc": "Các nhãn hàng thời trang quốc tế lớn (Nike, Adidas, Decathlon) có vị thế ép giá."},
            "substitution_threat": {"score": 1, "desc": "Quần áo dệt may là sản phẩm thiết yếu toàn cầu."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản xây dựng tệp khách hàng quốc tế và đáp ứng tiêu chuẩn kiểm định lao động ESG."}
        },
        "recommended_valuation": {
            "method": "P/E & P/B Theo Đơn hàng Xuất khẩu",
            "badge": "Khuyên dùng: P/E & P/B",
            "rationale": "Doanh nghiệp dệt may phụ thuộc vào lượng đơn hàng xuất khẩu và biên lãi gia công; P/E kết hợp P/B phản ánh sát giá trị doanh nghiệp.",
            "priority_tab": "pe"
        }
    },

    # 18. Công nghệ Thông tin & AI
    "IT_SOFTWARE": {
        "sector_name": "Công nghệ Thông tin & AI",
        "cycle": "Làn sóng Chuyển đổi Số Toàn cầu, Điện toán Đám mây & Đột phá Trí tuệ Nhân tạo (AI)",
        "sector_kpi_columns": [
            {"field": "dx_revenue_growth", "label": "Tăng trưởng CĐS (%)", "unit": "%", "color": "emerald"},
            {"field": "global_contracts_mil", "label": "Hợp đồng ($m)", "unit": "$m", "color": "sky"},
            {"field": "net_margin", "label": "Biên ròng (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "FPT", "name": "Tập đoàn FPT", "market_cap_bil": 185000.0, "pe": 24.5, "pb": 5.85, "roe": 26.5, "roa": 14.5, "net_margin": 15.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 20.5, "dx_revenue_growth": 32.5, "global_contracts_mil": 1250.0},
            {"ticker": "CMG", "name": "Tập đoàn Công nghệ CMC", "market_cap_bil": 8500.0, "pe": 18.5, "pb": 2.45, "roe": 14.5, "roa": 6.8, "net_margin": 7.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 15.0, "dx_revenue_growth": 22.0, "global_contracts_mil": 180.0},
            {"ticker": "ELC", "name": "Công nghệ Elcom", "market_cap_bil": 1850.0, "pe": 14.2, "pb": 1.85, "roe": 15.5, "roa": 8.5, "net_margin": 12.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 18.5, "dx_revenue_growth": 25.0, "global_contracts_mil": 45.0},
            {"ticker": "ITD", "name": "Công nghệ Tiên Phong", "market_cap_bil": 650.0, "pe": 12.5, "pb": 1.15, "roe": 9.5, "roa": 4.5, "net_margin": 5.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 10.0, "dx_revenue_growth": 15.0, "global_contracts_mil": 20.0},
            {"ticker": "SAM", "name": "SAM Holdings", "market_cap_bil": 2600.0, "pe": 18.5, "pb": 0.75, "roe": 4.5, "roa": 2.1, "net_margin": 3.2, "debt_to_equity": 0.65, "revenue_growth_yoy": 7.5, "dx_revenue_growth": 10.0, "global_contracts_mil": 15.0}
        ],
        "catalysts": [
            "Doanh số ký mới mảng xuất khẩu phần mềm toàn cầu vượt mốc 1 tỷ USD, duy trì tăng trưởng trên 25-30%/năm.",
            "Hợp tác chiến lược với NVIDIA mở rộng Trung tâm Dữ liệu AI Factory phục vụ đào tạo trí tuệ nhân tạo và thiết kế bán dẫn.",
            "Tỷ trọng doanh thu dịch vụ chuyển đổi số (Cloud, Big Data, AI) chiếm trên 45% tổng doanh thu CNTT với biên lợi nhuận cao."
        ],
        "risks": [
            "Biến động tỷ giá đồng Yên Nhật (JPY) và USD ảnh hưởng đến doanh thu quy đổi từ thị trường Nhật Bản và Mỹ.",
            "Cạnh tranh thu hút nhân tài kỹ sư phần mềm công nghệ cao đẩy chi phí tiền lương tăng."
        ],
        "forces": {
            "rivalry": {"score": 2, "desc": "Cạnh tranh quốc tế chủ yếu với các công ty CNTT Ấn Độ; doanh nghiệp Việt Nam có lợi thế chi phí và văn hóa."},
            "supplier_power": {"score": 2, "desc": "Nguồn nhân lực kỹ sư phần mềm trẻ và hợp tác sâu với các hãng công nghệ lớn (NVIDIA, Microsoft)."},
            "buyer_power": {"score": 2, "desc": "Khách hàng doanh nghiệp Fortune 500 có tính gắn kết hợp đồng dịch vụ nhiều năm."},
            "substitution_threat": {"score": 1, "desc": "Chuyển đổi số và hiện đại hóa hạ tầng IT là yêu cầu sinh tồn bắt buộc của mọi tổ chức."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản năng lực thực thi dự án quy mô lớn, chứng chỉ an ninh và danh tiếng thương hiệu."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền & P/E Tăng trưởng (PEG)",
            "badge": "Khuyên dùng: DCF & PEG",
            "rationale": "Doanh nghiệp công nghệ có tỷ suất sinh lời ROE vượt trội và tốc độ tăng trưởng lợi nhuận hai con số bền vững; DCF kết hợp PEG là tối ưu.",
            "priority_tab": "dcf"
        }
    },

    # 19. Viễn thông & Hạ tầng mạng
    "TELECOM_TOWERCO": {
        "sector_name": "Viễn thông & Hạ tầng mạng",
        "cycle": "Thương mại hóa Mạng 5G Toàn quốc & Xu hướng Chia sẻ Hạ tầng Trạm BTS TowerCo",
        "sector_kpi_columns": [
            {"field": "tower_bts_count", "label": "Trạm BTS (trạm)", "unit": "trạm", "color": "emerald"},
            {"field": "tenancy_ratio", "label": "Dùng chung (lần)", "unit": "x", "color": "sky"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "CTR", "name": "Viettel Construction", "market_cap_bil": 14500.0, "pe": 24.5, "pb": 5.20, "roe": 24.5, "roa": 7.5, "net_margin": 4.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 16.5, "tower_bts_count": 8500.0, "tenancy_ratio": 1.05, "ebitda_margin": 10.5},
            {"ticker": "VGI", "name": "Viettel Global", "market_cap_bil": 225000.0, "pe": 32.0, "pb": 5.85, "roe": 19.5, "roa": 9.5, "net_margin": 14.5, "debt_to_equity": 0.25, "revenue_growth_yoy": 22.0, "tower_bts_count": 28000.0, "tenancy_ratio": 1.02, "ebitda_margin": 38.5},
            {"ticker": "FOX", "name": "FPT Telecom", "market_cap_bil": 38000.0, "pe": 16.5, "pb": 3.85, "roe": 26.5, "roa": 11.5, "net_margin": 14.0, "debt_to_equity": 0.45, "revenue_growth_yoy": 10.5, "tower_bts_count": 0.0, "tenancy_ratio": 0.0, "ebitda_margin": 32.0},
            {"ticker": "TTN", "name": "Công nghệ Thông tin Viễn thông", "market_cap_bil": 680.0, "pe": 12.5, "pb": 1.25, "roe": 11.5, "roa": 5.8, "net_margin": 6.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 9.5, "tower_bts_count": 0.0, "tenancy_ratio": 0.0, "ebitda_margin": 14.0}
        ],
        "catalysts": [
            "Các nhà mạng lớn (Viettel, VinaPhone) triển khai mạng 5G toàn quốc thúc đẩy nhu cầu xây dựng và thuê trạm BTS tăng vọt.",
            "Chính sách khuyến khích dùng chung hạ tầng viễn thông giúp cải thiện hệ số dùng chung (Tenancy Ratio) và nới rộng biên EBITDA.",
            "Mảng dịch vụ vận hành khai thác (VHKT) và giải pháp năng lượng xanh (điện mặt trời mái nhà) mang lại dòng tiền tăng trưởng bền vững."
        ],
        "risks": [
            "Chi phí đầu tư Capex mua sắm thiết bị và phát triển trạm BTS ban đầu lớn.",
            "Rủi ro biến động tỷ giá tại các thị trường viễn thông quốc tế (châu Phi, Mỹ Latinh)."
        ],
        "forces": {
            "rivalry": {"score": 2, "desc": "CTR giữ vị thế số 1 tuyệt đối về quy mô trạm BTS TowerCo cho thuê tại Việt Nam."},
            "supplier_power": {"score": 2, "desc": "Thiết bị viễn thông và trụ thép trạm BTS nguồn cung dồi dào, kiểm soát chất lượng chặt chẽ."},
            "buyer_power": {"score": 3, "desc": "Khách hàng viễn thông lớn là các nhà mạng quốc gia (Viettel, Mobifone, VNPT)."},
            "substitution_threat": {"score": 1, "desc": "Hạ tầng trạm BTS là điều kiện tiên quyết không thể thay thế để phủ sóng 4G/5G."},
            "new_entrants_threat": {"score": 1, "desc": "Rào cản về kinh nghiệm thi công toàn quốc và đội ngũ kỹ thuật vận hành phủ khắp 63 tỉnh thành."}
        },
        "recommended_valuation": {
            "method": "EV/EBITDA & DCF Hạ tầng Viễn thông",
            "badge": "Khuyên dùng: EV/EBITDA",
            "rationale": "Mô hình TowerCo tạo dòng tiền cho thuê trạm dài hạn có tính chất dòng tiền đều đặn như tiện ích; EV/EBITDA là phương pháp tối ưu.",
            "priority_tab": "dcf"
        }
    },

    # 20. Dược phẩm & Y tế
    "PHARMA_HEALTHCARE": {
        "sector_name": "Dược phẩm & Y tế",
        "cycle": "Gia tăng Tiêu chuẩn EU-GMP & Đấu thầu Thuốc Kênh Bệnh viện (ETC)",
        "sector_kpi_columns": [
            {"field": "etc_hospital_ratio", "label": "Kênh ETC (%)", "unit": "%", "color": "emerald"},
            {"field": "gross_margin", "label": "Biên gộp (%)", "unit": "%", "color": "sky"},
            {"field": "eu_gmp_lines", "label": "Dây chuyền EU-GMP", "unit": "dây chuyền", "color": "amber"}
        ],
        "peers": [
            {"ticker": "DHG", "name": "Dược Hậu Giang", "market_cap_bil": 15500.0, "pe": 14.5, "pb": 3.10, "roe": 22.5, "roa": 17.5, "net_margin": 21.5, "debt_to_equity": 0.08, "revenue_growth_yoy": 9.5, "etc_hospital_ratio": 35.0, "gross_margin": 46.5, "eu_gmp_lines": 3.0},
            {"ticker": "IMP", "name": "Dược phẩm Imexpharm", "market_cap_bil": 5800.0, "pe": 16.5, "pb": 2.45, "roe": 16.5, "roa": 12.2, "net_margin": 14.8, "debt_to_equity": 0.15, "revenue_growth_yoy": 15.0, "etc_hospital_ratio": 62.0, "gross_margin": 42.0, "eu_gmp_lines": 11.0},
            {"ticker": "TRA", "name": "Traphaco", "market_cap_bil": 3800.0, "pe": 13.5, "pb": 2.20, "roe": 18.5, "roa": 13.5, "net_margin": 11.5, "debt_to_equity": 0.05, "revenue_growth_yoy": 8.0, "etc_hospital_ratio": 25.0, "gross_margin": 52.0, "eu_gmp_lines": 2.0},
            {"ticker": "DMC", "name": "Domesco", "market_cap_bil": 2200.0, "pe": 12.0, "pb": 1.65, "roe": 14.2, "roa": 9.5, "net_margin": 10.5, "debt_to_equity": 0.10, "revenue_growth_yoy": 10.5, "etc_hospital_ratio": 50.0, "gross_margin": 36.5, "eu_gmp_lines": 2.0},
            {"ticker": "DBD", "name": "Dược - Trang thiết bị Y tế Bình Định", "market_cap_bil": 3100.0, "pe": 12.5, "pb": 2.10, "roe": 18.0, "roa": 12.0, "net_margin": 16.5, "debt_to_equity": 0.12, "revenue_growth_yoy": 14.0, "etc_hospital_ratio": 58.0, "gross_margin": 48.0, "eu_gmp_lines": 2.0},
            {"ticker": "TNH", "name": "Bệnh viện Quốc tế Thái Nguyên", "market_cap_bil": 2800.0, "pe": 15.5, "pb": 1.85, "roe": 14.5, "roa": 8.5, "net_margin": 26.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 18.0, "etc_hospital_ratio": 0.0, "gross_margin": 45.0, "eu_gmp_lines": 0.0}
        ],
        "catalysts": [
            "Nâng cấp nhà máy đạt tiêu chuẩn EU-GMP giúp doanh nghiệp trúng thầu gói thuốc generic chất lượng cao Nhóm 1 & 2 kênh bệnh viện.",
            "Dân số Việt Nam bước vào giai đoạn già hóa và thu nhập gia tăng thúc đẩy chi tiêu thuốc bình quân trên đầu người.",
            "Cổ đông chiến lược ngoại (Taisho, SK Group) chuyển giao công nghệ sản xuất thuốc biệt dược và mở rộng xuất khẩu."
        ],
        "risks": [
            "Phụ thuộc nguồn nguyên liệu hoạt chất dược phẩm (API) nhập khẩu từ Trung Quốc và Ấn Độ.",
            "Áp lực đấu thầu thuốc tập trung siết chặt giá trúng thầu bảo hiểm y tế."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh phân khúc thuốc generic chất lượng cao và chuỗi phân phối nhà thuốc hiện đại."},
            "supplier_power": {"score": 4, "desc": "Phụ thuộc 80-90% nguồn nguyên liệu hoạt chất dược phẩm (API) nhập khẩu."},
            "buyer_power": {"score": 4, "desc": "Áp lực đấu thầu tập trung bảo hiểm y tế và kiểm soát giá bán lẻ thuốc."},
            "substitution_threat": {"score": 2, "desc": "Thực phẩm chức năng hỗ trợ điều trị cạnh tranh một phần danh mục thuốc bổ OTC."},
            "new_entrants_threat": {"score": 2, "desc": "Chi phí đầu tư nhà máy EU-GMP hàng trăm tỷ VND và thời gian thẩm định cấp phép kéo dài."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền & P/E Dược phẩm Phòng thủ",
            "badge": "Khuyên dùng: DCF & P/E",
            "rationale": "Doanh nghiệp dược phẩm có đặc tính phòng thủ cao, biên lợi nhuận ròng ổn định và dòng tiền mặt dồi dào; DCF và P/E là phương pháp tối ưu.",
            "priority_tab": "dcf"
        }
    },

    # 21. Khai khoáng & Tài nguyên
    "MINING_RESOURCES": {
        "sector_name": "Khai khoáng & Tài nguyên",
        "cycle": "Chu kỳ Giá Hàng hóa Kim loại Toàn cầu & Nhu cầu Than Nhiệt điện Nội địa",
        "sector_kpi_columns": [
            {"field": "reserve_volume_mton", "label": "Trữ lượng (tr.tấn)", "unit": "tr.tấn", "color": "emerald"},
            {"field": "net_profit_growth_yoy", "label": "Tăng trưởng LN (%)", "unit": "%", "color": "sky"},
            {"field": "ebitda_margin", "label": "EBITDA (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "KSV", "name": "Tổng Công ty Khoáng sản TKV", "market_cap_bil": 9500.0, "pe": 12.5, "pb": 2.10, "roe": 18.5, "roa": 8.5, "net_margin": 11.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 15.0, "reserve_volume_mton": 45.0, "ebitda_margin": 24.5},
            {"ticker": "MSR", "name": "Masan High-Tech Materials", "market_cap_bil": 16500.0, "pe": 28.0, "pb": 1.25, "roe": 5.2, "roa": 1.8, "net_margin": 2.5, "debt_to_equity": 1.65, "revenue_growth_yoy": 10.5, "reserve_volume_mton": 85.0, "ebitda_margin": 22.0},
            {"ticker": "NBC", "name": "Than Nông Sơn - TKV", "market_cap_bil": 680.0, "pe": 6.5, "pb": 0.95, "roe": 16.5, "roa": 5.8, "net_margin": 3.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 8.5, "reserve_volume_mton": 15.0, "ebitda_margin": 12.5},
            {"ticker": "CST", "name": "Than Cao Sơn - TKV", "market_cap_bil": 1850.0, "pe": 5.8, "pb": 1.15, "roe": 22.5, "roa": 8.5, "net_margin": 5.2, "debt_to_equity": 0.55, "revenue_growth_yoy": 11.5, "reserve_volume_mton": 28.0, "ebitda_margin": 14.0},
            {"ticker": "TDN", "name": "Than Đèo Nai - TKV", "market_cap_bil": 1200.0, "pe": 6.2, "pb": 1.05, "roe": 19.5, "roa": 7.2, "net_margin": 4.5, "debt_to_equity": 0.65, "revenue_growth_yoy": 9.5, "reserve_volume_mton": 20.0, "ebitda_margin": 13.5}
        ],
        "catalysts": [
            "Giá vonfram, đồng và kim loại màu trên sàn London Metal Exchange (LME) duy trì đà phục hồi tích cực.",
            "Nhu cầu than nguyên khai cung cấp cho các nhà máy nhiệt điện than quốc gia tăng cao trong các tháng cao điểm nắng nóng.",
            "Sở hữu các mỏ khoáng sản quy mô lớn với thời hạn khai thác dài hạn tạo rào cản độc quyền tự nhiên."
        ],
        "risks": [
            "Thuế tài nguyên, phí bảo vệ môi trường và chi phí bóc phủ đất đá gia tăng.",
            "Điều kiện khai thác hầm lò ngày càng xuống sâu làm tăng chi phí an toàn lao động và giá thành khai thác."
        ],
        "forces": {
            "rivalry": {"score": 2, "desc": "Tập đoàn Công nghiệp Than - Khoáng sản Việt Nam (TKV) điều phối phần lớn hạn ngạch khai thác."},
            "supplier_power": {"score": 2, "desc": "Máy móc khai khoáng và vật liệu nổ công nghiệp nguồn cung ổn định."},
            "buyer_power": {"score": 3, "desc": "EVN và các nhà máy nhiệt điện than là khách hàng tiêu thụ than chủ lực."},
            "substitution_threat": {"score": 2, "desc": "Năng lượng tái tạo đang tăng tỷ trọng nhưng nhiệt điện than vẫn giữ vai trò phụ tải nền."},
            "new_entrants_threat": {"score": 1, "desc": "Giấy phép khai thác mỏ mới được Chính phủ quản lý chặt chẽ theo Luật Khoáng sản."}
        },
        "recommended_valuation": {
            "method": "P/E & P/B Theo Trữ lượng Mỏ",
            "badge": "Khuyên dùng: P/E & P/B",
            "rationale": "Giá trị công ty khai khoáng gắn liền với trữ lượng mỏ được cấp phép và giá bán hàng hóa thực tế; định giá P/E kết hợp P/B là chuẩn xác.",
            "priority_tab": "pe"
        }
    },

    # 22. Cấp thoát nước & Môi trường Đô thị
    "WATER_ENVIRONMENT": {
        "sector_name": "Nước sạch & Môi trường",
        "cycle": "Lộ trình Tăng giá Nước Sạch Đô thị & Mở rộng Mạng lưới Cấp nước Vùng Công nghiệp",
        "sector_kpi_columns": [
            {"field": "water_supply_capacity_m3", "label": "Công suất (m³/ngày)", "unit": "m³/ngày", "color": "emerald"},
            {"field": "water_loss_ratio", "label": "Thất thoát nước (%)", "unit": "%", "color": "rose"},
            {"field": "net_margin", "label": "Biên ròng (%)", "unit": "%", "color": "sky"}
        ],
        "peers": [
            {"ticker": "BWE", "name": "Nước - Môi trường Bình Dương (Biwase)", "market_cap_bil": 10500.0, "pe": 12.5, "pb": 1.65, "roe": 15.5, "roa": 7.2, "net_margin": 18.5, "debt_to_equity": 0.85, "revenue_growth_yoy": 14.5, "water_supply_capacity_m3": 760000.0, "water_loss_ratio": 5.2, "net_margin_val": 18.5},
            {"ticker": "TDM", "name": "Nước Thủ Dầu Một", "market_cap_bil": 4800.0, "pe": 14.2, "pb": 1.85, "roe": 14.2, "roa": 10.5, "net_margin": 45.0, "debt_to_equity": 0.15, "revenue_growth_yoy": 11.5, "water_supply_capacity_m3": 280000.0, "water_loss_ratio": 3.8, "net_margin_val": 45.0},
            {"ticker": "DNW", "name": "Cấp nước Đồng Nai", "market_cap_bil": 3500.0, "pe": 10.5, "pb": 1.35, "roe": 13.5, "roa": 8.5, "net_margin": 16.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 9.5, "water_supply_capacity_m3": 450000.0, "water_loss_ratio": 7.5, "net_margin_val": 16.5},
            {"ticker": "VCW", "name": "Nước sạch Sông Đà (Viwasupco)", "market_cap_bil": 3800.0, "pe": 13.5, "pb": 1.95, "roe": 15.8, "roa": 9.2, "net_margin": 32.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 8.5, "water_supply_capacity_m3": 300000.0, "water_loss_ratio": 4.5, "net_margin_val": 32.5}
        ],
        "catalysts": [
            "UBND các tỉnh ban hành lộ trình tăng giá bán nước sạch sinh hoạt và công nghiệp 5-8%/năm.",
            "Nhu cầu cấp nước sạch tăng trưởng mạnh mẽ song hành cùng tốc độ đô thị hóa và mở rộng các KCN lớn.",
            "Mảng xử lý rác thải và phát điện từ rác (Waste-to-Energy) mở ra nguồn thu thặng dư biên lợi nhuận cao cho Biwase."
        ],
        "risks": [
            "Rủi ro ô nhiễm nguồn nước mặt tại các lưu vực sông cấp nước thô.",
            "Quy trình phê duyệt điều chỉnh giá nước sạch sinh hoạt phụ thuộc vào quyết định của cơ quan nhà nước."
        ],
        "forces": {
            "rivalry": {"score": 1, "desc": "Doanh nghiệp cấp nước có tính độc quyền địa bàn tự nhiên tuyệt đối theo phân vùng cấp phép."},
            "supplier_power": {"score": 2, "desc": "Nguồn nước thô từ các hồ tự nhiên và sông lớn có trữ lượng dồi dào."},
            "buyer_power": {"score": 1, "desc": "Người dân và doanh nghiệp công nghiệp bắt buộc phải đấu nối mạng lưới nước sạch duy nhất."},
            "substitution_threat": {"score": 1, "desc": "Nước sạch đô thị là nhu cầu sinh hoạt và sản xuất thiết yếu không thể thay thế."},
            "new_entrants_threat": {"score": 1, "desc": "Mạng lưới đường ống cấp nước ngầm và nhà máy xử lý là rào cản độc quyền tuyệt đối."}
        },
        "recommended_valuation": {
            "method": "DCF Dòng tiền & Tỷ suất Cổ tức Ổn định",
            "badge": "Khuyên dùng: DCF & Cổ tức",
            "rationale": "Cấp nước là ngành độc quyền tự nhiên với dòng tiền kinh doanh tiền mặt cực kỳ bền vững; phương pháp DCF và tỷ suất cổ tức là tối ưu nhất.",
            "priority_tab": "dcf"
        }
    },

    # 23. Tập đoàn Đa ngành
    "HOLDING_CONGLOMERATE": {
        "sector_name": "Doanh nghiệp niêm yết",
        "cycle": "Tái Cấu trúc Danh mục Đầu tư & Tối ưu Hóa Hiệu quả Hoạt động Tập đoàn",
        "sector_kpi_columns": [
            {"field": "net_profit_growth_yoy", "label": "Tăng trưởng LN (%)", "unit": "%", "color": "emerald"},
            {"field": "revenue_growth_yoy", "label": "Tăng trưởng DT (%)", "unit": "%", "color": "sky"},
            {"field": "price_change_ytd", "label": "Hiệu suất YTD (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "VIC", "name": "Tập đoàn Vingroup", "market_cap_bil": 165000.0, "pe": 28.5, "pb": 1.25, "roe": 4.5, "roa": 1.2, "net_margin": 2.5, "debt_to_equity": 2.15, "revenue_growth_yoy": 25.0},
            {"ticker": "GEX", "name": "Tập đoàn GELEX", "market_cap_bil": 18500.0, "pe": 13.5, "pb": 1.15, "roe": 10.5, "roa": 4.2, "net_margin": 6.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 15.0},
            {"ticker": "REE", "name": "Cơ Điện Lạnh (REE)", "market_cap_bil": 30500.0, "pe": 11.8, "pb": 1.45, "roe": 14.5, "roa": 8.5, "net_margin": 28.5, "debt_to_equity": 0.45, "revenue_growth_yoy": 14.0},
            {"ticker": "BCG", "name": "Bamboo Capital", "market_cap_bil": 4500.0, "pe": 15.0, "pb": 0.65, "roe": 5.2, "roa": 1.8, "net_margin": 4.5, "debt_to_equity": 1.85, "revenue_growth_yoy": 12.0},
            {"ticker": "PAN", "name": "Tập đoàn PAN", "market_cap_bil": 4500.0, "pe": 11.5, "pb": 0.95, "roe": 11.2, "roa": 4.6, "net_margin": 5.8, "debt_to_equity": 0.85, "revenue_growth_yoy": 12.0}
        ],
        "catalysts": [
            "Chiến lược tái cấu trúc danh mục đầu tư, thoái vốn khỏi các mảng kém hiệu quả và tập trung vào các trụ cột cốt lõi.",
            "Tận dụng lợi thế quy mô tập đoàn để tối ưu hóa chi phí vốn vay và quản trị dòng tiền thặng dư.",
            "Hợp tác với các đối tác chiến lược quốc tế thúc đẩy chuyển giao công nghệ và quản trị chuyên nghiệp."
        ],
        "risks": [
            "Rủi ro chiết khấu tập đoàn (Conglomerate Discount) do sự phức tạp trong quản trị đa ngành.",
            "Rủi ro đòn bẩy tài chính hợp nhất từ các công ty con và dự án đầu tư quy mô lớn."
        ],
        "forces": {
            "rivalry": {"score": 3, "desc": "Cạnh tranh tại từng phân khúc kinh doanh cụ thể của các công ty con thành viên."},
            "supplier_power": {"score": 3, "desc": "Đa dạng hóa nhà cung ứng theo từng ngành nghề kinh doanh độc lập."},
            "buyer_power": {"score": 3, "desc": "Tập khách hàng đa dạng cả bán buôn lẫn bán lẻ."},
            "substitution_threat": {"score": 2, "desc": "Mô hình đa ngành giúp phân tán rủi ro khi một số phân khúc gặp khó khăn."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản quy mô vốn hàng chục nghìn tỷ đồng và hệ sinh thái đa lĩnh vực."}
        },
        "recommended_valuation": {
            "method": "SOTP (Sum-of-the-Parts) & P/B",
            "badge": "Khuyên dùng: SOTP & P/B",
            "rationale": "Tập đoàn đa ngành sở hữu nhiều mảng kinh doanh với đặc tính dòng tiền khác nhau; phương pháp định giá từng phần SOTP là chuẩn mực nhất.",
            "priority_tab": "pb"
        }
    },

    # 23. Nông nghiệp & Thủy sản
    "AGRICULTURE_SEAFOOD": {
        "sector_name": "Nông nghiệp & Thủy sản",
        "cycle": "Chu kỳ Phục hồi Xuất khẩu Sang Mỹ/EU/Trung Quốc & Tự chủ Vùng nuôi 3F",
        "sector_kpi_columns": [
            {"field": "export_turnover_mil", "label": "Kim ngạch XK ($m)", "unit": "$m", "color": "emerald"},
            {"field": "gross_margin", "label": "Biên gộp (%)", "unit": "%", "color": "sky"},
            {"field": "raw_material_self_sufficiency", "label": "Tự chủ vùng nuôi (%)", "unit": "%", "color": "amber"}
        ],
        "peers": [
            {"ticker": "VHC", "name": "Vĩnh Hoàn (Nữ hoàng Cá tra)", "market_cap_bil": 14200.0, "pe": 12.0, "pb": 1.45, "roe": 14.5, "roa": 9.8, "net_margin": 9.5, "debt_to_equity": 0.35, "revenue_growth_yoy": 15.0, "export_turnover_mil": 450.0, "gross_margin": 18.5, "raw_material_self_sufficiency": 85.0},
            {"ticker": "ANV", "name": "Nam Việt (Navico Cá tra)", "market_cap_bil": 4500.0, "pe": 14.5, "pb": 0.95, "roe": 8.5, "roa": 4.5, "net_margin": 6.5, "debt_to_equity": 0.85, "revenue_growth_yoy": 18.0, "export_turnover_mil": 180.0, "gross_margin": 16.5, "raw_material_self_sufficiency": 100.0},
            {"ticker": "FMC", "name": "Sao Ta (Tôm xuất khẩu)", "market_cap_bil": 3800.0, "pe": 10.5, "pb": 1.35, "roe": 14.2, "roa": 8.5, "net_margin": 6.8, "debt_to_equity": 0.45, "revenue_growth_yoy": 12.0, "export_turnover_mil": 220.0, "gross_margin": 12.5, "raw_material_self_sufficiency": 40.0},
            {"ticker": "MPC", "name": "Thủy sản Minh Phú (Vua tôm)", "market_cap_bil": 6500.0, "pe": 16.0, "pb": 1.15, "roe": 7.5, "roa": 3.8, "net_margin": 4.2, "debt_to_equity": 0.95, "revenue_growth_yoy": 14.0, "export_turnover_mil": 550.0, "gross_margin": 10.5, "raw_material_self_sufficiency": 35.0},
            {"ticker": "DBC", "name": "DABACO (Chăn nuôi 3F & Vaccine)", "market_cap_bil": 9800.0, "pe": 11.2, "pb": 1.45, "roe": 15.2, "roa": 6.8, "net_margin": 6.5, "debt_to_equity": 0.95, "revenue_growth_yoy": 16.0, "export_turnover_mil": 50.0, "gross_margin": 14.8, "raw_material_self_sufficiency": 90.0},
            {"ticker": "BAF", "name": "Nông nghiệp BAF (Heo ăn chay)", "market_cap_bil": 3800.0, "pe": 13.5, "pb": 1.30, "roe": 11.5, "roa": 4.8, "net_margin": 5.5, "debt_to_equity": 1.15, "revenue_growth_yoy": 22.0, "export_turnover_mil": 20.0, "gross_margin": 12.0, "raw_material_self_sufficiency": 80.0},
            {"ticker": "HAG", "name": "Hoàng Anh Gia Lai", "market_cap_bil": 12500.0, "pe": 10.8, "pb": 1.65, "roe": 18.5, "roa": 7.5, "net_margin": 14.5, "debt_to_equity": 1.25, "revenue_growth_yoy": 20.0, "export_turnover_mil": 120.0, "gross_margin": 26.5, "raw_material_self_sufficiency": 95.0}
        ],
        "catalysts": [
            "Nhu cầu nhập khẩu cá tra và tôm phục hồi mạnh mẽ tại các thị trường trọng điểm Mỹ, Châu Âu và Trung Quốc.",
            "Bộ Thương mại Hoa Kỳ duy trì mức thuế chống bán phá giá (POR) ưu đãi 0 USD/kg cho các doanh nghiệp xuất khẩu lớn.",
            "Chuỗi giá trị khép kín 3F (Feed - Farm - Food) giúp tự chủ con giống, thức ăn thủy sản và ổn định giá vốn sản xuất.",
            "Chiến lược đẩy mạnh các sản phẩm chế biến sâu có biên lợi nhuận cao như Collagen, Gelatin và phụ phẩm giá trị gia tăng."
        ],
        "risks": [
            "Biến động giá nguyên liệu thức ăn chăn nuôi (ngô, khô đậu tương) và cước vận tải biển quốc tế.",
            "Rủi ro dịch bệnh trong nuôi trồng thủy sản và rào cản kỹ thuật vệ sinh an toàn thực phẩm từ thị trường nhập khẩu."
        ],
        "forces": {
            "rivalry": {"score": 4, "desc": "Cạnh tranh gay gắt về giá bán và hạn ngạch xuất khẩu với các nước như Ecuador, Ấn Độ, Indonesia."},
            "supplier_power": {"score": 3, "desc": "Doanh nghiệp tự chủ 100% vùng nuôi (như ANV) có lợi thế vượt trội so với thu mua ngoài."},
            "buyer_power": {"score": 4, "desc": "Nhà nhập khẩu lớn tại Mỹ/EU có quyền đàm phán cao về tiêu chuẩn chứng nhận quốc tế (ASC, BAP)."},
            "substitution_threat": {"score": 2, "desc": "Cá tra và tôm là nguồn đạm dinh dưỡng phổ biến với mức giá rất cạnh tranh toàn cầu."},
            "new_entrants_threat": {"score": 2, "desc": "Rào cản về vùng nuôi đạt chuẩn quốc tế, giấy phép xuất khẩu sang Mỹ và nhà máy chế biến sâu."}
        },
        "recommended_valuation": {
            "method": "DCF Chu kỳ & P/E Xuất khẩu",
            "badge": "Khuyên dùng: DCF & P/E",
            "rationale": "Doanh nghiệp thủy sản mang tính chu kỳ cao; định giá dựa trên dòng tiền DCF qua chu kỳ và P/E dự phóng khi ngành bước vào pha tăng trưởng.",
            "priority_tab": "dcf"
        }
    }
}

def get_universal_sector_peer_config(model_key: str, ticker: str = "") -> Dict[str, Any]:
    """Lấy cấu hình đối thủ cùng ngành và khuyến nghị định giá theo mã mô hình 23 ngành."""
    key = (model_key or "").upper().strip()
    if key in UNIVERSAL_SECTOR_PEERS_CONFIG:
        return UNIVERSAL_SECTOR_PEERS_CONFIG[key]
    return UNIVERSAL_SECTOR_PEERS_CONFIG.get("HOLDING_CONGLOMERATE", {})
