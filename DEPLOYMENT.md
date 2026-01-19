# Deployment Guide - Phase 3 Todo Application

## Environment Configuration Status

### ✅ Current Setup (Development)

**Frontend (.env.local):**
- Connected to backend: `http://localhost:8000`
- All authentication flows working
- Data saves to Neon PostgreSQL

**Backend (.env):**
- Neon PostgreSQL database configured
- JWT authentication enabled
- Cohere AI agent integrated

## Deployment Steps

### 1. Backend Deployment (Vercel/Render/Railway)

**Option A: Vercel**
```bash
cd backend
vercel
```

**Option B: Render**
1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables to Add:**
- `DATABASE_URL` (Your Neon PostgreSQL URL - already configured)
- `JWT_SECRET` (Already in .env)
- `BETTER_AUTH_SECRET` (Already in .env)
- `COHERE_API_KEY` (Already in .env)
- `ENV=production`
- `DEBUG=false`

### 2. Frontend Deployment (Vercel)

```bash
cd frontend
vercel
```

**Update Environment Variables:**
1. Go to Vercel Project Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`

### 3. Database (Neon PostgreSQL)

**Already Configured! ✅**
- Your Neon database URL is in `backend/.env`
- Connection string format: `postgresql://username:password@your-host.neon.tech/neondb?sslmode=require`
- This will work for both development and production

### 4. Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed with correct `NEXT_PUBLIC_API_URL`
- [ ] Test registration: Create new account
- [ ] Test login: Sign in with credentials
- [ ] Test tasks: Add, update, delete tasks
- [ ] Test AI chat: Send messages to chatbot
- [ ] Verify data persists in Neon database

## Current Configuration Summary

### Frontend Environment
```
NEXT_PUBLIC_API_URL=http://localhost:8000 (local)
                   =https://your-backend.vercel.app (production)
```

### Backend Environment
```
# Copy these from your backend/.env file
DATABASE_URL=postgresql://username:password@your-db-host.neon.tech/neondb?sslmode=require
JWT_SECRET=your_jwt_secret_here_use_openssl_rand_hex_32
BETTER_AUTH_SECRET=your_better_auth_secret_here_use_openssl_rand_hex_32
COHERE_API_KEY=your_cohere_api_key_from_dashboard
ENV=development (change to production)
DEBUG=true (change to false)
```

## Authentication Flow

1. User registers/logs in → Backend `/api/auth/register` or `/api/auth/login`
2. Backend validates credentials → Returns JWT token
3. Frontend stores token in localStorage
4. All API requests include `Authorization: Bearer <token>` header
5. Data saves to Neon PostgreSQL database

**This is exactly how Phase 2 worked! ✅**

## Quick Deployment Commands

### Deploy to Vercel (Recommended)

**Backend:**
```bash
cd backend
vercel --prod
# Note the deployment URL
```

**Frontend:**
```bash
cd frontend
# Update .env.local with backend URL
vercel env add NEXT_PUBLIC_API_URL production
# Paste your backend URL when prompted
vercel --prod
```

### Verify Deployment

```bash
# Test backend health
curl https://your-backend.vercel.app/health

# Test frontend
curl https://your-frontend.vercel.app
```

## Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
- Ensure backend allows CORS from frontend domain

### Database connection fails
- Verify `DATABASE_URL` is correct in backend environment
- Check Neon dashboard for connection issues
- Ensure connection string includes `?sslmode=require&channel_binding=require`

### Authentication not working
- Verify `JWT_SECRET` matches between dev and prod
- Check token is being saved to localStorage
- Inspect network tab for 401/403 errors

## Support

For issues, check:
1. Vercel deployment logs
2. Browser console (F12)
3. Network tab for API errors
4. Neon dashboard for database issues
