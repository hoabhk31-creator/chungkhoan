# -*- coding: utf-8 -*-
"""
pdf_generator.py - Bộ tạo Báo cáo Phân tích Định giá Doanh nghiệp chuẩn PDF
Chuyên nghiệp dành cho các Công ty Chứng khoán (SSI, HSC, Vietcap, VNDirect, VCBS...)
Hỗ trợ đầy đủ tiếng Việt Unicode, bố cục chuẩn báo cáo CTCK chuyên sâu.
"""

import os
import re
import base64
import tempfile
from datetime import datetime
from typing import Optional
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace
from engine import is_report_expired


def get_unicode_font_paths():
    """
    Tìm kiếm đường dẫn font Unicode hỗ trợ tiếng Việt trên mọi hệ điều hành (Windows, Linux, Docker, Render).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_fonts = os.path.join(base_dir, "fonts")

    # 1. Ưu tiên font trong thư mục fonts/ của dự án
    local_reg = os.path.join(local_fonts, "arial.ttf")
    local_bold = os.path.join(local_fonts, "arialbd.ttf")
    local_italic = os.path.join(local_fonts, "ariali.ttf")
    if os.path.exists(local_reg) and os.path.exists(local_bold):
        return local_reg, local_bold, (local_italic if os.path.exists(local_italic) else local_reg)

    # 2. Kiểm tra Windows Fonts
    win_fonts = os.environ.get("WINDIR", r"C:\Windows") + r"\Fonts"
    win_reg = os.path.join(win_fonts, "arial.ttf")
    win_bold = os.path.join(win_fonts, "arialbd.ttf")
    win_italic = os.path.join(win_fonts, "ariali.ttf")
    if os.path.exists(win_reg) and os.path.exists(win_bold):
        return win_reg, win_bold, (win_italic if os.path.exists(win_italic) else win_reg)

    # 3. Kiểm tra Linux / Ubuntu / Debian / Render Fonts
    linux_candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
        ("/usr/share/fonts/truetype/freefont/FreeSans.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf"),
    ]
    for reg, bold, it in linux_candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold, (it if os.path.exists(it) else reg)

    return None, None, None


def setup_pdf_unicode_fonts(pdf: FPDF):
    """Đăng ký font ArialVN hỗ trợ tiếng Việt Unicode cho file PDF."""
    reg, bold, italic = get_unicode_font_paths()
    if reg and bold:
        try:
            pdf.add_font("ArialVN", "", reg)
            pdf.add_font("ArialVN", "B", bold)
            pdf.add_font("ArialVN", "I", italic or reg)
            pdf.font_family_regular = "ArialVN"
            pdf.font_family_bold = "ArialVN"
            pdf.font_family_italic = "ArialVN"
            return
        except Exception as e:
            print("Error registering unicode font:", e)
    pdf.font_family_regular = "helvetica"
    pdf.font_family_bold = "helvetica"
    pdf.font_family_italic = "helvetica"


class InstitutionalReportPDF(FPDF):
    def __init__(self, institution_name: str, ticker: str, company_name: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        self.institution_name = institution_name
        self.ticker = ticker.upper()
        self.company_name = company_name

        setup_pdf_unicode_fonts(self)

    def header(self):
        # Header ở đầu trang
        self.set_fill_color(15, 23, 42)  # #0F172A Slate 900
        self.rect(0, 0, 210, 22, "F")

        # Tên CTCK & Loại báo cáo
        self.set_xy(14, 4)
        self.set_text_color(255, 255, 255)
        self.set_font(self.font_family_bold, "B", 13)
        self.cell(100, 7, f"{self.institution_name.upper()} RESEARCH", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_bold, "B", 10)
        self.set_text_color(56, 189, 248)  # Sky 400
        self.cell(82, 7, "BÁO CÁO PHÂN TÍCH & ĐỊNH GIÁ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.set_xy(14, 11)
        self.set_font(self.font_family_regular, "", 8)
        self.set_text_color(203, 213, 225)  # Slate 300
        self.cell(100, 6, f"Mã CK: {self.ticker} - {self.company_name}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.cell(82, 6, f"Ngày phát hành: {datetime.now().strftime('%d/%m/%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.ln(6)

    def footer(self):
        # Footer ở chân trang
        self.set_y(-14)
        self.set_draw_color(226, 232, 240)
        self.line(14, self.get_y(), 196, self.get_y())
        self.set_y(-11)
        self.set_font(self.font_family_regular, "I", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(120, 6, f"{self.institution_name} © Bản quyền báo cáo phân tích thuộc khối Nghiên cứu & Phân tích", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(62, 6, f"Trang {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")


def generate_ctck_report_pdf(
    ticker: str,
    company_name: str,
    sector: str,
    report: dict,
    consensus: dict = None,
) -> bytes:
    report = to_dict_safe(report)
    consensus = to_dict_safe(consensus)
    institution = report.get("institution", "CTCK")
    target_price = report.get("target_price", 0)
    current_price = report.get("current_price", 0)
    upside_pct = report.get("upside_pct", 0.0)
    recommendation = report.get("recommendation", "MUA")
    report_date = report.get("date", datetime.now().strftime("%d/%m/%Y"))
    catalysts = report.get("catalysts", "Triển vọng kinh doanh khả quan nhờ mở rộng công suất và nhu cầu thị trường hồi phục mạnh mẽ.")
    risks = report.get("risks", "Biến động chi phí nguyên vật liệu đầu vào và rủi ro tỷ giá.")
    
    pdf = InstitutionalReportPDF(institution, ticker, company_name)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- KHỐI TIÊU ĐỀ CHÍNH & KHUYẾN NGHỊ ---
    pdf.set_xy(14, 26)
    
    # Tiêu đề báo cáo
    pdf.set_font(pdf.font_family_bold, "B", 15)
    pdf.set_text_color(30, 41, 59)  # Slate 800
    pdf.cell(182, 8, f"{ticker}: Triển vọng tăng trưởng & Khuyến nghị {recommendation}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # Phân ngành & Ngày báo cáo
    pdf.set_font(pdf.font_family_regular, "", 9)
    pdf.set_text_color(100, 116, 139)  # Slate 500
    pdf.cell(182, 5, f"Ngành: {sector or 'Công nghiệp'} | Cập nhật định giá: {report_date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(3)

    # Khung tóm tắt Khuyến nghị & Định giá (Hero Metrics Box)
    box_y = pdf.get_y()
    pdf.set_fill_color(248, 250, 252)  # Slate 50
    pdf.set_draw_color(203, 213, 225)  # Slate 300
    pdf.rect(14, box_y, 182, 26, "DF")

    # 1. Khuyến nghị
    pdf.set_xy(18, box_y + 3)
    pdf.set_font(pdf.font_family_bold, "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(42, 5, "KHUYẾN NGHỊ", new_x=XPos.LEFT, new_y=YPos.NEXT, align="L")
    
    if "MUA" in recommendation.upper() or "KHA QUAN" in recommendation.upper() or "TÍCH CỰC" in recommendation.upper():
        pdf.set_text_color(16, 185, 129)  # Green
    elif "BAN" in recommendation.upper() or "GIAM" in recommendation.upper() or "TIEU CUC" in recommendation.upper():
        pdf.set_text_color(239, 68, 68)  # Red
    else:
        pdf.set_text_color(245, 158, 11)  # Amber
    
    pdf.set_font(pdf.font_family_bold, "B", 13)
    pdf.cell(42, 7, recommendation.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # 2. Giá mục tiêu (Target Price)
    pdf.set_xy(62, box_y + 3)
    pdf.set_font(pdf.font_family_bold, "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(42, 5, "GIÁ MỤC TIÊU (VND)", new_x=XPos.LEFT, new_y=YPos.NEXT, align="L")
    pdf.set_font(pdf.font_family_bold, "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(42, 7, f"{target_price:,.0f}" if target_price else "N/A", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # 3. Thị giá hiện tại (Current Price)
    pdf.set_xy(106, box_y + 3)
    pdf.set_font(pdf.font_family_bold, "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(42, 5, "THỊ GIÁ HIỆN TẠI (VND)", new_x=XPos.LEFT, new_y=YPos.NEXT, align="L")
    pdf.set_font(pdf.font_family_bold, "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(42, 7, f"{current_price:,.0f}" if current_price else "N/A", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # 4. Biên tăng giá kỳ vọng (% Upside)
    pdf.set_xy(150, box_y + 3)
    pdf.set_font(pdf.font_family_bold, "B", 8)
    pdf.set_text_color(100, 116, 139)
    is_exceeded = (upside_pct is not None and upside_pct < 0)
    pdf.cell(42, 5, "ĐÃ VƯỢT (%)" if is_exceeded else "BIÊN KỲ VỌNG (%)", new_x=XPos.LEFT, new_y=YPos.NEXT, align="L")
    pdf.set_font(pdf.font_family_bold, "B", 13)
    
    if upside_pct is not None and upside_pct > 0:
        pdf.set_text_color(16, 185, 129)
        pdf.cell(42, 7, f"+{upside_pct:.1f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    elif upside_pct is not None and upside_pct < 0:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(42, 7, f"Vượt +{abs(upside_pct):.1f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    elif upside_pct is not None:
        pdf.set_text_color(100, 116, 139)
        pdf.cell(42, 7, "0.0%", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    else:
        pdf.set_text_color(100, 116, 139)
        pdf.cell(42, 7, "N/A", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    pdf.set_y(box_y + 30)

    # --- PHẦN 1: TỔNG QUAN LUẬN ĐIỂM ĐẦU TƯ (INVESTMENT THESIS) ---
    pdf.set_font(pdf.font_family_bold, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(182, 7, "1. TÓM TẮT LUẬN ĐIỂM ĐẦU TƯ & ĐỊNH GIÁ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_draw_color(37, 99, 235)  # Blue underline
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(2)

    if upside_pct is not None and upside_pct < 0:
        up_thesis = f"thị giá hiện tại ({current_price:,.0f} VND) đã vượt mức giá mục tiêu này (+{abs(upside_pct):.1f}%)"
    elif upside_pct is not None:
        up_thesis = f"tương ứng với biên tăng giá kỳ vọng là +{upside_pct:.1f}% so với thị giá hiện tại {current_price:,.0f} VND"
    else:
        up_thesis = "đang theo dõi sát diễn biến thị giá và cập nhật định giá mới nhất"

    thesis_text = (
        f"{institution} công bố báo cáo phân tích đối với {company_name} ({ticker}) "
        f"với khuyến nghị {recommendation} và mức giá mục tiêu {target_price:,.0f} VND/cổ phiếu, "
        f"{up_thesis}.\n"
        f"Doanh nghiệp duy trì vị thế dẫn đầu trong ngành với năng lực cạnh tranh vượt trội, cơ cấu tài chính lành mạnh "
        f"và tiềm năng gia tăng thị phần rõ rệt trong chu kỳ hồi phục kinh tế 2025 - 2026."
    )
    pdf.set_font(pdf.font_family_regular, "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(182, 5.5, thesis_text)
    pdf.ln(3)

    # --- PHẦN 2: BẢNG CHỈ TIÊU DỰ BÁO VÀ ĐỊNH GIÁ MULTIPLES ---
    pdf.set_font(pdf.font_family_bold, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(182, 7, "2. DỰ BÁO KẾT QUẢ KINH DOANH & ĐỊNH GIÁ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_draw_color(37, 99, 235)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(2)

    # Table Header
    col_w = [46, 34, 34, 34, 34]
    headers = ["Chỉ tiêu tài chính", "Năm 2023", "Năm 2024", "Dự phóng 2025F", "Dự phóng 2026F"]
    
    pdf.set_fill_color(241, 245, 249)  # Slate 100
    pdf.set_text_color(30, 41, 59)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6.5, h, border=1, fill=True, align="C" if i > 0 else "L")
    pdf.ln()

    # Table Rows
    pdf.set_font(pdf.font_family_regular, "", 8.5)
    data_rows = [
        ("Doanh thu thuần (Tỷ VND)", "Tăng trưởng ổn định", "+18.5% YoY", "+22.4% YoY", "+16.8% YoY"),
        ("LNST công ty mẹ (Tỷ VND)", "Đạt đáy chu kỳ", "Hồi phục mạnh", "+35.2% YoY", "+19.5% YoY"),
        ("Tỷ suất EPS (VND/cp)", "1,850", "2,480", "3,350", "4,010"),
        ("Tỷ suất ROE (%)", "12.4%", "15.8%", "19.2%", "20.5%"),
        ("Hệ số P/E dự phóng (x)", "15.2x", "12.6x", "9.8x", "8.2x"),
        ("Hệ số P/B dự phóng (x)", "1.7x", "1.5x", "1.3x", "1.1x"),
    ]

    for row_idx, row in enumerate(data_rows):
        fill = (row_idx % 2 == 1)
        pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[0], 6, row[0], border=1, fill=fill, align="L")
        for i in range(1, 5):
            pdf.cell(col_w[i], 6, row[i], border=1, fill=fill, align="C")
        pdf.ln()

    pdf.ln(3)

    # --- PHẦN 3: CÁC ĐỘNG LỰC TĂNG TRƯỞNG & YẾU TỐ KỲ VỌNG ---
    pdf.set_font(pdf.font_family_bold, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(182, 7, "3. ĐỘNG LỰC TĂNG TRƯỞNG & YẾU TỐ KỲ VỌNG CHÍNH (CATALYSTS)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_draw_color(37, 99, 235)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(2)

    cat_box_y = pdf.get_y()
    pdf.set_fill_color(240, 253, 244)  # Green 50
    pdf.set_draw_color(187, 247, 208)  # Green 200
    pdf.rect(14, cat_box_y, 182, 22, "DF")

    pdf.set_xy(17, cat_box_y + 2)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    pdf.set_text_color(22, 101, 52)  # Green 800
    pdf.cell(176, 4.5, f"Luận cứ kỳ vọng cốt lõi từ {institution}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(17, cat_box_y + 7)
    pdf.set_font(pdf.font_family_regular, "", 8.5)
    pdf.set_text_color(21, 128, 61)  # Green 700
    pdf.multi_cell(176, 4.5, catalysts)

    pdf.set_y(cat_box_y + 25)

    # --- PHẦN 4: RỦI RO ĐẦU TƯ TRỌNG YẾU (KEY INVESTMENT RISKS) ---
    pdf.set_font(pdf.font_family_bold, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(182, 7, "4. RỦI RO TRỌNG YẾU CẦN THEO DÕI (KEY RISKS)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_draw_color(239, 68, 68)  # Red underline
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(2)

    risk_box_y = pdf.get_y()
    pdf.set_fill_color(254, 242, 242)  # Red 50
    pdf.set_draw_color(254, 202, 202)  # Red 200
    pdf.rect(14, risk_box_y, 182, 20, "DF")

    pdf.set_xy(17, risk_box_y + 2)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    pdf.set_text_color(153, 27, 27)  # Red 800
    pdf.cell(176, 4.5, "Các nguy cơ & thách thức đối với định giá:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(17, risk_box_y + 7)
    pdf.set_font(pdf.font_family_regular, "", 8.5)
    pdf.set_text_color(185, 28, 28)  # Red 700
    pdf.multi_cell(176, 4.5, risks)

    pdf.set_y(risk_box_y + 23)

    # --- PHẦN 5: BẢNG TỔNG HỢP SO SÁNH CONSENSUS THỊ TRƯỜNG (NẾU CÓ) ---
    if consensus:
        avg_target = consensus.get("avg_target", 0)
        avg_upside = consensus.get("avg_upside_pct", 0.0)
        highest = consensus.get("highest_target", 0)
        lowest = consensus.get("lowest_target", 0)
        total_reports = consensus.get("total_reports", 0)

        pdf.set_font(pdf.font_family_bold, "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(182, 6, f"5. SO SÁNH VỚI ĐỊNH GIÁ TRUNG BÌNH THỊ TRƯỜNG (CONSENSUS: {total_reports} CTCK)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.set_draw_color(203, 213, 225)
        pdf.line(14, pdf.get_y(), 196, pdf.get_y())
        pdf.ln(2)

        pdf.set_font(pdf.font_family_regular, "", 8.5)
        pdf.set_text_color(71, 85, 105)
        up_cons_str = f"thị giá đã vượt kỳ vọng định giá TB (+{abs(avg_upside):.1f}%)" if avg_upside < 0 else f"Biên tăng kỳ vọng trung bình: +{avg_upside:.1f}%"
        cons_text = (
            f"Thị trường hiện có {total_reports} CTCK theo dõi định giá {ticker}. "
            f"Mức định giá trung bình đạt {avg_target:,.0f} VND ({up_cons_str}). "
            f"Định giá cao nhất: {highest:,.0f} VND | Thấp nhất: {lowest:,.0f} VND. "
            f"Định giá của {institution} ({target_price:,.0f} VND) nằm ở vị trí "
            f"{'cao hơn' if target_price >= avg_target else 'thận trọng hơn'} mức trung bình ngành."
        )
        pdf.multi_cell(182, 4.5, cons_text)
        pdf.ln(2)

    # --- KHUYẾN CÁO MIỄN TRỪ TRÁCH NHIỆM (DISCLAIMER) ---
    pdf.set_y(260)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(14, 260, 182, 22, "DF")

    pdf.set_xy(16, 261)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(178, 4, "KHUYẾN CÁO MIỄN TRỪ TRÁCH NHIỆM (DISCLAIMER)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(16, 265)
    pdf.set_font(pdf.font_family_regular, "I", 6.8)
    pdf.set_text_color(148, 163, 184)
    disclaimer_text = (
        f"Báo cáo phân tích này được biên soạn bởi Bộ phận Nghiên cứu & Phân tích của {institution}. "
        "Mọi thông tin, nhận định và dự báo trong báo cáo dựa trên nguồn dữ liệu đáng tin cậy tại thời điểm công bố. "
        "Báo cáo chỉ nhằm mục đích cung cấp thông tin tham khảo cho nhà đầu tư, không cấu thành bất kỳ lời mời chào mua "
        "hay bán chứng khoán nào. Nhà đầu tư chịu hoàn toàn trách nhiệm đối với quyết định đầu tư của mình."
    )
    pdf.multi_cell(178, 3.2, disclaimer_text)

    # Xuất ra bytes
    return bytes(pdf.output())


class MatrixTableLandscapePDF(FPDF):
    def __init__(self, ticker: str, company_name: str, sector: str):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.ticker = ticker.upper()
        self.company_name = company_name
        self.sector = sector

        setup_pdf_unicode_fonts(self)

    def header(self):
        self.set_fill_color(15, 23, 42)  # #0F172A Slate 900
        self.rect(0, 0, 297, 20, "F")

        # Mục 1: IERM TERMINAL // BẢNG ĐỐI CHIẾU TRỰC DIỆN ĐA TỔ CHỨC -> Cho nhỏ lại (font 8pt, màu xám xanh Slate 400)
        self.set_xy(12, 2.5)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.set_font(self.font_family_regular, "", 8)
        self.cell(160, 4.5, "IERM TERMINAL // BẢNG ĐỐI CHIẾU TRỰC DIỆN ĐA TỔ CHỨC", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_regular, "", 7.5)
        self.set_text_color(100, 116, 139)  # Slate 500
        self.cell(113, 4.5, "HORIZONTAL RECONCILIATION MATRIX", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        # Mục 2: Mã CK, Tên công ty, Ngành -> Phóng to ra (font 11.5pt đậm), màu nổi bật (Vàng sáng / Cyan nổi bật)
        self.set_xy(12, 8)
        self.set_font(self.font_family_bold, "B", 11.5)
        self.set_text_color(254, 240, 138)  # Yellow 200 / Gold highlight
        self.cell(185, 7, f"Mã CK: {self.ticker} - {self.company_name} | Ngành: {self.sector}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_regular, "", 8)
        self.set_text_color(203, 213, 225)
        self.cell(88, 7, f"Thời điểm xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y(), 285, self.get_y())
        self.set_y(-10)
        self.set_font(self.font_family_regular, "I", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(180, 5, "IERM Financial Intelligence Engine © Chuẩn hóa dữ liệu theo nguyên tắc Fact & Data First", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(93, 5, f"Trang {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")


def sanitize_bullet_item(it: str) -> str:
    """Làm sạch 1 điểm catalyst/risk, sửa lỗi font tiếng Việt, loại bỏ bảng BCTC, DCF, disclaimer và giữ trọn vẹn độ dài."""
    if not it or not isinstance(it, str):
        return ""
    it_clean = it.strip()
    # Loại bỏ ký tự lạ Private Use Area (E000-F8FF) để font không bị missing glyphs
    it_clean = re.sub(r'[\ue000-\uf8ff]', '', it_clean)
    it_clean = re.sub(r'^[•\-\*\>\➢\★\►\▪\▫\s\d\.\/\:]+', '', it_clean).strip()
    if not it_clean:
        return ""

    # Sửa lỗi font tiếng Việt bị dãn cách ký tự từ PDF
    try:
        from crawler import clean_vietnamese_pdf_spacing, is_table_or_valuation_or_disclaimer_dump
        it_clean = clean_vietnamese_pdf_spacing(it_clean)
        if is_table_or_valuation_or_disclaimer_dump(it_clean):
            return ""
    except Exception:
        pass

    disclaimer_markers = [
        "khuyến cáo", "miễn trừ", "không chịu trách nhiệm", "không mang tính chất mời chào",
        "chỉ nhằm mục đích", "email:", "tel:", "điện thoại:", "disclaimer", "chuyên viên phân tích",
        "thời gian lịch sử phát triển", "tiền thân là", "thành lập năm 19", "bản quyền thuộc",
        "điều khoản sử dụng", "sử dụng báo cáo này", "không phải là các lời chào mua"
    ]
    if any(m in it_clean.lower() for m in disclaimer_markers):
        return ""
    return it_clean


def sanitize_cell_bullet_text(items: list, max_items: int = 10, default_text: str = "") -> str:
    """Làm sạch danh sách bullets, lọc bỏ disclaimer và giữ trọn vẹn văn bản không giới hạn ký tự (tối đa max_items)."""
    if not items:
        return f"• {default_text}" if default_text else "—"

    clean_bullets = []
    for it in items:
        cleaned = sanitize_bullet_item(it)
        if cleaned:
            clean_bullets.append(f"• {cleaned}")
        if len(clean_bullets) >= max_items:
            break

    if not clean_bullets:
        return f"• {default_text}" if default_text else "—"
    return "\n".join(clean_bullets)


def to_dict_safe(obj):
    """Chuyển đổi an toàn Pydantic model hoặc object thành dict."""
    if obj is None:
        return {}
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict") and callable(obj.dict):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {}


def safe_float(v, default=None):
    """Chuyển đổi an toàn giá trị bất kỳ sang float."""
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    try:
        clean_v = str(v).replace("%", "").replace("+", "").replace(",", "").strip()
        return float(clean_v)
    except Exception:
        return default


def generate_matrix_table_pdf(report_data: dict) -> bytes:
    """
    Tạo file PDF A4 Landscape chuẩn mực, linh động, không bị đè chữ, không bị cắt dòng.
    Bao gồm:
    - Trang 1: Bảng Ma Trận Đối Chiếu Định Lượng Đa Tổ Chức & Dải Chiến Lược Đầu Tư.
    - Trang 2+: Bảng So Sánh Chi Tiết Toàn Văn Luận Điểm Tăng Trưởng (Catalysts) & Rủi Ro (Key Risks) Đa Tổ Chức.
    """
    report_data = to_dict_safe(report_data)
    ticker = report_data.get("ticker", "CP")
    company_name = report_data.get("company_name", f"Công ty Cổ phần {ticker}")
    sector = report_data.get("sector", "Doanh nghiệp niêm yết")
    if not sector or sector in ["Doanh nghiệp niêm yết", "Doanh nghiệp Niêm yết"]:
        try:
            from adaptive_growth_engine import classify_business_model
            from sector_peers_matrix import get_universal_sector_peer_config
            model_info = classify_business_model(ticker, company_name, sector)
            cfg = get_universal_sector_peer_config(model_info.get("model_key", ""), ticker)
            sector = cfg.get("sector_name") or model_info.get("badge_text") or sector
        except Exception:
            pass
    raw_reports = report_data.get("matrix_table", [])
    reports = [to_dict_safe(r) for r in raw_reports]
    if reports:
        from engine import get_report_date_sort_key
        reports = sorted(reports, key=get_report_date_sort_key, reverse=True)
    cs = to_dict_safe(report_data.get("consensus_summary", {}))

    pdf = MatrixTableLandscapePDF(ticker=ticker, company_name=company_name, sector=sector)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- TRANG 1: MA TRẬN ĐỊNH LƯỢNG (QUANTITATIVE RECONCILIATION) ---
    market_p = safe_float(cs.get("current_market_price"), 0.0) or 0.0
    mean_target = safe_float(cs.get("mean_target_price"), 0.0) or 0.0
    avg_upside = safe_float(cs.get("average_upside"), 0.0) or 0.0
    rating = str(cs.get("consensus_rating") or "MUA")

    # Executive Summary Strip
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, 22, 273, 12, "DF")

    pdf.set_xy(15, 23)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(50, 3.5, "THỊ GIÁ THAM CHIẾU", align="L")
    pdf.cell(55, 3.5, "ĐỊNH GIÁ TRUNG BÌNH (MEAN)", align="L")
    pdf.cell(50, 3.5, "KỲ VỌNG THỊ GIÁ VS ĐỊNH GIÁ" if avg_upside < 0 else "TIỀM NĂNG TĂNG GIÁ (UPSIDE)", align="L")
    pdf.cell(60, 3.5, "ĐỒNG THUẬN KHUYẾN NGHỊ", align="L")
    pdf.cell(50, 3.5, "MẪU BÁO CÁO CTCK", align="L")
    pdf.ln()

    pdf.set_x(15)
    pdf.set_font(pdf.font_family_bold, "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5.5, f"{market_p:,.0f} VND" if market_p > 0 else "—", align="L")
    pdf.set_text_color(2, 132, 199)
    if mean_target > 0:
        pdf.cell(55, 5.5, f"{mean_target:,.0f} VND", align="L")
        if avg_upside >= 0:
            pdf.set_text_color(16, 185, 129)
            pdf.cell(50, 5.5, f"+{avg_upside:.1f}%", align="L")
        else:
            pdf.set_text_color(239, 68, 68)
            pdf.cell(50, 5.5, f"Vượt +{abs(avg_upside):.1f}%", align="L")
    else:
        pdf.cell(55, 5.5, "—", align="L")
        pdf.set_text_color(245, 158, 11)
        pdf.cell(50, 5.5, "Cần theo dõi thêm", align="L")

    pdf.set_text_color(15, 23, 42)
    pdf.cell(60, 5.5, str(rating), align="L")
    pdf.cell(50, 5.5, f"{len(reports)} Báo cáo Tổ chức", align="L")
    pdf.ln(7)

    # Tiêu đề Phần 1
    pdf.set_font(pdf.font_family_bold, "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(273, 5, "PHẦN 1: BẢNG ĐỐI CHIẾU TRỰC DIỆN ĐỊNH LƯỢNG (QUANTITATIVE RECONCILIATION MATRIX)", align="L")
    pdf.ln(5)

    # Tính độ rộng cột Trang 1 (Nếu quá 7 báo cáo, hiển thị Top 7 mới nhất trên Trang 1 để cột không bị co rúm)
    display_reports_p1 = reports[:7] if len(reports) > 7 else reports
    num_reports = max(1, len(display_reports_p1))
    col_crit_w = 48
    col_cons_w = 45
    rem_w = 273 - col_crit_w - col_cons_w
    col_r_w = rem_w / num_reports
    col_widths_p1 = [col_crit_w] + [col_r_w] * num_reports + [col_cons_w]

    headings_style = FontFace(family="ArialVN", emphasis="B", size_pt=7.5, color=(255, 255, 255), fill_color=(15, 23, 42))

    pdf.set_font(pdf.font_family_regular, "", 7.2)
    pdf.set_text_color(15, 23, 42)

    with pdf.table(col_widths=col_widths_p1, headings_style=headings_style, line_height=4.6, padding=1.2, text_align="CENTER") as table:
        # Header
        h_row = table.row()
        h_row.cell("TIÊU CHÍ ĐỐI CHIẾU", align="L")
        for r in display_reports_p1:
            inst = str(r.get("institution") or "CTCK")
            date_str = str(r.get("report_date") or "")
            is_exp = r.get("is_expired", False) or is_report_expired(date_str)
            exp_sub = "\n(Quá 1 năm)" if is_exp else ""
            h_row.cell(f"{inst}\n({date_str}){exp_sub}", align="C")
        if not display_reports_p1:
            h_row.cell("DỮ LIỆU CTCK", align="C")
        h_row.cell("CONSENSUS\n& ĐỘ LỆCH", align="C")

        # Row 1: Khuyến nghị
        r1 = table.row()
        r1.cell("1. Khuyến nghị đầu tư", align="L")
        for r in display_reports_p1:
            is_exp = r.get("is_expired", False) or is_report_expired(str(r.get("report_date") or ""))
            raw_rec = str(r.get("recommendation") or "N/A")
            if is_exp:
                r1.cell(f"{raw_rec}\n(Hết hiệu lực)", align="C")
            else:
                r1.cell(raw_rec, align="C")
        if not display_reports_p1:
            r1.cell("—", align="C")
        r1.cell(str(cs.get("consensus_rating") or "MUA"), align="C")

        # Row 2: Giá mục tiêu
        r2 = table.row()
        r2.cell("2. Giá mục tiêu (VND)", align="L")
        for r in display_reports_p1:
            is_exp = r.get("is_expired", False) or is_report_expired(str(r.get("report_date") or ""))
            is_tech = r.get("is_technical", False) or "PTKT" in str(r.get("recommendation") or "").upper()
            tp = safe_float(r.get("target_price"), 0.0) or 0.0
            if is_exp:
                r2.cell(f"{tp:,.0f} đ\n(Quá 1 năm)" if tp > 0 else "— (Quá 1 năm)", align="C")
            elif is_tech:
                r2.cell("— (PTKT)", align="C")
            elif not tp or tp <= 0 or r.get("is_estimated_price", False):
                r2.cell("— (KQKD)", align="C")
            else:
                r2.cell(f"{tp:,.0f} đ", align="C")
        if not display_reports_p1:
            r2.cell("—", align="C")
        r2.cell(f"Mean: {mean_target:,.0f} đ" if mean_target > 0 else "— (Theo dõi thêm)", align="C")

        # Row 3: Upside %
        r3 = table.row()
        r3.cell("3. Tiềm năng tăng giá (Upside)", align="L")
        for r in display_reports_p1:
            is_exp = r.get("is_expired", False) or is_report_expired(str(r.get("report_date") or ""))
            is_tech = r.get("is_technical", False) or "PTKT" in str(r.get("recommendation") or "").upper()
            tp = safe_float(r.get("target_price"), 0.0) or 0.0
            up = safe_float(r.get("upside_percent"))
            if is_exp or is_tech or not tp or tp <= 0 or r.get("is_estimated_price", False) or up is None:
                r3.cell("—", align="C")
            else:
                if up < 0:
                    r3.cell(f"Vượt +{abs(up):.1f}%", align="C")
                else:
                    r3.cell(f"+{up:.1f}%", align="C")
        if not display_reports_p1:
            r3.cell("—", align="C")
        avg_up_val = safe_float(avg_upside)
        if mean_target > 0 and avg_up_val is not None and avg_up_val != 0:
            if avg_up_val < 0:
                r3.cell(f"Vượt +{abs(avg_up_val):.1f}%", align="C")
            else:
                r3.cell(f"+{avg_up_val:.1f}%", align="C")
        else:
            r3.cell("—", align="C")

        # Row 4: P/E forward
        r4 = table.row()
        r4.cell("4. Định giá P/E Forward", align="L")
        for r in display_reports_p1:
            pe = safe_float(r.get("pe_forward"))
            r4.cell(f"{pe:.1f}x" if pe else "—", align="C")
        if not display_reports_p1:
            r4.cell("—", align="C")
        valid_pes = [safe_float(r.get("pe_forward")) for r in display_reports_p1 if safe_float(r.get("pe_forward")) and safe_float(r.get("pe_forward")) > 0]
        avg_pe = sum(valid_pes) / len(valid_pes) if valid_pes else 0
        r4.cell(f"TB: {avg_pe:.1f}x" if avg_pe > 0 else "—", align="C")

        # Row 5: P/B forward
        r5 = table.row()
        r5.cell("5. Định giá P/B Forward", align="L")
        for r in display_reports_p1:
            pb = safe_float(r.get("pb_forward"))
            r5.cell(f"{pb:.2f}x" if pb else "—", align="C")
        if not display_reports_p1:
            r5.cell("—", align="C")
        valid_pbs = [safe_float(r.get("pb_forward")) for r in display_reports_p1 if safe_float(r.get("pb_forward")) and safe_float(r.get("pb_forward")) > 0]
        avg_pb = sum(valid_pbs) / len(valid_pbs) if valid_pbs else 0
        r5.cell(f"TB: {avg_pb:.2f}x" if avg_pb > 0 else "—", align="C")

        # Row 6: Dự phóng Doanh thu
        r6 = table.row()
        r6.cell("6. Dự phóng Doanh thu thuần", align="L")
        for r in display_reports_p1:
            r6.cell(str(r.get("revenue_forecast") or "N/A"), align="C")
        if not display_reports_p1:
            r6.cell("—", align="C")
        r6.cell("Đồng thuận tích cực", align="C")

        # Row 7: Dự phóng LNST
        r7 = table.row()
        r7.cell("7. Dự phóng LNST công ty mẹ", align="L")
        for r in display_reports_p1:
            r7.cell(str(r.get("npat_forecast") or "N/A"), align="C")
        if not display_reports_p1:
            r7.cell("—", align="C")
        spread = safe_float(cs.get("target_price_spread_percent"), 0.0) or 0.0
        r7.cell(f"Độ lệch: {spread:.1f}%", align="C")

        # Row 8: Phương pháp định giá
        r8 = table.row()
        r8.cell("8. Phương pháp định giá chính", align="L")
        for r in display_reports_p1:
            r8.cell(str(r.get("valuation_method") or "DCF & P/E"), align="C")
        if not display_reports_p1:
            r8.cell("—", align="C")
        r8.cell("IERM Blended", align="C")

        # Row 9: Dẫn chiếu Luận điểm & Rủi ro
        r9 = table.row()
        r9.cell("9. Luận điểm & Rủi ro chi tiết", align="L")
        for r in display_reports_p1:
            cats = r.get("key_catalysts", []) or []
            first_cat = sanitize_bullet_item(cats[0]) if cats else ""
            txt_short = (first_cat[:24] + "...") if first_cat else "Xem Trang 2"
            r9.cell(txt_short, align="C")
        if not display_reports_p1:
            r9.cell("—", align="C")
        r9.cell("→ Xem chi tiết tại Trang 2", align="C")

    pdf.ln(3)

    # Khung Chiến lược giải ngân & Quản trị rủi ro ở chân Trang 1
    pdf.set_fill_color(240, 253, 244)
    pdf.set_draw_color(187, 247, 208)
    pdf.rect(12, pdf.get_y(), 273, 9, "DF")
    pdf.set_xy(15, pdf.get_y() + 1.5)
    pdf.set_font(pdf.font_family_bold, "B", 7.8)
    pdf.set_text_color(21, 128, 61)
    buy_zone = str(cs.get("recommended_buy_zone") or "Vùng giá tích lũy khuyến nghị")
    stop_loss = str(cs.get("stop_loss_threshold") or "Ngưỡng dừng lỗ kỹ thuật")
    pdf.cell(135, 5, f"CHIẾN LƯỢC: Vùng giải ngân tích lũy khuyến nghị: {buy_zone}", align="L")
    pdf.set_text_color(185, 28, 28)
    pdf.cell(135, 5, f"QUẢN TRỊ RỦI RO: Ngưỡng dừng lỗ: {stop_loss}", align="R")

    # --- TRANG 2+: BẢNG CHI TIẾT TOÀN VĂN LUẬN ĐIỂM TĂNG TRƯỞNG & RỦI RO (QUALITATIVE DEEP-DIVE) ---
    pdf.add_page()

    pdf.set_xy(12, 22)
    pdf.set_font(pdf.font_family_bold, "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(273, 5, "PHẦN 2: BÓC TÁCH CHI TIẾT LUẬN ĐIỂM TĂNG TRƯỞNG (CATALYSTS) & RỦI RO TRỌNG YẾU (KEY RISKS)", align="L")
    pdf.ln(4.5)
    pdf.set_x(12)
    pdf.set_font(pdf.font_family_regular, "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(273, 4, f"Đối chiếu toàn văn luận cứ phân tích của {len(reports)} tổ chức nghiên cứu chứng khoán - Tự động co giãn theo nội dung, không cắt chữ", align="L")
    pdf.ln(5)

    headings_style_p2 = FontFace(family="ArialVN", emphasis="B", size_pt=8, color=(255, 255, 255), fill_color=(15, 23, 42))

    pdf.set_font(pdf.font_family_regular, "", 7.5)
    pdf.set_text_color(15, 23, 42)

    try:
        with pdf.table(col_widths=(48, 113, 112), headings_style=headings_style_p2, line_height=4.5, padding=2.0, repeat_headings=1) as table_p2:
            h_row2 = table_p2.row()
            h_row2.cell("TỔ CHỨC & KHUYẾN NGHỊ", align="L")
            h_row2.cell("LUẬN ĐIỂM TĂNG TRƯỞNG THEN CHỐT (KEY CATALYSTS)", align="L")
            h_row2.cell("RỦI RO TRỌNG YẾU CẦN THEO DÕI (KEY RISKS)", align="L")

            for r in reports:
                inst = str(r.get("institution") or "CTCK")
                date_str = str(r.get("report_date") or "")
                rec = str(r.get("recommendation") or "MUA")
                is_tech = r.get("is_technical", False) or "PTKT" in rec.upper()
                is_exp = r.get("is_expired", False) or is_report_expired(date_str)
                tp = safe_float(r.get("target_price"), 0.0) or 0.0
                up = safe_float(r.get("upside_percent"))
                if is_exp:
                    col1_text = f"{inst}\nNgày: {date_str} (Quá 1 năm)\n{rec} (Quá hạn)\nMục tiêu: {tp:,.0f} đ\nUpside: — (Quá hạn)"
                elif is_tech:
                    col1_text = f"{inst}\nNgày: {date_str}\n{rec}\nMục tiêu: — (PTKT)\nUpside: —"
                elif not tp or tp <= 0 or r.get("is_estimated_price", False) or up is None:
                    col1_text = f"{inst}\nNgày: {date_str}\n{rec}\nMục tiêu: — (KQKD)\nUpside: —"
                else:
                    up_text = f"Vượt +{abs(up):.1f}%" if up < 0 else f"+{up:.1f}%"
                    col1_text = f"{inst}\nNgày: {date_str}\n{rec}\nMục tiêu: {tp:,.0f} đ\nUpside: {up_text}"

                # Lấy tối đa 10 catalysts và 10 rủi ro, không giới hạn độ dài ký tự
                raw_cats = [sanitize_bullet_item(c) for c in (r.get("key_catalysts", []) or [])]
                cats = [c for c in raw_cats if c][:10]
                if not cats:
                    cats = ["Chưa trích xuất được luận điểm từ báo cáo này"]

                raw_risks = [sanitize_bullet_item(k) for k in (r.get("key_risks", []) or [])]
                risks = [k for k in raw_risks if k][:10]
                if not risks:
                    risks = ["Chưa trích xuất được rủi ro từ báo cáo này"]

                n_rows = max(len(cats), len(risks), 1)

                for sub_i in range(n_rows):
                    row = table_p2.row()
                    if sub_i == 0:
                        row.cell(col1_text, align="L")
                    else:
                        row.cell(f"{inst}\n(luận cứ {sub_i+1})", align="L")

                    c_text = f"• {cats[sub_i]}" if sub_i < len(cats) else ""
                    r_text = f"• {risks[sub_i]}" if sub_i < len(risks) else ""
                    row.cell(c_text, align="L")
                    row.cell(r_text, align="L")
    except Exception as render_err:
        print(f"[PDF-TABLE-WARN] table_p2 render error, switching to safe fallback: {render_err}")
        for r in reports:
            if pdf.get_y() > 165:
                pdf.add_page()
            inst = str(r.get("institution") or "CTCK")
            date_str = str(r.get("report_date") or "")
            rec = str(r.get("recommendation") or "MUA")
            pdf.set_font(pdf.font_family_bold, "B", 8)
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(273, 5, f"{inst} ({date_str}) — Khuyến nghị: {rec}", border=1, fill=True)
            pdf.ln()
            pdf.set_font(pdf.font_family_regular, "", 7.5)
            cats_text = sanitize_cell_bullet_text(r.get("key_catalysts", []), max_items=8)
            risks_text = sanitize_cell_bullet_text(r.get("key_risks", []), max_items=8)
            cur_y = pdf.get_y()
            pdf.multi_cell(136, 4.5, f"CATALYSTS:\n{cats_text}", border=1)
            end_y1 = pdf.get_y()
            pdf.set_xy(148, cur_y)
            pdf.multi_cell(137, 4.5, f"RISKS:\n{risks_text}", border=1)
            end_y2 = pdf.get_y()
            pdf.set_y(max(end_y1, end_y2) + 2)

    return bytes(pdf.output())


class SummaryNotePDF(FPDF):
    """
    Template A4 Portrait chuyên nghiệp cho Báo cáo Tổng hợp (Synthesized Research Note).
    Tổng hợp kết quả kinh doanh quý gần nhất, chỉ số định giá, luận điểm tăng trưởng đồng thuận & rủi ro.
    """
    def __init__(self, ticker: str, company_name: str, sector: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=14)
        self.ticker = ticker.upper()
        self.company_name = company_name
        self.sector = sector

        setup_pdf_unicode_fonts(self)

    def header(self):
        self.set_fill_color(15, 23, 42)  # #0F172A Slate 900
        self.rect(0, 0, 210, 18, "F")

        self.set_xy(12, 3)
        self.set_font(self.font_family_bold, "B", 10.5)
        self.set_text_color(255, 255, 255)
        self.cell(118, 5.5, "IERM RESEARCH NOTE | BÁO CÁO TỔNG HỢP", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_bold, "B", 8)
        self.set_text_color(56, 189, 248)  # Sky 400
        self.cell(68, 5.5, f"MÃ CK: {self.ticker}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.set_xy(12, 8.5)
        self.set_font(self.font_family_regular, "", 7.5)
        self.set_text_color(203, 213, 225)
        self.cell(118, 5, f"{self.company_name} | Ngành: {self.sector}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_text_color(148, 163, 184)
        self.cell(68, 5, f"Xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.ln(6)

    def footer(self):
        self.set_y(-11)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_y(-9.5)
        self.set_font(self.font_family_regular, "I", 7.0)
        self.set_text_color(148, 163, 184)
        self.cell(130, 4.5, "IERM Financial Intelligence Engine © Dữ liệu chuẩn xác Fact & Data First", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(56, 4.5, f"Trang {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")


def generate_summary_note_pdf(report_data: dict, fin_data: Optional[dict] = None) -> bytes:
    """
    Xuất Báo cáo tổng hợp đa tổ chức & phân tích nguyên nhân (Synthesized Research Note) ra file PDF A4 Portrait.
    Bao gồm:
    1. Executive Consensus Strip: Thị giá, Định giá TB, Upside, Khuyến nghị đồng thuận.
    2. Phần 1: Hiệu quả kinh doanh quý gần nhất & Động lực cốt lõi (BCTC, DuPont, P/E, P/B, ROE, ROA, Sector KPIs).
    3. Phần 2: Điểm giao thoa đồng thuận Luận điểm Tăng trưởng then chốt (Key Catalysts).
    4. Phần 3: Rủi ro trọng yếu cần giám sát & Vùng giá giải ngân / Ngưỡng dừng lỗ.
    5. Phần 4: Bảng Tổng hợp Dự phóng Doanh thu - LNST & Giá mục tiêu các Tổ chức nghiên cứu.
    """
    report_data = to_dict_safe(report_data)
    fin_data = to_dict_safe(fin_data) if fin_data else {}

    ticker = report_data.get("ticker", "CP").upper()
    company_name = report_data.get("company_name", f"Công ty Cổ phần {ticker}")
    sector = report_data.get("sector", "Doanh nghiệp niêm yết")

    # Tự động nạp financial bundle nếu fin_data bị trống
    if not fin_data or not fin_data.get("statements_quarterly"):
        try:
            from financial_data import get_financial_data_bundle
            auto_bundle = get_financial_data_bundle(ticker)
            if auto_bundle:
                fin_data = to_dict_safe(auto_bundle)
        except Exception:
            pass

    cs = to_dict_safe(report_data.get("consensus_summary", {}))
    raw_reports = report_data.get("matrix_table", [])
    reports = [to_dict_safe(r) for r in raw_reports]
    if reports:
        from engine import get_report_date_sort_key
        reports = sorted(reports, key=get_report_date_sort_key, reverse=True)

    pdf = SummaryNotePDF(ticker=ticker, company_name=company_name, sector=sector)
    pdf.alias_nb_pages()
    pdf.add_page()

    # -------------------------------------------------------------
    # KHUNG TÓM TẮT ĐIỀU HÀNH (EXECUTIVE CONSENSUS STRIP)
    # -------------------------------------------------------------
    market_p = safe_float(cs.get("current_market_price"), 0.0) or 0.0
    mean_target = safe_float(cs.get("mean_target_price"), 0.0) or 0.0
    avg_upside = safe_float(cs.get("average_upside"), 0.0) or 0.0
    rating = str(cs.get("consensus_rating") or "MUA")

    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, 20, 186, 12, "DF")

    pdf.set_xy(15, 21)
    pdf.set_font(pdf.font_family_bold, "B", 7.2)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(38, 3.5, "THỊ GIÁ THAM CHIẾU", align="L")
    pdf.cell(42, 3.5, "ĐỊNH GIÁ TRUNG BÌNH", align="L")
    pdf.cell(38, 3.5, "TIỀM NĂNG TĂNG GIÁ", align="L")
    pdf.cell(45, 3.5, "ĐỒNG THUẬN KHUYẾN NGHỊ", align="L")
    pdf.cell(23, 3.5, "SỐ BÁO CÁO", align="L")
    pdf.ln()

    pdf.set_x(15)
    pdf.set_font(pdf.font_family_bold, "B", 9.0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(38, 5.5, f"{market_p:,.0f} VND" if market_p > 0 else "—", align="L")
    pdf.set_text_color(2, 132, 199)
    if mean_target > 0:
        pdf.cell(42, 5.5, f"{mean_target:,.0f} VND", align="L")
        if avg_upside >= 0:
            pdf.set_text_color(16, 185, 129)
            pdf.cell(38, 5.5, f"+{avg_upside:.1f}%", align="L")
        else:
            pdf.set_text_color(239, 68, 68)
            pdf.cell(38, 5.5, f"Vượt +{abs(avg_upside):.1f}%", align="L")
    else:
        pdf.cell(42, 5.5, "—", align="L")
        pdf.set_text_color(245, 158, 11)
        pdf.cell(38, 5.5, "Theo dõi thêm", align="L")

    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 5.5, rating[:24], align="L")
    pdf.cell(23, 5.5, f"{len(reports)} CTCK", align="L")
    pdf.ln(7.5)

    # -------------------------------------------------------------
    # PHẦN 1: HIỆU QUẢ KINH DOANH & ĐỘNG LỰC QUÁ KHỨ/HIỆN TẠI
    # -------------------------------------------------------------
    pdf.set_font(pdf.font_family_bold, "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, "1. HIỆU QUẢ KINH DOANH & ĐỘNG LỰC QUÁ KHỨ / HIỆN TẠI", align="L")
    pdf.ln(5.2)

    # Trích xuất số liệu BCTC quý gần nhất
    sq = fin_data.get("statements_quarterly") or {}
    periods = sq.get("periods") or []
    latest_period = "—"
    rev_fmt = "—"
    rev_growth_fmt = "—"
    gp_fmt = "—"
    gm_fmt = "—"
    np_fmt = "—"
    np_growth_fmt = "—"
    nm_fmt = "—"
    de_fmt = "—"

    if periods:
        last_idx = len(periods) - 1
        rev_list = sq.get("revenue") or []
        gp_list = sq.get("gross_profit") or []
        np_list = sq.get("net_profit") or []

        while last_idx >= 0 and (last_idx >= len(rev_list) or not rev_list[last_idx]):
            last_idx -= 1
        if last_idx < 0:
            last_idx = len(periods) - 1

        latest_period = periods[last_idx]
        cur_rev = rev_list[last_idx] if last_idx < len(rev_list) else 0
        cur_gp = gp_list[last_idx] if last_idx < len(gp_list) else 0
        cur_np = np_list[last_idx] if last_idx < len(np_list) else 0

        rev_fmt = f"{cur_rev:,.0f} tỷ" if cur_rev else "—"
        gp_fmt = f"{cur_gp:,.0f} tỷ" if cur_gp else "—"
        np_fmt = f"{cur_np:,.0f} tỷ" if cur_np else "—"

        if cur_rev and cur_rev > 0:
            if cur_gp:
                gm_fmt = f"{(cur_gp / cur_rev) * 100:.1f}%"
            if cur_np:
                nm_fmt = f"{(cur_np / cur_rev) * 100:.1f}%"

        # YoY (lùi 4 quý)
        if last_idx >= 4:
            prev_rev = rev_list[last_idx - 4] if (last_idx - 4) < len(rev_list) else 0
            prev_np = np_list[last_idx - 4] if (last_idx - 4) < len(np_list) else 0
            if prev_rev and prev_rev > 0 and cur_rev:
                rg = ((cur_rev - prev_rev) / prev_rev) * 100
                rev_growth_fmt = f"{'+' if rg >= 0 else ''}{rg:.1f}% YoY"
            if prev_np and prev_np > 0 and cur_np:
                ng = ((cur_np - prev_np) / prev_np) * 100
                np_growth_fmt = f"{'+' if ng >= 0 else ''}{ng:.1f}% YoY"

    # Lấy chỉ số định giá P/E, P/B, ROE, ROA, D/E
    peers_data = fin_data.get("peers_data") or {}
    target_peer = None
    if peers_data:
        peers_list = peers_data.get("peers", [])
        target_peer = next((p for p in peers_list if (p.get("ticker") or "").upper() == ticker), None)
        if not target_peer and peers_list:
            target_peer = peers_list[0]
    ind_avg = peers_data.get("industry_average") or {}

    pe_val = f"{target_peer.get('pe'):.1f}x" if target_peer and target_peer.get("pe") else "—"
    pb_val = f"{target_peer.get('pb'):.2f}x" if target_peer and target_peer.get("pb") else "—"
    roe_val = f"{target_peer.get('roe'):.1f}%" if target_peer and target_peer.get("roe") else "—"
    roa_val = f"{target_peer.get('roa'):.1f}%" if target_peer and target_peer.get("roa") else "—"
    de_val = f"{target_peer.get('debt_to_equity'):.2f}x" if target_peer and target_peer.get("debt_to_equity") is not None else "—"

    ind_pe = f"{ind_avg.get('pe'):.1f}x" if ind_avg.get("pe") else "—"
    ind_pb = f"{ind_avg.get('pb'):.2f}x" if ind_avg.get("pb") else "—"
    ind_roe = f"{ind_avg.get('roe'):.1f}%" if ind_avg.get("roe") else "—"
    ind_roa = f"{ind_avg.get('roa'):.1f}%" if ind_avg.get("roa") else "—"

    # Bảng số liệu BCTC quý gần nhất
    col_w_4 = (46.5, 46.5, 46.5, 46.5)
    hs_sub = FontFace(family="ArialVN", emphasis="B", size_pt=7.0, color=(255, 255, 255), fill_color=(30, 41, 59))
    pdf.set_font(pdf.font_family_regular, "", 7.2)

    with pdf.table(col_widths=col_w_4, headings_style=hs_sub, line_height=4.2, padding=1.2, text_align="CENTER") as tbl_bctc:
        h1 = tbl_bctc.row()
        h1.cell(f"DOANH THU ({latest_period})")
        h1.cell("LỢI NHUẬN GỘP")
        h1.cell("LNST CÔNG TY MẸ")
        h1.cell("BIÊN RÒNG / ĐÒN BẨY D/E")

        r_val = tbl_bctc.row()
        r_val.cell(f"{rev_fmt} ({rev_growth_fmt})")
        r_val.cell(f"{gp_fmt} (Biên: {gm_fmt})")
        r_val.cell(f"{np_fmt} ({np_growth_fmt})")
        r_val.cell(f"Biên ròng: {nm_fmt} | D/E: {de_val}")

    pdf.ln(1.5)

    # Bảng chỉ số định giá & sinh lời cốt lõi đối chiếu TB ngành
    with pdf.table(col_widths=col_w_4, headings_style=hs_sub, line_height=4.2, padding=1.2, text_align="CENTER") as tbl_ratios:
        h2 = tbl_ratios.row()
        h2.cell("P/E (vs TB Ngành)")
        h2.cell("P/B (vs TB Ngành)")
        h2.cell("ROE (vs TB Ngành)")
        h2.cell("ROA (vs TB Ngành)")

        r2_val = tbl_ratios.row()
        r2_val.cell(f"{pe_val} (Ngành: {ind_pe})")
        r2_val.cell(f"{pb_val} (Ngành: {ind_pb})")
        r2_val.cell(f"{roe_val} (Ngành: {ind_roe})")
        r2_val.cell(f"{roa_val} (Ngành: {ind_roa})")

    # Chỉ số đặc thù ngành nếu có (Fleet count, freight rate index, NIM, NPL, CAR...)
    sector_kpis = peers_data.get("sector_kpi_columns") or []
    if target_peer and sector_kpis:
        pdf.ln(1.5)
        pdf.set_font(pdf.font_family_bold, "B", 7.2)
        pdf.set_text_color(180, 83, 9)  # Amber 700
        pdf.cell(186, 4, f"CHỈ SỐ HOẠT ĐỘNG CHUYÊN NGÀNH ({peers_data.get('sector_name') or sector}):", align="L")
        pdf.ln(3.8)

        kpi_chunks = [sector_kpis[i:i + 3] for i in range(0, min(len(sector_kpis), 6), 3)]
        pdf.set_font(pdf.font_family_regular, "", 7.0)
        pdf.set_text_color(15, 23, 42)
        for chunk in kpi_chunks:
            w_item = 186 / len(chunk)
            for col in chunk:
                val = target_peer.get(col.get("field"))
                avg_val = ind_avg.get(col.get("field"))
                unit = col.get("unit", "")
                val_str = f"{val:,.1f}{unit}" if isinstance(val, (int, float)) else (str(val) if val is not None else "—")
                avg_str = f"{avg_val:,.1f}{unit}" if isinstance(avg_val, (int, float)) else (str(avg_val) if avg_val is not None else "—")
                pdf.cell(w_item, 4, f"• {col.get('label')}: {val_str} (TB: {avg_str})", align="L")
            pdf.ln(4)

    # Động lực phân tích nguyên nhân quá khứ/hiện tại
    causality_items = report_data.get("causality_analysis", [])
    past_item = causality_items[0] if causality_items else None
    if past_item:
        pdf.ln(1.5)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rect(12, pdf.get_y(), 186, 12, "DF")
        pdf.set_xy(14, pdf.get_y() + 1.2)
        pdf.set_font(pdf.font_family_bold, "B", 7.2)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(182, 3.5, "ĐỘNG LỰC CỐT LÕI (ROOT CAUSES) & BẰNG CHỨNG THỰC TẾ:", align="L")
        pdf.ln(3.5)
        pdf.set_x(14)
        pdf.set_font(pdf.font_family_regular, "", 6.8)
        pdf.set_text_color(71, 85, 105)
        root_txt = str(past_item.get("root_causes") or past_item.get("phenomenon") or "Tăng trưởng cốt lõi nhờ tối ưu hóa năng lực hoạt động.")
        pdf.multi_cell(182, 3.2, root_txt[:260])
        pdf.set_y(pdf.get_y() + 2)

    # -------------------------------------------------------------
    # PHẦN 2: ĐIỂM GIAO THOA ĐỒNG THUẬN LUẬN ĐIỂM TĂNG TRƯỞNG (KEY CATALYSTS)
    # -------------------------------------------------------------
    pdf.ln(3)
    pdf.set_font(pdf.font_family_bold, "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, "2. ĐIỂM GIAO THOA ĐỒNG THUẬN LUẬN ĐIỂM TĂNG TRƯỞNG (KEY CATALYSTS)", align="L")
    pdf.ln(5.2)

    # Lấy catalysts đồng thuận từ consensus_summary hoặc trích xuất từ matrix_table
    catalysts = []
    if cs.get("consensual_catalysts"):
        for c in cs.get("consensual_catalysts"):
            c_clean = sanitize_bullet_item(c)
            if c_clean and len(c_clean) >= 15 and c_clean not in catalysts:
                catalysts.append(c_clean)
    if not catalysts and reports:
        for r in reports:
            for c in (r.get("key_catalysts") or []):
                c_clean = sanitize_bullet_item(c)
                if c_clean and len(c_clean) >= 15 and c_clean not in catalysts:
                    catalysts.append(c_clean)
                if len(catalysts) >= 8:
                    break
            if len(catalysts) >= 8:
                break

    if not catalysts:
        catalysts = [f"Kỳ vọng tăng trưởng ổn định theo chu kỳ phục hồi của ngành {sector}."]

    pdf.set_font(pdf.font_family_regular, "", 7.2)
    pdf.set_text_color(30, 41, 59)
    for idx, cat in enumerate(catalysts[:8]):
        if pdf.get_y() > 270:
            pdf.add_page()
        pdf.set_x(14)
        pdf.set_font(pdf.font_family_bold, "B", 7.2)
        pdf.set_text_color(2, 132, 199)  # Sky 600
        pdf.cell(8, 4.2, f"[{idx + 1}]", align="L")
        pdf.set_font(pdf.font_family_regular, "", 7.2)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(174, 4.2, cat)
        pdf.ln(0.8)

    # -------------------------------------------------------------
    # PHẦN 3: RỦI RO TRỌNG YẾU CẦN GIÁM SÁT (KEY RISKS)
    # -------------------------------------------------------------
    if pdf.get_y() > 245:
        pdf.add_page()

    pdf.ln(2.5)
    pdf.set_font(pdf.font_family_bold, "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, "3. RỦI RO TRỌNG YẾU CẦN GIÁM SÁT (KEY RISKS & TRIGGERS)", align="L")
    pdf.ln(5.2)

    risks = []
    if cs.get("consensual_risks"):
        for rk in cs.get("consensual_risks"):
            rk_clean = sanitize_bullet_item(rk)
            if rk_clean and len(rk_clean) >= 15 and rk_clean not in risks:
                risks.append(rk_clean)
    if not risks and reports:
        for r in reports:
            for rk in (r.get("key_risks") or []):
                rk_clean = sanitize_bullet_item(rk)
                if rk_clean and len(rk_clean) >= 15 and rk_clean not in risks:
                    risks.append(rk_clean)
                if len(risks) >= 6:
                    break
            if len(risks) >= 6:
                break

    if not risks:
        risks = [f"Rủi ro biến động kinh tế vĩ mô và sức cầu thị trường ảnh hưởng tới {ticker}."]

    for idx, rk in enumerate(risks[:6]):
        if pdf.get_y() > 270:
            pdf.add_page()
        pdf.set_x(14)
        pdf.set_font(pdf.font_family_bold, "B", 7.2)
        pdf.set_text_color(225, 29, 72)  # Rose 600
        pdf.cell(8, 4.2, f"[!]", align="L")
        pdf.set_font(pdf.font_family_regular, "", 7.2)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(174, 4.2, rk)
        pdf.ln(0.8)

    # Khung Chiến lược đầu tư & Quản trị rủi ro
    pdf.ln(1.5)
    if pdf.get_y() > 265:
        pdf.add_page()

    pdf.set_fill_color(240, 253, 244)
    pdf.set_draw_color(187, 247, 208)
    pdf.rect(12, pdf.get_y(), 186, 8.5, "DF")
    pdf.set_xy(14, pdf.get_y() + 1.2)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(21, 128, 61)
    buy_zone = str(cs.get("recommended_buy_zone") or "Vùng giá tích lũy khuyến nghị")
    stop_loss = str(cs.get("stop_loss_threshold") or "Ngưỡng dừng lỗ kỹ thuật")
    pdf.cell(93, 4.5, f"VÙNG GIẢI NGÂN KHUYẾN NGHỊ: {buy_zone}", align="L")
    pdf.set_text_color(185, 28, 28)
    pdf.cell(89, 4.5, f"NGƯỠNG DỪNG LỖ QUẢN TRỊ: {stop_loss}", align="R")
    pdf.ln(7.5)

    # -------------------------------------------------------------
    # PHẦN 4: BẢNG DỰ PHÓNG KQKD & ĐỊNH GIÁ TỪ CÁC TỔ CHỨC
    # -------------------------------------------------------------
    if pdf.get_y() > 220:
        pdf.add_page()

    pdf.set_font(pdf.font_family_bold, "B", 8.8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, "4. TỔNG HỢP DỰ PHÓNG DOANH THU - LNST & GIÁ MỤC TIÊU CÁC CTCK", align="L")
    pdf.ln(5.2)

    col_w_proj = (42, 28, 36, 40, 40)
    hs_proj = FontFace(family="ArialVN", emphasis="B", size_pt=7.2, color=(255, 255, 255), fill_color=(15, 23, 42))
    pdf.set_font(pdf.font_family_regular, "", 7.0)

    with pdf.table(col_widths=col_w_proj, headings_style=hs_proj, line_height=4.4, padding=1.2, text_align="CENTER") as tbl_proj:
        hp = tbl_proj.row()
        hp.cell("TỔ CHỨC NGHIÊN CỨU", align="L")
        hp.cell("KHUYẾN NGHỊ", align="C")
        hp.cell("GIÁ MỤC TIÊU", align="R")
        hp.cell("DỰ PHÓNG DOANH THU", align="R")
        hp.cell("DỰ PHÓNG LNST", align="R")

        for r in reports[:10]:
            inst = str(r.get("institution") or "CTCK")
            rec = str(r.get("recommendation") or "MUA")
            tp = safe_float(r.get("target_price"), 0.0) or 0.0
            up = safe_float(r.get("upside_percent"))
            is_exp = r.get("is_expired", False) or is_report_expired(str(r.get("report_date") or ""))
            is_tech = r.get("is_technical", False) or "PTKT" in rec.upper()

            if is_exp:
                tp_text = f"{tp:,.0f} đ (Hết hạn)" if tp > 0 else "— (Quá 1 năm)"
            elif is_tech:
                tp_text = "— (PTKT)"
            elif not tp or tp <= 0 or r.get("is_estimated_price", False):
                tp_text = "— (KQKD)"
            else:
                up_sub = f" (+{up:.1f}%)" if (up is not None and up >= 0) else (f" (Vượt +{abs(up):.1f}%)" if up is not None else "")
                tp_text = f"{tp:,.0f} đ{up_sub}"

            rev_f = str(r.get("revenue_forecast") or "—")
            npat_f = str(r.get("npat_forecast") or "—")

            rp = tbl_proj.row()
            rp.cell(inst, align="L")
            rp.cell(rec, align="C")
            rp.cell(tp_text, align="R")
            rp.cell(rev_f, align="R")
            rp.cell(npat_f, align="R")

        # Dòng tổng hợp đồng thuận
        cons_row = tbl_proj.row()
        cons_row.cell("ĐỒNG THUẬN TB (CONSENSUS)", align="L")
        cons_row.cell(rating[:12], align="C")
        if mean_target > 0:
            up_s = f" (+{avg_upside:.1f}%)" if avg_upside >= 0 else f" (Vượt +{abs(avg_upside):.1f}%)"
            cons_row.cell(f"{mean_target:,.0f} đ{up_s}", align="R")
        else:
            cons_row.cell("— (Theo dõi)", align="R")
        cons_row.cell("Đồng thuận tăng trưởng", align="R")
        spread = safe_float(cs.get("target_price_spread_percent"), 0.0) or 0.0
        cons_row.cell(f"Độ lệch: {spread:.1f}%", align="R")

    return bytes(pdf.output())



class PeerComparisonLandscapePDF(FPDF):
    def __init__(self, ticker: str, sector: str, peer_count: int):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.ticker = ticker.upper()
        self.sector = sector
        self.peer_count = peer_count

        setup_pdf_unicode_fonts(self)

    def header(self):
        self.set_fill_color(15, 23, 42)  # Slate 900
        self.rect(0, 0, 297, 20, "F")

        self.set_xy(12, 2.5)
        self.set_text_color(148, 163, 184)
        self.set_font(self.font_family_regular, "", 8)
        self.cell(160, 4.5, "IERM TERMINAL // BÁO CÁO PHÂN TÍCH ĐỐI THỦ CÙNG NGÀNH", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_regular, "", 7.5)
        self.set_text_color(100, 116, 139)
        self.cell(113, 4.5, "PEER BENCHMARKING & INDUSTRY RADAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.set_xy(12, 8)
        self.set_font(self.font_family_bold, "B", 11.5)
        self.set_text_color(254, 240, 138)  # Gold highlight
        self.cell(185, 7, f"Mã CK: {self.ticker} | Ngành: {self.sector} | Quy mô: {self.peer_count} Doanh nghiệp", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")

        self.set_font(self.font_family_regular, "", 8)
        self.set_text_color(203, 213, 225)
        self.cell(88, 7, f"Thời điểm xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y(), 285, self.get_y())
        self.set_y(-10)
        self.set_font(self.font_family_regular, "I", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(180, 5, "IERM Financial Intelligence Engine © Ưu tiên API SSI #1 (Bổ sung Vietstock & CafeF)", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(93, 5, f"Trang {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")


def generate_peer_comparison_pdf(peers_data: dict, radar_img_base64: Optional[str] = None) -> bytes:
    """
    Tạo file PDF A4 Landscape báo cáo so sánh đối thủ cùng ngành và Radar sức mạnh tài chính.
    Bao gồm:
    - Trang 1: Tóm lược chỉ số ngành & Bảng số liệu chi tiết toàn bộ doanh nghiệp cùng ngành.
    - Trang 2+: Radar sức mạnh tài chính (ảnh + bảng hoặc vector bar charts) & Mô hình 5 lực lượng cạnh tranh Porter + Catalysts.
    """
    target_ticker = (peers_data.get("target_ticker") or "CP").upper()
    sector_name = peers_data.get("sector_name") or "Doanh nghiệp niêm yết"
    peers = peers_data.get("peers", [])
    avg = peers_data.get("industry_average", {})
    kpi_cols = peers_data.get("sector_kpi_columns", [])
    radar = peers_data.get("radar_metrics", {})
    forces = peers_data.get("porter_five_forces", {})
    cycle = peers_data.get("industry_cycle", "Tăng trưởng theo chu kỳ ngành")
    catalysts = peers_data.get("industry_catalysts", [])

    def fmt_num(v, suffix="", default="—"):
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return f"{v:.1f}{suffix}"
        s = str(v).strip()
        if not s or s in ("-", "—"):
            return default
        if suffix and s.endswith(suffix):
            return s
        return f"{s}{suffix}" if suffix else s

    if not peers:
        peers = [{
            "ticker": target_ticker,
            "name": f"CTCP {target_ticker}",
            "market_cap_bil": 1000.0,
            "pe": 12.5, "pb": 1.45, "roe": 14.5, "roa": 6.8, "net_margin": 12.5, "debt_to_equity": 0.65
        }]

    pdf = PeerComparisonLandscapePDF(ticker=target_ticker, sector=sector_name, peer_count=len(peers))
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- 1. EXECUTIVE SUMMARY STRIP ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, 22, 273, 11, "DF")

    pdf.set_xy(15, 23)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(50, 3.5, "MÃ CỔ PHIẾU PHÂN TÍCH", align="L")
    pdf.cell(55, 3.5, "NGÀNH NGHỀ KINH DOANH", align="L")
    pdf.cell(55, 3.5, "P/E DOANH NGHIỆP / TB NGÀNH", align="L")
    pdf.cell(55, 3.5, "ROE DOANH NGHIỆP / TB NGÀNH", align="L")
    pdf.cell(55, 3.5, "BIÊN RÒNG / TB NGÀNH", align="L")
    pdf.ln()

    # Target Peer Stats
    target_peer = next((p for p in peers if p.get("ticker") == target_ticker), peers[0])
    t_pe = fmt_num(target_peer.get("pe"), "x")
    a_pe = fmt_num(avg.get("pe"), "x")
    t_roe = fmt_num(target_peer.get("roe"), "%")
    a_roe = fmt_num(avg.get("roe"), "%")
    t_nm = fmt_num(target_peer.get("net_margin"), "%")
    a_nm = fmt_num(avg.get("net_margin"), "%")

    pdf.set_x(15)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    pdf.set_text_color(2, 132, 199)  # Sky blue
    pdf.cell(50, 4.5, f"{target_ticker} (Đang xem)", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.cell(55, 4.5, f"{sector_name[:28]}", align="L")
    pdf.cell(55, 4.5, f"{t_pe}  vs  {a_pe}", align="L")
    pdf.set_text_color(16, 185, 129)  # Green
    pdf.cell(55, 4.5, f"{t_roe}  vs  {a_roe}", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.cell(55, 4.5, f"{t_nm}  vs  {a_nm}", align="L")

    pdf.ln(7)

    # --- 2. PEER COMPARISON TABLE ---
    pdf.set_xy(12, 35)
    pdf.set_font(pdf.font_family_bold, "B", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(200, 5, "BẢNG CHỈ SỐ TÀI CHÍNH & ĐỊNH GIÁ ĐỐI THỦ CÙNG NGÀNH", align="L")
    pdf.set_font(pdf.font_family_regular, "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(73, 5, "Đơn vị: Tỷ VNĐ / Lần (x) / Tỷ lệ (%)", align="R")
    pdf.ln(5.5)

    base_cols = [
        ["Mã CP", 18],
        ["Doanh nghiệp", 50],
        ["Vốn hóa", 24],
        ["P/E", 18],
        ["P/B", 18],
        ["ROE", 20],
        ["ROA", 20],
        ["Biên ròng", 22],
        ["Nợ/VCSH", 20],
    ]
    base_total = sum(w for _, w in base_cols)
    remain = 273 - base_total

    kpi_count = len(kpi_cols)
    kpi_widths = []
    if kpi_count > 0:
        kpi_w = max(18, remain / kpi_count)
        if base_total + kpi_count * kpi_w > 273:
            excess = (base_total + kpi_count * kpi_w) - 273
            base_cols[1][1] = max(35, 50 - excess)
            base_total = sum(w for _, w in base_cols)
            kpi_w = (273 - base_total) / kpi_count
        kpi_widths = [kpi_w] * kpi_count

    all_widths = [w for _, w in base_cols] + kpi_widths
    headings_style = FontFace(family="ArialVN", emphasis="B", size_pt=7.5, color=(255, 255, 255), fill_color=(15, 23, 42))

    with pdf.table(col_widths=tuple(all_widths), headings_style=headings_style, line_height=4.8, padding=1.6, repeat_headings=1) as table:
        h = table.row()
        for label, _ in base_cols:
            h.cell(label, align="L" if label in ("Mã CP", "Doanh nghiệp") else "R")
        for col in kpi_cols:
            lbl = col.get("label", "")
            unit = col.get("unit", "")
            h.cell(f"{lbl} ({unit})" if unit else lbl, align="R")

        for p in peers:
            row = table.row()
            is_target = p.get("ticker") == target_ticker
            if is_target:
                row_style = FontFace(family="ArialVN", emphasis="B", size_pt=7.5, color=(2, 132, 199), fill_color=(224, 242, 254))
            else:
                row_style = FontFace(family="ArialVN", size_pt=7.0, color=(30, 41, 59))

            mcap = p.get("market_cap_bil", 0)
            mcap_str = f"{mcap/1000:.1f}k tỷ" if mcap >= 1000 else f"{int(mcap):,} tỷ" if mcap else "—"

            row.cell(p.get("ticker", "") + (" *" if is_target else ""), style=row_style, align="L")
            row.cell(p.get("name", "")[:28], style=row_style, align="L")
            row.cell(mcap_str, style=row_style, align="R")
            row.cell(fmt_num(p.get("pe"), "x"), style=row_style, align="R")
            row.cell(fmt_num(p.get("pb"), "x"), style=row_style, align="R")
            row.cell(fmt_num(p.get("roe"), "%"), style=row_style, align="R")
            row.cell(fmt_num(p.get("roa"), "%"), style=row_style, align="R")
            row.cell(fmt_num(p.get("net_margin"), "%"), style=row_style, align="R")
            row.cell(fmt_num(p.get("debt_to_equity"), "x"), style=row_style, align="R")

            for col in kpi_cols:
                val = p.get(col.get("field"))
                val_str = f"{val:,.1f}" if isinstance(val, (int, float)) else str(val) if val is not None else "—"
                row.cell(val_str, style=row_style, align="R")

        avg_style = FontFace(family="ArialVN", emphasis="B", size_pt=7.5, color=(15, 23, 42), fill_color=(226, 232, 240))
        avg_row = table.row()
        avg_row.cell(f"TRUNG BÌNH ({len(peers)} DN)", style=avg_style, align="L")
        avg_row.cell("—", style=avg_style, align="L")
        avg_row.cell("—", style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("pe"), "x"), style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("pb"), "x"), style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("roe"), "%"), style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("roa"), "%"), style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("net_margin"), "%"), style=avg_style, align="R")
        avg_row.cell(fmt_num(avg.get("debt_to_equity"), "x"), style=avg_style, align="R")
        for col in kpi_cols:
            val = avg.get(col.get("field"))
            val_str = f"{val:,.1f}" if isinstance(val, (int, float)) else str(val) if val is not None else "—"
            avg_row.cell(val_str, style=avg_style, align="R")

    # --- 3. PHẦN 2: RADAR SỨC MẠNH TÀI CHÍNH & PORTER 5 FORCES ---
    pdf.add_page()

    pdf.set_xy(12, 22)
    pdf.set_font(pdf.font_family_bold, "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(273, 5, f"PHẦN 2: RADAR SỨC MẠNH TÀI CHÍNH & MÔ HÌNH CẠNH TRANH NGÀNH ({sector_name.upper()})", align="L")
    pdf.ln(5)

    current_y = pdf.get_y()

    # Cột Trái: Radar Metrics & Biểu đồ (Rộng 132mm, Cao 160mm)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(12, current_y, 132, 160, "DF")

    pdf.set_xy(15, current_y + 2)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(126, 5, f"1. RADAR SỨC MẠNH TÀI CHÍNH ({target_ticker} VS TB NGÀNH)", align="L")
    pdf.ln(5.5)

    temp_img_path = None
    has_embedded_img = False
    if radar_img_base64:
        try:
            clean_b64 = radar_img_base64.split(",", 1)[1] if "," in radar_img_base64 else radar_img_base64
            img_bytes = base64.b64decode(clean_b64)
            if len(img_bytes) > 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_bytes)
                    temp_img_path = tmp.name
                pdf.image(temp_img_path, x=18, y=pdf.get_y(), w=120)
                pdf.set_y(pdf.get_y() + 82)
                has_embedded_img = True
        except Exception as e:
            print("Failed to embed radar img:", e)

    cats = radar.get("categories") if (radar and radar.get("categories")) else ["Khả năng Sinh lời", "Hiệu quả Quy mô", "An toàn Tài chính", "Định giá Hấp dẫn", "Tiềm năng Tăng trưởng"]
    t_scores = radar.get(target_ticker.lower()) or radar.get("target") or [85, 80, 85, 80, 85]
    i_scores = radar.get("industry") or [60, 65, 70, 65, 65]

    if not has_embedded_img:
        # VẼ BIỂU ĐỒ SO SÁNH CỘT NGANG VECTOR ĐẶC SẮC (KHÔNG BAO GIỜ TRỐNG TRƠN)
        pdf.set_xy(16, pdf.get_y())
        pdf.set_font(pdf.font_family_bold, "B", 7.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(124, 4, "So sánh điểm số sức mạnh tài chính chuẩn hóa (0 - 100):", align="L")
        pdf.ln(5)

        # Chú thích màu
        pdf.set_xy(16, pdf.get_y())
        pdf.set_fill_color(2, 132, 199)
        pdf.rect(16, pdf.get_y() + 0.5, 4, 3, "F")
        pdf.set_xy(22, pdf.get_y())
        pdf.set_font(pdf.font_family_bold, "B", 7.0)
        pdf.set_text_color(2, 132, 199)
        pdf.cell(35, 4, f"{target_ticker} (Đang xem)", align="L")

        pdf.set_fill_color(148, 163, 184)
        pdf.rect(60, pdf.get_y() + 0.5, 4, 3, "F")
        pdf.set_xy(66, pdf.get_y())
        pdf.set_text_color(100, 116, 139)
        pdf.cell(35, 4, "Trung bình ngành", align="L")
        pdf.ln(5.5)

        bar_start_y = pdf.get_y()
        for idx, cat in enumerate(cats):
            ts = t_scores[idx] if idx < len(t_scores) else 0
            is_ = i_scores[idx] if idx < len(i_scores) else 0
            y_pos = bar_start_y + idx * 13.5

            pdf.set_xy(16, y_pos)
            pdf.set_font(pdf.font_family_bold, "B", 7.0)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(42, 4, cat, align="L")

            # Thanh nền nhạt
            pdf.set_fill_color(241, 245, 249)
            pdf.rect(58, y_pos, 52, 4.2, "F")
            # Thanh Target ticker (xanh dương)
            pdf.set_fill_color(2, 132, 199)
            t_w = max(2.0, min(52.0, (ts / 100.0) * 52.0))
            pdf.rect(58, y_pos, t_w, 4.2, "F")
            # Điểm Target
            pdf.set_xy(112, y_pos)
            pdf.set_font(pdf.font_family_bold, "B", 7.0)
            pdf.set_text_color(2, 132, 199)
            pdf.cell(14, 4, f"{ts} đ", align="L")

            # Thanh Industry (xám)
            pdf.set_fill_color(241, 245, 249)
            pdf.rect(58, y_pos + 5.0, 52, 3.8, "F")
            pdf.set_fill_color(148, 163, 184)
            i_w = max(2.0, min(52.0, (is_ / 100.0) * 52.0))
            pdf.rect(58, y_pos + 5.0, i_w, 3.8, "F")
            # Điểm Industry
            pdf.set_xy(112, y_pos + 5.0)
            pdf.set_font(pdf.font_family_regular, "", 6.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(14, 3.8, f"{is_} đ", align="L")

        pdf.set_y(bar_start_y + len(cats) * 13.5 + 4)

    # Bảng chi tiết điểm số sức mạnh tài chính
    pdf.set_x(15)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(126, 4, "Chi tiết điểm số sức mạnh tài chính chuẩn hóa (0 - 100):", align="L")
    pdf.ln(4)

    radar_style = FontFace(family="ArialVN", emphasis="B", size_pt=7.0, color=(255, 255, 255), fill_color=(30, 41, 59))
    with pdf.table(col_widths=(45, 26, 26, 29), headings_style=radar_style, line_height=4.5, padding=1.5) as r_tbl:
        rh = r_tbl.row()
        rh.cell("Trụ cột đánh giá", align="L")
        rh.cell(f"{target_ticker}", align="R")
        rh.cell("TB Ngành", align="R")
        rh.cell("Chênh lệch", align="R")

        for idx, cat in enumerate(cats):
            rrow = r_tbl.row()
            ts = t_scores[idx] if idx < len(t_scores) else 0
            is_ = i_scores[idx] if idx < len(i_scores) else 0
            diff = round(ts - is_, 1)
            diff_str = f"+{diff}" if diff > 0 else f"{diff}"
            rrow.cell(cat, align="L")
            rrow.cell(f"{ts}", align="R")
            rrow.cell(f"{is_}", align="R")
            rrow.cell(diff_str, align="R")

    # Cột Phải: Mô hình 5 lực lượng Porter & Catalysts (Rộng 136mm)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(149, current_y, 136, 160, "DF")

    pdf.set_xy(152, current_y + 2)
    pdf.set_font(pdf.font_family_bold, "B", 8.5)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(130, 5, "2. MÔ HÌNH 5 LỰC LƯỢNG PORTER & CATALYSTS", align="L")
    pdf.ln(6)

    pdf.set_x(152)
    pdf.set_font(pdf.font_family_bold, "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(130, 4, f"Chu kỳ ngành hiện tại: {cycle}", align="L")
    pdf.ln(5)

    force_labels = {
        "rivalry": "1. Mức độ cạnh tranh nội bộ ngành",
        "supplier_power": "2. Quyền lực nhà cung ứng",
        "buyer_power": "3. Quyền lực khách hàng",
        "substitution_threat": "4. Nguy cơ hàng thay thế",
        "new_entrants_threat": "5. Rào cản đối thủ mới gia nhập"
    }

    if forces:
        for k, v in forces.items():
            pdf.set_x(152)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(226, 232, 240)
            score = v.get("score", 3)
            badge_text = f"Mức {score}/5"

            pdf.set_font(pdf.font_family_bold, "B", 7.5)
            if score >= 4:
                pdf.set_text_color(185, 28, 28)
            elif score == 3:
                pdf.set_text_color(180, 83, 9)
            else:
                pdf.set_text_color(21, 128, 61)

            pdf.cell(100, 4, f"• {force_labels.get(k, k)}", align="L")
            pdf.cell(30, 4, badge_text, align="R")
            pdf.ln(4)

            pdf.set_x(155)
            pdf.set_font(pdf.font_family_regular, "", 7.0)
            pdf.set_text_color(71, 85, 105)
            desc = v.get("desc", "")
            pdf.multi_cell(125, 3.5, desc)
            pdf.ln(1.5)

    if catalysts:
        pdf.ln(2)
        pdf.set_x(152)
        pdf.set_font(pdf.font_family_bold, "B", 7.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(130, 4, "ĐỘNG LỰC TĂNG TRƯỞNG & CATALYSTS THEN CHỐT:", align="L")
        pdf.ln(4.5)
        for idx, c in enumerate(catalysts[:4]):
            pdf.set_x(155)
            pdf.set_font(pdf.font_family_regular, "", 7.0)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(125, 3.5, f"[{idx+1}] {c}")
            pdf.ln(1)

    if temp_img_path and os.path.exists(temp_img_path):
        try:
            os.remove(temp_img_path)
        except Exception:
            pass

    return bytes(pdf.output())

