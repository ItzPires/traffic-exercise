from django.db import models
from django.contrib.gis.db import models as gis_models

class RoadSegment(models.Model):
    start_point = gis_models.PointField(null=False, blank=False)
    end_point = gis_models.PointField(null=False, blank=False)
    length = models.FloatField(default=0.0, null=False, blank=False)
    speed = models.FloatField(default=0.0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
