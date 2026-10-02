#!/bin/bash
# =============================================================================
# KỊCH BẢN ĐỒNG BỘ & KHỞI ĐỘNG LẠI WEBAPP TRÊN VPS (ZSTOCK.PRO.VN)
# =============================================================================
set -e

APP_DIR="/var/www/webapp"
ZIP_PATH="$APP_DIR/webapp_deploy.zip"

if [ ! -f "$ZIP_PATH" ]; then
    ZIP_PATH="/root/webapp_deploy.zip"
fi

if [ -f "$ZIP_PATH" ]; then
    echo ">>> Tìm thấy $ZIP_PATH, đang tiến hành giải nén cập nhật..."
    which unzip &>/dev/null || (apt update && apt install -y unzip)
    unzip -o "$ZIP_PATH" -d "$APP_DIR"
    rm -f "$ZIP_PATH"
    echo ">>> Giải nén thành công!"
fi

cd "$APP_DIR"

# 1. Cài đặt các thư viện mới nếu có thay đổi trong requirements.txt
if [ -d "$APP_DIR/venv" ]; then
    $APP_DIR/venv/bin/pip install --upgrade pip >/dev/null 2>&1 || true
    if [ -f "requirements.txt" ]; then
        $APP_DIR/venv/bin/pip install -r requirements.txt
    fi
fi

# 2. Cấu hình tên miền zstock.pro.vn vào Nginx Reverse Proxy
NGINX_CONF="/etc/nginx/sites-available/ierm"
if [ -f "$NGINX_CONF" ]; then
    if ! grep -q "zstock.pro.vn" "$NGINX_CONF"; then
        echo ">>> Cập nhật cấu hình Nginx cho tên miền zstock.pro.vn..."
        sed -i 's/server_name _;/server_name zstock.pro.vn www.zstock.pro.vn _;/g' "$NGINX_CONF" 2>/dev/null || true
        nginx -t && systemctl reload nginx
    fi
fi

# 3. Khởi động lại dịch vụ chạy ngầm IERM
echo ">>> Đang khởi động lại dịch vụ ierm..."
systemctl daemon-reload
systemctl restart ierm
systemctl restart nginx

echo "=========================================================="
echo ">>> ĐỒNG BỘ THÀNH CÔNG 100%! <<<"
echo "Kiểm tra hoạt động tại: http://zstock.pro.vn hoặc http://103.9.78.15"
echo "Để bật HTTPS (SSL xanh miễn phí), chạy lệnh:"
echo "certbot --nginx -d zstock.pro.vn -d www.zstock.pro.vn"
echo "=========================================================="
