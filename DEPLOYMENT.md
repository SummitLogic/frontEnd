# Deployment Guide for GateFlow Dashboard

> **Note:** This project has been restructured. All deployment files are now in the `deploy/` folder.  
> For detailed deployment instructions, see **[deploy/README.md](deploy/README.md)**

## Quick Overview

### Project Structure
```
frontEnd/
├── gategroupDashboard.py       # Main application
├── Dockerfile                  # Container definition
├── data/                       # User data (not in git)
└── deploy/                     # 🔥 All deployment configs here
    ├── README.md              # Detailed deployment guide
    ├── quick-deploy.sh        # Automated deployment script
    ├── docker-compose.yml     # Development setup
    ├── docker-compose.prod.yml # Production with nginx
    ├── .env.example           # Configuration template
    └── nginx/
        └── nginx.conf         # Reverse proxy configuration
```

### Deployment Options

1. **Docker + VPS (Recommended)**
   - See [`deploy/README.md`](deploy/README.md)
   - Full control, custom domain, SSL
   - Cost: ~$5-20/month

2. **Streamlit Community Cloud (Easiest)**
   - See [`STREAMLIT_CLOUD_DEPLOYMENT.md`](STREAMLIT_CLOUD_DEPLOYMENT.md)
   - Free tier available
   - Limited customization

3. **Quick Deploy Script**
   ```bash
   cd deploy
   ./quick-deploy.sh
   ```

## Prerequisites

For VPS deployment you need:
- A VPS/Cloud Server (DigitalOcean, AWS EC2, Linode, etc.)
- Domain name (optional but recommended)
- SSH access to server

## Quick Start

### Local Testing
```bash
# Clone the repository
git clone https://github.com/SummitLogic/frontEnd.git
cd frontEnd

# Build and run with Docker
cd deploy
docker compose up --build
```

Access at: http://localhost:8501

### Production Deployment

**Step 1: Point your domain to server**
```
DNS A Record:
Type: A
Name: @
Value: YOUR_SERVER_IP
```

**Step 2: Set up server**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone project
git clone https://github.com/SummitLogic/frontEnd.git
cd frontEnd/deploy
```

**Step 3: Deploy**
```bash
# Development mode
docker compose up -d --build

# OR Production mode (with nginx)
docker compose -f docker-compose.prod.yml up -d --build
```

**Step 4: Set up SSL**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Detailed Guides

- **Full Deployment Guide:** [`deploy/README.md`](deploy/README.md)
- **Streamlit Cloud:** [`STREAMLIT_CLOUD_DEPLOYMENT.md`](STREAMLIT_CLOUD_DEPLOYMENT.md)
- **Quick Deploy:** [`QUICK_DEPLOY.md`](QUICK_DEPLOY.md)

## Maintenance

```bash
# View logs
docker compose logs -f

# Restart
docker compose restart

# Update and rebuild
git pull
docker compose up -d --build

# Stop services
docker compose down
```

## Troubleshooting

**Container won't start:**
```bash
docker compose logs
docker ps -a
```

**Port already in use:**
```bash
# Check what's using port 8501
sudo lsof -i :8501
# Kill the process or change port in docker-compose.yml
```

**Domain not working:**
```bash
# Check DNS propagation
nslookup your-domain.com
# Verify nginx is running
sudo systemctl status nginx
```

## Security Checklist

- [ ] Change default user credentials
- [ ] Enable firewall (ports 80, 443, 22)
- [ ] Set up SSL/HTTPS
- [ ] Keep dependencies updated
- [ ] Back up `data/users.json`
- [ ] Use environment variables for secrets

## Support

- Streamlit Docs: https://docs.streamlit.io/
- Docker Docs: https://docs.docker.com/
- Nginx Docs: https://nginx.org/en/docs/

---

**For complete step-by-step instructions, go to [`deploy/README.md`](deploy/README.md)**

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
