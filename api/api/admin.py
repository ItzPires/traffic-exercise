from django.contrib import admin
from .models import (
    RoadSegment,
    SpeedReading,
    TrafficIntensityThreshold,
    Sensor,
    Car,
    TrafficObservation,
)

admin.site.register(RoadSegment)
admin.site.register(SpeedReading)
admin.site.register(TrafficIntensityThreshold)
admin.site.register(Sensor)
admin.site.register(Car)
admin.site.register(TrafficObservation)
