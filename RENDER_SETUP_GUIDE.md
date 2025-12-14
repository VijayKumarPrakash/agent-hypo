# Render Setup Guide - Step by Step

Complete guide for setting up your White Agent on Render.com

---

## Prerequisites

Before starting, make sure you have:
- ✅ Cloudflare R2 bucket created (`white-agent`)
- ✅ R2 API tokens (Access Key ID + Secret Access Key)
- ✅ R2 Account ID and URLs
- ✅ Gemini API key (optional)
- ✅ Code pushed to GitHub

---

## Step 1: Sign Up for Render

1. **Go to:** https://render.com

2. **Click:** "Get Started" button

3. **Choose:** "Sign up with GitHub" (easiest option)

4. **Authorize:** Allow Render to access your GitHub account

5. **Done!** You're in the Render dashboard

---

## Step 2: Create New Web Service

1. **In Render dashboard:**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

2. **Connect repository:**
   - You'll see a list of your GitHub repos
   - Find: **`cs294/agent-hypo`** (or your repo name)
   - Click **"Connect"**

   **Don't see your repo?**
   - Click "Configure account" link
   - Grant Render access to the specific repo
   - Refresh the page

---

## Step 3: Configure Service Settings

You'll see a form with many fields. Fill them in as follows:

### Basic Settings:

**Name:**
```
white-agent
```
(This becomes part of your URL: `white-agent.onrender.com`)

**Region:**
```
Oregon (US West)
```
(Or choose closest to your location)

**Branch:**
```
main
```
(Or whatever your default branch is)

**Root Directory:**
```
(leave empty)
```
(Your Dockerfile is in the root, so no need to specify)

---

### Build Settings:

**Environment:**
```
Docker
```
⚠️ **IMPORTANT:** Must select "Docker", not "Python"!

**Dockerfile Path:**
```
(auto-detected - leave as is)
```
Should show: `./Dockerfile`

**Docker Command:**
```
(leave empty)
```
Render will use the CMD from your Dockerfile automatically

---

### Instance Settings:

**Instance Type:**
```
Free
```
(Gives you 750 hours/month - enough for 24/7)

---

### Advanced Settings (Optional):

**Auto-Deploy:**
```
Yes (default)
```
Leave this enabled - Render will auto-deploy when you push to GitHub

**Health Check Path:**
```
/health
```
(Optional but recommended)

---

## Step 4: Add Environment Variables

**BEFORE clicking "Create Web Service":**

1. **Scroll down** to "Environment Variables" section

2. **Click "Add Environment Variable"**

3. **Add each of these 6 variables:**

### Variable 1: S3_BUCKET
```
Key:   S3_BUCKET
Value: white-agent
```

### Variable 2: S3_ACCESS_KEY_ID
```
Key:   S3_ACCESS_KEY_ID
Value: <paste your R2 Access Key ID>
```
(From Cloudflare R2 API token - looks like: `f1a2b3c4d5e6f7g8h9i0`)

### Variable 3: S3_SECRET_ACCESS_KEY
```
Key:   S3_SECRET_ACCESS_KEY
Value: <paste your R2 Secret Access Key>
```
(From Cloudflare R2 API token - longer, looks like: `a1b2c3d4e5f6...`)

### Variable 4: S3_ENDPOINT_URL
```
Key:   S3_ENDPOINT_URL
Value: https://<your-account-id>.r2.cloudflarestorage.com
```
(Replace `<your-account-id>` with your actual Cloudflare account ID)

### Variable 5: S3_PUBLIC_URL_BASE
```
Key:   S3_PUBLIC_URL_BASE
Value: https://pub-<your-subdomain>.r2.dev
```
(From R2 bucket settings - the R2.dev URL)

### Variable 6: GEMINI_API_KEY (Recommended)
```
Key:   GEMINI_API_KEY
Value: <paste your Gemini API key>
```
(From Google AI Studio - starts with `AIza...`)

---

## Step 5: Create the Service

1. **Review all settings** one more time:
   - Environment: `Docker` ✓
   - All 6 environment variables added ✓

2. **Click:** "Create Web Service" button at the bottom

3. **Wait for build:**
   - Render will clone your repo
   - Build Docker image
   - Start the container
   - Takes ~3-5 minutes

---

## Step 6: Monitor the Build

You'll see a logs screen showing:

