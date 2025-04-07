from rest_framework import serializers
from .models import RoadSegment, SpeedReading

class RoadSegmentSerializer(serializers.ModelSerializer):
    readings_count = serializers.SerializerMethodField()
    traffic_intensity = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadSegment
        fields = '__all__'
    
    def get_readings_count(self, obj):
        return obj.readings.count()
    
    def get_traffic_intensity(self, obj):
        return obj.traffic_intensity

class SpeedReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeedReading
        fields = '__all__'
