# insights/selectors.py
from typing import List, Dict, Optional
from django.db.models import Sum
from .models import DimRegion, FactAbsPopulation, FactAbsVehicleCensus

__all__ = [
    "getRegionById",
    "getSeriesPopulation",
    "getSeriesVehiclesByState",
    "yearlyPercentageChange",
    "averageAnnualGrowthRate",
    "valuesPer1000",
]

def getRegionById(regionId: str) -> Optional[DimRegion]:
    """
    Backward-compatible resolver:
    - first try by region_id (numeric as str is OK)
    - then try by region_code (e.g., 'VIC')
    """
    # try region_id
    try:
        return DimRegion.objects.get(region_id=int(regionId))
    except (DimRegion.DoesNotExist, ValueError, TypeError):
        pass

    # try region_code
    try:
        return DimRegion.objects.get(region_code=str(regionId))
    except DimRegion.DoesNotExist:
        return None

def getSeriesPopulation(region: DimRegion, startYear: Optional[int]=None, endYear: Optional[int]=None) -> List[Dict]:
    qs = (
        FactAbsPopulation.objects
        .filter(region=region)
        .values("ref_year")
        .annotate(population=Sum("population_total"))
        .order_by("ref_year")
    )
    data = [{"year": r["ref_year"], "value": int(r["population"] or 0)} for r in qs]
    if startYear is not None:
        data = [x for x in data if x["year"] >= startYear]
    if endYear is not None:
        data = [x for x in data if x["year"] <= endYear]
    return data

def getSeriesVehiclesByState(
    stateCode: str,
    startYear: Optional[int] = None,
    endYear: Optional[int] = None,
) -> List[Dict]:
    """
    Returns [{year, value}] for the given Australian state code (e.g., 'VIC', 'NSW'),
    summed from fact_abs_vehicle_census for that state's region_id.
    """
    stateCode = (stateCode or "").upper()
    try:
        region = DimRegion.objects.get(region_type="STATE", region_code=stateCode)
    except DimRegion.DoesNotExist:
        return []

    qs = FactAbsVehicleCensus.objects.filter(region=region)
    if startYear is not None:
        qs = qs.filter(ref_year__gte=startYear)
    if endYear is not None:
        qs = qs.filter(ref_year__lte=endYear)

    rows = (
        qs.values("ref_year")
          .annotate(value=Sum("vehicle_count"))
          .order_by("ref_year")
    )
    return [{"year": r["ref_year"], "value": int(r["value"] or 0)} for r in rows]


def yearlyPercentageChange(series: List[Dict]) -> List[Dict]:
    out = []
    for i in range(1, len(series)):
        prev = series[i-1]["value"]
        curr = series[i]["value"]
        if prev:
            out.append({"year": series[i]["year"], "value": ((curr - prev) / prev) * 100.0})
    return out

def averageAnnualGrowthRate(series: List[Dict]) -> Optional[float]:
    if not series or len(series) < 2:
        return None
    start, end = series[0], series[-1]
    n = (end["year"] - start["year"])
    if n <= 0 or start["value"] <= 0:
        return None
    return ((end["value"] / start["value"]) ** (1.0 / n) - 1.0) * 100.0

def valuesPer1000(numerator: List[Dict], denominator: List[Dict]) -> Optional[List[Dict]]:
    if not numerator or not denominator:
        return None
    d = {x["year"]: x["value"] for x in denominator}
    out = []
    for item in numerator:
        y = item["year"]
        if y in d and d[y] > 0:
            out.append({"year": y, "value": (item["value"] / d[y]) * 1000.0})
    return out or None
