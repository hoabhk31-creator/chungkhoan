"""
Hệ thống sao lưu, bảo tồn và khôi phục dữ liệu AI Tự Học (AI Learned Knowledge Backup & Restore).
Giúp bảo toàn 100% dữ liệu đã học khi triển khai (deploy) bản webapp mới hoặc nâng cấp code.
"""

import os
import sys
import glob
import json
import time
import shutil
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(ROOT_DIR, "data")
BACKUP_DIR = os.environ.get("BACKUP_DIR") or os.path.join(ROOT_DIR, "backups")
IMAGES_DIR = os.path.join(DATA_DIR, "learned_images")

# Danh sách các tệp tin tri thức cốt lõi của AI Tự Học & Bóc tách phân tích
CORE_KNOWLEDGE_FILES = [
    "ai_learned_catalysts.json",
    "ai_learning_templates.json",
    "ai_learning_history.json",
    "ai_learning_config.json",
    "ai_seen_reports.json",
    "ai_analyst_styles.json",
    "pdf_catalysts_cache.json",
    "discovered_projects_cache.json"
]


def ensure_backup_dir():
    """Tạo thư mục lưu trữ backup nếu chưa có."""
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
        except Exception as e:
            print(f"[Backup] Không thể tạo thư mục backup {BACKUP_DIR}: {e}")


def create_knowledge_backup(tag: str = "auto") -> Dict[str, Any]:
    """
    Tạo gói backup nén .zip chứa toàn bộ tri thức AI đã học, các templates,
    và thư mục ảnh mẫu huấn luyện (nếu có).
    """
    ensure_backup_dir()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_tag = "".join(c for c in tag if c.isalnum() or c in ("-", "_")) or "manual"
    zip_filename = f"ai_knowledge_backup_{timestamp_str}_{clean_tag}.zip"
    zip_filepath = os.path.join(BACKUP_DIR, zip_filename)

    included_files = []
    total_catalysts = 0
    total_templates = 0
    total_reports = 0

    try:
        with zipfile.ZipFile(zip_filepath, "w", compression=zipfile.ZIP_DEFLATED) as zip_out:
            # 1. Nén các file JSON tri thức cốt lõi
            for fname in CORE_KNOWLEDGE_FILES:
                src_path = os.path.join(DATA_DIR, fname)
                if os.path.exists(src_path):
                    zip_out.write(src_path, arcname=fname)
                    included_files.append(fname)
                    
                    # Thu thập thống kê nhanh
                    try:
                        if fname == "ai_learned_catalysts.json":
                            with open(src_path, "r", encoding="utf-8") as f:
                                d = json.load(f)
                                total_catalysts = sum(len(v.get("catalysts", [])) for v in d.values() if isinstance(v, dict))
                                total_tickers = len(d)
                        elif fname == "ai_learning_config.json":
                            with open(src_path, "r", encoding="utf-8") as f:
                                cfg = json.load(f)
                                lifetime_reports = cfg.get("lifetime_reports_learned", 0)
                                lifetime_catalysts = cfg.get("lifetime_catalysts_accumulated", 0)
                        elif fname == "ai_learning_templates.json":
                            with open(src_path, "r", encoding="utf-8") as f:
                                d = json.load(f)
                                total_templates = len(d) if isinstance(d, list) else 0
                        elif fname == "ai_learning_history.json":
                            with open(src_path, "r", encoding="utf-8") as f:
                                d = json.load(f)
                                total_reports = len(d) if isinstance(d, list) else 0
                    except Exception:
                        pass

            # 2. Nén thư mục ảnh huấn luyện learned_images (nếu có)
            if os.path.exists(IMAGES_DIR) and os.path.isdir(IMAGES_DIR):
                for img_file in glob.glob(os.path.join(IMAGES_DIR, "*")):
                    if os.path.isfile(img_file):
                        arc_name = os.path.join("learned_images", os.path.basename(img_file))
                        zip_out.write(img_file, arcname=arc_name)
                        included_files.append(arc_name)

            # 3. Ghi file manifest.json metadata vào gói zip
            manifest = {
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tag": clean_tag,
                "included_files_count": len(included_files),
                "stats": {
                    "total_catalysts": total_catalysts,
                    "total_tickers": total_tickers,
                    "total_templates": total_templates,
                    "total_reports": total_reports,
                    "lifetime_reports": lifetime_reports or total_reports,
                    "lifetime_catalysts": lifetime_catalysts or total_catalysts
                },
                "version": "2.0"
            }
            zip_out.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        file_size_bytes = os.path.getsize(zip_filepath)
        
        # Đồng thời cập nhật hoặc tạo file latest_backup.zip để tự động khôi phục khi deploy
        latest_path = os.path.join(BACKUP_DIR, "latest_backup.zip")
        try:
            shutil.copy2(zip_filepath, latest_path)
        except Exception:
            pass

        # Dọn dẹp chỉ giữ tối đa 15 bản backup gần nhất
        cleanup_old_backups(max_keep=15)

        return {
            "success": True,
            "filename": zip_filename,
            "filepath": zip_filepath,
            "size_bytes": file_size_bytes,
            "size_kb": round(file_size_bytes / 1024, 2),
            "created_at": manifest["created_at"],
            "stats": manifest["stats"]
        }
    except Exception as e:
        print(f"[Backup] Lỗi tạo backup: {e}")
        return {"success": False, "error": str(e)}


