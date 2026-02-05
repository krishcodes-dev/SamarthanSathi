"""
Validation service for crisis messages.

Filters out invalid, spam, or non-crisis messages before processing.
"""
import re
from typing import Tuple


# Spam detection patterns
SPAM_PATTERNS = [
    'http://',
    'https://',
    'www.',
    'prize',
    'lottery',
    'congratulations',
    'click here',
    'win now',
    'limited offer',
]

# Need keywords (crisis-related needs)
NEED_KEYWORDS = [
    # Basic needs
    'need', 'needs', 'needed', 'require', 'required', 'want', 'wants',
    # Specific resources
    'food', 'water', 'medicine', 'medical', 'doctor', 'ambulance',
    'shelter', 'blanket', 'blankets', 'clothes', 'clothing',
    'rescue', 'help', 'assistance', 'support', 'aid',
    # Hindi/Hinglish
    'chahiye', 'zarurat', 'paani', 'pani', 'khana', 'khaana',
    'dawa', 'dawai', 'madad',
]

# Urgency keywords
URGENCY_KEYWORDS = [
    'urgent', 'urgently', 'emergency', 'asap', 'immediately',
    'critical', 'serious', 'dying', 'collapsed', 'trapped',
    'injured', 'help', 'please', 'sos',
    # Hindi/Hinglish
    'turant', 'jaldi', 'abhi',
]

# Location indicators (basic)
LOCATION_KEYWORDS = [
    'at', 'near', 'in', 'location', 'address', 'area',
    'station', 'hospital', 'school', 'temple', 'mosque', 'church',
    'building', 'street', 'road', 'lane', 'nagar', 'colony',
]


def is_valid_crisis_request(text: str) -> Tuple[bool, str]:
    """
    Validate if a message is a legitimate crisis request.
    
    Args:
        text: Raw message text to validate
        
    Returns:
        Tuple of (is_valid: bool, reason: str)
        - If valid: (True, "Valid")
        - If invalid: (False, "Reason for rejection")
        
    Examples:
        >>> is_valid_crisis_request("Need 50 blankets near Andheri")
        (True, 'Valid')
        
        >>> is_valid_crisis_request("Help")
        (False, 'Message too short')
        
        >>> is_valid_crisis_request("Click here to win a prize!")
        (False, 'Potential spam detected')
    """
    # Trim whitespace
    text = text.strip()
    
    # Check 1: Minimum length
    if len(text) < 10:
        return False, "Message too short"
    
    # Check 2: Spam detection
    text_lower = text.lower()
    for pattern in SPAM_PATTERNS:
        if pattern in text_lower:
            return False, "Potential spam detected"
    
    # Check 3: Must contain at least one crisis indicator
    has_need_keyword = any(keyword in text_lower for keyword in NEED_KEYWORDS)
    has_urgency_keyword = any(keyword in text_lower for keyword in URGENCY_KEYWORDS)
    has_location_keyword = any(keyword in text_lower for keyword in LOCATION_KEYWORDS)
    
    if not (has_need_keyword or has_urgency_keyword or has_location_keyword):
        return False, "No clear crisis indicators (need/urgency/location) identified"
    
    # Passed all checks
    return True, "Valid"


def contains_need_keyword(text: str) -> bool:
    """
    Check if text contains any need-related keywords.
    
    Args:
        text: Text to check
        
    Returns:
        True if need keyword found, False otherwise
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in NEED_KEYWORDS)


def contains_urgency_keyword(text: str) -> bool:
    """
    Check if text contains any urgency-related keywords.
    
    Args:
        text: Text to check
        
    Returns:
        True if urgency keyword found, False otherwise
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in URGENCY_KEYWORDS)


def contains_location_keyword(text: str) -> bool:
    """
    Check if text contains any location-related keywords.
    
    Args:
        text: Text to check
        
    Returns:
        True if location keyword found, False otherwise
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in LOCATION_KEYWORDS)
