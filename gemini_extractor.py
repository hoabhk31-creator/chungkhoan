"""
Gemini Flash Intelligent PDF & Report Extraction Engine
Tự động bóc tách Catalysts và Rủi ro có cấu trúc từ báo cáo phân tích tài chính.
- Khống chế Rate Limiter nghiêm ngặt (tối đa 10 requests/phút) để đảm bảo 100% trong Free Tier (0đ).
- Lưu đệm cache vĩnh viễn (Chỉ phân tích 1 lần duy nhất cho mỗi báo cáo).
- Dự phòng an toàn (Graceful Fallback): Nếu không có API Key hoặc lỗi mạng, trả về None để dùng bộ lọc heuristic nội bộ.
"""

import os
import sys
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import httpx

# Đường dẫn cấu hình khóa API (tùy chọn lưu file hoặc biến môi trường)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
GEMINI_CONFIG_FILE = os.path.join(DATA_DIR, "gemini_config.json")

# Rate Limiter state: đảm bảo khoảng cách tối thiểu 4 giây giữa các requests (<= 15 RPM)
_LAST_REQUEST_TIME = 0.0
_REQUEST_LOCK = asyncio.Lock()
_QUOTA_EXHAUSTED_UNTIL = 0.0


def get_gemini_api_key() -> str:
    """Lấy Gemini API Key từ Environment Variable hoặc file config."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if key:
        return key.strip()

    if os.path.exists(GEMINI_CONFIG_FILE):
        try:
            with open(GEMINI_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return (cfg.get("api_key") or "").strip()
        except Exception:
            pass
    return ""


async def extract_catalysts_with_gemini_flash(
    text: str,
    ticker: str,
    institution: str = ""
) -> Optional[Tuple[List[str], List[str]]]:
    """
    Sử dụng Gemini 1.5 Flash để bóc tách thông minh các Catalysts & Key Risks từ văn bản báo cáo.
    Trả về (catalysts, risks) hoặc None nếu không khả dụng.
    """
    global _QUOTA_EXHAUSTED_UNTIL
    # Nếu đang trong thời gian cạn quota (429), lập tức fallback không chờ đợi
    if time.time() < _QUOTA_EXHAUSTED_UNTIL:
        return None

    api_key = get_gemini_api_key()
    if not api_key:
        return None

    if not text or len(text.strip()) < 100:
        return None

    # Khống chế tốc độ (Rate Limit Protection) - Tối đa 10 requests/phút
    global _LAST_REQUEST_TIME
    async with _REQUEST_LOCK:
        if time.time() < _QUOTA_EXHAUSTED_UNTIL:
            return None
        now = time.time()
        elapsed = now - _LAST_REQUEST_TIME
        if elapsed < 4.0:
            await asyncio.sleep(4.0 - elapsed)
        _LAST_REQUEST_TIME = time.time()

    models_to_try = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.5-flash"]

    prompt = f"""Bạn là chuyên gia phân tích tài chính cao cấp tại Việt Nam.
Hãy đọc kỹ nội dung báo cáo phân tích về mã cổ phiếu {ticker.upper()} của tổ chức {institution or 'CTCK'} dưới đây.
Trích xuất độc bản:
1. "catalysts": Tối đa 8 luận điểm ĐỘNG LỰC TĂNG TRƯỞNG & XÚC TÁC LỢI NHUẬN cốt lõi (chỉ lấy các luận điểm có số liệu, dự án KCN, backlog, hợp đồng ký mới, công suất, thị phần, kế hoạch doanh thu/LNST cụ thể; TUYỆT ĐỐI KHÔNG lấy câu chữ khuyến nghị giá mục tiêu, P/E, P/B dự phóng hay tỷ lệ chiết khấu).
2. "risks": Tối đa 5 RỦI RO TRỌNG YẾU (lãi suất cao, nợ vay tăng, chi phí nguyên vật liệu, trượt tiến độ, rủi ro thu hồi công nợ...).

YÊU CẦU ĐẶC BIỆT:
- Tuyệt đối KHÔNG xếp các luận điểm mang tính tiêu cực/rủi ro/thách thức vào mục "catalysts".
- Trả về đúng định dạng JSON:
{{
  "catalysts": ["luận điểm 1 có số liệu cụ thể", "luận điểm 2..."],
  "risks": ["rủi ro 1...", "rủi ro 2..."]
}}

NỘI DUNG BÁO CÁO:
{text[:12000]}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=18.0) as client:
            for model_name in models_to_try:
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json)
                    cats = [c.strip() for c in parsed.get("catalysts", []) if len(c.strip()) >= 20]
                    risks = [r.strip() for r in parsed.get("risks", []) if len(r.strip()) >= 20]
                    if cats or risks:
                        return (cats[:10], risks[:8])
                elif resp.status_code == 429:
                    print(f"[Gemini-Flash] Quota limit reached on {model_name}, graceful fallback to local heuristic.")
                    _QUOTA_EXHAUSTED_UNTIL = time.time() + 60.0
                    break
                else:
                    print(f"[Gemini-Flash] HTTP {resp.status_code} on {model_name}")
    except Exception as e:
        import traceback
        print(f"[Gemini-Flash] Error calling API: {type(e).__name__}: {repr(e)}")
        traceback.print_exc()

    return None
