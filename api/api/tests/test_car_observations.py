from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from ..models import RoadSegment, Sensor, Car, TrafficObservation
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
import uuid

class CarLast24hObservationsTests(APITestCase):
    def setUp(self):
        # Admin
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@admin.com'
        )
        
        # Create test data
        self.segment1 = RoadSegment.objects.create(
            start_point=Point(1.0, 1.0),
            end_point=Point(2.0, 2.0),
            length=1000.0
        )
        self.segment2 = RoadSegment.objects.create(
            start_point=Point(3.0, 3.0),
            end_point=Point(4.0, 4.0),
            length=1500.0
        )
        
        self.sensor1 = Sensor.objects.create(
            name="Sensor 1",
            uuid=uuid.uuid4()
        )
        self.sensor2 = Sensor.objects.create(
            name="Sensor 2",
            uuid=uuid.uuid4()
        )
        
        self.car = Car.objects.create(license_plate="AA16AA")
        
        now = timezone.now()
        
        # Within last 24h
        TrafficObservation.objects.create(
            road_segment=self.segment1,
            car=self.car,
            sensor=self.sensor1,
            timestamp=now - timedelta(hours=12)
        )
        TrafficObservation.objects.create(
            road_segment=self.segment2,
            car=self.car,
            sensor=self.sensor2,
            timestamp=now - timedelta(hours=6)
        )
        
        # Older than 24h
        TrafficObservation.objects.create(
            road_segment=self.segment1,
            car=self.car,
            sensor=self.sensor1,
            timestamp=now - timedelta(hours=25)
        )

    # Get last 24h observations for a car
    def test_get_last_24h_observations(self):
        url = reverse('car-last-24h-observations')
        params = {'license_plate': 'AA16AA'}
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('car', response.data)
        self.assertIn('observations', response.data)
        
        # Verify car data
        self.assertEqual(response.data['car']['license_plate'], 'AA16AA')
        
        # Should only return 2 observations
        self.assertEqual(len(response.data['observations']), 2)
        
        # Verify observation data
        for observation in response.data['observations']:
            self.assertIn('timestamp', observation)
            self.assertIn('road_segment', observation)
            self.assertIn('sensor', observation)
            
            # Verify road segment data
            self.assertIn('id', observation['road_segment'])
            self.assertIn('length', observation['road_segment'])
            self.assertIn('current_speed', observation['road_segment'])
            self.assertIn('traffic_intensity', observation['road_segment'])
            
            # Verify sensor data
            self.assertIn('uuid', observation['sensor'])
            self.assertIn('name', observation['sensor'])

    # Get last 24h observations without license plate
    def test_get_last_24h_observations_missing_license_plate(self):
        url = reverse('car-last-24h-observations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'License plate is required')

    # Get last 24h observations with invalid license plate
    def test_get_last_24h_observations_nonexistent_car(self):
        url = reverse('car-last-24h-observations')
        params = {'license_plate': 'NONEXISTENT'}
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Car not found')
