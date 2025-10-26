# Deploy to Streamlit Community Cloud with smart-gate.tech

## ✅ Complete Step-by-Step Guide

### Prerequisites
- GitHub account (free)
- Streamlit Community Cloud account (free - uses GitHub login)
- Your domain: smart-gate.tech (you already have this!)

---

## 🚀 Part 1: Push Your Code to GitHub

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `frontEnd` (or any name you prefer)
3. Make it **Public** (required for free Streamlit Cloud)
4. Don't initialize with README (you already have code)
5. Click "Create repository"

### Step 2: Push Your Code to GitHub

Open terminal in your project directory and run these commands:

```bash
cd /home/soni/hackmty25/frontEnd

# Check if git is initialized
git status

# If not initialized, run:
git init

# Add all files
git add .

# Commit your code
git commit -m "Initial deployment to Streamlit Cloud"

# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/frontEnd.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter your GitHub credentials when prompted.**

---

## 🌐 Part 2: Deploy to Streamlit Community Cloud

### Step 3: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign in" or "Get started"
3. Click "Continue with GitHub"
4. Authorize Streamlit to access your GitHub

### Step 4: Deploy Your App

1. Click the **"New app"** button (top right)
2. Fill in the deployment form:
   - **Repository:** `YOUR_USERNAME/frontEnd`
   - **Branch:** `main`
   - **Main file path:** `gategroupDashboard.py`
   - **App URL:** Choose a custom name like `smart-gate` or `gateflow`
3. Click **"Deploy!"**

### Step 5: Wait for Deployment

- Streamlit will install dependencies from `requirements.txt`
- Build takes 2-5 minutes
- You'll see build logs in real-time
- When complete, your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 🔗 Part 3: Connect Your Custom Domain (smart-gate.tech)

### Step 6: Get Your Streamlit App URL

After deployment, note your Streamlit URL. It will look like:
```
https://YOUR_APP_NAME.streamlit.app
```

### Step 7: Configure Custom Domain in Streamlit Cloud

1. In Streamlit Cloud, click on your app
2. Click the **"⋮"** menu (three dots) → **"Settings"**
3. Scroll down to **"Custom domain"** section
4. Click **"Add domain"**
5. Enter: `smart-gate.tech`
6. Click **"Add"**

Streamlit will show you DNS configuration instructions.

### Step 8: Configure Your Domain DNS

Go to your domain registrar (where you bought smart-gate.tech) and configure DNS:

**Option A: If your registrar supports CNAME flattening (Cloudflare, etc.)**
```
Type: CNAME
Name: @
Target: YOUR_APP_NAME.streamlit.app
TTL: Auto or 3600
```

**Option B: If CNAME not supported for root domain (most registrars)**
```
Type: A
Name: @
Target: 44.214.198.148
TTL: 3600

Type: CNAME
Name: www
Target: YOUR_APP_NAME.streamlit.app
TTL: 3600
```

**Note:** The A record IP (44.214.198.148) is Streamlit's current IP. Streamlit will provide the exact IP in their custom domain settings.

### Step 9: Verify DNS Configuration

1. Wait 10-30 minutes for DNS propagation
2. Check DNS status:
```bash
nslookup smart-gate.tech
dig smart-gate.tech
```

3. Visit your domain: https://smart-gate.tech
4. Streamlit will automatically provision FREE SSL certificate

---

## 🔄 Part 4: How to Update/Redeploy Your App

**Great news: Updates are AUTOMATIC!** Every time you push to GitHub, Streamlit automatically redeploys.

### Method 1: Automatic Redeployment (Recommended)

Whenever you make changes:

```bash
cd /home/soni/hackmty25/frontEnd

# Make your changes to files
# ... edit gategroupDashboard.py or other files ...

