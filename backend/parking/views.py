import os
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .prediction.main import ParkingPredictor
from .selectors import parking_list
from .services.google_maps import geocode_address 
from .utils import WALKING_SPEED_M_PER_S, haversine 

class ParkingListApi(APIView):
    class ParkingListOutputSerializer(serializers.Serializer):
        kerbside_id = serializers.CharField()
        zone_number = serializers.CharField()
        status_description = serializers.CharField()
        status_timestamp = serializers.DateTimeField()
        latitude = serializers.FloatField()
        longitude = serializers.FloatField()
        last_updated = serializers.DateTimeField()
        is_occupied = serializers.BooleanField()

    @extend_schema(
        responses=ParkingListOutputSerializer(many=True),
        parameters=[
            OpenApiParameter(name='kerbside_id', type=str, location=OpenApiParameter.QUERY, required=False, description='Filter by kerbside ID'),
            OpenApiParameter(name='zone_number', type=str, location=OpenApiParameter.QUERY, required=False, description='Filter by zone number'),
            OpenApiParameter(name='is_occupied', type=bool, location=OpenApiParameter.QUERY, required=False, description='Filter by occupancy'),
        ],
        description="List parking spot occupancy with optional filters."
    )
    def get(self, request):
        filters = {
            field: (value.lower() == "true" if field == "is_occupied" else value)
            for field in ["kerbside_id", "zone_number", "is_occupied"]
            if (value := request.query_params.get(field)) is not None
        }
        spots = parking_list(filters=filters)
        serializer = self.ParkingListOutputSerializer(spots, many=True)
        return Response(serializer.data)

class ParkingNearbyApi(APIView):
    class ParkingNearbyInputSerializer(serializers.Serializer):
        address = serializers.CharField()
        max_walk_time = serializers.IntegerField(required=False, default=5)

    class ParkingNearbyOutputSerializer(serializers.Serializer):
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
        request=ParkingNearbyInputSerializer,
        responses=ParkingNearbyOutputSerializer(many=True),
        description="Find nearby parking spot occupancy by address and walk time."
    )
    def post(self, request):
        input_data = self.ParkingNearbyInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)
        address = input_data.validated_data["address"]
        max_walk_time = input_data.validated_data["max_walk_time"]
        
        lat, lng = geocode_address(address)
        if lat is None or lng is None:
            return Response({"error": "Address not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        nearby_spots = [
            self._annotate_spot_with_distance_and_time(spot, lat, lng)
            for spot in parking_list(filters={"is_occupied": False})
            if self._calculate_walk_time(lat, lng, spot.latitude, spot.longitude) <= max_walk_time
        ]
        serializer = self.ParkingNearbyOutputSerializer(nearby_spots, many=True)
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

class ParkingNearbyPredictApi(APIView):
    class ParkingNearbyPredictInputSerializer(serializers.Serializer):
        address = serializers.CharField()
        datetime = serializers.DateTimeField()
        max_walk_time = serializers.IntegerField(required=False, default=5)

    class ParkingNearbyPredictOutputSerializer(serializers.Serializer):
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
        predicted_available_probability = serializers.FloatField()

    @extend_schema(
        request=ParkingNearbyPredictInputSerializer,
        responses=ParkingNearbyPredictOutputSerializer(many=True),
        description="Predict nearby parking spot occupancy by address, datetime, and walk time."
    )
    def post(self, request):
        input_data = self.ParkingNearbyPredictInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)
        address = input_data.validated_data["address"]
        dt = input_data.validated_data["datetime"]
        max_walk_time = input_data.validated_data["max_walk_time"]

        lat, lng = geocode_address(address)
        if lat is None or lng is None:
            return Response({"error": "Address not found"}, status=status.HTTP_400_BAD_REQUEST)

        model_path = os.path.join(os.path.dirname(__file__), 'prediction', 'parking_model.joblib')
        predictor = ParkingPredictor()
        predictor.load(model_path)

        nearby_spots = [
            self._annotate_spot_with_distance_and_time(spot, lat, lng)
            for spot in parking_list(filters={"is_occupied": False})
            if (
                self._calculate_walk_time(lat, lng, spot.latitude, spot.longitude) <= max_walk_time
                and spot.zone_number is not None
                and spot.kerbside_id is not None
            )
        ]

        for spot in nearby_spots:
            prob = predictor.predict_proba(
                int(float(spot["zone_number"])),
                int(float(spot["kerbside_id"])),
                dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
            )
            spot["predicted_available_probability"] = prob[0][1]

        serializer = self.ParkingNearbyPredictOutputSerializer(nearby_spots, many=True)
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