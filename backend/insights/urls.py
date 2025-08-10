from django.urls import path
from . import views

urlpatterns = [
    path('carOwnership', views.CarOwnershipApi.as_view(), name='carOwnership'),
    path('cbdPopulation', views.CbdPopulationGrowthApi.as_view(), name='cbdPopulation'),
]
