from django.db import models

class DimRegion(models.Model):
    region_id = models.BigIntegerField(primary_key=True)
    region_code = models.CharField(max_length=64, blank=True, null=True)
    region_name = models.CharField(max_length=128)
    region_type = models.CharField(max_length=32)  # e.g., STATE, LGA, SA2
    parent_region_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'dim_region'
        managed = False


class FactAbsPopulation(models.Model):
    id = models.BigAutoField(primary_key=True)
    region = models.ForeignKey(
        DimRegion,
        to_field='region_id',
        db_column='region_id',
        on_delete=models.DO_NOTHING,
        related_name='pop_records',
        db_constraint=False,
    )
    ref_year = models.SmallIntegerField()
    population_total = models.IntegerField()
    population_male = models.IntegerField(blank=True, null=True)
    population_female = models.IntegerField(blank=True, null=True)
    source_file = models.CharField(max_length=255, blank=True, null=True)
    load_batch_id = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'fact_abs_population'
        managed = False


class FactAbsVehicleCensus(models.Model):
    id = models.BigAutoField(primary_key=True)
    region = models.ForeignKey(
        DimRegion,
        to_field='region_id',
        db_column='region_id',
        on_delete=models.DO_NOTHING,
        related_name='vehicle_records',
        db_constraint=False,
    )
    ref_year = models.SmallIntegerField()
    vehicle_type = models.CharField(max_length=64, blank=True, null=True)
    fuel_type = models.CharField(max_length=64, blank=True, null=True)
    vehicle_count = models.IntegerField()
    source_file = models.CharField(max_length=255, blank=True, null=True)
    load_batch_id = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'fact_abs_vehicle_census'
        managed = False
