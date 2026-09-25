"""
Corporate Actions & Ex-Dividend Date Management Module
Xử lý sự kiện quyền (Cổ tức tiền mặt, Cổ tức cổ phiếu, Thưởng cổ phiếu, Phát hành thêm quyền mua)
và tự động chuẩn hóa, điều chỉnh giá mục tiêu (Target Price) của các CTCK sau ngày GDKHQ.
Nguồn tham chiếu: Vietstock (https://finance.vietstock.vn/lich-su-kien.htm), HOSE, HNX, CafeF.
"""

import os
import json
import re
import time
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
            "ref_price_before": 42500.0,
            "ref_price_after": 35420.0,
            "adjustment_factor": 0.8333,
            "description": "Chi trả cổ tức năm 2025 bằng cổ phiếu tỷ lệ 20% (sở hữu 100 cổ phiếu được nhận 20 cổ phiếu mới). Quy mô phát hành gần 96 triệu cổ phiếu.",
            "source": "HNX & Vietstock"
        },
        {
            "id": "pvs-ca-2025-div-stock",
            "ex_date": "27/11/2025",
            "record_date": "28/11/2025",
            "event_type": "dividend_stock",
            "title": "Trả cổ tức năm 2024 bằng cổ phiếu, tỷ lệ 100:7 (7%)",
            "cash_amount": 0.0,
            "stock_ratio": 0.07,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 38600.0,
            "ref_price_after": 36070.0,
            "adjustment_factor": 0.9346,
            "description": "Chi trả cổ tức năm 2024 bằng cổ phiếu tỷ lệ 7% (sở hữu 100 cổ phiếu được nhận 7 cổ phiếu mới).",
            "source": "HNX & Vietstock"
        },
        {
            "id": "pvs-ca-2024-div-cash",
            "ex_date": "29/08/2024",
            "record_date": "30/08/2024",
            "execution_date": "27/09/2024",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2023 bằng tiền mặt tỷ lệ 7% (700 đ/CP)",
            "cash_amount": 700.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 41200.0,
            "ref_price_after": 40500.0,
            "adjustment_factor": 0.9830,
            "description": "Thực hiện chi trả cổ tức năm 2023 bằng tiền mặt với tỷ lệ 7% (700 đồng/cổ phiếu).",
            "source": "HNX & Vietstock"
        },
        {
            "id": "pvs-ca-2023-div-cash",
            "ex_date": "28/08/2023",
            "record_date": "29/08/2023",
            "execution_date": "27/09/2023",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2022 bằng tiền mặt tỷ lệ 7% (700 đ/CP)",
            "cash_amount": 700.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 34800.0,
            "ref_price_after": 34100.0,
            "adjustment_factor": 0.9799,
            "description": "Chi trả cổ tức năm 2022 bằng tiền mặt tỷ lệ 7% (700 đ/CP).",
            "source": "HNX & Vietstock"
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
            "id": "ctg-ca-2026",
            "ex_date": "23/07/2026",
            "record_date": "24/07/2026",
            "execution_date": "23/07/2026",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2025 bằng tiền, 450 đồng/CP",
            "cash_amount": 450.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 35000.0,
            "ref_price_after": 34550.0,
            "adjustment_factor": 0.9871,
            "description": "Chi trả cổ tức năm 2025 bằng tiền mặt với tỷ lệ 4.5% (450 đồng/cổ phiếu).",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ctg-ca-2025-stock",
            "ex_date": "17/12/2025",
            "record_date": "18/12/2025",
            "execution_date": "17/12/2025",
            "event_type": "dividend_stock",
            "title": "Trả cổ tức bằng cổ phiếu, tỷ lệ 100:44.63658403",
            "cash_amount": 0.0,
            "stock_ratio": 0.4463658403,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 32000.0,
            "ref_price_after": 22120.0,
            "adjustment_factor": 0.6914,
            "description": "Phát hành cổ phiếu để trả cổ tức theo tỷ lệ 100:44.63658403 (cổ đông sở hữu 100 cổ phiếu nhận thêm 44.64 cổ phiếu mới).",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ctg-ca-2025-cash",
            "ex_date": "14/10/2025",
            "record_date": "15/10/2025",
            "execution_date": "14/10/2025",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2024 bằng tiền, 450 đồng/CP",
            "cash_amount": 450.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 30000.0,
            "ref_price_after": 29550.0,
            "adjustment_factor": 0.9850,
            "description": "Chi trả cổ tức năm 2024 bằng tiền mặt 450 đồng/cổ phiếu.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ctg-ca-2023",
            "ex_date": "30/11/2023",
            "record_date": "01/12/2023",
            "execution_date": "30/11/2023",
            "event_type": "dividend_stock",
            "title": "Chi trả cổ tức năm 2020 bằng cổ phiếu, tỷ lệ 100:11.7415",
            "cash_amount": 0.0,
            "stock_ratio": 0.117415,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 29800.0,
            "ref_price_after": 26670.0,
            "adjustment_factor": 0.8950,
            "description": "Tăng vốn điều lệ qua phát hành cổ phiếu trả cổ tức tỷ lệ 100:11.7415.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ctg-ca-2021-cash",
            "ex_date": "14/12/2021",
            "record_date": "15/12/2021",
            "execution_date": "14/12/2021",
            "event_type": "dividend_cash",
            "title": "Trả cổ tức năm 2020 bằng tiền, 800 đồng/CP",
            "cash_amount": 800.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "adjustment_factor": 0.9750,
            "description": "Chi trả cổ tức năm 2020 bằng tiền mặt 800 đồng/cổ phiếu.",
            "source": "HOSE & Vietstock"
        },
        {
            "id": "ctg-ca-2021-stock",
            "ex_date": "07/07/2021",
            "record_date": "08/07/2021",
            "execution_date": "07/07/2021",
            "event_type": "dividend_stock",
            "title": "Trả cổ tức bằng cổ phiếu, tỷ lệ 100:29.0695",
            "cash_amount": 0.0,
            "stock_ratio": 0.290695,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "adjustment_factor": 0.7748,
            "description": "Chi trả cổ tức bằng cổ phiếu tỷ lệ 100:29.0695.",
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
    ],
    "TRC": [
        {
            "id": "trc-ca-15092026-bonus_share",
            "ex_date": "15/09/2026",
            "record_date": "16/09/2026",
            "execution_date": "15/09/2026",
            "event_type": "bonus_share",
            "title": "TRC: Thông báo ngày ĐKCC phát hành cổ phiếu để tăng vốn cổ phần từ NVCSH",
            "description": "Thưởng cổ phiếu, tỷ lệ 1:3 (1 cổ phiếu được thêm 3 cổ phiếu mới)",
            "cash_amount": 0.0,
            "stock_ratio": 3.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "adjustment_factor": 0.25,
            "source": "Sở GDCK / Simplize Open API"
        },
        {
            "id": "trc-ca-31072026-dividend_cash",
            "ex_date": "31/07/2026",
            "record_date": "03/08/2026",
            "execution_date": "25/09/2026",
            "event_type": "dividend_cash",
            "title": "TRC: Thông báo về ngày đăng ký cuối cùng chi trả cổ tức năm 2025 bằng tiền mặt",
            "description": "Trả cổ tức năm 2025 bằng tiền, 3,000 đồng/CP",
            "cash_amount": 3000.0,
            "stock_ratio": 0.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "adjustment_factor": None,
            "source": "Sở GDCK / Simplize Open API"
        }
    ],
    "VHM": [
        {
            "id": "vhm-ca-06082026-dividend_stock",
            "ex_date": "06/08/2026",
            "record_date": "07/08/2026",
            "execution_date": "06/08/2026",
            "event_type": "dividend_stock",
            "title": "VHM: Thông báo trả cổ tức năm 2025 bằng cổ phiếu, tỷ lệ 1:1 (100%)",
            "description": "Trả cổ tức bằng cổ phiếu tỷ lệ 1:1 (cổ đông sở hữu 1 cổ phiếu được nhận thêm 1 cổ phiếu mới)",
            "cash_amount": 0.0,
            "stock_ratio": 1.0,
            "rights_ratio": 0.0,
            "rights_price": 0.0,
            "ref_price_before": 130800.0,
            "ref_price_after": 65400.0,
            "adjustment_factor": 0.5,
            "source": "HOSE & Vietstock"
        }
    ]
}


