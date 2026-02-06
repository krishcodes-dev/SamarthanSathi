"""
Entity extraction service for crisis messages.

Uses SpaCy NLP + custom rules to extract structured information from raw crisis text.
"""
import re
from typing import Optional, List, Tuple
import spacy
import phonenumbers
from phonenumbers import NumberParseException

from app.schemas.crisis import EntityExtraction


# Load SpaCy model (medium English model)
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("⚠️  SpaCy model 'en_core_web_md' not found. Run: python -m spacy download en_core_web_md")
    nlp = None


# Resource type keywords mapping with Hindi/Hinglish
RESOURCE_TYPE_KEYWORDS = {
    'medical': [
        'doctor', 'doctors', 'ambulance', 'ambulances', 'medicine', 'medicines',
        'medical', 'hospital', 'clinic', 'oxygen', 'ventilator', 'icu',
        'injured', 'injury', 'wound', 'bleeding', 'unconscious',
        'dawa', 'dawai', 'hospital', 'daktar',
    ],
    'food': [
        'food', 'meal', 'meals', 'rice', 'bread', 'grain', 'ration',
        'hunger', 'hungry', 'starving', 'nutrition',
        'khana', 'khaana', 'bhojan', 'roti', 'dal', 'chawal',
    ],
    'water': [
        'water', 'drinking water', 'tanker', 'bottle', 'bottles',
        'thirsty', 'dehydrated',
        'paani', 'pani', 'jal',
    ],
    'shelter': [
        'shelter', 'tent', 'tents', 'accommodation', 'room', 'house',
        'roof', 'temporary housing', 'homeless',
    ],
    'rescue': [
        # Core rescue terms
        'rescue', 'trapped', 'stuck', 'stranded',
        
        # Collapse terms
        'collapse', 'collapsed', 'collapsing', 'caved in',
        'building collapse', 'building collapsed', 'structure collapse',
        
        # Fire terms
        'fire', 'fires', 'burning', 'burnt', 'smoke',
        'fire brigade', 'fire department', 'firefighters',
        
        # Flood terms
        'flood', 'flooded', 'flooding', 'floodwater',
        
        # Natural disasters
        'earthquake', 'landslide', 'tree fell', 'debris', 'rubble',
    ],
    'transport': [
        'transport', 'vehicle', 'bus', 'car', 'truck', 'evacuation',
        'evacuate', 'move',
    ],
    'blankets': [
        'blanket', 'blankets', 'warm clothes', 'clothing', 'clothes',
        'kambal',
    ],
}

# Quantity patterns for different contexts
QUANTITY_PATTERNS = {
    'explicit_count': [
        r'\b(\d+)\s*(?:blankets?|bottles?|packets?|bags?|units?|doses?)',
        r'(?:need|require|want)\s+(\d+)',
    ],
    'people_count': [
        r'\b(\d+)\s*(?:people|persons|individuals|victims)',
    ],
    'families_count': [
        r'\b(\d+)\s*families',
    ],
    'injured_count': [
        r'\b(\d+)\s*(?:injured|wounded|hurt|casualties)',
    ],
}

# Qualitative quantity indicators
QUALITATIVE_QUANTITIES = {
    'multiple': 0.5,
    'many': 0.6,
    'several': 0.4,
    'few': 0.3,
    'couple': 0.2,
}


