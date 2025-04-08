from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from ..models import RoadSegment, SpeedReading, TrafficIntensityThreshold
from django.contrib.gis.geos import Point

class RoadSegmentTests(APITestCase):
    def setUp(self):
        # Admin
        self.admin = User.objects.create_superuser(
            username="admin", password="admin", email="admin@admin.com"
        )

        # Road segment
        self.segment = RoadSegment.objects.create(
            start_point=Point(1.0, 1.0), end_point=Point(2.0, 2.0), length=1000.0
        )

        # Threshold for traffic intensity tests
        TrafficIntensityThreshold.objects.create(medium_min=20.0, medium_max=50.0)

    # Create a road segment by admin
    def test_create_road_segment_admin(self):
        url = reverse("road-segment-list")
        data = {
            "start_point": "POINT(3.0 3.0)",
            "end_point": "POINT(4.0 4.0)",
            "length": 1500.0,
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoadSegment.objects.count(), 2)

    # Create a road segment by anonymous user
    def test_create_road_segment_unauthenticated(self):
        url = reverse("road-segment-list")
        data = {
            "start_point": "POINT(3.0 3.0)",
            "end_point": "POINT(4.0 4.0)",
            "length": 1500.0,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(RoadSegment.objects.count(), 1)

    # Get list of road segments by admin
    def test_list_road_segments_admin(self):
        url = reverse("road-segment-list")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Get list of road segments by anonymous user
    def test_list_road_segments_unauthenticated(self):
        url = reverse("road-segment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Update a road segment by admin
    def test_update_road_segment_admin(self):
        url = reverse("road-segment-detail", args=[self.segment.id])
        data = {
            "start_point": "POINT(5.0 5.0)",
            "end_point": "POINT(6.0 6.0)",
            "length": 2000.0,
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.length, 2000.0)

    # Update a road segment by anonymous user
    def test_update_road_segment_unauthenticated(self):
        url = reverse("road-segment-detail", args=[self.segment.id])
        data = {
            "start_point": "POINT(5.0 5.0)",
            "end_point": "POINT(6.0 6.0)",
            "length": 2000.0,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Delete a road segment by admin
    def test_delete_road_segment_admin(self):
        url = reverse("road-segment-detail", args=[self.segment.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RoadSegment.objects.count(), 0)

    # Delete a road segment by anonymous user
    def test_delete_road_segment_unauthenticated(self):
        url = reverse("road-segment-detail", args=[self.segment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(RoadSegment.objects.count(), 1)

    # Get readings count for a road segment
    def test_road_segment_readings_count(self):
        SpeedReading.objects.create(road_segment=self.segment, speed=50.0)
        SpeedReading.objects.create(road_segment=self.segment, speed=60.0)
        SpeedReading.objects.create(road_segment=self.segment, speed=70.0)

        url = reverse("road-segment-detail", args=[self.segment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["readings_count"], 3)

    # Get current speed for a road segment
    def test_road_segment_current_speed(self):
        SpeedReading.objects.create(road_segment=self.segment, speed=50.0)
        latest_reading = SpeedReading.objects.create(
            road_segment=self.segment, speed=60.0
        )

        url = reverse("road-segment-detail", args=[self.segment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_speed"], latest_reading.speed)

    # Change traffic intensity thresholds
    def test_road_segment_traffic_intensity(self):
        SpeedReading.objects.create(road_segment=self.segment, speed=60.0)
        url = reverse("road-segment-detail", args=[self.segment.id])
        response = self.client.get(url)
        self.assertEqual(response.data["traffic_intensity"], "low")

        SpeedReading.objects.create(road_segment=self.segment, speed=30.0)
        response = self.client.get(url)
        self.assertEqual(response.data["traffic_intensity"], "medium")

        SpeedReading.objects.create(road_segment=self.segment, speed=10.0)
        response = self.client.get(url)
        self.assertEqual(response.data["traffic_intensity"], "high")

    # Filter segments by traffic intensity
    def test_filter_by_traffic_intensity(self):
        segment_low = RoadSegment.objects.create(start_point=Point(10.0, 10.0), end_point=Point(11.0, 11.0))
        SpeedReading.objects.create(road_segment=segment_low, speed=60.0)  # low

        segment_medium = RoadSegment.objects.create(start_point=Point(20.0, 20.0), end_point=Point(21.0, 21.0))
        SpeedReading.objects.create(road_segment=segment_medium, speed=30.0)  # medium

        segment_high = RoadSegment.objects.create(start_point=Point(30.0, 30.0), end_point=Point(31.0, 31.0))
        SpeedReading.objects.create(road_segment=segment_high, speed=10.0)  # high

        # Test low intensity filter
        url = reverse("road-segment-list") + "?intensity=low"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], segment_low.id)

        # Test medium intensity filter
        url = reverse("road-segment-list") + "?intensity=medium"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], segment_medium.id)

        # Test high intensity filter
        url = reverse("road-segment-list") + "?intensity=high"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], segment_high.id)
