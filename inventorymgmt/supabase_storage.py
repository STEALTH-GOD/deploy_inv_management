import os
import logging
from io import BytesIO
from django.conf import settings
from urllib.parse import quote
import requests

# Conditional imports for optional dependencies
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """Handle image uploads to Supabase cloud storage using REST API"""
    
    def __init__(self):
        # Get credentials from Django settings
        self.supabase_url = settings.SUPABASE_URL
        # Use Service Role Key for uploads (has full permissions)
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        
        print(f"\n🔧 Supabase Configuration:")
        print(f"  URL: {self.supabase_url}")
        print(f"  Bucket: {self.bucket_name}")
        print(f"  Using: {'Service Role Key' if settings.SUPABASE_SERVICE_ROLE_KEY else 'Anon Key'}")
        print(f"  Key configured: {'✓' if self.supabase_key else '✗'}\n")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured in Django settings")
            self.client = None
        else:
            # We'll use REST API directly instead of SDK
            self.client = True  # Flag to indicate we're ready to use REST API
            print("✅ Supabase REST API ready\n")
    
    def upload_image(self, image_file, filename):
        """
        Upload image to Supabase using REST API and return public URL
        
        Args:
            image_file: Django UploadedFile object
            filename: Desired filename in Supabase
            
        Returns:
            Public URL of the uploaded image or None if failed
        """
        if not self.client:
            logger.error("Supabase not configured")
            print("❌ Supabase not configured")
            return None
        
        try:
            # Reset file pointer to beginning
            image_file.seek(0)
            
            # Read image file data
            image_data = image_file.read()
            print(f"\n📤 Uploading image to Supabase:")
            print(f"  Filename: {filename}")
            print(f"  Bucket: {self.bucket_name}")
            print(f"  File size: {len(image_data)} bytes")
            
            # Build the correct REST API endpoint for file upload
            # Format: https://projecturl.supabase.co/storage/v1/object/bucketname/filename
            upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            
            # Prepare headers with authorization
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "image/jpeg"
            }
            
            print(f"  Upload URL: {upload_url}")
            print(f"  Using anon key for public upload...")
            
            # Upload using REST API
            response = requests.post(
                upload_url,
                data=image_data,
                headers=headers
            )
            
            print(f"  Upload response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                # Construct public URL
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
                print(f"  ✅ Public URL: {public_url}\n")
                logger.info(f"Image uploaded successfully: {public_url}")
                return public_url
            else:
                error_msg = response.text
                print(f"  ❌ Upload failed: {response.status_code}")
                print(f"  Error: {error_msg}\n")
                
                if "row-level security" in error_msg.lower():
                    print("  💡 TIP: Your Supabase bucket has RLS enabled.")
                    print("     Go to Storage → inv_management → Policies")
                    print("     Either disable RLS or add a policy to allow public uploads.\n")
                
                logger.error(f"Upload failed: {response.status_code} - {error_msg}")
                return None
            
        except Exception as e:
            print(f"  ❌ Error uploading image: {str(e)}\n")
            logger.error(f"Error uploading image to Supabase: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_image(self, filename):
        """Delete image from Supabase using REST API"""
        if not self.client:
            return False
        
        try:
            delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}"
            }
            
            response = requests.delete(delete_url, headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info(f"Image deleted: {filename}")
                return True
            else:
                logger.error(f"Error deleting image: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return False
    
    def get_public_url(self, filename):
        """Get public URL for an image"""
        if not self.client:
            return None
        
        try:
            url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
            return url
        except Exception as e:
            logger.error(f"Error getting public URL: {str(e)}")
            return None
    


# Singleton instance
_supabase_storage = None

def get_supabase_storage():
    """Get or create Supabase storage instance"""
    global _supabase_storage
    if _supabase_storage is None:
        _supabase_storage = SupabaseStorage()
    return _supabase_storage