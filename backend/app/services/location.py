"""
Location resolution service with fuzzy matching against landmark registry.

Resolves extracted location strings to geocoordinates without external API calls.
"""
from typing import Optional, List, Dict, Tuple
from fuzzywuzzy import fuzz, process


# In-memory landmark registry for Mumbai
# Format: "Landmark Name": (latitude, longitude, "category")
MUMBAI_LANDMARKS = {
    # Railway Stations
    "Andheri Station": (19.1197, 72.8464, "station"),
    "Andheri East": (19.1136, 72.8697, "area"),
    "Andheri West": (19.1358, 72.8269, "area"),
    "Bandra Station": (19.0544, 72.8419, "station"),
    "Bandra East": (19.0596, 72.8526, "area"),
    "Bandra West": (19.0596, 72.8295, "area"),
    "Churchgate Station": (18.9354, 72.8274, "station"),
    "Dadar Station": (19.0176, 72.8433, "station"),
    "Dadar East": (19.0189, 72.8478, "area"),
    "Dadar West": (19.0189, 72.8393, "area"),
    "Kurla Station": (19.0661, 72.8790, "station"),
    "Kurla West": (19.0728, 72.8826, "area"),
    "Kurla East": (19.0658, 72.8898, "area"),
    "Malad Station": (19.1868, 72.8482, "station"),
    "Malad East": (19.1868, 72.8569, "area"),
    "Malad West": (19.1868, 72.8395, "area"),
    "Santacruz Station": (19.0813, 72.8409, "station"),
    "Santacruz East": (19.0813, 72.8496, "area"),
    "Santacruz West": (19.0813, 72.8322, "area"),
    "Mumbai Central": (18.9689, 72.8195, "station"),
    "Borivali Station": (19.2304, 72.8577, "station"),
    "Goregaon Station": (19.1547, 72.8497, "station"),
    "Jogeshwari Station": (19.1357, 72.8490, "station"),
    "Vile Parle Station": (19.1005, 72.8444, "station"),
    "Powai": (19.1176, 72.9060, "area"),
    "Juhu": (19.1075, 72.8263, "area"),
    "Dharavi": (19.0445, 72.8547, "area"),
    
    # Hospitals
    "Cooper Hospital": (19.0562, 72.8341, "hospital"),
    "Govindi Hospital": (19.1197, 72.8464, "hospital"),  # Near Andheri
    "Lilavati Hospital": (19.0539, 72.8307, "hospital"),
    "KEM Hospital": (18.9934, 72.8413, "hospital"),
    "Sion Hospital": (19.0433, 72.8616, "hospital"),
    "Nair Hospital": (18.9888, 72.8310, "hospital"),
    
    # Landmarks & Places
    "Powai Lake": (19.1284, 72.9057, "landmark"),
    "Juhu Beach": (19.0969, 72.8266, "landmark"),
    "Gateway of India": (18.9220, 72.8347, "landmark"),
    "Marine Drive": (18.9432, 72.8236, "landmark"),
    "Versova": (19.1316, 72.8113, "area"),
    "Colaba": (18.9067, 72.8147, "area"),
    
    # Religious Places
    "Siddhivinayak Temple": (19.0168, 72.8301, "temple"),
    "Haji Ali": (18.9826, 72.8089, "mosque"),
    "Mahalaxmi Temple": (18.9755, 72.8094, "temple"),
}

# Common abbreviations and variations
LOCATION_ALIASES = {
    "andheri": "Andheri Station",
    "bandra": "Bandra Station",
    "churchgate": "Churchgate Station",
    "dadar": "Dadar Station",
    "kurla": "Kurla Station",
    "malad": "Malad Station",
    "santacruz": "Santacruz Station",
    "santa cruz": "Santacruz Station",
    "powai lake area": "Powai Lake",
    "juhu beach side": "Juhu Beach",
    "cooper hospital area": "Cooper Hospital",
}


class LocationMatch:
    """Represents a location match result."""
    
    def __init__(
        self,
        value: str,
        lat: float,
        lng: float,
        confidence: float,
        category: str,
        alternatives: Optional[List[Dict]] = None
    ):
        self.value = value
        self.lat = lat
        self.lng = lng
        self.confidence = confidence
        self.category = category
        self.alternatives = alternatives or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "value": self.value,
            "lat": self.lat,
            "lng": self.lng,
            "confidence": self.confidence,
            "category": self.category,
            "alternatives": self.alternatives,
            "is_ambiguous": self.confidence < 0.6 or len(self.alternatives) > 0
        }


