# Supabase Integration Setup Guide

## Overview

Your Django Inventory Management App now uses Supabase for cloud-based image storage. Images are uploaded to Supabase's cloud storage, and only the public URLs are stored in PostgreSQL.

## Configuration Files Modified

### 1. **djangoproject/settings.py**

- Now uses environment variables from `.env` file
- Added Supabase configuration
- Database credentials loaded from `.env`
- Security settings configured from environment variables

### 2. **inventorymgmt/models.py**

- Changed `image` field from `ImageField` to `URLField`
- Updated signals to delete images from Supabase instead of local filesystem
- Images now store Supabase CDN URLs in the database

### 3. **inventorymgmt/forms.py**

- Enhanced `StockCreateForm` to handle Supabase uploads
- Added image validation (file size, format)
- Images are automatically uploaded to Supabase during form submission
- Public URL is stored in the database

### 4. **inventorymgmt/supabase_storage.py**

- Now reads credentials from Django settings instead of environment variables
- Improved error handling and logging

### 5. **inventorymgmt/migrations/0006_alter_stock_image.py**

- New migration to change the `image` field from ImageField to URLField

## Environment Variables (.env)

Make sure these variables are set in your `.env` file:

```env
# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL on Railway)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_BUCKET_NAME=inv_management

# Security (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
```

## How It Works

### Image Upload Flow

1. User selects an image when adding/updating a product
2. Form validates the image (size, format)
3. Image is uploaded to Supabase cloud storage
4. Public URL from Supabase is returned
5. Public URL is stored in PostgreSQL (not the image file)
6. User can view the image via the public URL

### Image Deletion Flow

1. When a product is deleted, the associated Supabase URL is extracted
2. Image is deleted from Supabase cloud storage
3. Product record is deleted from database

### Benefits

✅ **Scalable**: Images hosted on Supabase CDN  
✅ **Fast**: CDN distribution for faster image loading  
✅ **Reliable**: Cloud backup and redundancy  
✅ **Cost-effective**: Database only stores URLs, not large binary files  
✅ **Deployment-friendly**: No need to handle local image directories

## Running Migrations

After pulling this code, run:

```bash
python manage.py migrate
```

This will apply the migration to change the image field structure in the database.

## Testing Image Upload

1. Go to the "Add Item" page
2. Fill in the product details
3. Select an image file (max 5MB)
4. Submit the form
5. The image should be uploaded to Supabase and displayed in the product details

## Troubleshooting

### Issue: "Supabase client not initialized"

- Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correctly set in `.env`
- Ensure `.env` file is loaded before Django starts

### Issue: "Failed to upload image to cloud storage"

- Verify Supabase bucket exists and is named correctly
- Check that bucket policies allow public uploads
- Ensure the API keys have appropriate permissions

### Issue: Images not displaying

- Check the Supabase URL in the database
- Verify bucket is set to public access in Supabase
- Check browser console for CORS errors

## Next Steps

1. **Update your templates** to reference the image URLs correctly
2. **Test the deployment** on your Railway environment
3. **Monitor Supabase storage** usage and optimize if needed
4. **Set up backup policies** for your PostgreSQL database

## Related Files

- `.env` - Environment configuration (keep secure!)
- `djangoproject/settings.py` - Django settings with env vars
- `inventorymgmt/forms.py` - Form handling with Supabase upload
- `inventorymgmt/supabase_storage.py` - Supabase client wrapper
- `requirements.txt` - All dependencies including `supabase` package
