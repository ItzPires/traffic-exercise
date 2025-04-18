import csv
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    RoadSegment,
    SpeedReading,
    TrafficIntensityThreshold,
    Car,
    Sensor,
    TrafficObservation,
)
from django.contrib.gis.geos import Point
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    RoadSegmentSerializer,
    SpeedReadingSerializer,
    TrafficIntensityThresholdSerializer,
    CarSerializer,
    SensorSerializer,
    TrafficObservationSerializer,
)
from .permissions import IsAdminOrReadOnly, SensorAPIOnlyPermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        # Verify if is a CSV file
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            return JsonResponse({"error": "No CSV file uploaded."}, status=400)
        if not csv_file.name.endswith(".csv"):
            return JsonResponse({"error": "The file is not a CSV."}, status=400)

        file_content = csv_file.read().decode("utf-8")
        reader = csv.reader(file_content.splitlines())

        next(reader)  # Skip header row

        created_segments = []
        for row in reader:
            try:
                id, start_lon, start_lat, end_lon, end_lat, length, speed = (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                )

                start_point = Point(float(start_lon), float(start_lat))
                end_point = Point(float(end_lon), float(end_lat))

                road_segment = RoadSegment.objects.create(
                    start_point=start_point, end_point=end_point, length=length
                )

                SpeedReading.objects.create(
                    road_segment=road_segment, speed=float(speed)
                )

                created_segments.append(road_segment.id)

            except Exception as e:
                return JsonResponse(
                    {"error": f"Error while processing line {row}: {str(e)}"},
                    status=400,
                )

        return JsonResponse(
            {
                "message": "CSV successfully processed",
                "created_segments": created_segments,
                "readings_created": len(created_segments),
            },
            status=201,
        )


class RoadSegmentViewSet(viewsets.ModelViewSet):
    queryset = RoadSegment.objects.all()
    serializer_class = RoadSegmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "intensity",
                openapi.IN_QUERY,
                description="Filter by traffic intensity (high, medium, low)",
                type=openapi.TYPE_STRING,
                enum=["high", "medium", "low"],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        intensity = self.request.query_params.get("intensity", "").lower()

        if intensity in ["high", "medium", "low"]:
            queryset = [
                segment
                for segment in queryset
                if segment.traffic_intensity == intensity
            ]

            ids = [segment.id for segment in queryset]
            queryset = RoadSegment.objects.filter(id__in=ids)

        return queryset


class SpeedReadingViewSet(viewsets.ModelViewSet):
    queryset = SpeedReading.objects.all()
    serializer_class = SpeedReadingSerializer
    permission_classes = [IsAdminOrReadOnly]


class TrafficIntensityThresholdViewSet(viewsets.ModelViewSet):
    queryset = TrafficIntensityThreshold.objects.all()
    serializer_class = TrafficIntensityThresholdSerializer
    http_method_names = ["get", "post", "head"]  # Disable PUT/PATCH/DELETE

    def list(self, request, *args, **kwargs):
        instance = TrafficIntensityThreshold.current()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        return TrafficIntensityThreshold.objects.all().order_by("-created_at")[:1]


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "post", "delete", "head"]  # Disable PUT/PATCH

    @swagger_auto_schema(
        operation_description="Get last 24h observations for a car",
        responses={200: "Success", 400: "Bad Request", 404: "Car Not Found"},
        manual_parameters=[
            openapi.Parameter(
                "license_plate",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                example="AA16AA",
            )
        ],
    )
    @action(detail=False, methods=["get"])
    def last_24h_observations(self, request):
        license_plate = request.query_params.get("license_plate")

        if not license_plate:
            return Response(
                {"error": "License plate is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        start_time = now - timedelta(hours=24)

        try:
            car = Car.objects.get(license_plate=license_plate)
            observations = (
                TrafficObservation.objects.filter(car=car, timestamp__gte=start_time)
                .select_related("sensor", "road_segment")
                .order_by("-timestamp")
            )

            result = {
                "car": {
                    "license_plate": car.license_plate,
                    "created_at": car.created_at,
                },
                "observations": [],
            }

            for obs in observations:
                result["observations"].append(
                    {
                        "timestamp": obs.timestamp,
                        "road_segment": {
                            "id": obs.road_segment.id,
                            "length": obs.road_segment.length,
                            "current_speed": obs.road_segment.current_speed,
                            "traffic_intensity": obs.road_segment.traffic_intensity,
                        },
                        "sensor": {
                            "uuid": str(obs.sensor.uuid),
                            "name": obs.sensor.name,
                        },
                    }
                )

            return Response(result)

        except Car.DoesNotExist:
            return Response(
                {"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "post", "delete", "head"]  # Disable PUT/PATCH


class TrafficObservationViewSet(viewsets.ModelViewSet):
    queryset = TrafficObservation.objects.all()
    serializer_class = TrafficObservationSerializer
    permission_classes = [SensorAPIOnlyPermission]
    http_method_names = ["get", "post", "head"]  # Disable PUT/PATCH/DELETE

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # Bulk create
            serializer = self.get_serializer(data=request.data, many=True)
        else:  # Single create
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
