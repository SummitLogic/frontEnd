# Quick Deployment Guide for smart-gate.tech# Quick Deployment Guide for smart-gate.tech



> **⚡ FASTEST WAY:** Use the automated script  > **⚡ FASTEST WAY:** Use the automated script in `deploy/quick-deploy.sh`

> ```bash

> cd deploy## 🚀 Super Quick Start

> chmod +x quick-deploy.sh

> ./quick-deploy.sh```bash

> ```cd deploy

chmod +x quick-deploy.sh

## 🚀 Three Deployment Options./quick-deploy.sh

# Choose option 1 for development, option 2 for production

### Option 1: Docker on VPS (Recommended - Full Control)```



**Best for:** Production use, custom domain with SSL, full control  ## Step-by-Step Deployment Instructions

**Cost:** ~$5-20/month  

**Time:** 15-30 minutes### Option 1: Deploy with Docker (Recommended)



#### Quick Steps:#### Prerequisites:

- Docker installed on your machine/server

1. **Set up DNS** (at your domain registrar):- Domain DNS configured (A record pointing to your server IP)

   ```

   Type: A#### Quick Commands:

   Name: @

   Value: YOUR_SERVER_IP**Local Testing:**

   ``````bash

cd frontEnd/deploy

2. **Prepare server:**docker compose up --build

   ```bash# Access at http://localhost:8501

   # Install Docker```

   curl -fsSL https://get.docker.com -o get-docker.sh

   sudo sh get-docker.sh**Production with Nginx:**

   ```bash

   # Clone repositorycd frontEnd/deploy

   git clone https://github.com/SummitLogic/frontEnd.gitdocker compose -f docker-compose.prod.yml up -d --build

   cd frontEnd/deploy```

   ```

---

3. **Deploy:**

   ```bash### Option 2: Deploy on VPS (Full Control)

   # Development mode

   docker compose up -d --build#### Prerequisites:

   - A VPS/Cloud Server (DigitalOcean, AWS EC2, Linode, Vultr, etc.)

   # OR Production with nginx- SSH access to your server

   docker compose -f docker-compose.prod.yml up -d --build- Domain: smart-gate.tech pointing to server IP

   ```

#### Step 1: Configure DNS

4. **Set up SSL:**

   ```bashAdd these DNS records at your domain registrar:

   sudo apt install certbot python3-certbot-nginx -y

   sudo certbot --nginx -d smart-gate.tech -d www.smart-gate.tech```

   ```Type: A

Name: @

**Done!** Access at https://smart-gate.techValue: YOUR_SERVER_IP

TTL: 3600

---

Type: A  

### Option 2: Streamlit Community Cloud (Easiest - FREE)Name: www

Value: YOUR_SERVER_IP

**Best for:** Quick testing, no server management  TTL: 3600

**Cost:** FREE  ```

**Time:** 5-10 minutes

**DNS propagation:** 15-30 minutes (up to 48 hours)

#### Steps:

#### Step 2: Server Setup

1. **Push to GitHub:**

   ```bash```bash

   cd /home/soni/hackmty25/frontEnd# SSH into server

   git add .ssh root@YOUR_SERVER_IP

   git commit -m "Deploy to Streamlit Cloud"

   git push origin main# Install Docker

   ```curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

2. **Deploy:**sudo usermod -aG docker $USER

   - Go to https://share.streamlit.io/

   - Sign in with GitHub# Install other tools

   - Click "New app"sudo apt update && sudo apt install -y git nginx certbot python3-certbot-nginx

   - Select repository: `SummitLogic/frontEnd`

   - Main file: `gategroupDashboard.py`# Logout and login again for Docker permissions

   - Deploy!exit

ssh root@YOUR_SERVER_IP

3. **Custom domain (optional):**```

   - Add CNAME record in DNS:

     ```#### Step 3: Deploy Application

     Type: CNAME

     Name: www```bash

     Value: your-app.streamlit.app# Clone repository

     ```git clone https://github.com/SummitLogic/frontEnd.git

cd frontEnd/deploy

