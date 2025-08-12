from math import radians, cos, sin, asin, sqrt
import uuid
from rest_framework import serializers
import ulid

WALKING_SPEED_M_PER_S = 1.388

def haversine(lat1, lng1, lat2, lng2):
    """Calculate the great-circle distance between two points on the Earth in meters."""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def calculate_walk_time(from_lat, from_lng, to_lat, to_lng):
    distance_m = haversine(float(from_lat), float(from_lng), float(to_lat), float(to_lng))
    return distance_m / WALKING_SPEED_M_PER_S / 60

def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)

def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name=str(ulid.new()),fields=fields)
    if data is not None:
        return serializer_class(data=data, **kwargs)
    return serializer_class(**kwargs)