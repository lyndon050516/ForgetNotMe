"""
LLM and Audio Processing Module for Forget Me Not
Handles audio transcription using Whisper and text summarization using Groq API.
"""

import os
import whisper
import requests
import json
from typing import Optional

class LLMAudioProcessor:
    def __init__(self, groq_api_key=None, groq_api_url=None, groq_model=None):
        """
        Initialize the LLM and Audio Processor.
        
        Args:
            groq_api_key (str): API key for Groq service
            groq_api_url (str): URL for Groq API endpoint
            groq_model (str): Groq model to use
        """
        # Load Whisper model (base model for good balance of speed and accuracy)
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully")
        
        # Groq API configuration
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.groq_api_url = groq_api_url or os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
        self.groq_model = groq_model or os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        
        if not self.groq_api_key:
            print("Warning: No Groq API key found. Set GROQ_API_KEY environment variable.")
        else:
            print(f"Groq API configuration loaded (model: {self.groq_model})")
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        try:
            print(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe audio using Whisper
            result = self.whisper_model.transcribe(audio_file_path)
            transcript = result["text"].strip()
            
            if not transcript:
                print("No speech detected in audio file")
                return None
            
            print(f"Transcription successful: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            print(f"Error transcribing audio {audio_file_path}: {str(e)}")
            return None
    
    def summarize_text(self, transcript):
        """
        Summarize the transcript using Groq API.
        
        Args:
            transcript (str): Text to summarize
            
        Returns:
            str: Summarized text, or None if summarization failed
        """
        try:
            if not self.groq_api_key:
                print("No Groq API key available. Returning truncated transcript.")
                # Return first 200 characters as a fallback
                return transcript[:200] + "..." if len(transcript) > 200 else transcript
            
            print(f"Sending request to Groq API for summarization (model: {self.groq_model})...")
            
            # Prepare the prompt for summarization
            prompt = f"""Please summarize the key points of this conversation in 1-2 sentences. Focus on the main topics discussed and any important information shared:

{transcript}

Summary:"""
            
            # Prepare API request (Groq uses OpenAI-compatible format)
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.groq_model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that creates concise summaries of conversations. Focus on key topics, important details, and memorable information.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 150,
                'temperature': 0.3
            }
            
            # Make API request
            response = requests.post(self.groq_api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content'].strip()
                print(f"Summarization successful: {len(summary)} characters")
                return summary
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                # Fallback to truncated transcript
                return transcript[:200] + "..." if len(transcript) > 200 else transcript
                
        except requests.exceptions.Timeout:
            print("Groq API request timed out. Using fallback summary.")
            return transcript[:200] + "..." if len(transcript) > 200 else transcript
        except Exception as e:
            print(f"Error summarizing text: {str(e)}")
            # Fallback to truncated transcript
            return transcript[:200] + "..." if len(transcript) > 200 else transcript
    
    def get_summary_from_audio(self, audio_file_path):
        """
        Complete pipeline: transcribe audio and summarize the text.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: Final summary, or None if processing failed
        """
        try:
            print(f"Processing audio file: {audio_file_path}")
            
            # Step 1: Transcribe audio
            transcript = self.transcribe_audio(audio_file_path)
            if not transcript:
                print("Failed to transcribe audio")
                return None
            
            # Step 2: Summarize transcript
            summary = self.summarize_text(transcript)
            if not summary:
                print("Failed to summarize transcript")
                return None
            
            print("Audio processing pipeline completed successfully")
            return summary
            
        except Exception as e:
            print(f"Error in audio processing pipeline: {str(e)}")
            return None
    
    def get_conversation_keywords(self, transcript):
        """
        Extract key topics/keywords from the conversation.
        
        Args:
            transcript (str): Transcribed text
            
        Returns:
            list: List of key topics/keywords
        """
        try:
            if not self.groq_api_key:
                # Simple keyword extraction fallback
                words = transcript.lower().split()
                # Filter out common words and return top words
                common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
                
                keywords = [word for word in words if word not in common_words and len(word) > 3]
                return list(set(keywords))[:10]  # Return top 10 unique keywords
            
            # Use Groq API for better keyword extraction
            prompt = f"""Extract the main topics and keywords from this conversation. Return them as a comma-separated list:

{transcript}

Keywords:"""
            
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.groq_model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that extracts key topics and keywords from text.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 100,
                'temperature': 0.2
            }
            
            response = requests.post(self.groq_api_url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                keywords_text = result['choices'][0]['message']['content'].strip()
                keywords = [kw.strip() for kw in keywords_text.split(',')]
                return keywords[:10]
            else:
                print(f"Error extracting keywords: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return []
    
    def validate_audio_quality(self, audio_file_path):
        """
        Validate if the audio file is suitable for transcription.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            dict: Quality assessment with score and feedback
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return {
                    'score': 0.0,
                    'feedback': 'Audio file does not exist',
                    'valid': False
                }
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(audio_file_path)
            if file_size < 1000:  # Less than 1KB
                return {
                    'score': 0.2,
                    'feedback': 'Audio file too small',
                    'valid': False
                }
            
            if file_size > 50 * 1024 * 1024:  # More than 50MB
                return {
                    'score': 0.3,
                    'feedback': 'Audio file too large',
                    'valid': False
                }
            
            # Try to load with Whisper to check if it's valid audio
            try:
                result = self.whisper_model.transcribe(audio_file_path, fp16=False)
                duration = len(result["segments"]) * 1.0 if result["segments"] else 0.0
                
                if duration < 1.0:  # Less than 1 second
                    return {
                        'score': 0.4,
                        'feedback': 'Audio too short',
                        'valid': False
                    }
                
                if duration > 300.0:  # More than 5 minutes
                    return {
                        'score': 0.6,
                        'feedback': 'Audio very long',
                        'valid': True  # Still valid, just long
                    }
                
                return {
                    'score': 0.8,
                    'feedback': 'Good audio quality',
                    'valid': True
                }
                
            except Exception as e:
                return {
                    'score': 0.1,
                    'feedback': f'Invalid audio format: {str(e)}',
                    'valid': False
                }
                
        except Exception as e:
            return {
                'score': 0.0,
                'feedback': f'Error validating audio: {str(e)}',
                'valid': False
            }
