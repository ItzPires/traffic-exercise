from django.db import models
from django.contrib.gis.db import models as gis_models

class RoadSegment(models.Model):
    start_point = gis_models.PointField(null=False, blank=False)
    end_point = gis_models.PointField(null=False, blank=False)
    length = models.FloatField(default=0.0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def current_speed(self):
        last_reading = self.readings.order_by('-created_at').first()
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

class SpeedReading(models.Model):
    road_segment = models.ForeignKey(RoadSegment, related_name='readings', on_delete=models.CASCADE)
    speed = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class TrafficIntensityThreshold(models.Model):
    medium_min = models.FloatField(default=20.0) # Medium min and high max are the same
    medium_max = models.FloatField(default=50.0) # Medium max and low min are the same
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @classmethod
    def current(cls):
        return cls.objects.first() or cls()
