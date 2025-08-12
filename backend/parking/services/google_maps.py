import requests
from django.conf import settings

class GeocodeError(Exception):
    pass

def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status == "ZERO_RESULTS":
            raise GeocodeError("Address not found.")
        if status != "OK":
            error_message = data.get("error_message", status)
            raise GeocodeError(f"Google Maps API error: {error_message}")
        results = data.get("results")
        location = results[0]["geometry"]["location"]
        formatted_address = results[0].get("formatted_address", address)
        return {
            "latitude": location["lat"],
            "longitude": location["lng"],
            "address": address,
            "formatted_address": formatted_address,
        }
    except requests.RequestException as e:
        raise GeocodeError(f"Geocoding request failed: {e}")