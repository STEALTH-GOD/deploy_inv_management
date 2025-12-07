from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def compress_image(image, max_size=(800, 800), quality=85):
    """
    Compress and resize an uploaded image.
    
    Args:
        image: Django UploadedFile object
        max_size: Tuple of (width, height) for maximum dimensions
        quality: JPEG quality (1-100, higher is better quality but larger file)
    
    Returns:
        Compressed InMemoryUploadedFile
    """
    if not image:
        return None
    
    try:
        # Open the image
        img = Image.open(image)
        
        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get original dimensions
        original_width, original_height = img.size
        
        # Calculate new dimensions while maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Get file size info
        original_size = image.size / 1024  # KB
        compressed_size = sys.getsizeof(output.getvalue()) / 1024  # KB
        
        # Create a new InMemoryUploadedFile
        compressed_image = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output.getvalue()),
            None
        )
        
        print(f"Image compressed: {original_size:.2f}KB → {compressed_size:.2f}KB "
              f"({original_width}x{original_height} → {img.size[0]}x{img.size[1]})")
        
        return compressed_image
    
    except Exception as e:
        print(f"Error compressing image: {e}")
        return image  # Return original if compression fails
