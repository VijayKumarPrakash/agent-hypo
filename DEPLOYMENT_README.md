# 🚀 White Agent A2A - Complete Deployment Package

Everything you need to deploy the White Agent A2A service for **FREE**.

## 📚 Documentation Overview

| Document | Purpose | Time Required |
|----------|---------|---------------|
| **[ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md)** | ✅ Checklist to track your setup progress | Use as you go |
| **[DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)** | 📖 Detailed step-by-step deployment guide | 40-50 min (first time) |
| **[QUICK_START_A2A.md](QUICK_START_A2A.md)** | ⚡ Quick reference for getting started | 5 min read |
| **[README_A2A.md](README_A2A.md)** | 📘 Complete technical documentation | Reference |

## 🎯 Start Here

### First Time Deployment?

**Follow this order:**

1. **Print or open:** [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md)
   - Use this to track your progress
   - Fill in your credentials as you go

2. **Follow:** [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)
   - Complete step-by-step instructions
   - Covers account creation through testing
   - Includes screenshots and troubleshooting

3. **Test:** Use the provided test scripts
   ```bash
   python test_a2a_service.py
   ```

### Already Deployed?

- **Update your service:** Just `git push` (Render auto-deploys)
- **Monitor:** https://dashboard.render.com
- **API Docs:** `https://your-service.onrender.com/docs`

---

## 📋 What You'll Need

### Accounts (All Free)

1. **GitHub** - For code hosting
   - https://github.com/signup
   - Already have one? ✓

2. **Cloudflare** - For file storage (R2)
   - https://dash.cloudflare.com/sign-up
   - No credit card required

3. **Render** - For hosting the service
   - https://render.com
   - Sign up with GitHub (easiest)

4. **Google** - For Gemini API (optional)
   - https://aistudio.google.com/app/apikey
   - For LLM-powered analysis

### Total Time
- **First deployment:** 40-50 minutes
- **Future updates:** 1 minute (just `git push`)

### Total Cost
- **$0/month** for everything! 🎉

---

## 🏗️ What Gets Deployed

```
Your A2A Service
│
├── Hosting: Render.com (Free Tier)
│   └── 750 hours/month runtime
│   └── Auto-deploy on git push
│   └── HTTPS included
│
├── Storage: Cloudflare R2 (Free Tier)
│   └── 10GB storage
│   └── 1M operations/month
│   └── No egress fees
│
└── LLM: Gemini API (Free Tier)
    └── 60 requests/minute
    └── Intelligent analysis
```

---

## 🎬 Quick Start (If You're Experienced)

Already familiar with these tools? Here's the express version:

```bash
# 1. Set up R2 bucket on Cloudflare
# 2. Get API tokens from R2
# 3. Get Gemini API key (optional)

# 4. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/white-agent-a2a.git
git add .
git commit -m "Deploy A2A service"
git push -u origin main

# 5. Deploy on Render
# - New Web Service → Connect GitHub repo
# - Environment: Docker
# - Add environment variables (S3_*, GEMINI_API_KEY)
# - Deploy

# 6. Test
curl https://your-service.onrender.com/health
```

See [QUICK_START_A2A.md](QUICK_START_A2A.md) for more details.

---

## 📁 Deployment Files Reference

### Configuration Files

- **`render.yaml`** - Render.com blueprint for one-click deploy
- **`.dockerignore`** - Docker build optimization
- **`Dockerfile`** - Container definition
- **`.env.a2a.example`** - Environment variable template

### Scripts

- **`scripts/deploy_to_render.sh`** - Automated deployment helper
  ```bash
  ./scripts/deploy_to_render.sh
  ```

- **`scripts/keep_alive.sh`** - Local keep-alive monitor
  ```bash
  SERVICE_URL=https://your-service.onrender.com ./scripts/keep_alive.sh
  ```

- **`test_a2a_service.py`** - Service testing script
  ```bash
  python test_a2a_service.py
  ```

- **`verify_setup.sh`** - Pre-deployment verification
  ```bash
  ./verify_setup.sh
  ```

---

## 🔑 Environment Variables You'll Need

Save these in Render dashboard:

```bash
S3_BUCKET=white-agent                    # Your R2 bucket name
S3_ACCESS_KEY_ID=xxx                     # From R2 API tokens
S3_SECRET_ACCESS_KEY=xxx                 # From R2 API tokens
S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
S3_PUBLIC_URL_BASE=https://pub-xxx.r2.dev
GEMINI_API_KEY=xxx                       # Optional, for LLM mode
```

See [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) Step 7 for how to get these values.

