from rest_framework import serializers
from .models import RoadSegment, SpeedReading, TrafficIntensityThreshold, Sensor, Car, TrafficObservation

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

class TrafficIntensityThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficIntensityThreshold
        fields = '__all__'

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

class TrafficObservationSerializer(serializers.ModelSerializer):
    road_segment = serializers.PrimaryKeyRelatedField(queryset=RoadSegment.objects.all())
    license_plate = serializers.CharField(write_only=True)
    sensor_uuid = serializers.SlugRelatedField(queryset=Sensor.objects.all(), slug_field='uuid', write_only=True)
    
    # Get car and sensor details
    car = serializers.SerializerMethodField()
    sensor = serializers.SerializerMethodField()
    
    class Meta:
        model = TrafficObservation
        fields = [
            'id',
            'road_segment',
            'license_plate',
            'sensor_uuid',
            'timestamp',
            'created_at',
            'car',
            'sensor'
        ]
        read_only_fields = ['id', 'created_at', 'car', 'sensor']

    def get_car(self, obj):
        return {
            'license_plate': obj.car.license_plate,
            'created_at': obj.car.created_at
        }

    def get_sensor(self, obj):
        return {
            'id': obj.sensor.id,
            'uuid': str(obj.sensor.uuid),
            'name': obj.sensor.name
        }

    def create(self, validated_data):
        license_plate = validated_data.pop('license_plate')
        sensor = validated_data.pop('sensor')
        
        car, carCreated  = Car.objects.get_or_create(
            license_plate=license_plate
        )
        
        return TrafficObservation.objects.create(
            car=car,
            sensor=sensor,
            **validated_data
        )
