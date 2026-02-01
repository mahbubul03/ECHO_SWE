# Quick Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional):
   Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   FIREBASE_DATABASE_URL=https://hotel-monitor-ada02-default-rtdb.firebaseio.com/
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   ```
   
   Note: If you don't create a `.env` file, the app will use default values but Firebase won't work without credentials.

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Initialize 40 rooms**:
   ```bash
   python manage.py init_rooms
   ```
   This creates rooms 101-140, with room 101 configured for IoT device.

6. **Create a superuser** (optional, for admin panel):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Open browser: `http://127.0.0.1:8000/`
   - Sign up for a new account
   - Choose role: Manager or Normal User

## Firebase Setup (Optional but Recommended)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `hotel-monitor-ada02`
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Save the JSON file as `firebase-credentials.json` in the project root
6. Update `FIREBASE_CREDENTIALS_PATH` in `.env` file

## Testing the Application

1. **Create a Manager account**:
   - Sign up with role "Manager"
   - You'll see all 40 rooms on the dashboard

2. **Create a Normal User account**:
   - Sign up with role "Normal User"
   - Go to Reservations page
   - Select an available (white) room to reserve
   - View your reserved room on the dashboard

3. **Test Room Colors**:
   - White = Available
   - Yellow = Reserved/Occupied
   - Green = Your selected room

## Troubleshooting

- **Firebase errors**: The app will work without Firebase, but real-time occupancy data won't be available
- **Database errors**: Make sure you've run migrations
- **Static files not loading**: Run `python manage.py collectstatic` (for production)

## Next Steps

- Configure Firebase credentials for real-time data
- Customize room numbers if needed
- Add more IoT devices for other rooms
- Deploy to production server