def extract_need_types(text: str) -> Tuple[Optional[str], Optional[str], float]:
    """
    Extract primary and secondary need types from text.
    
    Args:
        text: Raw crisis message text
        
    Returns:
        Tuple of (primary_need: str | None, secondary_need: str | None, confidence: float)
    """
    text_lower = text.lower()
    
    # Count matches for each resource type
    match_scores = {}
    for resource_type, keywords in RESOURCE_TYPE_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > 0:
            match_scores[resource_type] = matches
    
    if not match_scores:
        return None, None, 0.0
    
    # Sort by match count
    sorted_types = sorted(match_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Primary need
    primary_type = sorted_types[0][0]
    primary_matches = sorted_types[0][1]
    
    # Secondary need (if significantly different from primary)
    secondary_type = None
    if len(sorted_types) > 1 and sorted_types[1][1] >= 1:
        secondary_type = sorted_types[1][0]
    
    # Calculate confidence based on primary matches
    confidence = min(0.5 + (primary_matches * 0.15), 1.0)
    
    return primary_type, secondary_type, confidence


def extract_quantities(text: str) -> dict:
    """
    Extract quantities with context-aware parsing.
    
    Returns dict with:
    - resource_quantity: int | None (explicit resource count)
    - affected_count: str | int | None (people/families affected)
    - confidence: float
    """
    result = {
        'resource_quantity': None,
        'affected_count': None,
        'confidence': 0.0,
    }
    
    # Extract explicit resource quantities
    resource_quantities = []
    for pattern in QUANTITY_PATTERNS['explicit_count']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        resource_quantities.extend([int(m) for m in matches])
    
    # Extract people counts
    people_counts = []
    for pattern in QUANTITY_PATTERNS['people_count']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        people_counts.extend([int(m) for m in matches])
    
    # Extract families counts (convert to affected_count as string for now)
    families_matches = re.findall(QUANTITY_PATTERNS['families_count'][0], text, re.IGNORECASE)
    if families_matches:
        result['affected_count'] = f"{families_matches[0]} families"
    
    # Extract injured counts
    injured_matches = re.findall(QUANTITY_PATTERNS['injured_count'][0], text, re.IGNORECASE)
    if injured_matches:
        if not result['affected_count']:
            result['affected_count'] = f"{injured_matches[0]} injured"
    
    # Check for qualitative indicators
    text_lower = text.lower()
    for qualifier, _ in QUALITATIVE_QUANTITIES.items():
        if qualifier in text_lower:
            if 'injured' in text_lower or 'wounded' in text_lower:
                result['affected_count'] = f"{qualifier} injured"
                result['confidence'] = 0.4  # Low confidence for qualitative
                return result
            elif not result['affected_count']:
                result['affected_count'] = qualifier
                result['confidence'] = 0.3
    
    # Set resource quantity
    if resource_quantities:
        result['resource_quantity'] = max(resource_quantities)
        result['confidence'] = 0.9
    elif people_counts:
        # If only people count, use it as affected_count
        if not result['affected_count']:
            result['affected_count'] = str(people_counts[0])
        result['confidence'] = 0.8
    
    return result


def extract_phone(text: str) -> Optional[str]:
    """
    Extract Indian phone number from text using phonenumbers library.
    
    Args:
        text: Raw crisis message text
        
    Returns:
        Formatted phone number in E.164 format (+919876543210) or None
    """
    try:
        # Try to find Indian phone numbers
        for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
            phone = phonenumbers.format_number(
                match.number,
                phonenumbers.PhoneNumberFormat.E164
            )
            return phone
    except NumberParseException:
        pass
    
    # Fallback: regex for 10-digit numbers
    pattern = r'\b(\d{10})\b'
    match = re.search(pattern, text)
    if match:
        return f"+91{match.group(1)}"
    
    return None


def extract_location_spacy(text: str) -> Tuple[Optional[str], float, Optional[List[str]]]:
    """
    Extract location using SpaCy NER + custom patterns.
    
    Args:
        text: Raw crisis message text
        
    Returns:
        Tuple of (location: str | None, confidence: float, alternatives: List[str] | None)
    """
    locations = []
    
    # Use SpaCy NER if available
    if nlp:
        doc = nlp(text)
        # Extract GPE (Geo-Political Entity) and LOC entities
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:  # FAC = Facility
                locations.append(ent.text)
    
    # Fallback to pattern matching if SpaCy didn't find anything
    if not locations:
        location_patterns = [
            r'(?:at|near|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:location|address):\s*(.+?)(?:\.|,|$)',
            r'([A-Z][a-z]+\s+(?:Station|Hospital|School|Temple|Mosque|Church|Building))',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)
    
    if not locations:
        return None, 0.0, None
    
    # Clean and deduplicate
    locations = [loc.strip() for loc in locations]
    locations = list(dict.fromkeys(locations))  # Preserve order, remove duplicates
    
    # Primary location
    location = locations[0]
    
    # Alternatives
    alternatives = locations[1:] if len(locations) > 1 else None
    
    # Confidence based on source
    if nlp and any(ent.text == location for ent in nlp(text).ents):
        confidence = 0.85  # SpaCy NER is more reliable
    elif re.search(r'(?:location|address):', text, re.IGNORECASE):
        confidence = 0.9  # Explicit label
    elif re.search(r'(?:at|near|in)\s+', text, re.IGNORECASE):
        confidence = 0.75  # Has preposition
    else:
        confidence = 0.6  # Pattern matched
    
    return location, confidence, alternatives


def extract_entities(text: str) -> EntityExtraction:
    """
    Extract all entities from crisis message text using SpaCy + custom rules.
    
    Args:
        text: Raw crisis message text
        
    Returns:
        EntityExtraction schema with all extracted entities and confidence scores
    """
    # Extract each entity type
    primary_need, secondary_need, need_confidence = extract_need_types(text)
    quantities = extract_quantities(text)
    location, location_confidence, location_alternatives = extract_location_spacy(text)
    phone = extract_phone(text)
    
    # Determine which need to report as primary
    # If we have both primary and secondary, store secondary in a note
    need_type = primary_need
    
    return EntityExtraction(
        need_type=need_type,
        need_type_confidence=need_confidence if need_type else None,
        quantity=quantities.get('resource_quantity'),
        quantity_confidence=quantities.get('confidence') if quantities.get('resource_quantity') else None,
        location=location,
        location_confidence=location_confidence if location else None,
        location_alternatives=location_alternatives,
        latitude=None,  # Will be added in geocoding phase
        longitude=None,  # Will be added in geocoding phase
        contact=phone,
        affected_count=quantities.get('affected_count'),
    )
