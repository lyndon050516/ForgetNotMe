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
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size for Unity VR files

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize managers
face_manager = FaceRecognitionManager()
audio_processor = LLMAudioProcessor()
db_manager = DatabaseManager()

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors."""
    return jsonify({
        "status": "error",
        "message": "File too large. Maximum size is 100MB per file.",
        "error_type": "RequestEntityTooLarge"
    }), 413

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
        # Log the request
        print(f"\n[{datetime.now().isoformat()}] POST /enroll request received")
        print(f"Content-Length: {request.headers.get('Content-Length', 'Unknown')}")
        
        # Check content length before processing
        content_length = request.headers.get('Content-Length')
        if content_length and int(content_length) > MAX_CONTENT_LENGTH:
            return jsonify({
                "status": "error",
                "message": f"Request too large. Maximum size is {MAX_CONTENT_LENGTH // (1024*1024)}MB.",
                "error_type": "RequestEntityTooLarge"
            }), 413
        
        # Log to file
        try:
            with open('logs/api_calls.log', 'a') as f:
                f.write(f"\n[{datetime.now().isoformat()}] POST /enroll request\n")
                f.write(f"Content-Length: {content_length}\n")
        except Exception as log_error:
            print(f"Logging error: {log_error}")
        # Check if required files are present
        print(f"Available files in request: {list(request.files.keys())}")
        print(f"Request content type: {request.content_type}")
        
        if 'image' not in request.files or 'audio' not in request.files:
            print(f"Missing files - image: {'image' in request.files}, audio: {'audio' in request.files}")
            return jsonify({
                "status": "error",
                "message": "Both image and audio files are required",
                "available_files": list(request.files.keys())
            }), 400

        image_file = request.files['image']
        audio_file = request.files['audio']

        # Check if files are selected
        print(f"Image filename: '{image_file.filename}'")
        print(f"Audio filename: '{audio_file.filename}'")
        
        if image_file.filename == '' or audio_file.filename == '':
            print("Empty filenames detected")
            return jsonify({
                "status": "error",
                "message": "No files selected",
                "image_filename": image_file.filename,
                "audio_filename": audio_file.filename
            }), 400

        # Validate file types
        image_valid = allowed_file(image_file.filename)
        audio_valid = allowed_file(audio_file.filename)
        print(f"File type validation - Image: {image_valid}, Audio: {audio_valid}")
        
        if not (image_valid and audio_valid):
            return jsonify({
                "status": "error",
                "message": "Invalid file types. Image must be PNG/JPG/JPEG, Audio must be WAV/MP3/M4A",
                "image_valid": image_valid,
                "audio_valid": audio_valid,
                "image_filename": image_file.filename,
                "audio_filename": audio_file.filename
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
        print(f"Attempting face detection on: {image_path}")
        face_embedding = face_manager.generate_embedding(image_path)
        if face_embedding is None:
            print(f"Face detection failed for: {image_path}")
            # Save the image temporarily for debugging (don't delete it)
            debug_image_path = f"uploads/debug_no_face_{person_id}.jpg"
            os.rename(image_path, debug_image_path)
            print(f"Saved debug image to: {debug_image_path}")
            
            # Clean up audio file on failure
            os.remove(audio_path)
            return jsonify({
                "status": "error",
                "message": "No face detected in the image. Please ensure the image contains a clear, well-lit face.",
                "debug_image_saved": debug_image_path
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
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in enroll endpoint: {str(e)}")
        print(f"Full traceback: {error_details}")
        
        # Log to file for debugging
        with open('logs/api_calls.log', 'a') as f:
            f.write(f"\n[{datetime.now().isoformat()}] ERROR in /enroll:\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Traceback: {error_details}\n")
            f.write("-" * 50 + "\n")
        
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "error_type": type(e).__name__
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

@app.route('/debug_image', methods=['POST'])
def save_debug_image():
    """
    Debug endpoint to save captured images for debugging.
    """
    try:
        if 'debug_image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No debug image file provided"
            }), 400
        
        debug_file = request.files['debug_image']
        if debug_file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No debug image file selected"
            }), 400
        
        # Save the debug image
        debug_filename = secure_filename(debug_file.filename)
        debug_path = os.path.join(app.config['UPLOAD_FOLDER'], debug_filename)
        debug_file.save(debug_path)
        
        print(f"DEBUG: Saved debug image to: {debug_path}")
        
        return jsonify({
            "status": "success",
            "message": "Debug image saved successfully",
            "filename": debug_filename,
            "path": debug_path
        })
        
    except Exception as e:
        print(f"Error saving debug image: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to save debug image: {str(e)}"
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
    print("  POST /debug_image - Save debug images (debug)")
    
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
