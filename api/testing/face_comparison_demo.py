#!/usr/bin/env python3
"""
Face Comparison Demo

This script compares faces between two images to demonstrate:
1. How embeddings work for the same person across different images
2. How embeddings differ for different people
3. The robustness of face recognition to background changes

Usage:
    python face_comparison_demo.py <image1_path> <image2_path>
    
Example:
    python face_comparison_demo.py ../test_files/lydon.png ../test_files/lydon2.png
"""

import sys
import os
import face_recognition
import numpy as np
from PIL import Image, ImageDraw

def load_and_detect_faces(image_path):
    """Load image and detect all faces with their embeddings."""
    try:
        print(f"Processing: {image_path}")
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        face_data = []
        for i, (location, encoding) in enumerate(zip(face_locations, face_encodings)):
            face_data.append({
                'face_id': f"{os.path.basename(image_path)}_face_{i+1}",
                'location': location,
                'encoding': encoding,
                'image_path': image_path
            })
        
        print(f"  Found {len(face_data)} face(s)")
        return face_data
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return []

def compare_all_faces(faces1, faces2):
    """Compare all faces between two sets."""
    print("\n" + "="*60)
    print("FACE COMPARISON RESULTS")
    print("="*60)
    
    if not faces1 or not faces2:
        print("Cannot compare - one or both images have no faces")
        return
    
    print(f"Comparing {len(faces1)} face(s) from first image with {len(faces2)} face(s) from second image")
    print()
    
    best_matches = []
    
    for i, face1 in enumerate(faces1):
        print(f"Face {i+1} from {os.path.basename(face1['image_path'])}:")
        
        best_match = None
        best_distance = float('inf')
        
        for j, face2 in enumerate(faces2):
            distance = face_recognition.face_distance([face1['encoding']], face2['encoding'])[0]
            similarity = max(0.0, 1.0 - distance)
            
            print(f"  vs Face {j+1} from {os.path.basename(face2['image_path'])}:")
            print(f"    Distance: {distance:.6f}")
            print(f"    Similarity: {similarity:.6f}")
            
            # Determine match quality
            if distance < 0.4:
                match_quality = "VERY STRONG MATCH"
                color = "🟢"
            elif distance < 0.6:
                match_quality = "STRONG MATCH"
                color = "🟡"
            elif distance < 0.8:
                match_quality = "WEAK MATCH"
                color = "🟠"
            else:
                match_quality = "NO MATCH"
                color = "🔴"
            
            print(f"    {color} {match_quality}")
            
            if distance < best_distance:
                best_distance = distance
                best_match = {
                    'face1': face1,
                    'face2': face2,
                    'distance': distance,
                    'similarity': similarity,
                    'quality': match_quality
                }
        
        if best_match:
            best_matches.append(best_match)
            print(f"  → Best match: {best_match['quality']} (distance: {best_match['distance']:.6f})")
        
        print()
    
    return best_matches

def create_comparison_image(image1_path, image2_path, faces1, faces2, best_matches, output_path="face_comparison_result.jpg"):
    """Create a side-by-side comparison image with bounding boxes."""
    try:
        # Load images
        img1 = face_recognition.load_image_file(image1_path)
        img2 = face_recognition.load_image_file(image2_path)
        
        # Convert to PIL
        pil_img1 = Image.fromarray(img1)
        pil_img2 = Image.fromarray(img2)
        
        # Resize images to same height for comparison
        target_height = min(pil_img1.height, pil_img2.height)
        pil_img1 = pil_img1.resize((int(pil_img1.width * target_height / pil_img1.height), target_height))
        pil_img2 = pil_img2.resize((int(pil_img2.width * target_height / pil_img2.height), target_height))
        
        # Create combined image
        total_width = pil_img1.width + pil_img2.width + 20  # 20px gap
        combined = Image.new('RGB', (total_width, target_height), 'white')
        combined.paste(pil_img1, (0, 0))
        combined.paste(pil_img2, (pil_img1.width + 20, 0))
        
        # Draw bounding boxes
        draw = ImageDraw.Draw(combined)
        
        # Draw boxes for first image
        for i, face in enumerate(faces1):
            top, right, bottom, left = face['location']
            # Scale coordinates if image was resized
            scale_factor = target_height / img1.shape[0]
            top = int(top * scale_factor)
            right = int(right * scale_factor)
            bottom = int(bottom * scale_factor)
            left = int(left * scale_factor)
            
            draw.rectangle([left, top, right, bottom], outline="blue", width=3)
            draw.text((left, top-20), f"Face {i+1}", fill="blue")
        
        # Draw boxes for second image
        for i, face in enumerate(faces2):
            top, right, bottom, left = face['location']
            # Scale coordinates and offset for second image
            scale_factor = target_height / img2.shape[0]
            top = int(top * scale_factor)
            right = int(right * scale_factor)
            bottom = int(bottom * scale_factor)
            left = int(left * scale_factor)
            
            # Offset for second image position
            left += pil_img1.width + 20
            right += pil_img1.width + 20
            
            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            draw.text((left, top-20), f"Face {i+1}", fill="red")
        
        # Save result
        combined.save(output_path)
        print(f"Comparison image saved to: {output_path}")
        
    except Exception as e:
        print(f"Error creating comparison image: {str(e)}")

def main():
    image1_path = "test_files/lydon.png"
    image2_path = "test_files/lydon2.png"
    
    print("Face Comparison Demo")
    print("="*30)
    
    # Process both images
    faces1 = load_and_detect_faces(image1_path)
    faces2 = load_and_detect_faces(image2_path)
    
    if not faces1:
        print(f"No faces found in {image1_path}")
        sys.exit(1)
    
    if not faces2:
        print(f"No faces found in {image2_path}")
        sys.exit(1)
    
    # Compare faces
    best_matches = compare_all_faces(faces1, faces2)
    
    # Create comparison image
    create_comparison_image(image1_path, image2_path, faces1, faces2, best_matches)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if best_matches:
        print("Best matches found:")
        for match in best_matches:
            print(f"  {match['face1']['face_id']} ↔ {match['face2']['face_id']}")
            print(f"    Distance: {match['distance']:.6f}")
            print(f"    Quality: {match['quality']}")
    else:
        print("No strong matches found between the images")
    
    print("\nInterpretation Guide:")
    print("🟢 VERY STRONG MATCH (distance < 0.4): Almost certainly the same person")
    print("🟡 STRONG MATCH (distance < 0.6): Probably the same person")
    print("🟠 WEAK MATCH (distance < 0.8): Possibly the same person")
    print("🔴 NO MATCH (distance ≥ 0.8): Different people")

if __name__ == "__main__":
    main()
