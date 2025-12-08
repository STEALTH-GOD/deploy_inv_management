# Render Deployment Guide

## Overview

This guide will help you deploy your Django Inventory Management App to Render with Supabase integration.

## Prerequisites

- Render account (https://render.com)
- GitHub repository with your code
- Supabase project with credentials
- PostgreSQL database (can be created by Render)

## Deployment Steps

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment files"
git push origin main
```

### 2. Connect GitHub to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Connect your GitHub account
5. Select your `django-Inv_Management_App` repository
6. Click **"Connect"**

### 3. Configure Web Service

**Name:** `django-inv-management`

**Branch:** `main`

**Runtime:** `Python 3`

**Build Command:**

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start Command:**

```bash
gunicorn djangoproject.wsgi:application --bind 0.0.0.0:$PORT
```

**Plan:** Standard (or your preferred plan)

### 4. Add Environment Variables

Click **"Environment"** and add these variables:

```
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_BUCKET_NAME=inv_management
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

### 5. Create Database (Optional)

If you don't have PostgreSQL:

1. Click **"Create PostgreSQL"**
2. Select **"Standard"** plan
3. Copy the connection string and use it as `DATABASE_URL`

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Monitor the deployment in the **"Logs"** tab
4. Once complete, your app will be live at `https://your-app-name.onrender.com`

## File Reference

### `render.yaml`

Infrastructure as Code configuration for Render. Defines:

- Web service configuration
- Build and start commands
- Environment variables
- Database setup

### `Procfile`

Process file for Render. Specifies:

- `web`: How to start the web server
- `release`: Migrations to run before deployment

### `.renderignore`

Files to exclude from deployment (similar to .gitignore for Render)

### `requirements.txt`

All Python dependencies needed for the app

## Post-Deployment Setup

### 1. Create Admin User

```bash
python manage.py createsuperuser
```

(Or access Render shell: click "Shell" in your web service)

### 2. Test Application

- Visit your Render URL
- Try adding a product with an image
- Verify image uploads to Supabase
- Check that image URL is stored in PostgreSQL

### 3. Configure Supabase Bucket

1. Go to your Supabase project
2. Navigate to **Storage** → **inv_management** bucket
3. Ensure bucket is **Public** and allows uploads
4. Optionally configure RLS policies for security

## Troubleshooting

### "Import Error: No module named..."

- Check `requirements.txt` has all dependencies
- Ensure `pip install -r requirements.txt` runs successfully

### "ModuleNotFoundError: No module named 'dotenv'"

- Add `python-dotenv` to requirements.txt (already there)

### "ProgrammingError at /..."

- Migrations didn't run
- Check build command includes: `python manage.py migrate`

### Images not uploading

- Verify Supabase credentials in environment variables
- Check bucket policies allow uploads
- Ensure SERVICE_ROLE_KEY has proper permissions

### SSL Certificate Issues

- Wait 5-10 minutes for Let's Encrypt certificate
- Ensure `SECURE_SSL_REDIRECT=True` is set
- Check `ALLOWED_HOSTS` includes your Render domain

## Monitoring & Maintenance

### View Logs

1. Click on your web service
2. Select **"Logs"** tab
3. Monitor real-time application logs

### Update Code

Simply push to GitHub and Render automatically redeploys

### Database Management

Use Render's PostgreSQL dashboard or connect via psql:

```bash
psql $DATABASE_URL
```

## Production Security Checklist

- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` is strong and unique
- ✅ `SECURE_SSL_REDIRECT=True`
- ✅ `SESSION_COOKIE_SECURE=True`
- ✅ `CSRF_COOKIE_SECURE=True`
- ✅ Database credentials in environment variables (not in code)
- ✅ Supabase keys in environment variables (not in code)
- ✅ ALLOWED_HOSTS configured correctly

## Rollback

If deployment fails:

1. Go to **"Deploys"** tab
2. Click on a previous successful deployment
3. Click **"Redeploy"**

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Supabase Docs: https://supabase.com/docs

Happy Deploying! 🚀
