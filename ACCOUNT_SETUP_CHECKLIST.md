# Account Setup Checklist

Use this checklist to track your progress through the deployment setup.

## ☐ Part 1: Accounts (15 minutes)

### ☐ GitHub Account
- [ ] Go to https://github.com/signup
- [ ] Sign up (or sign in if you have one)
- [ ] Verify email
- **Username:** _________________

### ☐ Cloudflare Account
- [ ] Go to https://dash.cloudflare.com/sign-up
- [ ] Sign up with email
- [ ] Verify email
- [ ] Log in successful
- **Email:** _________________

### ☐ Render Account
- [ ] Go to https://render.com
- [ ] Click "Get Started"
- [ ] Sign up with GitHub (easiest option)
- [ ] Authorize Render
- **Account created:** ✓

### ☐ Gemini API Key (For LLM mode - RECOMMENDED)
- [ ] Go to https://aistudio.google.com/app/apikey
- [ ] Sign in with Google
- [ ] Click "Create API Key"
- [ ] Select "Create API key in new project"
- [ ] Copy and save the key immediately
- **API Key (save securely):** _________________
- **Note:** Free tier = 60 requests/min, plenty for testing

---

## ☐ Part 2: Cloudflare R2 Setup (10 minutes)

### ☐ Create R2 Bucket
- [ ] In Cloudflare dashboard → R2 Object Storage
- [ ] Click "Create bucket"
- [ ] Name: `white-agent`
- [ ] Click "Create bucket"
- [ ] Go to Settings → Public access → "Allow Access"
- [ ] Note R2.dev URL (e.g., `https://pub-abc123.r2.dev`)
- **R2.dev URL:** _________________

### ☐ Generate API Tokens
- [ ] R2 → "Manage R2 API Tokens" (top right)
- [ ] Click "Create API Token"
- [ ] Configure:
  - Name: `white-agent-access`
  - Permissions: **Object Read & Write**
  - TTL: Forever (or set expiration)
- [ ] Click "Create API Token"
- [ ] **SAVE THESE IMMEDIATELY** (Secret Key shown only once!):

```
Access Key ID: _________________________________
(~20 characters, starts with letters/numbers)

Secret Access Key: _____________________________
(~40+ characters - KEEP SECRET!)

Account ID: ____________________________________
(from URL: dash.cloudflare.com/[THIS-PART]/r2)

Endpoint URL: https://___________.r2.cloudflarestorage.com
(format: https://<account-id>.r2.cloudflarestorage.com)
```

**Finding Account ID:**
- Look at browser URL bar when in R2
- Or click bucket → Settings → Account ID shown there

---

## ☐ Part 3: Environment Variables Template

Copy this and fill in your actual values:

```bash
S3_BUCKET=white-agent

S3_ACCESS_KEY_ID=___________________________

S3_SECRET_ACCESS_KEY=___________________________

S3_ENDPOINT_URL=https://___________.r2.cloudflarestorage.com

S3_PUBLIC_URL_BASE=___________________________
(your R2.dev URL from above)

GEMINI_API_KEY=___________________________
(optional - from Part 1)
```

**Save this in a secure location** - you'll paste these into Render.

---

## ☐ Part 4: GitHub Setup (2 minutes)

### ☐ Push Code to Existing GitHub Repository
- [ ] Open terminal in project directory: `cd /Users/vkp/dev/cs294/agent-hypo`
- [ ] Check git status: `git status`
- [ ] Verify remote is configured: `git remote -v`
- [ ] Add all new A2A files:
  ```bash
  git add .
  git commit -m "Add A2A service deployment configuration"
  git push
  ```
- [ ] Verify new files appear on GitHub (refresh your repo page)
  - Should see: `app/`, `Dockerfile`, `render.yaml`, etc.
- **GitHub Repo URL:** _________________
  (your existing cs294/agent-hypo repo)

---

## ☐ Part 5: Render Deployment (10 minutes)

