# Backend Deployment Guide

## Frontend Already Deployed ✅
Your frontend is live at: **https://the-evolution-of-todo-phase3.vercel.app/**

Now let's deploy the backend!

---

## Option 1: Vercel (Recommended - Same as Frontend) 🚀

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy Backend

```bash
cd backend
vercel
```

**Follow the prompts:**
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name? **todo-phase3-backend** (or any name)
- Directory? **./backend** (should be auto-detected)
- Override settings? **N**

### Step 4: Add Environment Variables

After deployment, go to:
```
https://vercel.com/dashboard
→ Select your backend project
→ Settings
→ Environment Variables
```

Add these:
```
DATABASE_URL=postgresql://neondb_owner:npg_GY2qWnTC8LZs@ep-icy-grass-a1xwtkeh-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

JWT_SECRET=03c35c2b642050264b16b06f0d8c11629b62a1157b8497099e3745dc2a19d36b

BETTER_AUTH_SECRET=e6213e03da0dba5946c654a1e5d94fd919a5f748b07dbbcb332bc455fade9f54

COHERE_API_KEY=7fAl0Z1NA6vscDYtQ8K6CWlxq5U0PTxhlhZ4VvFZ

ENV=production

DEBUG=false
```

### Step 5: Redeploy

```bash
vercel --prod
```

**Your backend URL will be:** `https://todo-phase3-backend.vercel.app` (or similar)

---

## Option 2: Render (Alternative) 🎨

### Step 1: Create Account
Go to: https://render.com and sign up

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the repo: **The-Evolution-of-Todo-Phase3**
4. Configure:
   - **Name:** todo-phase3-backend
   - **Root Directory:** backend
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
In Render dashboard, add:
```
DATABASE_URL=postgresql://neondb_owner:npg_GY2qWnTC8LZs@ep-icy-grass-a1xwtkeh-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
JWT_SECRET=03c35c2b642050264b16b06f0d8c11629b62a1157b8497099e3745dc2a19d36b
BETTER_AUTH_SECRET=e6213e03da0dba5946c654a1e5d94fd919a5f748b07dbbcb332bc455fade9f54
COHERE_API_KEY=7fAl0Z1NA6vscDYtQ8K6CWlxq5U0PTxhlhZ4VvFZ
ENV=production
DEBUG=false
```

### Step 4: Deploy
Click "Create Web Service" - Render will auto-deploy!

**Your backend URL will be:** `https://todo-phase3-backend.onrender.com`

---

## Option 3: Railway (Another Alternative) 🚂

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login & Deploy
```bash
cd backend
railway login
railway init
railway up
```

### Step 3: Add Environment Variables
```bash
railway variables set DATABASE_URL="postgresql://..."
railway variables set JWT_SECRET="03c35c2b..."
railway variables set BETTER_AUTH_SECRET="e6213e03..."
railway variables set COHERE_API_KEY="7fAl0Z1NA6vscDYtQ8K6CWlxq5U0PTxhlhZ4VvFZ"
railway variables set ENV="production"
railway variables set DEBUG="false"
```

**Your backend URL will be:** `https://your-app.railway.app`

---

## After Backend Deployment ✅

### Update Frontend Environment Variable

1. Go to Vercel Dashboard
2. Select your frontend project: **the-evolution-of-todo-phase3**
3. Go to: Settings → Environment Variables
4. Update `NEXT_PUBLIC_API_URL` to your backend URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
   ```
5. Redeploy frontend:
   ```bash
   cd frontend
   vercel --prod
   ```

---

## Testing Deployment 🧪

### Test Backend Health
```bash
curl https://your-backend-url.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Test Frontend
Open: https://the-evolution-of-todo-phase3.vercel.app
- Try registering a new account
- Login
- Add a task
- Test AI chat

---

## Troubleshooting 🔧

### Backend won't start
- Check logs in Vercel/Render dashboard
- Verify all environment variables are set
- Check DATABASE_URL is correct

### CORS errors
- Make sure frontend URL is in `app/main.py` CORS config
- Currently set to: `https://the-evolution-of-todo-phase3.vercel.app`

### Database connection fails
- Verify DATABASE_URL includes `?sslmode=require`
- Check Neon dashboard for connection issues
- Make sure database allows connections from deployment platform

### AI chat not working
- Verify COHERE_API_KEY is valid
- Check Cohere dashboard for API limits
- Review backend logs for Cohere errors

---

## Files Ready for Deployment ✅

- ✅ `requirements.txt` - All dependencies listed
- ✅ `vercel.json` - Vercel configuration
- ✅ `app/main.py` - Entry point with CORS configured
- ✅ `.env.production.example` - Environment variables template
- ✅ CORS includes your Vercel frontend URL

---

## Quick Deploy Command (Vercel)

```bash
cd backend
vercel --prod
```

Then add environment variables in Vercel dashboard!

---

## Support

For issues:
1. Check deployment logs
2. Verify environment variables
3. Test `/health` endpoint
4. Check Neon database dashboard

**Good luck with deployment! 🚀**
