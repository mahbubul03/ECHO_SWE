from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from rooms.models import Room
from .models import Reservation
from .forms import ReservationForm


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
def reservation_page(request):
    """Reservation page where users can select and reserve rooms"""
    # Mark expired reservations as completed
    mark_expired_reservations_completed()
    
    user = request.user
    
    # Get all rooms
    all_rooms = Room.objects.all()
    
    # Get all active reservations (exclude manager reservations and completed/cancelled)
    today = timezone.now().date()
    today_dt = timezone.now()
    active_reservations = Reservation.objects.filter(
        status__in=['reserved', 'active']
    ).select_related('room', 'user').exclude(
        user__role='manager'  # Exclude manager reservations
    )
    
    # Filter reservations that are currently active (today is within reservation period)
    # A room is reserved only if today is between check-in and check-out dates
    currently_active = []
    for res in active_reservations:
        # Skip manager reservations
        if res.user.is_manager():
            continue
        
        # If reservation has dates, check if today is within the reservation period
        if res.check_in and res.check_out:
            check_in_date = res.check_in.date() if hasattr(res.check_in, 'date') else res.check_in
            check_out_date = res.check_out.date() if hasattr(res.check_out, 'date') else res.check_out
            # Room is active only if today is within the reservation period (check_in <= today <= check_out)
            if check_in_date <= today <= check_out_date:
                currently_active.append(res)
        elif res.status in ['reserved', 'active']:
            # If no dates set but status is active/reserved, consider it active
            currently_active.append(res)
    
    # Create a set of reserved room IDs (only rooms where today is within reservation period)
    reserved_room_ids = {res.room.id for res in currently_active}
    
    # Get user's current reservation
    user_reservation = None
    if not user.is_manager():
        user_reservation = Reservation.objects.filter(
            user=user,
            status__in=['reserved', 'active']
        ).order_by('-reserved_at').first()
    
    # Prepare room data with status
    # Also get all future reservations to show in UI
    all_future_reservations = Reservation.objects.filter(
        status__in=['reserved', 'active']
    ).select_related('room', 'user').exclude(
        user__role='manager'
    )
    
    rooms_data = []
    for room in all_rooms:
        is_reserved = room.id in reserved_room_ids
        reservation = next((r for r in currently_active if r.room == room), None)
        
        # Get future reservation for this room (if any) to show dates
        future_reservation = None
        if not reservation:
            future_res = next((r for r in all_future_reservations if r.room == room and r.check_in and r.check_in.date() > today), None)
            if future_res:
                future_reservation = future_res
        
        # Determine if user can select this room
        # Room can be selected if:
        # 1. Not currently reserved (today is not within reservation period)
        # 2. Or it's the user's own reservation
        can_select = not is_reserved or (reservation and reservation.user == user)
        
        # Determine color
        if reservation and reservation.user == user:
            color = 'green'  # User's selected room
        elif is_reserved:
            color = 'yellow'  # Currently rented/reserved by someone else
        elif future_reservation:
            color = 'white'  # Available but has future reservation
        else:
            color = 'white'  # Available
        
        rooms_data.append({
            'room': room,
            'is_reserved': is_reserved,
            'reservation': reservation,
            'future_reservation': future_reservation,
            'can_select': can_select,
            'color': color
        })
    
    context = {
        'rooms_data': rooms_data,
        'user_reservation': user_reservation,
        'is_manager': user.is_manager(),
    }
    
    return render(request, 'reservations/reservation_page.html', context)


