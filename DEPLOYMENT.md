# Deployment Guide for GateFlow Dashboard

## Prerequisites
- A VPS/Cloud Server (DigitalOcean, AWS EC2, Linode, etc.)
- Your domain pointing to the server's IP address
- SSH access to your server

## Deployment Steps

### 1. Point Your Domain to Server
Update your domain's DNS A record to point to your server's IP address:
```
Type: A
Name: @ (or your subdomain)
Value: YOUR_SERVER_IP
TTL: 3600
```

### 2. Server Setup (Ubuntu/Debian)

SSH into your server and run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 3. Deploy the Application

```bash
# Clone or upload your project to the server
cd /home/youruser/
git clone YOUR_REPO_URL frontEnd
# OR use scp/rsync to upload files

cd frontEnd

# Build and run with Docker
docker-compose up -d --build

# Check if it's running
docker-compose logs -f
```

### 4. Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/gateflow

# Update the domain name in the config
sudo nano /etc/nginx/sites-available/gateflow
# Replace 'your-domain.com' with your actual domain

# Enable the site
sudo ln -s /etc/nginx/sites-available/gateflow /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 5. Setup SSL Certificate (HTTPS)

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically configure HTTPS
# Follow the prompts and select redirect HTTP to HTTPS
```

### 6. Update Streamlit Configuration

Edit `.streamlit/config.toml` and update `serverAddress`:
```toml
[browser]
serverAddress = "your-actual-domain.com"
```

Then rebuild:
```bash
docker-compose down
docker-compose up -d --build
```

## Alternative Deployment Methods

### Option A: Direct Python Deployment (Without Docker)

```bash
# Install Python and dependencies
sudo apt install python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run with systemd service
sudo nano /etc/systemd/system/streamlit.service
```

Add to streamlit.service:
```ini
[Unit]
Description=Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/frontEnd
Environment="PATH=/home/youruser/frontEnd/venv/bin"
ExecStart=/home/youruser/frontEnd/venv/bin/streamlit run gategroupDashboard.py

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl start streamlit
sudo systemctl enable streamlit
```

### Option B: Streamlit Community Cloud (Free, Easy)

1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Sign in with GitHub
4. Deploy your app
5. Use a CNAME record to point your domain to the Streamlit URL

### Option C: Platform as a Service

**Heroku:**
- Create `Procfile`: `web: streamlit run gategroupDashboard.py --server.port=$PORT`
- Deploy via Git
- Add custom domain in Heroku settings

**Railway/Render:**
- Connect GitHub repository
- Auto-deploy
- Add custom domain in settings

## Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Update application
git pull
docker-compose up -d --build

# Check status
docker-compose ps
sudo systemctl status nginx
```

## Troubleshooting

**App not accessible:**
- Check firewall: `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`
- Check nginx: `sudo systemctl status nginx`
- Check app: `docker-compose ps`

**WebSocket errors:**
- Ensure nginx.conf has proper WebSocket configuration
- Check `_stcore/stream` location block

**Domain not working:**
- Verify DNS propagation: `nslookup your-domain.com`
- Check A record points to correct IP
- Wait up to 48 hours for DNS propagation

## Security Recommendations

1. Enable firewall and only open necessary ports
2. Use SSL/HTTPS (Let's Encrypt)
3. Keep system and packages updated
4. Use environment variables for secrets
5. Regular backups
6. Monitor server resources

## Cost Estimate

- **VPS Hosting**: $5-20/month (DigitalOcean, Linode, Vultr)
- **Domain**: $10-15/year
- **SSL Certificate**: FREE (Let's Encrypt)
- **Total**: ~$6-21/month

---

For questions or issues, refer to:
- Streamlit docs: https://docs.streamlit.io/
- Nginx docs: https://nginx.org/en/docs/
- Docker docs: https://docs.docker.com/
