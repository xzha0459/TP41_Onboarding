from rest_framework.views import APIView
from rest_framework.response import Response
from .selectors import (
    getRegionById, getSeriesPopulation, getSeriesVehiclesByState,
    yearlyPercentageChange, averageAnnualGrowthRate, valuesPer1000
)

class InsightsIndexApi(APIView):
    def get(self, request):
        return Response({
            "availableEndpoints": ["carOwnership", "cbdPopulation"],
            "params": {
                "carOwnership": ["stateCode", "startYear", "endYear"],
                "cbdPopulation": ["regionId", "startYear", "endYear"]
            }
        })

class CarOwnershipApi(APIView):
    def get(self, request):
        stateCode = request.GET.get("stateCode")  # e.g. VIC
        if not stateCode:
            return Response({"error": "stateCode required"}, status=400)

        startYear = int(request.GET["startYear"]) if "startYear" in request.GET else None
        endYear = int(request.GET["endYear"]) if "endYear" in request.GET else None

        vehicleSeries = getSeriesVehiclesByState(stateCode, startYear, endYear)
        if not vehicleSeries:
            return Response({"error": "no vehicle data for state"}, status=404)

        populationSeries = None  # optional state-level pop if you import it later

        return Response({
            "state": stateCode,
            "values": vehicleSeries,
            "yearlyPercentageChange": yearlyPercentageChange(vehicleSeries),
            "averageAnnualGrowthRate": averageAnnualGrowthRate(vehicleSeries),
            "vehiclesPer1000": valuesPer1000(vehicleSeries, populationSeries) if populationSeries else None
        })

class CbdPopulationGrowthApi(APIView):
    def get(self, request):
        regionId = request.GET.get("regionId")  # CBD region id
        if not regionId:
            return Response({"error": "regionId required"}, status=400)

        startYear = int(request.GET["startYear"]) if "startYear" in request.GET else None
        endYear = int(request.GET["endYear"]) if "endYear" in request.GET else None

        region = getRegionById(regionId)
        if not region:
            return Response({"error": "region not found"}, status=404)

        populationSeries = getSeriesPopulation(region, startYear, endYear)
        if not populationSeries:
            return Response({"error": "no population data for region"}, status=404)

        return Response({
            "region": {"id": region.regionId, "name": region.name, "state": region.stateCode},
            "values": populationSeries,
            "yearlyPercentageChange": yearlyPercentageChange(populationSeries),
            "averageAnnualGrowthRate": averageAnnualGrowthRate(populationSeries)
        })
