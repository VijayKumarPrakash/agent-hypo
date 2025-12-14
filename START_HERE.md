# 👋 START HERE - White Agent A2A Deployment

## What Is This?

Your White Agent has been refactored into a **production-ready A2A HTTP service** that can be deployed to the cloud for **FREE**.

---

## ⚡ What You Need To Do

### Option 1: Just Want To Deploy? (Recommended)

**Follow this single document:**

### 📋 **[DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)**

This guide walks you through:
1. Creating all necessary accounts (GitHub, Cloudflare, Render)
2. Setting up cloud storage (Cloudflare R2)
3. Deploying your service (Render.com)
4. Testing everything works

**Time:** 40-50 minutes (first time)
**Cost:** $0/month

Print or open [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md) to track progress.

---

### Option 2: Want To Understand Everything First?

**Read these in order:**

1. **[DEPLOYMENT_README.md](DEPLOYMENT_README.md)** - Overview of deployment package
2. **[README_A2A.md](README_A2A.md)** - Complete technical documentation
3. **[REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)** - What changed in the refactor

Then follow [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) to deploy.

---

## 🎯 Quick Decision Guide

**"I just want to deploy and use it"**
→ Go to [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)

**"I want to test locally first"**
→ Go to [QUICK_START_A2A.md](QUICK_START_A2A.md)

**"I want to understand the architecture"**
→ Go to [README_A2A.md](README_A2A.md)

**"I want to use the old CLI version"**
→ Run: `python legacy_main.py --help`

---

## 📦 What You're Getting

### Free Cloud Service
- **HTTP API** for RCT analysis
- **Stateless** and scalable
- **A2A-compliant** for controller integration
- **Auto-deployment** on git push
- **HTTPS** included

### Free Cloud Storage
- **Cloudflare R2** for generated reports
- **Public URLs** to analysis outputs
- **10GB storage** free tier

### Smart Analysis
- **LLM-powered** mode (with Gemini API)
- **Traditional** mode (no API calls)
- **Auto-detection** of best mode

---

## 📊 What Accounts You'll Create

All are **FREE** with no credit card required:

1. **GitHub** (if you don't have)
   - For hosting your code
   - https://github.com/signup

2. **Cloudflare**
   - For file storage (R2)
   - https://dash.cloudflare.com/sign-up

3. **Render**
   - For hosting your service
   - https://render.com

4. **Google** (optional)
   - For Gemini API key
   - https://aistudio.google.com/app/apikey

---

## 🚀 After Deployment

Your service will be accessible at:
```
https://white-agent.onrender.com
```
(Or your custom name)

### Endpoints:
- **POST /run** - Run analysis
- **GET /health** - Health check
- **GET /docs** - Interactive API docs

### Example Usage:
```bash
curl -X POST https://white-agent.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://example.com/context.txt",
    "data_url": "https://example.com/data.csv"
  }'
```

---

## 📁 File Overview

### You Need To Read
- **[DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)** ← START HERE for deployment

### Reference Documents
- [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md) - Track your progress
- [DEPLOYMENT_README.md](DEPLOYMENT_README.md) - Package overview
- [README_A2A.md](README_A2A.md) - Technical documentation
- [QUICK_START_A2A.md](QUICK_START_A2A.md) - Local testing guide

### Helper Scripts
- `scripts/deploy_to_render.sh` - Deploy with one command
- `scripts/keep_alive.sh` - Keep service warm
- `test_a2a_service.py` - Test your deployment
- `verify_setup.sh` - Pre-flight checks

### Configuration
- `render.yaml` - Render deployment config
- `Dockerfile` - Container definition
- `.env.a2a.example` - Environment variables template

---

## ⏱️ Time Estimate

- **Reading this page:** 5 minutes ✓
- **Following deployment guide:** 40-50 minutes
- **Future updates:** 1 minute (just `git push`)

---

## 💡 Tips

1. **Use the checklist** - Print [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md) and check off items
2. **Save your credentials** - You'll need them during setup
3. **Don't rush** - Follow each step carefully
4. **Test as you go** - Verify each section works before moving on

---

## 🆘 If You Get Stuck

1. **Check troubleshooting** in [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)
2. **Review logs** in Render dashboard
3. **Verify credentials** match what you saved
4. **Test health endpoint** to diagnose issues

---

## ✨ Ready to Deploy?

### **👉 Go to [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) now!**

Or if you want to test locally first:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.a2a.example .env
# Edit .env with your settings

# Run locally
uvicorn app.server:app --reload

# Test
python test_a2a_service.py
```

See [QUICK_START_A2A.md](QUICK_START_A2A.md) for local setup details.

---

## 🎉 After Successful Deployment

You'll have:
- ✅ Production HTTP service running 24/7
- ✅ Cloud storage for analysis outputs
- ✅ Public API accessible via HTTPS
- ✅ Auto-deployment on code updates
- ✅ Interactive API documentation
- ✅ Completely free!

**All for $0/month** 💰

---

## 📞 Still Have Questions?

- Technical details → [README_A2A.md](README_A2A.md)
- Local testing → [QUICK_START_A2A.md](QUICK_START_A2A.md)
- What changed → [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)
- Legacy CLI → `python legacy_main.py --help`

---

**Don't overthink it - just start with [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)!** 🚀
