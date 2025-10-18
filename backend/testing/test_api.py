"""
Test script to simulate Unity app requests to the Forget Me Not Backend API
"""

import requests
import os
import json
import time
from PIL import Image
import numpy as np
import io

# ========================================
# CONFIGURATION - Change these paths here
# ========================================
# Simply change these paths to test with different images/audio files
TEST_IMAGE_PATH = "test_files/lydon2.png"  # Change this to your image path
TEST_AUDIO_PATH = "test_files/test_audio.wav"  # Change this to your audio path

# Examples:
# TEST_IMAGE_PATH = "test_files/james.png"
# TEST_IMAGE_PATH = "test_files/lyndon2.png"
# TEST_IMAGE_PATH = "test_files/test_face.png"
# ========================================

class APITester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_files_dir = "test_files"
        self.test_image_path = TEST_IMAGE_PATH
        self.test_audio_path = TEST_AUDIO_PATH
        self.setup_test_files()
    
    def setup_test_files(self):
        """Create test image and audio files if they don't exist."""
        if not os.path.exists(self.test_files_dir):
            os.makedirs(self.test_files_dir)
        
        # Check if test image exists, create dummy if not
        if not os.path.exists(self.test_image_path):
            print(f"⚠️  Test image not found: {self.test_image_path}")
            print("Creating a dummy test image...")
            self.create_test_image()
        else:
            print(f"✅ Using test image: {self.test_image_path}")
        
        # Check if test audio exists, create dummy if not
        if not os.path.exists(self.test_audio_path):
            print(f"⚠️  Test audio not found: {self.test_audio_path}")
            print("Creating a dummy test audio...")
            self.create_test_audio()
        else:
            print(f"✅ Using test audio: {self.test_audio_path}")
        
        print(f"✓ Test files ready in {self.test_files_dir}/")
    
    def create_test_image(self):
        """Create a simple test image with a face-like pattern."""
        # Create a simple image (100x100 pixels, RGB)
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Add a simple "face" pattern (circles for eyes, etc.)
        img_array[30:35, 40:45] = [0, 0, 0]  # Left eye
        img_array[30:35, 55:60] = [0, 0, 0]  # Right eye
        img_array[50:55, 45:55] = [255, 0, 0]  # Nose
        img_array[65:70, 40:60] = [0, 255, 0]  # Mouth
        
        # Determine file format from extension
        if self.test_image_path.lower().endswith('.png'):
            img_format = "PNG"
        else:
            img_format = "JPEG"
        
        # Save image
        img = Image.fromarray(img_array)
        img.save(self.test_image_path, img_format)
        print(f"✓ Created test image: {self.test_image_path}")
    
    def create_test_audio(self):
        """Create a dummy audio file."""
        # Create a simple WAV file header + minimal audio data
        # This is a very basic WAV file (1 second of silence)
        wav_data = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        
        with open(self.test_audio_path, 'wb') as f:
            f.write(wav_data)
        print(f"✓ Created test audio: {self.test_audio_path}")
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        print("\n🏥 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed: {data['status']}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Health check failed: {e}")
            return False
    
    def test_enroll_endpoint(self):
        """Test the enroll endpoint."""
        print("\n📝 Testing enroll endpoint...")
        try:
            with open(self.test_image_path, 'rb') as img_file, \
                 open(self.test_audio_path, 'rb') as audio_file:
                
                files = {
                    'image': (self.test_image_path, img_file, 'image/jpeg'),
                    'audio': ('test_audio.wav', audio_file, 'audio/wav')
                }
                
                response = requests.post(
                    f"{self.base_url}/enroll",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success':
                        print(f"✓ Enroll successful: {data['person_id']}")
                        print(f"  Summary: {data.get('summary', 'No summary')}")
                        return data['person_id']
                    else:
                        print(f"✗ Enroll failed: {data.get('message', 'Unknown error')}")
                        return None
                else:
                    print(f"✗ Enroll failed: {response.status_code} - {response.text}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            print(f"✗ Enroll request failed: {e}")
            return None
        except FileNotFoundError as e:
            print(f"✗ Test files not found: {e}")
            return None
    
    def test_recall_endpoint(self, person_id=None):
        """Test the recall endpoint."""
        print("\n🔍 Testing recall endpoint...")
        try:
            with open(self.test_image_path, 'rb') as img_file:
                files = {
                    'image': ('test_face.jpg', img_file, 'image/jpeg')
                }
                
                response = requests.post(
                    f"{self.base_url}/recall",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'match':
                        print(f"✓ Recall successful: Found person {data['person_id']}")
                        print(f"  Confidence: {data.get('confidence', 0):.3f}")
                        print(f"  Summary: {data.get('summary', 'No summary')}")
                        return True
                    elif data['status'] == 'no_match':
                        print("✓ Recall successful: No match found (expected if no persons enrolled)")
                        return True
                    else:
                        print(f"✗ Recall unexpected status: {data}")
                        return False
                else:
                    print(f"✗ Recall failed: {response.status_code} - {response.text}")
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"✗ Recall request failed: {e}")
            return False
        except FileNotFoundError as e:
            print(f"✗ Test image not found: {e}")
            return False
    
    def test_list_persons_endpoint(self):
        """Test the list persons debug endpoint."""
        return False
        print("\n📋 Testing list persons endpoint...")
        try:
            response = requests.get(f"{self.base_url}/list_persons", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ List persons successful: {data['count']} persons found")
                for person in data['persons']:
                    print(f"  - {person['person_id']}: {person['summary'][:50]}...")
                return True
            else:
                print(f"✗ List persons failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ List persons request failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid requests."""
        print("\n🚨 Testing error handling...")
        
        # Test enroll without files
        try:
            response = requests.post(f"{self.base_url}/enroll", timeout=10)
            if response.status_code == 400:
                print("✓ Enroll without files correctly returns 400")
            else:
                print(f"✗ Expected 400, got {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Error test failed: {e}")
        
        # Test recall without image
        try:
            response = requests.post(f"{self.base_url}/recall", timeout=10)
            if response.status_code == 400:
                print("✓ Recall without image correctly returns 400")
            else:
                print(f"✗ Expected 400, got {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Error test failed: {e}")
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🧪 Starting Forget Me Not API Tests")
        print("=" * 50)
        
        # Test 1: Health check
        health_ok = self.test_health_endpoint()
        if not health_ok:
            print("\n❌ Server is not running or not accessible")
            print("Make sure to start the server with: python api.py")
            return False
        
        # Test 2: Enroll a person
        person_id = self.test_enroll_endpoint()
        
        # Test 3: Recall the person
        recall_ok = self.test_recall_endpoint(person_id)
        
        # Test 4: List persons
        list_ok = self.test_list_persons_endpoint()
        
        # Test 5: Error handling
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"  Health Check: {'✓' if health_ok else '✗'}")
        print(f"  Enroll: {'✓' if person_id else '✗'}")
        print(f"  Recall: {'✓' if recall_ok else '✗'}")
        print(f"  List Persons: {'✓' if list_ok else '✗'}")
        
        if health_ok and person_id and recall_ok and list_ok:
            print("\n🎉 All tests passed! Your API is working correctly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Check the error messages above.")
            return False

def main():
    """Main test function."""
    print("🚀 Forget Me Not API Tester")
    print("Make sure your Flask server is running: python api.py")
    print("Press Enter to start tests...")
    input()
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ API is ready for Unity integration!")
        print("\nNext steps:")
        print("1. Share your IP address with the Unity developer")
        print("2. Test with real face images and audio files")
        print("3. Monitor server logs for any issues")
    else:
        print("\n❌ API needs fixes before Unity integration")
    
    return success

if __name__ == "__main__":
    main()
