"""
Corporate Actions & Ex-Dividend Date Management Module
Xử lý sự kiện quyền (Cổ tức tiền mặt, Cổ tức cổ phiếu, Thưởng cổ phiếu, Phát hành thêm quyền mua)
và tự động chuẩn hóa, điều chỉnh giá mục tiêu (Target Price) của các CTCK sau ngày GDKHQ.
Nguồn tham chiếu: Vietstock (https://finance.vietstock.vn/lich-su-kien.htm), HOSE, HNX, CafeF.
"""

import os
import json
import re
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "corporate_actions_cache.json")


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
        except Exception:
            pass


def parse_action_date(date_str: str) -> Optional[date]:
    """Chuyển đổi chuỗi ngày dạng dd/mm/yyyy, yyyy-mm-dd thành đối tượng date."""
    if not date_str or date_str == "-":
        return None
    clean = str(date_str).strip().split(" ")[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# CƠ SỞ DỮ LIỆU SỰ KIỆN QUYỀN & NGÀY GDKHQ CHUẨN HÓA (2023 - 2026)
# Đối chiếu theo công bố chính thức tại HOSE/HNX và Vietstock Lịch Sự Kiện
# ---------------------------------------------------------------------------
CURATED_CORPORATE_ACTIONS: Dict[str, List[Dict[str, Any]]] = {
    "HPG": [
        {
            "id": "hpg-ca-2024",
            "ex_date": "20/06/2024",
            "record_date": "21/06/2024",
            "event_type": "dividend_both",
            "title": "Trả cổ tức năm 2023 bằng tiền mặt tỷ lệ 5% (500 đ/CP) và cổ phiếu thưởng 10%",
            "cash_amount": 500.0,
            "stock_ratio": 0.10,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 29200.0,
            "ref_price_after": 26090.0,
            "adjustment_factor": 0.8935,
            "description": "Chia cổ tức tổng hợp năm 2023: 500 đồng tiền mặt/CP và thưởng 10% cổ phiếu (tỷ lệ 10:1).",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "hpg-ca-2022",
            "ex_date": "17/06/2022",
            "record_date": "20/06/2022",
            "event_type": "dividend_both",
            "title": "Trả cổ tức năm 2021 bằng tiền mặt 5% và cổ phiếu 30%",
            "cash_amount": 500.0,
            "stock_ratio": 0.30,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 30500.0,
            "ref_price_after": 23070.0,
            "adjustment_factor": 0.7566,
            "description": "Chia cổ tức khủng năm 2021 sau đại thắng lợi nhuận: 500 đ tiền mặt và 30% cổ phiếu.",
            "source": "HOSE & Vietstock"
        }
    ],
    "SSI": [
        {
            "id": "ssi-ca-2024",
            "ex_date": "23/09/2024",
            "record_date": "24/09/2024",
            "event_type": "dividend_and_rights",
            "title": "Thưởng cổ phiếu tỷ lệ 20% (5:1) và phát hành quyền mua tỷ lệ 10% giá 15,000 đ/CP",
            "cash_amount": 0.0,
            "stock_ratio": 0.20,
            "rights_ratio": 0.10,
            "rights_price": 15000.0,
            "ref_price_before": 34500.0,
            "ref_price_after": 27690.0,
            "adjustment_factor": 0.8026,
            "description": "Tăng vốn điều lệ lên 19,645 tỷ đồng qua thưởng CP 20% và chào bán quyền mua 10% giá 15,000 đ.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ssi-ca-2023",
            "ex_date": "21/09/2023",
            "record_date": "22/09/2023",
            "event_type": "dividend_cash",
            "title": "Chi trả cổ tức năm 2022 bằng tiền mặt tỷ lệ 10% (1,000 đ/CP)",
            "cash_amount": 1000.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 35000.0,
            "ref_price_after": 34000.0,
            "adjustment_factor": 0.9714,
            "description": "Chi trả cổ tức tiền mặt 1,000 đồng/CP.",
            "source": "HOSE & Vietstock"
        }
    ],
    "HCM": [
        {
            "id": "hcm-ca-2024",
            "ex_date": "03/01/2024",
            "record_date": "04/01/2024",
            "event_type": "rights_issue",
            "title": "Chào bán thêm cổ phiếu cho cổ đông hiện hữu tỷ lệ 2:1, giá 10,000 đ/CP",
            "cash_amount": 0.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.50,
            "rights_price": 10000.0,
            "ref_price_before": 32800.0,
            "ref_price_after": 25200.0,
            "adjustment_factor": 0.7683,
            "description": "Chào bán 228 triệu cổ phiếu tỷ lệ 2:1 với giá ưu đãi 10,000 đồng/CP.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "hcm-ca-2024-div",
            "ex_date": "18/07/2024",
            "record_date": "19/07/2024",
            "event_type": "dividend_both",
            "title": "Cổ tức năm 2023 đợt 2 bằng tiền mặt 500 đ/CP và thưởng cổ phiếu 15%",
            "cash_amount": 500.0,
            "stock_ratio": 0.15,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 29800.0,
            "ref_price_after": 25480.0,
            "adjustment_factor": 0.8550,
            "description": "Chi trả cổ tức tiền 500 đ/CP và thưởng 15% cổ phiếu.",
            "source": "HOSE & Vietstock"
        }
    ],
    "VND": [
        {
            "id": "vnd-ca-2024",
            "ex_date": "30/05/2024",
            "record_date": "31/05/2024",
            "event_type": "dividend_and_rights",
            "title": "Chào bán quyền mua tỷ lệ 5:1 (giá 10,000 đ/CP) và thưởng cổ phiếu 5%",
            "cash_amount": 0.0,
            "stock_ratio": 0.05,
            "rights_ratio": 0.20,
            "rights_price": 10000.0,
            "ref_price_before": 21500.0,
            "ref_price_after": 18800.0,
            "adjustment_factor": 0.8744,
            "description": "Tăng vốn điều lệ thêm 3,000 tỷ đồng phục vụ margin và thanh khoản.",
            "source": "HOSE & Vietstock"
        }
    ],
    "FPT": [
        {
            "id": "fpt-ca-2024",
            "ex_date": "13/06/2024",
            "record_date": "14/06/2024",
            "event_type": "dividend_both",
            "title": "Cổ tức đợt cuối năm 2023 bằng tiền mặt 10% (1,000 đ/CP) và cổ phiếu 15%",
            "cash_amount": 1000.0,
            "stock_ratio": 0.15,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 133500.0,
            "ref_price_after": 115200.0,
            "adjustment_factor": 0.8630,
            "description": "Chia cổ tức tiền mặt 10% và thưởng cổ phiếu 15% (20:3).",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "fpt-ca-2023",
            "ex_date": "06/06/2023",
            "record_date": "07/06/2023",
            "event_type": "dividend_both",
            "title": "Cổ tức năm 2022 bằng tiền mặt 10% và cổ phiếu 15%",
            "cash_amount": 1000.0,
            "stock_ratio": 0.15,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 84500.0,
            "ref_price_after": 72600.0,
            "adjustment_factor": 0.8592,
            "description": "Truyền thống cổ tức tiền 10% + cổ phiếu 15% hàng năm của FPT.",
            "source": "HOSE & Vietstock"
        }
    ],
    "VNM": [
        {
            "id": "vnm-ca-2026-q2",
            "ex_date": "26/06/2026",
            "record_date": "29/06/2026",
            "execution_date": "17/07/2026",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức đợt 2/2025 bằng tiền mặt tỷ lệ 18% (1,800 đ/CP)",
            "cash_amount": 1800.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 66000.0,
            "ref_price_after": 64200.0,
            "adjustment_factor": 0.9727,
            "description": "Trả cổ tức đợt 2/2025 bằng tiền mặt 1,800 đồng/cổ phiếu (tỷ lệ 18%).",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "vnm-ca-2024-q3",
            "ex_date": "23/09/2024",
            "record_date": "24/09/2024",
            "event_type": "dividend_cash",
            "title": "Tạm ứng cổ tức đợt 1 năm 2024 bằng tiền mặt 15% (1,500 đ/CP)",
            "cash_amount": 1500.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 72500.0,
            "ref_price_after": 71000.0,
            "adjustment_factor": 0.9793,
            "description": "Tạm ứng đợt 1/2024 bằng tiền 1,500 đồng/CP.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "vnm-ca-2024-q1",
            "ex_date": "18/03/2024",
            "record_date": "19/03/2024",
            "event_type": "dividend_cash",
            "title": "Tạm ứng cổ tức đợt 3 năm 2023 bằng tiền mặt 9% (900 đ/CP)",
            "cash_amount": 900.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 68000.0,
            "ref_price_after": 67100.0,
            "adjustment_factor": 0.9868,
            "description": "Trả cổ tức tiền mặt 900 đ/CP.",
            "source": "HOSE & Vietstock"
        }
    ],
    "MWG": [
        {
            "id": "mwg-ca-2024",
            "ex_date": "28/06/2024",
            "record_date": "01/07/2024",
            "event_type": "dividend_cash",
            "title": "Chi trả cổ tức năm 2023 bằng tiền mặt tỷ lệ 5% (500 đ/CP)",
            "cash_amount": 500.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 64500.0,
            "ref_price_after": 64000.0,
            "adjustment_factor": 0.9922,
            "description": "Chi trả cổ tức tiền mặt 500 đồng/cổ phiếu.",
            "source": "HOSE & Vietstock"
        }
    ],
    "MBB": [
        {
            "id": "mbb-ca-2024",
            "ex_date": "23/05/2024",
            "record_date": "24/05/2024",
            "event_type": "dividend_both",
            "title": "Chi trả cổ tức năm 2023 bằng tiền mặt 5% (500 đ/CP) và cổ phiếu 15%",
            "cash_amount": 500.0,
            "stock_ratio": 0.15,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 24800.0,
            "ref_price_after": 21130.0,
            "adjustment_factor": 0.8520,
            "description": "Chia cổ tức tiền 500 đ/CP và 15% cổ phiếu thưởng.",
            "source": "HOSE & Vietstock"
        }
    ],
    "TCB": [
        {
            "id": "tcb-ca-2024",
            "ex_date": "21/06/2024",
            "record_date": "24/06/2024",
            "event_type": "dividend_both",
            "title": "Chi trả cổ tức tiền mặt 15% (1,500 đ/CP) và thưởng cổ phiếu tỷ lệ 100% (1:1)",
            "cash_amount": 1500.0,
            "stock_ratio": 1.00,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 49000.0,
            "ref_price_after": 23750.0,
            "adjustment_factor": 0.4847,
            "description": "Sự kiện lịch sử thưởng cổ phiếu 1:1 và trả cổ tức tiền 1,500 đ/CP, vốn điều lệ tăng gấp đôi lên 70,450 tỷ.",
            "source": "HOSE & Vietstock"
        }
    ],
    "ACB": [
        {
            "id": "acb-ca-2024",
            "ex_date": "03/06/2024",
            "record_date": "04/06/2024",
            "event_type": "dividend_both",
            "title": "Chi trả cổ tức năm 2023 bằng tiền mặt 10% (1,000 đ/CP) và cổ phiếu 15%",
            "cash_amount": 1000.0,
            "stock_ratio": 0.15,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 25600.0,
            "ref_price_after": 21390.0,
            "adjustment_factor": 0.8355,
            "description": "Cổ tức tiền 10% và cổ phiếu 15%.",
            "source": "HOSE & Vietstock"
        }
    ],
    "CTG": [
        {
            "id": "ctg-ca-2023",
            "ex_date": "30/11/2023",
            "record_date": "01/12/2023",
            "event_type": "dividend_stock",
            "title": "Chi trả cổ tức bằng cổ phiếu tỷ lệ 11.74%",
            "cash_amount": 0.0,
            "stock_ratio": 0.1174,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 29800.0,
            "ref_price_after": 26670.0,
            "adjustment_factor": 0.8950,
            "description": "Tăng vốn điều lệ qua phát hành cổ phiếu trả cổ tức tỷ lệ 11.74%.",
            "source": "HOSE & Vietstock"
        }
    ],
    "DGC": [
        {
            "id": "dgc-ca-2024",
            "ex_date": "19/12/2024",
            "record_date": "20/12/2024",
            "event_type": "dividend_cash",
            "title": "Tạm ứng cổ tức năm 2024 bằng tiền mặt tỷ lệ 30% (3,000 đ/CP)",
            "cash_amount": 3000.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 115000.0,
            "ref_price_after": 112000.0,
            "adjustment_factor": 0.9739,
            "description": "Tạm ứng cổ tức tiền mặt 3,000 đồng/CP.",
            "source": "HOSE & Vietstock"
        }
    ],
    "NKG": [
        {
            "id": "nkg-ca-2024",
            "ex_date": "04/07/2024",
            "record_date": "05/07/2024",
            "event_type": "dividend_and_rights",
            "title": "Thưởng cổ phiếu tỷ lệ 20% và chào bán quyền mua 50% giá 12,000 đ/CP",
            "cash_amount": 0.0,
            "stock_ratio": 0.20,
            "rights_ratio": 0.50,
            "rights_price": 12000.0,
            "ref_price_before": 25500.0,
            "ref_price_after": 18530.0,
            "adjustment_factor": 0.7267,
            "description": "Tăng vốn tài trợ Dự án Nhà máy Tôn Nam Kim Phú Mỹ.",
            "source": "HOSE & Vietstock"
        }
    ],
    "HSG": [
        {
            "id": "hsg-ca-2024",
            "ex_date": "24/04/2024",
            "record_date": "25/04/2024",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức niên độ 2022-2023 bằng tiền mặt tỷ lệ 5% (500 đ/CP)",
            "cash_amount": 500.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 21800.0,
            "ref_price_after": 21300.0,
            "adjustment_factor": 0.9771,
            "description": "Trả cổ tức tiền mặt 500 đồng/CP.",
            "source": "HOSE & Vietstock"
        }
    ],
    "KBC": [
        {
            "id": "kbc-ca-2023",
            "ex_date": "28/06/2023",
            "record_date": "29/06/2023",
            "event_type": "dividend_cash",
            "title": "Chi trả cổ tức đợt 1/2022 bằng tiền mặt tỷ lệ 20% (2,000 đ/CP)",
            "cash_amount": 2000.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 29500.0,
            "ref_price_after": 27500.0,
            "adjustment_factor": 0.9322,
            "description": "Chi trả cổ tức tiền mặt 2,000 đồng/cổ phiếu.",
            "source": "HOSE & Vietstock"
        }
    ],
    "PVS": [
        {
            "id": "pvs-ca-2026-div-stock",
            "ex_date": "14/09/2026",
            "record_date": "15/09/2026",
            "event_type": "dividend_stock",
            "title": "Trả cổ tức năm 2025 bằng cổ phiếu, tỷ lệ 100:20 (20%)",
            "cash_amount": 0.0,
            "stock_ratio": 0.20,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 40000.0,
            "ref_price_after": 33330.0,
            "adjustment_factor": 0.8333333333333334,
            "description": "Trả cổ tức năm 2025 bằng cổ phiếu cho cổ đông hiện hữu tỷ lệ 100:20 (tương ứng 20% cổ phiếu mới phát hành thêm).",
            "source": "HNX & Vietstock"
        },
        {
            "id": "pvs-ca-2024-cash",
            "ex_date": "29/08/2024",
            "record_date": "30/08/2024",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2023 bằng tiền mặt tỷ lệ 7% (700 đ/CP)",
            "cash_amount": 700.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 42500.0,
            "ref_price_after": 41800.0,
            "adjustment_factor": 0.9835,
            "description": "Chi trả cổ tức tiền mặt 700 đồng/cổ phiếu.",
            "source": "HNX & Vietstock"
        }
    ]
}


# Bộ nhớ tạm in-memory
_CORPORATE_ACTIONS_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def load_corporate_actions_cache():
    """Tải bộ nhớ sự kiện quyền từ disk và bổ sung curated data."""
    global _CORPORATE_ACTIONS_CACHE
    _ensure_cache_dir()
    _CORPORATE_ACTIONS_CACHE = {}

    # Nạp từ file nếu có
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                disk_data = json.load(f)
                if isinstance(disk_data, dict):
                    _CORPORATE_ACTIONS_CACHE = disk_data
        except Exception:
            _CORPORATE_ACTIONS_CACHE = {}

    # Nạp/Merge các sự kiện curated vào cache
    for ticker, events in CURATED_CORPORATE_ACTIONS.items():
        if ticker not in _CORPORATE_ACTIONS_CACHE:
            _CORPORATE_ACTIONS_CACHE[ticker] = events
        else:
            existing_ids = {e.get("id") or f"{e.get('ex_date')}_{e.get('event_type')}" for e in _CORPORATE_ACTIONS_CACHE[ticker]}
            for ev in events:
                ev_id = ev.get("id") or f"{ev.get('ex_date')}_{ev.get('event_type')}"
                if ev_id not in existing_ids:
                    _CORPORATE_ACTIONS_CACHE[ticker].append(ev)


def save_corporate_actions_cache():
    """Lưu bộ nhớ sự kiện quyền xuống disk."""
    _ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_CORPORATE_ACTIONS_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# Khởi tạo cache khi import
load_corporate_actions_cache()


def calculate_vas_adjustment_factor(
    event: Dict[str, Any],
    ref_price_before: Optional[float] = None
) -> float:
    """
    Tính hệ số điều chỉnh giá (k) theo công thức chuẩn mực của Sở GDCK (HOSE / HNX):
    P_adj = (P_c - D + P_issue * alpha) / (1 + beta + alpha)
    k = P_adj / P_c
    """
    if event.get("adjustment_factor") and float(event["adjustment_factor"]) > 0:
        return float(event["adjustment_factor"])

    p_c = ref_price_before or float(event.get("ref_price_before") or 25000.0)
    d_cash = float(event.get("cash_amount") or 0.0)
    beta = float(event.get("stock_ratio") or 0.0)
    alpha = float(event.get("rights_ratio") or 0.0)
    p_issue = float(event.get("rights_price") or 0.0)

    denominator = 1.0 + beta + alpha
    if denominator <= 0 or p_c <= 0:
        return 1.0

    numerator = p_c - d_cash + (p_issue * alpha)
    p_adj = max(100.0, numerator / denominator)
    k = p_adj / p_c
    return round(k, 4)


def get_ticker_corporate_actions(ticker: str) -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả các sự kiện quyền / ngày GDKHQ của 1 mã cổ phiếu, sắp xếp mới nhất lên đầu."""
    clean_ticker = ticker.upper().strip()
    if not _CORPORATE_ACTIONS_CACHE:
        load_corporate_actions_cache()
    events = _CORPORATE_ACTIONS_CACHE.get(clean_ticker, [])
    # Sắp xếp giảm dần theo ngày GDKHQ
    def _sort_key(ev):
        d = parse_action_date(ev.get("ex_date", ""))
        return d or date(2000, 1, 1)

    return sorted(events, key=_sort_key, reverse=True)


def adjust_target_price_for_corporate_actions(
    ticker: str,
    report_date_str: str,
    raw_target_price: float,
    current_market_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Thuật toán kiểm tra và điều chỉnh giá mục tiêu ban đầu của CTCK nếu báo cáo được phát hành
    TRƯỚC ngày Giao dịch không hưởng quyền (GDKHQ).
    
    Quy tắc:
    - Nếu T_report >= T_ex: Báo cáo phát hành sau ngày chia, CTCK đã định giá trên cơ sở vốn mới -> Giữ nguyên.
    - Nếu T_report < T_ex: Báo cáo phát hành trước ngày chia, giá mục tiêu cũ cần nhân hệ số pha loãng k.
    
    Trả về Dict gồm:
    - raw_target_price: Giá mục tiêu ban đầu
    - adjusted_target_price: Giá mục tiêu sau điều chỉnh
    - is_price_adjusted: True nếu có ít nhất 1 sự kiện chia sau ngày ra báo cáo
    - cumulative_factor: Tích các hệ số điều chỉnh
    - applied_events: Danh sách các sự kiện GDKHQ đã áp dụng
    - notes: Chuỗi ghi chú minh bạch cho Nhà đầu tư
    """
    clean_ticker = ticker.upper().strip()
    if not raw_target_price or raw_target_price <= 0:
        return {
            "raw_target_price": raw_target_price,
            "adjusted_target_price": raw_target_price,
            "is_price_adjusted": False,
            "cumulative_factor": 1.0,
            "applied_events": [],
            "notes": ""
        }

    rep_date = parse_action_date(report_date_str)
    if not rep_date:
        return {
            "raw_target_price": raw_target_price,
            "adjusted_target_price": raw_target_price,
            "is_price_adjusted": False,
            "cumulative_factor": 1.0,
            "applied_events": [],
            "notes": ""
        }

    actions = get_ticker_corporate_actions(clean_ticker)
    applied_events = []
    cumulative_factor = 1.0
    notes_list = []

    today = date.today()

    # Duyệt qua các sự kiện quyền theo thứ tự thời gian từ cũ đến mới (sau ngày ra báo cáo)
    chronological_actions = sorted(
        actions,
        key=lambda x: parse_action_date(x.get("ex_date", "")) or date(2000, 1, 1)
    )

    curr_p = float(raw_target_price)

    for ev in chronological_actions:
        ex_d = parse_action_date(ev.get("ex_date", ""))
        if not ex_d:
            continue

        # Chỉ xét sự kiện nếu ngày GDKHQ xảy ra SAU ngày phát hành báo cáo và TRƯỚC HOẶC BẰNG ngày hiện tại
        if rep_date < ex_d <= today:
            k = calculate_vas_adjustment_factor(ev, ref_price_before=curr_p)
            if 0.1 <= k < 0.999:
                curr_p = curr_p * k
                cumulative_factor *= k
                applied_events.append(ev)

                # Soạn ghi chú tóm tắt
                ex_str = ev.get("ex_date", "")
                title = ev.get("title") or ev.get("description") or "Điều chỉnh quyền"
                notes_list.append(f"GDKHQ {ex_str}: {title}")

    is_adjusted = len(applied_events) > 0
    adj_price = round(curr_p, -2) if is_adjusted else raw_target_price

    if is_adjusted:
        notes_str = (
            f"Định giá gốc {raw_target_price:,.0f} đ (ngày {report_date_str}) phát hành trước ngày GDKHQ. "
            f"Đã tự động điều chỉnh về {adj_price:,.0f} đ theo tỷ lệ chia cổ tức/thưởng cổ phiếu "
            f"({'; '.join(notes_list)}) để phản ánh chính xác thị giá sau điều chỉnh."
        )
    else:
        notes_str = ""

    return {
        "raw_target_price": float(raw_target_price),
        "adjusted_target_price": float(adj_price),
        "is_price_adjusted": is_adjusted,
        "cumulative_factor": round(cumulative_factor, 4),
        "applied_events": applied_events,
        "notes": notes_str
    }


# ---------------------------------------------------------------------------
# CƠ CHẾ ĐỒNG BỘ ONLINE TỰ ĐỘNG & BỔ SUNG SỰ KIỆN TÙY CHỈNH (FALLBACK ĐA TẦNG)
# ---------------------------------------------------------------------------

def parse_simplize_event(item: Dict[str, Any], ticker: str) -> Optional[Dict[str, Any]]:
    """Bóc tách sự kiện tài chính từ API mở Simplize (nguồn chuẩn hóa từ HOSE/HNX/VSD & Vietstock)."""
    desc = item.get("description") or ""
    title = item.get("title") or ""
    event_type_name = item.get("eventTypeName") or ""
    text = f"{title} {desc} {event_type_name}"
    
    ex_date = item.get("exDividendDate")
    record_date = item.get("recordDate")
    exec_date = item.get("executionDate")
    
    if not ex_date:
        return None
        
    cash_amount = 0.0
    stock_ratio = 0.0
    rights_ratio = 0.0
    rights_price = 0.0
    ev_type = "other"
    
    # 1. Cổ tức tiền mặt
    if "tiền" in text.lower():
        m_cash = re.search(r"([0-9]{1,3}(?:[.,][0-9]{3})*)\s*(?:đồng|đ|vnd|/cp)", text, re.IGNORECASE)
        if m_cash:
            val_str = m_cash.group(1).replace(".", "").replace(",", "")
            try:
                cash_amount = float(val_str)
                ev_type = "dividend_cash"
            except Exception:
                pass
        if cash_amount == 0:
            m_pct = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", text)
            if m_pct:
                pct = float(m_pct.group(1))
                if pct <= 100:
                    cash_amount = pct * 100.0
                    ev_type = "dividend_cash"
                    
    # 2. Cổ tức cổ phiếu / Cổ phiếu thưởng
    if "cổ phiếu" in text.lower() or "thưởng" in text.lower():
        m_ratio = re.search(r"tỷ lệ\s*([0-9]+)\s*:\s*([0-9]+)", text, re.IGNORECASE)
        if m_ratio:
            a, b = float(m_ratio.group(1)), float(m_ratio.group(2))
            if a > 0 and b > 0:
                stock_ratio = b / a if a >= b else a / b
                ev_type = "bonus_share" if "thưởng" in text.lower() else "dividend_stock"
        else:
            m_pct = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", text)
            if m_pct and "tiền" not in text.lower():
                stock_ratio = float(m_pct.group(1)) / 100.0
                ev_type = "dividend_stock"

    # 3. Phát hành thêm / Quyền mua
    if "quyền mua" in text.lower() or "phát hành thêm" in text.lower():
        ev_type = "rights_issue"
        m_ratio = re.search(r"tỷ lệ\s*([0-9]+)\s*:\s*([0-9]+)", text, re.IGNORECASE)
        if m_ratio:
            a, b = float(m_ratio.group(1)), float(m_ratio.group(2))
            if a > 0 and b > 0:
                rights_ratio = b / a if a >= b else a / b
        m_price = re.search(r"giá\s*([0-9]{1,3}(?:[.,][0-9]{3})*)", text, re.IGNORECASE)
        if m_price:
            try:
                rights_price = float(m_price.group(1).replace(".", "").replace(",", ""))
            except Exception:
                pass

    if cash_amount > 0 and (stock_ratio > 0 or rights_ratio > 0):
        ev_type = "dividend_both"

    if cash_amount == 0 and stock_ratio == 0 and rights_ratio == 0:
        return None

    # Tính hệ số điều chỉnh ước tính
    ref_p = 50000.0
    denom = 1.0 + stock_ratio + rights_ratio
    factor = round(((ref_p - cash_amount + rights_price * rights_ratio) / denom) / ref_p, 4) if denom > 0 else 1.0

    return {
        "id": f"{ticker.lower()}-ca-{ex_date.replace('/', '')}-{ev_type}",
        "ex_date": ex_date,
        "record_date": record_date or "",
        "execution_date": exec_date or "",
        "event_type": ev_type,
        "title": title or desc,
        "description": desc or title,
        "cash_amount": cash_amount,
        "stock_ratio": round(stock_ratio, 4),
        "rights_ratio": round(rights_ratio, 4),
        "rights_price": rights_price,
        "adjustment_factor": factor,
        "source": "Sở GDCK / Simplize Open API"
    }


async def sync_ticker_corporate_actions_online(ticker: str) -> List[Dict[str, Any]]:
    """
    Tự động đồng bộ hóa lịch sự kiện quyền & ngày GDKHQ mới nhất từ Open Financial API.
    Giải quyết triệt để việc các trang web như Vietstock, CafeF chặn bot hoặc yêu cầu anti-forgery token.
    Tự động nạp, khử trùng lặp và lưu trữ bền vững vào disk cache.
    """
    import asyncio
    import urllib.request

    clean_ticker = ticker.upper().strip()
    url = f"https://api.simplize.vn/api/company/events/list?ticker={clean_ticker}"
    
    def _fetch_simplize():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=4) as response:
            return json.loads(response.read().decode("utf-8"))

    try:
        loop = asyncio.get_event_loop()
        res_data = await loop.run_in_executor(None, _fetch_simplize)
        raw_items = res_data.get("data", []) if isinstance(res_data, dict) else []
        
        parsed_events = []
        for item in raw_items:
            parsed = parse_simplize_event(item, clean_ticker)
            if parsed:
                parsed_events.append(parsed)
                
        if parsed_events:
            if clean_ticker not in _CORPORATE_ACTIONS_CACHE:
                _CORPORATE_ACTIONS_CACHE[clean_ticker] = []
            
            existing_ex_dates = {
                f"{e.get('ex_date')}_{e.get('event_type')}" for e in _CORPORATE_ACTIONS_CACHE[clean_ticker]
            }
            new_added = 0
            for ev in parsed_events:
                key = f"{ev.get('ex_date')}_{ev.get('event_type')}"
                if key not in existing_ex_dates:
                    _CORPORATE_ACTIONS_CACHE[clean_ticker].append(ev)
                    existing_ex_dates.add(key)
                    new_added += 1
                    
            if new_added > 0:
                save_corporate_actions_cache()
                
    except Exception as e:
        # Fallback im lặng nếu offline hoặc timeout, dữ liệu curated vẫn bảo đảm hoạt động
        pass

    return get_ticker_corporate_actions(clean_ticker)


def add_custom_corporate_action(ticker: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cho phép Nhà đầu tư hoặc Chuyên viên phân tích chủ động bổ sung sự kiện quyền mới
    khi doanh nghiệp vừa công bố Nghị quyết HĐQT/ĐHĐCĐ mà các trang web tài chính chưa kịp cập nhật.
    """
    clean_ticker = ticker.upper().strip()
    if clean_ticker not in _CORPORATE_ACTIONS_CACHE:
        _CORPORATE_ACTIONS_CACHE[clean_ticker] = []

    ex_date = action_data.get("ex_date", "")
    ev_type = action_data.get("event_type", "dividend_cash")
    action_id = action_data.get("id") or f"{clean_ticker.lower()}-ca-{ex_date.replace('/', '')}-{ev_type}"
    action_data["id"] = action_id
    action_data["source"] = action_data.get("source") or "Công bố thông tin trực tiếp / Nghị quyết HĐQT"

    _CORPORATE_ACTIONS_CACHE[clean_ticker] = [
        e for e in _CORPORATE_ACTIONS_CACHE[clean_ticker] if e.get("id") != action_id
    ]
    _CORPORATE_ACTIONS_CACHE[clean_ticker].append(action_data)
    save_corporate_actions_cache()

    return action_data
