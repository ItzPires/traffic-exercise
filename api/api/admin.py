from django.contrib import admin
from .models import RoadSegment, SpeedReading, TrafficIntensityThreshold

admin.site.register(RoadSegment)
admin.site.register(SpeedReading)
admin.site.register(TrafficIntensityThreshold)
