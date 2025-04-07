from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CSVUploadView, RoadSegmentViewSet, SpeedReadingViewSet, TrafficIntensityThresholdViewSet

router = DefaultRouter()
router.register(r'roadsegment', RoadSegmentViewSet, basename='roadsegment')
router.register(r'speedreading', SpeedReadingViewSet, basename='speedreading')
router.register(r'thresholds', TrafficIntensityThresholdViewSet, basename='threshold')

urlpatterns = [
    path('upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('', include(router.urls)),
]
