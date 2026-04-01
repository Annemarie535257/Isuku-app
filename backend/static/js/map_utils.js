/**
 * Map utilities for Isuku app using Leaflet
 */

// Initialize map with default location (Kigali, Rwanda)
function initMap(mapId, options = {}) {
    const defaultLat = options.lat || -1.9441; // Kigali latitude
    const defaultLon = options.lon || 30.0619; // Kigali longitude
    const zoom = options.zoom || 13;
    
    const map = L.map(mapId).setView([defaultLat, defaultLon], zoom);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    return map;
}

// Add marker to map
function addMarker(map, lat, lon, popupText = '', iconColor = 'blue') {
    const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${iconColor}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
    
    const marker = L.marker([lat, lon], { icon: icon }).addTo(map);
    
    if (popupText) {
        marker.bindPopup(popupText);
    }
    
    return marker;
}

// Get user's current location
function getCurrentLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                callback({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    success: true
                });
            },
            function(error) {
                console.error('Geolocation error:', error);
                callback({
                    lat: -1.9441, // Default to Kigali
                    lon: 30.0619,
                    success: false,
                    error: error.message
                });
            }
        );
    } else {
        callback({
            lat: -1.9441,
            lon: 30.0619,
            success: false,
            error: 'Geolocation not supported'
        });
    }
}

// Update location via API
function updateLocation(lat, lon, userType = 'household') {
    const csrftoken = getCookie('csrftoken');
    
    return fetch('/api/update-location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lon,
            user_type: userType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Location updated successfully');
            return { success: true, data: data };
        } else {
            console.error('Failed to update location:', data.error);
            return { success: false, error: data.error };
        }
    })
    .catch(error => {
        console.error('Error updating location:', error);
        return { success: false, error: error.message };
    });
}

// Get nearby collectors
function getNearbyCollectors(lat, lon, maxDistance = 10) {
    return fetch(`/api/nearby-collectors/?max_distance=${maxDistance}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return { success: true, collectors: data.collectors };
            } else {
                return { success: false, error: data.error };
            }
        })
        .catch(error => {
            console.error('Error fetching nearby collectors:', error);
            return { success: false, error: error.message };
        });
}

// Get nearby pickups
function getNearbyPickups(lat, lon, maxDistance = 10) {
    return fetch(`/api/nearby-pickups/?max_distance=${maxDistance}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return { success: true, pickups: data.pickups };
            } else {
                return { success: false, error: data.error };
            }
        })
        .catch(error => {
            console.error('Error fetching nearby pickups:', error);
            return { success: false, error: error.message };
        });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

