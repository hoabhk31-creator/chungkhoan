# -*- coding: utf-8 -*-
"""
BATCH SYNCHRONIZATION FOR GEMINI GROWTH CARDS
Quét và bóc tách tự động cho toàn bộ các mã cổ phiếu trên sàn có báo cáo trong vòng 1.5 năm.
- Giãn cách 6.0 giây giữa mỗi request đảm bảo 100% trong Free Tier của Google Gemini (<= 10 RPM).
- Không gọi trùng lặp nếu mã đã có trong cache và còn trong hạn 1.5 năm.
- Tự động xóa sạch mọi dữ liệu/báo cáo quá 1.5 năm (550 ngày) để tiết kiệm dung lượng đĩa.
"""

import asyncio
import os
import sys
import json
import time
import re

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from gemini_growth_extractor import (
    extract_growth_profile_with_gemini,
    load_gemini_growth_cache,
    save_gemini_growth_cache,
    MAX_DATA_AGE_SECONDS,
    DATA_DIR
)

# Danh sách các mã phổ biến nhất có tài liệu công bố
PRIORITY_TICKERS = [
    "MBB", "VCB", "TCB", "CTG", "HDB", "ACB", "VPB", "STB", "BID", "TPB",
    "SSI", "VND", "VCI", "HCM", "MBS", "SHS", "FTS", "VIX",
    "VHM", "NHA", "HPG", "MWG", "FPT", "GAS", "POW", "GMD", "HAH",
    "DGC", "KBC", "IDC", "REE", "NLG", "VNM", "MSN", "PVD", "PVS",
    "VRE", "DCM", "HSG", "PNJ", "BSR", "DXG", "VHC"
]

async def run_batch_sync(limit: int = 20):
    cache = load_gemini_growth_cache()
    now = time.time()
    print(f">>> [BatchSync] Bắt đầu đồng bộ Gemini Growth Cards (Đã có sẵn {len(cache)} mã trong cache)...")

    processed = 0
    for ticker in PRIORITY_TICKERS:
        if processed >= limit:
            break

        # Nếu đã có trong cache và trong hạn 1.5 năm -> Bỏ qua
        if ticker in cache and (now - cache[ticker].get("timestamp", 0)) < MAX_DATA_AGE_SECONDS:
            cards = cache[ticker].get("growth_cards", [])
            print(f"  + [{ticker}] Đã có trong cache ({len(cards)} thẻ). Bỏ qua.")
            continue

        print(f"  -> [{ticker}] Đang đọc báo cáo và bóc tách bằng Gemini Flash...")
        res = await extract_growth_profile_with_gemini(ticker, force_refresh=True)
        if res and res.get("growth_cards"):
            print(f"     ✓ Thành công: {len(res['growth_cards'])} thẻ thực tế.")
            processed += 1
        else:
            print(f"     ! Không có dữ liệu mới hoặc API cooldown.")

        # Giãn cách 6.0 giây để tuân thủ Rate Limit Free Tier
        await asyncio.sleep(6.0)

    print(f">>> [BatchSync] Hoàn tất đợt đồng bộ! Tổng số mã cập nhật mới: {processed}")

if __name__ == '__main__':
    asyncio.run(run_batch_sync(limit=10))
