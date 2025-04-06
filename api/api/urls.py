from django.urls import path
from .views import CSVUploadView

urlpatterns = [
    path('upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
]

