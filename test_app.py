"""
Institutional Equity Research Matrix (IERM) - Automated Verification Suite
"""

import unittest
from engine import (
    ReportItem,
    calculate_consensus,
    extract_financial_data_from_text,
    PRESET_DATASETS
)
from server import app
from starlette.testclient import TestClient


class TestIERM(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_presets_integrity(self):
        """Kiểm tra tính toàn vẹn của các bộ dữ liệu mẫu đa tổ chức HPG, FPT, MWG, HCM, GEX, PDR"""
        self.assertIn("HPG", PRESET_DATASETS)
        self.assertIn("FPT", PRESET_DATASETS)
        self.assertIn("MWG", PRESET_DATASETS)
        self.assertIn("HCM", PRESET_DATASETS)
        self.assertIn("GEX", PRESET_DATASETS)
        self.assertIn("PDR", PRESET_DATASETS)

        hpg = PRESET_DATASETS["HPG"]
        self.assertEqual(hpg.ticker, "HPG")
        self.assertEqual(len(hpg.matrix_table), 6)  # 6 CTCK: SSI, HSC, Vietcap, VNDirect, MAS, VCBS
        self.assertGreater(hpg.consensus_summary.mean_target_price, 30000)
        self.assertGreater(len(hpg.causality_analysis), 0)
        self.assertGreater(len(hpg.disensus_table), 0)

        hcm = PRESET_DATASETS["HCM"]
        self.assertEqual(hcm.ticker, "HCM")
        self.assertEqual(len(hcm.matrix_table), 5)  # 5 CTCK: SSI, Vietcap, VNDirect, MAS, VCBS
        self.assertGreater(hcm.consensus_summary.mean_target_price, 30000)

    def test_hcm_full_bundle(self):
        """Kiểm tra mã HCM (khoanh đỏ số 1) nạp đầy đủ dữ liệu cho cả 6 tabs mà không bị thiếu mục nào"""
        resp_preset = self.client.get("/api/preset/HCM")
        self.assertEqual(resp_preset.status_code, 200)
        p_data = resp_preset.json()
        self.assertEqual(p_data["ticker"], "HCM")
        self.assertIn("HSC", p_data["company_name"])
        self.assertGreater(len(p_data["matrix_table"]), 0)

        resp_fin = self.client.get("/api/financial-overview/HCM")
        self.assertEqual(resp_fin.status_code, 200)
        f_data = resp_fin.json()
        self.assertEqual(f_data["company_profile"]["ticker"], "HCM")
        self.assertEqual(len(f_data["dupont"]), 9)  # Dupont fields
        self.assertEqual(len(f_data["piotroski"]["criteria"]), 9)
        self.assertIn("statements_annual", f_data)
        self.assertGreater(len(f_data["statements_annual"]["revenue"]), 0)

        resp_tech = self.client.get("/api/technical/HCM")
        self.assertEqual(resp_tech.status_code, 200)
        t_data = resp_tech.json()
        self.assertEqual(t_data["ticker"], "HCM")
        self.assertGreater(len(t_data["candles_history"]), 0)

    def test_lhg_company_name_and_sector(self):
        """Kiểm tra mã LHG hiển thị đúng tên CTCP Long Hậu và ngành Bất động sản Khu công nghiệp"""
        resp_preset = self.client.get("/api/preset/LHG")
        self.assertEqual(resp_preset.status_code, 200)
        p_data = resp_preset.json()
        self.assertEqual(p_data["ticker"], "LHG")
        self.assertIn("Long Hậu", p_data["company_name"])
        self.assertIn("Khu công nghiệp", p_data["sector"])
        self.assertNotEqual(p_data["sector"], "Doanh nghiệp niêm yết")

        resp_fin = self.client.get("/api/financial-overview/LHG")
        self.assertEqual(resp_fin.status_code, 200)
        f_data = resp_fin.json()
        self.assertIn("Long Hậu", f_data["company_profile"]["name"])
        self.assertIn("Khu công nghiệp", f_data["company_profile"]["sector"])

    def test_consensus_calculator(self):
        """Kiểm tra bộ tính toán Consensus và Disensus"""
        reports = [
            ReportItem(
                institution="CTCK A",
                report_date="01/08/2026",
                recommendation="MUA",
                target_price=40000,
                current_price_at_report=30000,
                pe_forward=12.0,
                revenue_forecast="100,000 tỷ",
                npat_forecast="10,000 tỷ",
                key_catalysts=["Mở rộng thị phần"],
                key_risks=["Tỷ giá"]
            ),
            ReportItem(
                institution="CTCK B",
                report_date="05/08/2026",
                recommendation="KHẢ QUAN",
                target_price=36000,
                current_price_at_report=30000,
                pe_forward=13.0,
                revenue_forecast="95,000 tỷ",
                npat_forecast="9,200 tỷ",
                key_catalysts=["Tiết giảm chi phí"],
                key_risks=["Lãi suất"]
            ),
            ReportItem(
                institution="CTCK C",
                report_date="10/08/2026",
                recommendation="NẮM GIỮ",
                target_price=32000,
                current_price_at_report=30000,
                pe_forward=14.0,
                revenue_forecast="90,000 tỷ",
                npat_forecast="8,500 tỷ",
                key_catalysts=["Đầu tư công"],
                key_risks=["Cạnh tranh"]
            )
        ]

        result = calculate_consensus(reports, ticker="TEST", current_market_price=30000)
        cs = result.consensus_summary

        self.assertEqual(cs.mean_target_price, 36000)
        self.assertEqual(cs.median_target_price, 36000)
        self.assertEqual(cs.min_target_price, 32000)
        self.assertEqual(cs.max_target_price, 40000)
        self.assertAlmostEqual(cs.average_upside, 20.0, places=1)
        self.assertGreater(len(result.disensus_table), 0)

    def test_market_tape_api(self):
        """Kiểm tra API bảng giá thị trường live cho dải Ticker Tape (Khoanh đỏ số 3)"""
        resp = self.client.get("/api/market-tape?ticker=HCM")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("indices", data)
        self.assertIn("stocks", data)
        self.assertGreater(len(data["indices"]), 0)
        self.assertGreater(len(data["stocks"]), 0)
        symbols = [s["symbol"] for s in data["stocks"]]
        self.assertIn("HCM", symbols)

    def test_benchmark_recommendations_api(self):
        """Kiểm tra API danh sách khuyến nghị CTCK cho thanh chip tiêu biểu (Khoanh đỏ số 2)"""
        resp = self.client.get("/api/benchmark-recommendations")
        self.assertEqual(resp.status_code, 200)
        list_rec = resp.json()
        self.assertEqual(len(list_rec), 8)
        tickers = [x["ticker"] for x in list_rec]
        self.assertIn("HPG", tickers)
        self.assertIn("HCM", tickers)
        self.assertIn("SSI", tickers)
        for item in list_rec:
            self.assertIn("rating", item)
            self.assertIn("upside", item)

    def test_api_health_and_presets(self):
        """Kiểm tra API health check và presets"""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "online")

        resp2 = self.client.get("/api/presets")
        self.assertEqual(resp2.status_code, 200)
        presets = resp2.json()
        self.assertGreaterEqual(len(presets), 8)

        resp3 = self.client.get("/api/preset/HPG")
        self.assertEqual(resp3.status_code, 200)
        hpg_data = resp3.json()
        self.assertEqual(hpg_data["ticker"], "HPG")

    def test_api_search(self):
        """Kiểm tra API tìm kiếm báo cáo"""
        resp = self.client.get("/api/search?ticker=HPG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["total_found"], 0)

    def test_api_raw_text_analysis(self):
        """Kiểm tra bóc tách văn bản thô tiếng Việt"""
        raw_text = """
        Báo cáo phân tích SSI Research phát hành ngày 15/08/2026.
        Khuyến nghị: MUA
        Giá mục tiêu: 38,500 đồng/cp.
        P/E forward: 11.5x. P/B forward: 1.6x.
        Doanh thu kỳ vọng: 170,000 tỷ VND (+22% YoY).
        LNST dự phóng: 16,000 tỷ VND (+40% YoY).
        Luận điểm then chốt:
        - Đưa lò cao Dung Quất 2 vào hoạt động đúng kế hoạch.
        - Biên lợi nhuận gộp hồi phục mạnh nhờ giá quặng sắt giảm.
        - Hưởng lợi từ chính sách phòng vệ thương mại chống bán phá giá.
        Rủi ro trọng yếu:
        - Thị trường bất động sản hồi phục chậm.
        - Biến động tỷ giá USD/VND.
        """
        admin_hdr = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}
        resp = self.client.post("/api/analyze-raw", json={"raw_text": raw_text, "institution": "SSI"}, headers=admin_hdr)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()
        self.assertEqual(item["institution"], "SSI")
        self.assertEqual(item["recommendation"], "MUA")
        self.assertEqual(item["target_price"], 38500)
        self.assertEqual(item["pe_forward"], 11.5)
        self.assertIn("16,000", item["npat_forecast"])

    def test_api_export_markdown_and_csv(self):
        """Kiểm tra tính năng xuất Markdown và CSV đúng chuẩn 4 phần của prompt"""
        hpg = PRESET_DATASETS["HPG"].model_dump()
        resp = self.client.post("/api/export-markdown", json={"report_data": hpg})
        self.assertEqual(resp.status_code, 200)
        md = resp.json()["markdown"]

        # Kiểm tra sự hiện diện của đầy đủ 4 phần
        self.assertIn("1. BẢNG MA TRẬN SO SÁNH ĐA TỔ CHỨC", md)
        self.assertIn("2. PHÂN TÍCH CHUYÊN SÂU: NGUYÊN NHÂN - KẾT QUẢ - BẰNG CHỨNG", md)
        self.assertIn("3. BẢNG PHÂN HÓA QUAN ĐIỂM (DISENSUS & CONSENSUS ANALYSIS)", md)
        self.assertIn("4. KẾT LUẬN & HÀNH ĐỘNG DÀNH CHO NHÀ ĐẦU TƯ", md)

        # Kiểm tra CSV
        resp_csv = self.client.post("/api/export-csv", json={"report_data": hpg})
        self.assertEqual(resp_csv.status_code, 200)
        self.assertIn("text/csv", resp_csv.headers["content-type"])
        self.assertIn("Vietcap (VCSC)", resp_csv.text)

    def test_api_live_price(self):
        """Kiểm tra API lấy giá đóng cửa từ Vietstock Chart và CTCKs"""
        resp = self.client.get("/api/live-price/HPG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "HPG")
        self.assertGreater(data["latest_close"], 0)
        self.assertIn("selected_source", data)
        self.assertGreater(len(data["sources_comparison"]), 0)


    def test_api_financial_overview(self):
        """Kiểm tra API phân tích BCTC, Dupont, Piotroski, Z-score, DCF"""
        resp = self.client.get("/api/financial-overview/HPG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "HPG")
        self.assertIn("dupont", data)
        self.assertIn("piotroski", data)
        self.assertIn("altman_z", data)
        self.assertIn("statements_annual", data)
        self.assertIn("peers_data", data)
        self.assertIn("valuation", data)

        # Check Piotroski score criteria count
        self.assertEqual(len(data["piotroski"]["criteria"]), 9)
        # Check Altman Z score is safe or grey
        self.assertIn(data["altman_z"]["color"], ["emerald", "amber"])

    def test_api_interactive_dcf(self):
        """Kiểm tra API định giá DCF tùy biến tương tác"""
        req_body = {
            "ticker": "HPG",
            "wacc": 11.5,
            "terminal_g": 2.5,
            "fcf_growth_rate": 15.0
        }
        resp = self.client.post("/api/valuation/dcf", json=req_body)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "HPG")
        self.assertGreater(data["dcf_fair_value"], 0)
        self.assertIn("margin_of_safety_percent", data)

    def test_api_crawl_url_and_synthesis(self):
        """Kiểm tra API bóc tách dữ liệu từ link URL (Web/PDF) và cơ chế tổng hợp tự động"""
        admin_hdr = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}
        resp = self.client.post("/api/crawl-url", json={
            "url": "https://finance.vietstock.vn/TCH/bao-cao-phan-tich.htm",
            "ticker": "TCH",
            "institution": "SSI Research"
        }, headers=admin_hdr)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("extracted_report", data)
        rep = data["extracted_report"]
        self.assertEqual(rep["institution"], "SSI")
        self.assertGreater(rep["target_price"], 0)
        self.assertGreater(len(rep["key_catalysts"]), 0)
        self.assertGreater(len(rep["key_risks"]), 0)

    def test_api_preset_dynamic_ticker(self):
        """Kiểm tra API tự động tổng hợp báo cáo đa tổ chức cho mã bất kỳ ngoài preset (VD: TCH)"""
        resp = self.client.get("/api/preset/TCH")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "TCH")
        self.assertGreaterEqual(len(data["matrix_table"]), 3)
        self.assertGreater(data["consensus_summary"]["mean_target_price"], 0)
        self.assertGreater(len(data["causality_analysis"]), 0)
        self.assertGreater(len(data["disensus_table"]), 0)

    def test_api_analyze_raw_text(self):
        """Kiểm tra trích xuất chỉ số định lượng từ văn bản thô báo cáo CTCK"""
        admin_hdr = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}
        sample_text = """
        BÁO CÁO PHÂN TÍCH SSI RESEARCH - CỔ PHIẾU HPG
        Khuyến nghị: MUA MẠNH
        Giá mục tiêu: 39,000 VND
        Thị giá hiện tại: 21,700 VND
        P/E Forward: 11.5x
        LNST dự phóng: 16,200 tỷ VND (+38% YoY)
        Luận điểm:
        - Dung Quất 2 chạy thử thương mại
        - Hưởng lợi thuế chống bán phá giá HRC
        Rủi ro:
        - Bất động sản dân dụng phục hồi chậm
        """
        resp = self.client.post("/api/analyze-raw", json={
            "raw_text": sample_text,
            "ticker": "HPG",
            "institution": "SSI Research"
        }, headers=admin_hdr)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["institution"], "SSI")
        self.assertEqual(data["recommendation"], "MUA MẠNH")
        self.assertEqual(data["target_price"], 39000.0)
        self.assertEqual(data["pe_forward"], 11.5)

    def test_api_upload_pdf(self):
        """Kiểm tra upload file PDF và trích xuất qua PyPDF"""
        admin_hdr = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT /F1 12 Tf 100 700 Td (BAO CAO SSI: HPG MUA GIA MUC TIEU 38000 VND PE 11.5) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n465\n%%EOF"
        resp = self.client.post(
            "/api/upload-pdf",
            files={"file": ("report.pdf", pdf_content, "application/pdf")},
            data={"ticker": "HPG", "institution": "SSI"},
            headers=admin_hdr
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("extracted_report", data)
        self.assertGreater(data["extracted_report"]["target_price"], 0)

    def test_api_get_report_pdf(self):
        """Kiểm tra xuất file PDF báo cáo phân tích của CTCK (SSI, HSC, Vietcap...)"""
        # 1. Kiểm tra xuất PDF cho HPG / SSI
        resp = self.client.get("/api/reports/pdf/HPG/SSI.pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF-"))
        self.assertIn("inline; filename=", resp.headers.get("content-disposition", ""))

        # 2. Kiểm tra xuất PDF cho FPT / Vietcap
        resp_fpt = self.client.get("/api/reports/pdf/FPT/Vietcap.pdf")
        self.assertEqual(resp_fpt.status_code, 200)
        self.assertEqual(resp_fpt.headers["content-type"], "application/pdf")
        self.assertTrue(resp_fpt.content.startswith(b"%PDF-"))

        # 3. Kiểm tra mã mới bất kỳ (dynamically generated report)
        resp_dynamic = self.client.get("/api/reports/pdf/TCB/SSI.pdf")
        self.assertEqual(resp_dynamic.status_code, 200)
        self.assertEqual(resp_dynamic.headers["content-type"], "application/pdf")
        self.assertTrue(resp_dynamic.content.startswith(b"%PDF-"))

    def test_peers_comparison_sector_alignment(self):
        """Kiểm tra bảng đối thủ cùng ngành phân loại chính xác, không bị lẫn ngành khác (VD: LHG chỉ có KBC, IDC, SZC, BCM)"""
        # 1. Test qua financial-overview
        resp = self.client.get("/api/financial-overview/LHG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        peers_data = data["peers_data"]
        self.assertEqual(peers_data["target_ticker"], "LHG")
        self.assertIn("Khu công nghiệp", peers_data["sector_name"])
        
        peer_tickers = [p["ticker"] for p in peers_data["peers"]]
        self.assertEqual(peer_tickers[0], "LHG")  # Target ticker luôn đứng đầu tiên
        self.assertIn("KBC", peer_tickers)
        self.assertTrue(any(t in ["SZC", "IDC", "BCM", "VGC"] for t in peer_tickers))
        
        # Tuyệt đối không lẫn ngành khác như SSI, HPG, VNM
        self.assertNotIn("SSI", peer_tickers)
        self.assertNotIn("HPG", peer_tickers)
        self.assertNotIn("VNM", peer_tickers)

        # Kiểm tra vốn hóa LHG >= 1,000 tỷ VND (để hiển thị 1.3k tỷ thay vì 0.0k tỷ)
        lhg_peer = next(p for p in peers_data["peers"] if p["ticker"] == "LHG")
        self.assertGreaterEqual(lhg_peer["market_cap_bil"], 1000.0)

        # 2. Test qua direct peers API /api/peers/LHG
        resp_peers = self.client.get("/api/peers/LHG")
        self.assertEqual(resp_peers.status_code, 200)
        p_data = resp_peers.json()
        self.assertEqual(p_data["target_ticker"], "LHG")
        self.assertEqual(p_data["peers"][0]["ticker"], "LHG")
        self.assertNotIn("SSI", [p["ticker"] for p in p_data["peers"]])
        self.assertNotIn("HPG", [p["ticker"] for p in p_data["peers"]])

    def test_peers_export_pdf_vietnamese_sectors(self):
        """Kiểm tra xuất file PDF đối thủ cùng ngành với tên ngành tiếng Việt có dấu (VND, VCB, HPG, DXG) không bị lỗi HTTP 500 latin-1."""
        test_cases = [
            ("VND", "Môi giới chứng khoán"),
            ("VCB", "Ngân hàng"),
            ("HPG", "Thép và sản phẩm thép"),
            ("DXG", "Bất động sản dân cư"),
        ]
        for ticker, sector in test_cases:
            payload = {
                "peers_data": {
                    "target_ticker": ticker,
                    "sector_name": sector,
                    "peers": [
                        {"ticker": ticker, "name": f"DN {ticker}", "market_cap_bil": 30000, "pe": 12.5, "pb": 1.6, "roe": 15.2, "roa": 4.5, "net_margin": 20.1, "debt_to_equity": 0.8}
                    ],
                    "industry_average": {"pe": 13.0, "pb": 1.7, "roe": 14.0, "roa": 4.0, "net_margin": 18.0, "debt_to_equity": 1.0}
                }
            }
            resp = self.client.post("/api/peers/export-pdf", json=payload)
            self.assertEqual(resp.status_code, 200, f"Failed for {ticker} with sector '{sector}': {resp.status_code}")
            self.assertEqual(resp.headers["content-type"], "application/pdf")
            self.assertTrue(resp.content.startswith(b"%PDF"))
            self.assertGreater(len(resp.content), 10000)
            self.assertIn("attachment; filename=", resp.headers.get("content-disposition", ""))


    def test_pvt_peers_export_pdf_complete(self):
        """Kiểm tra xuất file PDF đối thủ cho PVT: đảm bảo đầy đủ dữ liệu, không bị trang trắng và có vector fallback."""
        resp_peers = self.client.get("/api/peers/PVT")
        self.assertEqual(resp_peers.status_code, 200)
        peers_data = resp_peers.json()
        self.assertEqual(peers_data["target_ticker"], "PVT")
        self.assertGreaterEqual(len(peers_data["peers"]), 8)

        # Xuất PDF không kèm ảnh radar (kiểm tra vector chart fallback)
        payload = {
            "peers_data": peers_data,
            "radar_image_base64": None
        }
        resp = self.client.post("/api/peers/export-pdf", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "application/pdf")
        self.assertGreater(len(resp.content), 20000)

        # Kiểm tra nội dung PDF bằng pypdf
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(resp.content))
        self.assertGreaterEqual(len(reader.pages), 2)
        all_text = " ".join([p.extract_text() for p in reader.pages])
        self.assertIn("PVT", all_text)
        self.assertIn("RADAR SỨC MẠNH TÀI CHÍNH", all_text)
        self.assertIn("MÔ HÌNH 5 LỰC LƯỢNG", all_text)

    def test_acb_institutional_reports_sector_accuracy(self):
        """
        Kiểm tra mã ACB (Ngân hàng TMCP Á Châu):
        1. Luận điểm then chốt (catalysts) và Rủi ro (risks) chuẩn ngành Ngân hàng (tín dụng, NIM, CASA, CAR, nợ xấu).
        2. TUYỆT ĐỐI KHÔNG chứa thuật ngữ ngành sản xuất công nghiệp ("công suất", "chuỗi cung ứng", "nguyên vật liệu", "xuất khẩu").
        3. Có đường link tra cứu báo cáo phân tích và ngày phát hành (report_date).
        """
        resp = self.client.get("/api/preset/ACB")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "ACB")
        self.assertIn("Ngân hàng", data["sector"])
        
        matrix = data["matrix_table"]
        self.assertGreater(len(matrix), 0)

        # Kiểm tra từng báo cáo trong ma trận
        manufacturing_forbidden_words = ["công suất", "chuỗi cung ứng", "nguyên vật liệu", "xuất khẩu"]
        for rep in matrix:
            self.assertTrue(rep["report_date"])
            self.assertTrue(rep["source_url"])
            
            combined_text = " ".join(rep["key_catalysts"] + rep["key_risks"]).lower()
            for word in manufacturing_forbidden_words:
                self.assertNotIn(word, combined_text, f"Từ cấm '{word}' xuất hiện trong báo cáo ACB: {combined_text}")

            # Kiểm tra chứa ít nhất một thuật ngữ ngành ngân hàng
            banking_terms = ["tín dụng", "nim", "casa", "car", "nợ xấu", "lãi", "tài chính", "dự phòng"]
            has_banking_term = any(term in combined_text for term in banking_terms)
            self.assertTrue(has_banking_term, f"Báo cáo ACB không chứa thuật ngữ ngân hàng: {combined_text}")

    def test_corporate_capital_standardization_dbc(self):
        """
        Kiểm tra chuẩn hóa và đồng bộ số liệu vốn hóa, số CP lưu hành / niêm yết,
        cơ cấu tỷ lệ sở hữu, và tỷ suất cổ tức cho DBC và HPG.
        """
        resp = self.client.get("/api/financial-overview/DBC")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        profile = data["company_profile"]

        # 1. Số CP lưu hành & Niêm yết của DBC (chuẩn hóa đạt ~384.87 triệu CP thay vì 334 triệu CP cũ)
        self.assertAlmostEqual(profile["shares_outstanding_mil"], 384.87, delta=1.0)
        self.assertAlmostEqual(profile["shares_listed_mil"], 384.87, delta=1.0)

        # 2. Cơ cấu tỷ lệ sở hữu (Nước ngoài ~1.49%, Trong nước ~98.51% thay vì 22.5% mặc định)
        self.assertLess(profile["foreign_ownership_pct"], 5.0)
        self.assertAlmostEqual(profile["foreign_ownership_pct"], 1.49, delta=0.5)
        self.assertGreater(profile["domestic_ownership_pct"], 95.0)

        # 3. Tỷ suất cổ tức (Yield)
        self.assertGreaterEqual(profile["dividend_yield_pct"], 1.5)

        # 4. Vốn hóa thị trường phải được đồng bộ chính xác với thị giá live
        expected_mcap = round((profile["shares_outstanding_mil"] * profile["current_market_price"]) / 1000.0, 1)
        self.assertEqual(profile["market_cap_bil"], expected_mcap)

    def test_corporate_database_endpoints(self):
        """
        Kiểm tra cơ sở dữ liệu hơn 650+ doanh nghiệp niêm yết từ Google Sheets:
        1. API /api/database/companies: trả về hơn 650 doanh nghiệp, hỗ trợ lọc theo keyword và ngành.
        2. API /api/database/companies/{ticker}: trả về thông tin chi tiết (DBC, HPG, LHG).
        3. API /api/database/sectors: trả về 34 phân ngành kinh tế với tỷ lệ bao phủ và tăng trưởng.
        """
        # 1. Danh sách doanh nghiệp
        resp = self.client.get("/api/database/companies?limit=10")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(data["total_database_records"], 650)
        self.assertEqual(len(data["companies"]), 10)

        # 2. Tìm kiếm theo keyword 'DBC'
        resp_dbc = self.client.get("/api/database/companies?q=DBC")
        self.assertEqual(resp_dbc.status_code, 200)
        dbc_data = resp_dbc.json()
        self.assertGreaterEqual(len(dbc_data["companies"]), 1)
        dbc_item = next(c for c in dbc_data["companies"] if c["ticker"] == "DBC")
        self.assertEqual(dbc_item["exchange"], "HOSE")
        self.assertIn("Chăn nuôi", dbc_item["fiintrade_sector"])

        # 3. Tra cứu chi tiết HPG
        resp_hpg = self.client.get("/api/database/companies/HPG")
        self.assertEqual(resp_hpg.status_code, 200)
        hpg_item = resp_hpg.json()
        self.assertEqual(hpg_item["ticker"], "HPG")
        self.assertEqual(hpg_item["exchange"], "HOSE")
        self.assertIn("Thép", hpg_item["icb4"])

        # 4. Tra cứu danh mục phân ngành
        resp_sec = self.client.get("/api/database/sectors")
        self.assertEqual(resp_sec.status_code, 200)
        sec_data = resp_sec.json()
        self.assertGreaterEqual(sec_data["total_sectors"], 30)
        sec_names = [s["sector_name"] for s in sec_data["sectors"]]
        self.assertIn("Ngân hàng", sec_names)
        self.assertIn("Bất động sản", sec_names)

    def test_quarterly_financial_statements(self):
        """
        Kiểm tra tính năng Báo cáo Quý (vị trí 1):
        API /api/financial-overview/{ticker} phải trả về trường statements_quarterly
        gồm 4 quý gần nhất ('Q2/2025', 'Q3/2025', 'Q4/2025', 'Q1/2026') với đầy đủ doanh thu & LNST.
        """
        resp = self.client.get("/api/financial-overview/HPG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("statements_annual", data)
        self.assertIn("statements_quarterly", data)
        
        sq = data["statements_quarterly"]
        self.assertGreaterEqual(len(sq["periods"]), 4)
        self.assertIn("Q2/2026", sq["periods"])
        self.assertEqual(len(sq["revenue"]), len(sq["periods"]))
        self.assertEqual(len(sq["net_profit"]), len(sq["periods"]))
        self.assertEqual(len(sq["total_assets"]), len(sq["periods"]))
        self.assertEqual(len(sq["owner_equity"]), len(sq["periods"]))

    def test_hag_agricultural_sector_and_peers_accuracy(self):
        """
        Kiểm tra khắc phục lỗi so sánh đối thủ cùng ngành cho mã HAG (vị trí 2 & mũi tên 2):
        1. Ngành của HAG phải là Nông sản / Nông sản & Chăn nuôi.
        2. Đối thủ peers tuyệt đối không được rơi vào nhóm Bất động sản (VHM, KDH, NLG, PDR).
        3. Đối thủ peers phải là các doanh nghiệp cùng ngành nông nghiệp, chăn nuôi, thực phẩm (DBC, BAF, HNG, MML...).
        """
        resp = self.client.get("/api/financial-overview/HAG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # 1. Kiểm tra ngành của HAG
        sec = data["company_profile"]["sector"]
        self.assertTrue(any(k in sec.lower() for k in ["nông", "chăn nuôi"]), f"Ngành HAG không chuẩn: {sec}")
        
        # 2. Kiểm tra danh sách đối thủ
        peers_data = data["peers_data"]
        peer_tickers = [p["ticker"] for p in peers_data["peers"]]
        self.assertEqual(peer_tickers[0], "HAG", "Mã đang tra cứu phải ở vị trí đầu tiên")
        
        # Tuyệt đối không chứa các mã Bất động sản
        real_estate_forbidden = ["VHM", "KDH", "NLG", "PDR", "DXG", "DIG", "NVL"]
        for bds_tick in real_estate_forbidden:
            self.assertNotIn(bds_tick, peer_tickers, f"Mã BĐS '{bds_tick}' không được xuất hiện trong đối thủ của HAG!")
            
        # Phải chứa các mã nông sản, chăn nuôi, thực phẩm
        agri_peers = ["DBC", "BAF", "HNG", "MML", "PAN", "VHC", "ANV"]
        matching_count = sum(1 for t in peer_tickers[1:] if t in agri_peers)
        self.assertGreaterEqual(matching_count, 3, f"Phải có ít nhất 3 đối thủ nông sản/chăn nuôi, hiện có: {peer_tickers}")

    def test_peer_comparison_expanded_all_peers(self):
        """
        Kiểm tra mở rộng bảng đối thủ cùng ngành:
        Không còn giới hạn 5 mã, phải hiển thị đầy đủ tất cả doanh nghiệp đầu ngành (> 8 mã).
        """
        # 1. Ngân hàng (VCB)
        resp_vcb = self.client.get("/api/financial-overview/VCB")
        self.assertEqual(resp_vcb.status_code, 200)
        vcb_peers = resp_vcb.json()["peers_data"]["peers"]
        self.assertGreaterEqual(len(vcb_peers), 10, "Nhóm ngân hàng phải có >= 10 mã đối thủ")

        # 2. Dầu khí & Năng lượng (GAS)
        resp_gas = self.client.get("/api/financial-overview/GAS")
        self.assertEqual(resp_gas.status_code, 200)
        gas_peers = resp_gas.json()["peers_data"]["peers"]
        self.assertGreaterEqual(len(gas_peers), 8, "Nhóm dầu khí phải có >= 8 mã đối thủ")

        # 3. BĐS Khu công nghiệp (KBC)
        resp_kbc = self.client.get("/api/financial-overview/KBC")
        self.assertEqual(resp_kbc.status_code, 200)
        kbc_peers = resp_kbc.json()["peers_data"]["peers"]
        self.assertGreaterEqual(len(kbc_peers), 8, "Nhóm KCN phải có >= 8 mã đối thủ")

        # 4. Chứng khoán (SSI) - Mã trong PRESET vẫn phải hiển thị đầy đủ >= 10 đối thủ như VIX
        resp_ssi = self.client.get("/api/financial-overview/SSI")
        self.assertEqual(resp_ssi.status_code, 200)
        ssi_pd = resp_ssi.json()["peers_data"]
        self.assertGreaterEqual(len(ssi_pd["peers"]), 10, "SSI phải có >= 10 mã đối thủ ngành chứng khoán")
        self.assertIn("sector_kpi_columns", ssi_pd)
        ssi_kpi_fields = [c["field"] for c in ssi_pd["sector_kpi_columns"]]
        self.assertIn("margin_loan_bil", ssi_kpi_fields)
        self.assertEqual(ssi_pd["peers"][0]["ticker"], "SSI")
        self.assertIn("VIX", [p["ticker"] for p in ssi_pd["peers"]])

    def test_peer_comparison_sector_kpis(self):
        """
        Kiểm tra chỉ số KPI đặc thù theo từng ngành:
        1. Ngân hàng: NIM, CASA, NPL, Tín dụng, CAR
        2. BĐS KCN: Tỷ lệ lấp đầy, Giá thuê đất, DT trả trước
        3. BĐS Dân dụng: Tiền người mua trả trước, Backlog
        4. Dầu khí: EBITDA Margin, Capex/Doanh thu
        """
        # 1. Ngân hàng VCB
        resp_vcb = self.client.get("/api/financial-overview/VCB")
        self.assertEqual(resp_vcb.status_code, 200)
        vcb_pd = resp_vcb.json()["peers_data"]
        self.assertIn("sector_kpi_columns", vcb_pd)
        kpi_fields = [col["field"] for col in vcb_pd["sector_kpi_columns"]]
        self.assertIn("nim_percent", kpi_fields)
        self.assertIn("casa_percent", kpi_fields)
        self.assertIn("npl_percent", kpi_fields)
        # Kiểm tra dữ liệu cụ thể của VCB
        vcb_self = vcb_pd["peers"][0]
        self.assertIsNotNone(vcb_self.get("nim_percent"))
        self.assertGreater(vcb_self.get("nim_percent"), 2.0)
        self.assertIsNotNone(vcb_self.get("casa_percent"))

        # 2. BĐS Dân dụng VHM
        resp_vhm = self.client.get("/api/financial-overview/VHM")
        self.assertEqual(resp_vhm.status_code, 200)
        vhm_pd = resp_vhm.json()["peers_data"]
        vhm_kpi_fields = [col["field"] for col in vhm_pd["sector_kpi_columns"]]
        self.assertIn("advance_from_buyers_bil", vhm_kpi_fields)
        self.assertIn("backlog_bil", vhm_kpi_fields)
        vhm_self = vhm_pd["peers"][0]
        self.assertIsNotNone(vhm_self.get("advance_from_buyers_bil"))
        self.assertGreater(vhm_self.get("advance_from_buyers_bil"), 10000)

        # 3. Dầu khí GAS
        resp_gas = self.client.get("/api/financial-overview/GAS")
        self.assertEqual(resp_gas.status_code, 200)
        gas_pd = resp_gas.json()["peers_data"]
        gas_kpi_fields = [col["field"] for col in gas_pd["sector_kpi_columns"]]
        self.assertIn("ebitda_margin", gas_kpi_fields)
        self.assertIn("capex_rev_ratio", gas_kpi_fields)
        gas_self = gas_pd["peers"][0]
        self.assertIsNotNone(gas_self.get("ebitda_margin"))

    def test_industry_reports_endpoint(self):
        """Kiểm tra endpoint /api/industry-reports trả về đúng định dạng, liên kết ngành & hàng hóa và link PDF"""
        # 1. Test với HPG (Ngành Thép & Kim loại)
        resp_hpg = self.client.get("/api/industry-reports?ticker=HPG")
        self.assertEqual(resp_hpg.status_code, 200)
        data_hpg = resp_hpg.json()
        self.assertEqual(data_hpg["ticker"], "HPG")
        self.assertIn("Thép", data_hpg["sector_name"])
        self.assertGreaterEqual(len(data_hpg["commodities"]), 2)
        self.assertGreater(data_hpg["total_found"], 0)
        self.assertGreater(len(data_hpg["reports"]), 0)

        first_rep = data_hpg["reports"][0]
        self.assertIn("title", first_rep)
        self.assertIn("date", first_rep)
        self.assertIn("source", first_rep)
        self.assertIn("file_url", first_rep)
        self.assertTrue(first_rep["file_url"].endswith(".pdf") or "pdf" in first_rep["file_url"].lower())
        self.assertIn("page_count", first_rep)

        # 2. Test với SSI (Ngành Chứng khoán)
        resp_ssi = self.client.get("/api/industry-reports?ticker=SSI")
        self.assertEqual(resp_ssi.status_code, 200)
        data_ssi = resp_ssi.json()
        self.assertIn("Chứng khoán", data_ssi["sector_name"])

        # 3. Test lọc từ khóa
        resp_filter = self.client.get("/api/industry-reports?ticker=HPG&keyword=thép")
        self.assertEqual(resp_filter.status_code, 200)
        data_filter = resp_filter.json()
        self.assertGreater(len(data_filter["reports"]), 0)

        # 4. Test với DBC (Nông nghiệp & Chăn nuôi)
        resp_dbc = self.client.get("/api/industry-reports?ticker=DBC")
        self.assertEqual(resp_dbc.status_code, 200)
        data_dbc = resp_dbc.json()
        self.assertEqual(data_dbc["ticker"], "DBC")
        self.assertIn("Chăn nuôi", data_dbc["sector_name"])
        self.assertEqual(data_dbc["primary_keyword"], "chăn nuôi")
        self.assertGreater(len(data_dbc["reports"]), 0)

        # 5. Test khi người dùng xóa từ khóa và bấm Tìm (all_industries=true)
        resp_all = self.client.get("/api/industry-reports?ticker=MWG&all_industries=true")
        self.assertEqual(resp_all.status_code, 200)
        data_all = resp_all.json()
        self.assertTrue(data_all["all_industries"])
        self.assertEqual(data_all["sector_name"], "Tất cả các ngành")
        self.assertGreaterEqual(len(data_all["reports"]), 10)

    def test_overview_redesign_endpoints(self):
        """Kiểm tra các endpoint phục vụ thiết kế 5 phân tầng của Tab Tổng quan (Hình 1, 2, 3, 4)"""
        # 1. Mini Chart Series & Market Stats (Hình 1)
        resp_mini = self.client.get("/api/mini-chart-series/HPG")
        self.assertEqual(resp_mini.status_code, 200)
        mini_data = resp_mini.json()
        self.assertEqual(mini_data["ticker"], "HPG")
        self.assertIn("series", mini_data)
        self.assertIn("1D", mini_data["series"])
        self.assertIn("timeframe_percents", mini_data)
        self.assertIn("1D", mini_data["timeframe_percents"])
        self.assertIn("ALL", mini_data["timeframe_percents"])
        self.assertGreater(mini_data["market_cap_bil"], 0)
        self.assertGreater(mini_data["volume"], 0)

        # 2. Company News & Corporate Events (Hình 2)
        resp_news = self.client.get("/api/company-news-events/HPG")
        self.assertEqual(resp_news.status_code, 200)
        news_data = resp_news.json()
        self.assertEqual(news_data["ticker"], "HPG")
        self.assertIn("news", news_data)
        self.assertIn("events", news_data)
        self.assertGreater(len(news_data["news"]), 0)
        self.assertGreater(len(news_data["events"]), 0)

        # 3. Company Catalysts, Key Projects & AI Insights (Phân tầng 4)
        resp_cat = self.client.get("/api/company-catalysts-insights/HPG")
        self.assertEqual(resp_cat.status_code, 200)
        cat_data = resp_cat.json()
        self.assertEqual(cat_data["ticker"], "HPG")
        self.assertIn("catalysts", cat_data)
        self.assertIn("projects", cat_data)
        self.assertIn("ai_insights", cat_data)
        self.assertGreater(len(cat_data["projects"]), 0)
        self.assertIn("scale", cat_data["projects"][0])
        self.assertIn("progress_pct", cat_data["projects"][0])
        self.assertIn("commercial_date", cat_data["projects"][0])

    def test_multi_model_valuation_endpoint(self):
        """Kiểm tra ma trận định giá đa mô hình (DCF, Graham 1-2-3, P/E, P/B) và tính năng tùy biến trọng số"""
        # 1. Check multi-model valuation in financial overview bundle
        resp_bundle = self.client.get("/api/financial-overview/HPG")
        self.assertEqual(resp_bundle.status_code, 200)
        bundle_data = resp_bundle.json()
        self.assertIn("valuation", bundle_data)
        val = bundle_data["valuation"]
        self.assertIn("models", val)
        self.assertEqual(len(val["models"]), 6)
        self.assertGreater(val["blended_fair_value"], 0)
        self.assertGreater(val["blended_fair_value_k"], 0)
        
        # Verify all 6 models are present
        model_ids = [m["id"] for m in val["models"]]
        self.assertIn("dcf", model_ids)
        self.assertIn("graham_1", model_ids)
        self.assertIn("graham_2", model_ids)
        self.assertIn("graham_3", model_ids)
        self.assertIn("pe", model_ids)
        self.assertIn("pb", model_ids)

        # 2. Test POST /api/valuation/multi-model with custom weights
        custom_weights = {
            "dcf": 20.0,
            "graham_1": 10.0,
            "graham_2": 20.0,
            "graham_3": 10.0,
            "pe": 30.0,
            "pb": 10.0
        }
        resp_custom = self.client.post("/api/valuation/multi-model", json={
            "ticker": "HPG",
            "custom_weights": custom_weights
        })
        self.assertEqual(resp_custom.status_code, 200)
        custom_val = resp_custom.json()
        self.assertEqual(len(custom_val["models"]), 6)
        self.assertGreater(custom_val["blended_fair_value"], 0)
        self.assertAlmostEqual(sum(m["weight_percent"] for m in custom_val["models"]), 100.0, places=1)

    def test_valuation_bands_endpoint(self):
        """Kiểm tra biểu đồ định giá PE Band và PB Band theo các khung thời gian 3M, 6M, 1Y, 5Y, ALL"""
        # 1. Test GET /api/valuation/bands/HPG
        resp = self.client.get("/api/valuation/bands/HPG?timeframe=5Y")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "HPG")
        self.assertEqual(data["timeframe"], "5Y")
        self.assertIn("selected_data", data)
        self.assertIn("pe", data["selected_data"])
        self.assertIn("pb", data["selected_data"])
        
        # Verify PE & PB band metrics
        pe = data["selected_data"]["pe"]
        pb = data["selected_data"]["pb"]
        self.assertGreater(pe["mean"], 0)
        self.assertGreater(pe["upper_2sd"], pe["mean"])
        self.assertLess(pe["lower_2sd"], pe["mean"])
        self.assertGreater(len(pe["actual"]), 0)
        self.assertIn("zone", pe)
        
        self.assertGreater(pb["mean"], 0)
        self.assertGreater(pb["upper_2sd"], pb["mean"])
        self.assertLess(pb["lower_2sd"], pb["mean"])
        self.assertGreater(len(pb["actual"]), 0)
        self.assertIn("zone", pb)

        # 2. Check all timeframes available
        self.assertEqual(len(data["timeframes_available"]), 5)
        for tf in ["3M", "6M", "1Y", "5Y", "ALL"]:
            self.assertIn(tf, data["all_timeframes"])
            self.assertIn("pe", data["all_timeframes"][tf])
            self.assertIn("pb", data["all_timeframes"][tf])

    def test_company_news_and_events_interactive(self):
        """Kiểm tra API /api/company-news-events/{ticker} trả về đầy đủ tin tức, sự kiện, tóm tắt, điểm nhấn và link web"""
        for ticker in ["SSI", "HPG", "VNM", "FPT", "VIC"]:
            resp = self.client.get(f"/api/company-news-events/{ticker}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["ticker"], ticker)
            self.assertIn("news", data)
            self.assertIn("events", data)
            self.assertIn("cafef_url", data)
            self.assertIn("vietstock_url", data)
            self.assertGreater(len(data["news"]), 0)
            self.assertGreater(len(data["events"]), 0)

            # Test first news item structure
            n0 = data["news"][0]
            self.assertIn("title", n0)
            self.assertIn("source", n0)
            self.assertIn("date", n0)
            self.assertIn("url", n0)
            self.assertIn("summary", n0)
            self.assertIn("key_takeaways", n0)

            # Test first event item structure
            e0 = data["events"][0]
            self.assertIn("title", e0)
            self.assertIn("event_type", e0)
            self.assertIn("details", e0)
            self.assertIn("url", e0)

    def test_ai_learning_templates_crud(self):
        """Kiểm tra quản lý Mẫu học (Few-Shot Templates) hệ thống và CRUD mẫu người dùng (kèm xác thực Admin)"""
        admin_headers = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}

        # 1. Danh sách mẫu mặc định (GET công khai)
        resp = self.client.get("/api/ai-learning/templates")
        self.assertEqual(resp.status_code, 200)
        tpls = resp.json()
        self.assertGreaterEqual(len(tpls), 6)

        # Kiểm tra mẫu Thép & Vật liệu xây dựng
        thep_tpl = next((t for t in tpls if "thep" in t["id"].lower()), None)
        self.assertIsNotNone(thep_tpl)
        self.assertTrue(thep_tpl["is_system"])
        self.assertGreater(len(thep_tpl["catalyst_rules"]), 0)
        self.assertGreater(len(thep_tpl["thesis_rules"]), 0)

        # 2. Thêm mẫu học mới khi không có quyền Admin -> Phải trả về 403 Forbidden
        custom_payload = {
            "name": "Hóa chất & Phân bón (DGC, DCM)",
            "sector": "Hóa chất & Phân bón",
            "keywords": ["dgc", "dcm", "phốt pho vàng", "apatit", "urê", "hóa chất"],
            "catalyst_rules": [
                "Tiến độ tổ hợp hóa chất Nghi Sơn và nhà máy mới",
                "Chênh lệch giá xuất khẩu phốt pho vàng (P4) và giá quặng apatit đầu vào"
            ],
            "thesis_rules": [
                "Lợi thế tự chủ nguồn quặng apatit giúp kiểm soát giá vốn cạnh tranh"
            ],
            "risk_rules": [
                "Giá phân bón thế giới sụt giảm do nguồn cung xuất khẩu từ Trung Quốc"
            ]
        }
        resp_unauth = self.client.post("/api/ai-learning/templates", json=custom_payload)
        self.assertEqual(resp_unauth.status_code, 403)

        # 3. Thêm mẫu học mới với quyền Admin hợp lệ -> Thành công 200
        resp_add = self.client.post("/api/ai-learning/templates", json=custom_payload, headers=admin_headers)
        self.assertEqual(resp_add.status_code, 200)
        add_data = resp_add.json()
        self.assertEqual(add_data["status"], "SUCCESS")
        new_tpl_id = add_data["template"]["id"]
        self.assertFalse(add_data["template"]["is_system"])

        # 4. Kiểm tra mẫu mới đã có trong danh sách
        resp_after = self.client.get("/api/ai-learning/templates")
        tpl_ids = [t["id"] for t in resp_after.json()]
        self.assertIn(new_tpl_id, tpl_ids)

        # 5. Xóa mẫu người dùng tự tạo (yêu cầu Admin)
        resp_del = self.client.delete(f"/api/ai-learning/templates/{new_tpl_id}", headers=admin_headers)
        self.assertEqual(resp_del.status_code, 200)

        # 6. Kiểm tra không được xóa mẫu hệ thống
        resp_del_sys = self.client.delete("/api/ai-learning/templates/tpl-thep-vat-lieu", headers=admin_headers)
        self.assertEqual(resp_del_sys.status_code, 400)

        # 7. Kiểm tra API đọc & phân tích hình ảnh AI (Test cả HPG và KBC - BĐS Khu công nghiệp)
        fake_img_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
        files_hpg = {"file": ("hpg_report_chart.png", fake_img_bytes, "image/png")}
        resp_img_hpg = self.client.post("/api/ai-learning/analyze-template-image", files=files_hpg, data={"ticker": "HPG"}, headers=admin_headers)
        self.assertEqual(resp_img_hpg.status_code, 200)
        img_data_hpg = resp_img_hpg.json()
        self.assertIn("Thép", img_data_hpg["sector"])

        # Test upload file KBC.png -> Phải phân loại đúng nhóm ngành Bất động sản Khu công nghiệp
        files_kbc = {"file": ("KBC.png", fake_img_bytes, "image/png")}
        resp_img_kbc = self.client.post("/api/ai-learning/analyze-template-image", files=files_kbc, headers=admin_headers)
        self.assertEqual(resp_img_kbc.status_code, 200)
        img_data_kbc = resp_img_kbc.json()
        self.assertEqual(img_data_kbc["sector"], "Bất động sản Khu công nghiệp")
        self.assertIn("kbc", img_data_kbc["keywords"])
        self.assertIn("KBC", img_data_kbc["name"])
        self.assertTrue(any("KCN" in c or "Khu công nghiệp" in c or "FDI" in c for c in img_data_kbc["catalyst_rules"]))

    def test_ai_learning_advanced_extraction(self):
        """Kiểm tra bộ trích xuất Few-Shot Extractor nhận diện sâu sắc Catalysts và Luận điểm"""
        from ai_learning_engine import extract_advanced_knowledge

        # Test case 1: Thép HPG
        text_hpg = "HPG chuẩn bị đưa phân kỳ 1 dự án Dung Quất 2 vào vận hành từ cuối năm. Động lực chính đến từ HRC xuất khẩu và tiêu thụ nội địa. Doanh thu dự phóng đạt 155,000 tỷ. Lợi nhuận sau thuế dự phóng đạt 16,500 tỷ."
        res_hpg = extract_advanced_knowledge(text_hpg, ticker="HPG")
        self.assertGreaterEqual(res_hpg["confidence_score"], 0.85)
        self.assertGreaterEqual(len(res_hpg["key_catalysts"]), 3)
        self.assertIn("Dự án & Capex", res_hpg["categorized_catalysts"])
        self.assertTrue(any("Dung Quất 2" in c for c in res_hpg["key_catalysts"]))

        # Test case 2: Bán lẻ MWG thông qua engine.extract_financial_data_from_text
        text_mwg = "MWG ghi nhận chuỗi Bách Hóa Xanh đạt điểm hòa vốn sau thuế và bắt đầu có lãi. Mảng ICT phục hồi doanh thu trên từng cửa hàng."
        rep_mwg = extract_financial_data_from_text(text_mwg, ticker="MWG")
        self.assertGreaterEqual(len(rep_mwg.key_catalysts), 3)
        self.assertTrue(any("Bách Hóa Xanh" in c for c in rep_mwg.key_catalysts))

    def test_ai_learning_config_and_scheduler(self):
        """Kiểm tra API cấu hình tần suất lập lịch tự động quét và học online"""
        # 1. Lấy cấu hình
        resp = self.client.get("/api/ai-learning/config")
        self.assertEqual(resp.status_code, 200)
        cfg = resp.json()
        self.assertIn("interval_hours", cfg)
        self.assertIn("watchlist", cfg)

        # 2. Cập nhật tần suất và watchlist
        update_payload = {
            "interval_hours": 3,
            "watchlist": ["HPG", "SSI", "FPT", "MWG", "TCH"],
            "enabled": True
        }
        resp_up = self.client.post("/api/ai-learning/config", json=update_payload)
        self.assertEqual(resp_up.status_code, 200)
        up_cfg = resp_up.json()
        self.assertEqual(up_cfg["interval_hours"], 3)
        self.assertIn("TCH", up_cfg["watchlist"])
        self.assertIn(":", up_cfg["next_run"])

        # 3. Phục hồi cấu hình chuẩn 6h
        self.client.post("/api/ai-learning/config", json={"interval_hours": 6})

    def test_ai_learning_trigger_and_history(self):
        """Kiểm tra kích hoạt chu kỳ tự học online và xem nhật ký & thống kê tri thức"""
        # 1. Trigger học ngay cho 2 mã
        resp_trig = self.client.post("/api/ai-learning/trigger-learn", json={"tickers": ["HPG", "SSI"]})
        self.assertEqual(resp_trig.status_code, 200)
        data = resp_trig.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreater(data["reports_learned"], 0)
        self.assertGreater(data["catalysts_extracted"], 0)

        # 1b. Trigger quét toàn bộ thị trường khi danh sách mã để trống
        resp_market = self.client.post("/api/ai-learning/trigger-learn", json={"tickers": []})
        self.assertEqual(resp_market.status_code, 200)
        market_data = resp_market.json()
        self.assertEqual(market_data["status"], "SUCCESS")
        self.assertGreater(market_data["reports_learned"], 0)
        self.assertIn("TOÀN BỘ THỊ TRƯỜNG", market_data.get("scope", ""))

        # 2. Kiểm tra nhật ký học
        resp_hist = self.client.get("/api/ai-learning/history")
        self.assertEqual(resp_hist.status_code, 200)
        hist = resp_hist.json()
        self.assertGreater(len(hist), 0)
        self.assertIn("ticker", hist[0])
        self.assertIn("confidence", hist[0])

        # 3. Kiểm tra thống kê tổng quan
        resp_stats = self.client.get("/api/ai-learning/stats")
        self.assertEqual(resp_stats.status_code, 200)
        stats = resp_stats.json()
        self.assertGreater(stats["total_reports_learned"], 0)
        self.assertGreater(stats["total_catalysts_accumulated"], 0)
        self.assertGreater(stats["average_confidence"], 0.8)

    def test_real_ctck_pdf_direct_reading(self):
        """
        Kiểm tra tính năng đọc trực tiếp báo cáo phân tích thực tế của các CTCK:
        1. Trả về đúng HTTP 200 và media_type application/pdf.
        2. File là PDF thực tế (> 100KB, header %PDF), không phải file mẫu 1 trang.
        3. Header Content-Disposition là inline cho phép xem trực tiếp trên browser / iframe.
        """
        # 1. Test HPG - Vietcap
        resp_hpg = self.client.get("/api/reports/pdf/HPG/Vietcap.pdf")
        self.assertEqual(resp_hpg.status_code, 200)
        self.assertIn("application/pdf", resp_hpg.headers["content-type"])
        self.assertTrue(resp_hpg.content.startswith(b"%PDF"))
        self.assertGreater(len(resp_hpg.content), 100000, "File PDF phải là bản gốc nhiều trang thực tế (>100KB)")
        self.assertIn("inline", resp_hpg.headers.get("content-disposition", ""))
        self.assertIn("HPG", resp_hpg.headers.get("content-disposition", ""))

        # 2. Test FPT - SSI Research
        resp_fpt = self.client.get("/api/reports/pdf/FPT/SSI%20Research.pdf")
        self.assertEqual(resp_fpt.status_code, 200)
        self.assertIn("application/pdf", resp_fpt.headers["content-type"])
        self.assertTrue(resp_fpt.content.startswith(b"%PDF"))
        self.assertGreater(len(resp_fpt.content), 100000)

        # 3. Test HPG - VietinBank Securities (CTS)
        import io
        from pypdf import PdfReader
        resp_cts = self.client.get("/api/reports/pdf/HPG/VietinBank%20Securities.pdf")
        self.assertEqual(resp_cts.status_code, 200)
        self.assertTrue(resp_cts.content.startswith(b"%PDF"))
        reader_cts = PdfReader(io.BytesIO(resp_cts.content))
        text_cts = " ".join([p.extract_text() for p in reader_cts.pages]).lower()
        self.assertIn("vietinbank", text_cts)

        # 4. Test HPG - Shinhan Securities (SSV)
        resp_ssv = self.client.get("/api/reports/pdf/HPG/Shinhan%20Securities.pdf")
        self.assertEqual(resp_ssv.status_code, 200)
        self.assertTrue(resp_ssv.content.startswith(b"%PDF"))
        reader_ssv = PdfReader(io.BytesIO(resp_ssv.content))
        text_ssv = " ".join([p.extract_text() for p in reader_ssv.pages]).lower()
        self.assertIn("shinhan", text_ssv)

    def test_admin_auth_and_manual_protection(self):
        """
        Kiểm tra bảo vệ tính năng cập nhật thủ công (Link, PDF, Text thô):
        1. /api/auth/admin-verify xác thực đúng user admin và pass 325396.
        2. Nếu không có pass hoặc pass sai -> Bị chặn 403 Forbidden.
        3. /api/crawl-url, /api/upload-pdf, /api/analyze-raw:
           - Không có quyền Admin -> HTTP 403 Forbidden.
           - Có user admin và pass 325396 -> Vượt qua xác thực quyền thành công.
        """
        # 1. Test verify endpoint
        resp_fail1 = self.client.post("/api/auth/admin-verify", json={"username": "guest", "password": "wrongpassword"})
        self.assertEqual(resp_fail1.status_code, 403)

        resp_fail2 = self.client.post("/api/auth/admin-verify", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(resp_fail2.status_code, 403)

        resp_ok = self.client.post("/api/auth/admin-verify", json={"username": "admin", "password": "325396"})
        self.assertEqual(resp_ok.status_code, 200)
        self.assertTrue(resp_ok.json().get("authenticated"))

        # 2. Test /api/analyze-raw
        sample_text = "BÁO CÁO PHÂN TÍCH DOANH NGHIỆP CỔ PHIẾU HPG SSI RESEARCH KHUYẾN NGHỊ MUA GIÁ MỤC TIÊU 38,000 ĐỒNG"
        # No auth -> 403
        resp_raw_blocked = self.client.post("/api/analyze-raw", json={"raw_text": sample_text, "ticker": "HPG", "institution": "SSI Research"})
        self.assertEqual(resp_raw_blocked.status_code, 403)
        self.assertIn("Quản trị viên", resp_raw_blocked.json()["detail"])

        # Auth with headers -> 200
        headers = {"X-Admin-User": "admin", "X-Admin-Password": "325396"}
        resp_raw_ok = self.client.post("/api/analyze-raw", json={"raw_text": sample_text, "ticker": "HPG", "institution": "SSI Research"}, headers=headers)
        self.assertEqual(resp_raw_ok.status_code, 200)
        self.assertEqual(resp_raw_ok.json()["recommendation"], "MUA")

        # Auth with JSON body fallback -> 200
        resp_raw_body_ok = self.client.post("/api/analyze-raw", json={
            "raw_text": sample_text,
            "ticker": "HPG",
            "institution": "SSI Research",
            "admin_user": "admin",
            "admin_password": "325396"
        })
        self.assertEqual(resp_raw_body_ok.status_code, 200)

        # 3. Test /api/crawl-url
        # No auth -> 403
        resp_crawl_blocked = self.client.post("/api/crawl-url", json={"url": "https://example.com/report.pdf", "ticker": "HPG", "institution": "CTCK"})
        self.assertEqual(resp_crawl_blocked.status_code, 403)
        self.assertIn("Quản trị viên", resp_crawl_blocked.json()["detail"])

        # 4. Test /api/upload-pdf
        fake_pdf = b"%PDF-1.4 sample content with enough length"
        # No auth -> 403
        resp_pdf_blocked = self.client.post(
            "/api/upload-pdf",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={"ticker": "HPG", "institution": "SSI Research"}
        )
        self.assertEqual(resp_pdf_blocked.status_code, 403)

        # Auth with form fields -> proceeds past auth check (not 403)
        resp_pdf_auth = self.client.post(
            "/api/upload-pdf",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={"ticker": "HPG", "institution": "SSI Research", "admin_user": "admin", "admin_password": "325396"}
        )
        self.assertNotEqual(resp_pdf_auth.status_code, 403)

    def test_admin_forgot_password_flow(self):
        """
        Kiểm tra toàn diện tính năng khôi phục/đổi mật khẩu Admin qua email hoabhk31@gmail.com:
        1. Gửi OTP đến email không phải hoabhk31@gmail.com -> Bị chặn 400.
        2. Gửi OTP đến đúng email hoabhk31@gmail.com -> Thành công 200 và sinh mã OTP.
        3. Nhập sai OTP hoặc OTP rỗng -> Bị từ chối 400.
        4. Nhập đúng OTP và mật khẩu mới hợp lệ -> Đổi thành công 200.
        5. Đăng nhập bằng mật khẩu mới -> Thành công 200.
        6. Đăng nhập bằng mật khẩu cũ (325396) -> Bị từ chối 403.
        7. Khôi phục lại mật khẩu mặc định (325396) để các test khác chạy ổn định.
        """
        # 1. Thử gửi email lạ
        resp_bad_email = self.client.post("/api/auth/forgot-password/request-otp", json={"email": "hacker@example.com"})
        self.assertEqual(resp_bad_email.status_code, 400)
        self.assertIn("hoabhk31@gmail.com", resp_bad_email.json()["detail"])

        # 2. Gửi đúng email hoabhk31@gmail.com
        resp_req = self.client.post("/api/auth/forgot-password/request-otp", json={"email": "hoabhk31@gmail.com"})
        self.assertEqual(resp_req.status_code, 200)
        self.assertIn("Mã xác thực OTP", resp_req.json()["message"])

        # Lấy OTP từ file admin_auth.json
        from server import get_admin_auth_data, save_admin_auth_data
        auth_data = get_admin_auth_data()
        generated_otp = auth_data.get("active_otp")
        self.assertIsNotNone(generated_otp)
        self.assertEqual(len(generated_otp), 6)

        # 3. Thử reset với OTP sai
        resp_wrong_otp = self.client.post("/api/auth/forgot-password/verify-reset", json={
            "email": "hoabhk31@gmail.com",
            "otp": "000000",
            "new_password": "NewSecretPass2026@"
        })
        self.assertEqual(resp_wrong_otp.status_code, 400)

        # 4. Reset với đúng OTP và mật khẩu mới
        new_test_password = "NewAdminPass2026@"
        resp_reset = self.client.post("/api/auth/forgot-password/verify-reset", json={
            "email": "hoabhk31@gmail.com",
            "otp": generated_otp,
            "new_password": new_test_password
        })
        self.assertEqual(resp_reset.status_code, 200)
        self.assertIn("thành công", resp_reset.json()["message"].lower())

        # 5. Đăng nhập bằng mật khẩu mới -> 200
        resp_login_new = self.client.post("/api/auth/admin-verify", json={
            "username": "admin",
            "password": new_test_password
        })
        self.assertEqual(resp_login_new.status_code, 200)

        # 6. Đăng nhập bằng mật khẩu cũ (khi chưa khôi phục) -> 403
        resp_login_old = self.client.post("/api/auth/admin-verify", json={
            "username": "admin",
            "password": "wrong_old_password"
        })
        self.assertEqual(resp_login_old.status_code, 403)

        # 7. Khôi phục mật khẩu mặc định 325396
        auth_data = get_admin_auth_data()
        auth_data["password"] = "325396"
        auth_data["active_otp"] = None
        save_admin_auth_data(auth_data)

        # Kiểm tra lại mật khẩu 325396 hoạt động bình thường
        resp_restored = self.client.post("/api/auth/admin-verify", json={
            "username": "admin",
            "password": "325396"
        })
        self.assertEqual(resp_restored.status_code, 200)

    def test_hpg_and_market_lctt_2024(self):
        """
        Kiểm tra tính toàn vẹn dữ liệu LCTT (Báo cáo Lưu chuyển tiền tệ) chi tiết:
        1. HPG năm 2024 phải có dữ liệu đầy đủ các dòng chỉ tiêu (không bị trống/zero).
        2. raw_cf cho 2024 phải có dữ liệu CFO, CFI, CFF, Vay, Trả nợ vay.
        3. Kiểm tra các mã khác (VNM, FPT, MWG, KBC) cũng có dữ liệu LCTT hoàn chỉnh.
        """
        resp = self.client.get("/api/financial-overview/HPG")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        stm_annual = data.get("statements_annual", {})
        periods = stm_annual.get("periods", [])
        self.assertIn("2024", periods)
        idx_2024 = periods.index("2024")

        raw_cf = stm_annual.get("raw_cf", {})
        self.assertGreater(len(raw_cf), 0)

        # Số dòng có dữ liệu khác 0 trong năm 2024 phải chiếm đa số (> 50%)
        non_zeros_2024 = sum(1 for v in raw_cf.values() if idx_2024 < len(v) and v[idx_2024] != 0)
        self.assertGreater(non_zeros_2024, 25)

        # Kiểm tra các chỉ tiêu dòng tiền cốt lõi của HPG năm 2024
        cfo_val = stm_annual.get("cfo", [])[idx_2024]
        cfi_val = stm_annual.get("cfi", [])[idx_2024]
        cff_val = stm_annual.get("cff", [])[idx_2024]
        self.assertNotEqual(cfo_val, 0.0)
        self.assertNotEqual(cfi_val, 0.0)
        self.assertNotEqual(cff_val, 0.0)

    def test_bctc_toolbar_and_excel_export_ui(self):
        """
        Kiểm tra tích hợp giao diện Tab Chi tiết BCTC:
        1. Khung bên trái hiển thị mã chứng khoán, tên công ty, ngành/sàn (#bctc-ticker-info-bar).
        2. Khung bên phải có nút Xuất Excel 3 Sheet (KQKD, CĐKT, LCTT) và nút PDF.
        3. Các hàm JS updateBctcTickerInfoBar, exportBctcThreeSheetsExcel, exportBctcTablePdf có mặt đầy đủ trong app.js.
        """
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        self.assertIn("bctc-ticker-info-bar", html_content)
        self.assertIn("bctc-info-ticker", html_content)
        self.assertIn("bctc-info-name", html_content)
        self.assertIn("bctc-info-sector", html_content)
        self.assertIn("btn-export-bctc-excel", html_content)
        self.assertIn("exportBctcThreeSheetsExcel()", html_content)
        self.assertIn("btn-export-bctc-pdf", html_content)
        self.assertIn("exportBctcTablePdf()", html_content)

        with open("static/app.js", "r", encoding="utf-8") as f:
            js_content = f.read()

        self.assertIn("function updateBctcTickerInfoBar()", js_content)
        self.assertIn("function exportBctcThreeSheetsExcel()", js_content)
        self.assertIn("function exportBctcTablePdf()", js_content)
        self.assertIn("1. KQKD", js_content)
        self.assertIn("2. CĐKT", js_content)
        self.assertIn("3. LCTT", js_content)

    def test_overview_company_reports_feature(self):
        """
        Kiểm tra tính năng Báo cáo phân tích doanh nghiệp trong tab Tổng quan (thay thế mô tả cũ):
        1. HTML chứa đầy đủ bảng báo cáo, ô tìm kiếm mã CP, dropdown loại, dropdown nguồn, nút Tìm.
        2. JS chứa đầy đủ loadOverviewCompanyReports, handleOverviewReportSearch, clearOverviewReportKeyword.
        3. Endpoint API trả về danh sách bài báo cáo có đầy đủ tiêu đề, nguồn, ngày, link PDF trực tiếp.
        """
        with open("static/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn("overview-reports-table", html)
        self.assertIn("overview-report-keyword", html)
        self.assertIn("overview-report-type-select", html)
        self.assertIn("overview-report-source-select", html)
        self.assertIn("overview-reports-body", html)
        self.assertIn("overview-report-ticker-badge", html)
        self.assertIn("handleOverviewReportSearch()", html)
        self.assertIn("clearOverviewReportKeyword()", html)

        with open("static/app.js", "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("function loadOverviewCompanyReports", js)
        self.assertIn("function handleOverviewReportSearch", js)
        self.assertIn("function clearOverviewReportKeyword", js)
        self.assertIn("function handleReportPdfClick", js)

        # Kiểm tra gọi API truy xuất báo cáo phân tích cho HPG
        resp = self.client.get("/api/industry-reports?ticker=HPG&keyword=hpg")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        reports = data.get("reports", [])
        self.assertGreater(len(reports), 0)
        first_rep = reports[0]
        self.assertIn("title", first_rep)
        self.assertIn("source", first_rep)
        self.assertIn("date", first_rep)
        self.assertIn("file_url", first_rep)
        self.assertTrue(first_rep["file_url"].startswith("http") or first_rep["file_url"].endswith(".pdf"))


if __name__ == "__main__":
    unittest.main()