# Save and commit changes
git add .
git commit -m "Updated dashboard features"
git push origin main
```

**That's it!** Streamlit Cloud will detect the push and automatically redeploy within 1-2 minutes.

### Method 2: Manual Reboot

If automatic deploy doesn't trigger:

1. Go to https://share.streamlit.io/
2. Click on your app
3. Click the **"⋮"** menu → **"Reboot app"**

### Method 3: Manual Redeploy

For a complete redeploy:

1. Go to your app in Streamlit Cloud
2. Click **"⋮"** → **"Delete app"**
3. Deploy again following Step 4

---

## 📝 Common Workflow for Updates

Here's your typical workflow when making changes:

```bash
# 1. Navigate to your project
cd /home/soni/hackmty25/frontEnd

# 2. Make changes to your files
# Edit gategroupDashboard.py, add features, fix bugs, etc.

# 3. Test locally (optional but recommended)
streamlit run gategroupDashboard.py

# 4. Commit and push to GitHub
git add .
git commit -m "Description of changes"
git push origin main

# 5. Wait 1-2 minutes - Streamlit auto-deploys!
# 6. Visit https://smart-gate.tech to see changes live
```

---

## 🔧 Important Configuration Notes

### Secrets Management

If you need to add API keys or secrets:

1. In Streamlit Cloud, go to your app settings
2. Click **"Secrets"**
3. Add secrets in TOML format:
```toml
api_key = "your_secret_key"
database_url = "your_db_url"
```

Access in your code:
```python
import streamlit as st
api_key = st.secrets["api_key"]
```

### Requirements.txt

Your current `requirements.txt` is:
```
streamlit>=1.20.0
pandas>=1.5.3
plotly>=5.15.0
requests>=2.31.0
```

This is perfect! If you need more packages:
```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add new dependency"
git push origin main
```

---

## 🎯 Complete Checklist

- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Sign up for Streamlit Cloud
- [ ] Deploy app from GitHub repo
- [ ] Note your Streamlit app URL
- [ ] Add custom domain in Streamlit settings
- [ ] Configure DNS records at domain registrar
- [ ] Wait for DNS propagation (10-30 mins)
- [ ] Verify site works at https://smart-gate.tech
- [ ] Test auto-deploy by making a small change

---

## 🐛 Troubleshooting

### App won't deploy
- Check `requirements.txt` has all dependencies
- Make sure repository is public
- Check build logs for errors in Streamlit Cloud

### Domain not working
- Verify DNS records are correct
- Check DNS propagation: https://dnschecker.org/
- Wait up to 48 hours for full propagation
- Make sure you added domain in Streamlit settings

### App shows old version
- Go to Streamlit Cloud → Reboot app
- Clear browser cache (Ctrl+Shift+R)
- Check GitHub to confirm push was successful

### Build fails
- Check Python version compatibility
- Verify all imports are in requirements.txt
- Check Streamlit Cloud build logs for specific errors

---

## 💰 Costs

- **Streamlit Community Cloud:** FREE ✅
- **GitHub:** FREE ✅
- **SSL Certificate:** FREE (auto-provisioned) ✅
- **Domain (smart-gate.tech):** Already purchased ✅

**Total monthly cost: $0** 🎉

---

## 📊 Limitations of Free Tier

- **Resources:** 1 GB RAM, 1 CPU core per app
- **Apps:** 3 public apps per account
- **Sleep:** Apps sleep after 7 days of inactivity (wake on first visit)
- **Concurrent users:** Reasonable limits for small-medium traffic
- **Repo visibility:** Must be public GitHub repository

For more resources, Streamlit offers paid plans starting at $20/month.

---

## 🔐 Security Notes

Since your repository is public:
- **Never commit** API keys, passwords, or secrets
- Use Streamlit Secrets for sensitive data
- Add `.streamlit/secrets.toml` to `.gitignore`
- Review your code before pushing

---

## 📚 Useful Links

- **Streamlit Cloud Dashboard:** https://share.streamlit.io/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Docs:** https://docs.github.com/

---

## 🎉 You're All Set!

Your workflow is now:
1. **Develop locally** → Make changes to your code
2. **Push to GitHub** → `git push origin main`
3. **Auto-deploy** → Streamlit rebuilds automatically
4. **Live in 1-2 minutes** → Visit https://smart-gate.tech

**Questions?** The Streamlit community forum is very helpful!

---

**Domain configured for: smart-gate.tech**
**Deployment method: Streamlit Community Cloud (FREE)**
