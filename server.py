"""
Institutional Equity Research Matrix (IERM) - FastAPI Server
"""

import io
import os
import re
import csv
import httpx
import time
from datetime import datetime, date
import json
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import asyncio
import unicodedata
import urllib.parse
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

def to_ascii_slug(text: str) -> str:
    """Chuyển đổi chuỗi có dấu tiếng Việt thành chuỗi không dấu ASCII an toàn cho HTTP headers và tên file."""
    if not text:
        return ""
    text = str(text).replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    slug = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in ascii_text)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")

def make_content_disposition(disposition_type: str, raw_filename: str) -> str:
    """Tạo header Content-Disposition chuẩn RFC 6266 / RFC 5987, an toàn latin-1 và hỗ trợ UTF-8."""
    base_name = raw_filename.rsplit(".", 1)[0] if "." in raw_filename else raw_filename
    ext = f".{raw_filename.rsplit('.', 1)[1]}" if "." in raw_filename else ""
    ascii_name = f"{to_ascii_slug(base_name)}{ext}"
    if not ascii_name or ascii_name == ext:
        ascii_name = f"document{ext}"
    utf8_encoded = urllib.parse.quote(raw_filename)
    return f'{disposition_type}; filename="{ascii_name}"; filename*=UTF-8\'\'{utf8_encoded}'

from engine import (
    ReportItem,
    FullMatrixReport,
    PRESET_DATASETS,
    calculate_consensus,
    extract_financial_data_from_text
)
from crawler import (
    crawl_url_content,
    parse_pdf_bytes,
    search_institutional_reports,
    fetch_reconciled_live_price,
    fetch_live_market_tape,
    fetch_stock_company_profile,
    fetch_stock_corporate_capital,
    fetch_edocs_reports,
    parse_edocs_item_to_report,
    generate_sector_institutional_reports,
    fetch_industry_reports,
    fetch_company_reports,
    get_ssi_fastconnect_status,
    get_synchronized_matrix_reports
)
from financial_data import (
    get_financial_data_bundle,
    calculate_dcf_model,
    calculate_multi_model_valuation,
    VIETNAM_STOCK_DIRECTORY,
    get_company_news_and_events,
    get_mini_chart_series,
    get_company_catalysts_and_projects
)
from company_database import (
    COMPANY_DATABASE,
    SECTOR_DATABASE,
    get_company,
    search_companies,
    get_all_sectors_summary,
    sync_from_google_sheets
)
from pdf_generator import generate_ctck_report_pdf, generate_matrix_table_pdf, generate_peer_comparison_pdf
from ssi_fastconnect import (
    SSI_API_CATALOG,
    SSI_CONFIG,
    SSIFastConnectClient,
    fetch_hybrid_ohlcv_data,
    calculate_technical_indicators,
    get_stock_depth_metrics,
    get_market_overview
)
from ai_learning_engine import (
    ai_scheduler,
    template_store,
    extract_advanced_knowledge,
    analyze_template_image_ai,
    apply_learned_catalysts_to_report,
    save_learned_ticker_catalysts,
    get_learned_ticker_catalysts
)

app = FastAPI(
    title="Institutional Equity Research Matrix (IERM)",
    description="Fintech Research Co-Pilot & WebApp Engine for Vietnam Financial Market",
    version="1.0.0"
)

# Thư mục static UI
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Tự động đồng bộ nếu người dùng kéo thả file ra ngoài thư mục gốc trên GitHub
for _fn in ["index.html", "app.js", "styles.css"]:
    _root_f = os.path.join(ROOT_DIR, _fn)
    _stat_f = os.path.join(STATIC_DIR, _fn)
    if os.path.exists(_root_f) and not os.path.exists(_stat_f):
        try:
            import shutil
            shutil.copy2(_root_f, _stat_f)
        except Exception:
            pass

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
DATA_STORAGE_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_STORAGE_DIR, exist_ok=True)
app.mount("/data", StaticFiles(directory=DATA_STORAGE_DIR), name="data")


@app.on_event("startup")
async def startup_event():
    """Tự động làm nóng bộ nhớ đệm bảng giá SSI toàn thị trường và khởi động AI Learning Scheduler ngầm."""
    try:
        from crawler import fetch_ssi_live_stock_quote
        asyncio.create_task(fetch_ssi_live_stock_quote("HPG"))
    except Exception as e:
        print(f"SSI startup pre-warm exception: {e}")

    try:
        asyncio.create_task(ai_scheduler.start_background_loop())
    except Exception as e:
        print(f"AI Learning Scheduler startup exception: {e}")

    # Pre-warm cache cho top 20 mã phổ biến nhất để giảm latency lần đầu
    async def _prewarm_top_tickers():
        top_tickers = [
            "HPG", "VHM", "VIC", "VNM", "MWG", "FPT", "TCB", "VCB", "BID", "CTG",
            "STB", "MSN", "GVR", "SAB", "ACB", "MBB", "VPB", "HDB", "EIB", "PLX"
        ]
        await asyncio.sleep(5)  # Đợi server sẵn sàng hoàn toàn
        for tkr in top_tickers:
            try:
                await asyncio.wait_for(
                    get_synchronized_matrix_reports(
                        ticker=tkr, base_reports=[], comp_name="", sector_name="", market_p=25000.0
                    ),
                    timeout=15.0
                )
                await asyncio.sleep(2)  # Throttle để tránh DDoS Vietstock
            except Exception:
                pass

    try:
        asyncio.create_task(_prewarm_top_tickers())
    except Exception as e:
        print(f"Pre-warm startup exception: {e}")



ADMIN_AUTH_FILE = os.path.join(ROOT_DIR, "data", "admin_auth.json")
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "325396"
ADMIN_RECOVERY_EMAIL = "hoabhk31@gmail.com"

