"""
Resource matching engine for crisis requests.

Matches crisis requests to available resources with urgency-aware weighting
and partial fulfillment support.
"""
import math
from typing import List, Dict, Optional, Tuple
from app.models.crisis import Resource, CrisisRequest, ResourceType, AvailabilityStatus



# ===== CONFIGURATION =====

# Distance thresholds
MAX_EFFECTIVE_DISTANCE_KM = 20.0  # Distance at which score becomes 0

# Urgency Profiles (Weights must sum to 1.0)
URGENCY_PROFILES = {
    "U1": {"distance": 0.80, "quantity": 0.20},  # Critical: Proximity is paramount
    "U2": {"distance": 0.70, "quantity": 0.30},  # High: strong distance preference
    "U3": {"distance": 0.50, "quantity": 0.50},  # Medium: balanced
    "U4": {"distance": 0.30, "quantity": 0.70},  # Low: quantity matters more
    "U5": {"distance": 0.20, "quantity": 0.80},  # Minimal: go far for bulk
}


from app.utils.geo import haversine_distance


def score_distance(distance_km: float) -> Tuple[float, str]:
    """
    Score resource based on distance (0-100).
    Linear decay: 100 at 0km -> 0 at 20km
    """
    if distance_km >= MAX_EFFECTIVE_DISTANCE_KM:
        return 0.0, f"{distance_km:.1f}km (Too far)"
    
    # Linear scaling: (1 - d/max) * 100
    score = (1 - (distance_km / MAX_EFFECTIVE_DISTANCE_KM)) * 100
    return max(0.0, score), f"{distance_km:.1f}km"


def score_quantity(
    requested_qty: Optional[int],
    available_qty: int
) -> Tuple[float, str, bool]:
    """
    Score resource based on quantity match (0-100).
    Returns (score, reasoning, is_partial)
    """
    if available_qty <= 0:
        return 0.0, "None available", False
        
    # If no quantity requested, assume 100% score (perfect match)
    if requested_qty is None or requested_qty <= 0:
        return 100.0, f"Available: {available_qty}", False

    if available_qty >= requested_qty:
        # Full fulfillment
        return 100.0, f"Available: {available_qty} (Full)", False
    
    # Partial fulfillment ratio
    ratio = available_qty / requested_qty
    score = ratio * 100
    return score, f"Available: {available_qty} ({int(ratio*100)}% of req)", True


def score_availability(status: AvailabilityStatus) -> Tuple[float, str]:
    """
    Helper for reasoning text.
    """
    status_map = {
        AvailabilityStatus.AVAILABLE: "Available",
        AvailabilityStatus.PARTIALLY_AVAILABLE: "Limited",
        AvailabilityStatus.DISPATCHED: "Dispatched",
        AvailabilityStatus.UNAVAILABLE: "Unavailable",
    }
    return 0.0, status_map.get(status, "Unknown")


def calculate_match_score(
    request_lat: float,
    request_lng: float,
    request_qty: Optional[int],
    urgency_level: str,
    resource: Resource
) -> Tuple[float, List[str], bool]:
    """
    Calculate overall match score for a resource using urgency profiles.
    Returns score normalized to 0-1 for API compatibility.
    """
    reasoning = []
    
    # 0. Determine Weights
    # Extract "U1" from "U1 - Critical"
    u_code = urgency_level.split(" ")[0] if urgency_level else "U4"
    profile = URGENCY_PROFILES.get(u_code, URGENCY_PROFILES["U4"])
    
    w_dist = profile["distance"]
    w_qty = profile["quantity"]

    # 1. Distance score (0-100)
    distance_km = haversine_distance(
        request_lat, request_lng,
        resource.latitude, resource.longitude
    )
    dist_score, dist_text = score_distance(distance_km)
    
    # Explain: "Distance: 5.0km (Score: 75, Weight: 80%)"
    reasoning.append(
        f"📍 Distance: {dist_text} (Score: {int(dist_score)}, Weight: {int(w_dist*100)}%)"
    )
    
    # 2. Quantity score (0-100)
    qty_score, qty_text, is_partial = score_quantity(request_qty, resource.quantity_available)
    
    reasoning.append(
        f"📦 Capacity: {qty_text} (Score: {int(qty_score)}, Weight: {int(w_qty*100)}%)"
    )
    
    # 3. Availability info (No score impact, just for info)
    _, avail_text = score_availability(resource.availability_status)
    reasoning.append(f"ℹ️ Status: {avail_text}")

    # 4. Final Weighted Calculation (0-100)
    final_score_100 = (dist_score * w_dist) + (qty_score * w_qty)
    
    # 5. Normalize to 0-1 for API contract
    final_score_0_1 = round(final_score_100 / 100.0, 2)
    
    reasoning.insert(0, f"🎯 Match Score: {int(final_score_100)}/100 ({u_code} Profile)")

    return final_score_0_1, reasoning, is_partial


