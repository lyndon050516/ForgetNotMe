#!/usr/bin/env python3
"""
Test script to demonstrate the enroll workflow with duplicate detection.

This script shows how the API now checks for existing persons before enrolling.
"""

import requests
import json
import os

def test_enroll_workflow():
    """Test the enroll endpoint with duplicate detection."""
    
    # API endpoint
    url = "http://localhost:5000/enroll"
    
    # Test images (using the same person - lydon)
    test_images = [
        "test_files/lydon.png",
        "test_files/lydon2.png"  # Same person, different photo
    ]
    
    # Test audio file (you can use any audio file)
    test_audio = "test_files/test_audio.wav"
    
    print("🧪 Testing Enroll Workflow with Duplicate Detection")
    print("=" * 60)
    
    for i, image_path in enumerate(test_images, 1):
        print(f"\n📸 Test {i}: Enrolling with {image_path}")
        print("-" * 40)
        
        # Check if files exist
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            continue
            
        if not os.path.exists(test_audio):
            print(f"❌ Audio file not found: {test_audio}")
            continue
        
        # Prepare the request
        files = {
            'image': open(image_path, 'rb'),
            'audio': open(test_audio, 'rb')
        }
        
        try:
            # Make the request
            response = requests.post(url, files=files)
            
            # Close files
            files['image'].close()
            files['audio'].close()
            
            # Parse response
            result = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('status') == 'already_enrolled':
                print("✅ Duplicate detected! Person already in database.")
            elif result.get('status') == 'success':
                print("✅ New person enrolled successfully.")
            else:
                print(f"❌ Error: {result.get('message', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error: Make sure the API server is running!")
            print("   Run: python api.py")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Expected Results:")
    print("1. First enrollment: Should succeed (new person)")
    print("2. Second enrollment: Should detect duplicate (same person)")
    print("\n💡 The API now prevents duplicate enrollments by checking")
    print("   face embeddings against existing database entries!")

if __name__ == "__main__":
    test_enroll_workflow()
