from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import DimRegion, FactAbsPopulation, FactAbsVehicleCensus
from .selectors import yearlyPercentageChange, averageAnnualGrowthRate

CBD_REGION_ID = 1
VIC_NAME = "Victoria"

def _parse_years(request, default_start: int, default_end: int):
    try:
        start = int(request.GET.get("startYear", default_start))
    except Exception:
        start = default_start
    try:
        end = int(request.GET.get("endYear", default_end))
    except Exception:
        end = default_end
    if start > end:
        start, end = end, start
    return start, end


@extend_schema(
    summary="Vehicle registrations (VIC only)",
    parameters=[
        OpenApiParameter(name="startYear", type=int, required=False, description="Default 2016"),
        OpenApiParameter(name="endYear", type=int, required=False, description="Default 2021"),
    ],
    responses={200: OpenApiResponse(description="Series & growth metrics for Victoria")}
)
class CarOwnershipApi(APIView):
    def get(self, request):
        start, end = _parse_years(request, 2016, 2021)

        try:
            vic = DimRegion.objects.get(region_type="STATE", region_code=VIC_NAME)
        except DimRegion.DoesNotExist:
            return Response({"error": "VIC not found in dim_region"}, status=404)

        qs = (FactAbsVehicleCensus.objects
              .filter(region=vic, ref_year__gte=start, ref_year__lte=end)
              .values("ref_year")
              .annotate(total=Sum("vehicle_count"))
              .order_by("ref_year"))

        rows = list(qs)
        if not rows:
            return Response({"error": f"no VIC vehicle data in {start}-{end}"}, status=404)

        series = [{"year": r["ref_year"], "value": int(r["total"] or 0)} for r in rows]

        return Response({
            "region": {"code": VIC_NAME, "name": "Victoria", "type": "STATE"},
            "values": series,
            "yearlyPercentageChange": yearlyPercentageChange(series),
            "averageAnnualGrowthRate": averageAnnualGrowthRate(series),
        })

class CbdPopulationGrowthApi(APIView):
    @extend_schema(
        summary="Population (CBD only)",
        parameters=[
            OpenApiParameter(name="startYear", type=int, required=False, description="Default 2001"),
            OpenApiParameter(name="endYear", type=int, required=False, description="Default 2021"),
        ],
        responses={200: OpenApiResponse(description="Series & growth metrics")}
    )
    def get(self, request):
        start, end = _parse_years(request, 2001, 2021)

        try:
            region = DimRegion.objects.get(region_id=CBD_REGION_ID)
        except DimRegion.DoesNotExist:
            return Response({"error": "CBD region not found (check CBD_REGION_ID)"}, status=404)

        qs = (FactAbsPopulation.objects
              .filter(region=region, ref_year__gte=start, ref_year__lte=end)
              .values("ref_year")
              .annotate(total=Sum("population_total"))
              .order_by("ref_year"))

        rows = list(qs)
        if not rows:
            return Response({"error": f"no population data for CBD in {start}-{end}"}, status=404)

        series = [{"year": r["ref_year"], "value": int(r["total"] or 0)} for r in rows]
        return Response({
            "region": {
                "id": int(region.region_id),
                "name": region.region_name,
                "code": region.region_code,
                "type": region.region_type,
            },
            "values": series,
            "yearlyPercentageChange": yearlyPercentageChange(series),
            "averageAnnualGrowthRate": averageAnnualGrowthRate(series),
        })
