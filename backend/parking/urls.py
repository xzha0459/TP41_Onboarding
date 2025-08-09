from django.urls import path
from . import views

urlpatterns = [
    path('', views.ParkingSpotListApi.as_view(), name='parking-spot-list'),
    path('nearby', views.ParkingSpotNearbyWalkTimeApi.as_view(), name='parking-spot-nearby-walk-time'),
]