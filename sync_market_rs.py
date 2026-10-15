import asyncio
import os
import sys
import json
import time
import httpx
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
COMPANIES_JSON = os.path.join(DATA_DIR, "vietnam_companies_database.json")
PERF_CACHE_JSON = os.path.join(DATA_DIR, "market_performance_cache.json")

async def sync_all_stocks():
    print(">>> [RS-SYNC] Bat dau dong bo hieu suat nến lich su toan thi truong...")
    t0 = time.time()
    
    # 1. Load danh sach ma tu DB va SSI
    symbols = set()
    db = {}
    if os.path.exists(COMPANIES_JSON):
        try:
            with open(COMPANIES_JSON, "r", encoding="utf-8") as f:
                db = json.load(f)
            for s in db.keys():
                if len(s) == 3 and s.isalpha():
                    symbols.add(s.upper())
        except Exception as e:
            print(f"Error loading {COMPANIES_JSON}: {e}")
            
    # Load SSI cache neu co
    try:
        from crawler import _SSI_EXCHANGE_CACHE, fetch_ssi_live_stock_quote
        if not _SSI_EXCHANGE_CACHE or len(_SSI_EXCHANGE_CACHE) < 500:
            await fetch_ssi_live_stock_quote("HPG", force_refresh=False)
        for s in _SSI_EXCHANGE_CACHE.keys():
            if len(s) == 3 and s.isalpha():
                symbols.add(s.upper())
    except Exception as e:
        print(f"Error loading SSI cache: {e}")

    sym_list = sorted(list(symbols))
    print(f">>> [RS-SYNC] Tong so ma can dong bo: {len(sym_list)}")
    
    sem = asyncio.Semaphore(25) # 25 concurrent requests
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    perf_results = {}
    
    async def fetch_symbol_perf(client: httpx.AsyncClient, sym: str):
        async with sem:
            # Thu lay tu VNDirect dchart API
            try:
                url = f"https://dchart-api.vndirect.com.vn/dchart/history?resolution=D&symbol={sym}&from=1735689600&to=1800000000"
                r = await client.get(url, timeout=6.0)
                if r.status_code == 200:
                    data = r.json()
                    c = data.get("c", [])
                    if len(c) >= 5:
                        p_now = float(c[-1])
                        c1m = round((p_now - c[-20]) / c[-20] * 100, 2) if len(c) >= 20 else 0.0
                        c3m = round((p_now - c[-60]) / c[-60] * 100, 2) if len(c) >= 60 else 0.0
                        c6m = round((p_now - c[-120]) / c[-120] * 100, 2) if len(c) >= 120 else c3m
                        c1y = round((p_now - c[-250]) / c[-250] * 100, 2) if len(c) >= 250 else round((p_now - c[0]) / c[0] * 100, 2)
                        
                        # Cong thuc RS Score chuan William O'Neil (CANSLIM):
                        # Q4 (3M gan nhat): trong so 2.0 (40%)
                        # Q3 (3-6M): trong so 1.0 (20%)
                        # Q1+Q2 (1Y): trong so 0.5 (20%)
                        # 1M (da tang ngan han): trong so 1.0
                        score = c3m * 2.0 + c1m * 1.0 + c6m * 0.5 + c1y * 0.5
                        
                        return sym, {
                            "price": p_now * 1000.0 if p_now < 1000.0 else p_now,
                            "c1m": c1m,
                            "c3m": c3m,
                            "c6m": c6m,
                            "c1y": c1y,
                            "score": round(score, 2),
                            "updated_at": time.time()
                        }
            except Exception:
                pass
        return sym, None

    async with httpx.AsyncClient(headers=headers, timeout=8.0) as client:
        tasks = [fetch_symbol_perf(client, s) for s in sym_list]
        chunk_res = await asyncio.gather(*tasks)
        for sym, data in chunk_res:
            if data:
                perf_results[sym] = data

    print(f">>> [RS-SYNC] Da tai va tinh toan thanh cong {len(perf_results)}/{len(sym_list)} ma (Thoi gian: {time.time()-t0:.2f}s)")
    
    # 2. Tinh toan Percentile RS (1-99) cho toan thi truong
    sorted_stocks = sorted(perf_results.items(), key=lambda x: x[1]["score"])
    n = max(1, len(sorted_stocks))
    for rank, (sym, p_data) in enumerate(sorted_stocks):
        rs_rating = max(1, min(99, int(round((rank + 1) / n * 99))))
        p_data["rs_rating"] = rs_rating

    # Ghi vao cache market_performance_cache.json
    with open(PERF_CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(perf_results, f, ensure_ascii=False, indent=2)
    print(f">>> [RS-SYNC] Da luu {PERF_CACHE_JSON}")
    
    # 3. Cap nhat dong bo vao vietnam_companies_database.json
    updated_count = 0
    added_count = 0
    
    # Lấy thông tin SSI để bổ sung tên/sàn cho các mã mới như HHP
    from crawler import _SSI_EXCHANGE_CACHE
    
    for sym, p_data in perf_results.items():
        if sym in db:
            # Cập nhật mã hiện có
            db[sym]["price"] = p_data["price"]
            db[sym]["price_change_1m_pct"] = p_data["c1m"]
            db[sym]["price_change_3m_pct"] = p_data["c3m"]
            db[sym]["price_change_ytd_pct"] = p_data["c1y"]
            updated_count += 1
        else:
            # Bổ sung mã mới vào database (ví dụ HHP)
            ssi_info = _SSI_EXCHANGE_CACHE.get(sym, {})
            c_name = ssi_info.get("companyNameVi") or ssi_info.get("clientName") or sym
            ex = (ssi_info.get("exchange") or "HOSE").upper().strip()
            db[sym] = {
                "ticker": sym,
                "name": c_name,
                "exchange": ex,
                "price": p_data["price"],
                "price_change_1m_pct": p_data["c1m"],
                "price_change_3m_pct": p_data["c3m"],
                "price_change_ytd_pct": p_data["c1y"],
                "price_change_2w_pct": p_data["c1m"] * 0.5,
                "update_source": "HeThongDongBoLichSu"
            }
            added_count += 1
            
    with open(COMPANIES_JSON, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f">>> [RS-SYNC] Cap nhat {updated_count} ma hien co, bo sung {added_count} ma moi vao {COMPANIES_JSON}")

    # In kiem tra HHS va HHP
    hhs_res = perf_results.get("HHS")
    hhp_res = perf_results.get("HHP")
    print(f">>> [KET QUA KIEM TRA]")
    print(f"HHS -> Price: {hhs_res.get('price') if hhs_res else 'N/A'}, 1M: {hhs_res.get('c1m')}%, 3M: {hhs_res.get('c3m')}%, 1Y: {hhs_res.get('c1y')}%, Score: {hhs_res.get('score')}, RS: {hhs_res.get('rs_rating')}")
    print(f"HHP -> Price: {hhp_res.get('price') if hhp_res else 'N/A'}, 1M: {hhp_res.get('c1m')}%, 3M: {hhp_res.get('c3m')}%, 1Y: {hhp_res.get('c1y')}%, Score: {hhp_res.get('score')}, RS: {hhp_res.get('rs_rating')}")

if __name__ == "__main__":
    asyncio.run(sync_all_stocks())
