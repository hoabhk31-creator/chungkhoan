# -*- coding: utf-8 -*-
"""
GEMINI FLASH CORPORATE GROWTH & PROJECTS EXTRACTION ENGINE
Hệ thống AI tự động đọc BCTN, BCTC soát xét & Báo cáo Phân tích trong 1.5 năm gần nhất.
- Bóc tách chỉ tiêu kế hoạch kinh doanh, tiến độ dự án, chỉ số nghiệp vụ thực tế.
- Tự động thay đổi linh hoạt theo từng ngành nghề (Ngân hàng, BĐS, Thép, Bán lẻ...).
- Tuyệt đối loại bỏ văn mẫu, không bịa đặt số liệu (Zero-Fabrication).
- Quản lý Rate Limit nghiêm ngặt (khoảng cách tối thiểu 5s/request) tránh trùng lặp gây lỗi 429.
- Bộ nhớ Cache vĩnh viễn (data/gemini_growth_cache.json) với cơ chế tự động dọn dẹp dữ liệu > 1.5 năm để tiết kiệm dung lượng đĩa.
"""

import os
import json
import time
import re
import asyncio
from typing import Dict, List, Any, Optional
import httpx

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "gemini_growth_cache.json")
GEMINI_CONFIG_FILE = os.path.join(DATA_DIR, "gemini_config.json")
PDF_CATALYSTS_FILE = os.path.join(DATA_DIR, "pdf_catalysts_cache.json")

# Hạn định thời gian: Tối đa 1.5 năm (18 tháng / 550 ngày)
MAX_DATA_AGE_SECONDS = 550 * 86400

# Quản lý khóa chống trùng lặp request và giãn cách tối thiểu 5 giây
_REQUEST_LOCK = asyncio.Lock()
_LAST_REQUEST_TIME = 0.0
_QUOTA_COOLDOWN_UNTIL = 0.0


def get_gemini_api_key() -> str:
    """Lấy API Key từ Environment hoặc gemini_config.json."""
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if k:
        return k.strip()
    if os.path.exists(GEMINI_CONFIG_FILE):
        try:
            with open(GEMINI_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return (cfg.get("api_key") or "").strip()
        except Exception:
            pass
    return ""


def load_gemini_growth_cache() -> Dict[str, Any]:
    """Tải cache và tự động dọn dẹp các mục cũ hơn 1.5 năm để tiết kiệm dung lượng."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        now = time.time()
        # Dọn dẹp tự động các mục quá 1.5 năm
        pruned = {}
        for t, entry in cache.items():
            ts = entry.get("timestamp", 0)
            if (now - ts) <= MAX_DATA_AGE_SECONDS:
                pruned[t] = entry
        if len(pruned) < len(cache):
            save_gemini_growth_cache(pruned)
        return pruned
    except Exception as e:
        print(f"[GeminiGrowth] Lỗi đọc cache: {e}")
        return {}


def save_gemini_growth_cache(cache: Dict[str, Any]) -> None:
    """Lưu cache an toàn."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[GeminiGrowth] Lỗi ghi cache: {e}")


def collect_recent_documents_for_ticker(ticker: str) -> List[str]:
    """
    Thu thập các đoạn trích báo cáo có độ tuổi <= 1.5 năm cho mã ticker.
    Áp dụng regex ranh giới từ phân biệt chữ HOA chống dính mã.
    """
    clean_ticker = (ticker or "").upper().strip()
    if not os.path.exists(PDF_CATALYSTS_FILE):
        return []

    try:
        with open(PDF_CATALYSTS_FILE, "r", encoding="utf-8") as f:
            pdf_data = json.load(f)
    except Exception:
        return []

    now = time.time()
    pat = re.compile(rf'(?:^|[_\-/\.])({clean_ticker})(?:[_\-\./]|$)')
    collected = []

    for url, entry in pdf_data.items():
        if not pat.search(url):
            continue
        ts = entry.get("ts", 0)
        # Bỏ qua tài liệu quá 1.5 năm (18 tháng)
        if ts and (now - ts > MAX_DATA_AGE_SECONDS):
            continue
        
        cats = entry.get("cats", [])
        for c in cats:
            c_str = c.strip()
            if len(c_str) >= 25 and c_str not in collected:
                collected.append(c_str)

    return collected


