#!/usr/bin/env python3
"""
Simple Face Detection and Embedding Demo

This script demonstrates:
1. Loading an image and detecting faces
2. Drawing bounding boxes around detected faces
3. Generating and displaying face embeddings
4. Showing how embeddings are deterministic for the same person

Usage:
    python face_detection_demo.py <image_path>
    
Example:
    python face_detection_demo.py ../test_files/lydon.png
"""

import sys
import os
import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def draw_face_boxes(image_path, output_path=None):
    """
    Detect faces in an image, draw bounding boxes, and display embeddings.
    
    Args:
        image_path (str): Path to the input image
        output_path (str, optional): Path to save the output image with boxes
    """
    try:
        # Load the image
        print(f"Loading image: {image_path}")
        image = face_recognition.load_image_file(image_path)
        
        # Find face locations
        print("Detecting faces...")
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            print("No faces detected in the image!")
            return None, None
        
        print(f"Found {len(face_locations)} face(s)")
        
        # Get face encodings (embeddings)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        # Convert to PIL Image for drawing
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        face_data = []
        
        # Draw bounding boxes and collect face data
        for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
            top, right, bottom, left = face_location
            
            # Draw rectangle
            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            
            # Add label
            label = f"Face {i+1}"
            draw.text((left, top-25), label, fill="red", font=font)
            
            # Store face data
            face_data.append({
                'face_number': i+1,
                'location': face_location,
                'encoding': face_encoding,
                'encoding_norm': np.linalg.norm(face_encoding)
            })
            
            print(f"\nFace {i+1}:")
            print(f"  Location: top={top}, right={right}, bottom={bottom}, left={left}")
            print(f"  Encoding shape: {face_encoding.shape}")
            print(f"  Encoding norm: {np.linalg.norm(face_encoding):.6f}")
            print(f"  First 10 values: {face_encoding[:10]}")
        
        # Save the image with bounding boxes
        if output_path is None:
            output_path = f"face_detection_result_{os.path.basename(image_path)}"
        
        pil_image.save(output_path)
        print(f"\nImage with bounding boxes saved to: {output_path}")
        
        return face_data, output_path
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None, None

def compare_face_embeddings(face_data1, face_data2):
    """
    Compare face embeddings between two sets of face data.
    
    Args:
        face_data1 (list): Face data from first image
        face_data2 (list): Face data from second image
    """
    print("\n" + "="*50)
    print("FACE EMBEDDING COMPARISON")
    print("="*50)
    
    for i, face1 in enumerate(face_data1):
        print(f"\nFace {face1['face_number']} from first image:")
        
        for j, face2 in enumerate(face_data2):
            # Calculate face distance (lower is more similar)
            distance = face_recognition.face_distance([face1['encoding']], face2['encoding'])[0]
            
            # Convert to similarity (higher is more similar)
            similarity = max(0.0, 1.0 - distance)
            
            print(f"  vs Face {face2['face_number']} from second image:")
            print(f"    Distance: {distance:.6f}")
            print(f"    Similarity: {similarity:.6f}")
            
            # Interpretation
            if distance < 0.4:
                print(f"    → VERY STRONG MATCH (likely same person)")
            elif distance < 0.6:
                print(f"    → STRONG MATCH (probably same person)")
            elif distance < 0.8:
                print(f"    → WEAK MATCH (possibly same person)")
            else:
                print(f"    → NO MATCH (different people)")

def demonstrate_determinism(image_path):
    """
    Demonstrate that face embeddings are deterministic by processing the same image twice.
    """
    print("\n" + "="*50)
    print("DETERMINISM DEMONSTRATION")
    print("="*50)
    print("Processing the same image twice to show embedding consistency...")
    
    # Process the same image twice
    face_data1, _ = draw_face_boxes(image_path, "temp1.jpg")
    face_data2, _ = draw_face_boxes(image_path, "temp2.jpg")
    
    if face_data1 and face_data2:
        print("\nComparing embeddings from the same image processed twice:")
        compare_face_embeddings(face_data1, face_data2)
        
        # Clean up temp files
        os.remove("temp1.jpg")
        os.remove("temp2.jpg")

def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python face_detection_demo.py <image_path>")
    #     print("Example: python face_detection_demo.py ../test_files/lydon.png")
    #     sys.exit(1)
    
    image_path = "test_files/lydon2.png"
    
    # Process the image
    face_data, output_path = draw_face_boxes(image_path)
    
    if face_data is None:
        print("No faces detected or error occurred. Exiting.")
        return
    
    # Show embedding details
    print("\n" + "="*50)
    print("FACE EMBEDDING DETAILS")
    print("="*50)
    
    for face in face_data:
        print(f"\nFace {face['face_number']}:")
        print(f"  Full embedding (first 20 values): {face['encoding'][:20]}")
        print(f"  Embedding statistics:")
        print(f"    Min: {np.min(face['encoding']):.6f}")
        print(f"    Max: {np.max(face['encoding']):.6f}")
        print(f"    Mean: {np.mean(face['encoding']):.6f}")
        print(f"    Std: {np.std(face['encoding']):.6f}")
    
    # Demonstrate determinism
    demonstrate_determinism(image_path)
    
    print(f"\n✅ Demo complete! Check the output image: {output_path}")
    print("\nKey Points about Face Embeddings:")
    print("- Embeddings are 128-dimensional vectors")
    print("- Same person = low distance (< 0.6), high similarity")
    print("- Different people = high distance (> 0.6), low similarity")
    print("- Embeddings are robust to background, lighting, and clothing changes")
    print("- The same face will produce nearly identical embeddings")

if __name__ == "__main__":
    main()
