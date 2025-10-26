# Quick Deployment Guide for smart-gate.tech

## Step-by-Step Deployment Instructions

### Option 1: Deploy with VPS (Recommended - Most Control)

#### Prerequisites:
- A VPS/Cloud Server (DigitalOcean, AWS EC2, Linode, Vultr, etc.)
- SSH access to your server
- Root or sudo access

#### Step 1: Configure Your Domain DNS

Go to your domain registrar (where you bought smart-gate.tech) and add these DNS records:

```
Type: A
Name: @
Value: YOUR_SERVER_IP_ADDRESS
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP_ADDRESS
TTL: 3600
```

**Note:** DNS propagation can take up to 48 hours, but usually completes in 15-30 minutes.

#### Step 2: Set Up Your Server

SSH into your server:
```bash
ssh root@YOUR_SERVER_IP
# or
ssh your-username@YOUR_SERVER_IP
```

Install required software:
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

# Install Certbot for free SSL
sudo apt install certbot python3-certbot-nginx -y

# Install Git
sudo apt install git -y
```

Log out and log back in for Docker permissions to take effect:
```bash
exit
ssh root@YOUR_SERVER_IP
```

#### Step 3: Deploy Your Application

```bash
# Navigate to home directory
cd ~

# Clone your repository (if using Git)
git clone https://github.com/SummitLogic/frontEnd.git
cd frontEnd

# OR upload files using SCP from your local machine:
# scp -r /home/soni/hackmty25/frontEnd root@YOUR_SERVER_IP:/root/
# Then: cd frontEnd
```

Build and run the Docker container:
```bash
docker-compose up -d --build
```

Check if it's running:
```bash
docker-compose ps
docker-compose logs -f
# Press Ctrl+C to exit logs
```

#### Step 4: Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/smart-gate

# Enable the site
sudo ln -s /etc/nginx/sites-available/smart-gate /etc/nginx/sites-enabled/

# Remove default nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# If test is successful, restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### Step 5: Open Firewall Ports

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH (important!)

# Enable firewall (if not already enabled)
sudo ufw --force enable

# Check status
sudo ufw status
```

#### Step 6: Setup Free SSL Certificate (HTTPS)

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d smart-gate.tech -d www.smart-gate.tech

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)
```

Certbot will automatically configure HTTPS in Nginx!

#### Step 7: Verify Deployment

Visit in your browser:
- http://smart-gate.tech (should redirect to HTTPS)
- https://smart-gate.tech (secure version)

### Step 8: Enable Auto-Renewal for SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Certificate will auto-renew via cron
```

---

## Option 2: Deploy with Streamlit Community Cloud (Easiest - FREE)

#### Step 1: Push Code to GitHub

```bash
cd /home/soni/hackmty25/frontEnd

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Push to GitHub (create repo at github.com first)
git remote add origin https://github.com/SummitLogic/frontEnd.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `SummitLogic/frontEnd`
5. Main file path: `gategroupDashboard.py`
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
