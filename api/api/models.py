from django.db import models
from django.contrib.gis.db import models as gis_models


class RoadSegment(models.Model):
    start_point = gis_models.PointField(null=False, blank=False)
    end_point = gis_models.PointField(null=False, blank=False)
    length = models.FloatField(default=0.0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def current_speed(self):
        last_reading = self.readings.order_by("-created_at").first()
        return last_reading.speed if last_reading else None

    @property
    def traffic_intensity(self):
        speed = self.current_speed
        if speed is None:
            return "no_data"

        thresholds = TrafficIntensityThreshold.current()

        if speed > thresholds.medium_max:
            return "low"
        elif speed <= thresholds.medium_max and speed > thresholds.medium_min:
            return "medium"
        return "high"

    @property
    def updated_at(self):
        last_reading = self.readings.order_by("-created_at").first()
        return last_reading.created_at if last_reading else self.created_at


class SpeedReading(models.Model):
    road_segment = models.ForeignKey(
        RoadSegment, related_name="readings", on_delete=models.CASCADE
    )
    speed = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class TrafficIntensityThreshold(models.Model):
    medium_min = models.FloatField(default=20.0)  # Medium min and high max are the same
    medium_max = models.FloatField(default=50.0)  # Medium max and low min are the same
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def current(cls):
        return cls.objects.first() or cls()

    # Validation of the model
    def clean(self):
        if self.medium_min >= self.medium_max:
            raise ValidationError(
                {
                    "medium_min": "Must be less than medium_max",
                    "medium_max": "Must be greater than medium_min",
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Before saving, call clean() to validate the model
        super().save(*args, **kwargs)


class Sensor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Car(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TrafficObservation(models.Model):
    road_segment = models.ForeignKey(RoadSegment, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
