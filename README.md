# ECHO-Occupancy Monitor

A web-based room occupancy and reservation system built with Django, featuring real-time IoT device integration via Firebase Realtime Database.

## Features

- **User Authentication**: Sign up, login, and logout with role-based access control
- **Two User Roles**:
  - **Manager**: Can view all 40 rooms, see all occupancy and reservation data
  - **Normal User**: Can only view their rented room
- **Room Management**: 40 predefined rooms (101-140) with IoT device support
- **Reservation System**: Users can reserve available rooms
- **Real-time Occupancy Data**: Integration with Firebase Realtime Database for live IoT sensor data
- **Color-coded Room Status**:
  - **White**: Available
  - **Yellow**: Rented/Reserved
  - **Green**: Selected by current user

## Tech Stack

- **Backend**: Django 4.2.7
- **Frontend**: Django Templates (HTML, CSS, JavaScript)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time Data**: Firebase Realtime Database
- **Authentication**: Django Auth with custom User model

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ECHO
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   FIREBASE_DATABASE_URL=https://hotel-monitor-ada02-default-rtdb.firebaseio.com/
   FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Initialize rooms**:
   ```bash
   python manage.py init_rooms
   ```
   This creates 40 rooms (101-140) and sets up room 101 with an IoT device.

7. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Sign up for a new account or log in

## Firebase Setup

1. **Get Firebase Credentials**:
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate a new private key
   - Save the JSON file as `firebase-credentials.json` in your project root
   - Update `FIREBASE_CREDENTIALS_PATH` in `.env`

2. **Firebase Database Structure**:
   The app expects Firebase data in one of these structures:
   - `/devices/{device_id}` - For device-based data
   - `/rooms/{room_number}` - For room-based data

   Each entry should have:
   ```json
   {
     "occupied": true/false,
     "is_occupied": true/false,
     "timestamp": "2024-01-01T00:00:00Z"
   }
   ```

## Usage

### For Managers:
1. Sign up or log in with a Manager account
2. View the dashboard to see all 40 rooms
3. Click on any room to view detailed information
4. Monitor real-time occupancy data from IoT devices

### For Normal Users:
1. Sign up or log in with a Normal User account
2. Go to the Reservations page
3. Select an available (white) room to reserve
4. View your reserved room on the dashboard
5. View occupancy data for your room

## Project Structure

```
ECHO/
├── accounts/          # User authentication app
├── rooms/            # Room management app
├── reservations/     # Reservation system app
├── echo_occupancy/   # Main project settings
├── templates/        # HTML templates
├── static/          # CSS, JavaScript, images
├── manage.py        # Django management script
└── requirements.txt # Python dependencies
```

## Models

- **User**: Custom user model with role field (Manager/Normal User)
- **Room**: Represents the 40 rooms with IoT device information
- **Reservation**: Links users to rooms with status tracking
- **OccupancyData**: Historical occupancy data from IoT devices

## API Endpoints

- `/` - Home/Login
- `/signup/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/rooms/` - Dashboard (role-based)
- `/rooms/<room_number>/` - Room detail page
- `/reservations/` - Reservation page
- `/reservations/reserve/<room_number>/` - Reserve a room
- `/reservations/cancel/<reservation_id>/` - Cancel reservation

## Development

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Notes

- Currently, only room 101 has an IoT device configured
- Firebase integration requires proper credentials and database structure
- The app uses SQLite by default for development (change to PostgreSQL for production)
- Real-time updates can be enhanced using Firebase JavaScript SDK for instant updates

## License

This project is proprietary software for ECHO-Occupancy Monitor.

