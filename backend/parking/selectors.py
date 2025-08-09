from .models import ParkingSpot

def parking_spot_list(*, filters=None):
    filters = filters or {}
    qs = ParkingSpot.objects.all()
    if "is_occupied" in filters:
        status = "Present" if filters.pop("is_occupied") else "Unoccupied"
        qs = qs.filter(status_description=status)
    if filters:
        qs = qs.filter(**filters)
    return qs