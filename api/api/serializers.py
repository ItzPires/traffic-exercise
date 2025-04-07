from rest_framework import serializers
from .models import RoadSegment, SpeedReading

class RoadSegmentSerializer(serializers.ModelSerializer):
    current_speed = serializers.SerializerMethodField()
    traffic_intensity = serializers.SerializerMethodField()
    readings_count = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = RoadSegment
        fields = '__all__'
        extra_fields = ['current_speed', 'traffic_intensity', 'readings_count', 'updated_at']

    def get_current_speed(self, obj):
        return obj.current_speed
    
    def get_traffic_intensity(self, obj):
        return obj.traffic_intensity

    def get_readings_count(self, obj):
        return obj.readings.count()

    def get_updated_at(self, obj):
        return obj.updated_at

class SpeedReadingSerializer(serializers.ModelSerializer):
    traffic_intensity = serializers.ReadOnlyField()

    class Meta:
        model = SpeedReading
        fields = '__all__'
