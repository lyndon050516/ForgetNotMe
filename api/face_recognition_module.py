"""
Face Recognition Module for Forget Me Not
Handles facial embedding generation and similarity search using face_recognition library.
"""

import face_recognition
import numpy as np
from PIL import Image
import cv2
import os

class FaceRecognitionManager:
    def __init__(self, confidence_threshold=0.6):
        """
        Initialize the Face Recognition Manager.
        
        Args:
            confidence_threshold (float): Minimum confidence for face matching (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        print("Face Recognition Manager initialized")
    
    def generate_embedding(self, image_path):
        """
        Generate a facial embedding vector from an image file.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Face embedding vector, or None if no face found
        """
        try:
            # Load the image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations in the image
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                print(f"No face found in image: {image_path}")
                return None
            
            if len(face_locations) > 1:
                print(f"Multiple faces found in image: {image_path}. Using the first one.")
            
            # Get face encodings (embeddings)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) == 0:
                print(f"Could not generate encoding for face in image: {image_path}")
                return None
            
            # Return the first (and likely only) face encoding
            face_embedding = face_encodings[0]
            print(f"Successfully generated face embedding for image: {image_path}")
            return face_embedding
            
        except Exception as e:
            print(f"Error generating face embedding for {image_path}: {str(e)}")
            return None
    
    def find_most_similar_face(self, query_embedding):
        """
        Find the most similar face from the database.
        
        Args:
            query_embedding (numpy.ndarray): Face embedding to search for
            
        Returns:
            dict: {'person_id': str, 'confidence': float} or None if no match
        """
        try:
            from database_manager import DatabaseManager
            db_manager = DatabaseManager()
            
            # Get all persons from database
            all_persons = db_manager.get_all_persons()
            
            if not all_persons:
                print("No persons in database to search")
                return None
            
            best_match = None
            best_confidence = 0.0
            
            # Compare with each person in database
            for person_id, person_data in all_persons.items():
                stored_embedding = np.array(person_data['face_embedding'])
                
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([stored_embedding], query_embedding)[0]
                
                # Convert distance to confidence (1.0 - distance, with minimum of 0.0)
                confidence = max(0.0, 1.0 - face_distance)
                
                print(f"Person {person_id}: distance={face_distance:.3f}, confidence={confidence:.3f}")
                
                # Update best match if this is better and above threshold
                if confidence > best_confidence and confidence >= self.confidence_threshold:
                    best_confidence = confidence
                    best_match = {
                        'person_id': person_id,
                        'confidence': confidence,
                        'distance': face_distance
                    }
            
            if best_match:
                print(f"Best match found: {best_match['person_id']} with confidence {best_match['confidence']:.3f}")
                return best_match
            else:
                print(f"No match found above confidence threshold {self.confidence_threshold}")
                return None
                
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            return None
    
    def calculate_face_similarity(self, embedding1, embedding2):
        """
        Calculate similarity between two face embeddings.
        
        Args:
            embedding1 (numpy.ndarray): First face embedding
            embedding2 (numpy.ndarray): Second face embedding
            
        Returns:
            float: Similarity score (0.0-1.0)
        """
        try:
            distance = face_recognition.face_distance([embedding1], embedding2)[0]
            similarity = max(0.0, 1.0 - distance)
            return similarity
        except Exception as e:
            print(f"Error calculating face similarity: {str(e)}")
            return 0.0
    
    def detect_faces_in_image(self, image_path):
        """
        Detect all faces in an image and return their locations.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            list: List of face locations [(top, right, bottom, left), ...]
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            return face_locations
        except Exception as e:
            print(f"Error detecting faces in {image_path}: {str(e)}")
            return []
    
    def validate_face_quality(self, image_path):
        """
        Validate if the face in the image is of good quality for recognition.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Quality assessment with score and feedback
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return {
                    'score': 0.0,
                    'feedback': 'No face detected',
                    'valid': False
                }
            
            if len(face_locations) > 1:
                return {
                    'score': 0.3,
                    'feedback': 'Multiple faces detected',
                    'valid': False
                }
            
            # Get face location
            top, right, bottom, left = face_locations[0]
            face_height = bottom - top
            face_width = right - left
            
            # Check face size (should be reasonably large)
            image_height, image_width = image.shape[:2]
            face_size_ratio = (face_height * face_width) / (image_height * image_width)
            
            if face_size_ratio < 0.01:  # Face too small
                return {
                    'score': 0.4,
                    'feedback': 'Face too small in image',
                    'valid': False
                }
            
            if face_size_ratio > 0.5:  # Face too large (might be cropped)
                return {
                    'score': 0.6,
                    'feedback': 'Face too large (might be cropped)',
                    'valid': False
                }
            
            # If we get here, the face quality is acceptable
            return {
                'score': 0.8,
                'feedback': 'Good face quality',
                'valid': True
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'feedback': f'Error validating face: {str(e)}',
                'valid': False
            }