def normalize_location(text: str) -> str:
    """
    Normalize location text for better matching.
    
    Args:
        text: Raw location string
        
    Returns:
        Normalized location string
    """
    # Convert to lowercase
    normalized = text.lower().strip()
    
    # Remove common words that don't help matching
    noise_words = ['near', 'at', 'in', 'area', 'ke paas', 'side']
    for word in noise_words:
        normalized = normalized.replace(word, '')
    
    # Clean up extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized


def resolve_location(
    location_text: str,
    city_context: Optional[str] = "Mumbai",
    min_confidence: float = 0.5
) -> Optional[LocationMatch]:
    """
    Resolve location text to geocoordinates using fuzzy matching.
    
    Args:
        location_text: Extracted location string from crisis message
        city_context: Optional city/district for context (default: Mumbai)
        min_confidence: Minimum confidence score to return (0.0-1.0)
        
    Returns:
        LocationMatch object with coordinates and alternatives, or None if no match
        
    Examples:
        >>> result = resolve_location("near andheri station")
        >>> result.value
        'Andheri Station'
        >>> result.lat
        19.1197
        >>> result.confidence
        0.95
    """
    if not location_text or not location_text.strip():
        return None
    
    # Normalize input
    normalized_text = normalize_location(location_text)
    
    # Check for exact alias match first
    if normalized_text in LOCATION_ALIASES:
        canonical_name = LOCATION_ALIASES[normalized_text]
        if canonical_name in MUMBAI_LANDMARKS:
            lat, lng, category = MUMBAI_LANDMARKS[canonical_name]
            return LocationMatch(
                value=canonical_name,
                lat=lat,
                lng=lng,
                confidence=1.0,  # Exact alias match
                category=category
            )
    
    # Fuzzy match against all landmarks
    # Get top 4 matches to identify alternatives
    matches = process.extract(
        normalized_text,
        MUMBAI_LANDMARKS.keys(),
        scorer=fuzz.token_sort_ratio,
        limit=4
    )
    
    if not matches:
        return None
    
    # Best match
    best_name, best_score = matches[0]
    
    # Filter out low-confidence matches
    if best_score < (min_confidence * 100):
        return None
    
    # Get coordinates for best match
    lat, lng, category = MUMBAI_LANDMARKS[best_name]
    
    # Calculate confidence (normalize score to 0-1)
    # Fuzzy scores are 0-100, we normalize and apply scaling
    confidence = min(best_score / 100.0, 1.0)
    
    # Build alternatives list (if other matches are close)
    alternatives = []
    for alt_name, alt_score in matches[1:]:
        # Only include alternatives that are reasonably close
        if alt_score >= 70:  # Within 30 points of max score
            alt_lat, alt_lng, alt_category = MUMBAI_LANDMARKS[alt_name]
            alternatives.append({
                "value": alt_name,
                "lat": alt_lat,
                "lng": alt_lng,
                "confidence": alt_score / 100.0,
                "category": alt_category
            })
    
    # Lower confidence if there are close alternatives (ambiguity penalty)
    if alternatives and (matches[1][1] >= 80):  # Second match is very close
        confidence = confidence * 0.85  # Reduce by 15%
    
    return LocationMatch(
        value=best_name,
        lat=lat,
        lng=lng,
        confidence=confidence,
        category=category,
        alternatives=alternatives
    )


def batch_resolve_locations(
    location_texts: List[str],
    city_context: Optional[str] = "Mumbai"
) -> List[Optional[LocationMatch]]:
    """
    Resolve multiple locations in batch.
    
    Args:
        location_texts: List of location strings to resolve
        city_context: Optional city/district for context
        
    Returns:
        List of LocationMatch objects (or None for unresolved)
    """
    return [resolve_location(text, city_context) for text in location_texts]


def get_nearby_landmarks(lat: float, lng: float, radius_km: float = 5.0) -> List[Dict]:
    """
    Get landmarks within radius of coordinates (simple distance calculation).
    
    Args:
        lat: Latitude
        lng: Longitude
        radius_km: Search radius in kilometers
        
    Returns:
        List of nearby landmarks with distances
    """
    import math
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km."""
        R = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    nearby = []
    for name, (landmark_lat, landmark_lng, category) in MUMBAI_LANDMARKS.items():
        distance = haversine_distance(lat, lng, landmark_lat, landmark_lng)
        if distance <= radius_km:
            nearby.append({
                "name": name,
                "lat": landmark_lat,
                "lng": landmark_lng,
                "category": category,
                "distance_km": round(distance, 2)
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby
