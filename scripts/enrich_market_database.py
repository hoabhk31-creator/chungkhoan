# -*- coding: utf-8 -*-
"""
HỆ THỐNG ĐỒNG BỘ VÀ LÀM GIÀU DỮ LIỆU CỔ TỨC & DOANH NGHIỆP TOÀN DIỆN (MARKET ENRICHMENT ENGINE)
- Đồng bộ sự kiện quyền, cổ tức tiền mặt & cổ phiếu từ Simplize Open API vào corporate_actions_cache.json
- Bổ sung SLCP lưu hành (listed shares), vốn hóa thực tế (market cap) từ SSI iboard vào vietnam_companies_database.json
- Bổ sung ngành nghề chuẩn hóa 23 nhóm ngành IERM
"""

import os
import sys
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT_DIR, "cache")
DATA_DIR = os.path.join(ROOT_DIR, "data")
CA_FILE = os.path.join(CACHE_DIR, "corporate_actions_cache.json")
DB_FILE = os.path.join(DATA_DIR, "vietnam_companies_database.json")

# Import parser sự kiện quyền và phân loại ngành
sys.path.insert(0, ROOT_DIR)
from corporate_actions import parse_simplize_event
from adaptive_growth_engine import classify_business_model


def sync_all_corporate_actions():
    print("=== [1/3] ĐỒNG BỘ SỰ KIỆN QUYỀN & CỔ TỨC TOÀN SÀN ===")
    if not os.path.exists(CA_FILE):
        ca_data = {}
    else:
        with open(CA_FILE, "r", encoding="utf-8") as f:
            ca_data = json.load(f)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        comp_db = json.load(f)

    all_tickers = sorted(list(comp_db.keys()))
    missing_tickers = [t for t in all_tickers if t not in ca_data or len(ca_data.get(t, [])) == 0]
    print(f"Tổng số mã: {len(all_tickers)} | Đã có cache: {len(ca_data)} | Cần đồng bộ: {len(missing_tickers)}")

    def fetch_ca(ticker):
        url = f"https://api.simplize.vn/api/company/events/list?ticker={ticker}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=4.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_items = data.get("data", []) if isinstance(data, dict) else []
                parsed = []
                for item in raw_items:
                    ev = parse_simplize_event(item, ticker)
                    if ev:
                        parsed.append(ev)
                return ticker, parsed
        except Exception:
            return ticker, []

    success_count = 0
    with ThreadPoolExecutor(max_workers=18) as executor:
        for idx, (sym, events) in enumerate(executor.map(fetch_ca, missing_tickers)):
            ca_data[sym] = events
            if len(events) > 0:
                success_count += 1
            if (idx + 1) % 100 == 0 or (idx + 1) == len(missing_tickers):
                print(f"  -> Tiến độ Cổ tức: {idx + 1}/{len(missing_tickers)} (tìm thấy sự kiện: {success_count})")

    with open(CA_FILE, "w", encoding="utf-8") as f:
        json.dump(ca_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã lưu {len(ca_data)} mã cổ phiếu vào {CA_FILE}!\n")


def sync_all_stock_capital_and_sectors():
    print("=== [2/3] BỔ SUNG SLCP LƯU HÀNH, VỐN HÓA & CHUẨN HÓA NGÀNH NGHỀ ===")
    with open(DB_FILE, "r", encoding="utf-8") as f:
        comp_db = json.load(f)

    all_tickers = sorted(list(comp_db.keys()))
    print(f"Quét thông tin vốn hóa và cổ phiếu lưu hành từ SSI iBoard cho {len(all_tickers)} mã...")

    def fetch_ssi_shares(ticker):
        url = f"https://iboard-query.ssi.com.vn/stock/{ticker}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                d = json.loads(resp.read().decode("utf-8"))
                item = d.get("data", {}) if isinstance(d, dict) else {}
                return ticker, item.get("listedShare"), item.get("companyNameVi"), item.get("refPrice")
        except Exception:
            return ticker, None, None, None

    ssi_results = {}
    with ThreadPoolExecutor(max_workers=18) as executor:
        for idx, (sym, shares, name_vi, ref_p) in enumerate(executor.map(fetch_ssi_shares, all_tickers)):
            ssi_results[sym] = (shares, name_vi, ref_p)
            if (idx + 1) % 200 == 0 or (idx + 1) == len(all_tickers):
                print(f"  -> Tiến độ SSI: {idx + 1}/{len(all_tickers)}")

    updated_count = 0
    sector_updated = 0
    for sym, comp in comp_db.items():
        sh, name_vi, ref_p = ssi_results.get(sym, (None, None, None))
        
        # 1. Cập nhật tên tiếng Việt có dấu chuẩn nếu có
        if name_vi and len(name_vi.strip()) > len(comp.get("name", "")):
            comp["name"] = name_vi.strip()

        # 2. Cập nhật SLCP lưu hành
        p = float(comp.get("price") or ref_p or 0.0)
        if sh and sh > 0:
            sh_mil = round(float(sh) / 1_000_000, 2)
            comp["shares_outstanding_mil"] = sh_mil
            comp["listed_shares"] = int(sh)
            # Tính vốn hóa chuẩn xác
            if p > 0:
                comp["market_cap_bil"] = round((float(sh) * p) / 1_000_000_000, 2)
                updated_count += 1

        # 3. Chuẩn hóa ngành nghề nếu rỗng hoặc chung chung
        cur_sec = comp.get("fiintrade_sector") or comp.get("icb2")
        if not cur_sec or cur_sec == "Doanh nghiệp niêm yết":
            b_info = classify_business_model(sym, "", comp.get("name", ""))
            badge = b_info.get("badge_text")
            if badge and badge != "Doanh nghiệp niêm yết":
                comp["fiintrade_sector"] = badge
                comp["icb2"] = badge
                sector_updated += 1

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comp_db, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã cập nhật Vốn hóa/SLCP cho {updated_count} mã và Chuẩn hóa Ngành cho {sector_updated} mã vào {DB_FILE}!\n")


def sync_annual_statements_for_missing():
    print("=== [3/3] TỰ ĐỘNG NẠP BCTC NĂM VÀ DOANH THU/LNST CHO CÁC MÃ CÒN THIẾU ===")
    from financial_scraper import fetch_multi_period_financials
    with open(DB_FILE, "r", encoding="utf-8") as f:
        comp_db = json.load(f)

    stmt_dir = os.path.join(CACHE_DIR, "statements")
    os.makedirs(stmt_dir, exist_ok=True)

    # Lấy danh sách các mã có thanh khoản hoặc vốn hóa lớn chưa có BCTC
    missing_bctc = []
    for sym, comp in comp_db.items():
        fn_year = os.path.join(stmt_dir, f"{sym}_year.json")
        fn_quarter = os.path.join(stmt_dir, f"{sym}_quarter.json")
        if not os.path.exists(fn_year) and not os.path.exists(fn_quarter):
            missing_bctc.append(sym)

    print(f"Số mã chưa có BCTC: {len(missing_bctc)}. Nạp thử nghiệm 80 mã có thanh khoản/quy mô hàng đầu...")
    top_missing = missing_bctc[:80]

    def fetch_bctc(sym):
        try:
            return sym, fetch_multi_period_financials(sym, "year")
        except Exception:
            return sym, None

    done_bctc = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        for idx, (sym, data) in enumerate(executor.map(fetch_bctc, top_missing)):
            if data and data.get("periods"):
                done_bctc += 1
            if (idx + 1) % 20 == 0 or (idx + 1) == len(top_missing):
                print(f"  -> Tiến độ BCTC: {idx + 1}/{len(top_missing)} (thành công: {done_bctc})")
    print(f"✓ Đã nạp thành công BCTC cho {done_bctc} mã vào cache!\n")


if __name__ == "__main__":
    t_start = time.time()
    sync_all_corporate_actions()
    sync_all_stock_capital_and_sectors()
    sync_annual_statements_for_missing()
    print(f"🎉 HOÀN TẤT TOÀN DIỆN TRONG {round(time.time() - t_start, 1)} GIÂY!")
