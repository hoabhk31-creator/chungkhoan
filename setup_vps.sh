#!/bin/bash
# =============================================================================
# KỊCH BẢN TỰ ĐỘNG CÀI ĐẶT & TRIỂN KHAI IERM TERMINAL LÊN VPS UBUNTU (22.04 / 24.04)
# =============================================================================

set -e

echo "=========================================================="
echo ">>> [1/6] Cập nhật hệ thống & kích hoạt 2GB Swap RAM..."
echo "=========================================================="
apt update && apt upgrade -y

# Kiểm tra và tạo 2GB Swap RAM nếu chưa có (chống sập khi bóc tách PDF)
if ! grep -q "swapfile" /etc/fstab; then
    echo ">>> Đang thiết lập 2GB RAM ảo (Swap)..."
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    echo ">>> Kích hoạt 2GB Swap RAM thành công!"
fi

echo "=========================================================="
echo ">>> [2/6] Cài đặt Python 3, Nginx và các công cụ cần thiết..."
echo "=========================================================="
# Kiểm tra và cài đặt Python >= 3.8 (ưu tiên Python 3.10 hoặc 3.11)
apt install -y python3 python3-pip python3-venv nginx curl git ufw certbot python3-certbot-nginx

# Kiểm tra nếu python3 hiện tại < 3.8 thì bổ sung deadsnakes PPA (Ubuntu)
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo 0)
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 0)

PY_CMD="python3"
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
    echo ">>> Phát hiện Python hiện tại ($PY_MAJOR.$PY_MINOR) quá cũ (< 3.8). Đang tiến hành cài đặt Python 3.10/3.11..."
    apt install -y software-properties-common
    add-apt-repository ppa:deadsnakes/ppa -y || true
    apt update
    apt install -y python3.11 python3.11-venv python3.11-dev || apt install -y python3.10 python3.10-venv python3.10-dev
    if command -v python3.11 &> /dev/null; then
        PY_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PY_CMD="python3.10"
    fi
fi

# Tạo thư mục chạy ứng dụng nếu chưa có
mkdir -p /var/www/webapp
cd /var/www/webapp

echo "=========================================================="
echo ">>> [3/6] Cài đặt môi trường Python ảo (Virtualenv)..."
echo "=========================================================="
# Nếu venv cũ được tạo bởi python cũ (< 3.8), xoá đi tạo lại
if [ -d "venv" ]; then
    VENV_PY_VER=$(venv/bin/python -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 0)
    if [ "$VENV_PY_VER" -lt 8 ]; then
        echo ">>> Xoá môi trường venv cũ (Python 3.$VENV_PY_VER)..."
        rm -rf venv
    fi
fi

if [ ! -d "venv" ]; then
    $PY_CMD -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn httpx beautifulsoup4 fpdf2 pypdf pydantic requests python-multipart
fi

echo "=========================================================="
echo ">>> [4/6] Cấu hình Dịch vụ chạy ngầm 24/7 (Systemd)..."
echo "=========================================================="
cat << 'EOF' > /etc/systemd/system/ierm.service
[Unit]
Description=IERM Financial Terminal FastAPI Service
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/webapp
ExecStart=/var/www/webapp/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ierm
systemctl restart ierm

echo "=========================================================="
echo ">>> [5/6] Cấu hình Máy chủ Web Nginx Reverse Proxy..."
echo "=========================================================="
cat << 'EOF' > /etc/nginx/sites-available/ierm
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 50M;

    # Gzip nén dữ liệu tăng tốc độ tải trang
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
EOF

# Kích hoạt site Nginx
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/ierm /etc/nginx/sites-enabled/ierm
nginx -t
systemctl restart nginx

echo "=========================================================="
echo ">>> [6/6] Mở tường lửa UFW (Port 22, 80, 443)..."
echo "=========================================================="
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "=========================================================="
echo ">>> HOÀN TẤT CÀI ĐẶT 100%! <<<"
echo "Bạn có thể mở trình duyệt và gõ trực tiếp địa chỉ IP của VPS để kiểm tra."
echo "Để gắn tên miền và bật bảo mật SSL (HTTPS), chạy lệnh:"
echo "certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo "=========================================================="