def cleanup_old_backups(max_keep: int = 15):
    """Giữ lại số lượng bản backup gần nhất, xóa bớt bản cũ để tiết kiệm dung lượng."""
    try:
        ensure_backup_dir()
        backups = list_all_backups()
        if len(backups) > max_keep:
            for old in backups[max_keep:]:
                fpath = os.path.join(BACKUP_DIR, old["filename"])
                if os.path.exists(fpath):
                    os.remove(fpath)
    except Exception as e:
        print(f"[Backup] Lỗi dọn dẹp backup cũ: {e}")


def list_all_backups() -> List[Dict[str, Any]]:
    """Liệt kê toàn bộ các file backup hiện có trong thư mục backups."""
    ensure_backup_dir()
    result = []
    pattern = os.path.join(BACKUP_DIR, "ai_knowledge_backup_*.zip")
    for fpath in glob.glob(pattern):
        try:
            fname = os.path.basename(fpath)
            stat = os.stat(fpath)
            created_dt = datetime.fromtimestamp(stat.st_mtime)
            
            # Đọc manifest nếu có
            manifest_info = {}
            try:
                with zipfile.ZipFile(fpath, "r") as zf:
                    if "manifest.json" in zf.namelist():
                        manifest_info = json.loads(zf.read("manifest.json").decode("utf-8"))
            except Exception:
                pass

            result.append({
                "filename": fname,
                "filepath": fpath,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "created_at": created_dt.strftime("%d/%m/%Y %H:%M:%S"),
                "timestamp": stat.st_mtime,
                "stats": manifest_info.get("stats", {})
            })
        except Exception:
            pass

    # Sắp xếp mới nhất lên đầu
    result.sort(key=lambda x: x["timestamp"], reverse=True)
    return result


def restore_knowledge_from_zip(zip_filepath: str, merge: bool = True) -> Dict[str, Any]:
    """
    Khôi phục tri thức AI từ file zip đã sao lưu.
    - merge=True: Giữ nguyên dữ liệu hiện tại và hợp nhất bổ sung thêm từ backup (khuyên dùng).
    - merge=False: Ghi đè thay thế hoàn toàn bằng file backup.
    """
    if not os.path.exists(zip_filepath):
        return {"success": False, "error": f"Không tìm thấy file backup {zip_filepath}"}

    restored_files = []
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_filepath, "r") as zf:
            file_names = zf.namelist()
            
            for item in file_names:
                if item == "manifest.json":
                    continue
                
                # Khôi phục file ảnh
                if item.startswith("learned_images/") or item.startswith("learned_images\\"):
                    target_img = os.path.join(DATA_DIR, item)
                    os.makedirs(os.path.dirname(target_img), exist_ok=True)
                    with open(target_img, "wb") as f_out:
                        f_out.write(zf.read(item))
                    restored_files.append(item)
                    continue

                # Khôi phục file JSON
                if item in CORE_KNOWLEDGE_FILES:
                    content_bytes = zf.read(item)
                    target_file = os.path.join(DATA_DIR, item)

                    if not merge or not os.path.exists(target_file):
                        # Ghi đè hoặc file đích chưa tồn tại
                        with open(target_file, "wb") as f_out:
                            f_out.write(content_bytes)
                        restored_files.append(item)
                    else:
                        # MERGE THÔNG MINH: Kết hợp dữ liệu cũ & mới
                        try:
                            backup_data = json.loads(content_bytes.decode("utf-8"))
                            with open(target_file, "r", encoding="utf-8") as f_curr:
                                curr_data = json.load(f_curr)

                            if item == "ai_learned_catalysts.json":
                                # Hợp nhất từng mã cổ phiếu
                                if isinstance(curr_data, dict) and isinstance(backup_data, dict):
                                    for tkr, b_entry in backup_data.items():
                                        if tkr not in curr_data:
                                            curr_data[tkr] = b_entry
                                        else:
                                            # Hợp nhất catalysts & risks
                                            c_cats = curr_data[tkr].get("catalysts", [])
                                            b_cats = b_entry.get("catalysts", [])
                                            for c in b_cats:
                                                if c and c not in c_cats:
                                                    c_cats.append(c)
                                            curr_data[tkr]["catalysts"] = c_cats[:15]

                                            c_risks = curr_data[tkr].get("risks", [])
                                            b_risks = b_entry.get("risks", [])
                                            for r in b_risks:
                                                if r and r not in c_risks:
                                                    c_risks.append(r)
                                            curr_data[tkr]["risks"] = c_risks[:10]

                                            # Hợp nhất history
                                            c_hist = curr_data[tkr].get("history", [])
                                            b_hist = b_entry.get("history", [])
                                            curr_data[tkr]["history"] = (c_hist + b_hist)[:25]
                                    
                                    with open(target_file, "w", encoding="utf-8") as f_out:
                                        json.dump(curr_data, f_out, ensure_ascii=False, indent=2)
                                    restored_files.append(f"{item} (merged)")

                            elif item == "ai_learning_templates.json":
                                # Hợp nhất templates
                                if isinstance(curr_data, list) and isinstance(backup_data, list):
                                    existing_ids = {t.get("id") for t in curr_data if isinstance(t, dict)}
                                    for tpl in backup_data:
                                        if isinstance(tpl, dict) and tpl.get("id") not in existing_ids:
                                            curr_data.append(tpl)
                                    with open(target_file, "w", encoding="utf-8") as f_out:
                                        json.dump(curr_data, f_out, ensure_ascii=False, indent=2)
                                    restored_files.append(f"{item} (merged)")

                            elif item == "ai_learning_history.json":
                                if isinstance(curr_data, list) and isinstance(backup_data, list):
                                    seen_keys = {f"{h.get('ticker')}_{h.get('title')}" for h in curr_data if isinstance(h, dict)}
                                    for h in backup_data:
                                        if isinstance(h, dict) and f"{h.get('ticker')}_{h.get('title')}" not in seen_keys:
                                            curr_data.append(h)
                                    curr_data = curr_data[:100]  # Giữ 100 log mới nhất
                                    with open(target_file, "w", encoding="utf-8") as f_out:
                                        json.dump(curr_data, f_out, ensure_ascii=False, indent=2)
                                    restored_files.append(f"{item} (merged)")

                            elif item == "pdf_catalysts_cache.json":
                                if isinstance(curr_data, dict) and isinstance(backup_data, dict):
                                    curr_data.update(backup_data)
                                    with open(target_file, "w", encoding="utf-8") as f_out:
                                        json.dump(curr_data, f_out, ensure_ascii=False, indent=2)
                                    restored_files.append(f"{item} (merged)")
                            else:
                                # Các file khác chỉ ghi đè nếu file hiện tại rỗng
                                if not curr_data:
                                    with open(target_file, "wb") as f_out:
                                        f_out.write(content_bytes)
                                    restored_files.append(item)
                        except Exception as parse_e:
                            print(f"[Backup] Lỗi merge {item}: {parse_e}, fallback ghi file")
                            with open(target_file, "wb") as f_out:
                                f_out.write(content_bytes)
                            restored_files.append(item)

        return {
            "success": True,
            "restored_files": restored_files,
            "message": f"Đã khôi phục thành công {len(restored_files)} tệp tin tri thức"
        }
    except Exception as e:
        print(f"[Backup] Lỗi khôi phục backup: {e}")
        return {"success": False, "error": str(e)}


