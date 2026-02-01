"""
Firebase Realtime Database service for fetching occupancy data
"""
import firebase_admin
from firebase_admin import credentials, db
from django.conf import settings
import os


class FirebaseService:
    """Service class for interacting with Firebase Realtime Database"""
    
    _app = None
    
    def __init__(self):
        if FirebaseService._app is None:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with timeout to prevent hanging"""
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
            
            def init_firebase():
                # Try to use credentials file if provided
                if hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') and settings.FIREBASE_CREDENTIALS_PATH:
                    cred_path = settings.FIREBASE_CREDENTIALS_PATH
                    if os.path.exists(cred_path):
                        cred = credentials.Certificate(cred_path)
                        return firebase_admin.initialize_app(
                            cred,
                            {'databaseURL': settings.FIREBASE_DATABASE_URL}
                        )
                
                # Try to use default credentials (for Google Cloud environments)
                try:
                    return firebase_admin.initialize_app(
                        options={'databaseURL': settings.FIREBASE_DATABASE_URL}
                    )
                except ValueError:
                    # App already initialized
                    return firebase_admin.get_app()
            
            # Use timeout to prevent hanging (2 seconds max for initialization)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(init_firebase)
                try:
                    FirebaseService._app = future.result(timeout=2)
                except FutureTimeoutError:
                    print("Warning: Firebase initialization timed out")
                    print("The app will work but real-time occupancy data may not be available.")
                    FirebaseService._app = None
                except Exception as e:
                    print(f"Warning: Firebase initialization failed: {e}")
                    print("The app will work but real-time occupancy data may not be available.")
                    FirebaseService._app = None
        except Exception as e:
            print(f"Warning: Firebase initialization failed: {e}")
            print("The app will work but real-time occupancy data may not be available.")
            FirebaseService._app = None
    
    def get_room_occupancy(self, device_id, timeout=1):
        """
        Get real-time occupancy data for a room device
        
        Args:
            device_id: The Firebase device ID or room number
            timeout: Timeout in seconds (default: 1)
            
        Returns:
            dict: Occupancy data or None if not available
        """
        # Fast return if Firebase is not initialized
        if FirebaseService._app is None:
            return None
        
        try:
            # Use threading-based timeout for cross-platform compatibility
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
            
            def fetch_firebase_data():
                # Firebase path structure: /devices/{device_id} or /rooms/{room_number}
                # Adjust based on your Firebase structure
                ref = db.reference(f'/devices/{device_id}')
                data = ref.get()
                
                if data:
                    return {
                        'is_occupied': data.get('occupied', False) or data.get('is_occupied', False),
                        'timestamp': data.get('timestamp'),
                        'sensor_data': data
                    }
                
                # Try alternative path structure
                ref = db.reference(f'/rooms/{device_id}')
                data = ref.get()
                
                if data:
                    return {
                        'is_occupied': data.get('occupied', False) or data.get('is_occupied', False),
                        'timestamp': data.get('timestamp'),
                        'sensor_data': data
                    }
                
                return None
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fetch_firebase_data)
                try:
                    return future.result(timeout=timeout)
                except FutureTimeoutError:
                    print(f"Timeout fetching Firebase data for device {device_id} after {timeout} seconds")
                    return None
                    
        except Exception as e:
            print(f"Error fetching Firebase data for device {device_id}: {e}")
            return None
    
    def get_all_rooms_occupancy(self, timeout=5):
        """Get occupancy data for all rooms with IoT devices"""
        if FirebaseService._app is None:
            return {}
        
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
            
            def fetch_all_data():
                ref = db.reference('/devices')
                all_data = ref.get()
                return all_data if all_data else {}
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fetch_all_data)
                try:
                    return future.result(timeout=timeout)
                except FutureTimeoutError:
                    print(f"Timeout fetching all Firebase data after {timeout} seconds")
                    return {}
        except Exception as e:
            print(f"Error fetching all Firebase data: {e}")
            return {}

