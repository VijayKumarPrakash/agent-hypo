# Complete Deployment Guide - Step by Step

This guide walks you through deploying the White Agent A2A service for **FREE**.

## 📋 What You'll Need

- GitHub account (free)
- Cloudflare account (free)
- Render.com account (free)
- Google account (for Gemini API - free tier available)

---

## Part 1: Account Setup (One-time, ~15 minutes)

### Step 1: Create GitHub Account (if you don't have one)

**Already have GitHub?** Skip to Step 2.

1. Go to https://github.com/signup
2. Enter your email
3. Create password
4. Verify email
5. **Done!**

---

### Step 2: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Enter email and create password
3. Verify email
4. Log in to Cloudflare dashboard
5. **Done!**

**Cost: $0** - You don't need to add a credit card for R2.

---

### Step 3: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"**
3. Choose **"Sign up with GitHub"** (easiest)
4. Authorize Render to access your GitHub
5. **Done!**

**Cost: $0** - Free tier doesn't require a credit card.

---

### Step 4: Get Gemini API Key (Optional but Recommended)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select **"Create API key in new project"**
5. Copy the API key (save it somewhere safe!)
6. **Done!**

**Cost: $0** - Generous free tier (60 requests/minute).

---

## Part 2: Set Up Cloud Storage (~10 minutes)

### Step 5: Create Cloudflare R2 Bucket

1. **Log in to Cloudflare dashboard**
   - https://dash.cloudflare.com

2. **Navigate to R2:**
   - Left sidebar → **R2 Object Storage**
   - Click **"Create bucket"**

3. **Create bucket:**
   - **Bucket name:** `white-agent` (lowercase, no spaces)
   - **Region:** Automatic
   - Click **"Create bucket"**

4. **Enable public access:**
   - Click on your `white-agent` bucket
   - Go to **Settings** tab
   - Scroll to **Public access**
   - Click **"Allow Access"**
   - Confirm

5. **Get public URL:**
   - In Settings, find **"R2.dev subdomain"**
   - Click **"Allow Access"** if needed
   - You'll get a URL like: `https://pub-abc123.r2.dev`
   - **Save this URL** - you'll need it later

6. **Done!**

---

### Step 6: Generate R2 API Tokens

1. **In Cloudflare dashboard:**
   - Left sidebar → **R2 Object Storage**
   - Click **"Manage R2 API Tokens"** (top right)

2. **Create API token:**
   - Click **"Create API Token"**
   - **Token name:** `white-agent-access`
   - **Permissions:**
     - ✅ Object Read & Write
   - **TTL:** Forever (or set expiration if you prefer)
   - Click **"Create API Token"**

3. **IMPORTANT - Save these values immediately:**
   ```
   Access Key ID: <copy this>
   Secret Access Key: <copy this>
   ```
   **You won't be able to see the Secret Access Key again!**

4. **Also note your Account ID:**
   - Look at the URL in your browser
   - Format: `https://dash.cloudflare.com/<ACCOUNT_ID>/r2/...`
   - Or find it in R2 dashboard under "Account ID"
   - **Save this Account ID**

5. **Build your endpoint URL:**
   ```
   Format: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
   Example: https://abc123def456.r2.cloudflarestorage.com
   ```
   **Save this URL**

---

### Step 7: Prepare Your Environment Variables

