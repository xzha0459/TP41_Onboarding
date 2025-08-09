import requests
from django.conf import settings

def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        results = resp.json().get("results")
        if not results:
            return None, None
        location = results[0]["geometry"]["location"]
        return location["lat"], location["lng"]
    except requests.RequestException:
        return None, None