from django.urls import path
from . import views

urlpatterns = [
    path('', views.InsightsIndexApi.as_view(), name='insightsIndex'),
    path('carOwnership', views.CarOwnershipApi.as_view(), name='carOwnership'),
    path('cbdPopulation', views.CbdPopulationGrowthApi.as_view(), name='cbdPopulation'),
]
