from rest_framework import serializers
from .models import ParkingSpot

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = [
            'kerbside_id',
            'zone_number',
            'status_description',
            'status_timestamp',
            'last_updated',
            'longitude',
            'latitude'
        ]
        