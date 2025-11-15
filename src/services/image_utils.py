"""Image upload and processing utilities."""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image


def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed.
    
    Args:
        filename: File name
        allowed_extensions: Set of allowed extensions (without dot)
    
    Returns:
        bool: True if extension is allowed
    """
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    # Block double extensions (e.g., file.jpg.exe)
    if filename.count('.') > 1:
        return False
    
    return ext in allowed_extensions


def validate_image_content(file_path):
    """
    Validate that file is actually an image by trying to open it with PIL.
    
    Args:
        file_path: Path to file
    
    Returns:
        bool: True if file is a valid image
    """
    try:
        with Image.open(file_path) as img:
            # Verify it's one of our allowed formats
            allowed_formats = {'JPEG', 'PNG', 'WEBP'}
            return img.format in allowed_formats
    except Exception:
        return False


def generate_thumbnail(image_path, thumbnail_path, max_width=400):
    """
    Generate a thumbnail from an image.
    
    Args:
        image_path: Path to source image
        thumbnail_path: Path to save thumbnail
        max_width: Maximum width for thumbnail
    
    Returns:
        bool: True if successful
    """
    try:
        with Image.open(image_path) as img:
            # Calculate new size maintaining aspect ratio
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img.thumbnail(new_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(thumbnail_path)
            return True
    except Exception:
        return False


def save_uploaded_image(file_storage, resource_id, upload_folder, allowed_extensions):
    """
    Save an uploaded image and generate thumbnail.
    
    Args:
        file_storage: Werkzeug FileStorage object
        resource_id: Resource ID
        upload_folder: Base upload folder path
        allowed_extensions: Set of allowed extensions
    
    Returns:
        tuple: (relative_path, thumbnail_relative_path) or (None, None) if failed
    
    Raises:
        ValueError: If file is invalid
    """
    # Validate filename
    if not file_storage.filename:
        raise ValueError("No filename provided")
    
    # Secure filename and check extension
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename, allowed_extensions):
        raise ValueError(f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}")
    
    # Generate unique filename
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create resource-specific directory
    resource_dir = Path(upload_folder) / str(resource_id)
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    # Full paths
    full_path = resource_dir / unique_filename
    thumbnail_filename = f"{unique_filename.rsplit('.', 1)[0]}_thumb.{ext}"
    thumbnail_path = resource_dir / thumbnail_filename
    
    # Save file
    file_storage.save(str(full_path))
    
    # Validate image content (check MIME type)
    if not validate_image_content(str(full_path)):
        # Clean up if invalid
        if full_path.exists():
            full_path.unlink()
        raise ValueError("File is not a valid image")
    
    # Generate thumbnail
    if not generate_thumbnail(str(full_path), str(thumbnail_path)):
        # If thumbnail generation fails, still keep the original
        pass
    
    # Return relative paths (from static/uploads/resources/)
    relative_path = f"resources/{resource_id}/{unique_filename}"
    thumbnail_relative_path = f"resources/{resource_id}/{thumbnail_filename}"
    
    return relative_path, thumbnail_relative_path

