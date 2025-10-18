#!/usr/bin/env python3
"""
Simple JPG to PNG converter script
Converts JPG/JPEG files to PNG format while preserving image quality
"""

import os
import sys
from PIL import Image
import argparse

def convert_jpg_to_png(input_path, output_path=None):
    """
    Convert a JPG/JPEG file to PNG format
    
    Args:
        input_path (str): Path to the input JPG file
        output_path (str): Path for the output PNG file (optional)
    
    Returns:
        str: Path to the converted PNG file
    """
    try:
        # Open the JPG image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (handles different color modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Keep transparency if present
                pass
            else:
                img = img.convert('RGB')
            
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}.png"
            
            # Save as PNG
            img.save(output_path, 'PNG')
            print(f"✅ Successfully converted: {input_path} → {output_path}")
            return output_path
            
    except Exception as e:
        print(f"❌ Error converting {input_path}: {str(e)}")
        return None

def batch_convert_directory(directory_path, recursive=False):
    """
    Convert all JPG/JPEG files in a directory to PNG
    
    Args:
        directory_path (str): Path to directory containing JPG files
        recursive (bool): Whether to search subdirectories recursively
    """
    jpg_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    converted_count = 0
    
    if recursive:
        # Walk through all subdirectories
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    input_path = os.path.join(root, file)
                    convert_jpg_to_png(input_path)
                    converted_count += 1
    else:
        # Only process files in the specified directory
        for file in os.listdir(directory_path):
            if file.lower().endswith(('.jpg', '.jpeg')):
                input_path = os.path.join(directory_path, file)
                convert_jpg_to_png(input_path)
                converted_count += 1
    
    print(f"\n📊 Total files converted: {converted_count}")

def main():
    parser = argparse.ArgumentParser(description='Convert JPG/JPEG files to PNG format')
    parser.add_argument('input', help='Input JPG file or directory path')
    parser.add_argument('-o', '--output', help='Output PNG file path (for single file conversion)')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Recursively process subdirectories (when input is a directory)')
    parser.add_argument('--batch', action='store_true',
                       help='Force batch processing even for single files')
    
    args = parser.parse_args()
    
    input_path = args.input
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Path '{input_path}' does not exist")
        sys.exit(1)
    
    if os.path.isfile(input_path):
        # Single file conversion
        if input_path.lower().endswith(('.jpg', '.jpeg')):
            convert_jpg_to_png(input_path, args.output)
        else:
            print(f"❌ Error: '{input_path}' is not a JPG/JPEG file")
            sys.exit(1)
    
    elif os.path.isdir(input_path):
        # Directory batch conversion
        print(f"🔄 Processing directory: {input_path}")
        batch_convert_directory(input_path, args.recursive)
    
    else:
        print(f"❌ Error: '{input_path}' is neither a file nor a directory")
        sys.exit(1)

if __name__ == "__main__":
    # If no command line arguments, show usage examples
    if len(sys.argv) == 1:
        print("🖼️  JPG to PNG Converter")
        print("=" * 50)
        print("\nUsage examples:")
        print("  python jpg_to_png_converter.py image.jpg")
        print("  python jpg_to_png_converter.py image.jpg -o converted_image.png")
        print("  python jpg_to_png_converter.py ./uploads/")
        print("  python jpg_to_png_converter.py ./uploads/ -r")
        print("\nFor help: python jpg_to_png_converter.py -h")
        sys.exit(0)
    
    main()