**See full guide:** [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

# Deploy with production setup

---docker compose -f docker-compose.prod.yml up -d --build



### Option 3: Railway/Render (Easy + Affordable)# Check logs

docker compose logs -f

**Best for:** Automated deployment, easy scaling  ```

**Cost:** $5-7/month (FREE tier available)  

**Time:** 10-15 minutes#### Step 4: Set up SSL (HTTPS)



#### Railway:```bash

# Get SSL certificate

1. Push code to GitHub (same as Option 2)sudo certbot --nginx -d smart-gate.tech -d www.smart-gate.tech

2. Go to https://railway.app/

3. "New Project" → "Deploy from GitHub"# Certificates auto-renew, but test it:

4. Select repositorysudo certbot renew --dry-run

5. Add custom domain in settings```



#### Render:---



1. Go to https://render.com/### Option 3: Streamlit Community Cloud (Easiest - No Server Needed)

2. "New" → "Web Service"

3. Connect GitHub repository# Enable the site

4. Render auto-detects Dockerfilesudo ln -s /etc/nginx/sites-available/smart-gate /etc/nginx/sites-enabled/

5. Deploy!

# Remove default nginx site

---sudo rm -f /etc/nginx/sites-enabled/default



## 📋 Detailed Guides# Test nginx configuration

sudo nginx -t

- **Full VPS deployment:** [`deploy/README.md`](deploy/README.md)

- **Streamlit Cloud:** [`STREAMLIT_CLOUD_DEPLOYMENT.md`](STREAMLIT_CLOUD_DEPLOYMENT.md)# If test is successful, restart nginx

- **General deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)sudo systemctl restart nginx

sudo systemctl enable nginx

---```



## 🔧 Troubleshooting#### Step 5: Open Firewall Ports



**Container won't start:**```bash

```bash# Allow HTTP and HTTPS traffic

docker compose logs -fsudo ufw allow 80/tcp

```sudo ufw allow 443/tcp

sudo ufw allow 22/tcp  # SSH (important!)

**Port already in use:**

```bash# Enable firewall (if not already enabled)

sudo lsof -i :8501sudo ufw --force enable

# Kill process or change port in deploy/docker-compose.yml

```# Check status

sudo ufw status

**Domain not working:**```

```bash

# Check DNS#### Step 6: Setup Free SSL Certificate (HTTPS)

nslookup smart-gate.tech

```bash

# Check nginx# Get SSL certificate from Let's Encrypt

sudo systemctl status nginxsudo certbot --nginx -d smart-gate.tech -d www.smart-gate.tech

```

# Follow the prompts:

**SSL certificate failed:**# - Enter your email

```bash# - Agree to terms

# Ensure DNS is propagated first# - Choose to redirect HTTP to HTTPS (option 2)

# Then retry:```

sudo certbot --nginx -d smart-gate.tech

```Certbot will automatically configure HTTPS in Nginx!



---#### Step 7: Verify Deployment



## 🛠️ MaintenanceVisit in your browser:

- http://smart-gate.tech (should redirect to HTTPS)

```bash- https://smart-gate.tech (secure version)

# Update application

cd frontEnd/deploy### Step 8: Enable Auto-Renewal for SSL

git pull

docker compose down```bash

docker compose up -d --build# Test renewal

sudo certbot renew --dry-run

# View logs

docker compose logs -f# Certificate will auto-renew via cron

```

# Restart

docker compose restart---

```

## Option 2: Deploy with Streamlit Community Cloud (Easiest - FREE)

---

#### Step 1: Push Code to GitHub

## 💰 Hosting Comparison

```bash

| Provider | Cost/Month | Free Tier | SSL | Custom Domain |cd /home/soni/hackmty25/frontEnd

|----------|-----------|-----------|-----|---------------|

| **Streamlit Cloud** | $0-20 | ✅ Yes | ✅ Auto | ⚠️ Limited |# Initialize git if not already done

| **DigitalOcean** | $6 | ❌ No | ✅ Manual | ✅ Full |git init

| **Railway** | $5 | ⚠️ 500hrs | ✅ Auto | ✅ Full |git add .

| **Render** | $7 | ⚠️ Limited | ✅ Auto | ✅ Full |git commit -m "Initial commit"

| **Linode** | $5 | ❌ No | ✅ Manual | ✅ Full |

# Push to GitHub (create repo at github.com first)

---git remote add origin https://github.com/SummitLogic/frontEnd.git

git branch -M main

## 📚 Resourcesgit push -u origin main

```

- [Docker Documentation](https://docs.docker.com/)

- [Nginx Documentation](https://nginx.org/en/docs/)#### Step 2: Deploy on Streamlit Cloud

- [Streamlit Documentation](https://docs.streamlit.io/)

- [Let's Encrypt](https://letsencrypt.org/)1. Go to https://share.streamlit.io/

2. Sign in with your GitHub account

---3. Click "New app"

4. Select your repository: `SummitLogic/frontEnd`

**Need help?** Check [`deploy/README.md`](deploy/README.md) for detailed instructions.5. Main file path: `gategroupDashboard.py`

6. Click "Deploy"

#### Step 3: Configure Custom Domain

After deployment, Streamlit will give you a URL like: `your-app.streamlit.app`

Go to your DNS provider and add a CNAME record:
```
Type: CNAME
Name: @
Value: your-app.streamlit.app
TTL: 3600
```

**Note:** Some DNS providers don't allow CNAME on root domain. In that case, use:
```
Type: A (for @)
Type: CNAME (for www)
Name: www
Value: your-app.streamlit.app
```

Then in Streamlit Cloud settings:
1. Go to your app settings
2. Navigate to "Custom domain"
3. Add `smart-gate.tech`

---

## Option 3: Deploy with Railway (Easy + Affordable)

#### Step 1: Push to GitHub (same as Option 2)

#### Step 2: Deploy on Railway

1. Go to https://railway.app/
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `frontEnd` repository
5. Railway auto-detects the Dockerfile and deploys
6. Get your deployment URL

#### Step 3: Add Custom Domain

1. In Railway dashboard, go to your project
2. Click "Settings" → "Domains"
3. Click "Custom Domain"
4. Enter `smart-gate.tech`
5. Railway will show you DNS records to add

Add these to your DNS:
```
Type: CNAME
Name: @
Value: [Railway provides this]
```

---

## Recommended Hosting Providers & Costs

### VPS Options:
- **DigitalOcean**: $6/month (1GB RAM) - [Sign up](https://digitalocean.com)
- **Linode**: $5/month (1GB RAM) - [Sign up](https://linode.com)
- **Vultr**: $6/month (1GB RAM) - [Sign up](https://vultr.com)
- **AWS Lightsail**: $5/month (512MB RAM) - [Sign up](https://aws.amazon.com/lightsail/)
- **Hetzner**: €4.50/month (~$5) - [Sign up](https://hetzner.com)

### Platform as a Service:
- **Streamlit Community Cloud**: FREE (with limitations)
- **Railway**: $5/month (500 hours execution)
- **Render**: FREE tier available, $7/month for production
- **Heroku**: $7/month (Eco plan)

---

## Troubleshooting

### App not accessible:
```bash
# Check if Docker container is running
docker-compose ps

# View container logs
docker-compose logs -f

# Check nginx status
sudo systemctl status nginx

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Domain not resolving:
```bash
# Check DNS propagation
nslookup smart-gate.tech
dig smart-gate.tech

# Verify A record points to correct IP
```

### SSL Certificate Issues:
```bash
# Check certificate status
sudo certbot certificates

# Renew manually if needed
sudo certbot renew
```

### Firewall blocking access:
```bash
# Check firewall status
sudo ufw status

# Ensure ports are open
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## Maintenance Commands

```bash
# Update application
cd ~/frontEnd
git pull
docker-compose down
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
sudo systemctl restart nginx

# Check disk usage
df -h

# Monitor resources
htop
```

---

## Need Help?

- **Streamlit Docs**: https://docs.streamlit.io/
- **Docker Docs**: https://docs.docker.com/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

**Your domain is configured for: smart-gate.tech**

Choose the deployment option that best fits your needs and budget!
