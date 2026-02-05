"""
Resource matching engine for crisis requests.

Matches crisis requests to available resources with urgency-aware weighting
and partial fulfillment support.
"""
import math
from typing import List, Dict, Optional, Tuple
from app.models.crisis import Resource, CrisisRequest, ResourceType, AvailabilityStatus


# ===== CONFIGURATION =====

# Distance thresholds (km)
MAX_DISTANCE_KM = 50.0  # Maximum distance to consider
IDEAL_DISTANCE_KM = 5.0  # Ideal distance for full distance score

# Urgency weights (how much urgency affects matching)
URGENCY_WEIGHTS = {
    "U1": 2.0,   # Critical - double the importance of proximity
    "U2": 1.5,   # High - 50% more weight
    "U3": 1.2,   # Medium - slight boost
    "U4": 1.0,   # Low - normal weighting
    "U5": 0.8,   # Minimal - slightly reduced
}

# Scoring weights
WEIGHT_DISTANCE = 0.35      # 35% weight to proximity
WEIGHT_QUANTITY = 0.30      # 30% weight to quantity match
WEIGHT_AVAILABILITY = 0.20  # 20% weight to availability status
WEIGHT_URGENCY = 0.15       # 15% weight to urgency alignment


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def score_distance(distance_km: float, urgency_level: str) -> Tuple[float, str]:
    """
    Score resource based on distance with urgency weighting.
    
    Args:
        distance_km: Distance to resource in km
        urgency_level: Urgency level (U1-U5)
        
    Returns:
        Tuple of (score 0-1, reasoning)
    """
    if distance_km > MAX_DISTANCE_KM:
        return 0.0, f"Too far: {distance_km:.1f}km (max: {MAX_DISTANCE_KM}km)"
    
    # Base distance score (exponential decay)
    # Score = 1.0 at 0km, ~0.6 at ideal distance, approaches 0 at max
    base_score = math.exp(-distance_km / IDEAL_DISTANCE_KM)
    
    # Apply urgency weighting
    urgency_weight = URGENCY_WEIGHTS.get(urgency_level.split()[0], 1.0)
    
    # For critical cases, penalize distance more heavily
    if urgency_weight > 1.0:
        base_score = base_score ** (1.0 / urgency_weight)
    
    reasoning = f"Distance: {distance_km:.1f}km (urgency: {urgency_level}, weight: {urgency_weight}x)"
    
    return round(base_score, 3), reasoning


def score_quantity(
    requested_qty: Optional[int],
    available_qty: int,
    urgency_level: str
) -> Tuple[float, str, bool]:
    """
    Score resource based on quantity match.
    
    Args:
        requested_qty: Quantity requested (None if unspecified)
        available_qty: Quantity available
        urgency_level: Urgency level (U1-U5)
        
    Returns:
        Tuple of (score 0-1, reasoning, is_partial)
    """
    # If quantity not specified, assume resource is good enough
    if requested_qty is None:
        return 1.0, "Quantity not specified - assuming adequate", False
    
    if available_qty <= 0:
        return 0.0, "No quantity available", False
    
    if available_qty >= requested_qty:
        # Full fulfillment
        surplus_pct = ((available_qty - requested_qty) / requested_qty) * 100
        reasoning = f"Full match: {available_qty}/{requested_qty} ({surplus_pct:.0f}% surplus)"
        return 1.0, reasoning, False
    
    else:
        # Partial fulfillment
        fulfillment_pct = (available_qty / requested_qty)
        
        # For critical cases, partial fulfillment is less acceptable
        urgency_weight = URGENCY_WEIGHTS.get(urgency_level.split()[0], 1.0)
        
        if urgency_weight >= 1.5:  # U1, U2
            # Penalize partial fulfillment more for critical cases
            score = fulfillment_pct * 0.7  # Max 70% score for partial
        else:
            # More lenient for non-critical cases
            score = fulfillment_pct * 0.85  # Max 85% score for partial
        
        reasoning = f"Partial match: {available_qty}/{requested_qty} ({fulfillment_pct*100:.0f}% fulfillment)"
        return round(score, 3), reasoning, True


def score_availability(status: AvailabilityStatus) -> Tuple[float, str]:
    """
    Score resource based on availability status.
    
    Args:
        status: Current availability status
        
    Returns:
        Tuple of (score 0-1, reasoning)
    """
    status_scores = {
        AvailabilityStatus.AVAILABLE: (1.0, "Fully available"),
        AvailabilityStatus.PARTIALLY_AVAILABLE: (0.7, "Partially available"),
        AvailabilityStatus.DISPATCHED: (0.3, "Currently dispatched"),
        AvailabilityStatus.UNAVAILABLE: (0.0, "Unavailable"),
    }
    
    return status_scores.get(status, (0.0, "Unknown status"))


def calculate_match_score(
    request_lat: float,
    request_lng: float,
    request_qty: Optional[int],
    urgency_level: str,
    resource: Resource
) -> Tuple[float, List[str], bool]:
    """
    Calculate overall match score for a resource.
    
    Args:
        request_lat, request_lng: Request location
        request_qty: Requested quantity
        urgency_level: Urgency level (U1-U5)
        resource: Resource to match
        
    Returns:
        Tuple of (total_score, reasoning_list, is_partial_fulfillment)
    """
    reasoning = []
    
    # 1. Distance score
    distance_km = haversine_distance(
        request_lat, request_lng,
        resource.latitude, resource.longitude
    )
    dist_score, dist_reason = score_distance(distance_km, urgency_level)
    reasoning.append(f"📍 {dist_reason} → {dist_score:.2f}")
    
    # 2. Quantity score
    qty_score, qty_reason, is_partial = score_quantity(
        request_qty, resource.quantity_available, urgency_level
    )
    reasoning.append(f"📦 {qty_reason} → {qty_score:.2f}")
    
    # 3. Availability score
    avail_score, avail_reason = score_availability(resource.availability_status)
    reasoning.append(f"✓ {avail_reason} → {avail_score:.2f}")
    
    # 4. Calculate weighted total
    total_score = (
        dist_score * WEIGHT_DISTANCE +
        qty_score * WEIGHT_QUANTITY +
        avail_score * WEIGHT_AVAILABILITY
    )
    
    # 5. Urgency bonus (for critical cases, boost score if other factors are good)
    urgency_weight = URGENCY_WEIGHTS.get(urgency_level.split()[0], 1.0)
    if urgency_weight >= 1.5 and total_score >= 0.6:
        urgency_bonus = 0.05 * urgency_weight
        total_score = min(total_score + urgency_bonus, 1.0)
        reasoning.append(f"⚡ Urgency bonus: {urgency_level} (+{urgency_bonus:.2f})")
    
    total_score = round(total_score, 3)
    reasoning.insert(0, f"🎯 Total match score: {total_score:.2f}/1.00")
    
    return total_score, reasoning, is_partial


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