def get_admin_auth_data() -> dict:
    os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)
    if os.path.exists(ADMIN_AUTH_FILE):
        try:
            with open(ADMIN_AUTH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "username" in data and "password" in data:
                    data.setdefault("recovery_email", ADMIN_RECOVERY_EMAIL)
                    data.setdefault("active_otp", None)
                    data.setdefault("otp_expires_at", 0)
                    return data
        except Exception as e:
            print(f"Error loading admin_auth.json: {e}")
    initial_data = {
        "username": DEFAULT_ADMIN_USER,
        "password": DEFAULT_ADMIN_PASSWORD,
        "recovery_email": ADMIN_RECOVERY_EMAIL,
        "active_otp": None,
        "otp_expires_at": 0
    }
    save_admin_auth_data(initial_data)
    return initial_data

def save_admin_auth_data(data: dict):
    os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)
    with open(ADMIN_AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_recovery_otp_email(to_email: str, otp: str) -> dict:
    """
    Gửi email mã OTP phục hồi mật khẩu tới hoabhk31@gmail.com qua SMTP.
    Đồng thời ghi log an toàn vào data/admin_reset_email_log.txt để hỗ trợ khôi phục dự phòng.
    """
    os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)
    log_path = os.path.join(ROOT_DIR, "data", "admin_reset_email_log.txt")
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp_str}] Gửi mã OTP: {otp} tới email: {to_email} (Thời hạn 15 phút)\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line)

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user or "admin@ierm.finance")

    subject = f"[IERM Matrix] Mã xác nhận đổi mật khẩu Quản trị viên (Admin): {otp}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border: 1px solid #1e293b; border-radius: 12px; padding: 24px;">
        <h2 style="color: #38bdf8; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 12px;">
            🛡️ IERM Institutional Matrix - Đặt Lại Mật Khẩu
        </h2>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
            Xin chào Quản trị viên, bạn vừa yêu cầu đổi mật khẩu cho tài khoản <b>admin</b> trên hệ thống <b>IERM Financial Intelligence Matrix</b>.
        </p>
        <div style="background: #020617; border: 1px dashed #38bdf8; border-radius: 8px; padding: 18px; text-align: center; margin: 20px 0;">
            <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 6px;">MÃ XÁC THỰC OTP (Hiệu lực trong 15 phút):</span>
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #38bdf8; font-family: monospace;">{otp}</span>
        </div>
        <p style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
            Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email. Mật khẩu hiện tại của bạn vẫn được bảo mật an toàn.
        </p>
        <hr style="border: 0; border-top: 1px solid #1e293b; margin: 20px 0;">
        <p style="font-size: 11px; color: #64748b; text-align: center;">
            IERM Intelligence Platform © 2026. Email tự động, vui lòng không phản hồi.
        </p>
    </div>
    """

    email_sent = False
    error_msg = ""
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = to_email
            msg.attach(MIMEText(f"Mã xác nhận OTP đặt lại mật khẩu admin: {otp} (Hiệu lực 15 phút).", "plain", "utf-8"))
            msg.attach(MIMEText(body_html, "html", "utf-8"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [to_email], msg.as_string())
            email_sent = True
        except Exception as e:
            error_msg = str(e)
            print(f"SMTP dispatch notice: {e}")

    return {
        "sent_via_smtp": email_sent,
        "smtp_error": error_msg,
        "recipient": to_email,
        "logged_locally": True
    }


class AdminAuthRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

def is_admin_authorized(
    user: Optional[str] = None,
    password: Optional[str] = None,
    auth_header: Optional[str] = None
) -> bool:
    auth_data = get_admin_auth_data()
    expected_user = auth_data.get("username", DEFAULT_ADMIN_USER)
    expected_password = auth_data.get("password", DEFAULT_ADMIN_PASSWORD)

    if (user or "").strip() == expected_user and (password or "").strip() == expected_password:
        return True
    if auth_header and auth_header.startswith("Basic "):
        try:
            import base64
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            u, p = decoded.split(":", 1)
            if u.strip() == expected_user and p.strip() == expected_password:
                return True
        except Exception:
            pass
    return False

def enforce_admin_permission(
    x_admin_user: Optional[str] = None,
    x_admin_password: Optional[str] = None,
    authorization: Optional[str] = None,
    fallback_user: Optional[str] = None,
    fallback_password: Optional[str] = None
):
    auth_data = get_admin_auth_data()
    expected_password = auth_data.get("password", DEFAULT_ADMIN_PASSWORD)
    
    u = x_admin_user or fallback_user
    p = x_admin_password or fallback_password

    # Nếu hệ thống đang dùng mật khẩu mặc định hoặc không truyền credentials từ client giao diện, tự động cho phép thao tác
    if (not u and not p and not authorization) or (expected_password == DEFAULT_ADMIN_PASSWORD and not p):
        return

    if not is_admin_authorized(u, p, authorization):
        raise HTTPException(
            status_code=403,
            detail="Yêu cầu quyền Quản trị viên (Admin) để cập nhật dữ liệu báo cáo thủ công. Vui lòng cung cấp mật khẩu chính xác."
        )


class CrawlRequest(BaseModel):
    url: str
    ticker: Optional[str] = "HPG"
    institution: Optional[str] = "CTCK"
    admin_user: Optional[str] = None
    admin_password: Optional[str] = None


class RawTextAnalysisRequest(BaseModel):
    raw_text: str
    ticker: Optional[str] = "HPG"
    institution: Optional[str] = "CTCK"
    admin_user: Optional[str] = None
    admin_password: Optional[str] = None


class ReconcileRequest(BaseModel):
    ticker: str
    company_name: Optional[str] = ""
    sector: Optional[str] = ""
    current_market_price: Optional[float] = None
    price_source_info: Optional[dict] = None
    reports: List[ReportItem]


class ExportRequest(BaseModel):
    report_data: Union[FullMatrixReport, Dict[str, Any]]


def normalize_full_matrix_dict(raw: Any) -> Dict[str, Any]:
    """Chuyển đổi an toàn dữ liệu ma trận sang dict chuẩn, tương thích cả Pydantic lẫn JSON raw."""
    if hasattr(raw, "model_dump"):
        d = raw.model_dump()
    elif hasattr(raw, "dict") and callable(raw.dict):
        d = raw.dict()
    elif isinstance(raw, dict):
        d = dict(raw)
    else:
        try:
            d = dict(raw)
        except Exception:
            d = {}

    cs = d.get("consensus_summary")
    if hasattr(cs, "model_dump"):
        d["consensus_summary"] = cs.model_dump()
    elif hasattr(cs, "dict") and callable(cs.dict):
        d["consensus_summary"] = cs.dict()
    elif not isinstance(cs, dict):
        d["consensus_summary"] = {}

    clean_matrix = []
    for it in d.get("matrix_table", []):
        if hasattr(it, "model_dump"):
            clean_matrix.append(it.model_dump())
        elif hasattr(it, "dict") and callable(it.dict):
            clean_matrix.append(it.dict())
        elif isinstance(it, dict):
            clean_matrix.append(dict(it))
        else:
            try:
                clean_matrix.append(dict(it))
            except Exception:
                pass
    d["matrix_table"] = clean_matrix
    return d


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


class TemplateCreateUpdateRequest(BaseModel):
    id: Optional[str] = None
    name: str
    sector: str
    keywords: List[str] = []
    catalyst_rules: List[str] = []
    thesis_rules: List[str] = []
    risk_rules: List[str] = []
    sample_text: Optional[str] = ""


class LearningConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    interval_hours: Optional[int] = None
    watchlist: Optional[List[str]] = None
    auto_ingest_matrix: Optional[bool] = None


class TriggerLearnRequest(BaseModel):
    tickers: Optional[List[str]] = None



@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    for candidate in [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(ROOT_DIR, "index.html"),
    ]:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(
        "<div style='font-family:sans-serif;padding:30px;max-width:650px;margin:50px auto;border:1px solid #cbd5e1;border-radius:12px;background:#f8fafc;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);'>"
        "<h2 style='color:#e11d48;margin-top:0;'>⚠️ Chưa có file giao diện (index.html)</h2>"
        "<p style='color:#334155;line-height:1.6;'>Máy chủ Render đã kích hoạt thành công, nhưng repository trên GitHub của bạn <b>chưa có thư mục <code>static</code></b> (chứa <code>index.html</code>, <code>app.js</code>, <code>styles.css</code>).</p>"
        "<div style='background:#f1f5f9;padding:15px;border-radius:8px;border-left:4px solid #0284c7;margin:15px 0;'>"
        "<strong style='color:#0369a1;'>👉 Cách xử lý nhanh:</strong><br>"
        "Vào GitHub repository của bạn &rarr; bấm <b>Add file</b> &rarr; <b>Upload files</b> &rarr; tải thư mục <b><code>static</code></b> (hoặc cả 3 file <code>index.html</code>, <code>app.js</code>, <code>styles.css</code>) lên &rarr; Render sẽ tự tải lại web trong 1 phút."
        "</div>"
        "</div>"
    )


CLIENT_ERROR_LOGS = []

@app.post("/api/client-log")
async def log_client_error(data: dict):
    CLIENT_ERROR_LOGS.append(data)
    print(f"[CLIENT LOG/ERROR] {data}")
    return {"status": "ok", "total": len(CLIENT_ERROR_LOGS)}

@app.get("/api/client-log")
async def get_client_errors():
    return {"errors": CLIENT_ERROR_LOGS}



@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "engine": "IERM Quantitative Engine v1.0",
        "available_presets": list(PRESET_DATASETS.keys())
    }


@app.get("/api/presets")
async def get_presets():
    return [
        {
            "ticker": k,
            "company_name": v.company_name,
            "sector": v.sector,
            "reports_count": len(v.matrix_table),
            "consensus_rating": v.consensus_summary.consensus_rating,
            "mean_target_price": v.consensus_summary.mean_target_price,
            "upside": v.consensus_summary.average_upside,
            "market_price": v.consensus_summary.current_market_price,
            "market_to_fair_value_ratio": v.consensus_summary.market_to_fair_value_ratio
        }
        for k, v in PRESET_DATASETS.items()
    ]


@app.get("/api/live-price/{ticker}")
async def get_live_price(ticker: str):
    """
    Lấy giá đóng cửa mới nhất trên chart Vietstock (https://finance.vietstock.vn/phan-tich-ky-thuat.htm)
    và đối chiếu với bảng giá của các CTCK (VNDirect, DNSE), lấy nguồn nào mới hơn.
    """
    clean_ticker = ticker.upper().strip()
    price_info = await fetch_reconciled_live_price(clean_ticker)
    return price_info


_SYNCHRONIZED_PRESETS_CACHE: Dict[str, FullMatrixReport] = {}
_SYNCHRONIZED_PRESETS_CACHE_TS: Dict[str, float] = {}
_PRESET_LOCKS: Dict[str, asyncio.Lock] = {}

_FIN_OVERVIEW_CACHE: Dict[str, Dict[str, Any]] = {}
_FIN_OVERVIEW_CACHE_TS: Dict[str, float] = {}

_TECH_SIGNALS_CACHE: Dict[str, Dict[str, Any]] = {}
_TECH_SIGNALS_CACHE_TS: Dict[str, float] = {}


@app.get("/api/preset/{ticker}")
async def get_preset_by_ticker(ticker: str, sync_live_price: bool = True, refresh: bool = False):
    clean_ticker = ticker.upper().strip()
    now_ts = time.time()

    # 1. Kiểm tra cache bộ nhớ để phản hồi tức thì nếu còn mới (300s TTL)
    if not refresh:
        cached_rep = _SYNCHRONIZED_PRESETS_CACHE.get(clean_ticker)
        cached_time = _SYNCHRONIZED_PRESETS_CACHE_TS.get(clean_ticker, 0)
        if cached_rep and (now_ts - cached_time) < 300.0 and cached_rep.ticker == clean_ticker:
            return cached_rep

    # 2. Khóa concurrency để tránh gọi đúp song song nhiều crawler cùng 1 mã
    if clean_ticker not in _PRESET_LOCKS:
        _PRESET_LOCKS[clean_ticker] = asyncio.Lock()

    async with _PRESET_LOCKS[clean_ticker]:
        now_ts = time.time()
        if not refresh:
            cached_rep = _SYNCHRONIZED_PRESETS_CACHE.get(clean_ticker)
            cached_time = _SYNCHRONIZED_PRESETS_CACHE_TS.get(clean_ticker, 0)
            if cached_rep and (now_ts - cached_time) < 300.0 and cached_rep.ticker == clean_ticker:
                return cached_rep

        stock_meta = VIETNAM_STOCK_DIRECTORY.get(clean_ticker, {})
        cached_name = stock_meta.get("name", f"Công ty Cổ phần {clean_ticker}")
        cached_sector = stock_meta.get("sector", "Doanh nghiệp niêm yết")

        # Tối ưu hóa siêu tốc: Chạy song song Profile, Giá Live và Lịch Sự Kiện Quyền
        async def _safe_profile():
            try:
                return await asyncio.wait_for(fetch_stock_company_profile(clean_ticker), timeout=2.0)
            except Exception:
                return {}

        async def _safe_price():
            try:
                return await asyncio.wait_for(fetch_reconciled_live_price(clean_ticker), timeout=3.0)
            except Exception:
                return None

        async def _safe_ca():
            try:
                from corporate_actions import sync_ticker_corporate_actions_online, load_corporate_actions_cache
                load_corporate_actions_cache()
                await asyncio.wait_for(sync_ticker_corporate_actions_online(clean_ticker), timeout=3.5)
            except Exception:
                pass

        prof_res, live_res, _ = await asyncio.gather(_safe_profile(), _safe_price(), _safe_ca(), return_exceptions=True)
        profile = prof_res if isinstance(prof_res, dict) else {}
        live_info = live_res if isinstance(live_res, dict) else None
        market_p = live_info.get("latest_close", 25000.0) if live_info else 25000.0

        comp_name = profile.get("name") or cached_name
        sect_name = profile.get("sector") or cached_sector
        final_comp_name = comp_name
        final_sect_name = sect_name

        base_reports = []
        base_causality = []
        base_disensus = []
        if clean_ticker in PRESET_DATASETS:
            report = PRESET_DATASETS[clean_ticker]
            if comp_name and (report.company_name.startswith("Công ty Cổ phần " + clean_ticker) or report.company_name.startswith("CTCP " + clean_ticker)):
                report.company_name = comp_name
            if sect_name and report.sector in ["Doanh nghiệp niêm yết", "Doanh nghiệp Niêm yết"]:
                report.sector = sect_name
            base_reports = list(report.matrix_table) if report.matrix_table else []
            base_causality = report.causality_analysis or []
            base_disensus = report.disensus_table or []
            final_comp_name = report.company_name
            final_sect_name = report.sector

        # Đồng bộ hóa báo cáo phân tích đa tổ chức với các bài viết mới nhất từ Vietstock eDocs & CTCK
        try:
            synced_reports = await asyncio.wait_for(
                get_synchronized_matrix_reports(
                    ticker=clean_ticker,
                    base_reports=base_reports,
                    comp_name=final_comp_name,
                    sector_name=final_sect_name,
                    market_p=market_p,
                    max_reports=20
                ),
                timeout=10.0
            )
        except Exception as sync_err:
            synced_reports = base_reports

        reconciled = calculate_consensus(
            reports=synced_reports,
            ticker=clean_ticker,
            company_name=final_comp_name,
            sector=final_sect_name,
            current_market_price=market_p,
            price_source_info=live_info
        )

        # Đảm bảo mã ticker luôn là clean_ticker
        reconciled.ticker = clean_ticker
        if final_comp_name:
            reconciled.company_name = final_comp_name
        if final_sect_name:
            reconciled.sector = final_sect_name

        if base_causality and len(base_causality) > len(reconciled.causality_analysis):
            reconciled.causality_analysis = base_causality
        if base_disensus and len(reconciled.disensus_table) == 0:
            reconciled.disensus_table = base_disensus

        # Tự động đồng bộ các luận điểm tăng trưởng (Catalysts) và rủi ro mà AI đã học vào Báo cáo đa tổ chức
        try:
            reconciled = apply_learned_catalysts_to_report(reconciled)
        except Exception as e:
            print(f"Error applying AI learned catalysts for {clean_ticker}: {e}")

        # Chỉ lưu cache dài hạn khi đã lấy được danh sách báo cáo
        if synced_reports or clean_ticker in PRESET_DATASETS:
            _SYNCHRONIZED_PRESETS_CACHE[clean_ticker] = reconciled
            _SYNCHRONIZED_PRESETS_CACHE_TS[clean_ticker] = time.time()
        return reconciled


@app.get("/api/corporate-actions/{ticker}")
async def get_corporate_actions_endpoint(ticker: str):
    """
    Truy xuất danh sách các sự kiện quyền (GDKHQ: cổ tức tiền mặt, cổ tức cổ phiếu, phát hành thêm)
    và hệ số điều chỉnh giá tương ứng để Nhà đầu tư tra cứu và đối chiếu.
    Tham chiếu: Vietstock, Simplize Open API & Sở GDCK (HOSE/HNX).
    """
    clean_ticker = ticker.upper().strip()
    from corporate_actions import get_ticker_corporate_actions, sync_ticker_corporate_actions_online
    try:
        await asyncio.wait_for(sync_ticker_corporate_actions_online(clean_ticker), timeout=2.0)
    except Exception:
        pass
    actions = get_ticker_corporate_actions(clean_ticker)
    return {
        "ticker": clean_ticker,
        "count": len(actions),
        "source": "Vietstock, Simplize Open API & Sở GDCK (HOSE/HNX)",
        "corporate_actions": actions
    }


class CustomCorporateActionModel(BaseModel):
    ticker: str
    ex_date: str
    record_date: Optional[str] = ""
    execution_date: Optional[str] = ""
    event_type: str = "dividend_cash"
    title: str
    cash_amount: float = 0.0
    stock_ratio: float = 0.0
    rights_ratio: float = 0.0
    rights_price: float = 0.0
    description: Optional[str] = ""
    source: Optional[str] = "Công bố thông tin trực tiếp / Nghị quyết HĐQT"


@app.post("/api/corporate-actions/add")
async def add_corporate_action_endpoint(req: CustomCorporateActionModel):
    """
    Cho phép Nhà đầu tư hoặc Chuyên viên phân tích chủ động bổ sung sự kiện quyền
    (như cổ tức tiền, cổ phiếu thưởng, phát hành thêm) ngay khi doanh nghiệp vừa ra Nghị quyết HĐQT.
    """
    from corporate_actions import add_custom_corporate_action
    added = add_custom_corporate_action(req.ticker, req.model_dump())
    # Xóa cache reconciled cũ để tính lại ma trận định giá ngay lập tức
    clean_t = req.ticker.upper().strip()
    if clean_t in _SYNCHRONIZED_PRESETS_CACHE:
        del _SYNCHRONIZED_PRESETS_CACHE[clean_t]
    return {
        "success": True,
        "message": f"Đã cập nhật sự kiện quyền cho mã {clean_t} thành công",
        "action": added
    }


@app.get("/api/ssi/status")
async def get_ssi_status():
    """
    Trả về trạng thái kết nối & chẩn đoán của dịch vụ SSI FastConnect Data API.
    """
    return get_ssi_fastconnect_status()


@app.get("/api/market-tape")
async def get_market_tape(ticker: Optional[str] = None):
    """
    Lấy dữ liệu chỉ số thị trường (VN-INDEX, VN30) và các mã cổ phiếu tiêu biểu
    trực tiếp từ API bảng giá các CTCK (DNSE Entrade, Vietstock).
    """
    tape = await fetch_live_market_tape(ticker)
    return tape


@app.get("/api/industry-reports")
async def get_industry_reports(
    ticker: Optional[str] = "HPG",
    keyword: Optional[str] = None,
    report_type: Optional[int] = None,
    source: Optional[str] = None,
    all_industries: Optional[bool] = False,
    limit: int = 50
):
    """
    Truy xuất danh sách báo cáo phân tích ngành, báo cáo hàng hóa và vĩ mô liên quan trực tiếp
    tới mã cổ phiếu đang xem (từ Vietstock eDocs, các CTCK và FireAnt).
    Khi all_industries=True: hiển thị toàn bộ báo cáo mới nhất của tất cả các ngành.
    """
    res = await fetch_industry_reports(
        ticker=ticker,
        keyword=keyword,
        report_type_id=report_type,
        source_name=source,
        all_industries=bool(all_industries),
        page_size=limit
    )
    return res


@app.get("/api/company-reports")
async def get_company_reports(
    ticker: Optional[str] = "HPG",
    keyword: Optional[str] = None,
    report_type: Optional[int] = None,
    source: Optional[str] = None,
    limit: int = 50
):
    """
    Truy xuất danh sách báo cáo phân tích doanh nghiệp (báo cáo định giá, khuyến nghị, cập nhật KQKD)
    dành riêng cho mã cổ phiếu chỉ định (từ Vietstock eDocs, các CTCK uy tín và ma trận IERM).
    """
    res = await fetch_company_reports(
        ticker=ticker,
        keyword=keyword,
        report_type_id=report_type,
        source_name=source,
        page_size=limit
    )
    return res


@app.get("/api/benchmark-recommendations")
async def get_benchmark_recommendations():
    """
    Trả về danh sách các mã cổ phiếu tiêu biểu kèm khuyến nghị và upside đồng thuận mới nhất
    từ các CTCK để hiển thị trên thanh chip điều hướng nhanh (MÃ TIÊU BIỂU).
    """
    benchmark_symbols = ["HPG", "SSI", "HCM", "VNM", "FPT", "MWG", "GEX", "PDR"]
    results = []
    for sym in benchmark_symbols:
        rep = _SYNCHRONIZED_PRESETS_CACHE.get(sym) or PRESET_DATASETS.get(sym)
        if rep:
            cs = rep.consensus_summary
            if cs and (cs.average_upside < 0 or (cs.mean_target_price > 0 and cs.current_market_price > cs.mean_target_price)):
                short_rating = "VƯỢT MỤC TIÊU"
                raw_rating = cs.consensus_rating
            elif cs and (cs.mean_target_price <= 0 or "THEO DÕI" in (cs.consensus_rating or "").upper()):
                short_rating = "THEO DÕI"
                raw_rating = cs.consensus_rating
            else:
                raw_rating = cs.consensus_rating.split("(")[0].strip() if cs else "MUA"
                short_rating = "MUA" if "MUA" in raw_rating else ("KHẢ QUAN" if "KHẢ QUAN" in raw_rating else ("TÍCH LŨY" if "TÍCH LŨY" in raw_rating else "NẮM GIỮ"))
            results.append({
                "ticker": sym,
                "name": rep.company_name,
                "sector": rep.sector,
                "rating": short_rating,
                "full_rating": raw_rating,
                "upside": cs.average_upside if cs else 25.0,
                "target_price": cs.mean_target_price if cs else 0,
                "current_price": cs.current_market_price if cs else rep.current_price
            })
        else:
            info = VIETNAM_STOCK_DIRECTORY.get(sym, {})
            results.append({
                "ticker": sym,
                "name": info.get("name", sym),
                "sector": info.get("sector", "Doanh nghiệp niêm yết"),
                "rating": "KHẢ QUAN",
                "full_rating": "KHẢ QUAN",
                "upside": 25.0,
                "target_price": 0,
                "current_price": 25000
            })
    return results

class DcfCustomRequest(BaseModel):
    ticker: str
    wacc: float = 11.5
    terminal_g: float = 2.5
    fcf_growth_rate: float = 15.0
    projection_years: int = 5
    current_market_price: Optional[float] = None


class MultiModelValuationRequest(BaseModel):
    ticker: str
    wacc: float = 11.5
    terminal_g: float = 2.5
    growth_rate: float = 12.0
    risk_free_rate: float = 4.8
    industry_pe: Optional[float] = None
    industry_pb: Optional[float] = None
    weights: Optional[Dict[str, float]] = None
    current_market_price: Optional[float] = None



@app.get("/api/financial-overview/{ticker}")
async def get_financial_overview(ticker: str):
    """
    Truy xuất toàn bộ phân tích BCTC, Dupont 3 & 5 bước, Piotroski F-score, Altman Z-score, và định giá DCF.
    """
    clean_ticker = ticker.upper().strip()
    now_ts = time.time()
    if clean_ticker in _FIN_OVERVIEW_CACHE and (now_ts - _FIN_OVERVIEW_CACHE_TS.get(clean_ticker, 0)) < 120.0:
        return _FIN_OVERVIEW_CACHE[clean_ticker]

    stock_meta = VIETNAM_STOCK_DIRECTORY.get(clean_ticker, {})
    default_name = stock_meta.get("name")
    default_sector = stock_meta.get("sector")

    async def _safe_p():
        try:
            live_price_info = await asyncio.wait_for(fetch_reconciled_live_price(clean_ticker), timeout=2.5)
            return live_price_info.get("latest_close", 25000.0) if live_price_info else 25000.0
        except Exception:
            return 25000.0

    async def _safe_prof():
        try:
            return await asyncio.wait_for(fetch_stock_company_profile(clean_ticker), timeout=2.0)
        except Exception:
            return {}

    async def _safe_cap():
        try:
            return await asyncio.wait_for(fetch_stock_corporate_capital(clean_ticker), timeout=2.0)
        except Exception:
            return {}

    p_res, prof_res, cap_res = await asyncio.gather(_safe_p(), _safe_prof(), _safe_cap(), return_exceptions=True)
    market_p = p_res if isinstance(p_res, (int, float)) else 25000.0
    profile = prof_res if isinstance(prof_res, dict) else {}
    capital_info = cap_res if isinstance(cap_res, dict) else {}

    data = get_financial_data_bundle(
        clean_ticker,
        current_market_price=market_p,
        company_name=profile.get("name") or default_name,
        sector=profile.get("sector") or default_sector,
        corporate_capital=capital_info
    )
    _FIN_OVERVIEW_CACHE[clean_ticker] = data
    _FIN_OVERVIEW_CACHE_TS[clean_ticker] = now_ts
    return data


@app.get("/api/peers/{ticker}")
async def get_peers_comparison(ticker: str):
    """
    Truy xuất danh sách đối thủ cùng ngành, trung bình ngành, radar chart và mô hình 5 lực lượng cạnh tranh Porter.
    """
    clean_ticker = ticker.upper().strip()
    now_ts = time.time()
    if clean_ticker in _FIN_OVERVIEW_CACHE and (now_ts - _FIN_OVERVIEW_CACHE_TS.get(clean_ticker, 0)) < 120.0:
        return _FIN_OVERVIEW_CACHE[clean_ticker].get("peers_data", {})

    data = await get_financial_overview(clean_ticker)
    return data.get("peers_data", {})


@app.get("/api/company-news-events/{ticker}")
async def get_news_and_events(ticker: str):
    """
    Truy xuất danh sách tin tức và sự kiện doanh nghiệp cập nhật.
    """
    clean_ticker = ticker.upper().strip()
    return get_company_news_and_events(clean_ticker)


@app.get("/api/mini-chart-series/{ticker}")
async def get_overview_mini_chart_series(ticker: str):
    """
    Truy xuất chuỗi dữ liệu nến/giá/khối lượng cho biểu đồ kỹ thuật mini (1D, 5D, 1M, 6M, YTD, 1Y, 5Y, ALL)
    kèm bảng thống kê thị trường chi tiết theo giá thời gian thực.
    """
    clean_ticker = ticker.upper().strip()
    live_price = None
    live_ref = None
    live_open = None
    live_high = None
    live_low = None
    live_vol = None
    live_change = None
    live_pct = None
    live_f_buy = None
    live_bid = None
    live_ask = None
    try:
        live_info = await fetch_reconciled_live_price(clean_ticker)
        if live_info and "latest_close" in live_info:
            live_price = float(live_info["latest_close"])
            if live_info.get("sources_comparison") and len(live_info["sources_comparison"]) > 0:
                s0 = live_info["sources_comparison"][0]
                live_ref = s0.get("ref_price")
                live_open = s0.get("open")
                live_high = s0.get("high")
                live_low = s0.get("low")
                live_vol = s0.get("volume")
                live_change = s0.get("change")
                live_pct = s0.get("change_percent")
                live_f_buy = s0.get("foreign_buy")
                live_bid = s0.get("bid_vol")
                live_ask = s0.get("ask_vol")
    except Exception as e:
        print(f"Fetch live price for mini-chart-series failed ({clean_ticker}): {e}")

    capital_info = None
    if clean_ticker in _FIN_OVERVIEW_CACHE:
        prof = _FIN_OVERVIEW_CACHE[clean_ticker].get("company_profile", {})
        if prof.get("shares_outstanding_mil"):
            capital_info = {"shares_outstanding_mil": prof["shares_outstanding_mil"]}
    if not capital_info:
        try:
            capital_info = await asyncio.wait_for(fetch_stock_corporate_capital(clean_ticker), timeout=1.5)
        except Exception:
            pass

    return get_mini_chart_series(
        clean_ticker,
        live_price=live_price,
        live_ref=live_ref,
        live_open=live_open,
        live_high=live_high,
        live_low=live_low,
        live_vol=live_vol,
        live_change=live_change,
        live_pct=live_pct,
        live_foreign_buy=live_f_buy,
        live_bid_vol=live_bid,
        live_ask_vol=live_ask,
        corporate_capital=capital_info
    )


@app.get("/api/company-catalysts-insights/{ticker}")
async def get_catalysts_and_insights(ticker: str):
    """
    Truy xuất thông tin catalysts động lực tăng trưởng, dự án trọng yếu (quy mô, vốn, tiến độ/lấp đầy)
    và phân tích AI chuyên sâu.
    Mặc định tự động Quét BCTN, BCTC và Website doanh nghiệp để luôn trả về danh mục dự án đầy đủ, đúng và mới nhất.
    """
    clean_ticker = ticker.upper().strip()
    data = get_company_catalysts_and_projects(clean_ticker)

    # Mặc định tự động Quét BCTN & Website chính thức từ Project Discovery Engine
    try:
        from project_discovery_engine import discover_company_projects_master, SSC_COMPANY_PROFILES_SEARCH_URL, SSC_DISCLOSURE_PORTAL_NAME
        data["ssc_portal_url"] = SSC_COMPANY_PROFILES_SEARCH_URL
        data["ssc_portal_name"] = SSC_DISCLOSURE_PORTAL_NAME

        # Tự động quét và lấy danh mục dự án mới nhất (sử dụng cache thông minh nếu vừa quét, hoặc quét tự động)
        disc_entry = await discover_company_projects_master(clean_ticker, force_refresh=False)
        if disc_entry and disc_entry.get("projects"):
            data["projects"] = disc_entry["projects"]
            data["total_projects"] = len(disc_entry["projects"])
            data["total_investment_bil"] = disc_entry.get("total_investment_bil", data.get("total_investment_bil", 0))
            data["official_website"] = disc_entry.get("official_website")
            data["scan_sources"] = disc_entry.get("scan_sources")
            data["scan_time_str"] = disc_entry.get("scan_time_str")
            data["auto_discovered"] = True
    except Exception as e:
        print(f"[get_catalysts_and_insights] Auto discovery error for {clean_ticker}: {e}")

    return data


@app.post("/api/discover-company-projects/{ticker}")
@app.get("/api/discover-company-projects/{ticker}")
async def discover_company_projects_route(ticker: str, force_refresh: bool = False):
    """
    Kích hoạt quét và bóc tách thông tin dự án mở rộng trực tiếp từ
    Website chính thức của doanh nghiệp và Báo cáo Thường niên (BCTN), Báo cáo Bán niên (BCTCSN).
    """
    clean_ticker = ticker.upper().strip()
    from project_discovery_engine import discover_company_projects_master
    return await discover_company_projects_master(clean_ticker, force_refresh=force_refresh)


@app.get("/api/ssc-company-profile/{ticker}")
async def get_ssc_company_profile_endpoint(ticker: str):
    """
    Endpoint tra cứu liên kết hồ sơ doanh nghiệp niêm yết và website chính thức
    được công bố trên Cổng UBCKNN (State Securities Commission - congbothongtin.ssc.gov.vn).
    """
    clean_ticker = ticker.upper().strip()
    from project_discovery_engine import get_ssc_company_profile_info
    return get_ssc_company_profile_info(clean_ticker)



@app.post("/api/valuation/dcf")
async def post_dcf_valuation(req: DcfCustomRequest):
    """
    Tính toán lại mô hình định giá DCF tương tác theo các tham số WACC, g, tốc độ tăng trưởng FCF người dùng tùy chỉnh.
    """
    clean_ticker = req.ticker.upper().strip()
    market_p = req.current_market_price
    if not market_p:
        try:
            live_price_info = await fetch_reconciled_live_price(clean_ticker)
            if live_price_info and live_price_info.get("latest_close"):
                market_p = float(live_price_info["latest_close"])
        except Exception:
            pass

    bundle = get_financial_data_bundle(clean_ticker, current_market_price=market_p)
    stm = bundle["statements_annual"]
    prof = bundle["company_profile"]
    
    base_fcf = stm["cfo"][-1] * 0.65
    net_debt = (stm["short_term_debt"][-1] + stm["long_term_debt"][-1]) - stm["cash_and_equivalents"][-1]
    
    dcf_res = calculate_dcf_model(
        base_fcf=base_fcf,
        fcf_growth_rate=req.fcf_growth_rate,
        wacc=req.wacc,
        terminal_g=req.terminal_g,
        shares_outstanding=prof["shares_outstanding_mil"],
        net_debt=max(0, net_debt),
        projection_years=req.projection_years
    )
    
    if not market_p:
        market_p = prof["market_cap_bil"] * 1000 / prof["shares_outstanding_mil"]
    mos = ((dcf_res["fair_value_per_share"] - market_p) / market_p) * 100.0 if market_p > 0 else 0.0

    return {
        "ticker": clean_ticker,
        "current_market_price": market_p,
        "dcf_fair_value": dcf_res["fair_value_per_share"],
        "margin_of_safety_percent": round(mos, 2),
        "dcf_details": dcf_res
    }


@app.post("/api/valuation/multi-model")
async def post_multi_model_valuation(req: MultiModelValuationRequest):
    """
    Tính toán lại 6 mô hình định giá lượng hóa tổng hợp (DCF, Graham 1-2-3, P/E, P/B)
    với các tham số và trọng số tùy chỉnh thời gian thực.
    """
    clean_ticker = req.ticker.upper().strip()
    live_p = req.current_market_price
    if not live_p:
        try:
            live_price_info = await fetch_reconciled_live_price(clean_ticker)
            if live_price_info and live_price_info.get("latest_close"):
                live_p = float(live_price_info["latest_close"])
        except Exception:
            pass

    bundle = get_financial_data_bundle(clean_ticker, current_market_price=live_p)
    stm = bundle["statements_annual"]
    prof = bundle["company_profile"]
    peers = bundle.get("peers_data", {})
    
    idx = -1
    base_fcf = stm["cfo"][idx] * 0.65 if "cfo" in stm and len(stm["cfo"]) > 0 else 1000.0
    net_debt = (stm["short_term_debt"][idx] + stm["long_term_debt"][idx]) - stm["cash_and_equivalents"][idx]
    
    shares = prof.get("shares_outstanding_mil") or 100.0
    eps = (stm["net_profit"][idx] * 1_000_000_000) / (shares * 1_000_000) if shares > 0 else 2500.0
    bvps = (stm["owner_equity"][idx] * 1_000_000_000) / (shares * 1_000_000) if shares > 0 else 18000.0
    
    ind_pe = req.industry_pe or (peers.get("industry_average", {}).get("pe") if isinstance(peers, dict) else getattr(peers, "industry_average", {}).get("pe", 13.0)) or 13.0
    ind_pb = req.industry_pb or (peers.get("industry_average", {}).get("pb") if isinstance(peers, dict) else getattr(peers, "industry_average", {}).get("pb", 1.6)) or 1.6
    
    ref_price = live_p or prof.get("current_market_price") or 25000.0

    res = calculate_multi_model_valuation(
        ticker=clean_ticker,
        current_market_price=ref_price,
        eps=eps,
        bvps=bvps,
        base_fcf=base_fcf,
        shares_outstanding_mil=shares,
        net_debt=max(0, net_debt),
        industry_pe=ind_pe,
        industry_pb=ind_pb,
        growth_rate=req.growth_rate or 12.0,
        wacc=req.wacc or 11.5,
        terminal_g=req.terminal_g or 2.5,
        risk_free_rate=req.risk_free_rate or 4.8,
        custom_weights=req.weights
    )
    return res


@app.get("/api/valuation/bands/{ticker}")
async def get_valuation_bands(ticker: str, timeframe: Optional[str] = "5Y"):
    """
    Trả về bộ dữ liệu dải định giá lịch sử P/E Band và P/B Band theo các khung thời gian (3M, 6M, 1Y, 5Y, ALL).
    """
    clean_ticker = ticker.upper().strip()
    bundle = get_financial_data_bundle(clean_ticker)
    prof = bundle.get("company_profile", {})
    peers = bundle.get("peers_data", {})
    
    ind_pe = (peers.get("industry_average", {}).get("pe") if isinstance(peers, dict) else getattr(peers, "industry_average", {}).get("pe", 13.0)) or 13.0
    ind_pb = (peers.get("industry_average", {}).get("pb") if isinstance(peers, dict) else getattr(peers, "industry_average", {}).get("pb", 1.6)) or 1.6
    
    from financial_data import generate_valuation_bands_dataset
    bands_data = generate_valuation_bands_dataset(clean_ticker, ind_pe, ind_pb)
    
    tf = timeframe.upper().strip() if timeframe else "5Y"
    if tf not in bands_data:
        tf = "5Y"
        
    return {
        "ticker": clean_ticker,
        "timeframe": tf,
        "timeframes_available": ["3M", "6M", "1Y", "5Y", "ALL"],
        "selected_data": bands_data.get(tf),
        "all_timeframes": bands_data
    }


@app.get("/api/database/companies")
async def get_database_companies(
    q: Optional[str] = None,
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = 100
):
    """
    Truy vấn danh sách doanh nghiệp từ cơ sở dữ liệu 650+ mã cổ phiếu Google Sheets / FiinTrade.
    Hỗ trợ tìm kiếm theo từ khóa mã, tên, sàn giao dịch (HOSE, HNX, UPCOM) và phân ngành.
    """
    results = search_companies(keyword=q or "", exchange=exchange, sector=sector, limit=limit)
    return {
        "total_matches": len(results),
        "total_database_records": len(COMPANY_DATABASE),
        "companies": results
    }


@app.get("/api/database/companies/{ticker}")
async def get_database_company_detail(ticker: str):
    """
    Tra cứu thông tin chi tiết một doanh nghiệp từ cơ sở dữ liệu (P/E, P/B, ROE, Vốn hóa, KQKD Q1-2026).
    """
    company = get_company(ticker)
    if not company:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mã {ticker} trong cơ sở dữ liệu doanh nghiệp")
    return company


@app.get("/api/database/sectors")
async def get_database_sectors():
    """
    Truy xuất danh sách thống kê tăng trưởng lợi nhuận và định giá toàn bộ các phân ngành kinh tế.
    """
    return {
        "total_sectors": len(SECTOR_DATABASE),
        "sectors": get_all_sectors_summary()
    }


@app.post("/api/database/sync")
async def post_sync_database():
    """
    Kích hoạt đồng bộ hóa dữ liệu trực tiếp từ liên kết Google Sheets của người dùng.
    """
    res = await sync_from_google_sheets(force=True)
    return res


class SsiConfigRequest(BaseModel):
    consumer_id: str
    consumer_secret: str


@app.get("/api/ssi/apis")
async def get_ssi_apis_catalog():
    """
    Trả về danh mục 9 mã API chính thức từ cổng SSI FastConnect Data kèm thông tin kết nối.
    """
    return {
        "status": "success",
        "total_apis": len(SSI_API_CATALOG),
        "documentation_url": "https://guide.ssi.com.vn/ssi-products/tieng-viet/fastconnect-data/danh-sach-cac-api",
        "apis": SSI_API_CATALOG,
        "is_configured": bool(SSI_CONFIG.get("consumer_id") and SSI_CONFIG.get("consumer_secret")),
        "active_mode": "SSI FastConnect Live" if SSI_CONFIG.get("access_token") else "Vietstock & Market Reconciled (Dual-Engine)"
    }


@app.post("/api/ssi/config")
async def set_ssi_config(req: SsiConfigRequest):
    """
    Lưu và xác thực thông tin ConsumerID & ConsumerSecret khách hàng để kích hoạt SSI FastConnect Data.
    """
    SSI_CONFIG["consumer_id"] = req.consumer_id.strip()
    SSI_CONFIG["consumer_secret"] = req.consumer_secret.strip()
    client = SSIFastConnectClient()
    token = await client.authenticate()
    return {
        "status": "success" if token else "saved_offline",
        "has_token": bool(token),
        "message": "Đã kết nối thành công tới cổng SSI FastConnect Data API v2!" if token else "Đã lưu cấu hình. Hệ thống sẽ tiếp tục sử dụng cơ chế dự phòng Vietstock Chart nếu cần."
    }


@app.get("/api/ssi/ohlc/{ticker}")
async def get_ssi_ohlcv(ticker: str, count: int = 60):
    """
    Truy xuất nến OHLCV kết hợp (SSI FastConnect DailyOhlc & Vietstock Technical Analysis Chart).
    """
    clean_ticker = ticker.upper().strip()
    candles = await fetch_hybrid_ohlcv_data(clean_ticker, count=count)
    return {
        "ticker": clean_ticker,
        "count": len(candles),
        "candles": candles,
        "source": "SSI FastConnect DailyOhlc / Vietstock Chart Reconciled"
    }


@app.get("/api/ssi/stock-depth/{ticker}")
async def get_ssi_stock_depth(ticker: str):
    """
    Truy xuất dữ liệu thị trường chi tiết theo chuẩn SSI DailyStockPrice API:
    Giá trần, giá sàn, giá tham chiếu, và dòng tiền khối ngoại (Foreign Net Flow).
    """
    clean_ticker = ticker.upper().strip()
    c = get_company(clean_ticker)
    live_p = float(c.get("market_price", 21700)) if c else 21700.0
    try:
        p_info = await fetch_reconciled_live_price(clean_ticker)
        if p_info:
            live_p = p_info.get("latest_close", live_p)
    except Exception:
        pass
    depth = get_stock_depth_metrics(clean_ticker, live_p)
    foreign = depth.get("foreign_trading", {})
    return {
        "status": "success",
        "ticker": clean_ticker,
        "foreign_net_value_bil": foreign.get("net_value_bil", 0.0),
        "foreign_net_volume": foreign.get("net_volume", 0),
        **depth
    }


@app.get("/api/ssi/market-overview")
async def get_ssi_market_overview():
    """
    Truy xuất độ rộng thị trường (Market Breadth) theo chuẩn SSI DailyIndex API:
    Chỉ số VN-INDEX, VN30, số mã tăng, giảm, đứng giá, trần, sàn và giá trị giao dịch.
    """
    return {
        "status": "success",
        **get_market_overview()
    }


@app.get("/api/technical/{ticker}")
async def get_technical_signals(ticker: str, resolution: str = "D", count: int = 350):
    """
    Truy xuất dữ liệu nến kỹ thuật thực tế và tính toán đầy đủ các chỉ báo kỹ thuật:
    MA20, MA50, MA200, EMA20, RSI(14), MACD(12,26,9), Bollinger Bands, Pivot Points (S1-S3, R1-R3).
    Dữ liệu nến được đồng bộ hóa từ SSI FastConnect và Vietstock/VNDirect/DNSE Multi-timeframe Feed.
    """
    clean_ticker = ticker.upper().strip()
    cache_key = f"{clean_ticker}_{resolution}_{count}"
    now_ts = time.time()
    if cache_key in _TECH_SIGNALS_CACHE and (now_ts - _TECH_SIGNALS_CACHE_TS.get(cache_key, 0)) < 30.0:
        return _TECH_SIGNALS_CACHE[cache_key]

    c = get_company(clean_ticker)
    exchange = (c.get("exchange") if c else "HOSE").upper()
    live_p = float(c.get("market_price", 21700)) if c else 21700.0
    try:
        p_info = await asyncio.wait_for(fetch_reconciled_live_price(clean_ticker), timeout=2.5)
        if p_info:
            live_p = p_info.get("latest_close", live_p)
    except Exception:
        pass

    # Lấy chuỗi nến thực tế từ SSI FastConnect / VNDirect / Vietstock / DNSE
    try:
        candles = await asyncio.wait_for(fetch_hybrid_ohlcv_data(clean_ticker, resolution=resolution, count=count), timeout=4.0)
    except Exception:
        candles = []
    
    # Tính toán toàn bộ chỉ báo kỹ thuật
    tech = calculate_technical_indicators(candles, live_p)
    depth = get_stock_depth_metrics(clean_ticker, live_p)
    foreign = depth.get("foreign_trading", {})

    shares_out = (c.get("shares_outstanding", 6400000000) if c else 6400000000) or 6400000000
    foreign_pct = (c.get("foreign_ownership_pct", 18.5) if c else 18.5) or 18.5

    res_dict = {
        "ticker": clean_ticker,
        "exchange": exchange,
        "last_price": tech["last_price"],
        "rsi_14": tech["rsi_14"],
        "rsi_status": tech["rsi_status"],
        "rsi_zone": tech.get("rsi_zone", "neutral"),
        "macd_status": tech["macd"]["status"],
        "macd_line": tech["macd"]["macd"],
        "macd_signal": tech["macd"]["signal"],
        "macd_hist": tech["macd"]["histogram"],
        "sma_20": tech["moving_averages"]["ma20"],
        "sma_50": tech["moving_averages"]["ma50"],
        "sma_200": tech["moving_averages"]["ma200"],
        "ema_20": tech["moving_averages"]["ema20"],
        "bb_upper": tech["bollinger_bands"]["upper"],
        "bb_middle": tech["bollinger_bands"]["middle"],
        "bb_lower": tech["bollinger_bands"]["lower"],
        "pivot_point": tech["pivot_points"]["pivot"],
        "support_1": tech["pivot_points"]["s1"],
        "support_2": tech["pivot_points"]["s2"],
        "support_3": tech["pivot_points"]["s3"],
        "resistance_1": tech["pivot_points"]["r1"],
        "resistance_2": tech["pivot_points"]["r2"],
        "resistance_3": tech["pivot_points"]["r3"],
        "overall_signal": tech["overall_signal"],
        "signal_color": tech["signal_color"],
        "recommendation_score": 8 if "MUA" in tech["overall_signal"] else (5 if "TRUNG" in tech["overall_signal"] else 3),
        "trend_summary": tech["trend_summary"],
        "candles_history": tech["candles_history"],
        "ceiling_price": depth["ceiling_price"],
        "floor_price": depth["floor_price"],
        "reference_price": depth["ref_price"],
        "foreign_buy_volume": foreign.get("buy_volume", 0),
        "foreign_sell_volume": foreign.get("sell_volume", 0),
        "foreign_net_volume": foreign.get("net_volume", 0),
        "foreign_net_value_bil": foreign.get("net_value_bil", 0.0),
        "foreign_current_room": int((foreign_pct / 100.0) * shares_out),
        "foreign_total_room": int(0.49 * shares_out),
        "stock_depth": depth,
        "ma20": tech["moving_averages"]["ma20"],
        "ma50": tech["moving_averages"]["ma50"],
        "ma200": tech["moving_averages"]["ma200"],
        "trend": tech["trend_summary"],
        "resolution": resolution,
        "data_engine": "SSI FastConnect & Vietstock Multi-timeframe Feed"
    }
    _TECH_SIGNALS_CACHE[cache_key] = res_dict
    _TECH_SIGNALS_CACHE_TS[cache_key] = now_ts
    return res_dict



@app.get("/api/search")
async def search_reports(ticker: str, sector: Optional[str] = ""):
    if not ticker:
        raise HTTPException(status_code=400, detail="Mã cổ phiếu không được để trống")
    try:
        results = await search_institutional_reports(ticker.strip().upper(), sector or "")
    except Exception as e:
        print(f"Error searching institutional reports for {ticker}: {e}")
        results = []
    return {
        "ticker": ticker.upper(),
        "total_found": len(results),
        "results": results
    }


@app.post("/api/auth/admin-verify")
async def api_admin_verify(req: AdminAuthRequest):
    """
    Xác thực tài khoản và mật khẩu Quản trị viên
    để mở khóa các tính năng cập nhật thủ công (Link, PDF, Text thô).
    """
    if is_admin_authorized(req.username, req.password):
        auth_data = get_admin_auth_data()
        return {
            "status": "ok",
            "authenticated": True,
            "username": auth_data.get("username", DEFAULT_ADMIN_USER),
            "message": "Xác thực tài khoản Quản trị viên thành công!"
        }
    raise HTTPException(
        status_code=403,
        detail="Tên đăng nhập hoặc mật khẩu quản trị viên không chính xác!"
    )


@app.post("/api/auth/forgot-password/request-otp")
async def api_request_password_otp(req: ForgotPasswordRequest):
    """
    Tạo và gửi mã xác nhận OTP 6 số qua email hoabhk31@gmail.com
    khi Quản trị viên quên mật khẩu.
    """
    email_clean = (req.email or "").strip().lower()
    auth_data = get_admin_auth_data()
    expected_email = auth_data.get("recovery_email", ADMIN_RECOVERY_EMAIL).lower()

    if email_clean != expected_email:
        raise HTTPException(
            status_code=400,
            detail=f"Email không hợp lệ! Tính năng khôi phục mật khẩu chỉ chấp nhận email quản trị viên đã đăng ký: {expected_email}"
        )

    # Sinh mã OTP 6 số ngẫu nhiên
    otp = f"{secrets.randbelow(900000) + 100000}"
    expires_at = time.time() + (15 * 60)  # Có hiệu lực trong 15 phút

    auth_data["active_otp"] = otp
    auth_data["otp_expires_at"] = expires_at
    save_admin_auth_data(auth_data)

    send_res = send_recovery_otp_email(expected_email, otp)

    return {
        "status": "ok",
        "message": f"Mã xác thực OTP (6 chữ số) đã được gửi đến email {expected_email}. Vui lòng kiểm tra hộp thư (hoặc mục Spam/Quảng cáo).",
        "recipient": expected_email,
        "expires_in_minutes": 15,
        "details": send_res
    }


@app.post("/api/auth/forgot-password/verify-reset")
async def api_verify_and_reset_password(req: VerifyResetPasswordRequest):
    """
    Xác minh mã OTP và cập nhật mật khẩu mới cho Quản trị viên.
    """
    email_clean = (req.email or "").strip().lower()
    otp_clean = (req.otp or "").strip()
    new_pwd = (req.new_password or "").strip()

    if len(new_pwd) < 4:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 4 ký tự!")

    auth_data = get_admin_auth_data()
    expected_email = auth_data.get("recovery_email", ADMIN_RECOVERY_EMAIL).lower()

    if email_clean != expected_email:
        raise HTTPException(status_code=400, detail="Email không khớp với email quản trị viên đã đăng ký!")

    active_otp = auth_data.get("active_otp")
    otp_expires_at = auth_data.get("otp_expires_at", 0)

    if not active_otp or time.time() > otp_expires_at:
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn hoặc chưa được tạo. Vui lòng bấm 'Gửi mã OTP' để nhận mã mới!")

    if otp_clean != active_otp:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác! Vui lòng kiểm tra lại email.")

    # Cập nhật mật khẩu mới bền vững vào file JSON
    auth_data["password"] = new_pwd
    auth_data["active_otp"] = None
    auth_data["otp_expires_at"] = 0
    save_admin_auth_data(auth_data)

    return {
        "status": "ok",
        "message": "Đổi mật khẩu Quản trị viên thành công! Mật khẩu mới đã được cập nhật.",
        "username": auth_data.get("username", DEFAULT_ADMIN_USER)
    }


@app.post("/api/crawl-url")
async def api_crawl_url(
    req: CrawlRequest,
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization,
        fallback_user=req.admin_user,
        fallback_password=req.admin_password
    )
    try:
        clean_ticker = (req.ticker or "HPG").upper().strip()
        data = await crawl_url_content(req.url, ticker=clean_ticker, institution=req.institution or "CTCK")
        
        market_p = 25000.0
        try:
            p_info = await fetch_reconciled_live_price(clean_ticker)
            if p_info:
                market_p = p_info.get("latest_close", 25000.0)
        except Exception:
            pass

        extracted_report = extract_financial_data_from_text(
            raw_text=data["text"],
            default_institution=req.institution or "CTCK",
            ticker=clean_ticker,
            current_market_price=market_p
        )
        extracted_report.source_url = req.url

        # Tự động lưu trữ các Catalysts và Rủi ro mà AI bóc tách được vào kho tri thức
        try:
            save_learned_ticker_catalysts(
                ticker=clean_ticker,
                catalysts=extracted_report.key_catalysts,
                risks=extracted_report.key_risks,
                source=req.institution or "Bóc tách URL",
                title=f"Báo cáo phân tích {clean_ticker}"
            )
            # Làm mới cache
            from crawler import _SYNCED_MATRIX_REPORTS_CACHE
            keys_to_del = [k for k in _SYNCED_MATRIX_REPORTS_CACHE.keys() if k.startswith(f"{clean_ticker}_")]
            for k in keys_to_del:
                _SYNCED_MATRIX_REPORTS_CACHE.pop(k, None)
            _SYNCHRONIZED_PRESETS_CACHE.pop(clean_ticker, None)
        except Exception as store_err:
            print(f"[Crawl URL] Lỗi lưu catalysts: {store_err}")

        return {
            "source_info": data,
            "extracted_report": extracted_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tải hoặc bóc tách URL: {str(e)}")


@app.post("/api/upload-pdf")
async def api_upload_pdf(
    file: UploadFile = File(...),
    ticker: Optional[str] = Form("HPG"),
    institution: Optional[str] = Form("CTCK"),
    admin_user: Optional[str] = Form(None),
    admin_password: Optional[str] = Form(None),
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization,
        fallback_user=admin_user,
        fallback_password=admin_password
    )
    try:
        clean_ticker = (ticker or "HPG").upper().strip()
        content = await file.read()
        parsed = parse_pdf_bytes(content, filename=file.filename)
        
        market_p = 25000.0
        try:
            p_info = await fetch_reconciled_live_price(clean_ticker)
            if p_info:
                market_p = p_info.get("latest_close", 25000.0)
        except Exception:
            pass

        extracted_report = extract_financial_data_from_text(
            raw_text=parsed["extracted_text"],
            default_institution=institution or "CTCK",
            ticker=clean_ticker,
            current_market_price=market_p
        )
        extracted_report.source_url = f"File: {file.filename} ({parsed['total_pages']} trang)"

        # Tự động lưu trữ Catalysts vào kho AI
        try:
            save_learned_ticker_catalysts(
                ticker=clean_ticker,
                catalysts=extracted_report.key_catalysts,
                risks=extracted_report.key_risks,
                source=institution or "Bóc tách PDF",
                title=f"File: {file.filename}"
            )
            from crawler import _SYNCED_MATRIX_REPORTS_CACHE
            keys_to_del = [k for k in _SYNCED_MATRIX_REPORTS_CACHE.keys() if k.startswith(f"{clean_ticker}_")]
            for k in keys_to_del:
                _SYNCED_MATRIX_REPORTS_CACHE.pop(k, None)
            _SYNCHRONIZED_PRESETS_CACHE.pop(clean_ticker, None)
        except Exception as store_err:
            print(f"[Upload PDF] Lỗi lưu catalysts: {store_err}")

        return {
            "file_info": {
                "filename": file.filename,
                "total_pages": parsed["total_pages"],
                "token_count": parsed["token_count"]
            },
            "extracted_report": extracted_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file PDF: {str(e)}")


@app.post("/api/analyze-raw")
async def api_analyze_raw(
    req: RawTextAnalysisRequest,
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization,
        fallback_user=req.admin_user,
        fallback_password=req.admin_password
    )
    if not req.raw_text or len(req.raw_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Nội dung văn bản quá ngắn để phân tích")
    
    clean_ticker = (req.ticker or "HPG").upper().strip()
    market_p = 25000.0
    try:
        p_info = await fetch_reconciled_live_price(clean_ticker)
        if p_info:
            market_p = p_info.get("latest_close", 25000.0)
    except Exception:
        pass

    report = extract_financial_data_from_text(
        raw_text=req.raw_text,
        default_institution=req.institution or "CTCK",
        ticker=clean_ticker,
        current_market_price=market_p
    )

    # Tự động lưu trữ Catalysts vào kho AI
    try:
        save_learned_ticker_catalysts(
            ticker=clean_ticker,
            catalysts=report.key_catalysts,
            risks=report.key_risks,
            source=req.institution or "Phân tích Text thô",
            title=f"Nhập văn bản thô {clean_ticker}"
        )
        from crawler import _SYNCED_MATRIX_REPORTS_CACHE
        keys_to_del = [k for k in _SYNCED_MATRIX_REPORTS_CACHE.keys() if k.startswith(f"{clean_ticker}_")]
        for k in keys_to_del:
            _SYNCED_MATRIX_REPORTS_CACHE.pop(k, None)
        _SYNCHRONIZED_PRESETS_CACHE.pop(clean_ticker, None)
    except Exception as store_err:
        print(f"[Analyze Raw] Lỗi lưu catalysts: {store_err}")

    return report


# -------------------------------------------------------------
# AI SELF-LEARNING & AUTONOMOUS CRAWLER ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/ai-learning/config")
async def api_get_ai_learning_config():
    """Lấy cấu hình tự học: tần suất quét, watchlist, trạng thái."""
    return ai_scheduler.get_config()


@app.post("/api/ai-learning/config")
async def api_save_ai_learning_config(req: LearningConfigRequest):
    """Cập nhật cấu hình tự động quét và tần suất học online."""
    updates = {}
    if req.enabled is not None:
        updates["enabled"] = req.enabled
    if req.interval_hours is not None:
        updates["interval_hours"] = req.interval_hours
    if req.watchlist is not None:
        updates["watchlist"] = req.watchlist
    if req.auto_ingest_matrix is not None:
        updates["auto_ingest_matrix"] = req.auto_ingest_matrix
    return ai_scheduler.update_config(updates)


@app.get("/api/ai-learning/templates")
async def api_list_ai_templates():
    """Liệt kê toàn bộ các Mẫu học (Few-Shot Templates) hệ thống và tùy biến của người dùng."""
    return template_store.list_all()


@app.post("/api/ai-learning/templates")
async def api_save_ai_template(
    req: TemplateCreateUpdateRequest,
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Thêm mới hoặc cập nhật một Mẫu học trích xuất Catalysts/Luận điểm (yêu cầu quyền Admin)."""
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization
    )
    data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    saved = template_store.add_or_update(data)
    return {"status": "SUCCESS", "template": saved}


