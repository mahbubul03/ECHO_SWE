"""
Management command to initialize 40 rooms
"""
from django.core.management.base import BaseCommand
from rooms.models import Room


class Command(BaseCommand):
    help = 'Initialize 40 rooms in the database'

    def handle(self, *args, **options):
        # Create 40 rooms (101-140)
        rooms_created = 0
        rooms_updated = 0
        
        for i in range(101, 141):
            room_number = str(i)
            room, created = Room.objects.get_or_create(
                room_number=room_number,
                defaults={
                    'has_iot_device': (i == 101),  # Only room 101 has IoT device
                    'iot_device_id': '101' if i == 101 else None
                }
            )
            
            if created:
                rooms_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created room {room_number}')
                )
            else:
                # Update existing room if needed
                if i == 101 and not room.has_iot_device:
                    room.has_iot_device = True
                    room.iot_device_id = '101'
                    room.save()
                    rooms_updated += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated room {room_number} with IoT device')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {rooms_created} rooms and updated {rooms_updated} rooms.'
            )
        )

