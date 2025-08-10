from django.db import models

class RegionBoundary(models.Model):
    regionId = models.CharField(max_length=32, primary_key=True)
    stateCode = models.CharField(max_length=8, db_index=True)  
    name = models.CharField(max_length=128)
    geometry = models.TextField(blank=True)  

    def __str__(self):
        return f"{self.regionId} {self.name}"

class RegionalPopulation(models.Model):
    region = models.ForeignKey(RegionBoundary, on_delete=models.CASCADE, related_name="pop")
    sa2 = models.CharField(max_length=32)              
    year = models.IntegerField()
    population = models.BigIntegerField()
    area = models.FloatField(null=True, blank=True)    
    density = models.FloatField(null=True, blank=True) 

    class Meta:
        unique_together = ("region", "year")
        indexes = [
            models.Index(fields=["year", "region"]),
            models.Index(fields=["sa2"]),
        ]

class MotorVehicleCensus(models.Model):
    state = models.CharField(max_length=8)     
    year = models.IntegerField()
    vehicleCount = models.BigIntegerField()
    growthRate = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("state", "year")
        indexes = [models.Index(fields=["state", "year"])]

    def __str__(self):
        return f"{self.state} {self.year}: {self.vehicleCount}"