def match_resources(
    request_lat: float,
    request_lng: float,
    need_type: str,
    request_qty: Optional[int],
    urgency_score: int,
    urgency_level: str,
    available_resources: List[Resource],
    top_n: int = 3
) -> List[Dict]:
    """
    Find best matching resources for a crisis request.
    
    Args:
        request_lat, request_lng: Request location coordinates
        need_type: Type of resource needed
        request_qty: Quantity requested (None if unspecified)
        urgency_score: Urgency score (0-100)
        urgency_level: Urgency level string (e.g., "U1 - Critical")
        available_resources: List of available resources
        top_n: Number of top matches to return
        
    Returns:
        List of match dictionaries, sorted by score (descending)
    """
    matches = []
    
    # Filter by resource type first
    type_filtered = [
        r for r in available_resources
        if r.resource_type.value == need_type
    ]
    
    if not type_filtered:
        return []
    
    # Score each resource
    for resource in type_filtered:
        # Calculate distance first (needed for scoring and response)
        distance_km = haversine_distance(
            request_lat, request_lng,
            resource.latitude, resource.longitude
        )
        
        match_score, reasoning, is_partial = calculate_match_score(
            request_lat,
            request_lng,
            request_qty,
            urgency_level,
            resource
        )
        
        # Skip if score is too low (< 20%)
        if match_score < 0.2:
            continue
        
        # Calculate fulfillment ratio
        if request_qty and request_qty > 0:
            fulfillment_ratio = min(resource.quantity_available / request_qty, 1.0)
        else:
            fulfillment_ratio = 1.0
        
        # Create match dict (not using ResourceMatch schema since it's for DB relationships)
        match = {
            "resource_id": resource.id,
            "resource_type": resource.resource_type.value,
            "provider_name": resource.provider_name,
            "quantity_available": resource.quantity_available,
            "distance_km": round(distance_km, 2),
            "match_score": match_score,
            "reasoning": reasoning,
            "is_partial_fulfillment": is_partial,
            "fulfillment_ratio": round(fulfillment_ratio, 2),
            "location_name": resource.location_name,
        }
        
        matches.append(match)
    
    # Sort by match score (descending)
    matches.sort(key=lambda m: m['match_score'], reverse=True)
    
    # Return top N
    return matches[:top_n]


def match_crisis_request(
    crisis_request: Dict,  # Simplified request dict with extraction + urgency
    available_resources: List[Resource],
    top_n: int = 3
) -> List[Dict]:
    """
    High-level matching function for crisis requests.
    
    Args:
        crisis_request: Dict with keys:
            - latitude, longitude: Request location (required)
            - need_type: Type of need (required)
            - quantity: Requested quantity (optional)
            - urgency_score: Urgency score 0-100 (required)
            - urgency_level: Urgency level string (required)
        available_resources: List of Resource objects
        top_n: Number of matches to return
        
    Returns:
        List of top N match dictionaries
    """
    # Validate required fields
    if not all(k in crisis_request for k in ['latitude', 'longitude', 'need_type', 'urgency_level']):
        raise ValueError("Missing required fields in crisis_request")
    
    return match_resources(
        request_lat=crisis_request['latitude'],
        request_lng=crisis_request['longitude'],
        need_type=crisis_request['need_type'],
        request_qty=crisis_request.get('quantity'),
        urgency_score=crisis_request.get('urgency_score', 50),
        urgency_level=crisis_request['urgency_level'],
        available_resources=available_resources,
        top_n=top_n
    )