def auto_protect_on_startup():
    """
    Tự động chạy khi server khởi động:
    1. Kiểm tra nếu thư mục data bị trống hoặc thiếu tri thức (do vừa deploy phiên bản code mới):
       Tự động tìm kiếm bản backup gần nhất trong backups/ hoặc latest_backup.zip để khôi phục ngay lập tức!
    2. Nếu dữ liệu đang đầy đủ: Tự động chụp 1 bản backup bảo vệ dữ liệu hiện có.
    """
    try:
        ensure_backup_dir()
        catalysts_file = os.path.join(DATA_DIR, "ai_learned_catalysts.json")
        is_empty = False

        if not os.path.exists(catalysts_file) or os.path.getsize(catalysts_file) < 50:
            is_empty = True
        else:
            try:
                with open(catalysts_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if not content or len(content) == 0:
                        is_empty = True
            except Exception:
                is_empty = True

        if is_empty:
            print("[Auto-Restore] Phát hiện kho tri thức AI trống (có thể vừa deploy phiên bản mới). Đang tìm bản backup để tự động khôi phục...")
            latest_zip = os.path.join(BACKUP_DIR, "latest_backup.zip")
            backups = list_all_backups()
            target_zip = None

            if os.path.exists(latest_zip) and os.path.getsize(latest_zip) > 100:
                target_zip = latest_zip
            elif backups:
                target_zip = backups[0]["filepath"]

            if target_zip:
                res = restore_knowledge_from_zip(target_zip, merge=False)
                print(f"[Auto-Restore] Kết quả tự động khôi phục: {res}")
            else:
                print("[Auto-Restore] Chưa có bản backup nào trong thư mục backups. Sẵn sàng tích lũy tri thức mới.")
        else:
            # Dữ liệu đang có sẵn: Tự động tạo 1 bản backup dự phòng
            # Chỉ tạo nếu bản backup gần nhất đã quá 6 tiếng
            backups = list_all_backups()
            should_create = True
            if backups:
                latest_ts = backups[0]["timestamp"]
                if time.time() - latest_ts < 21600:  # 6 tiếng
                    should_create = False

            if should_create:
                res = create_knowledge_backup(tag="startup")
                print(f"[Auto-Backup] Đã tạo bản sao lưu tri thức dự phòng khi khởi động: {res.get('filename')}")
    except Exception as e:
        print(f"[Auto-Protect] Ngoại lệ bảo vệ dữ liệu khởi động: {e}")
