#!/usr/bin/env python3
"""
Debug Image Viewer for Forget Me Not
This script helps you view and manage debug images captured during testing.
"""

import os
import glob
from datetime import datetime
import subprocess
import sys

def list_debug_images():
    """List all debug images in the uploads folder."""
    uploads_dir = "uploads"
    debug_images = glob.glob(os.path.join(uploads_dir, "debug_*.jpg"))
    
    if not debug_images:
        print("No debug images found in uploads folder.")
        return []
    
    # Sort by modification time (newest first)
    debug_images.sort(key=os.path.getmtime, reverse=True)
    
    print(f"Found {len(debug_images)} debug images:")
    print("-" * 80)
    
    for i, img_path in enumerate(debug_images, 1):
        filename = os.path.basename(img_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(img_path))
        size = os.path.getsize(img_path)
        
        # Parse filename to extract type and timestamp
        parts = filename.replace("debug_", "").replace(".jpg", "").split("_")
        if len(parts) >= 2:
            img_type = parts[0]
            timestamp = f"{parts[1]}_{parts[2]}" if len(parts) > 2 else "unknown"
        else:
            img_type = "unknown"
            timestamp = "unknown"
        
        print(f"{i:2d}. {filename}")
        print(f"    Type: {img_type} | Time: {timestamp} | Size: {size:,} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    return debug_images

def open_image(image_path):
    """Open an image with the default system viewer."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", image_path])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", image_path], shell=True)
        else:  # Linux
            subprocess.run(["xdg-open", image_path])
        print(f"Opened: {image_path}")
    except Exception as e:
        print(f"Error opening image: {e}")

def main():
    print("🔍 Forget Me Not Debug Image Viewer")
    print("=" * 50)
    
    while True:
        debug_images = list_debug_images()
        
        if not debug_images:
            print("No debug images to view. Try capturing some images in your VR app first.")
            break
        
        print("\nOptions:")
        print("1. View an image (enter number)")
        print("2. View latest image")
        print("3. Open uploads folder")
        print("4. Refresh list")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            try:
                img_num = int(input("Enter image number: ")) - 1
                if 0 <= img_num < len(debug_images):
                    open_image(debug_images[img_num])
                else:
                    print("Invalid image number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == "2":
            open_image(debug_images[0])  # First image is newest
        
        elif choice == "3":
            uploads_path = os.path.abspath("uploads")
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", uploads_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", uploads_path])
            else:  # Linux
                subprocess.run(["xdg-open", uploads_path])
        
        elif choice == "4":
            continue  # Refresh the list
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
