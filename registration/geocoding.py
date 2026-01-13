"""
Geocoding utilities for converting addresses to coordinates
and calculating distances between locations
"""
import math
from typing import Optional, Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    Returns distance in kilometers.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    
    return distance


def geocode_address(address: str, city: str = "", country: str = "Rwanda") -> Optional[Tuple[float, float]]:
    """
    Geocode an address to get latitude and longitude.
    Uses a simple approach for Rwanda addresses or can be extended with API services.
    
    Args:
        address: Street address
        city: City name
        country: Country name (default: Rwanda)
    
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    # For now, return None - this can be extended with:
    # 1. OpenStreetMap Nominatim API (free, no key required)
    # 2. Google Geocoding API (requires API key)
    # 3. Mapbox Geocoding API (requires API key)
    
    # Default coordinates for Kigali, Rwanda (can be used as fallback)
    # Kigali center: -1.9441, 30.0619
    default_coords = (-1.9441, 30.0619)
    
    # TODO: Implement actual geocoding using an API
    # For now, return default coordinates for Rwanda addresses
    if "rwanda" in country.lower() or "kigali" in city.lower():
        return default_coords
    
    return None


def find_nearby_collectors(household_lat: float, household_lon: float, 
                           max_distance_km: float = 10.0) -> list:
    """
    Find collectors within a specified distance from a household location.
    
    Args:
        household_lat: Household latitude
        household_lon: Household longitude
        max_distance_km: Maximum distance in kilometers (default: 10km)
    
    Returns:
        List of collectors with distance information
    """
    from .models import Collector
    
    nearby_collectors = []
    
    # Get all available collectors with locations
    collectors = Collector.objects.filter(
        is_available=True,
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    for collector in collectors:
        distance = calculate_distance(
            household_lat, household_lon,
            float(collector.latitude), float(collector.longitude)
        )
        
        # Check if collector is within service radius
        service_radius = float(collector.service_radius) if collector.service_radius else max_distance_km
        
        if distance <= service_radius:
            nearby_collectors.append({
                'collector': collector,
                'distance_km': round(distance, 2),
                'within_radius': distance <= service_radius
            })
    
    # Sort by distance (closest first)
    nearby_collectors.sort(key=lambda x: x['distance_km'])
    
    return nearby_collectors


def find_nearby_pickups(collector_lat: float, collector_lon: float,
                        max_distance_km: float = 10.0) -> list:
    """
    Find pickup requests within a specified distance from a collector location.
    
    Args:
        collector_lat: Collector latitude
        collector_lon: Collector longitude
        max_distance_km: Maximum distance in kilometers (default: 10km)
    
    Returns:
        List of pickup requests with distance information
    """
    from .models import WastePickupRequest
    
    nearby_pickups = []
    
    # Get all pending/scheduled pickups with locations
    pickups = WastePickupRequest.objects.filter(
        status__in=['Pending', 'Scheduled'],
        latitude__isnull=False,
        longitude__isnull=False,
        collector__isnull=True  # Only unassigned pickups
    )
    
    for pickup in pickups:
        distance = calculate_distance(
            collector_lat, collector_lon,
            float(pickup.latitude), float(pickup.longitude)
        )
        
        if distance <= max_distance_km:
            nearby_pickups.append({
                'pickup': pickup,
                'distance_km': round(distance, 2)
            })
    
    # Sort by distance (closest first)
    nearby_pickups.sort(key=lambda x: x['distance_km'])
    
    return nearby_pickups


def auto_assign_collector(pickup_request) -> bool:
    """
    Automatically assign the nearest available collector to a pickup request.
    
    Args:
        pickup_request: WastePickupRequest instance
    
    Returns:
        True if assignment successful, False otherwise
    """
    if not pickup_request.has_location():
        return False
    
    # Find nearby collectors
    nearby = find_nearby_collectors(
        float(pickup_request.latitude),
        float(pickup_request.longitude),
        max_distance_km=15.0  # Search within 15km
    )
    
    if nearby:
        # Assign the closest collector
        closest = nearby[0]
        pickup_request.collector = closest['collector']
        pickup_request.status = 'Scheduled'
        pickup_request.save()
        return True
    
    return False

