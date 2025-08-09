from django.urls import path
from . import views

urlpatterns = [
    path('', views.ParkingSpotListApi.as_view(), name='parking-spot-list'),
    path('unoccupied', views.ParkingSpotUnoccupiedListApi.as_view(), name='parking-spot-unoccupied-list'),
]