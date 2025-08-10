from typing import List, Dict, Optional
from .models import RegionBoundary, RegionalPopulation, MotorVehicleCensus
from math import sqrt

def getRegionById(regionId: str) -> Optional[RegionBoundary]:
    try:
        return RegionBoundary.objects.get(pk=regionId)
    except RegionBoundary.DoesNotExist:
        return None

def getSeriesPopulation(region: RegionBoundary, startYear: Optional[int]=None, endYear: Optional[int]=None) -> List[Dict]:
    qs = RegionalPopulation.objects.filter(region=region).values("year", "population").order_by("year")
    data = [{"year": r["year"], "value": r["population"]} for r in qs]
    if startYear is not None:
        data = [x for x in data if x["year"] >= startYear]
    if endYear is not None:
        data = [x for x in data if x["year"] <= endYear]
    return data

def getSeriesVehiclesByState(stateCode: str, startYear: Optional[int]=None, endYear: Optional[int]=None) -> List[Dict]:
    qs = MotorVehicleCensus.objects.filter(state=stateCode).values("year", "vehicleCount").order_by("year")
    data = [{"year": r["year"], "value": r["vehicleCount"]} for r in qs]
    if startYear is not None:
        data = [x for x in data if x["year"] >= startYear]
    if endYear is not None:
        data = [x for x in data if x["year"] <= endYear]
    return data

def yearlyPercentageChange(data: List[Dict]) -> List[Dict]:
    result = []
    for i in range(1, len(data)):
        prev = data[i-1]["value"]
        cur = data[i]["value"]
        if prev:
            result.append({"year": data[i]["year"], "percentage": (cur - prev) / prev * 100.0})
    return result

def averageAnnualGrowthRate(data: List[Dict]) -> Optional[float]:
    if len(data) < 2:
        return None
    start = data[0]; end = data[-1]
    n = end["year"] - start["year"]
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
