"""
Forget Me Not - Backend API Server
Main Flask application that handles Unity VR app requests for face recognition and conversation recall.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np
import face_recognition


# Import our custom modules
from face_recognition_module import FaceRecognitionManager
from llm_audio_module import LLMAudioProcessor
from database_manager import DatabaseManager

app = Flask(__name__)
CORS(app)  # Enable CORS for Unity app communication

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3', 'm4a'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize managers
face_manager = FaceRecognitionManager()
audio_processor = LLMAudioProcessor()
db_manager = DatabaseManager()

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint for Quest 3 connectivity test."""
    return jsonify({
        "status": "ok", 
        "service": "Forget Me Not"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Forget Me Not Backend"
    })

@app.route('/enroll', methods=['POST'])
def enroll_person():
    """
    Endpoint 1: POST /enroll
    Input: Image file (for face) and Audio file (for conversation).
    Output: {"status": "success", "person_id": "some_unique_id"}
    """
    try:
        # Check if required files are present
        if 'image' not in request.files or 'audio' not in request.files:
            return jsonify({
                "status": "error",
                "message": "Both image and audio files are required"
            }), 400

        image_file = request.files['image']
        audio_file = request.files['audio']

        # Check if files are selected
        if image_file.filename == '' or audio_file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No files selected"
            }), 400

        # Validate file types
        if not (allowed_file(image_file.filename) and allowed_file(audio_file.filename)):
            return jsonify({
                "status": "error",
                "message": "Invalid file types. Image must be PNG/JPG/JPEG, Audio must be WAV/MP3/M4A"
            }), 400

        # Generate unique person ID
        person_id = str(uuid.uuid4())
        
        # Save files with secure names
        image_filename = secure_filename(f"{person_id}_image.jpg")
        audio_filename = secure_filename(f"{person_id}_audio.wav")
        
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        
        image_file.save(image_path)
        audio_file.save(audio_path)

        # Process the enrollment
        print(f"Processing enrollment for person_id: {person_id}")
        
        # Step 1: Generate face embedding
        face_embedding = face_manager.generate_embedding(image_path)
        if face_embedding is None:
            # Clean up files on failure
            os.remove(image_path)
            os.remove(audio_path)
            return jsonify({
                "status": "error",
                "message": "No face detected in the image"
            }), 400

        # Step 2: Process audio and get summary
        conversation_summary = audio_processor.get_summary_from_audio(audio_path)
        if conversation_summary is None:
            # Clean up files on failure
            os.remove(image_path)
            os.remove(audio_path)
            return jsonify({
                "status": "error",
                "message": "Failed to process audio"
            }), 400
        # Check if this face embedding already exists (avoid duplicate enrollments)
        # Use a threshold of 0.6 (distance < 0.4) for strong matches
        existing_person_id = db_manager.find_person_by_embedding(face_embedding, similarity_threshold=0.6)
        if existing_person_id is not None:
            # Clean up files because we won't enroll again
            os.remove(image_path)
            os.remove(audio_path)
            print(f"Person already enrolled with ID: {existing_person_id}")
            
            # Get existing person data
            existing_person = db_manager.get_person(existing_person_id)
            return jsonify({
                "status": "already_enrolled",
                "person_id": existing_person_id,
                "summary": existing_person.get('summary', 'No summary available'),
                "enrolled_at": existing_person.get('enrolled_at', 'Unknown'),
                "message": "This person is already in the database"
            }), 200
        # Step 3: Save to database
        success = db_manager.save_person(person_id, face_embedding, conversation_summary, {
            'image_path': image_path,
            'audio_path': audio_path,
            'enrolled_at': datetime.now().isoformat()
        })

        if not success:
            # Clean up files on failure
            os.remove(image_path)
            os.remove(audio_path)
            return jsonify({
                "status": "error",
                "message": "Failed to save person data"
            }), 500

        print(f"Successfully enrolled person: {person_id}")
        
        return jsonify({
            "status": "success",
            "person_id": person_id,
            "summary": conversation_summary
        })

    except Exception as e:
        print(f"Error in enroll endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/recall', methods=['POST'])
def recall_person():
    """
    Endpoint 2: POST /recall
    Input: Image file (of the person you see now).
    Output: {"status": "match", "summary": "Last time we talked about..."} or {"status": "no_match"}
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "Image file is required"
            }), 400

        image_file = request.files['image']

        # Check if file is selected
        if image_file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No image file selected"
            }), 400

        # Validate file type
        if not allowed_file(image_file.filename):
            return jsonify({
                "status": "error",
                "message": "Invalid file type. Image must be PNG/JPG/JPEG"
            }), 400

        # Save temporary image file
        temp_filename = secure_filename(f"temp_{uuid.uuid4()}.jpg")
        temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        image_file.save(temp_image_path)

        # Generate face embedding for the query image
        query_embedding = face_manager.generate_embedding(temp_image_path)
        
        # Clean up temporary file
        os.remove(temp_image_path)
        
        if query_embedding is None:
            return jsonify({
                "status": "no_match",
                "message": "No face detected in the image"
            })

        # Find the most similar person using the same logic as enroll
        matching_person_id = db_manager.find_person_by_embedding(query_embedding, similarity_threshold=0.6)
        
        if matching_person_id is None:
            return jsonify({
                "status": "no_match",
                "message": "No matching person found above similarity threshold"
            })

        # Get person data from database
        person_data = db_manager.get_person(matching_person_id)
        
        if person_data is None:
            return jsonify({
                "status": "no_match",
                "message": "Person data not found"
            })

        # Calculate the actual similarity for response
        stored_embedding = np.array(person_data['face_embedding'])
        face_distance = face_recognition.face_distance([stored_embedding], query_embedding)[0]
        confidence = max(0.0, 1.0 - face_distance)

        print(f"✅ Recall successful: Found person {matching_person_id} with confidence: {confidence:.3f}")
        
        return jsonify({
            "status": "match",
            "person_id": matching_person_id,
            "confidence": round(confidence, 3),
            "summary": person_data['summary'],
            "enrolled_at": person_data.get('metadata', {}).get('enrolled_at', 'Unknown')
        })

    except Exception as e:
        print(f"Error in recall endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/list_persons', methods=['GET'])
def list_persons():
    """
    Debug endpoint to list all enrolled persons.
    """
    try:
        persons = db_manager.list_all_persons()
        return jsonify({
            "status": "success",
            "count": len(persons),
            "persons": persons
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/clear_database', methods=['POST'])
def clear_database():
    """
    Debug endpoint to clear all data.
    """
    try:
        db_manager.clear_all_data()
        return jsonify({
            "status": "success",
            "message": "Database cleared successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    import socket
    
    print("Starting Forget Me Not Backend Server...")
    print("API Endpoints:")
    print("  GET /ping - Simple connectivity test")
    print("  POST /enroll - Enroll a new person (image + audio)")
    print("  POST /recall - Recall a person (image)")
    print("  GET /health - Health check")
    print("  GET /list_persons - List all enrolled persons (debug)")
    print("  POST /clear_database - Clear all data (debug)")
    
    # Get local IP address
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"\n🌐 Connect from Quest 3 using: http://{local_ip}:5001")
        print(f"   Test connectivity: http://{local_ip}:5001/ping")
    except:
        print("\n🌐 Connect from Quest 3 using: http://YOUR_IP_ADDRESS:5001")
        print("   (Find your IP address in your network settings)")
    
    print()
    
    # Run the server
    app.run(host='0.0.0.0', port=5001, debug=True)
