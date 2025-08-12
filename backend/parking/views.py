import os

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .prediction.main import ParkingPredictor
from .selectors import parking_list
from .services.google_maps import GeocodeError, geocode_address 
from .utils import calculate_walk_time, haversine 
from .serializers import ( ParkingSerializer,ParkingNearbySerializer )

class ParkingListApi(APIView):
    
    @extend_schema(
        responses=ParkingSerializer(many=True),
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
        serializer = self.ParkingSerializer(spots, many=True)
        return Response(serializer.data)

class ParkingNearbyApi(APIView):
    
    class ParkingNearbyInputSerializer(serializers.Serializer):
        address = serializers.CharField()
        max_walk_time = serializers.IntegerField(required=False, default=5)

    @extend_schema(
        request=ParkingNearbyInputSerializer,
        responses=ParkingNearbySerializer,
        description="Find nearby parking spot occupancy by address and walk time."
    )
    def post(self, request):
        input_data = self.ParkingNearbyInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)
        
        address = input_data.validated_data["address"]
        max_walk_time = input_data.validated_data["max_walk_time"]
        
        try:
            origin_data = geocode_address(address)
        except GeocodeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        lat, lng = origin_data["latitude"], origin_data["longitude"]
        
        nearby_spots = []
        for spot in parking_list(filters={"is_occupied": False}):
            walk_time = calculate_walk_time(lat, lng, spot.latitude, spot.longitude)
            if (
                walk_time <= max_walk_time
                and spot.zone_number is not None
                and spot.kerbside_id is not None
            ):
                spot_data = ParkingSerializer(spot).data
                spot_data["walk_time"] = walk_time
                spot_data["distance_km"] = haversine(lat, lng, spot.latitude, spot.longitude) / 1000
                spot_data["predicted_available_probability"] = None 
                nearby_spots.append(spot_data)
        
        serializer = ParkingNearbySerializer({"origin": origin_data, "nearby": nearby_spots})
        return Response(serializer.data)
    
class ParkingNearbyPredictApi(APIView):
    
    class ParkingNearbyPredictInputSerializer(serializers.Serializer):
        address = serializers.CharField()
        datetime = serializers.DateTimeField()
        max_walk_time = serializers.IntegerField(required=False, default=5)

    @extend_schema(
        request=ParkingNearbyPredictInputSerializer,
        responses=ParkingNearbySerializer,
        description="Predict nearby parking spot occupancy by address, datetime, and walk time."
    )
    def post(self, request):
        input_data = self.ParkingNearbyPredictInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)
        
        address = input_data.validated_data["address"]
        dt = input_data.validated_data["datetime"]
        max_walk_time = input_data.validated_data["max_walk_time"]

        try:
            origin_data = geocode_address(address)
        except GeocodeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        lat, lng = origin_data["latitude"], origin_data["longitude"]

        model_path = os.path.join(os.path.dirname(__file__), 'prediction', 'parking_model.joblib')
        predictor = ParkingPredictor()
        predictor.load(model_path)

        nearby_spots = []
        for spot in parking_list(filters={"is_occupied": False}):
            walk_time = calculate_walk_time(lat, lng, spot.latitude, spot.longitude)
            if (
                walk_time <= max_walk_time
                and spot.zone_number is not None
                and spot.kerbside_id is not None
            ):
                spot_data = ParkingSerializer(spot).data
                spot_data["walk_time"] = walk_time
                spot_data["distance_km"] = haversine(lat, lng, spot.latitude, spot.longitude) / 1000
                prob = predictor.predict_proba(
                    int(float(spot.zone_number)),
                    int(float(spot.kerbside_id)),
                    dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
                )
                spot_data["predicted_available_probability"] = prob[0][1]
                nearby_spots.append(spot_data)

        serializer = ParkingNearbySerializer({"origin": origin_data, "nearby": nearby_spots})
        return Response(serializer.data)
