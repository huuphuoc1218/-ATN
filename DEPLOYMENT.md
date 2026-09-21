# Deployment (Option 1): Render + Vercel

This guide deploys:

- Backend (FastAPI) on Render
- Database (PostgreSQL) on Render
- Frontend (Vue + Vite) on Vercel

Image storage choices:

- Option A: Render Persistent Disk (`UPLOADS_ROOT_DIR`) for local file storage.
- Option B (recommended free tier): Cloudinary storage, save returned URL in PostgreSQL.

## Prerequisites

- Source code already pushed to GitHub
- Render account
- Vercel account

## A. Deploy Backend + PostgreSQL on Render

1. Create PostgreSQL on Render

- In Render dashboard, choose New -> PostgreSQL.
- Keep plan that matches your budget.
- After creation, copy DB connection values.

2. Create Backend Web Service

- Choose New -> Web Service.
- Connect your GitHub repo.
- Configure:
  - Root Directory: backend
  - Build Command: pip install -r requirements.txt
  - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

3. Create Persistent Disk for Uploads (required for avatars/court images)

- In Render backend service, open Disks -> Add Disk.
- Mount Path: /var/data/uploads
- Size: choose based on your image volume.
- This prevents uploaded files from disappearing after restart/redeploy.

4. Set Backend Environment Variables
   Use values from backend/.env.example:

- DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
- SECRET_KEY (must be strong and unique)
- ALGORITHM=HS256
- ACCESS_TOKEN_EXPIRE_MINUTES=30
- DEBUG=False
- BACKEND_PUBLIC_BASE_URL=https://<your-backend>.onrender.com
- BACKEND_CORS_ORIGINS=https://<your-frontend>.vercel.app,http://localhost:5173
- UPLOADS_ROOT_DIR=/var/data/uploads
- CLOUDINARY_CLOUD_NAME=<your-cloud-name>
- CLOUDINARY_API_KEY=<your-api-key>
- CLOUDINARY_API_SECRET=<your-api-secret>
- CLOUDINARY_FOLDER=pickleball
- SMTP\_\* (optional, for emails)

5. Verify Backend

- Open https://<your-backend>.onrender.com/health
- Expect: {"status":"healthy"}
- Open docs: https://<your-backend>.onrender.com/docs

## B. Deploy Frontend on Vercel

1. Import Project

- In Vercel, choose Add New -> Project.
- Select the same GitHub repository.
- Set Root Directory to frontend.

2. Configure Build

- Build Command: npm run build
- Output Directory: dist

3. Set Frontend Environment Variable
   Use frontend/.env.production.example:

- VITE_API_BASE_URL=https://<your-backend>.onrender.com/api

4. Deploy and verify page loads.

## C. Final CORS Sync

After frontend has final URL:

1. Copy exact Vercel domain (or custom domain).
2. Update backend env BACKEND_CORS_ORIGINS with that domain.
3. Redeploy backend.

## D. Production Checklist

- DEBUG=False on backend
- Strong SECRET_KEY
- DB password not default
- Frontend points to production API URL
- CORS includes only allowed domains
- Login/register and booking flow tested

## E. Common Issues and Fixes

1. CORS error in browser

- Cause: frontend domain missing in BACKEND_CORS_ORIGINS
- Fix: add exact domain and redeploy backend

2. Frontend still calls localhost API

- Cause: VITE_API_BASE_URL not set in Vercel
- Fix: set env and redeploy frontend

3. 500 from backend after deploy

- Cause: database env values incorrect
- Fix: verify DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD

4. Email not sent

- Cause: SMTP env not configured
- Fix: set SMTP\_\* variables or disable email-dependent flows

5. Uploaded images disappear after restart/redeploy

- Cause: files were stored in container local filesystem (ephemeral).
- Fix: mount a Render Persistent Disk and set UPLOADS_ROOT_DIR=/var/data/uploads.
- Note: images already lost from previous restarts must be uploaded again.

6. Want fully free image storage without server disk

- Use Cloudinary free plan and set CLOUDINARY_* env vars.
- Backend will upload avatars/court images/advertisement images to Cloudinary and store returned HTTPS URL in DB.
- You can leave UPLOADS_ROOT_DIR empty when using only Cloudinary.