async def extract_growth_profile_with_gemini(ticker: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Sử dụng Gemini Flash đọc BCTN & Báo cáo phân tích trong 1.5 năm gần nhất.
    Trích xuất cấu trúc động lực tăng trưởng thực tế, lưu Persistent Cache.
    """
    clean_ticker = (ticker or "").upper().strip()
    if not clean_ticker:
        return None

    cache = load_gemini_growth_cache()
    now = time.time()

    # 1. Kiểm tra cache: Nếu có và trong hạn 1.5 năm (và không force refresh) -> Trả về ngay lập tức
    if not force_refresh and clean_ticker in cache:
        entry = cache[clean_ticker]
        if (now - entry.get("timestamp", 0)) < MAX_DATA_AGE_SECONDS:
            return entry

    # 2. Thu thập văn bản thực tế trong vòng 1.5 năm
    doc_lines = collect_recent_documents_for_ticker(clean_ticker)
    if not doc_lines:
        return None

    api_key = get_gemini_api_key()
    if not api_key:
        return None

    # Khống chế thời gian cooldown và giãn cách request tối thiểu 5s để không bị 429
    global _LAST_REQUEST_TIME, _QUOTA_COOLDOWN_UNTIL
    if time.time() < _QUOTA_COOLDOWN_UNTIL:
        # Nếu đang trong thời gian chờ sau 429, không spam API
        return None

    async with _REQUEST_LOCK:
        if time.time() < _QUOTA_COOLDOWN_UNTIL:
            return None
        elapsed = time.time() - _LAST_REQUEST_TIME
        if elapsed < 5.0:
            await asyncio.sleep(5.0 - elapsed)
        _LAST_REQUEST_TIME = time.time()

    from adaptive_growth_engine import classify_business_model
    model_info = classify_business_model(clean_ticker)
    m_key = model_info.get("model_key", "GENERAL")
    badge_text = model_info.get("badge_text", "Doanh nghiệp")

    # Giới hạn nội dung tài liệu nạp vào AI (khoảng 35 dòng cốt lõi nhất)
    sample_text = "\n---\n".join(doc_lines[:40])

    prompt = f"""Bạn là chuyên gia phân tích tài chính cấp cao tại Việt Nam.
Dưới đây là các dữ liệu công bố và trích đoạn Báo cáo Tài chính/Báo cáo Thường niên trong 1.5 năm gần đây của mã cổ phiếu {clean_ticker} (Mô hình: {badge_text}).

Hãy đọc kỹ và bóc tách cấu trúc ĐỘNG LỰC TĂNG TRƯỞNG & DỰ ÁN THỰC TẾ thành định dạng JSON:

YÊU CẦU NGHIÊM NGẶT:
1. TUYỆT ĐỐI KHÔNG DÙNG VĂN MẪU CHUNG CHUNG (Không dùng các câu sáo rỗng như 'Doanh nghiệp đặt mục tiêu nâng cao hiệu quả vận hành...').
2. TUYỆT ĐỐI KHÔNG BỊA ĐẶT SỐ LIỆU (Tuyệt đối không điền số mặc định 1.000 tỷ hay 100 tỷ hay 20%). Nếu tài liệu không ghi, điền 'Chưa công bố'.
3. Bóc tách linh hoạt theo từng nhóm ngành:
   - Nếu là Ngân hàng: Trích xuất Tăng trưởng tín dụng YTD, LNTT lũy kế và tỷ lệ hoàn thành kế hoạch năm của ĐHĐCĐ, Tỷ lệ CASA %, NPL %, CIR %, động lực cho vay hạ tầng/APEC, nhận chuyển giao bắt buộc ngân hàng 0 đồng (nếu có).
   - Nếu là Chứng khoán: Dư nợ Margin, Thị phần môi giới, Hệ thống KRX, Kế hoạch LNTT & Cổ tức.
   - Nếu là BĐS / Xây dựng / Hạ tầng / Thép / Năng lượng: Trích xuất các Dự án/Nhà máy cụ thể (tên dự án, vốn đầu tư tỷ đồng, tiến độ bàn giao thực tế).
   - Nếu là Bán lẻ / Tiêu dùng: Số lượng cửa hàng chuỗi mở mới, doanh thu/cửa hàng, mở rộng quốc tế.

CẤU TRÚC JSON PHẢI TRẢ VỀ:
{{
  "ticker": "{clean_ticker}",
  "growth_cards": [
    {{
      "title": "Tiêu đề cụ thể chứa số liệu thật của doanh nghiệp",
      "category_tag": "Tên nhóm chỉ tiêu",
      "metrics": [
        {{"label": "Tên chỉ số 1", "value": "Giá trị thật"}},
        {{"label": "Tên chỉ số 2", "value": "Giá trị thật"}},
        {{"label": "Tên chỉ số 3", "value": "Giá trị thật"}}
      ],
      "content": "Phân tích 2-3 câu bám sát số liệu thực tế được ghi nhận.",
      "source": "Báo cáo phân tích CTCK & BCTC Soát xét"
    }}
  ]
}}

NỘI DUNG TÀI LIỆU TRONG 1.5 NĂM GẦN ĐÂY:
{sample_text[:9500]}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    # Danh sách các models Flash có sẵn trong Free Tier
    models_to_try = [
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
        "gemini-3.5-flash"
    ]

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            for model_name in models_to_try:
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                try:
                    resp = await client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_text)
                        cards = parsed.get("growth_cards", [])
                        if cards:
                            result_data = {
                                "ticker": clean_ticker,
                                "timestamp": now,
                                "ai_model": model_name,
                                "growth_cards": cards
                            }
                            # Lưu vào Persistent Cache
                            cache[clean_ticker] = result_data
                            save_gemini_growth_cache(cache)
                            print(f"[GeminiGrowth] Bóc tách thành công {len(cards)} thẻ cho {clean_ticker} qua {model_name}")
                            return result_data
                    elif resp.status_code == 429:
                        print(f"[GeminiGrowth] 429 Quota trên model {model_name}, chuyển sang model kế tiếp...")
                        _QUOTA_COOLDOWN_UNTIL = time.time() + 60.0
                        continue
                    else:
                        print(f"[GeminiGrowth] HTTP {resp.status_code} trên model {model_name}")
                except Exception as ex:
                    print(f"[GeminiGrowth] Lỗi gọi model {model_name}: {ex}")
                    continue
    except Exception as e:
        print(f"[GeminiGrowth] Exception tổng thể: {e}")

    return None
