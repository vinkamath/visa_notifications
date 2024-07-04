import re

def check_slots_availability(message):
    if not message:
        return False

    # Define patterns that indicate no slots are available
    unavailable_patterns = [
        r'no slots available',
        r'no slots',
        r'na all',
        r'na',
        r'n\.a\.',
        r'n/a',
        r'not available'
    ]
    # Define patterns that indicate slots are available
    available_patterns = [
        r'available',
        r'slots open',
        r'slots still available',
        r'slots are available',
        r'just booked',
        r'saw',
        r'open',
        r'remaining',
        r'available for',
        r'available in',
        r'available on',
        r'available now',
        r'yes',
    ]

    # Convert the message to lowercase for case insensitive matching
    message_lower = message.lower()

    # Check if any of the negative patterns match
    for pattern in unavailable_patterns:
        if re.search(pattern, message_lower):
            return False # No slots available, do nothing

    # Check if any of the patterns match
    for pattern in available_patterns:
        if re.search(pattern, message_lower):
            return True
