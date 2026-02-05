"""
Test script for location resolution service.
"""
from app.services.location import resolve_location


# Test locations from previous extraction tests
TEST_LOCATIONS = [
    # Clear matches
    "Andheri Station",
    "Cooper Hospital area",
    "Powai Lake area",
    
    # With noise words
    "near malad mandir",
    "at bandra station",
    "in kurla west",
    
    # Lowercase/messy
    "juhu beach side",
    "santacruz west",
    "dadar station ke paas",
    
    # Ambiguous
    "andheri",  # Could be Andheri East, West, or Station
    "hospital",  # Multiple hospitals
    
    # Typos
    "anderi station",  # Missing 'h'
    "banda station",   # Missing 'r'
    
    # Not in registry
    "xyz random place",
    "govindi hospital andheri",  # Complex, has govindi
]


def print_resolution_result(location_text: str):
    """Print detailed resolution results for a location."""
    print(f"\n{'=' * 100}")
    print(f"Input: '{location_text}'")
    print(f"{'-' * 100}")
    
    result = resolve_location(location_text)
    
    if result:
        result_dict = result.to_dict()
        
        print(f"\n✅ RESOLVED")
        print(f"  📍 Best Match: {result.value}")
        print(f"  🗺️  Coordinates: ({result.lat}, {result.lng})")
        print(f"  📊 Confidence: {result.confidence:.2f}")
        print(f"  🏷️  Category: {result.category}")
        
        if result_dict['is_ambiguous']:
            print(f"  ⚠️  Status: AMBIGUOUS (confidence < 0.6 or has alternatives)")
        
        if result.alternatives:
            print(f"\n  🔄 Alternatives ({len(result.alternatives)}):")
            for i, alt in enumerate(result.alternatives, 1):
                print(f"     {i}. {alt['value']} (confidence: {alt['confidence']:.2f})")
    else:
        print(f"\n❌ NOT RESOLVED")
        print(f"  No matching landmarks found")


def main():
    print("\n" + "=" * 100)
    print(" " * 35 + "LOCATION RESOLUTION TESTS")
    print(" " * 30 + f"{len(TEST_LOCATIONS)} Test Cases with Fuzzy Matching")
    print("=" * 100)
    
    for location in TEST_LOCATIONS:
        print_resolution_result(location)
    
    print(f"\n{'=' * 100}")
    print(f"{'✅ ALL TESTS COMPLETED':^100}")
    print(f"{'=' * 100}\n")
    
    # Additional: Demonstrate nearby landmarks
    print("\n" + "=" * 100)
    print(" " * 35 + "BONUS: NEARBY LANDMARKS")
    print("=" * 100)
    
    from app.services.location import get_nearby_landmarks
    
    # Get landmarks near Andheri Station
    result = resolve_location("Andheri Station")
    if result:
        print(f"\nLandmarks within 3km of Andheri Station:")
        nearby = get_nearby_landmarks(result.lat, result.lng, radius_km=3.0)
        for landmark in nearby[:5]:  # Top 5
            print(f"  • {landmark['name']} - {landmark['distance_km']}km ({landmark['category']})")


if __name__ == "__main__":
    main()
