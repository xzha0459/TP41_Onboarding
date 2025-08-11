from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Optional

from django.db import connection
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

# Your DB schema prefix
SCHEMA = "parking_prod"

def _t(name: str) -> str:
    return f"{SCHEMA}.{name}" if SCHEMA else name

def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _parse_dt(val: Optional[str], default: datetime) -> str:
    if not val:
        return _iso(default)
    try:
        return _iso(datetime.fromisoformat(val))
    except Exception:
        return _iso(default)

def _run(sql: str, params: List[Any]) -> List[Tuple]:
    with connection.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# -------------------- BAY SCOPE HELPERS --------------------

def _scoped_bays(scope: str) -> Optional[str]:
    """
    Build a SQL subselect that yields a single-column table (bay_id) for the requested scope.
    Supported given your actual columns:
      - "segment" or "street_segment"  -> asset_parking_bay.segment_id = %s
      - "bay"                           -> a single bay_id = %s
    """
    s = (scope or "").lower()
    if s in ("segment", "street_segment"):
        return f"(SELECT b.bay_id FROM {_t('asset_parking_bay')} b WHERE b.segment_id = %s)"
    if s == "bay":
        # Pass the bay_id directly as a single-row "table"
        return "(SELECT %s AS bay_id)"
    return None

def _hourly_sql_for_scope(sb_sql: str) -> str:
    return f"""
    WITH scoped_bays AS {sb_sql},
    joined AS (
        SELECT
            o.status_ts AS tstamp,
            CASE
              WHEN UPPER(COALESCE(o.status_desc,'')) IN ('OCCUPIED','BUSY') THEN 1
              WHEN o.status_desc IN (1,'1','Y','YES','Y') THEN 1
              ELSE 0
            END AS occ
        FROM {_t('ops_bay_status')} o
        JOIN scoped_bays sb ON sb.bay_id = o.bay_id
        WHERE o.status_ts BETWEEN %s AND %s
    )
    SELECT DATE_FORMAT(tstamp, '%%Y-%%m-%%d %%H:00:00') AS hour,
           COUNT(*) AS samples,
           SUM(1 - occ) AS free_obs,
           SUM(occ)     AS occ_obs
    FROM joined
    GROUP BY hour
    ORDER BY hour;
    """

def _heatmap_sql_for_scope(sb_sql: str) -> str:
    return f"""
    WITH scoped_bays AS {sb_sql},
    scoped AS (
        SELECT
            o.status_ts AS tstamp,
            CASE
              WHEN UPPER(COALESCE(o.status_desc,'')) IN ('OCCUPIED','BUSY') THEN 0
              WHEN o.status_desc IN (1,'1','Y','YES','Y') THEN 0
              ELSE 1
            END AS is_free
        FROM {_t('ops_bay_status')} o
        JOIN scoped_bays sb ON sb.bay_id = o.bay_id
        WHERE o.status_ts BETWEEN %s AND %s
    ),
    bucketed AS (
        SELECT
            MOD((DAYOFWEEK(tstamp)+5), 7) AS dow,  -- 0=Mon..6=Sun
            HOUR(tstamp)                  AS hh,
            COUNT(*)                      AS samples,
            AVG(is_free)                  AS avg_free_ratio
        FROM scoped
        GROUP BY dow, hh
    )
    SELECT dow, hh, samples, avg_free_ratio FROM bucketed ORDER BY dow, hh;
    """

# -------------------- Swagger request bodies --------------------

class HistoryQueryBody(serializers.Serializer):
    # Use one of these:
    #   - scope+id (recommended: "segment" or "bay")
    #   - lat+lng (+radius)  -> disabled w/o spatial permissions (explained at runtime)
    scope = serializers.ChoiceField(["segment", "street_segment", "bay"], required=False)
    id = serializers.CharField(required=False)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    radiusMeters = serializers.IntegerField(required=False, default=300)
    startDate = serializers.CharField(required=False)
    endDate   = serializers.CharField(required=False)

class SummaryQueryBody(HistoryQueryBody):
    minSamplesPerBucket = serializers.IntegerField(required=False, default=10)
    topN = serializers.IntegerField(required=False, default=3)

# -------------------- Time helper --------------------

def _resolve_times_from_request(request) -> Tuple[str, str]:
    end_iso = _parse_dt(request.data.get("endDate") if request.method == "POST" else request.GET.get("endDate"),
                        datetime.utcnow())
    end_dt = datetime.fromisoformat(end_iso)
    start_iso = _parse_dt(
        request.data.get("startDate") if request.method == "POST" else request.GET.get("startDate"),
        end_dt - timedelta(days=30),
    )
    return start_iso, end_iso

# -------------------- Views --------------------

