from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response

from .selectors import parking_spot_list

class ParkingSpotListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        kerbside_id = serializers.CharField()
        zone_number = serializers.CharField()
        status_description = serializers.CharField()
        status_timestamp = serializers.DateTimeField()
        latitude = serializers.FloatField()
        longitude = serializers.FloatField()
        last_updated = serializers.DateTimeField()
        is_occupied = serializers.BooleanField()

    def get(self, request):
        spots = parking_spot_list()
        data = [
            {
                "kerbside_id": spot.kerbside_id,
                "zone_number": spot.zone_number,
                "status_description": spot.status_description,
                "status_timestamp": spot.status_timestamp,
                "latitude": spot.latitude,
                "longitude": spot.longitude,
                "last_updated": spot.last_updated,
                "is_occupied": spot.is_occupied
            }
            for spot in spots
        ]
        return Response(data)
    
class ParkingSpotUnoccupiedListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        kerbside_id = serializers.CharField()
        zone_number = serializers.CharField()
        status_description = serializers.CharField()
        status_timestamp = serializers.DateTimeField()
        latitude = serializers.FloatField()
        longitude = serializers.FloatField()
        last_updated = serializers.DateTimeField()

    def get(self, request):
        spots = parking_spot_list(filters={"is_occupied": False})
        data = [
            {
                "kerbside_id": spot.kerbside_id,
                "zone_number": spot.zone_number,
                "status_description": spot.status_description,
                "status_timestamp": spot.status_timestamp,
                "latitude": spot.latitude,
                "longitude": spot.longitude,
                "last_updated": spot.last_updated,
            }
            for spot in spots
        ]
        return Response(data)