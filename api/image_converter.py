"""
Image conversion utilities for the Forget Me Not API
Handles JPG to PNG conversion for Quest 3 uploads
"""

import os
from PIL import Image
import uuid

def convert_jpg_to_png(input_path, output_dir=None, keep_original=True):
    """
    Convert a JPG/JPEG file to PNG format
    
    Args:
        input_path (str): Path to the input JPG file
        output_dir (str): Directory to save the PNG file (optional)
        keep_original (bool): Whether to keep the original JPG file
    
    Returns:
        str: Path to the converted PNG file, or None if conversion failed
    """
    try:
        # Open the JPG image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode not in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Generate output path
            if output_dir is None:
                output_dir = os.path.dirname(input_path)
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            output_path = os.path.join(output_dir, f"{unique_id}_converted.png")
            
            # Save as PNG
            img.save(output_path, 'PNG')
            
            # Remove original if requested
            if not keep_original:
                os.remove(input_path)
            
            return output_path
            
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return None

def is_jpg_file(file_path):
    """
    Check if a file is a JPG/JPEG image
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        bool: True if the file is a JPG/JPEG image
    """
    return file_path.lower().endswith(('.jpg', '.jpeg'))

def auto_convert_upload(file_path, uploads_dir=None):
    """
    Automatically convert JPG uploads to PNG
    
    Args:
        file_path (str): Path to the uploaded file
        uploads_dir (str): Directory where uploads are stored
    
    Returns:
        str: Path to the converted PNG file or original file if no conversion needed
    """
    if is_jpg_file(file_path):
        print(f"Converting JPG to PNG: {file_path}")
        converted_path = convert_jpg_to_png(file_path, uploads_dir)
        if converted_path:
            return converted_path
    
    return file_path

# Example usage for API integration
def process_quest_upload(image_file, uploads_dir):
    """
    Process an image upload from Quest 3, converting JPG to PNG if needed
    
    Args:
        image_file: Flask file object from request
        uploads_dir (str): Directory to save the processed file
    
    Returns:
        str: Path to the final processed image file
    """
    # Save the uploaded file
    unique_id = str(uuid.uuid4())
    original_extension = os.path.splitext(image_file.filename)[1].lower()
    temp_path = os.path.join(uploads_dir, f"{unique_id}_temp{original_extension}")
    
    image_file.save(temp_path)
    
    # Convert if it's a JPG
    if is_jpg_file(temp_path):
        final_path = convert_jpg_to_png(temp_path, uploads_dir, keep_original=False)
        return final_path
    else:
        # Rename to PNG extension
        final_path = os.path.join(uploads_dir, f"{unique_id}_image.png")
        os.rename(temp_path, final_path)
        return final_path
