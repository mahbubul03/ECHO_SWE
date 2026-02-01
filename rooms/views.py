from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import Room
from reservations.models import Reservation


def mark_expired_reservations_completed():
    """Mark reservations as completed if check-out date has passed"""
    today = timezone.now().date()
    expired_reservations = Reservation.objects.filter(
        status__in=['reserved', 'active'],
        check_out__isnull=False
    )
    
    for reservation in expired_reservations:
        if reservation.check_out.date() < today:
            reservation.status = 'completed'
            reservation.save()


@login_required
def dashboard(request):
    """Role-based dashboard view"""
    # Mark expired reservations as completed
    mark_expired_reservations_completed()
    
    user = request.user
    
    if user.is_manager():
        # Manager can see all rooms
        rooms = Room.objects.all()
    else:
        # Normal user can only see their rented room
        user_reservation = Reservation.objects.filter(
            user=user,
            status__in=['reserved', 'active']
        ).first()
        
        if user_reservation:
            rooms = Room.objects.filter(id=user_reservation.room.id)
        else:
            rooms = Room.objects.none()
    
    # Get occupancy status for each room
    today = timezone.now().date()
    rooms_data = []
    for room in rooms:
        status = room.get_current_occupancy_status()
        # Exclude manager reservations and check if today is within reservation period
        all_reservations = Reservation.objects.filter(
            room=room,
            status__in=['reserved', 'active']
        ).exclude(user__role='manager')
        
        # Find reservation where today is within the reservation period
        reservation = None
        for res in all_reservations:
            if res.check_in and res.check_out:
                check_in_date = res.check_in.date() if hasattr(res.check_in, 'date') else res.check_in
                check_out_date = res.check_out.date() if hasattr(res.check_out, 'date') else res.check_out
                if check_in_date <= today <= check_out_date:
                    reservation = res
                    break
            elif not res.check_in and not res.check_out:
                # If no dates, consider it active
                reservation = res
                break
        
        # Determine room color
        if reservation and reservation.user == user:
            color = 'green'  # User's selected room
        elif reservation:
            color = 'yellow'  # Currently rented/reserved by someone else
        elif status['is_occupied']:
            color = 'yellow'  # Occupied
        else:
            color = 'white'  # Available
        
        rooms_data.append({
            'room': room,
            'status': status,
            'reservation': reservation,
            'color': color
        })
    
    context = {
        'rooms_data': rooms_data,
        'is_manager': user.is_manager(),
        'user': user
    }
    
    return render(request, 'rooms/dashboard.html', context)


@login_required
def room_detail(request, room_number):
    """Room detail view with occupancy data"""
    room = get_object_or_404(Room, room_number=room_number)
    user = request.user
    
    # Check permissions
    if not user.is_manager():
        # Normal user can only view their own room
        user_reservation = Reservation.objects.filter(
            user=user,
            room=room,
            status__in=['reserved', 'active']
        ).first()
        
        if not user_reservation:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'You do not have permission to view this room.')
            return redirect('rooms:dashboard')
    
    # Get current occupancy status
    status = room.get_current_occupancy_status()
    
    # Get reservation info (exclude manager reservations)
    reservation = Reservation.objects.filter(
        room=room,
        status__in=['reserved', 'active']
    ).exclude(user__role='manager').first()
    
    # Get historical occupancy data
    occupancy_history = room.occupancy_history.all()[:50]  # Last 50 records
    
    context = {
        'room': room,
        'status': status,
        'reservation': reservation,
        'occupancy_history': occupancy_history,
        'is_manager': user.is_manager(),
    }
    
    return render(request, 'rooms/room_detail.html', context)

