"""
Test script for resource matching engine.
"""
from app.models.crisis import Resource, ResourceType, AvailabilityStatus
from app.services.matching import match_crisis_request
import uuid


# Create mock resources for testing
MOCK_RESOURCES = [
    # Medical resources
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.MEDICAL,
        provider_name="Cooper Hospital",
        quantity_available=10,
        latitude=19.0562,
        longitude=72.8341,
        location_name="Cooper Hospital, Juhu",
        availability_status=AvailabilityStatus.AVAILABLE
    ),
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.MEDICAL,
        provider_name="Lilavati Hospital",
        quantity_available=5,
        latitude=19.0539,
        longitude=72.8307,
        location_name="Lilavati Hospital, Bandra",
        availability_status=AvailabilityStatus.AVAILABLE
    ),
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.MEDICAL,
        provider_name="KEM Hospital",
        quantity_available=20,
        latitude=18.9934,
        longitude=72.8413,
        location_name="KEM Hospital, Parel",
        availability_status=AvailabilityStatus.PARTIALLY_AVAILABLE
    ),
    
    # Blankets
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.BLANKETS,
        provider_name="Andheri Relief Center",
        quantity_available=100,
        latitude=19.1197,
        longitude=72.8464,
        location_name="Andheri Station",
        availability_status=AvailabilityStatus.AVAILABLE
    ),
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.BLANKETS,
        provider_name="Malad Shelter",
        quantity_available=30,
        latitude=19.1868,
        longitude=72.8482,
        location_name="Malad Station",
        availability_status=AvailabilityStatus.AVAILABLE
    ),
    
    # Food
    Resource(
        id=uuid.uuid4(),
        resource_type=ResourceType.FOOD,
        provider_name="Bandra Kitchen",
        quantity_available=200,
        latitude=19.0544,
        longitude=72.8419,
        location_name="Bandra Station",
        availability_status=AvailabilityStatus.AVAILABLE
    ),
]


# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Critical Medical - Close by",
        "request": {
            "latitude": 19.0550,  # Near Bandra
            "longitude": 72.8350,
            "need_type": "medical",
            "quantity": 3,
            "urgency_score": 95,
            "urgency_level": "U1 - Critical"
        },
        "description": "Critical case near Bandra hospitals"
    },
    {
        "name": "High Urgency - Partial Fulfillment",
        "request": {
            "latitude": 19.0000,  # South Mumbai
            "longitude": 72.8200,
            "need_type": "medical",
            "quantity": 15,  # More than most have
            "urgency_score": 75,
            "urgency_level": "U2 - High"
        },
        "description": "High urgency medical need, requires partial fulfillment"
    },
    {
        "name": "Low Urgency - Large Quantity",
        "request": {
            "latitude": 19.1200,  # Near Andheri
            "longitude": 72.8500,
            "need_type": "blankets",
            "quantity": 50,
            "urgency_score": 25,
            "urgency_level": "U4 - Low"
        },
        "description": "Non-urgent blankets, large quantity"
    },
    {
        "name": "Medium Urgency - Unspecified Quantity",
        "request": {
            "latitude": 19.0600,  # Bandra area
            "longitude": 72.8400,
            "need_type": "food",
            "quantity": None,  # No quantity specified
            "urgency_score": 45,
            "urgency_level": "U3 - Medium"
        },
        "description": "Food request without specific quantity"
    },
    {
        "name": "Critical - Far from Resources",
        "request": {
            "latitude": 19.2500,  # North Mumbai
            "longitude": 72.8600,
            "need_type": "medical",
            "quantity": 5,
            "urgency_score": 90,
            "urgency_level": "U1 - Critical"
        },
        "description": "Critical case far from available resources"
    },
]


def print_matching_results(scenario: dict):
    """Print detailed matching results for a scenario."""
    print(f"\n{'=' * 100}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"{'=' * 100}")
    print(f"Description: {scenario['description']}")
    print(f"\nRequest Details:")
    print(f"  Location: ({scenario['request']['latitude']}, {scenario['request']['longitude']})")
    print(f"  Need: {scenario['request']['need_type']}")
    print(f"  Quantity: {scenario['request'].get('quantity', 'Unspecified')}")
    print(f"  Urgency: {scenario['request']['urgency_level']} (score: {scenario['request']['urgency_score']})")
    print(f"{'-' * 100}")
    
    # Get matches
    matches = match_crisis_request(
        crisis_request=scenario['request'],
        available_resources=MOCK_RESOURCES,
        top_n=3
    )
    
    if not matches:
        print("\n❌ NO MATCHES FOUND")
        print("  No resources of this type available")
        return
    
    print(f"\n✅ TOP {len(matches)} MATCHES:")
    
    for i, match in enumerate(matches, 1):
        print(f"\n  {i}. {match['provider_name']}")
        print(f"     Match Score: {match['match_score']:.2f}/1.00")
        print(f"     Distance: {match['distance_km']}km")
        print(f"     Quantity: {match['quantity_available']}")
        
        if match['is_partial_fulfillment']:
            fulfillment_pct = match['fulfillment_ratio'] * 100
            print(f"     ⚠️  Partial Fulfillment: {fulfillment_pct:.0f}%")
        
        print(f"     Reasoning:")
        for reason in match['reasoning']:
            print(f"       {reason}")


def main():
    print("\n" + "=" * 100)
    print(" " * 30 + "RESOURCE MATCHING ENGINE TESTS")
    print(" " * 25 + f"{len(TEST_SCENARIOS)} Test Scenarios with Various Constraints")
    print("=" * 100)
    
    for scenario in TEST_SCENARIOS:
        print_matching_results(scenario)
    
    print(f"\n{'=' * 100}")
    print(f"{'✅ ALL TESTS COMPLETED':^100}")
    print(f"{'=' * 100}\n")
    
    # Summary
    print("\n" + "=" * 100)
    print(" " * 40 + "MATCHING SUMMARY")
    print("=" * 100)
    print("\nKey Features Demonstrated:")
    print("  ✓ Urgency-aware scoring (U1 cases prioritize proximity)")
    print("  ✓ Distance-quantity tradeoffs (closer vs. more available)")
    print("  ✓ Partial fulfillment handling (identified and scored)")
    print("  ✓ Availability status weighting")
    print("  ✓ Top-3 ranking with explainable reasoning")
    print("\nFuture Work:")
    print("  • Multi-request optimization (dispatch planning)")
    print("  • Resource reservation/locking")
    print("  • Real-time availability updates")
    print("  • Route optimization (actual travel time)")


if __name__ == "__main__":
    main()
