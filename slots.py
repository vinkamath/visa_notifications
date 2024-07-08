import re

def check_slots_availability(message):
    if not message:
        return False

    # Define patterns that indicate no slots are available. 
    # Use word boundaries for whole word matches.
    unavailable_patterns = [
        r'\bno slots available\b',
        r'\bno slots\b',
        r'\bna all\b',
        r'\bna\b',
        r'\bn\.a\.\b',
        r'\bn/a\b',
        r'\bnot available\b'
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
        r'jan',
        r'feb',
        r'mar',
        r'apr',
        r'may',
        r'jun',
        r'jul',
        r'aug',
        r'sep',
        r'oct',
        r'nov',
        r'dec'
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
