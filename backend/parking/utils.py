from math import radians, cos, sin, asin, sqrt

WALKING_SPEED_M_PER_S = 1.388

def haversine(lat1, lng1, lat2, lng2):
    """Calculate the great-circle distance between two points on the Earth in meters."""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c