```
==> Cloning from GitHub...
==> Building Docker image...
==> Step 1/10 : FROM python:3.11-slim
==> Step 2/10 : WORKDIR /build
...
==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

**Watch for:**
- ✅ "Build successful" message
- ✅ "Your service is live" message
- ❌ Any errors (check logs if build fails)

---

## Step 7: Get Your Service URL

Once deployed:

1. **At the top of the page**, you'll see your service URL:
   ```
   https://white-agent.onrender.com
   ```
   (Or similar - might have random characters if name was taken)

2. **Copy this URL** - you'll need it for testing

---

## Step 8: Test Your Deployment

### Test 1: Health Check

**In browser, visit:**
```
https://white-agent.onrender.com/health
```

**Or use curl:**
```bash
curl https://white-agent.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_available": true,
  "storage_configured": true
}
```

✅ If you see this, **deployment successful!**

---

### Test 2: API Documentation

**In browser, visit:**
```
https://white-agent.onrender.com/docs
```

You should see interactive Swagger UI documentation.

**Try:**
1. Click on `GET /health`
2. Click "Try it out"
3. Click "Execute"
4. See the response

---

### Test 3: Run Analysis (Optional)

Only if you have publicly accessible test data:

```bash
curl -X POST https://white-agent.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://your-url.com/context.txt",
    "data_url": "https://your-url.com/data.csv",
    "mode": "auto"
  }'
```

---

## 🆘 Troubleshooting

### Build Failed

**Check logs for errors:**
- Render dashboard → Your service → Logs tab
- Look for specific error messages

**Common issues:**
- Missing Dockerfile: Make sure it's in repo root
- Git push failed: Verify code is pushed to GitHub
- Wrong branch: Check you selected the right branch

**Solution:**
- Fix the issue in your code
- Push to GitHub
- Render will auto-rebuild

---

### "Storage not configured" in Health Check

**Problem:** One or more S3_* variables are missing or incorrect

**Solution:**
1. Go to Render dashboard → Your service
2. Click "Environment" tab (left sidebar)
3. Verify all 5 S3_* variables are present
4. Check for typos in variable names
5. Click "Save Changes"
6. Service will auto-redeploy

---

### Service Takes Forever to Respond

**First request after 15 min inactivity:**
- Free tier spins down after inactivity
- First request "wakes it up" (~30 seconds)
- Subsequent requests are fast

**Solution:**
- This is normal behavior
- Set up keep-alive cron job (optional)
- Or upgrade to paid tier ($7/month for always-on)

---

### Can't Find Environment Variables Section

**During initial setup:**
- It's in the "Create Web Service" form
- Scroll down past all other settings
- Should be near the bottom

**After service is created:**
- Render dashboard → Your service
- Click "Environment" tab in left sidebar
- Add/edit variables there

---

### Build Succeeds But Service Won't Start

**Check startup logs:**
- Render dashboard → Logs tab
- Look for Python errors or missing dependencies

**Common causes:**
- Missing dependencies in requirements.txt
- Import errors
- Port binding issues (should use PORT env var)

**Solution:**
- Fix the code issue
- Push to GitHub
- Render auto-rebuilds

---

## 🔄 Making Updates

After initial deployment, to update your service:

```bash
# Make changes to your code
git add .
git commit -m "Update service"
git push

# Render automatically:
# 1. Detects the push
# 2. Rebuilds Docker image
# 3. Deploys new version
# 4. Takes ~2-3 minutes
```

**Watch deployment:**
- Render dashboard → Your service → Logs
- See real-time build progress

---

## 📊 Monitoring Your Service

### View Logs:
- Render dashboard → Your service → Logs tab
- Shows deployment logs and runtime logs
- Helpful for debugging

### Check Metrics:
- Render dashboard → Your service → Metrics tab
- See CPU, memory, request count
- Monitor free tier usage

### Service Settings:
- Render dashboard → Your service → Settings tab
- Change environment, plan, etc.
- Suspend or delete service

---

## 💡 Pro Tips

1. **First deployment takes longest** (~5 min)
   - Subsequent deployments faster (~2-3 min)

2. **Check "Events" tab** for deployment history
   - See all past deployments
   - View what triggered each build

3. **Use custom domain** (optional)
   - Settings → Custom Domains
   - Add your own domain instead of .onrender.com

4. **Set up notifications**
   - Settings → Notifications
   - Get emails for deploy failures

5. **Environment groups** (for multiple services)
   - Share env vars across services
   - Useful if you deploy multiple agents

---

## ✅ Success Checklist

Your deployment is successful when:

- [x] Build completes without errors
- [x] Service shows "Live" status
- [x] `/health` endpoint returns `"status": "healthy"`
- [x] `/docs` shows Swagger UI
- [x] `"storage_configured": true` in health check
- [x] `"llm_available": true` (if you set GEMINI_API_KEY)

---

## 🎉 You're Done!

Your White Agent A2A service is now:
- ✅ Running on Render
- ✅ Accessible via HTTPS
- ✅ Connected to Cloudflare R2
- ✅ Using Gemini for LLM analysis
- ✅ Auto-deploying from GitHub

**Service URL:** `https://white-agent.onrender.com`

**Next steps:**
- Register with A2A controller
- Set up keep-alive (optional)
- Monitor in Render dashboard

---

**Questions?** Check [YOUR_DEPLOYMENT_SETUP.md](YOUR_DEPLOYMENT_SETUP.md) for quick reference!
