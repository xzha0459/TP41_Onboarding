from rest_framework import serializers
from .utils import inline_serializer

class OriginSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    address = serializers.CharField()
    formatted_address = serializers.CharField() 

class ParkingSerializer(serializers.Serializer):
    kerbside_id = serializers.CharField()
    zone_number = serializers.CharField()
    status_description = serializers.CharField()
    status_timestamp = serializers.DateTimeField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    last_updated = serializers.DateTimeField()
    is_occupied = serializers.BooleanField()
    sign_text = serializers.CharField(required=False, allow_null=True)
    days_of_week = serializers.CharField(required=False, allow_null=True)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    
class ParkingNearbySerializer(serializers.Serializer):
    origin = OriginSerializer()
    nearby = inline_serializer(
        fields={
            **{field: ParkingSerializer().fields[field] for field in ParkingSerializer().fields},
            "walk_time": serializers.FloatField(),
            "distance_km": serializers.FloatField(),
            "predicted_available_probability": serializers.FloatField(),
        },
        many=True
    )