# Bộ nhớ tạm in-memory
_CORPORATE_ACTIONS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_SYNCED_TICKERS: Dict[str, float] = {}


def load_corporate_actions_cache():
    """Tải bộ nhớ sự kiện quyền từ disk và bổ sung curated data."""
    global _CORPORATE_ACTIONS_CACHE, _SYNCED_TICKERS
    _ensure_cache_dir()
    _CORPORATE_ACTIONS_CACHE = {}

    # Nạp từ file nếu có
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                disk_data = json.load(f)
                if isinstance(disk_data, dict):
                    _CORPORATE_ACTIONS_CACHE = disk_data
                    now = time.time()
                    for t, ev_list in disk_data.items():
                        if ev_list:
                            _SYNCED_TICKERS[t] = now
        except Exception:
            _CORPORATE_ACTIONS_CACHE = {}

    # Nạp/Merge các sự kiện curated vào cache (Curated là nguồn chuẩn hóa cao nhất)
    for ticker, events in CURATED_CORPORATE_ACTIONS.items():
        if ticker not in _CORPORATE_ACTIONS_CACHE:
            _CORPORATE_ACTIONS_CACHE[ticker] = list(events)
        else:
            existing_map = {
                (e.get("id") or f"{e.get('ex_date')}_{e.get('event_type')}"): idx
                for idx, e in enumerate(_CORPORATE_ACTIONS_CACHE[ticker])
            }
            for ev in events:
                ev_id = ev.get("id") or f"{ev.get('ex_date')}_{ev.get('event_type')}"
                if ev_id in existing_map:
                    _CORPORATE_ACTIONS_CACHE[ticker][existing_map[ev_id]].update(ev)
                else:
                    _CORPORATE_ACTIONS_CACHE[ticker].append(ev)
        _SYNCED_TICKERS[ticker] = time.time()

    save_corporate_actions_cache()


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
    Tính hệ số điều chỉnh giá (k) theo công thức chuẩn mực của Sở GDCK (HOSE / HNX / UBCKNN):
    P_adj = (P_c - D + P_issue * alpha) / (1 + beta + alpha)
    k = P_adj / P_c
    
    Trong đó:
    - P_c: Giá trước ngày GDKHQ (hoặc Giá mục tiêu TP ban đầu của CTCK)
    - D: Cổ tức bằng tiền mặt (VNĐ/CP)
    - beta: Tỷ lệ cổ tức bằng cổ phiếu / cổ phiếu thưởng (ví dụ: 10% -> 0.1, 4:3 -> 0.75)
    - alpha: Tỷ lệ phát hành quyền mua thêm (ví dụ: 10:1 -> 0.1)
    - P_issue: Giá phát hành quyền mua (VNĐ/CP)
    """
    d_cash = float(event.get("cash_amount") or 0.0)
    beta = float(event.get("stock_ratio") or 0.0)
    alpha = float(event.get("rights_ratio") or 0.0)
    p_issue = float(event.get("rights_price") or 0.0)

    # 1. Thuần chia cổ tức bằng cổ phiếu / cổ phiếu thưởng (D = 0, alpha = 0, beta > 0)
    # Hệ số k = 1 / (1 + beta) là hằng số toán học độc lập hoàn toàn với giá tham chiếu
    if d_cash == 0.0 and alpha == 0.0:
        if beta > 0:
            return round(1.0 / (1.0 + beta), 4)
        return 1.0

    # 2. Có cổ tức tiền mặt hoặc quyền mua: phụ thuộc trực tiếp vào giá tham chiếu P_c
    p_c = ref_price_before or float(event.get("ref_price_before") or 0.0)
    if p_c <= 0:
        if event.get("adjustment_factor") and float(event["adjustment_factor"]) > 0:
            return float(event["adjustment_factor"])
        p_c = 50000.0

    effective_rights_val = (p_issue * alpha) if (alpha > 0 and p_issue < p_c) else 0.0
    effective_alpha = alpha if (alpha > 0 and p_issue < p_c) else 0.0
    denom = 1.0 + beta + effective_alpha
    if denom <= 0:
        return 1.0

    numerator = p_c - d_cash + effective_rights_val
    p_adj = max(100.0, numerator / denom)
    k = p_adj / p_c
    return round(k, 4)


def get_ticker_corporate_actions(ticker: str, auto_sync: bool = True) -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả các sự kiện quyền / ngày GDKHQ của 1 mã cổ phiếu, sắp xếp mới nhất lên đầu (đã khử trùng lặp)."""
    clean_ticker = ticker.upper().strip()
    if not _CORPORATE_ACTIONS_CACHE:
        load_corporate_actions_cache()

    # Tự động đồng bộ hóa trực tuyến nếu mã chưa có trong cache hoặc chưa từng sync
    if auto_sync and (clean_ticker not in _CORPORATE_ACTIONS_CACHE or clean_ticker not in _SYNCED_TICKERS):
        sync_ticker_corporate_actions_sync(clean_ticker)

    raw_events = _CORPORATE_ACTIONS_CACHE.get(clean_ticker, [])
    
    # Khử trùng lặp chuẩn xác theo ngày GDKHQ và loại sự kiện
    dedup_events = []
    seen_keys = set()
    for ev in raw_events:
        ex_d = str(ev.get("ex_date", "")).strip()
        ev_type = str(ev.get("event_type", "")).strip()
        key = f"{ex_d}_{ev_type}"
        if key not in seen_keys:
            seen_keys.add(key)
            dedup_events.append(dict(ev))
        else:
            # Ưu tiên bản ghi curated nếu bản ghi trước là scraped
            for idx, existing in enumerate(dedup_events):
                ex_key = f"{str(existing.get('ex_date', '')).strip()}_{str(existing.get('event_type', '')).strip()}"
                if ex_key == key:
                    if str(ev.get("id", "")).startswith(f"{clean_ticker.lower()}-ca-"):
                        dedup_events[idx] = dict(ev)
                    break

    def _sort_key(ev):
        d = parse_action_date(ev.get("ex_date", ""))
        return d or date(2000, 1, 1)

    return sorted(dedup_events, key=_sort_key, reverse=True)


