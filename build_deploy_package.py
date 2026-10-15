"""
Script đóng gói toàn diện mã nguồn webapp thành gói triển khai chuẩn (webapp_deploy.zip).
Bảo toàn đầy đủ:
- Bộ code mới nhất (server, crawler, gemini_extractor, knowledge_backup_manager,...)
- Thư mục data (tri thức đã học, templates, database cổ phiếu)
- Thư mục backups (chứa các bản snapshot tự khôi phục khi deploy)
- Toàn bộ static (giao diện HTML, app.js mới nhất)
- Kịch bản chạy trên VPS (deploy_update.sh, setup_vps.sh) và chạy local (run.py, start.bat)
"""

import os
import sys
import shutil
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

source_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(source_dir)
zip_path_in_webapp = os.path.join(source_dir, "webapp_deploy.zip")
zip_path_in_parent = os.path.join(parent_dir, "webapp_deploy.zip")

print(">>> [1/4] Đang chuẩn bị kịch bản triển khai VPS vào thư mục webapp...")

# Copy hoặc đảm bảo có deploy_update.sh và setup_vps.sh
deploy_dir_ref = os.path.join(parent_dir, "webapp_deploy")
for script_name in ["deploy_update.sh", "setup_vps.sh"]:
    dst = os.path.join(source_dir, script_name)
    src = os.path.join(deploy_dir_ref, script_name)
    if os.path.exists(src) and not os.path.exists(dst):
        try:
            shutil.copy2(src, dst)
            print(f"  + Đã bổ sung {script_name}")
        except Exception:
            pass

print(">>> [2/4] Đang quét và đóng gói các tệp tin...")

# Danh sách loại trừ để gói zip gọn nhẹ & sạch sẽ
exclude_dirs = {
    "__pycache__", ".git", "venv", ".idea", ".vscode", "scratch", 
    "edocs_pdfs", "tests", "tmp"
}
exclude_exts = {".log", ".tmp", ".pyc"}
exclude_filenames = {
    "webapp_deploy.zip", "test_DGC_matrix.pdf", "test_DGC_matrix_clean.pdf",
    "visitor_stats.json"
}

# Xóa gói cũ nếu có
for zp in [zip_path_in_webapp, zip_path_in_parent]:
    if os.path.exists(zp):
        try:
            os.remove(zp)
        except Exception as e:
            print(f"  ! Không thể xóa {zp}: {e}")

packaged_count = 0
total_uncompressed_bytes = 0

with zipfile.ZipFile(zip_path_in_webapp, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in exclude_exts or f in exclude_filenames:
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, source_dir)

            try:
                zipf.write(full_path, rel_path)
                packaged_count += 1
                total_uncompressed_bytes += os.path.getsize(full_path)
            except Exception as e:
                print(f"  ! Lỗi nén file {rel_path}: {e}")

print(">>> [3/4] Đồng bộ gói sang thư mục gốc dự án E:\\Anti\\...")
try:
    shutil.copy2(zip_path_in_webapp, zip_path_in_parent)
    print(f"  + Đã đồng bộ sang {zip_path_in_parent}")
except Exception as e:
    print(f"  ! Không thể sao chép sang thư mục cha: {e}")

# Đồng bộ luôn sang thư mục E:\Anti\webapp_deploy để người dùng có thể dùng thư mục đó nếu muốn
if os.path.exists(deploy_dir_ref):
    try:
        shutil.copy2(zip_path_in_webapp, os.path.join(deploy_dir_ref, "webapp_deploy.zip"))
        print(f"  + Đã đồng bộ sang {os.path.join(deploy_dir_ref, 'webapp_deploy.zip')}")
    except Exception:
        pass

size_mb = os.path.getsize(zip_path_in_webapp) / (1024 * 1024)
raw_mb = total_uncompressed_bytes / (1024 * 1024)

print(">>> [4/4] KẾT QUẢ ĐÓNG GÓI TRIỂN KHAI:")
print(f"  - Tổng số tệp tin đã đóng gói: {packaged_count} files")
print(f"  - Dung lượng gốc: {raw_mb:.2f} MB")
print(f"  - Dung lượng nén (.zip): {size_mb:.2f} MB")
print(f"  - Vị trí tệp triển khai: {zip_path_in_webapp}")
print(">>> HOÀN TẤT ĐÓNG GÓI!")