---

## ✅ Pre-Deployment Checklist

Before you start, make sure you have:

- [ ] Code pushed to GitHub
- [ ] R2 bucket created on Cloudflare
- [ ] R2 API tokens generated
- [ ] (Optional) Gemini API key obtained
- [ ] All environment variables ready to paste

**Ready?** Start with [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)

---

## 🧪 Testing Your Deployment

### 1. Automated Tests
```bash
python test_a2a_service.py
```

### 2. Manual Tests

**Health Check:**
```bash
curl https://your-service.onrender.com/health
```

**API Documentation:**
```
https://your-service.onrender.com/docs
```

**Run Analysis:**
```bash
curl -X POST https://your-service.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://example.com/context.txt",
    "data_url": "https://example.com/data.csv",
    "mode": "auto"
  }'
```

---

## 🔄 Updating Your Deployed Service

After initial deployment, updates are easy:

```bash
# 1. Make your changes to the code

# 2. Commit and push
git add .
git commit -m "Your changes"
git push

# 3. Render automatically rebuilds and deploys!
# Watch progress at: https://dashboard.render.com
```

Or use the helper script:
```bash
./scripts/deploy_to_render.sh
```

---

## 📊 Monitoring Your Service

### Render Dashboard
- **URL:** https://dashboard.render.com
- **View:** Logs, metrics, deployment history
- **Access:** Click on your `white-agent` service

### Health Endpoint
- **URL:** `https://your-service.onrender.com/health`
- **Check:** Service status, LLM availability, storage config

### Logs
```bash
# View in Render dashboard → Logs tab
# Or use Render CLI (install from https://render.com/docs/cli)
```

---

## 🆘 Troubleshooting

### Issue: Build failed on Render
**Solution:**
- Check Render logs for specific error
- Verify all files pushed to GitHub: `git log`
- Ensure Dockerfile exists

### Issue: "Storage not configured"
**Solution:**
- Verify all 5 S3_* variables set in Render
- Check for typos in variable names
- Verify R2 bucket exists

### Issue: Service times out
**Solution:**
- Cold start is normal (~30s first request)
- Set up keep-alive cron job
- Or upgrade to paid tier ($7/month)

### Issue: Can't access uploaded files
**Solution:**
- Enable public access on R2 bucket
- Verify S3_PUBLIC_URL_BASE is correct
- Check R2.dev subdomain is enabled

**More help:** See [README_A2A.md](README_A2A.md) "Troubleshooting" section

---

## 💰 Cost Breakdown

| Service | Free Tier | Paid Option | Notes |
|---------|-----------|-------------|-------|
| **Render** | 750 hrs/month | $7/month | Enough for 24/7 on free tier |
| **Cloudflare R2** | 10GB + 1M ops | Pay as you go | Very generous limits |
| **Gemini API** | 60 req/min | Pay as you go | Free tier usually enough |
| **Total** | **$0/month** | ~$7/month | For always-on service |

---

## 🎯 Success Metrics

You'll know deployment succeeded when:

- ✅ Health endpoint returns `"status": "healthy"`
- ✅ `"storage_configured": true` in health response
- ✅ API docs load at `/docs` endpoint
- ✅ Test analysis run completes successfully
- ✅ Generated files accessible via returned URLs

---

## 📚 Additional Resources

### Documentation
- [README_A2A.md](README_A2A.md) - Complete technical docs
- [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md) - Technical architecture
- [QUICK_START_A2A.md](QUICK_START_A2A.md) - Fast local setup

### External Docs
- [Render Documentation](https://render.com/docs)
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Legacy System
- Original CLI still works: `python legacy_main.py`
- Original docs: [README.md](README.md)

---

## 🎊 Next Steps After Deployment

1. **Register with A2A Controller**
   - Provide your service URL
   - Configure health check endpoint

2. **Set Up Monitoring**
   - Add uptime monitoring (e.g., UptimeRobot)
   - Configure alerts for downtime

3. **Optimize Performance**
   - Add keep-alive cron job (prevents cold starts)
   - Consider upgrading to paid tier if needed

4. **Scale If Needed**
   - Monitor usage in Render dashboard
   - Upgrade plan when approaching limits
   - Consider adding caching layer

---

## 🤝 Support

**Need help?**

1. Check [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) troubleshooting
2. Review [README_A2A.md](README_A2A.md) detailed docs
3. Check Render/Cloudflare status pages
4. Review service logs in Render dashboard

---

## 📝 License

See LICENSE file for details.

---

**Ready to deploy? Start with [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md)!** ✨