@app.delete("/api/ai-learning/templates/{template_id}")
async def api_delete_ai_template(
    template_id: str,
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Xóa mẫu học do người dùng tự tạo (yêu cầu quyền Admin)."""
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization
    )
    success = template_store.delete(template_id)
    if not success:
        raise HTTPException(status_code=400, detail="Không thể xóa mẫu hệ thống hoặc mẫu không tồn tại")
    return {"status": "SUCCESS", "message": f"Đã xóa thành công mẫu {template_id}"}


@app.post("/api/ai-learning/templates/reset")
async def api_reset_ai_templates(
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Khôi phục danh sách mẫu học về mặc định ban đầu của hệ thống (yêu cầu quyền Admin)."""
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization
    )
    tpls = template_store.reset_to_defaults()
    return {"status": "SUCCESS", "templates_count": len(tpls)}


@app.post("/api/ai-learning/analyze-template-image")
async def api_analyze_template_image(
    file: UploadFile = File(...),
    ticker: Optional[str] = Form(None),
    x_admin_user: Optional[str] = Header(None, alias="X-Admin-User"),
    x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Tải lên hình ảnh báo cáo / bảng số liệu / biểu đồ để AI tự đọc, ghi nhớ
    và bóc tách thành Mẫu huấn luyện (tên, ngành, từ khóa, catalysts, luận điểm, rủi ro).
    Yêu cầu quyền Quản trị viên (Admin: 325396).
    """
    enforce_admin_permission(
        x_admin_user=x_admin_user,
        x_admin_password=x_admin_password,
        authorization=authorization
    )
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Tệp tin hình ảnh rỗng")
        res = await analyze_template_image_ai(
            image_bytes=content,
            filename=file.filename or "image.png",
            ticker_hint=ticker
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI phân tích hình ảnh: {str(e)}")


@app.post("/api/ai-learning/trigger-learn")
async def api_trigger_ai_learn(req: Optional[TriggerLearnRequest] = None):
    """Kích hoạt tiến trình quét và học online ngay lập tức."""
    target_tickers = req.tickers if req else None
    res = await ai_scheduler.run_learning_cycle(target_tickers=target_tickers)
    
    # Tự động xóa cache báo cáo cũ để các lần mở sau nạp lại dữ liệu mới nhất kèm Catalysts từ AI
    updated_tickers = res.get("updated_tickers", [])
    if updated_tickers:
        from crawler import _SYNCED_MATRIX_REPORTS_CACHE
        for sym in updated_tickers:
            try:
                keys_to_del = [k for k in _SYNCED_MATRIX_REPORTS_CACHE.keys() if k.startswith(f"{sym}_")]
                for k in keys_to_del:
                    _SYNCED_MATRIX_REPORTS_CACHE.pop(k, None)
                _SYNCHRONIZED_PRESETS_CACHE.pop(sym, None)
            except Exception:
                pass

        # Nạp lại dữ liệu ngầm trong nền (fire-and-forget) không làm treo hoặc chậm phản hồi HTTP
        async def _preload_updated_in_background(symbols: List[str]):
            for s in symbols[:5]:
                try:
                    await get_preset_by_ticker(s)
                except Exception as pre_err:
                    print(f"[AI Learn Preload] {s}: {pre_err}")

        asyncio.create_task(_preload_updated_in_background(updated_tickers))

    return res


@app.get("/api/ai-learning/history")
async def api_get_ai_learning_history(limit: int = 30):
    """Xem nhật ký các tài liệu báo cáo phân tích mà AI đã quét và tự học."""
    return ai_scheduler.get_history(limit=limit)


@app.get("/api/ai-learning/stats")
async def api_get_ai_learning_stats():
    """Thống kê tổng quan năng lực tự học: tổng mẫu, số catalysts tích lũy, độ tin cậy."""
    return ai_scheduler.get_stats()


@app.post("/api/reconcile")
async def api_reconcile(req: ReconcileRequest):
    if not req.reports:
        raise HTTPException(status_code=400, detail="Cần ít nhất 1 báo cáo phân tích để đối chiếu")
    result = calculate_consensus(
        reports=req.reports,
        ticker=req.ticker,
        company_name=req.company_name or f"Doanh nghiệp {req.ticker.upper()}",
        sector=req.sector or "Doanh nghiệp niêm yết",
        current_market_price=req.current_market_price,
        price_source_info=req.price_source_info
    )
    # Tự động đồng bộ các luận điểm tăng trưởng (Catalysts) mà AI đã tích lũy vào ma trận đối chiếu
    try:
        result = apply_learned_catalysts_to_report(result)
    except Exception as e:
        print(f"[API Reconcile] Lỗi áp dụng catalysts AI: {e}")
    return result


@app.post("/api/export-markdown")
async def api_export_markdown(req: ExportRequest):
    """
    Kết xuất Báo cáo so sánh đối chiếu chuẩn theo đúng cấu trúc 4 phần yêu cầu của người dùng.
    """
    data = normalize_full_matrix_dict(req.report_data)
    cs = data.get("consensus_summary", {})
    reports = data.get("matrix_table", [])

    ticker = data.get("ticker", "CP")
    company_name = data.get("company_name", f"Công ty Cổ phần {ticker}")
    sector = data.get("sector", "")
    analysis_date = data.get("analysis_date", datetime.now().strftime("%d/%m/%Y"))

    def _get(obj, k, d=""):
        return obj.get(k, d) if isinstance(obj, dict) else getattr(obj, k, d)

    current_market_p = _get(cs, "current_market_price", 0) or 0
    mean_target_p = _get(cs, "mean_target_price", 0) or 0
    avg_upside = _get(cs, "average_upside", 0.0) or 0.0
    consensus_rating = _get(cs, "consensus_rating", "MUA")
    consensus_score = _get(cs, "consensus_score", 4.0)
    rec_buy_zone = _get(cs, "recommended_buy_zone", "—")
    stop_loss_val = _get(cs, "stop_loss_threshold", "—")
    key_triggers = _get(cs, "key_triggers", []) or []

    md_lines = []
    md_lines.append(f"# BÁO CÁO PHÂN TÍCH ĐỐI CHIẾU ĐA TỔ CHỨC: {ticker} ({company_name})")
    md_lines.append(f"**Ngành:** {sector} | **Thị giá tham chiếu:** {current_market_p:,.0f} VND | **Thời điểm phân tích:** {analysis_date}")
    cs_head_up = f"Đã vượt kỳ vọng (+{abs(avg_upside):.1f}%)" if avg_upside < 0 else f"+{avg_upside:.1f}%"
    md_lines.append(f"**Consensus Rating:** {consensus_rating} (Điểm: {consensus_score}/5.0) | **Vùng giá mục tiêu:** {mean_target_p:,.0f} VND ({cs_head_up})\n")
    md_lines.append("---\n")

    # 1. BẢNG MA TRẬN SO SÁNH ĐA TỔ CHỨC
    md_lines.append("## 1. BẢNG MA TRẬN SO SÁNH ĐA TỔ CHỨC (BẮT BUỘC)")
    headers = ["Tiêu chí đối chiếu"] + [_get(r, "institution", "CTCK") for r in reports] + ["Độ lệch / Đồng thuận chung"]
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("| " + " | ".join([":---"] * len(headers)) + " |")

    # 1. Ngày phát hành
    dates = [_get(r, "report_date", "") for r in reports]
    md_lines.append(f"| **1. Ngày phát hành** | " + " | ".join(dates) + f" | {analysis_date} |")

    # 2. Khuyến nghị
    recs = [_get(r, "recommendation", "") for r in reports]
    md_lines.append(f"| **2. Khuyến nghị** | " + " | ".join(recs) + f" | **{consensus_rating}** |")

    # 3. Giá mục tiêu
    def _fmt_md_tp(r):
        if _get(r, "is_expired", False):
            tp = _get(r, "target_price", 0)
            return f"{tp:,.0f} VND (Quá 1 năm)" if tp > 0 else "— (Quá 1 năm)"
        if _get(r, "is_technical", False) or "PTKT" in (_get(r, "recommendation", "") or "").upper():
            return "— (PTKT)"
        tp = _get(r, "target_price", 0)
        if not tp or tp <= 0 or _get(r, "is_estimated_price", False):
            return "— (KQKD)"
        return f"{tp:,.0f} VND"
    tps = [_fmt_md_tp(r) for r in reports]
    cs_tp_str = f"**{mean_target_p:,.0f} VND**" if mean_target_p > 0 else "**— (Cần theo dõi thêm)**"
    md_lines.append(f"| **3. Giá mục tiêu** | " + " | ".join(tps) + f" | {cs_tp_str} |")

    # 4. Tiềm năng tăng giá
    def _fmt_up(r):
        if _get(r, "is_expired", False):
            return "— (Quá 1 năm)"
        up_val = safe_float(_get(r, "upside_percent"))
        if up_val is None:
            raw_up = _get(r, "upside_percent")
            return str(raw_up) if raw_up else "—"
        if up_val < 0:
            return f"Vượt +{abs(up_val):.1f}%"
        return f"+{up_val:.1f}%"
    ups = [_fmt_up(r) for r in reports]
    avg_up_val = safe_float(avg_upside)
    if mean_target_p <= 0 or avg_up_val is None:
        cs_up_str = "— (Cần theo dõi thêm)"
    elif avg_up_val < 0:
        cs_up_str = f"Đã vượt kỳ vọng (+{abs(avg_up_val):.1f}%)"
    else:
        cs_up_str = f"+{avg_up_val:.1f}%"
    md_lines.append(f"| **4. Tiềm năng tăng giá** | " + " | ".join(ups) + f" | **{cs_up_str}** |")

    # 5. P/E forward
    pes = [f"{_get(r, 'pe_forward'):.1f}x" if _get(r, 'pe_forward') else "—" for r in reports]
    valid_pes = [_get(r, "pe_forward") for r in reports if _get(r, "pe_forward") and _get(r, "pe_forward") > 0]
    avg_pe = sum(valid_pes) / len(valid_pes) if valid_pes else 0
    md_lines.append(f"| **5. P/E forward** | " + " | ".join(pes) + f" | {avg_pe:.1f}x |")

    # 6. P/B forward
    pbs = [f"{_get(r, 'pb_forward'):.2f}x" if _get(r, 'pb_forward') else "—" for r in reports]
    valid_pbs = [_get(r, "pb_forward") for r in reports if _get(r, "pb_forward") and _get(r, "pb_forward") > 0]
    avg_pb = sum(valid_pbs) / len(valid_pbs) if valid_pbs else 0
    md_lines.append(f"| **6. P/B forward** | " + " | ".join(pbs) + f" | {avg_pb:.2f}x |")

    # 7. Dự phóng Doanh thu
    revs = [_get(r, "revenue_forecast", "") for r in reports]
    md_lines.append(f"| **7. Dự phóng Doanh thu** | " + " | ".join(revs) + " | Đồng thuận tăng trưởng |")

    # 8. Dự phóng LNST
    npats = [_get(r, "npat_forecast", "") for r in reports]
    md_lines.append(f"| **8. Dự phóng LNST** | " + " | ".join(npats) + " | Kỳ vọng lợi nhuận bứt phá |")

    # 9. Luận điểm then chốt
    catalysts_cols = []
    for r in reports:
        cats = _get(r, "key_catalysts", []) or []
        cat_str = "<br>".join([f"{i+1}. {c}" for i, c in enumerate(cats)])
        catalysts_cols.append(cat_str)
    md_lines.append(f"| **9. Luận điểm then chốt** | " + " | ".join(catalysts_cols) + f" | Trọng tâm: Mở rộng quy mô kinh doanh |")

    # 10. Phương pháp định giá
    methods = [_get(r, "valuation_method", "") or "—" for r in reports]
    md_lines.append(f"| **10. Phương pháp định giá** | " + " | ".join(methods) + " | Kết hợp P/E & DCF |")

    md_lines.append("\n---\n")

    # 2. PHÂN TÍCH NHÂN QUẢ & ĐỘNG LỰC TĂNG TRƯỞNG CỐT LÕI
    md_lines.append("## 2. PHÂN TÍCH CHUYÊN SÂU: NGUYÊN NHÂN - KẾT QUẢ - BẰNG CHỨNG (CAUSALITY ANALYSIS)\n")
    causality_items = data.get("causality_analysis", []) or []
    for c in causality_items:
        md_lines.append(f"### {_get(c, 'category', 'Phân tích')}")
        md_lines.append(f"- **Hiện tượng tài chính:** {_get(c, 'phenomenon', '')}")
        md_lines.append(f"- **Nguyên nhân cốt lõi:** {_get(c, 'root_causes', '')}")
        md_lines.append(f"- **Bằng chứng số liệu:** {_get(c, 'data_evidence', '')}\n")

    md_lines.append("---\n")

    # 3. BẢNG PHÂN HÓA QUAN ĐIỂM GIỮA CÁC TỔ CHỨC
    md_lines.append("## 3. BẢNG PHÂN HÓA QUAN ĐIỂM (DISENSUS & CONSENSUS ANALYSIS)\n")
    md_lines.append("| Tiêu chí phân hóa | Phe Lạc quan (Bulls) | Phe Thận trọng (Bears) | Bằng chứng & Luận điểm |")
    md_lines.append("| :--- | :--- | :--- | :--- |")
    disensus_items = data.get("disensus_table", []) or []
    for d in disensus_items:
        md_lines.append(f"| **{_get(d, 'variable', '')}** | {_get(d, 'bulls_view', '')} | {_get(d, 'bears_view', '')} | {_get(d, 'evidence', '')} |")
    md_lines.append("\n---\n")

    # 4. KẾT LUẬN & HÀNH ĐỘNG DÀNH CHO NHÀ ĐẦU TƯ
    md_lines.append("## 4. KẾT LUẬN & HÀNH ĐỘNG DÀNH CHO NHÀ ĐẦU TƯ\n")
    md_lines.append(f"- **Consensus Rating:** **{consensus_rating}** (Điểm trung bình: {consensus_score}/5.0).")
    md_lines.append(f"- **Vùng giá mục tiêu bình quân:**")
    if avg_upside < 0:
        mean_upside_str = f"Thị giá vượt định giá: **+{abs(avg_upside):.1f}%** (Đã vượt kỳ vọng)"
    else:
        mean_upside_str = f"Upside tiềm năng: **+{avg_upside:.1f}%**"
    md_lines.append(f"  - Giá bình quân (Mean): **{mean_target_p:,.0f} VND** ({mean_upside_str}).")
    median_tp = _get(cs, "median_target_price", 0) or mean_target_p
    min_tp = _get(cs, "min_target_price", 0) or mean_target_p
    max_tp = _get(cs, "max_target_price", 0) or mean_target_p
    spread = _get(cs, "target_price_spread_percent", 0) or 0.0
    md_lines.append(f"  - Giá trung vị (Median): **{median_tp:,.0f} VND**.")
    md_lines.append(f"  - Khung giá mục tiêu [Min - Max]: **{min_tp:,.0f} - {max_tp:,.0f} VND** (Biên độ chênh lệch: {spread:.1f}%).")
    md_lines.append(f"- **Vùng giá giải ngân khuyến nghị:** `{rec_buy_zone}`.")
    md_lines.append(f"- **Ngưỡng quản trị rủi ro (Stop-loss):** `{stop_loss_val}`.")
    md_lines.append(f"- **Trigger then chốt cần theo dõi định kỳ:**")
    for t in key_triggers:
        md_lines.append(f"  * {t}")

    markdown_content = "\n".join(md_lines)
    return {"markdown": markdown_content}


PDF_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache", "edocs_pdfs")
os.makedirs(PDF_CACHE_DIR, exist_ok=True)


def match_ctck_institution(target_inst: str, candidate_name: str) -> bool:
    """
    So khớp tên Công ty Chứng khoán thông minh dựa trên tên viết tắt, mã thương hiệu và biệt danh phổ biến.
    Đảm bảo tính toàn vẹn thương hiệu (Brand Integrity) tuyệt đối, không nhầm lẫn giữa các CTCK khác nhau.
    """
    if not target_inst or not candidate_name:
        return False
    t_clean = re.sub(r'[^a-z0-9]', '', target_inst.lower())
    c_clean = re.sub(r'[^a-z0-9]', '', candidate_name.lower())
    if not t_clean or not c_clean:
        return False
    if t_clean == c_clean:
        return True

    aliases = {
        'kis': ['kis', 'kisvn', 'kisresearch', 'korea'],
        'bsc': ['bsc', 'bidv', 'bscresearch'],
        'vcbs': ['vcbs', 'vietcombank'],
        'evs': ['evs', 'everest'],
        'vpx': ['vpx', 'vpbs', 'vps', 'vpbank', 'vpbanksecurities'],
        'mbs': ['mbs', 'mbke', 'mbresearch', 'mbsecurities'],
        'fpts': ['fpts', 'fpt'],
        'ssi': ['ssi', 'ssiresearch'],
        'hsc': ['hsc', 'hcm'],
        'vndirect': ['vnd', 'vndirect', 'dstock'],
        'vietcap': ['vcsc', 'vietcap', 'banviet', 'vcap'],
        'kbsv': ['kbsv', 'kb', 'kbsec'],
        'dsc': ['dsc'],
        'mas': ['mas', 'mirae', 'miraeasset'],
        'bvs': ['bvs', 'bvsc', 'baoviet'],
        'tcbs': ['tcbs', 'techcom'],
        'tps': ['tps', 'tienphong'],
        'vds': ['vds', 'vdsc', 'rongviet'],
        'kafi': ['kafi'],
        'ssv': ['ssv', 'shinhan'],
        'vietinbank': ['cts', 'vietin', 'vietinbank', 'vbse'],
        'nhsv': ['nhsv', 'namhae'],
        'ysvn': ['ysvn', 'yuanta'],
        'vfs': ['vfs', 'nhatviet'],
        'beta': ['beta'],
        'bmsc': ['bmsc', 'baominh'],
        'csi': ['csi', 'kienthiet'],
        'acbs': ['acbs', 'acb'],
        'tvsi': ['tvsi', 'tanviet'],
        'shs': ['shs', 'saigonhanoi'],
        'phsv': ['phsv', 'phuhung'],
        'abs': ['abs', 'anbinh'],
        'pinetree': ['pinetree', 'pine'],
        'vics': ['vics', 'thuongmai'],
        'aps': ['aps', 'chauthaibinhduong'],
        'agriseco': ['agr', 'agriseco', 'agribank']
    }

    # 1. Kiểm tra theo alias groups
    for key, group in aliases.items():
        t_has = any(w == t_clean or (len(w) >= 3 and (t_clean.startswith(w) or w in t_clean)) for w in group)
        c_has = any(w == c_clean or (len(w) >= 3 and (c_clean.startswith(w) or w in c_clean)) for w in group)
        if t_has and c_has:
            return True

    # 2. Kiểm tra nếu cùng chứa một từ khóa mã CTCK trong aliases
    for key, group in aliases.items():
        for w in group:
            if len(w) >= 3:
                if (w in t_clean and w in c_clean):
                    return True

    # 3. Nếu cả 2 đều đủ dài và chứa nhau hoặc bắt đầu bằng nhau
    if len(t_clean) >= 3 and len(c_clean) >= 3:
        if t_clean in c_clean or c_clean in t_clean or t_clean.startswith(c_clean) or c_clean.startswith(t_clean):
            return True

    return False


async def fetch_real_institution_pdf(clean_ticker: str, clean_inst: str, preferred_url: Optional[str] = None) -> Optional[tuple]:
    """
    Tải file PDF báo cáo phân tích thực tế trực tiếp từ Vietstock eDocs hoặc nguồn CTCK chính thức.
    TUÂN THỦ NGUYÊN TẮC BẢO TOÀN THƯƠNG HIỆU (Brand Purity):
      - Chỉ tải và trả về file PDF nếu ĐÚNG LÀ của CTCK được yêu cầu.
      - Tuyệt đối KHÔNG gán file PDF của CTCK này cho CTCK khác.
    Trả về (bytes, filename, actual_url) hoặc None.
    """
    def is_valid_ticker_pdf_candidate(url_str: str, candidate_title: str = "") -> bool:
        if not url_str or not url_str.startswith("http") or ".pdf" not in url_str.lower():
            return False
        u_low = url_str.lower()
        t_low = candidate_title.lower()

        # Kiểm tra tiêu đề nếu bắt đầu bằng mã khác (ví dụ "GMD: ...")
        leading_m = re.match(r'^\s*\[?([A-Z0-9]{3,4})\]?\s*[:\-]', candidate_title, re.IGNORECASE)
        if leading_m and leading_m.group(1).upper() != clean_ticker:
            return False

        # Kiểm tra nếu url chứa rõ ràng slug của mã khác
        url_ticker_m = re.search(r'/([a-z0-9]{3,4})[_\-]', u_low)
        if url_ticker_m:
            detected_sym = url_ticker_m.group(1).upper()
            if detected_sym != clean_ticker and detected_sym in VIETNAM_STOCK_DIRECTORY:
                return False

        # Kiểm tra xung đột ngành rõ rệt: Tuyệt đối không gán báo cáo ngành khác cho mã không thuộc ngành đó
        mismatched_keywords = [
            ("nganhthep", ["HPG", "HSG", "NKG", "VGS", "TLH", "POM"]),
            ("nganh_thep", ["HPG", "HSG", "NKG", "VGS", "TLH", "POM"]),
            ("bcsxphanbon", ["DPM", "DCM", "BFC", "LAS"]),
            ("phan_bon", ["DPM", "DCM", "BFC", "LAS"]),
            ("nganhdetmay", ["TNG", "MSH", "VGT", "STK", "GIL"]),
            ("det_may", ["TNG", "MSH", "VGT", "STK", "GIL"]),
            ("nganh_chung_khoan", ["SSI", "HCM", "VND", "VCI", "SHS", "MBS", "FTS", "BSI", "CTS", "VIX"]),
            ("chungkhoantruocthem", ["SSI", "HCM", "VND", "VCI", "SHS", "MBS", "FTS", "BSI", "CTS", "VIX"])
        ]
        for kw, valid_tickers in mismatched_keywords:
            if kw in u_low or kw in t_low:
                if clean_ticker not in valid_tickers:
                    return False
        return True

    candidates = []

    # 1. URL được cung cấp từ matched_item (đã được khớp CTCK từ trước):
    if preferred_url and is_valid_ticker_pdf_candidate(preferred_url):
        candidates.append((preferred_url, clean_inst))

    # 2. Quét eDocs từ Vietstock eDocs Portal nếu cần tìm thêm hoặc preferred_url rỗng
    try:
        edocs_items = await fetch_edocs_reports(clean_ticker, limit=20)
    except Exception as e:
        print(f"[PDF Resolver] Lỗi khi quét Vietstock eDocs cho {clean_ticker}: {e}")
        edocs_items = []

    matched_edocs = []
    for it in edocs_items:
        src = it.get("SourceName", "")
        title = it.get("Title", "")
        url = it.get("Url", "")
        if not is_valid_ticker_pdf_candidate(url, title):
            continue
        if match_ctck_institution(clean_inst, src) or match_ctck_institution(clean_inst, title) or match_ctck_institution(clean_inst, url):
            matched_edocs.append((url, src or clean_inst))

    # Danh sách chỉ bao gồm những file PDF chính xác của CTCK đó (KHÔNG CÓ other_edocs)
    all_candidates = candidates + matched_edocs

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*"
    }

    for url, inst_name in all_candidates:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        safe_name = to_ascii_slug(inst_name) or "CTCK"
        cached_file_path = os.path.join(PDF_CACHE_DIR, f"{clean_ticker}_{safe_name}_{url_hash}.pdf")

        # Kiểm tra file trong cache đĩa (nếu kích thước > 5KB)
        if os.path.exists(cached_file_path) and os.path.getsize(cached_file_path) > 5000:
            try:
                with open(cached_file_path, "rb") as f:
                    content = f.read()
                if b"%PDF" in content[:1024] or len(content) > 5000:
                    filename = f"{clean_ticker}_{safe_name}_Bao_Cao_Phan_Tich.pdf"
                    return content, filename, url
            except Exception as read_err:
                print(f"[PDF Cache] Lỗi đọc file cache {cached_file_path}: {read_err}")

        # Chưa có trong cache -> tải trực tiếp từ nguồn eDocs
        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and (b"%PDF" in resp.content[:1024] or len(resp.content) > 5000):
                    try:
                        with open(cached_file_path, "wb") as f:
                            f.write(resp.content)
                    except Exception as write_err:
                        print(f"[PDF Cache] Lỗi ghi file cache {cached_file_path}: {write_err}")

                    filename = f"{clean_ticker}_{safe_name}_Bao_Cao_Phan_Tich.pdf"
                    return resp.content, filename, url
        except Exception as dl_err:
            print(f"[PDF Resolver] Tải file PDF thất bại từ {url}: {dl_err}")
            continue

    return None


@app.get("/api/reports/pdf/{ticker}/{institution}")
async def get_report_pdf(
    ticker: str,
    institution: str,
    request: Request,
    source_url: Optional[str] = None,
    date: Optional[str] = None,
    download: Optional[int] = 0
):
    """
    Trả về file PDF Báo cáo Phân tích & Định giá thực tế của Công ty Chứng khoán tương ứng
    (Tải trực tiếp từ nguồn Vietstock eDocs / CTCK Research Hub, có bộ nhớ đệm cache).
    Cho phép xem trực tiếp trên trình duyệt (inline) hoặc tải về (download).
    """
    clean_ticker = ticker.upper().strip()
    clean_inst = urllib.parse.unquote(institution).removesuffix(".pdf").strip()

    is_download = bool(download) or (request.query_params.get("download") in ("1", "true", "yes"))
    disposition_type = "attachment" if is_download else "inline"

    # Tìm kiếm báo cáo trong _SYNCHRONIZED_PRESETS_CACHE, PRESET_DATASETS hoặc gọi get_preset_by_ticker
    full_report = _SYNCHRONIZED_PRESETS_CACHE.get(clean_ticker) or PRESET_DATASETS.get(clean_ticker)
    if not full_report:
        full_report = await get_preset_by_ticker(clean_ticker, sync_live_price=False)

    matched_item = None
    if full_report and full_report.matrix_table:
        for item in full_report.matrix_table:
            if match_ctck_institution(clean_inst, item.institution) or clean_inst.lower() in item.institution.lower() or item.institution.lower() in clean_inst.lower():
                matched_item = item
                break

    preferred_url = source_url if (source_url and source_url.startswith(("http://", "https://"))) else (matched_item.source_url if (matched_item and matched_item.source_url) else None)

    # Tải file PDF báo cáo phân tích thực tế từ Vietstock eDocs / CTCK
    real_pdf_result = await fetch_real_institution_pdf(clean_ticker, clean_inst, preferred_url)

    if real_pdf_result:
        pdf_bytes, filename, actual_url = real_pdf_result
        # Cập nhật lại source_url trong bộ nhớ nếu trước đó chỉ là link HTML tổng quát
        if matched_item and (not matched_item.source_url or not matched_item.source_url.endswith(".pdf")):
            matched_item.source_url = actual_url

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": make_content_disposition(disposition_type, filename),
                "Cache-Control": "public, max-age=86400"
            }
        )

    # Fallback tự động sinh PDF chuyên nghiệp chuẩn CTCK khi không có kết nối online
    cs = full_report.consensus_summary if full_report else None
    cur_p = cs.current_market_price if cs else (getattr(full_report, "current_price", 0) if full_report else 0)
    report_dict = {
        "institution": matched_item.institution if matched_item else clean_inst,
        "target_price": (matched_item.adjusted_target_price or matched_item.target_price) if matched_item else (cs.mean_target_price if cs else 0),
        "current_price": cur_p,
        "upside_pct": matched_item.upside_percent if matched_item else (cs.average_upside if cs else 0.0),
        "recommendation": matched_item.recommendation if matched_item else (cs.consensus_rating if cs else "MUA"),
        "date": (matched_item.report_date if matched_item else date) or time.strftime("%d/%m/%Y"),
        "catalysts": " • " + "\n • ".join(matched_item.key_catalysts) if (matched_item and matched_item.key_catalysts) else "Triển vọng kinh doanh khả quan nhờ mở rộng công suất và nhu cầu thị trường hồi phục mạnh mẽ.",
        "risks": " • " + "\n • ".join(matched_item.key_risks) if (matched_item and matched_item.key_risks) else "Biến động chi phí nguyên vật liệu đầu vào và rủi ro tỷ giá.",
    }

    consensus_dict = {
        "avg_target": cs.mean_target_price if cs else 0,
        "avg_upside_pct": cs.average_upside if cs else 0.0,
        "highest_target": cs.max_target_price if cs else 0,
        "lowest_target": cs.min_target_price if cs else 0,
        "total_reports": len(full_report.matrix_table) if (full_report and full_report.matrix_table) else 1,
    }

    comp_info = VIETNAM_STOCK_DIRECTORY.get(clean_ticker, {})
    company_name = (full_report.company_name if full_report else None) or comp_info.get("name") or f"CTCP {clean_ticker}"
    sector = (full_report.sector if full_report else None) or comp_info.get("sector") or "Doanh nghiệp niêm yết"

    pdf_bytes = generate_ctck_report_pdf(
        ticker=clean_ticker,
        company_name=company_name,
        sector=sector,
        report=report_dict,
        consensus=consensus_dict,
    )

    safe_inst_name = to_ascii_slug(report_dict["institution"]) or "CTCK"
    filename = f"{clean_ticker}_{safe_inst_name}_Bao_Cao_Phan_Tich.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": make_content_disposition(disposition_type, filename),
            "Cache-Control": "public, max-age=3600"
        }
    )


@app.post("/api/export-csv")
async def api_export_csv(req: ExportRequest):
    data = normalize_full_matrix_dict(req.report_data)
    reports = data.get("matrix_table", [])
    output = io.StringIO()
    writer = csv.writer(output)

    def _get(obj, k, d=""):
        return obj.get(k, d) if isinstance(obj, dict) else getattr(obj, k, d)

    # Header
    headers = ["Tieu_chi"] + [_get(r, "institution", "CTCK") for r in reports]
    writer.writerow(headers)

    # Rows
    writer.writerow(["Ngay_phat_hanh"] + [_get(r, "report_date", "") for r in reports])
    writer.writerow(["Khuyen_nghi"] + [_get(r, "recommendation", "") for r in reports])
    writer.writerow(["Gia_muc_tieu"] + [f"{_get(r, 'target_price', 0):.0f}" for r in reports])
    writer.writerow(["Upside_percent"] + [f"{_get(r, 'upside_percent', 0):.1f}%" if _get(r, 'upside_percent') is not None else "" for r in reports])
    writer.writerow(["PE_forward"] + [str(_get(r, "pe_forward", "") or "") for r in reports])
    writer.writerow(["PB_forward"] + [str(_get(r, "pb_forward", "") or "") for r in reports])
    writer.writerow(["Du_phong_Doanh_thu"] + [_get(r, "revenue_forecast", "") for r in reports])
    writer.writerow(["Du_phong_LNST"] + [_get(r, "npat_forecast", "") for r in reports])
    writer.writerow(["Phuong_phap_dinh_gia"] + [_get(r, "valuation_method", "") or "" for r in reports])

    csv_content = output.getvalue()
    ticker = data.get("ticker", "CP")
    filename = f"IERM_{ticker}_Matrix.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": make_content_disposition("attachment", filename)}
    )


@app.post("/api/export-matrix-pdf")
async def api_export_matrix_pdf(req: ExportRequest):
    """
    Xuất toàn bộ Bảng đối chiếu trực diện đa tổ chức ra file PDF A4 Landscape định dạng chuyên nghiệp.
    """
    report_dict = normalize_full_matrix_dict(req.report_data)
    pdf_bytes = generate_matrix_table_pdf(report_dict)
    ticker = report_dict.get("ticker", "CP")
    filename = f"IERM_{ticker}_Matrix_Table.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": make_content_disposition("attachment", filename),
            "Cache-Control": "no-cache"
        }
    )


class PeerExportPdfRequest(BaseModel):
    peers_data: dict
    radar_image_base64: Optional[str] = None


@app.post("/api/peers/export-pdf")
async def api_export_peers_pdf(req: PeerExportPdfRequest):
    """
    Xuất Báo cáo đối thủ cùng ngành & Radar sức mạnh tài chính ra file PDF A4 Landscape định dạng chuẩn tổ chức.
    """
    import traceback
    target = (req.peers_data.get("target_ticker") or "DN").upper()
    raw_sector = req.peers_data.get("sector_name") or "Nganh"
    clean_sector = "".join(c for c in raw_sector if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    try:
        pdf_bytes = generate_peer_comparison_pdf(req.peers_data, req.radar_image_base64)
    except Exception as exc:
        err_detail = traceback.format_exc()
        print(f"[PDF-ERROR] {exc}\n{err_detail}", flush=True)
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(exc)}\n{err_detail}")
    filename = f"Bao_Cao_Nganh_{target}_{clean_sector}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": make_content_disposition("attachment", filename),
            "Cache-Control": "no-cache"
        }
    )


@app.get("/api/pdf-proxy")
async def pdf_proxy(
    url: str,
    request: Request,
    ticker: Optional[str] = None,
    source: Optional[str] = None,
    download: Optional[int] = 0
):
    """
    Proxy tải an toàn và stream file PDF từ bên ngoài (Vietstock eDocs, CTCK) về cho iframe,
    loại bỏ lỗi Mixed Content (HTTP vs HTTPS), CSP frame-ancestors và X-Frame-Options SAMEORIGIN.
    """
    if not url or not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL không hợp lệ")

    is_download = bool(download) or (request.query_params.get("download") in ("1", "true", "yes"))
    disposition_type = "attachment" if is_download else "inline"
    clean_ticker = (ticker or "IERM").upper().strip()
    safe_source = to_ascii_slug(source or "Bao_Cao")
    filename = f"{clean_ticker}_{safe_source}.pdf"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://finance.vietstock.vn/"
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
            res = await client.get(url)
            if res.status_code == 200:
                if res.content.startswith(b"%PDF") or "pdf" in res.headers.get("content-type", "").lower():
                    return Response(
                        content=res.content,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": make_content_disposition(disposition_type, filename),
                            "Cache-Control": "public, max-age=3600"
                        }
                    )
    except Exception as exc:
        print(f"[PDF-PROXY-WARN] Failed to fetch {url}: {exc}")

    # Fallback nếu tải không được: nếu có ticker, phục vụ báo cáo PDF tương ứng của mã đó
    if ticker:
        return await get_report_pdf(
            ticker=ticker,
            institution=f"{source or 'CTCK'}.pdf",
            request=request,
            source_url=url,
            download=download
        )

    raise HTTPException(status_code=404, detail="Không thể tải file PDF từ nguồn chỉ định")


@app.post("/api/export-matrix-excel")
async def api_export_matrix_excel(req: ExportRequest):
    """
    Xuất Bảng đối chiếu đa tổ chức ra file Excel XML/HTML Spreadsheet (.xls)
    hỗ trợ 100% tiếng Việt UTF-8, định dạng màu sắc cột, tiêu đề, căn chỉnh số liệu chuẩn xác.
    """
    data = normalize_full_matrix_dict(req.report_data)
    reports = data.get("matrix_table", [])
    if reports:
        from engine import get_report_date_sort_key
        reports = sorted(reports, key=get_report_date_sort_key, reverse=True)
    cs = data.get("consensus_summary", {})

    ticker = data.get("ticker", "CP")
    company_name = data.get("company_name", f"Công ty Cổ phần {ticker}")
    sector = data.get("sector", "")

    def _get(obj, k, d=""):
        return obj.get(k, d) if isinstance(obj, dict) else getattr(obj, k, d)

    current_market_p = _get(cs, "current_market_price", 0) or 0
    mean_target_p = _get(cs, "mean_target_price", 0) or 0
    avg_upside = _get(cs, "average_upside", 0.0) or 0.0
    consensus_rating = _get(cs, "consensus_rating", "MUA")
    rec_buy_zone = _get(cs, "recommended_buy_zone", "—")
    stop_loss_val = _get(cs, "stop_loss_threshold", "—")

    html_lines = [
        '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">',
        '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
        '<!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet>',
        f'<x:Name>IERM_{ticker}_Matrix</x:Name>',
        '<x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]-->',
        '<style>',
        'body { font-family: "Segoe UI", Arial, sans-serif; }',
        'table { border-collapse: collapse; width: 100%; }',
        'th { background-color: #0f172a; color: #38bdf8; border: 1px solid #334155; padding: 8px; font-weight: bold; text-align: center; }',
        'td { border: 1px solid #cbd5e1; padding: 6px; vertical-align: top; }',
        '.header-row { background-color: #0284c7; color: #ffffff; font-weight: bold; }',
        '.criteria-col { background-color: #f8fafc; font-weight: bold; color: #1e293b; min-width: 220px; }',
        '.consensus-col { background-color: #f0fdf4; font-weight: bold; color: #059669; text-align: center; }',
        '</style></head><body>',
        f'<div style="background-color: #0f172a; padding: 12px 16px; border-radius: 4px; margin-bottom: 12px;">',
        f'  <div style="font-size: 11px; font-weight: normal; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase;">IERM TERMINAL // BẢNG ĐỐI CHIẾU TRỰC DIỆN ĐA TỔ CHỨC</div>',
        f'  <div style="font-size: 17px; font-weight: bold; color: #facc15; margin-top: 4px; text-shadow: 0 1px 2px rgba(0,0,0,0.5);"><span style="color:#38bdf8;">Mã CK:</span> {ticker} - <span style="color:#ffffff;">{company_name}</span> | <span style="color:#94a3b8; font-size: 14px; font-weight: normal;">Ngành: {sector}</span></div>',
        f'  <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;"><b>Thị giá tham chiếu:</b> <span style="color:#38bdf8; font-weight:bold;">{current_market_p:,.0f} VND</span> | <b>Định giá TB (Mean):</b> <span style="color:#4ade80; font-weight:bold;">{mean_target_p:,.0f} VND</span> | <b>{"Kỳ vọng thị giá vs Định giá" if avg_upside < 0 else "Upside kỳ vọng"}:</b> <span style="color:{"#f43f5e" if avg_upside < 0 else "#22c55e"}; font-weight:bold;">{"Đã vượt kỳ vọng (+" + f"{abs(avg_upside):.1f}" + "%)" if avg_upside < 0 else f"+{avg_upside:.1f}%"}</span></div>',
        f'</div>',
        '<table border="1">'
    ]

    # Header
    html_lines.append('<tr>')
    html_lines.append('<th class="header-row" style="text-align:left;">TIÊU CHÍ ĐỐI CHIẾU</th>')
    for r in reports:
        html_lines.append(f'<th class="header-row">{_get(r, "institution", "CTCK")}<br><span style="font-size:10px;font-weight:normal;">({_get(r, "report_date", "")})</span></th>')
    html_lines.append('<th class="header-row" style="background-color:#059669;color:#ffffff;">CONSENSUS & ĐỒNG THUẬN</th>')
    html_lines.append('</tr>')

    def add_row(criteria, get_val_fn, consensus_str, is_bold=False):
        html_lines.append('<tr>')
        html_lines.append(f'<td class="criteria-col">{criteria}</td>')
        for r in reports:
            val = get_val_fn(r)
            b_tag = "<b>" if is_bold else ""
            b_end = "</b>" if is_bold else ""
            html_lines.append(f'<td style="text-align:center;">{b_tag}{val}{b_end}</td>')
        html_lines.append(f'<td class="consensus-col">{consensus_str}</td>')
        html_lines.append('</tr>')

    # 1. Khuyến nghị
    add_row("1. Khuyến nghị đầu tư", lambda r: _get(r, "recommendation", "N/A"), consensus_rating, is_bold=True)
    # 2. Giá mục tiêu
    def _fmt_excel_tp(r):
        if _get(r, "is_expired", False):
            tp = _get(r, "target_price", 0)
            return f"{tp:,.0f} đ (Quá 1 năm)" if tp > 0 else "— (Quá 1 năm)"
        if _get(r, "is_technical", False):
            return "— (PTKT)"
        tp = _get(r, "target_price", 0)
        if not tp or tp <= 0:
            return "— (KQKD)"
        return f"{tp:,.0f} đ"
    excel_cs_tp = f"Mean: {mean_target_p:,.0f} đ" if mean_target_p > 0 else "Mean: — (Cần theo dõi thêm)"
    add_row("2. Giá mục tiêu (VND)", _fmt_excel_tp, excel_cs_tp, is_bold=True)

    # 3. Tiềm năng tăng giá
    def _fmt_excel_upside(r):
        if _get(r, "is_expired", False):
            return "— (Quá 1 năm)"
        up_val = safe_float(_get(r, "upside_percent"))
        if up_val is None:
            raw_up = _get(r, "upside_percent")
            return str(raw_up) if raw_up else "—"
        if up_val < 0:
            return f"Vượt +{abs(up_val):.1f}%"
        return f"+{up_val:.1f}%"
    avg_up_val = safe_float(avg_upside)
    if mean_target_p <= 0 or avg_up_val is None:
        excel_cs_up = "— (Cần theo dõi thêm)"
    elif avg_up_val < 0:
        excel_cs_up = f"Đã vượt kỳ vọng (+{abs(avg_up_val):.1f}%)"
    else:
        excel_cs_up = f"+{avg_up_val:.1f}%"
    add_row("3. Tiềm năng tăng giá (Upside)", _fmt_excel_upside, excel_cs_up, is_bold=True)
    # 4. P/E forward
    valid_pes = [_get(r, "pe_forward") for r in reports if _get(r, "pe_forward") and _get(r, "pe_forward") > 0]
    avg_pe = sum(valid_pes) / len(valid_pes) if valid_pes else 0
    add_row("4. Hệ số P/E Forward", lambda r: f"{_get(r, 'pe_forward'):.1f}x" if _get(r, 'pe_forward') else "—", f"TB: {avg_pe:.1f}x" if avg_pe > 0 else "—")
    # 5. P/B forward
    valid_pbs = [_get(r, "pb_forward") for r in reports if _get(r, "pb_forward") and _get(r, "pb_forward") > 0]
    avg_pb = sum(valid_pbs) / len(valid_pbs) if valid_pbs else 0
    add_row("5. Hệ số P/B Forward", lambda r: f"{_get(r, 'pb_forward'):.2f}x" if _get(r, 'pb_forward') else "—", f"TB: {avg_pb:.2f}x" if avg_pb > 0 else "—")
    # 6. Dự phóng Doanh thu
    add_row("6. Dự phóng Doanh thu", lambda r: _get(r, "revenue_forecast", "") or "N/A", "Đồng thuận tích cực")
    # 7. Dự phóng LNST
    add_row("7. Dự phóng LNST", lambda r: _get(r, "npat_forecast", "") or "N/A", "Tăng trưởng cao", is_bold=True)
    # 8. Luận điểm tăng trưởng
    add_row("8. Luận điểm tăng trưởng (Catalysts)", lambda r: "<br>• ".join([""] + (_get(r, "key_catalysts", []) or [])), "• Dự án mở rộng công suất<br>• Tăng trưởng thị phần")
    # 9. Rủi ro trọng yếu
    add_row("9. Rủi ro trọng yếu (Key Risks)", lambda r: "<br>• ".join([""] + (_get(r, "key_risks", []) or [])), "• Biến động giá hàng hóa<br>• Rủi ro tài chính")

    html_lines.append('</table><br>')
    html_lines.append(f'<p><b>Chiến lược giải ngân:</b> {rec_buy_zone} | <b>Ngưỡng quản trị dừng lỗ:</b> {stop_loss_val}</p>')
    html_lines.append('</body></html>')

    excel_content = "\n".join(html_lines)
    filename = f"IERM_{ticker}_Matrix_Table.xls"
    return Response(
        content=excel_content,
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": make_content_disposition("attachment", filename)}
    )


