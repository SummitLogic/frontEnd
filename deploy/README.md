# Deployment Configuration

This directory contains all deployment-related files for the GateFlow Dashboard.

## Structure

```
deploy/
├── docker-compose.yml       # Development/testing compose file
├── docker-compose.prod.yml  # Production compose file with nginx
├── .env.example            # Environment variables template
└── nginx/
    └── nginx.conf          # Nginx reverse proxy configuration
```

## Quick Start

### Development (Local Testing)

```bash
cd deploy
docker-compose up --build
```

Access at: http://localhost:8501

### Production Deployment

1. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Deploy with nginx:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. **Set up SSL (Let's Encrypt):**
   ```bash
   # Install certbot on your server
   sudo apt install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d smart-gate.tech -d www.smart-gate.tech
   
   # Then uncomment the HTTPS section in nginx/nginx.conf
   ```

4. **Restart services:**
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart a service
docker-compose restart streamlit

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Check container status
docker-compose ps
```

## Notes

- The `data/` folder is mounted as a volume for persistence
- User data (`users.json`) is stored in `data/` (not in git)
- Nginx proxies requests from port 80/443 to Streamlit on port 8501
- SSL certificates should be placed in `deploy/ssl/` directory
