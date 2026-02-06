from typing import Tuple, List

def validate_crisis_message(text: str) -> Tuple[bool, List[str]]:
    """
    Validate if message is a legitimate crisis request.
    
    Checks for:
    1. Length (too short/long)
    2. Spam keywords
    3. Urgent intent indicators
    
    Returns: (is_valid, error_messages)
    """
    errors = []
    
    # Empty check
    if not text or not text.strip():
        return False, ["Message cannot be empty"]

    cleaned_text = text.strip()

    # Length check
    if len(cleaned_text) < 10:
        errors.append("Message too short (min 10 characters)")
    
    if len(cleaned_text) > 500:
        errors.append("Message too long (max 500 characters)")
    
    # Spam detection
    spam_keywords = ['click here', 'winner', 'prize', 'lottery', 'buy now', 'offer', 'casino', 'subscribe', 'visit our website']
    if any(spam in text.lower() for spam in spam_keywords):
        errors.append("Potential spam content detected")
    
    # Must have some urgent intent OR clear location keywords
    # Must have some urgent intent OR clear location keywords
    urgent_keywords = [
        # English
        'need', 'require', 'help', 'urgent', 'emergency', 'trapped', 'injured', 
        'fire', 'flood', 'collapse', 'stuck', 'accident', 'critical', 'save', 
        'casualty', 'supply', 'food', 'water', 'ambulance', 'medicine', 'hospital',
        'doctor', 'bleeding', 'pain', 'burning', 'please', 'sos', 'rescue',
        # Hinglish/Hindi
        'madad', 'bachao', 'chahiye', 'jarurat', 'khana', 'pani', 'dawa',
        'aag', 'phas', 'gaya', 'accident', 'mar', 'dawakhana'
    ]
    
    has_need_indicator = any(word in text.lower() for word in urgent_keywords)
    
    # Relaxed location check: Look for common prepositions or location keywords
    location_keywords = [
        'at', 'in', 'near', 'from', 'location', 'address', 'bldg', 'road', 
        'st', 'marg', 'lane', 'opp', 'behind', 'near', 'sector', 'plot',
        'gali', 'chowk', 'nagar', 'colony', 'apartment', 'flat'
    ]
    has_location_indicator = any(kw in text.lower() for kw in location_keywords)
    
    # Also check for numbers (often indicates address or quantity)
    has_number = any(char.isdigit() for char in text)

    # Allow if urgency keywords OR location indicators are found
    if not has_need_indicator and not (has_location_indicator or has_number):
        errors.append("Message lacks clear indicators of a crisis (e.g., 'help', 'need', 'fire', or location)")
    
    return (len(errors) == 0, errors)
