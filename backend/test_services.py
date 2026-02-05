"""
Comprehensive test script for enhanced entity extraction with SpaCy.
Tests 10 messy, real-world crisis messages.
"""
from app.services.validation import is_valid_crisis_request
from app.services.extraction import extract_entities


# 10 messy, real-world test messages
MESSY_TEST_MESSAGES = [
    # Test 1: Multi-need with families count
    "building collapsed near govindi hospital andheri!!! need rescue team AND medical help for 15 families trapped inside call 9876543210 URGENT!!!",
    
    # Test 2: Multiple injured with qualitative count
    "multiple injured in accident at bandra station, need ambulance immediately, bleeding badly",
    
    # Test 3: Hindi/English mix with location variations
    "paani ki bahut zarurat hai.. around 50 bottles chahiye near malad mandir or andheri temple pls send urgent contact ramesh 98765-43210",
    
    # Test 4: Families + explicit resource count
    "20 families homeless after fire, need 80 blankets and food packets for tonight, location: Cooper Hospital area",
    
    # Test 5: Only qualitative indicators
    "several people trapped in debris near churchgate, rescue needed asap, many injured",
    
    # Test 6: Mixed Hindi with injured count
    "5 bachche injured badly, doctor chahiye turant, Dadar station ke paas",
    
    # Test 7: No phone, multiple locations
    "flood in kurla west near station also dharavi affected, need food and water for hundreds of people",
    
    # Test 8: Hinglish with unclear count
    "bahut log hungry hai, khana bhejo please, juhu beach side",
    
    # Test 9: Secondary need embedded
    "stuck on terrace after flood!! primary need is RESCUE but also running out of water, 8 people here at santacruz west +919998887776",
    
    # Test 10: Messy formatting with multiple resources
    "HELP!!! 30blankets+100 food packets wanted immediately location:::: powai lake area.. 25families affected fire accident... no contact number available..",
]


def print_extraction_results(test_num: int, text: str):
    """Print detailed extraction results for a test message."""
    print(f"\n{'=' * 100}")
    print(f"TEST #{test_num}")
    print(f"{'=' * 100}")
    print(f"Message: {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"{'-' * 100}")
    
    # Validation
    is_valid, reason = is_valid_crisis_request(text)
    print(f"\n✓ Validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"  Reason: {reason}")
    
    if not is_valid:
        return
    
    # Extraction
    entities = extract_entities(text)
    print(f"\n✓ Entity Extraction Results:")
    
    # Need type
    if entities.need_type:
        print(f"  🎯 Need Type: {entities.need_type}")
        print(f"     Confidence: {entities.need_type_confidence:.2f}")
    else:
        print(f"  🎯 Need Type: ❌ Not detected")
    
    # Quantities
    if entities.quantity:
        print(f"  📦 Resource Quantity: {entities.quantity}")
        print(f"     Confidence: {entities.quantity_confidence:.2f}")
    
    if entities.affected_count:
        print(f"  👥 Affected Count: {entities.affected_count}")
    
    # Location
    if entities.location:
        print(f"  📍 Location: {entities.location}")
        print(f"     Confidence: {entities.location_confidence:.2f}")
        if entities.location_alternatives:
            print(f"     Alternatives: {', '.join(entities.location_alternatives)}")
    else:
        print(f"  📍 Location: ❌ Not detected")
    
    # Contact
    if entities.contact:
        print(f"  📞 Contact: {entities.contact}")
    else:
        print(f"  📞 Contact: ❌ Not detected")


def main():
    print("\n" + "=" * 100)
    print(" " * 30 + "ENHANCED EXTRACTION SERVICE TESTS")
    print(" " * 35 + "10 Messy Real-World Messages")
    print("=" * 100)
    
    for i, message in enumerate(MESSY_TEST_MESSAGES, 1):
        print_extraction_results(i, message)
    
    print(f"\n{'=' * 100}")
    print(f"{'✅ ALL 10 TESTS COMPLETED':^100}")
    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    main()
