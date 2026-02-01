/**
 * Real-time occupancy data updates using Firebase
 * This script can be extended to use Firebase JavaScript SDK for real-time updates
 */

// Function to update room occupancy status in real-time
function updateRoomOccupancy(roomNumber, occupancyData) {
    const roomCard = document.querySelector(`[data-room-number="${roomNumber}"]`);
    if (!roomCard) return;

    const statusBadge = roomCard.querySelector('.room-status .badge');
    const realtimeIndicator = roomCard.querySelector('.realtime-indicator');

    if (occupancyData && occupancyData.is_occupied) {
        // Update to occupied status
        if (statusBadge) {
            statusBadge.textContent = 'Occupied';
            statusBadge.className = 'badge badge-yellow';
        }
        roomCard.classList.remove('room-white');
        roomCard.classList.add('room-yellow');
    } else {
        // Update to available status (if not reserved)
        const isReserved = roomCard.classList.contains('room-yellow') && 
                          !roomCard.classList.contains('room-green');
        
        if (!isReserved && statusBadge) {
            statusBadge.textContent = 'Available';
            statusBadge.className = 'badge badge-white';
            roomCard.classList.remove('room-yellow');
            roomCard.classList.add('room-white');
        }
    }

    // Show real-time indicator
    if (realtimeIndicator) {
        realtimeIndicator.style.display = 'inline-block';
    }
}

// Poll for real-time updates (fallback if WebSocket/Firebase JS SDK not available)
function pollOccupancyUpdates() {
    // This would typically use Firebase JavaScript SDK or WebSocket
    // For now, we'll use a polling mechanism as a fallback
    
    const roomsWithIoT = document.querySelectorAll('.room-card[data-has-iot="true"]');
    
    roomsWithIoT.forEach(roomCard => {
        const roomNumber = roomCard.getAttribute('data-room-number');
        
        // Fetch occupancy data from Django backend
        fetch(`/api/rooms/${roomNumber}/occupancy/`)
            .then(response => response.json())
            .then(data => {
                if (data && data.occupancy_data) {
                    updateRoomOccupancy(roomNumber, data.occupancy_data);
                }
            })
            .catch(error => {
                console.error('Error fetching occupancy data:', error);
            });
    });
}

// Initialize real-time updates when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Poll every 5 seconds for updates (adjust as needed)
    // setInterval(pollOccupancyUpdates, 5000);
    
    // Note: For production, implement Firebase JavaScript SDK for real-time updates
    // This would provide instant updates without polling
});

// Add room number data attributes to room cards for easier selection
document.addEventListener('DOMContentLoaded', function() {
    const roomCards = document.querySelectorAll('.room-card');
    roomCards.forEach(card => {
        const roomNumber = card.querySelector('.room-number');
        if (roomNumber) {
            const number = roomNumber.textContent.trim().replace('Room ', '');
            card.setAttribute('data-room-number', number);
            
            // Check if room has IoT device
            const iotBadge = card.querySelector('.iot-badge');
            if (iotBadge) {
                card.setAttribute('data-has-iot', 'true');
            }
        }
    });
});

