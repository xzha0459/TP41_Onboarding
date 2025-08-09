from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .selectors import parking_spot_list
from .services.google_maps import geocode_address 
from .utils import WALKING_SPEED_M_PER_S, haversine 

class ParkingSpotListApi(APIView):
    class ParkingSpotListOutputSerializer(serializers.Serializer):
        kerbside_id = serializers.CharField()
        zone_number = serializers.CharField()
        status_description = serializers.CharField()
        status_timestamp = serializers.DateTimeField()
        latitude = serializers.FloatField()
        longitude = serializers.FloatField()
        last_updated = serializers.DateTimeField()
        is_occupied = serializers.BooleanField()

    @extend_schema(
        responses=ParkingSpotListOutputSerializer(many=True),
        parameters=[
            OpenApiParameter(name='kerbside_id', type=str, location=OpenApiParameter.QUERY, required=False, description='Filter by kerbside ID'),
            OpenApiParameter(name='zone_number', type=str, location=OpenApiParameter.QUERY, required=False, description='Filter by zone number'),
            OpenApiParameter(name='is_occupied', type=bool, location=OpenApiParameter.QUERY, required=False, description='Filter by occupancy'),
        ],
        description="List parking spots with optional filters."
    )
    def get(self, request):
        filters = {
            field: (value.lower() == "true" if field == "is_occupied" else value)
            for field in ["kerbside_id", "zone_number", "is_occupied"]
            if (value := request.query_params.get(field)) is not None
        }
        spots = parking_spot_list(filters=filters)
        serializer = self.ParkingSpotListOutputSerializer(spots, many=True)
        return Response(serializer.data)

class ParkingSpotNearbyWalkTimeApi(APIView):
    class InputSerializer(serializers.Serializer):
        address = serializers.CharField()
        max_walk_time = serializers.IntegerField(required=False, default=5)

    class ParkingSpotNearbyWalkTimeOutputSerializer(serializers.Serializer):
        kerbside_id = serializers.CharField()
        zone_number = serializers.CharField()
        status_description = serializers.CharField()
        status_timestamp = serializers.DateTimeField()
        latitude = serializers.FloatField()
        longitude = serializers.FloatField()
        last_updated = serializers.DateTimeField()
        is_occupied = serializers.BooleanField()
        walk_time = serializers.FloatField()
        distance_km = serializers.FloatField()

    @extend_schema(
        request=InputSerializer,
        responses=ParkingSpotNearbyWalkTimeOutputSerializer(many=True),
        description="Find nearby parking spots by address and walk time."
    )
    def post(self, request):
        input_data = self.InputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)
        address = input_data.validated_data["address"]
        max_walk_time = input_data.validated_data["max_walk_time"]
        
        lat, lng = geocode_address(address)
        if lat is None or lng is None:
            return Response({"error": "Address not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        nearby_spots = [
            self._annotate_spot_with_distance_and_time(spot, lat, lng)
            for spot in parking_spot_list(filters={"is_occupied": False})
            if self._calculate_walk_time(lat, lng, spot.latitude, spot.longitude) <= max_walk_time
        ]
        serializer = self.ParkingSpotNearbyWalkTimeOutputSerializer(nearby_spots, many=True)
        return Response(serializer.data)
    
    def _calculate_walk_time(self, from_lat, from_lng, to_lat, to_lng):
        distance_m = haversine(float(from_lat), float(from_lng), float(to_lat), float(to_lng))
        return distance_m / WALKING_SPEED_M_PER_S / 60

    def _annotate_spot_with_distance_and_time(self, spot, from_lat, from_lng):
        distance_m = haversine(float(from_lat), float(from_lng), float(spot.latitude), float(spot.longitude))
        return {
            "kerbside_id": spot.kerbside_id,
            "zone_number": spot.zone_number,
            "status_description": spot.status_description,
            "status_timestamp": spot.status_timestamp,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "last_updated": spot.last_updated,
            "is_occupied": spot.is_occupied,
            "walk_time": distance_m / WALKING_SPEED_M_PER_S / 60,
            "distance_km": distance_m / 1000
        }