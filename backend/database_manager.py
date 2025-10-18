"""
Database Manager for Forget Me Not
Handles storage and retrieval of person data using JSON files.
"""

import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseManager:
    def __init__(self, db_file='person_database.json'):
        """
        Initialize the Database Manager.
        
        Args:
            db_file (str): Path to the JSON database file
        """
        self.db_file = db_file
        self.data = self._load_database()
        print(f"Database Manager initialized with {len(self.data)} persons")
    
    def _load_database(self) -> Dict[str, Any]:
        """
        Load the database from JSON file.
        
        Returns:
            Dict: Loaded database data
        """
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    # Convert face embeddings back to numpy arrays
                    for person_id, person_data in data.items():
                        if 'face_embedding' in person_data:
                            person_data['face_embedding'] = np.array(person_data['face_embedding'])
                    print(f"Loaded database from {self.db_file}")
                    return data
            else:
                print(f"Database file {self.db_file} not found, starting with empty database")
                return {}
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return {}
    
    def _save_database(self) -> bool:
        """
        Save the database to JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a copy of data with numpy arrays converted to lists
            data_to_save = {}
            for person_id, person_data in self.data.items():
                data_to_save[person_id] = person_data.copy()
                if 'face_embedding' in data_to_save[person_id]:
                    data_to_save[person_id]['face_embedding'] = data_to_save[person_id]['face_embedding'].tolist()
            
            with open(self.db_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            print(f"Database saved to {self.db_file}")
            return True
            
        except Exception as e:
            print(f"Error saving database: {str(e)}")
            return False
    
    def save_person(self, person_id: str, face_embedding: np.ndarray, summary: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save a new person to the database.
        
        Args:
            person_id (str): Unique identifier for the person
            face_embedding (numpy.ndarray): Face embedding vector
            summary (str): Conversation summary
            metadata (dict): Additional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            person_data = {
                'person_id': person_id,
                'face_embedding': face_embedding,
                'summary': summary,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self.data[person_id] = person_data
            
            success = self._save_database()
            if success:
                print(f"Successfully saved person {person_id} to database")
            else:
                # Remove from memory if save failed
                del self.data[person_id]
                print(f"Failed to save person {person_id} to database")
            
            return success
            
        except Exception as e:
            print(f"Error saving person {person_id}: {str(e)}")
            return False
    
    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a person from the database.
        
        Args:
            person_id (str): Unique identifier for the person
            
        Returns:
            Dict: Person data or None if not found
        """
        try:
            return self.data.get(person_id)
        except Exception as e:
            print(f"Error retrieving person {person_id}: {str(e)}")
            return None
    
    def get_all_persons(self) -> Dict[str, Any]:
        """
        Get all persons from the database.
        
        Returns:
            Dict: All person data
        """
        return self.data.copy()
    
    def update_person(self, person_id: str, **updates) -> bool:
        """
        Update a person's data in the database.
        
        Args:
            person_id (str): Unique identifier for the person
            **updates: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if person_id not in self.data:
                print(f"Person {person_id} not found in database")
                return False
            
            # Update fields
            for key, value in updates.items():
                self.data[person_id][key] = value
            
            # Update timestamp
            self.data[person_id]['updated_at'] = datetime.now().isoformat()
            
            success = self._save_database()
            if success:
                print(f"Successfully updated person {person_id}")
            else:
                print(f"Failed to update person {person_id}")
            
            return success
            
        except Exception as e:
            print(f"Error updating person {person_id}: {str(e)}")
            return False
    
    def delete_person(self, person_id: str) -> bool:
        """
        Delete a person from the database.
        
        Args:
            person_id (str): Unique identifier for the person
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if person_id not in self.data:
                print(f"Person {person_id} not found in database")
                return False
            
            del self.data[person_id]
            success = self._save_database()
            
            if success:
                print(f"Successfully deleted person {person_id}")
            else:
                print(f"Failed to delete person {person_id}")
            
            return success
            
        except Exception as e:
            print(f"Error deleting person {person_id}: {str(e)}")
            return False
    
    def list_all_persons(self) -> List[Dict[str, Any]]:
        """
        List all persons with basic information (excluding embeddings).
        
        Returns:
            List: List of person summaries
        """
        try:
            persons = []
            for person_id, person_data in self.data.items():
                person_summary = {
                    'person_id': person_id,
                    'summary': person_data.get('summary', ''),
                    'created_at': person_data.get('created_at', ''),
                    'updated_at': person_data.get('updated_at', ''),
                    'metadata': person_data.get('metadata', {})
                }
                persons.append(person_summary)
            
            return persons
            
        except Exception as e:
            print(f"Error listing persons: {str(e)}")
            return []
    
    def find_person_by_embedding(self, query_embedding: np.ndarray, similarity_threshold: float = 0.6) -> Optional[str]:
        """
        Find a person by face embedding with high similarity.
        
        Args:
            query_embedding (numpy.ndarray): Face embedding to search for
            similarity_threshold (float): Minimum similarity threshold (0.0-1.0)
                                     0.6 = distance < 0.4 (very strong match)
                                     0.4 = distance < 0.6 (strong match)
            
        Returns:
            str: Person ID if found, None otherwise
        """
        try:
            import face_recognition
            
            best_match = None
            best_similarity = 0.0
            best_distance = float('inf')
            
            print(f"Searching for existing person with similarity threshold: {similarity_threshold}")
            
            for person_id, person_data in self.data.items():
                stored_embedding = np.array(person_data['face_embedding'])
                
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([stored_embedding], query_embedding)[0]
                
                # Convert distance to similarity (1.0 - distance, with minimum of 0.0)
                similarity = max(0.0, 1.0 - face_distance)
                
                print(f"  Person {person_id}: distance={face_distance:.3f}, similarity={similarity:.3f}")
                
                if similarity > best_similarity and similarity >= similarity_threshold:
                    best_similarity = similarity
                    best_distance = face_distance
                    best_match = person_id
            
            if best_match:
                print(f"✅ Found existing person {best_match} with similarity {best_similarity:.3f} (distance: {best_distance:.3f})")
                return best_match
            else:
                print(f"❌ No existing person found above similarity threshold {similarity_threshold}")
                return None
                
        except Exception as e:
            print(f"Error finding person by embedding: {str(e)}")
            return None

    def search_persons_by_summary(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for persons by summary content.
        
        Args:
            query (str): Search query
            
        Returns:
            List: Matching persons
        """
        try:
            query_lower = query.lower()
            matches = []
            
            for person_id, person_data in self.data.items():
                summary = person_data.get('summary', '').lower()
                if query_lower in summary:
                    person_summary = {
                        'person_id': person_id,
                        'summary': person_data.get('summary', ''),
                        'created_at': person_data.get('created_at', ''),
                        'relevance_score': summary.count(query_lower)  # Simple relevance scoring
                    }
                    matches.append(person_summary)
            
            # Sort by relevance score
            matches.sort(key=lambda x: x['relevance_score'], reverse=True)
            return matches
            
        except Exception as e:
            print(f"Error searching persons: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict: Database statistics
        """
        try:
            total_persons = len(self.data)
            
            if total_persons == 0:
                return {
                    'total_persons': 0,
                    'database_size_mb': 0,
                    'oldest_person': None,
                    'newest_person': None
                }
            
            # Calculate database file size
            db_size_mb = os.path.getsize(self.db_file) / (1024 * 1024) if os.path.exists(self.db_file) else 0
            
            # Find oldest and newest persons
            created_dates = [person_data.get('created_at', '') for person_data in self.data.values()]
            created_dates = [date for date in created_dates if date]  # Filter out empty dates
            
            oldest_person = min(created_dates) if created_dates else None
            newest_person = max(created_dates) if created_dates else None
            
            return {
                'total_persons': total_persons,
                'database_size_mb': round(db_size_mb, 2),
                'oldest_person': oldest_person,
                'newest_person': newest_person,
                'database_file': self.db_file
            }
            
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {'error': str(e)}
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.data = {}
            success = self._save_database()
            
            if success:
                print("Successfully cleared all database data")
            else:
                print("Failed to clear database data")
            
            return success
            
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return False
    
    def backup_database(self, backup_file: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_file (str): Path for backup file (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not backup_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{self.db_file}.backup_{timestamp}"
            
            # Create backup with numpy arrays converted to lists
            data_to_backup = {}
            for person_id, person_data in self.data.items():
                data_to_backup[person_id] = person_data.copy()
                if 'face_embedding' in data_to_backup[person_id]:
                    data_to_backup[person_id]['face_embedding'] = data_to_backup[person_id]['face_embedding'].tolist()
            
            with open(backup_file, 'w') as f:
                json.dump(data_to_backup, f, indent=2)
            
            print(f"Database backed up to {backup_file}")
            return True
            
        except Exception as e:
            print(f"Error backing up database: {str(e)}")
            return False
