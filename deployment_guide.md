# Deployment Guide

## 🛑 Critical: Backend Deployment Warning

You asked about deploying the full stack to Vercel. Here is the recommendation:

**✅ Frontend:** Deploy to **Vercel**.
**❌ Backend:** Do **NOT** deploy to Vercel (yet).

### The Reason
Your backend currently uses **SQLite** (`test.db`).
- Vercel functions are "serverless" and ephemeral.
- **Every time your app restarts or sleeps (which is often), your database file will be deleted/reset.**
- You will lose all users, requests, and data immediately.

---

## 🚀 Recommended Strategy

### 1. Frontend (Vercel)
The frontend is perfect for Vercel.
1.  Push code to GitHub.
2.  Import project in Vercel.
3.  **Important:** Set the Environment Variable in Vercel settings:
    -   `VITE_API_BASE_URL`: [Your URL from Step 2]

### 2. Backend (Options)

#### Option A: The "Easiest" (Render/Railway)
Deploy the backend to a service that supports persistent disks or standard servers.
-   **Services:** [Render](https://render.com), [Railway](https://railway.app).
-   **Note:** You must enable a "Persistent Disk" if you want to keep using SQLite safely, otherwise you still risk data loss on redeploys.

#### Option B: The "Pro" Way (Switch to Postgres)
If you switch from SQLite to a Cloud Postgres database, you **can** deploy the backend to Vercel (or anywhere else) safely.
1.  Get a free database from [Supabase](https://supabase.com) or [Neon](https://neon.tech).
2.  Update your `.env`: `DATABASE_URL=postgres://user:pass@host...`
3.  Deploy backend to Vercel.

---

## Decision
- If this is just a **demo** and you don't care about data persisting purely, you *can* deploy to Render (free tier) and accept that data might wipe on redeploy.
- If you want a **real app**, switch to Postgres.
