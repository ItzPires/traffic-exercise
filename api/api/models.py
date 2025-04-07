from django.db import models
from django.contrib.gis.db import models as gis_models

class RoadSegment(models.Model):
    start_point = gis_models.PointField(null=False, blank=False)
    end_point = gis_models.PointField(null=False, blank=False)
    length = models.FloatField(default=0.0, null=False, blank=False)
    speed = models.FloatField(default=0.0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def traffic_intensity(self):
        thresholds = TrafficIntensityThreshold.current()
        
        if self.speed > thresholds.medium_max:
            return "high"
        elif self.speed <= thresholds.medium_max <= and self.speed >= thresholds.low_min:
            return "medium"
        return "low"

class SpeedReading(models.Model):
    road_segment = models.ForeignKey(RoadSegment, related_name='readings', on_delete=models.CASCADE)
    speed = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class TrafficIntensityThreshold(models.Model):
    medium_min = models.FloatField(default=20.0) # Medium min and high max are the same
    medium_max = models.FloatField(default=50.0) # Medium max and low min are the same
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @classmethod
    def current(cls):
        return cls.objects.first() or cls()
