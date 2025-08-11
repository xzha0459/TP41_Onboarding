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

def _get_vic_region():
    # Avoid .get() – pick one deterministically if duplicates exist.
    base = DimRegion.objects.filter(region_name__iexact=VIC_NAME)
    # Prefer STATE rows if present, then the smallest region_id for stability
    obj = base.filter(region_type="STATE").order_by("region_id").first()
    if obj:
        return obj
    return base.order_by("region_type", "region_id").first()

class CarOwnershipApi(APIView):
    @extend_schema(
        summary="Vehicle ownership in Victoria (years only)",
        parameters=[
            OpenApiParameter(name="startYear", type=int, required=False, description="Default 2016"),
            OpenApiParameter(name="endYear", type=int, required=False, description="Default 2021"),
        ],
        responses={200: OpenApiResponse(description="Series & growth metrics")},
    )
    def get(self, request):
        start, end = _parse_years(request, 2016, 2021)

        vic = _get_vic_region()
        if not vic:
            return Response({"error": "Could not resolve Victoria region"}, status=404)

        qs = (
            FactAbsVehicleCensus.objects
            .filter(region=vic, ref_year__gte=start, ref_year__lte=end)
            .values("ref_year")
            .annotate(total=Sum("vehicle_count"))
            .order_by("ref_year")
        )

        years = [row["ref_year"] for row in qs]
        vehicle_counts = [int(row["total"] or 0) for row in qs]

        total_growth_pct = None
        if len(vehicle_counts) >= 2 and vehicle_counts[0]:
            total_growth_pct = round(
                (vehicle_counts[-1] - vehicle_counts[0]) / vehicle_counts[0] * 100, 2
            )

        # Same shape your chart used before
        return Response({
            "years": years,
            "vehicleCounts": vehicle_counts,
            "totalGrowthPct": total_growth_pct,
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