Create a text file with your values (you'll paste these into Render later):

```bash
# Copy this template and fill in YOUR values:

S3_BUCKET=white-agent

S3_ACCESS_KEY_ID=<paste Access Key ID from Step 6>

S3_SECRET_ACCESS_KEY=<paste Secret Access Key from Step 6>

S3_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com

S3_PUBLIC_URL_BASE=https://pub-abc123.r2.dev
# (Use the R2.dev URL from Step 5)

GEMINI_API_KEY=<paste API key from Step 4>
# (Optional - but recommended for LLM mode)
```

**Save this file** as `my-env-vars.txt` - you'll copy/paste from it in Step 10.

---

## Part 3: Deploy to Render (~10 minutes)

### Step 8: Push Your Code to GitHub

1. **Open terminal in your project directory:**
   ```bash
   cd /Users/vkp/dev/cs294/agent-hypo
   ```

2. **Check if you have a remote:**
   ```bash
   git remote -v
   ```

3. **If no remote exists, create GitHub repo:**
   - Go to https://github.com/new
   - **Repository name:** `white-agent-a2a`
   - **Visibility:** Private (or Public - your choice)
   - **Don't** initialize with README (you already have code)
   - Click **"Create repository"**

4. **Connect and push:**
   ```bash
   # If you just created a new repo:
   git remote add origin https://github.com/YOUR_USERNAME/white-agent-a2a.git

   # Push your code
   git add .
   git commit -m "Add A2A service deployment files"
   git push -u origin main
   ```

5. **Verify:**
   - Refresh your GitHub repo page
   - You should see all your files

---

### Step 9: Deploy to Render

1. **Log in to Render:**
   - https://dashboard.render.com

2. **Create new Web Service:**
   - Click **"New +"** (top right)
   - Select **"Web Service"**

3. **Connect repository:**
   - Click **"Connect account"** if needed
   - Find your `white-agent-a2a` repository
   - Click **"Connect"**

4. **Configure service:**
   ```
   Name: white-agent
   Region: Oregon (US West) - or choose closest to you
   Branch: main
   Root Directory: (leave empty)
   Environment: Docker
   Plan: Free
   ```

5. **Click "Create Web Service"** (DON'T click "Advanced" yet)

---

### Step 10: Add Environment Variables

1. **In your Render service dashboard:**
   - Click **"Environment"** tab (left sidebar)

2. **Add each variable one by one:**
   - Click **"Add Environment Variable"**
   - Copy each line from your `my-env-vars.txt` file
   - Paste **Key** and **Value**

   Add these 6 variables:
   ```
   S3_BUCKET
   S3_ACCESS_KEY_ID
   S3_SECRET_ACCESS_KEY
   S3_ENDPOINT_URL
   S3_PUBLIC_URL_BASE
   GEMINI_API_KEY
   ```

3. **Save changes:**
   - Click **"Save Changes"** button at top

4. **Render will automatically redeploy** with your environment variables

---

### Step 11: Wait for Deployment

1. **Monitor the build:**
   - Click **"Logs"** tab
   - You'll see the Docker build progress
   - Takes ~3-5 minutes

2. **Wait for:**
   ```
   ==> Build successful 🎉
   ==> Deploying...
   ==> Your service is live 🎉
   ```

3. **Get your service URL:**
   - Top of dashboard shows: `https://white-agent.onrender.com`
   - (Or similar - your actual URL will be shown)
   - **Copy this URL**

---

### Step 12: Test Your Deployment

1. **Health check (in browser or terminal):**
   ```bash
   curl https://white-agent.onrender.com/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "llm_available": true,
     "storage_configured": true
   }
   ```

2. **View API docs (in browser):**
   ```
   https://white-agent.onrender.com/docs
   ```
   You should see interactive Swagger UI!

3. **Test with sample data:**

   You'll need publicly accessible URLs to test. Options:

   **Option A: Use GitHub raw URLs (if you have test data)**
   ```bash
   # If you have test files in your repo
   curl -X POST https://white-agent.onrender.com/run \
     -H "Content-Type: application/json" \
     -d '{
       "context_url": "https://raw.githubusercontent.com/YOUR_USERNAME/white-agent-a2a/main/inputs/test_1/context.txt",
       "data_url": "https://raw.githubusercontent.com/YOUR_USERNAME/white-agent-a2a/main/inputs/test_1/data.csv",
       "mode": "auto"
     }'
   ```

   **Option B: Use the interactive API docs**
   - Go to `https://white-agent.onrender.com/docs`
   - Click on `POST /run`
   - Click "Try it out"
   - Fill in your URLs
   - Click "Execute"

---

## Part 4: Keep Service Alive (Optional)

Since Render free tier spins down after 15 minutes of inactivity, set up a keep-alive ping.

### Step 13: Set Up Free Cron Job

1. **Go to https://cron-job.org/en/signup/**

2. **Create free account:**
   - Enter email and password
   - Verify email

3. **Create new cron job:**
   - Dashboard → **"Create cronjob"**
   - **Title:** `White Agent Keep-Alive`
   - **URL:** `https://white-agent.onrender.com/health`
   - **Schedule:** Every 10 minutes
     - Pattern: `*/10 * * * *`
   - **Enable:** ✅ Enabled
   - Click **"Create cronjob"**

4. **Done!** Your service will stay warm.

---

## 🎉 You're Done!

Your White Agent A2A service is now:
- ✅ Deployed and running
- ✅ Accessible via HTTPS
- ✅ Connected to cloud storage
- ✅ Ready for A2A controller integration

### Your Service URL:
```
https://white-agent.onrender.com
```
(Replace with your actual URL)

### Next Steps:

1. **Register with A2A Controller:**
   ```python
   {
     "agent_name": "white-agent",
     "endpoint": "https://white-agent.onrender.com/run",
     "health_check": "https://white-agent.onrender.com/health"
   }
   ```

2. **Monitor your service:**
   - Render dashboard: https://dashboard.render.com
   - View logs, metrics, and deployment history

3. **Update your agent:**
   ```bash
   git add .
   git commit -m "Update agent"
   git push
   # Render will auto-deploy!
   ```

---

## 📊 Summary of What You Created

| Service | What It Does | Cost |
|---------|-------------|------|
| **Cloudflare R2** | Stores analysis outputs | $0 (10GB free) |
| **Render.com** | Runs your HTTP service | $0 (750 hrs/month) |
| **Gemini API** | Powers LLM analysis | $0 (free tier) |
| **Cron-job.org** | Keeps service alive | $0 |
| **Total** | Full production deployment | **$0/month** |

---

## 🆘 Troubleshooting

### Build failed on Render
- Check logs in Render dashboard
- Verify Dockerfile exists in repo
- Make sure you pushed all files to GitHub

### "Storage not configured" error
- Verify all 5 S3 environment variables are set in Render
- Check for typos in variable names
- Ensure R2 bucket name matches `S3_BUCKET` value

### "Service Unavailable" after 15 min
- Cold start is normal on free tier (~30 seconds)
- Set up cron job (Step 13) to keep it warm
- Or upgrade to paid tier ($7/month) for always-on

### Can't access uploaded files
- Verify R2 bucket has public access enabled
- Check `S3_PUBLIC_URL_BASE` is correct
- Test by visiting a generated URL directly

### Need help?
- Check Render logs: Dashboard → Logs tab
- Check service status: `curl https://your-service.onrender.com/health`
- Review [README_A2A.md](README_A2A.md) for detailed troubleshooting

---

## 💰 If You Exceed Free Tier

**Render Free Tier Limits:**
- 750 hours/month (enough for ~1 month if always on)
- If exceeded: Service pauses until next month

**Solutions:**
1. **Accept the pause** - Service resumes next month
2. **Upgrade to Starter** - $7/month for unlimited hours
3. **Use multiple free services** - Deploy to Railway/Fly.io as backup

**R2 Free Tier Limits:**
- 10GB storage
- 1M Class A operations/month
- Very hard to exceed for typical usage

---

**🎊 Congratulations! Your A2A service is live!**
