#!/bin/bash
# GAAS SystemD Deployment Script

set -e

echo "🚀 Deploying GAAS SystemD services..."

# Configuration
SERVICE_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/dev/gaas"
LOG_DIR="/home/ubuntu/logs"

# Create log directory
sudo mkdir -p $LOG_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $LOG_DIR

# Install required packages
echo "📦 Installing required packages..."
sudo apt update
sudo apt install -y python3.11-venv python3-pip nginx certbot python3-certbot-nginx

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "🐍 Creating virtual environment..."
    cd $PROJECT_DIR
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Create SystemD service files
echo "🔧 Creating SystemD service files..."

# GAAS Main Service
sudo tee /etc/systemd/system/gaas.service > /dev/null << EOF
[Unit]
Description=GAAS - Sports Analytics Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR/src
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/src/gaas_unified.py --parallel --commit
Restart=always
RestartSec=30
StandardOutput=append:$LOG_DIR/gaas.log
StandardError=append:$LOG_DIR/gaas_error.log

# Resource limits
MemoryMax=2G
CPUQuota=50%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$PROJECT_DIR/data $PROJECT_DIR/results $PROJECT_DIR/logs

[Install]
WantedBy=multi-user.target
EOF

# GAAS Web Service
sudo tee /etc/systemd/system/gaas-web.service > /dev/null << EOF
[Unit]
Description=GAAS Web Interface
After=network.target gaas.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR/src
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/gaas_web.log
StandardError=append:$LOG_DIR/gaas_web_error.log

# Resource limits
MemoryMax=512M
CPUQuota=20%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$PROJECT_DIR/results

[Install]
WantedBy=multi-user.target
EOF

# Create log rotation
sudo tee /etc/logrotate.d/gaas > /dev/null << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        systemctl reload gaas gaas-web || true
    endscript
}
EOF

# Create nginx configuration
sudo tee /etc/nginx/sites-available/gaas > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS for production
    # return 301 https://\$server_name\$request_uri;

    # For now, serve HTTP directly
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Static files caching
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}

# Rate limiting
http {
    limit_req_zone \$binary_remote_addr zone=api:10m rate=5r/s;
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/gaas /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Create monitoring script
sudo tee /usr/local/bin/gaas-monitor > /dev/null << 'EOF'
#!/bin/bash
# GAAS monitoring script

LOG_FILE="/home/ubuntu/logs/gaas_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if services are running
if ! systemctl is-active --quiet gaas; then
    echo "$DATE: GAAS service is not running" >> $LOG_FILE
    systemctl restart gaas
fi

if ! systemctl is-active --quiet gaas-web; then
    echo "$DATE: GAAS web service is not running" >> $LOG_FILE
    systemctl restart gaas-web
fi

# Check disk space
DISK_USAGE=$(df /home/ubuntu | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 85 ]; then
    echo "$DATE: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi

# Check if web interface is responding
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "$DATE: Web interface not responding" >> $LOG_FILE
    systemctl restart gaas-web
fi
EOF

sudo chmod +x /usr/local/bin/gaas-monitor

# Create cron job for monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/gaas-monitor") | crontab -

# Create backup script
sudo tee /usr/local/bin/gaas-backup > /dev/null << 'EOF'
#!/bin/bash
# GAAS backup script

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date '+%Y%m%d_%H%M%S')
PROJECT_DIR="/home/ubuntu/dev/gaas"

mkdir -p $BACKUP_DIR

# Backup results and databases
tar -czf "$BACKUP_DIR/gaas_backup_$DATE.tar.gz" \
    -C $PROJECT_DIR \
    results/ data/ logs/ --exclude='*.pyc'

# Keep only last 7 days of backups
find $BACKUP_DIR -name "gaas_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: gaas_backup_$DATE.tar.gz"
EOF

sudo chmod +x /usr/local/bin/gaas-backup

# Create cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/gaas-backup") | crontab -

# Reload systemd and start services
echo "🔄 Reloading SystemD and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable gaas gaas-web
sudo systemctl restart nginx

# Start services
sudo systemctl start gaas gaas-web

# Wait a moment and check status
sleep 5

echo "📊 Service status:"
echo "GAAS Service: $(systemctl is-active gaas)"
echo "GAAS Web Service: $(systemctl is-active gaas-web)"
echo "Nginx: $(systemctl is-active nginx)"

# Show recent logs
echo ""
echo "📋 Recent GAAS logs:"
tail -5 $LOG_DIR/gaas.log 2>/dev/null || echo "No logs yet"

echo ""
echo "🎉 GAAS deployment complete!"
echo ""
echo "Web interface: http://localhost"
echo "API endpoint: http://localhost/api/"
echo "Health check: http://localhost/health"
echo ""
echo "Monitor with: sudo journalctl -u gaas -f"
echo "Monitor web with: sudo journalctl -u gaas-web -f"
echo "View logs: tail -f $LOG_DIR/gaas.log"
EOF
