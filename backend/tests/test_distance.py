import pytest
from app.utils.distance import haversine_distance

def test_haversine_distance_same_point():
    """Test distance between same points is 0."""
    lat, lon = 19.0760, 72.8777
    assert haversine_distance(lat, lon, lat, lon) == 0.0

def test_haversine_distance_mumbai_landmarks():
    """Test known distance between Mumbai landmarks."""
    # Gateway of India
    lat1, lon1 = 18.9220, 72.8347
    # Chhatrapati Shivaji Maharaj Terminus (CSMT) - approx 2km away
    lat2, lon2 = 18.9400, 72.8353
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    # Expected approx 2.0 km (1.9 to 2.1 range)
    assert 1.9 <= distance <= 2.1

def test_haversine_distance_far_points():
    """Test distance between far points (Mumbai -> Delhi)."""
    # Mumbai
    lat1, lon1 = 19.0760, 72.8777
    # Delhi
    lat2, lon2 = 28.7041, 77.1025
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    # Expected approx 1150 km
    assert 1100 <= distance <= 1200
