import os
import logging
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from supabase import create_client, Client
from urllib.parse import quote

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """Handle image uploads to Supabase cloud storage"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'product-images')
        
        print(f"\n🔧 Supabase Configuration:")
        print(f"  URL: {self.supabase_url}")
        print(f"  Bucket: {self.bucket_name}")
        print(f"  Key configured: {'✓' if self.supabase_key else '✗'}\n")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Supabase client initialized successfully\n")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}\n")
                self.client = None
    
    def upload_image(self, image_file, filename):
        """
        Upload image to Supabase and return public URL
        
        Args:
            image_file: Django UploadedFile object
            filename: Desired filename in Supabase
            
        Returns:
            Public URL of the uploaded image or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            # Read image file
            image_data = image_file.read()
            
            # Upload to Supabase
            file_path = f"{self.bucket_name}/{filename}"
            
            response = self.client.storage.from_(self.bucket_name).upload(
                file=image_data,
                path=filename,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Get public URL
            public_url = self.get_public_url(filename)
            logger.info(f"Image uploaded successfully: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading image to Supabase: {str(e)}")
            return None
    
    def delete_image(self, filename):
        """Delete image from Supabase"""
        if not self.client:
            return False
        
        try:
            self.client.storage.from_(self.bucket_name).remove([filename])
            logger.info(f"Image deleted: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return False
    
    def get_public_url(self, filename):
        """Get public URL for an image"""
        if not self.client:
            return None
        
        try:
            url = self.client.storage.from_(self.bucket_name).get_public_url(filename)
            return url
        except Exception as e:
            logger.error(f"Error getting public URL: {str(e)}")
            return None
    
    def upload_and_get_url(self, image_file, filename):
        """Upload image and return public URL"""
        if not self.client:
            logger.error("Supabase not configured")
            print("❌ Supabase client not initialized")
            return None
        
        try:
            print(f"\n📤 UPLOAD PROCESS:")
            print(f"  Filename: {filename}")
            print(f"  Bucket: {self.bucket_name}")
            
            # Read image data
            image_file.seek(0)
            image_data = image_file.read()
            print(f"  Image size: {len(image_data)} bytes")
            
            # Upload to Supabase
            print(f"  Uploading...")
            response = self.client.storage.from_(self.bucket_name).upload(
                file=image_data,
                path=filename,
                file_options={"content-type": "image/jpeg"},
                skip_hash_check=True
            )
            print(f"  Upload response: {response}")
            
            # Construct public URL
            url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
            print(f"  ✅ Public URL: {url}\n")
            return url
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            logger.error(f"Error in upload_and_get_url: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# Singleton instance
_supabase_storage = None

def get_supabase_storage():
    """Get or create Supabase storage instance"""
    global _supabase_storage
    if _supabase_storage is None:
        _supabase_storage = SupabaseStorage()
    return _supabase_storage