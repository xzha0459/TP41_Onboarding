from django.core.management.base import BaseCommand
from django.db import transaction, models
from insights.models import RegionBoundary, RegionalPopulation, MotorVehicleCensus

class Command(BaseCommand):
    help = "Insert a minimal VIC/CBD dataset for testing insights endpoints."

    def add_arguments(self, parser):
        parser.add_argument("--stateCode", default="VIC")
        parser.add_argument("--regionIdentifier", default="CBD_SA2_ID")
        parser.add_argument("--regionName", default="Melbourne CBD")

    def handle(self, *args, **options):
        state_code = options["stateCode"]
        region_identifier = options["regionIdentifier"]
        region_name = options["regionName"]

        # ---------- RegionBoundary detection ----------
        rb_fields = {f.name for f in RegionBoundary._meta.get_fields() if getattr(f, "concrete", False)}
        # primary key / natural key
        rb_pk = "regionIdentifier" if "regionIdentifier" in rb_fields else ("regionId" if "regionId" in rb_fields else None)
        if rb_pk is None:
            raise RuntimeError("RegionBoundary must have 'regionIdentifier' or 'regionId'.")

        # state field
        rb_state = "stateCode" if "stateCode" in rb_fields else ("state" if "state" in rb_fields else None)
        if rb_state is None:
            raise RuntimeError("RegionBoundary must have 'stateCode' or 'state'.")

        # geometry optional
        has_geometry = "geometry" in rb_fields

        # ---------- MotorVehicleCensus detection ----------
        mvc_fields = {f.name for f in MotorVehicleCensus._meta.get_fields() if getattr(f, "concrete", False)}
        mvc_state = "stateCode" if "stateCode" in mvc_fields else ("state" if "state" in mvc_fields else None)
        if mvc_state is None:
            raise RuntimeError("MotorVehicleCensus must have 'stateCode' or 'state'.")
        has_vehicle_count = "vehicleCount" in mvc_fields

        # ---------- RegionalPopulation detection ----------
        rp_model = RegionalPopulation
        rp_fields = {f.name for f in rp_model._meta.get_fields() if getattr(f, "concrete", False)}

        if "year" not in rp_fields:
            raise RuntimeError("RegionalPopulation must have a 'year' field (int).")

        # find the FK field that points to RegionBoundary
        rp_region_fk = None
        for f in rp_model._meta.get_fields():
            if isinstance(f, models.ForeignKey) and f.concrete and f.related_model == RegionBoundary:
                rp_region_fk = f.name
                break
        if not rp_region_fk:
            raise RuntimeError("RegionalPopulation must have a ForeignKey to RegionBoundary.")

        # detect the population count column name
        pop_candidates = ["populationCount", "population", "pop", "count", "population_value", "value"]
        rp_pop_field = next((c for c in pop_candidates if c in rp_fields), None)
        if rp_pop_field is None:
            raise RuntimeError(
                "RegionalPopulation must have a population field. "
                f"Tried: {', '.join(pop_candidates)}. Actual fields: {sorted(rp_fields)}"
            )

        # optional extras if they exist
        has_sa2 = "sa2" in rp_fields
        has_area = "areaSquareKilometers" in rp_fields
        has_density = "populationDensityPerSquareKm" in rp_fields

        with transaction.atomic():
            # -------- Upsert Region --------
            region_lookup = {rb_pk: region_identifier}
            region_defaults = {rb_state: state_code, "name": region_name}
            if has_geometry:
                region_defaults["geometry"] = ""
            region, _ = RegionBoundary.objects.update_or_create(**region_lookup, defaults=region_defaults)

            # -------- Upsert Motor Vehicle rows --------
            vehicle_rows = [
                (2019, 4_800_000),
                (2020, 4_920_000),
                (2021, 5_040_000),
                (2022, 5_150_000),
            ]
            for year, vehicle_count in vehicle_rows:
                lookup = {mvc_state: state_code, "year": year}
                defaults = {}
                if has_vehicle_count:
                    defaults["vehicleCount"] = vehicle_count
                MotorVehicleCensus.objects.update_or_create(**lookup, defaults=defaults)

            # -------- Upsert CBD Population rows --------
            population_rows = [
                (2019, 45_000),
                (2020, 47_000),
                (2021, 52_000),
                (2022, 56_000),
            ]
            for year, pop_val in population_rows:
                defaults = {rp_pop_field: pop_val}
                if has_sa2:
                    defaults["sa2"] = region_identifier
                if has_area:
                    defaults["areaSquareKilometers"] = None
                if has_density:
                    defaults["populationDensityPerSquareKm"] = None

                RegionalPopulation.objects.update_or_create(
                    **{rp_region_fk: region, "year": year},
                    defaults=defaults,
                )

        self.stdout.write(self.style.SUCCESS("✅ Seeded sample VIC/CBD data for insights."))