@extend_schema(
    summary="Historical parking (hourly) — by segment or bay",
    request=HistoryQueryBody,
    responses={200: OpenApiResponse(description="Hourly series")},
    parameters=[
        OpenApiParameter("scope", str, False, description="segment | street_segment | bay"),
        OpenApiParameter("id", str, False, description="segment_id or bay_id matching the chosen scope"),
        OpenApiParameter("startDate", str, False),
        OpenApiParameter("endDate", str, False),
        # The lat/lng options are shown but will return a clear 400 due to DB permissions:
        OpenApiParameter("lat", float, False),
        OpenApiParameter("lng", float, False),
        OpenApiParameter("radiusMeters", int, False),
    ],
)
class ParkingHistoryApi(APIView):
    def post(self, request):
        body = HistoryQueryBody(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        start_iso, end_iso = _resolve_times_from_request(request)

        has_scope = bool((data.get("scope") or "") and data.get("id"))
        has_point = (data.get("lat") is not None and data.get("lng") is not None)

        if not (has_scope or has_point):
            return Response({"error": "Provide either scope+id OR lat+lng."}, status=400)

        # Point search disabled: no spatial perms + no lat/lon columns in asset_parking_bay
        if has_point and not has_scope:
            return Response({
                "error": "Point-radius search is disabled for this database user (no EXECUTE on spatial routines), "
                         "and asset_parking_bay does not expose lat/lon columns. Use scope+id instead.",
                "how_to_test_quickly": {
                    "scope": "segment",
                    "id": "<an existing segment_id from asset_parking_bay>",
                    "date_window_hint": "Use dates between your ops_bay_status min/max timestamps."
                }
            }, status=400)

        # Scope path (works with your schema)
        sb = _scoped_bays(data["scope"])
        if not sb:
            return Response({"error": f"Unsupported scope '{data['scope']}'. Use 'segment' or 'bay'."}, status=400)

        try:
            sql = _hourly_sql_for_scope(sb)
            # 'segment' takes 1 param; 'bay' also takes 1. Both then take start,end.
            params = [data["id"], start_iso, end_iso]
            rows = _run(sql, params)
        except Exception as e:
            return Response({"error": f"SQL error: {e}"}, status=400)

        items: List[Dict[str, Any]] = []
        for hour, samples, free_obs, occ_obs in rows:
            samples = int(samples or 0); free_obs = int(free_obs or 0); occ_obs = int(occ_obs or 0)
            items.append({
                "timestamp": hour,
                "samples": samples,
                "free": free_obs,
                "occupied": occ_obs,
                "free_ratio": round(free_obs / samples, 4) if samples else None,
            })

        if not items:
            return Response({
                "items": [],
                "summary": {"count": 0},
                "hint": "No observations for the chosen scope in this date range. "
                        "Try a busier segment_id or expand the date window."
            }, status=200)

        return Response({
            "items": items,
            "summary": {"count": len(items), "start": items[0]["timestamp"], "end": items[-1]["timestamp"]}
        })

    def get(self, request):
        fake = {
            "scope": request.GET.get("scope"),
            "id": request.GET.get("id"),
            "lat": request.GET.get("lat"),
            "lng": request.GET.get("lng"),
            "radiusMeters": request.GET.get("radiusMeters"),
            "startDate": request.GET.get("startDate"),
            "endDate": request.GET.get("endDate"),
        }
        request._full_data = fake
        return self.post(request)

@extend_schema(
    summary="Historical summary (7×24 heatmap) + suggested arrival windows — by segment or bay",
    request=SummaryQueryBody,
    responses={200: OpenApiResponse(description="Heatmap + windows")},
)
class ParkingHistorySummaryApi(APIView):
    def post(self, request):
        body = SummaryQueryBody(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data

        end_iso = _parse_dt(data.get("endDate"), datetime.utcnow())
        end_dt = datetime.fromisoformat(end_iso)
        start_iso = _parse_dt(data.get("startDate"), end_dt - timedelta(days=90))
        min_samples = int(data.get("minSamplesPerBucket", 10))
        topn = max(1, min(10, int(data.get("topN", 3))))

        has_scope = bool((data.get("scope") or "") and data.get("id"))
        has_point = (data.get("lat") is not None and data.get("lng") is not None)

        if not (has_scope or has_point):
            return Response({"error": "Provide either scope+id OR lat+lng."}, status=400)

        if has_point and not has_scope:
            return Response({
                "error": "Point-radius search is disabled for this database user (no EXECUTE on spatial routines), "
                         "and asset_parking_bay does not expose lat/lon columns. Use scope+id instead."
            }, status=400)

        sb = _scoped_bays(data["scope"])
        if not sb:
            return Response({"error": f"Unsupported scope '{data['scope']}'. Use 'segment' or 'bay'."}, status=400)

        try:
            sql = _heatmap_sql_for_scope(sb)
            rows = _run(sql, [data["id"], start_iso, end_iso])
        except Exception as e:
            return Response({"error": f"SQL error: {e}"}, status=400)

        heatmap = [{"dow": int(dow), "hh": int(hh), "samples": int(s or 0), "avg_free_ratio": float(r or 0)} for dow, hh, s, r in rows]
        windows = _best_windows(heatmap, min_samples=min_samples, topn=topn)

        if not heatmap:
            return Response({
                "heatmap": [],
                "windows": [],
                "hint": "No observations for the chosen scope in this date range. Try another id or wider dates."
            }, status=200)

        return Response({"heatmap": heatmap, "windows": windows})

    def get(self, request):
        fake = {
            "scope": request.GET.get("scope"),
            "id": request.GET.get("id"),
            "lat": request.GET.get("lat"),
            "lng": request.GET.get("lng"),
            "radiusMeters": request.GET.get("radiusMeters"),
            "startDate": request.GET.get("startDate"),
            "endDate": request.GET.get("endDate"),
            "minSamplesPerBucket": request.GET.get("minSamplesPerBucket"),
            "topN": request.GET.get("topN"),
        }
        request._full_data = fake
        return self.post(request)

# -------------------- Helpers --------------------

def _best_windows(heatmap: List[Dict[str, Any]], min_samples: int, topn: int) -> List[Dict[str, Any]]:
    filtered = [b for b in heatmap if (b.get("samples") or 0) >= min_samples]
    filtered.sort(key=lambda x: x.get("avg_free_ratio", 0), reverse=True)
    return [
        {"dow": int(r["dow"]), "hour": int(r["hh"]), "avg_free_ratio": round(float(r["avg_free_ratio"]), 4)}
        for r in filtered[:topn]
    ]
