from rest_framework import serializers
from .models import RoadSegment, SpeedReading

class RoadSegmentSerializer(serializers.ModelSerializer):
    current_speed = serializers.SerializerMethodField()
    traffic_intensity = serializers.SerializerMethodField()
    readings_count = serializers.SerializerMethodField()

    class Meta:
        model = RoadSegment
        fields = '__all__'
        extra_fields = ['current_speed', 'traffic_intensity', 'readings_count']

    def get_current_speed(self, obj):
        return obj.current_speed
    
    def get_traffic_intensity(self, obj):
        return obj.traffic_intensity

    def get_readings_count(self, obj):
        return obj.readings.count()

class SpeedReadingSerializer(serializers.ModelSerializer):
    traffic_intensity = serializers.ReadOnlyField()

    class Meta:
        model = SpeedReading
        fields = '__all__'
