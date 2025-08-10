from django.db import models

# Create your models here.

class Parking(models.Model):
    kerbside_id = models.CharField(primary_key=True, max_length=50)
    zone_number = models.CharField(max_length=20)
    status_description = models.CharField(max_length=50)
    status_timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_updated = models.DateTimeField()
    
    class Meta:
        db_table = 'vw_api_bay_list'
    
    @property   
    def is_occupied(self):
        return self.status_description == "Present"

    def __str__(self):
        return f"{self.name} ({'Available' if self.is_available else 'Occupied'})"
