import csv
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import RoadSegment, SpeedReading, TrafficIntensityThreshold
from django.contrib.gis.geos import Point
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.http import JsonResponse
from .serializers import RoadSegmentSerializer, SpeedReadingSerializer, TrafficIntensityThresholdSerializer
from .permissions import IsAdminOrReadOnly

class CSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminOrReadOnly]
    
    def post(self, request, *args, **kwargs):
        # Verify if is a CSV file
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return JsonResponse({"error": "No CSV file uploaded."}, status=400)
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({"error": "The file is not a CSV."}, status=400)

        file_content = csv_file.read().decode('utf-8')
        reader = csv.reader(file_content.splitlines())

        next(reader) # Skip header row

        created_segments = []
        for row in reader:
            try:
                id, start_lon, start_lat, end_lon, end_lat, length, speed = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                
                start_point = Point(float(start_lon), float(start_lat))
                end_point = Point(float(end_lon), float(end_lat))
                
                road_segment = RoadSegment.objects.create(
                    start_point=start_point,
                    end_point=end_point,
                    length=length
                )
                
                SpeedReading.objects.create(
                    road_segment=road_segment,
                    speed=float(speed)
                )

                created_segments.append(road_segment.id)

            except Exception as e:
                return JsonResponse({"error": f"Error while processing line {row}: {str(e)}"}, status=400)

        return JsonResponse({
            "message": "CSV successfully processed",
            "created_segments": created_segments,
            "readings_created": len(created_segments)
        }, status=201)

class RoadSegmentViewSet(viewsets.ModelViewSet):
    queryset = RoadSegment.objects.all()
    serializer_class = RoadSegmentSerializer
    permission_classes = [IsAdminOrReadOnly]

class SpeedReadingViewSet(viewsets.ModelViewSet):
    queryset = SpeedReading.objects.all()
    serializer_class = SpeedReadingSerializer
    permission_classes = [IsAdminOrReadOnly]

class TrafficIntensityThresholdViewSet(viewsets.ModelViewSet):
    queryset = TrafficIntensityThreshold.objects.all()
    serializer_class = TrafficIntensityThresholdSerializer
    http_method_names = ['get', 'post', 'head']  # Disable PUT/PATCH/DELETE

    def list(self, request, *args, **kwargs):
        instance = TrafficIntensityThreshold.current()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        return TrafficIntensityThreshold.objects.all().order_by('-created_at')[:1]
