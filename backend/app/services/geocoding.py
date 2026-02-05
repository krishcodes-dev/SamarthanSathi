"""
Hybrid geocoding service combining local cache with external API fallback.

Uses a tiered approach:
1. Fast local fuzzy matching against landmark cache
2. Fallback to Nominatim (OpenStreetMap) for novel locations
3. Cache successful API results for future requests
"""
from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Import existing fuzzy matching
from app.services.location import resolve_location as fuzzy_resolve_location


# Initialize geocoder (lazy to avoid startup delay)
_geolocator = None

def _get_geolocator():
    """Lazy initialization of geocoder."""
    global _geolocator
    if _geolocator is None:
        _geolocator = Nominatim(
            user_agent="samarthansathi_crisis_dispatcher",
            timeout=3  # Fast timeout for demo safety
        )
    return _geolocator


# Simple in-memory cache for geocoded results
_geocode_cache = {}


def resolve_location_smart(location_text: str, default_region: str = "Mumbai, India") -> Optional[Dict]:
    """
    Geocode location using Nominatim API with caching.
    
    Handles ANY location without hardcoded lists:
    - "R City Mall Ghatkopar" → coordinates
    - "near big temple Malad" → best guess coordinates
    - Typos automatically corrected by OSM
    
    Args:
        location_text: Location string extracted from crisis message
        default_region: Default region to bias results
        
    Returns:
        Dict with location_name, lat, lng, confidence, source
    """
    # Check cache first
    cache_key = location_text.lower().strip()
    if cache_key in _geocode_cache:
        cached = _geocode_cache[cache_key].copy()
        cached['source'] = 'geocoder_cache'
        return cached
    
    geolocator = _get_geolocator()
    
    try:
        # Try exact match with region first
        full_query = f"{location_text}, {default_region}"
        location = geolocator.geocode(full_query)
        
        if location:
            result = {
                'location_name': location.address,
                'lat': location.latitude,
                'lng': location.longitude,
                'confidence': 0.85,  # High confidence for exact match
                'source': 'geocoder',
                'raw_location': location_text
            }
            # Cache successful result
            _geocode_cache[cache_key] = result.copy()
            return result
        
        # Fallback: Try without region (less confident)
        location = geolocator.geocode(location_text)
        if location:
            result = {
                'location_name': location.address,
                'lat': location.latitude,
                'lng': location.longitude,
                'confidence': 0.65,  # Lower confidence (could be wrong city)
                'source': 'geocoder_fallback',
                'raw_location': location_text,
                'flags': ['verify_city']
            }
            # Cache this too
            _geocode_cache[cache_key] = result.copy()
            return result
        
        return None
        
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        # Network issues - graceful degradation
        print(f"⚠️  Geocoding API failed for '{location_text}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected geocoding error: {e}")
        return None


def resolve_location_hybrid(location_text: str) -> Dict:
    """
    Hybrid location resolution combining fast local cache with external API.
    
    Strategy:
    1. Try local fuzzy matching first (fast, accurate for known places)
    2. Fall back to geocoding API for unknown locations
    3. Return best available result with confidence scoring
    
    Args:
        location_text: Location string to resolve
        
    Returns:
        Dict with location_name, lat, lng, confidence, source, flags
    """
    if not location_text:
        return {
            'location_name': None,
            'lat': None,
            'lng': None,
            'confidence': 0.0,
            'source': 'none',
            'flags': ['missing_location']
        }
    
    # Step 1: Try local fuzzy matching (your current landmarks)
    local_result = fuzzy_resolve_location(location_text)
    
    # If high-confidence local match, return immediately (fast path)
    if local_result and local_result.confidence and local_result.confidence > 0.85:
        return {
            'location_name': local_result.value,
            'lat': local_result.lat,
            'lng': local_result.lng,
            'confidence': local_result.confidence,
            'source': 'local_cache',
            'method': 'fuzzy_match'
        }
    
    # Step 2: Try external geocoding API (slow but comprehensive)
    api_result = resolve_location_smart(location_text)
    
    if api_result:
        # Use API result if better than local or if local failed
        if not local_result or api_result['confidence'] > local_result.confidence:
            # Preserve local alternatives if they exist (valuable context)
            if local_result and hasattr(local_result, 'alternatives') and local_result.alternatives:
                api_result['alternatives'] = local_result.alternatives[:3]
                # Flag that we have ambiguity despite API match
                if 'flags' not in api_result:
                    api_result['flags'] = []
                api_result['flags'].append('ambiguous_location')
            
            return api_result
    
    # Step 3: Return local result if we have one (even if low confidence)
    if local_result:
        result = {
            'location_name': local_result.value,
            'lat': local_result.lat,
            'lng': local_result.lng,
            'confidence': local_result.confidence,
            'source': 'local_cache',
            'method': 'fuzzy_match_uncertain'
        }
        
        # Add alternatives if available
        if hasattr(local_result, 'alternatives') and local_result.alternatives:
            result['alternatives'] = local_result.alternatives[:3]
        
        return result
    
    # Step 4: No resolution possible
    return {
        'location_name': location_text,
        'lat': None,
        'lng': None,
        'confidence': 0.2,
        'source': 'none',
        'flags': ['ambiguous_location', 'manual_verification_needed'],
        'raw_text': location_text
    }
