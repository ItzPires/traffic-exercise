from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CSVUploadView, RoadSegmentViewSet, SpeedReadingViewSet, TrafficIntensityThresholdViewSet, CarViewSet, SensorViewSet, TrafficObservationViewSet

router = DefaultRouter()
router.register(r'roadsegment', RoadSegmentViewSet, basename='road-segment')
router.register(r'speedreading', SpeedReadingViewSet, basename='speed-reading')
router.register(r'thresholds', TrafficIntensityThresholdViewSet, basename='threshold')
router.register(r'cars', CarViewSet, basename='car')
router.register(r'sensors', SensorViewSet, basename='sensor')
router.register(r'trafficobservations', TrafficObservationViewSet, basename='traffic-observation')

urlpatterns = [
    path('upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('', include(router.urls)),
]
