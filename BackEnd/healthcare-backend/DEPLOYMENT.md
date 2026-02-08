# Deployment Guide

Production deployment guide for Universal Healthcare Backend.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- PostgreSQL 14+
- Python 3.10+
- Nginx (for reverse proxy)
- SSL certificate (Let's Encrypt recommended)
- Domain name

## 1. Server Setup

### Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Python 3.10+

```bash
sudo apt install python3.10 python3.10-venv python3-pip -y
```

### Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Install Nginx

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 2. Database Setup

### Create Database and User

```bash
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE healthcare_db;

-- Create user
CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;

-- Enable extensions
\c healthcare_db
CREATE EXTENSION IF NOT EXISTS timescaledb;

\q
```

### Configure PostgreSQL for Remote Access (if needed)

Edit `/etc/postgresql/14/main/postgresql.conf`:
```
listen_addresses = 'localhost'
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 3. Application Deployment

### Create Application User

```bash
sudo useradd -m -s /bin/bash healthcare
sudo su - healthcare
```

### Clone/Upload Application

```bash
mkdir -p /home/healthcare/app
cd /home/healthcare/app
# Upload your application files here
```

### Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment

```bash
nano .env
```

**Production .env**:
```env
# Database
DATABASE_URL=postgresql://healthcare_user:your_secure_password@localhost:5432/healthcare_db

# JWT
SECRET_KEY=your_generated_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_API=60/minute

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Emergency
EMERGENCY_ACCESS_DURATION_HOURS=2

# Retention
AUDIT_LOG_RETENTION_DAYS=2555
VITAL_DATA_RETENTION_DAYS=3650
ALERT_RETENTION_DAYS=365

# Encryption
ENCRYPTION_KEY=your_generated_encryption_key_32_bytes
```

**Generate Secure Keys**:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

### Test Application

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
# Test at http://your-server-ip:8000/health
# Press Ctrl+C to stop
```

## 4. Systemd Service Setup

Create service file:

```bash
sudo nano /etc/systemd/system/healthcare-backend.service
```

**Service Configuration**:
```ini
[Unit]
Description=Universal Healthcare Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=healthcare
Group=healthcare
WorkingDirectory=/home/healthcare/app
Environment="PATH=/home/healthcare/app/venv/bin"
ExecStart=/home/healthcare/app/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable healthcare-backend
sudo systemctl start healthcare-backend
sudo systemctl status healthcare-backend
```

### Check Logs

```bash
sudo journalctl -u healthcare-backend -f
```

## 5. Nginx Configuration

### Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/healthcare-backend
```

**Nginx Configuration**:
```nginx
upstream healthcare_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/healthcare-backend-access.log;
    error_log /var/log/nginx/healthcare-backend-error.log;

    # Client body size (for file uploads)
    client_max_body_size 10M;

    # Proxy Settings
    location / {
        proxy_pass http://healthcare_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/healthcare-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain Certificate

```bash
sudo certbot --nginx -d api.yourdomain.com
```

### Auto-renewal

Certbot automatically sets up renewal. Test it:
```bash
sudo certbot renew --dry-run
```

## 7. Firewall Configuration

```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
sudo ufw status
```

## 8. Database Backups

### Create Backup Script

```bash
sudo nano /home/healthcare/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/healthcare/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/healthcare_db_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

pg_dump -U healthcare_user healthcare_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Make Executable

```bash
chmod +x /home/healthcare/backup.sh
```

### Schedule Daily Backups

```bash
crontab -e
```

Add:
```
0 2 * * * /home/healthcare/backup.sh >> /home/healthcare/backup.log 2>&1
```

## 9. Monitoring Setup

### Install Monitoring Tools

```bash
sudo apt install htop iotop iftop -y
```

### Application Monitoring

Monitor service:
```bash
sudo systemctl status healthcare-backend
sudo journalctl -u healthcare-backend -f
```

Monitor processes:
```bash
htop
```

Monitor logs:
```bash
tail -f /var/log/nginx/healthcare-backend-access.log
tail -f /var/log/nginx/healthcare-backend-error.log
```

## 10. Security Hardening

### SSH Hardening

Edit `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Restart SSH:
```bash
sudo systemctl restart ssh
```

### Fail2Ban

Install:
```bash
sudo apt install fail2ban -y
```

Configure:
```bash
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

Start:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Database Security

Set strong passwords:
```bash
sudo -u postgres psql
ALTER USER healthcare_user WITH PASSWORD 'new_very_strong_password';
\q
```

Update `.env` with new password.

## 11. Performance Tuning

### PostgreSQL

Edit `/etc/postgresql/14/main/postgresql.conf`:

```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Uvicorn Workers

Adjust workers in systemd service based on CPU cores:
```
--workers 4  # For 4-core server
```

## 12. Testing Production Deployment

### Health Check

```bash
curl https://api.yourdomain.com/health
```

### API Test

```bash
curl -X POST https://api.yourdomain.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123!","role":"doctor"}'
```

## 13. Maintenance

### Update Application

```bash
sudo su - healthcare
cd /home/healthcare/app
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart healthcare-backend
```

### View Logs

```bash
sudo journalctl -u healthcare-backend -n 100
sudo tail -f /var/log/nginx/healthcare-backend-error.log
```

### Database Maintenance

```bash
sudo -u postgres psql healthcare_db
VACUUM ANALYZE;
REINDEX DATABASE healthcare_db;
```

## 14. Disaster Recovery

### Restore from Backup

```bash
gunzip /home/healthcare/backups/healthcare_db_YYYYMMDD_HHMMSS.sql.gz
psql -U healthcare_user healthcare_db < /home/healthcare/backups/healthcare_db_YYYYMMDD_HHMMSS.sql
```

### Complete Rebuild

1. Deploy fresh server
2. Install all dependencies
3. Restore database from backup
4. Copy .env file
5. Deploy application
6. Test thoroughly

## Production Checklist

- [ ] PostgreSQL installed and secured
- [ ] Application deployed
- [ ] Environment variables configured (production values)
- [ ] SSL certificate installed
- [ ] Nginx configured and running
- [ ] Systemd service enabled
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring set up
- [ ] SSH hardened
- [ ] Fail2Ban installed
- [ ] API endpoints tested
- [ ] Documentation updated
- [ ] Team trained on deployment

## Support

For issues:
1. Check logs: `sudo journalctl -u healthcare-backend -f`
2. Check Nginx logs: `/var/log/nginx/`
3. Check database connectivity
4. Verify environment variables
5. Test with curl

---

**🎉 Deployment Complete!**

Your Universal Healthcare Backend is now live and secure.
