import math
from typing import List, TypeVar
from django.conf import settings

T = TypeVar('T')

def generate_jitsi_url(event_id: str, group_identifier: str) -> str:
    """
    Generate a deterministic Jitsi meeting URL for a specific group in an event.
    
    Args:
        event_id: The ID of the event.
        group_identifier: A unique identifier for the group (e.g., 'group-1').
        
    Returns:
        A complete Jitsi URL string.
    """
    domain = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')
    
    # Clean the event ID to create cleaner URLs
    clean_event_id = str(event_id).replace('-', '')
    
    # Example format: talkabout-event-1234abcd-group-1
    room_name = f"talkabout-event-{clean_event_id}-{group_identifier}"
    
    return f"https://{domain}/{room_name}"


def distribute_participants(participants: List[T], max_per_room: int) -> List[List[T]]:
    """
    Distribute participants into groups, maximizing balance across rooms.
    Ensures that participants are spread evenly to avoid solitary users.
    
    Args:
        participants: A list of participant objects (e.g. WaitingRoomParticipant).
        max_per_room: Maximum number of participants allowed in a single room.
        
    Returns:
        List of lists, where each inner list contains the participants for a room.
    """
    total = len(participants)
    
    if total < 2:
        return []
        
    if max_per_room <= 0:
        raise ValueError("max_per_room must be greater than 0")
        
    # Calculate number of rooms needed
    k = math.ceil(total / max_per_room)
    
    # Calculate base size for each room
    base_size = total // k
    
    # Calculate how many rooms will have an extra participant
    remainder = total % k
    
    rooms = []
    current_idx = 0
    
    for i in range(k):
        # The first 'remainder' rooms get base_size + 1 participants
        room_size = base_size + 1 if i < remainder else base_size
        
        # Slice the participants array for this room
        room_participants = participants[current_idx:current_idx + room_size]
        rooms.append(room_participants)
        
        current_idx += room_size
        
    # Post-process: Ensure no room has exactly 1 participant (since total >= 2)
    # Rule: Minimum 2 per room is strictly more important than max_per_room
    rooms_to_keep = []
    singles = []
    
    for r in rooms:
        if len(r) == 1:
            singles.extend(r)
        else:
            rooms_to_keep.append(r)
            
    # Merge singles into the smallest available rooms
    for single in singles:
        if not rooms_to_keep:
            # Fallback (should not happen with total >= 2)
            rooms_to_keep.append([single])
        else:
            # Find the smallest room and append the single participant
            rooms_to_keep.sort(key=len)
            rooms_to_keep[0].append(single)
            
    return rooms_to_keep
