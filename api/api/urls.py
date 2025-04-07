from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CSVUploadView, RoadSegmentViewSet, SpeedReadingViewSet

router = DefaultRouter()
router.register(r'roadsegment', RoadSegmentViewSet, basename='roadsegment')
router.register(r'speedreading', SpeedReadingViewSet, basename='speedreading')

urlpatterns = [
    path('upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('', include(router.urls)),
]
