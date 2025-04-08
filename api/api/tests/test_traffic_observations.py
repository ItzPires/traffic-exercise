from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from ..models import RoadSegment, Sensor, Car, TrafficObservation
from django.contrib.gis.geos import Point
import uuid


class TrafficObservationTests(APITestCase):
    def setUp(self):
        # Admin
        self.admin = User.objects.create_superuser(
            username="admin", password="admin", email="admin@admin.com"
        )

        # Create test data
        self.segment1 = RoadSegment.objects.create(
            start_point=Point(1.0, 1.0), end_point=Point(2.0, 2.0), length=1000.0
        )
        self.segment2 = RoadSegment.objects.create(
            start_point=Point(3.0, 3.0), end_point=Point(4.0, 4.0), length=1500.0
        )

        self.sensor1 = Sensor.objects.create(
            name="Sensor 1", uuid=uuid.UUID("270e4cc0-d454-4b42-8682-80e87c3d163c")
        )
        self.sensor2 = Sensor.objects.create(
            name="Sensor 2", uuid=uuid.UUID("a3e86bd0-c19f-44e9-84c0-eadf4d4da197")
        )

        # API keys
        self.valid_api_key = "23231c7a-80a7-4810-93b3-98a18ecfbc42"
        self.invalid_api_key = "invalid-key-1234"

    # Create multiple traffic observations with valid API key
    def test_create_bulk_traffic_observations_with_valid_api_key(self):
        """Should create multiple observations and cars with valid API key"""
        url = reverse("traffic-observation-list")
        data = [
            {
                "road_segment": self.segment1.id,
                "license_plate": "AA16AA",
                "timestamp": "2023-05-29T09:27:26.769Z",
                "sensor_uuid": str(self.sensor1.uuid),
            },
            {
                "road_segment": self.segment2.id,
                "license_plate": "BB17BB",
                "timestamp": "2025-04-07T17:05:21.713Z",
                "sensor_uuid": str(self.sensor2.uuid),
            },
        ]

        # Add valid API key to headers
        self.client.credentials(HTTP_X_API_KEY=self.valid_api_key)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify observations were created
        self.assertEqual(TrafficObservation.objects.count(), 2)
        self.assertEqual(Car.objects.count(), 2)

    # Create a traffic observation with invalid API key
    def test_create_traffic_observation_with_invalid_api_key(self):
        url = reverse("traffic-observation-list")
        data = {
            "road_segment": self.segment1.id,
            "license_plate": "AA16AA",
            "timestamp": "2023-05-29T09:27:26.769Z",
            "sensor_uuid": str(self.sensor1.uuid),
        }

        # Add invalid API key to headers
        self.client.credentials(HTTP_X_API_KEY=self.invalid_api_key)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TrafficObservation.objects.count(), 0)
        self.assertEqual(Car.objects.count(), 0)

    # Create a traffic observation without API key
    def test_create_traffic_observation_without_api_key(self):
        """Should reject request without API key"""
        url = reverse("traffic-observation-list")
        data = {
            "road_segment": self.segment1.id,
            "license_plate": "AA16AA",
            "timestamp": "2023-05-29T09:27:26.769Z",
            "sensor_uuid": str(self.sensor1.uuid),
        }

        # No API key in headers
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TrafficObservation.objects.count(), 0)
        self.assertEqual(Car.objects.count(), 0)

    # Create a traffic observation with non-existent sensor
    def test_create_traffic_observation_with_nonexistent_sensor(self):
        url = reverse("traffic-observation-list")
        data = {
            "road_segment": self.segment1.id,
            "license_plate": "AA16AA",
            "timestamp": "2023-05-29T09:27:26.769Z",
            "sensor_uuid": "00000000-0000-0000-0000-000000000000",  # Non-existent UUID
        }

        self.client.credentials(HTTP_X_API_KEY=self.valid_api_key)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrafficObservation.objects.count(), 0)
        self.assertEqual(Car.objects.count(), 0)

    # Create a traffic observation with non-existent road segment
    def test_create_traffic_observation_with_nonexistent_segment(self):
        url = reverse("traffic-observation-list")
        data = {
            "road_segment": 9999,  # Non-existent segment ID
            "license_plate": "AA16AA",
            "timestamp": "2023-05-29T09:27:26.769Z",
            "sensor_uuid": str(self.sensor1.uuid),
        }

        self.client.credentials(HTTP_X_API_KEY=self.valid_api_key)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrafficObservation.objects.count(), 0)
        self.assertEqual(Car.objects.count(), 0)
