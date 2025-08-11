from django.urls import path
from . import views
from .views_history import ParkingHistoryApi, ParkingHistorySummaryApi


urlpatterns = [
    path('', views.ParkingListApi.as_view(), name='parking-list'),
    path('nearby', views.ParkingNearbyApi.as_view(), name='parking-nearby'),
    path('nearby/predict', views.ParkingNearbyPredictApi.as_view(), name='parking-nearby-predict'),
    path('history', ParkingHistoryApi.as_view(), name='parking-history'),
    path('history/summary', ParkingHistorySummaryApi.as_view(), name='parking-history-summary'),
]