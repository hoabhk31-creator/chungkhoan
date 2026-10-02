import os
import sys
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

source_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(source_dir, "webapp_deploy.zip")

if os.path.exists(zip_path):
    try:
        os.remove(zip_path)
    except Exception as e:
        print(f"Khong the xoa zip cu: {e}")

exclude_dirs = {"__pycache__", ".git", "venv", ".idea", ".vscode", "scratch", "edocs_pdfs"}
exclude_exts = {".zip", ".log", ".png"}
exclude_files = {"test_DGC_matrix.pdf", "test_DGC_matrix_clean.pdf"}

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in exclude_exts or f in exclude_files or f.startswith("pvd_"):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, source_dir)
            zipf.write(full_path, rel_path)

size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f">>> DA DONG GOI THANH CONG: {zip_path}")
print(f">>> Dung luong: {size_mb:.2f} MB")