### ☐ Create Web Service
- [ ] Log in to https://dashboard.render.com
- [ ] Click "New +" → "Web Service"
- [ ] Connect your existing GitHub repository: `cs294/agent-hypo`
- [ ] Configure:
  - Name: `white-agent`
  - Region: Oregon (or closest to you)
  - Branch: `main` (or your default branch)
  - Root Directory: (leave empty)
  - Environment: `Docker`
  - **Start Command:** (leave empty - auto-detected from Dockerfile)
  - Plan: `Free`
- [ ] Click "Create Web Service"

### ☐ Add Environment Variables
- [ ] In Render dashboard → "Environment" tab
- [ ] Add each variable from Part 3 (one by one):
  - [ ] S3_BUCKET
  - [ ] S3_ACCESS_KEY_ID
  - [ ] S3_SECRET_ACCESS_KEY
  - [ ] S3_ENDPOINT_URL
  - [ ] S3_PUBLIC_URL_BASE
  - [ ] GEMINI_API_KEY
- [ ] Click "Save Changes"
- [ ] Wait for auto-redeploy (~3-5 minutes)

### ☐ Get Service URL
- **Your Render URL:** _________________
  (shown at top of dashboard, e.g., `https://white-agent.onrender.com`)

---

## ☐ Part 6: Testing (5 minutes)

### ☐ Health Check
- [ ] Open in browser: `https://YOUR_URL.onrender.com/health`
- [ ] Or test with curl:
  ```bash
  curl https://YOUR_URL.onrender.com/health
  ```
- [ ] Verify response shows:
  - [ ] `"status": "healthy"`
  - [ ] `"storage_configured": true`
  - [ ] `"llm_available": true` (if GEMINI_API_KEY set)

### ☐ API Documentation
- [ ] Open: `https://YOUR_URL.onrender.com/docs`
- [ ] Verify Swagger UI loads
- [ ] Try the `/health` endpoint in Swagger

### ☐ Test Analysis (if you have test data)
- [ ] Use `/docs` interface or curl
- [ ] Verify you get back URLs to generated files
- [ ] Check files are accessible in browser

---

## ☐ Part 7: Keep-Alive Setup (Optional - 5 minutes)

To prevent cold starts on Render free tier:

### ☐ Set Up Cron Job
- [ ] Go to https://cron-job.org/en/signup/
- [ ] Create account and verify email
- [ ] Create new cronjob:
  - Title: `White Agent Keep-Alive`
  - URL: `https://YOUR_URL.onrender.com/health`
  - Schedule: `*/10 * * * *` (every 10 min)
  - Enable: ✓
- [ ] Click "Create cronjob"
- [ ] Verify it's running

---

## 🎉 Deployment Complete!

### Your Service Details

```
Service URL: _________________________________

Health Check: _________________________________/health

API Docs: _________________________________/docs

Render Dashboard: https://dashboard.render.com

Cloudflare Dashboard: https://dash.cloudflare.com
```

### Next Steps

1. **Register with A2A Controller**
2. **Monitor your service** in Render dashboard
3. **Update your agent:**
   ```bash
   git add .
   git commit -m "Update"
   git push
   # Render auto-deploys!
   ```

---

## 📞 Support Resources

- **Deployment Guide:** [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)
- **API Documentation:** [README_A2A.md](README_A2A.md)
- **Quick Start:** [QUICK_START_A2A.md](QUICK_START_A2A.md)
- **Render Docs:** https://render.com/docs
- **Cloudflare R2 Docs:** https://developers.cloudflare.com/r2/

---

## ⏱️ Total Time Estimate

- Account setup: ~15 minutes
- R2 configuration: ~10 minutes
- GitHub push: ~5 minutes
- Render deployment: ~10 minutes
- Testing: ~5 minutes
- Keep-alive (optional): ~5 minutes

**Total: 40-50 minutes** (first time)

Future deployments: Just `git push` (~1 minute)!