@login_required
def reserve_room(request, room_number):
    """Reserve a room with date selection"""
    user = request.user
    room = get_object_or_404(Room, room_number=room_number)
    
    # Managers cannot reserve rooms
    if user.is_manager():
        messages.error(request, 'Managers cannot reserve rooms. This feature is only available for normal users.')
        return redirect('reservations:reservation_page')
    
    # Check if user already has an active reservation
    existing_reservation = Reservation.objects.filter(
        user=user,
        status__in=['reserved', 'active']
    ).first()
    
    if existing_reservation:
        if existing_reservation.room == room:
            messages.info(request, f'You already have a reservation for Room {room_number}.')
        else:
            messages.error(request, f'You already have a reservation for Room {existing_reservation.room.room_number}. Please cancel it first.')
        return redirect('reservations:reservation_page')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Get dates from form cleaned_data (they are date objects)
            check_in_date = form.cleaned_data.get('check_in_date')
            check_out_date = form.cleaned_data.get('check_out_date')
            
            # Check for date conflicts with existing reservations
            # Allow booking if dates don't overlap with existing reservations
            existing_reservations = Reservation.objects.filter(
                room=room,
                status__in=['reserved', 'active']
            ).exclude(user__role='manager')
            
            if check_in_date and check_out_date:
                # Convert to datetime for comparison
                check_in_dt = timezone.make_aware(
                    datetime.combine(check_in_date, datetime.min.time())
                )
                check_out_dt = timezone.make_aware(
                    datetime.combine(check_out_date, datetime.min.time())
                )
                
                # Check for overlapping reservations
                # Two reservations overlap if: 
                # - new check-in is between existing check-in and check-out, OR
                # - new check-out is between existing check-in and check-out, OR
                # - new reservation completely contains existing reservation
                conflicting_reservations = existing_reservations.filter(
                    check_in__isnull=False,
                    check_out__isnull=False
                ).exclude(
                    Q(check_out__lte=check_in_dt) | Q(check_in__gte=check_out_dt)
                )
                
                if conflicting_reservations.exists():
                    conflict = conflicting_reservations.first()
                    messages.error(
                        request, 
                        f'Room {room_number} is already reserved from {conflict.check_in.date()} to {conflict.check_out.date()}. Please choose different dates.'
                    )
                    return render(request, 'reservations/reserve_room.html', {
                        'form': form,
                        'room': room,
                        'room_number': room_number
                    })
            else:
                # If no dates provided, check if room has any active reservation
                active_reservation = existing_reservations.filter(
                    check_in__isnull=True,
                    check_out__isnull=True
                ).first()
                
                if active_reservation:
                    messages.error(request, f'Room {room_number} is already reserved by another user.')
                    return render(request, 'reservations/reserve_room.html', {
                        'form': form,
                        'room': room,
                        'room_number': room_number
                    })
            
            reservation = form.save(commit=False)
            reservation.user = user
            reservation.room = room
            reservation.status = 'reserved'
            
            # Convert date to datetime for check_in and check_out
            if check_in_date:
                reservation.check_in = timezone.make_aware(
                    datetime.combine(check_in_date, datetime.min.time())
                )
            if check_out_date:
                reservation.check_out = timezone.make_aware(
                    datetime.combine(check_out_date, datetime.min.time())
                )
            
            reservation.save()
            messages.success(
                request, 
                f'Room {room_number} has been reserved from {check_in_date} to {check_out_date}!'
            )
            return redirect('reservations:reservation_page')
        else:
            # If form is invalid, show errors but keep the form
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            # Re-render form with errors
            return render(request, 'reservations/reserve_room.html', {
                'form': form,
                'room': room,
                'room_number': room_number
            })
    else:
        form = ReservationForm()
    
    # If GET request, show reservation form
    return render(request, 'reservations/reserve_room.html', {
        'form': form,
        'room': room,
        'room_number': room_number
    })


@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check permissions
    if not request.user.is_manager() and reservation.user != request.user:
        messages.error(request, 'You do not have permission to cancel this reservation.')
        return redirect('reservations:reservation_page')
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(
            request, 
            f'Reservation for Room {reservation.room.room_number} has been cancelled.'
        )
        return redirect('reservations:reservation_page')
    
    return redirect('reservations:reservation_page')

