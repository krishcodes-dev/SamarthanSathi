"""
Test script for urgency scoring engine.
"""
from app.services.extraction import extract_entities
from app.services.urgency import calculate_urgency


# Test messages with varying urgency levels
TEST_MESSAGES = [
    # U1 - Critical cases
    {
        "text": "Building collapsed. 5 people trapped unconscious. Location: Andheri East. Call 9876543210",
        "expected_level": "U1",
        "description": "Life-threatening + trapped + specific count"
    },
    {
        "text": "Child not breathing, need doctor immediately at Cooper Hospital",
        "expected_level": "U1",
        "description": "Life-threatening + vulnerable + medical"
    },
    {
        "text": "Multiple injured bleeding badly in accident near Bandra station",
        "expected_level": "U1",
        "description": "Multiple injured + bleeding + accident"
    },
    
    # U2 - High urgency
    {
        "text": "Fire in building, 20 families need evacuation urgently. Malad West.",
        "expected_level": "U2",
        "description": "Fire + high count + urgent"
    },
    {
        "text": "Flood trapped 8 people on terrace, rescue needed asap +919998887776",
        "expected_level": "U2",
        "description": "Trapped + rescue + specific count"
    },
    
    # U3 - Medium urgency
    {
        "text": "Need 50 blankets for 15 families affected by heavy rains. Kurla area.",
        "expected_level": "U3",
        "description": "Factual, no life threat but significant need"
    },
    {
        "text": "Food required for 100 people in shelter. Contact: 9876543210",
        "expected_level": "U3",
        "description": "Large group but not critical need"
    },
    
    # U4 - Low urgency
    {
        "text": "Need 10 blankets for tonight, location near Powai lake",
        "expected_level": "U4",
        "description": "Small need, non-critical resource"
    },
    
    # U5 - Minimal urgency
    {
        "text": "Looking for information about shelter availability in Mumbai",
        "expected_level": "U5",
        "description": "Informational query"
    },
    
    # Edge cases - Understatement detection
    {
        "text": "5 injured. Malad station. 9876543210",
        "expected_level": "U1 or U2",
        "description": "Understated critical case - short, factual, no emotion"
    },
    {
        "text": "Medical help needed. 3 children. Dadar.",
        "expected_level": "U2",
        "description": "Understated + vulnerable population"
    },
    
    # Edge case - Emotional inflation prevention
    {
        "text": "Please please help!!! We are so desperate and scared!!! Need blankets please!!!",
        "expected_level": "U4 or U5",
        "description": "Lots of emotion but no critical indicators"
    },
]


def print_urgency_analysis(test_case: dict, index: int):
    """Print detailed urgency analysis for a test case."""
    print(f"\n{'=' * 100}")
    print(f"TEST #{index + 1}: {test_case['description']}")
    print(f"Expected: {test_case['expected_level']}")
    print(f"{'=' * 100}")
    print(f"Message: {test_case['text']}")
    print(f"{'-' * 100}")
    
    # Extract entities
    extraction = extract_entities(test_case['text'])
    
    # Calculate urgency
    urgency = calculate_urgency(test_case['text'], extraction)
    
    # Display results
    print(f"\n🎯 URGENCY ANALYSIS:")
    print(f"  Level: {urgency.level}")
    print(f"  Score: {urgency.score}/100")
    print(f"  Confidence: {urgency.confidence:.2f}")
    
    print(f"\n📊 REASONING:")
    for reason in urgency.reasoning:
        print(f"  {reason}")
    
    if urgency.flags:
        print(f"\n⚠️  FLAGS:")
        for flag in urgency.flags:
            print(f"  • {flag}")
    
    # Check if expected level matches
    actual_level = urgency.level.split()[0]  # Extract "U1" from "U1 - Critical"
    expected_levels = test_case['expected_level'].split(' or ')
    
    if actual_level in expected_levels:
        print(f"\n✅ MATCH: {actual_level} == {test_case['expected_level']}")
    else:
        print(f"\n⚠️  MISMATCH: Got {actual_level}, expected {test_case['expected_level']}")


def main():
    print("\n" + "=" * 100)
    print(" " * 30 + "URGENCY SCORING ENGINE TESTS")
    print(" " * 25 + f"{len(TEST_MESSAGES)} Test Cases Across All Urgency Levels")
    print("=" * 100)
    
    for i, test_case in enumerate(TEST_MESSAGES):
        print_urgency_analysis(test_case, i)
    
    print(f"\n{'=' * 100}")
    print(f"{'✅ ALL TESTS COMPLETED':^100}")
    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    main()