def adjust_target_price_for_corporate_actions(
    ticker: str,
    report_date_str: str,
    raw_target_price: float,
    current_market_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Thuật toán kiểm tra và điều chỉnh giá mục tiêu ban đầu của CTCK nếu báo cáo được phát hành
    TRƯỚC ngày Giao dịch không hưởng quyền (GDKHQ).
    
    Quy tắc chuẩn hóa theo Quy chế niêm yết & giao dịch của Sở GDCK (HOSE / HNX):
    - Nếu T_report >= T_ex: Báo cáo phát hành sau ngày chia, CTCK đã định giá trên cơ sở vốn mới -> Giữ nguyên.
    - Nếu T_report < T_ex: Báo cáo phát hành trước ngày chia, giá mục tiêu cũ cần điều chỉnh:
      + Chia cổ tức bằng tiền: P_adj = P_c - D
      + Cổ tức CP / thưởng CP: P_adj = P_c / (1 + beta)
      + Quyền mua phát hành mới: P_adj = (P_c + P_issue * alpha) / (1 + alpha) (với P_issue < P_c)
      + Tổng quát đa quyền: P_adj = (P_c - D + P_issue * alpha) / (1 + beta + alpha)
    
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

    actions = get_ticker_corporate_actions(clean_ticker, auto_sync=True)
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
            d_cash = float(ev.get("cash_amount") or 0.0)
            beta = float(ev.get("stock_ratio") or 0.0)
            alpha = float(ev.get("rights_ratio") or 0.0)
            p_issue = float(ev.get("rights_price") or 0.0)

            # Quyền mua chỉ làm pha loãng giá nếu giá phát hành thấp hơn giá hiện tại
            effective_rights_val = (p_issue * alpha) if (alpha > 0 and (curr_p <= 0 or p_issue < curr_p)) else 0.0
            effective_alpha = alpha if (alpha > 0 and (curr_p <= 0 or p_issue < curr_p)) else 0.0

            denom = 1.0 + beta + effective_alpha
            if denom > 0 and curr_p > 0:
                # Tính trực tiếp theo công thức chuẩn của Sở GDCK (HOSE / HNX / UBCKNN):
                # P_adj = (P_c - D + P_issue * alpha) / (1 + beta + alpha)
                p_adj = max(100.0, (curr_p - d_cash + effective_rights_val) / denom)
                
                # Áp dụng nếu có sự điều chỉnh giảm giá hợp lệ
                if p_adj < curr_p - 1e-4:
                    k = p_adj / curr_p
                    prev_p = curr_p
                    curr_p = p_adj
                    cumulative_factor *= k

                    ev_applied = dict(ev)
                    ev_applied["adjustment_factor"] = round(k, 4)
                    ev_applied["applied_price_before"] = round(prev_p, -2)
                    ev_applied["applied_price_after"] = round(p_adj, -2)
                    applied_events.append(ev_applied)

                    # Soạn ghi chú tóm tắt
                    ex_str = ev.get("ex_date", "")
                    title = ev.get("title") or ev.get("description") or "Điều chỉnh quyền"
                    notes_list.append(f"GDKHQ {ex_str}: {title}")

    is_adjusted = len(applied_events) > 0
    if is_adjusted:
        # Bước giá chuẩn HOSE/HNX: 10.000 - 49.950 bước 50đ; >= 50.000 bước 100đ; < 10.000 bước 10đ
        if 10000.0 <= curr_p < 50000.0:
            adj_price = round(curr_p / 50.0) * 50.0
        elif curr_p >= 50000.0:
            adj_price = round(curr_p / 100.0) * 100.0
        else:
            adj_price = round(curr_p / 10.0) * 10.0
    else:
        adj_price = raw_target_price

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


def get_corporate_actions_dilution_factor(
    ticker: str,
    base_shares_mil: Optional[float] = None,
    as_of_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Xác định hệ số pha loãng và điều chỉnh số lượng cổ phiếu lưu hành, EPS, BVPS,
    và các mô hình định giá (DCF, Graham, P/E, P/B) do các sự kiện quyền:
    - Cổ tức bằng cổ phiếu (dividend_stock)
    - Thưởng cổ phiếu từ NVCSH (bonus_share)
    - Phát hành quyền mua cho cổ đông hiện hữu (rights_issue)
    
    Quy tắc:
    - Chỉ áp dụng các sự kiện có ngày GDKHQ ex_date <= as_of_date (mặc định là ngày hôm nay).
    - Kiểm tra xem base_shares_mil trong cơ sở dữ liệu đã phản ánh số lượng cổ phiếu mới hay chưa:
      + Nếu base_shares_mil chưa cập nhật (ví dụ VHM 4,354 triệu cp chưa nhân 2 sau đợt 1:1; TRC 30 triệu cp chưa nhân 4 sau đợt 1:3),
        tự động nhân hệ số pha loãng để đưa về số lượng cổ phiếu thực tế sau chia.
      + Nếu base_shares_mil đã là số lượng mới (như TCB 7,080 triệu cp; HPG 7,675 triệu cp; VCB 5,589 triệu cp), không nhân đúp.
    """
    clean_ticker = (ticker or "").upper().strip()
    actions = get_ticker_corporate_actions(clean_ticker, auto_sync=True)
    today = as_of_date or date.today()

    # Danh mục các mã mà cơ sở dữ liệu số lượng cổ phiếu tĩnh đã ghi nhận sẵn đợt chia cổ phiếu cũ
    ALREADY_FACTORED_TICKERS = {
        "TCB": {"cutoff_date": date(2025, 1, 1)},
        "HPG": {"cutoff_date": date(2025, 1, 1)},
        "VCB": {"cutoff_date": date(2025, 1, 1)},
        "SSI": {"cutoff_date": date(2025, 1, 1)},
    }

    dilution_multiplier = 1.0
    applied_events = []
    notes = []

    sorted_actions = sorted(
        actions,
        key=lambda x: parse_action_date(x.get("ex_date", "")) or date(2000, 1, 1)
    )

    for ev in sorted_actions:
        ex_d = parse_action_date(ev.get("ex_date", ""))
        if not ex_d:
            continue

        if ex_d <= today:
            # Nếu sự kiện đã được phản ánh trong base_shares tĩnh của CSDL thì bỏ qua
            if clean_ticker in ALREADY_FACTORED_TICKERS:
                cutoff = ALREADY_FACTORED_TICKERS[clean_ticker]["cutoff_date"]
                if ex_d < cutoff:
                    continue

            sr = float(ev.get("stock_ratio") or 0.0)
            rr = float(ev.get("rights_ratio") or 0.0)

            # Cổ tức bằng cổ phiếu, thưởng cổ phiếu hoặc quyền mua làm tăng số lượng CP
            if sr > 0 or rr > 0:
                step_mult = 1.0 + sr + rr
                dilution_multiplier *= step_mult
                applied_events.append({
                    "ex_date": ev.get("ex_date"),
                    "event_type": ev.get("event_type"),
                    "title": ev.get("title") or ev.get("description"),
                    "stock_ratio": sr,
                    "rights_ratio": rr,
                    "step_multiplier": round(step_mult, 4),
                    "adjustment_factor": round(1.0 / step_mult, 4)
                })
                t_str = f"Cổ phiếu: +{int(round(sr*100))}% ({'1:1' if sr==1.0 else ('1:'+str(int(sr)) if sr>=1 else '100:'+str(int(sr*100)))})" if sr > 0 else ""
                r_str = f"Quyền mua: +{int(round(rr*100))}%" if rr > 0 else ""
                combined_desc = ", ".join(filter(None, [t_str, r_str]))
                notes.append(f"GDKHQ {ev.get('ex_date')} ({combined_desc})")

    has_dilution = dilution_multiplier > 1.0001
    price_adj_factor = round(1.0 / dilution_multiplier, 4) if dilution_multiplier > 0 else 1.0
    
    base_shares = float(base_shares_mil or 1000.0)
    adjusted_shares = round(base_shares * dilution_multiplier, 2)

    return {
        "ticker": clean_ticker,
        "has_dilution": has_dilution,
        "base_shares_mil": base_shares,
        "adjusted_shares_mil": adjusted_shares,
        "dilution_multiplier": round(dilution_multiplier, 4),
        "price_adjustment_factor": price_adj_factor,
        "applied_events_count": len(applied_events),
        "applied_events": applied_events,
        "summary_note": "; ".join(notes) if notes else "Không có sự kiện pha loãng cổ phiếu."
    }



# ---------------------------------------------------------------------------
# CƠ CHẾ ĐỒNG BỘ ONLINE TỰ ĐỘNG & BỔ SUNG SỰ KIỆN TÙY CHỈNH (FALLBACK ĐA TẦNG)
# ---------------------------------------------------------------------------

def parse_corporate_action_ratio(a: float, b: float) -> float:
    """
    Quy đổi tỷ lệ A : B trong sự kiện quyền (HOSE / HNX / VSD) thành hệ số thực hưởng.
    Quy chuẩn TTCK Việt Nam:
    'Tỷ lệ A : B' có nghĩa là: Sở hữu A cổ phiếu cũ được nhận/mua B cổ phiếu mới.
    Do đó tỷ lệ thực hưởng là B / A.
    
    Ví dụ:
    - 1:3 -> sở hữu 1 CP nhận 3 CP mới -> ratio = 3 / 1 = 3.0 (300%) [như TRC thưởng 1:3]
    - 1:1 -> sở hữu 1 CP nhận 1 CP mới -> ratio = 1 / 1 = 1.0 (100%)
    - 1:2 -> sở hữu 1 CP nhận 2 CP mới -> ratio = 2 / 1 = 2.0 (200%)
    - 2:1 -> sở hữu 2 CP nhận 1 CP mới -> ratio = 1 / 2 = 0.5 (50%)
    - 4:1 -> sở hữu 4 CP nhận 1 CP mới -> ratio = 1 / 4 = 0.25 (25%)
    - 10:1 -> sở hữu 10 CP nhận 1 CP mới -> ratio = 1 / 10 = 0.1 (10%)
    - 4:3 -> sở hữu 4 CP nhận 3 CP mới -> ratio = 3 / 4 = 0.75 (75%)
    - 10:3 -> sở hữu 10 CP nhận 3 CP mới -> ratio = 3 / 10 = 0.3 (30%)
    - 100:15 -> sở hữu 100 CP nhận 15 CP mới -> ratio = 15 / 100 = 0.15 (15%)
    
    Ngoại lệ gõ ngược (nếu A == 1 và B >= 10, ví dụ '1:10', '1:20'):
    Trong thực tế không có DN nào thưởng 1000% mà không ghi 100:1000,
    nên '1:10' là do người đăng tin gõ ngược từ '10:1' (10%).
    """
    if a <= 0:
        return 0.0
    if a == 1.0 and b >= 10.0:
        return round(1.0 / b, 6)
    return round(b / a, 6)


def parse_simplize_event(item: Dict[str, Any], ticker: str) -> Optional[Dict[str, Any]]:
    """Bóc tách sự kiện tài chính từ API mở Simplize (nguồn chuẩn hóa từ HOSE/HNX/VSD & Vietstock)."""
    desc = item.get("description") or ""
    title = item.get("title") or ""
    ev_type_name = item.get("eventTypeName") or ""
    ex_date = item.get("exDividendDate")
    record_date = item.get("recordDate") or ""
    exec_date = item.get("executionDate") or ""
    
    if not ex_date:
        return None
        
    full_text = f"{title} | {desc} | {ev_type_name}"
    desc_lower = f"{desc} {ev_type_name}".lower()
    full_lower = full_text.lower()
    
    cash_amount = 0.0
    stock_ratio = 0.0
    rights_ratio = 0.0
    rights_price = 0.0
    ev_type = "other"

    # Kiểm tra phân loại sự kiện dựa trên eventTypeName và mô tả
    is_cash_type = "tiền" in ev_type_name.lower() or "tiền" in desc_lower
    is_stock_type = (
        "cổ phiếu" in ev_type_name.lower() or
        "thưởng" in ev_type_name.lower() or
        "thưởng" in desc_lower or
        "bằng cổ phiếu" in desc_lower or
        "nguồn vốn chủ sở hữu" in full_lower or
        "nguồn vốn csh" in full_lower
    )
    is_rights_type = (
        "phát hành" in ev_type_name.lower() or
        "quyền mua" in ev_type_name.lower() or
        "quyền mua" in desc_lower or
        "chào bán" in desc_lower
    )

    # 1. Cổ tức tiền mặt
    if is_cash_type and not is_rights_type:
        m_cash = re.search(r"([0-9]{1,3}(?:[.,][0-9]{3})*)\s*(?:đồng|đ|vnd|/cp)", desc, re.IGNORECASE)
        if not m_cash:
            m_cash = re.search(r"([0-9]{1,3}(?:[.,][0-9]{3})*)\s*(?:đồng|đ|vnd|/cp)", full_text, re.IGNORECASE)
        if m_cash:
            cash_amount = float(m_cash.group(1).replace(".", "").replace(",", ""))
            ev_type = "dividend_cash"
        else:
            m_pct = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", desc)
            if m_pct and float(m_pct.group(1)) <= 100:
                cash_amount = float(m_pct.group(1)) * 100.0
                ev_type = "dividend_cash"

    # 2. Quyền mua / Phát hành thêm
    if is_rights_type:
        ev_type = "rights_issue"
        m_price = re.search(r"giá\s*([0-9]{1,3}(?:[.,][0-9]{3})*)", desc, re.IGNORECASE)
        if not m_price:
            m_price = re.search(r"giá\s*([0-9]{1,3}(?:[.,][0-9]{3})*)", full_text, re.IGNORECASE)
        if m_price:
            rights_price = float(m_price.group(1).replace(".", "").replace(",", ""))

        m_ratio = re.search(r"tỷ lệ\s*([0-9]+(?:\.[0-9]+)?)\s*:\s*([0-9]+(?:\.[0-9]+)?)", desc, re.IGNORECASE)
        if not m_ratio:
            m_ratio = re.search(r"tỷ lệ\s*([0-9]+(?:\.[0-9]+)?)\s*:\s*([0-9]+(?:\.[0-9]+)?)", full_text, re.IGNORECASE)
        if m_ratio:
            a, b = float(m_ratio.group(1)), float(m_ratio.group(2))
            rights_ratio = parse_corporate_action_ratio(a, b)
        else:
            m_pct = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", desc)
            if m_pct:
                rights_ratio = float(m_pct.group(1)) / 100.0

    # 3. Cổ tức cổ phiếu / Cổ phiếu thưởng
    if is_stock_type and not is_rights_type:
        ev_type = "bonus_share" if "thưởng" in desc_lower else "dividend_stock"
        m_ratio = re.search(r"tỷ lệ\s*([0-9]+(?:\.[0-9]+)?)\s*:\s*([0-9]+(?:\.[0-9]+)?)", desc, re.IGNORECASE)
        if not m_ratio:
            m_ratio = re.search(r"tỷ lệ\s*([0-9]+(?:\.[0-9]+)?)\s*:\s*([0-9]+(?:\.[0-9]+)?)", full_text, re.IGNORECASE)
        if m_ratio:
            a, b = float(m_ratio.group(1)), float(m_ratio.group(2))
            stock_ratio = parse_corporate_action_ratio(a, b)
        else:
            m_pct = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", desc)
            if m_pct:
                stock_ratio = float(m_pct.group(1)) / 100.0

    # Hỗn hợp: cả tiền mặt và cổ phiếu/quyền
    if cash_amount > 0 and (stock_ratio > 0 or rights_ratio > 0):
        ev_type = "dividend_both"
    elif stock_ratio > 0 and rights_ratio > 0:
        ev_type = "dividend_and_rights"

    if cash_amount == 0 and stock_ratio == 0 and rights_ratio == 0:
        return None

    # Hệ số điều chỉnh thuần túy cho cổ tức cổ phiếu / thưởng cổ phiếu
    factor = None
    if cash_amount == 0 and rights_ratio == 0 and stock_ratio > 0:
        factor = round(1.0 / (1.0 + stock_ratio), 4)

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


def sync_ticker_corporate_actions_sync(ticker: str, timeout: float = 3.5) -> List[Dict[str, Any]]:
    """
    Đồng bộ hóa sự kiện quyền và ngày GDKHQ từ Simplize Open API (nguồn chuẩn hóa HOSE/HNX/VSD).
    Chạy đồng bộ, an toàn, có timeout và fallback vào cache nếu mất kết nối hoặc timeout.
    """
    import urllib.request
    clean_ticker = ticker.upper().strip()
    
    # Kiểm tra thời gian đã sync gần đây (tránh gọi lặp trong vòng 3600 giây = 1 giờ)
    now_ts = time.time()
    last_sync = _SYNCED_TICKERS.get(clean_ticker, 0.0)
    if (now_ts - last_sync) < 3600.0 and clean_ticker in _CORPORATE_ACTIONS_CACHE:
        return _CORPORATE_ACTIONS_CACHE.get(clean_ticker, [])

    url = f"https://api.simplize.vn/api/company/events/list?ticker={clean_ticker}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_items = data.get("data", []) if isinstance(data, dict) else []
            
            parsed_events = []
            for item in raw_items:
                parsed = parse_simplize_event(item, clean_ticker)
                if parsed:
                    parsed_events.append(parsed)
                    
            if clean_ticker not in _CORPORATE_ACTIONS_CACHE:
                _CORPORATE_ACTIONS_CACHE[clean_ticker] = []

            # Tập hợp các khóa sự kiện đã tồn tại
            existing_map = {}
            for idx, e in enumerate(_CORPORATE_ACTIONS_CACHE[clean_ticker]):
                k = f"{str(e.get('ex_date', '')).strip()}_{str(e.get('event_type', '')).strip()}"
                existing_map[k] = idx

            new_added = 0
            for ev in parsed_events:
                k = f"{str(ev.get('ex_date', '')).strip()}_{str(ev.get('event_type', '')).strip()}"
                if k not in existing_map:
                    _CORPORATE_ACTIONS_CACHE[clean_ticker].append(ev)
                    existing_map[k] = len(_CORPORATE_ACTIONS_CACHE[clean_ticker]) - 1
                    new_added += 1
                else:
                    curr_idx = existing_map[k]
                    existing_item = _CORPORATE_ACTIONS_CACHE[clean_ticker][curr_idx]
                    # Nếu bản ghi trước đó không phải curated, cập nhật thông tin
                    if not str(existing_item.get("id", "")).startswith(f"{clean_ticker.lower()}-ca-"):
                        _CORPORATE_ACTIONS_CACHE[clean_ticker][curr_idx] = ev

            _SYNCED_TICKERS[clean_ticker] = now_ts
            if new_added > 0:
                save_corporate_actions_cache()
    except Exception:
        _SYNCED_TICKERS[clean_ticker] = now_ts

    return _CORPORATE_ACTIONS_CACHE.get(clean_ticker, [])


async def sync_ticker_corporate_actions_online(ticker: str) -> List[Dict[str, Any]]:
    """
    Tự động đồng bộ hóa lịch sự kiện quyền & ngày GDKHQ mới nhất từ Open Financial API (Async).
    """
    import asyncio
    clean_ticker = ticker.upper().strip()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_ticker_corporate_actions_sync, clean_ticker)


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
