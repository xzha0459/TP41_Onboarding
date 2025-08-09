from django.urls import path
from . import views

urlpatterns = [
    path('', views.ParkingListApi.as_view(), name='parking-list'),
    path('nearby', views.ParkingNearbyApi.as_view(), name='parking-nearby'),
    path('nearby/predict', views.ParkingNearbyPredictApi.as_view(), name='parking-nearby-predict'),
]