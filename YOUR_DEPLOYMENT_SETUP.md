# Your Deployment Setup - Quick Reference

This is YOUR specific deployment configuration.

---

## 🎯 Your Chosen Stack

✅ **Storage:** Cloudflare R2 (free tier)
✅ **Hosting:** Render.com (free tier)
✅ **LLM:** Gemini API (free tier)
✅ **Code:** Existing GitHub repo (cs294/agent-hypo)

**Total Cost:** $0/month

---

## 📋 Deployment Checklist

Follow [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md) - it's been updated for your setup!

### Quick Overview:

1. ✅ **Accounts** (15 min)
   - GitHub (you already have)
   - Cloudflare (sign up)
   - Render (sign up with GitHub)
   - Google (for Gemini API key)

2. ✅ **Cloudflare R2** (10 min)
   - Create bucket: `white-agent`
   - Enable public access
   - Generate API tokens
   - Save: Access Key, Secret Key, Account ID, R2.dev URL

3. ✅ **Push to GitHub** (2 min)
   ```bash
   cd /Users/vkp/dev/cs294/agent-hypo
   git add .
   git commit -m "Add A2A service deployment"
   git push
   ```

4. ✅ **Deploy on Render** (10 min)
   - Connect existing repo: `cs294/agent-hypo`
   - Environment: `Docker`
   - **Start Command: LEAVE EMPTY**
   - Add 6 environment variables

5. ✅ **Test** (5 min)
   - Health check
   - API docs
   - Run analysis

---

## 🔑 Environment Variables for Render

When you get to Render setup, add these **6 variables** in the Environment tab:

### Required (from Cloudflare R2):

```
S3_BUCKET
Value: white-agent

S3_ACCESS_KEY_ID
Value: <from R2 API token>

S3_SECRET_ACCESS_KEY
Value: <from R2 API token>

S3_ENDPOINT_URL
Value: https://<account-id>.r2.cloudflarestorage.com

S3_PUBLIC_URL_BASE
Value: https://pub-<subdomain>.r2.dev
```

### Recommended (from Google):

```
GEMINI_API_KEY
Value: <from Google AI Studio>
```

---

## 🚀 Render Configuration

When creating web service on Render:

| Setting | Value |
|---------|-------|
| **Name** | `white-agent` |
| **Repository** | Your existing: `cs294/agent-hypo` |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Environment** | `Docker` |
| **Start Command** | **(leave empty - auto-detected)** |
| **Plan** | `Free` |

**Why leave Start Command empty?**
- Your Dockerfile already has the command
- Render auto-detects it
- No need to specify manually

---

## 📝 What Happens in Render

1. **First deployment:**
   - Render clones your GitHub repo
   - Builds Docker image from your Dockerfile
   - Starts container with CMD from Dockerfile
   - Takes ~3-5 minutes

2. **Future updates:**
   - Just `git push` to GitHub
   - Render auto-rebuilds and redeploys
   - Takes ~2-3 minutes

---

## 🔍 How to Get Your Credentials

### Cloudflare R2:

**Access Key ID & Secret:**
1. Cloudflare dashboard → R2 → Manage R2 API Tokens
2. Create API Token
3. Name: `white-agent-access`
4. Permissions: Object Read & Write
5. **Save both keys immediately!**

**Account ID:**
- Look at URL: `dash.cloudflare.com/[ACCOUNT-ID]/r2`
- Or: R2 bucket → Settings

**R2.dev URL:**
- R2 bucket → Settings → Public Access
- Enable R2.dev subdomain
- Copy the URL shown

### Gemini API Key:

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Create API Key → Create API key in new project
4. Copy and save immediately

---

## ✅ Testing Your Deployment

After Render deployment completes:

### 1. Health Check
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

### 2. API Documentation
Open in browser:
```
https://white-agent.onrender.com/docs
```

### 3. Test Analysis
Use the interactive docs at `/docs` or:
```bash
curl -X POST https://white-agent.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "YOUR_CONTEXT_URL",
    "data_url": "YOUR_DATA_URL",
    "mode": "auto"
  }'
```

---

## 🆘 Common Issues & Solutions

### "Storage not configured" error
- Check all 5 S3_* variables are set in Render
- Verify no typos in variable names
- Confirm R2 bucket exists

### "Build failed" in Render
- Check Render logs for specific error
- Verify all files pushed to GitHub
- Ensure Dockerfile exists in repo root

### "Service Unavailable" after 15 min
- Normal for free tier (cold start)
- First request takes ~30 seconds
- Set up keep-alive cron job to prevent

### Can't access uploaded files
- Enable public access on R2 bucket
- Verify S3_PUBLIC_URL_BASE is correct
- Check R2.dev subdomain is enabled

---

## 📊 Your Service URLs

After deployment, save these:

```
Service URL: https://white-agent.onrender.com

Health Check: https://white-agent.onrender.com/health

API Docs: https://white-agent.onrender.com/docs

Render Dashboard: https://dashboard.render.com

Cloudflare R2: https://dash.cloudflare.com
```

---

## 🔄 Updating Your Service

To deploy changes:

```bash
cd /Users/vkp/dev/cs294/agent-hypo

# Make your changes to code

git add .
git commit -m "Your update message"
git push

# Render automatically rebuilds and deploys!
# Watch progress at: https://dashboard.render.com
```

---

## 💡 Pro Tips

1. **Save credentials securely**
   - Use password manager
   - Never commit .env to git
   - Keep Secret Access Key private

2. **Monitor your usage**
   - Render dashboard shows hours used
   - R2 dashboard shows storage/operations
   - Both have free tier limits

3. **Set up keep-alive** (optional)
   - Use cron-job.org
   - Ping `/health` every 10 minutes
   - Prevents cold starts

4. **Check logs**
   - Render dashboard → Logs tab
   - Shows deployment and runtime logs
   - Helpful for debugging

---

## 📞 Need Help?

- **Setup issues:** See [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md)
- **Technical details:** See [README_A2A.md](README_A2A.md)
- **Deployment steps:** See [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)

---

**Ready to deploy?** Start with [ACCOUNT_SETUP_CHECKLIST.md](ACCOUNT_SETUP_CHECKLIST.md)! ✨
