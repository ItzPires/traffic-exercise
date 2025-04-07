import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from api.models import RoadSegment, SpeedReading, Sensor

def create_admin():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password='admin'
        )
        print("Admin user created")

def import_road_segments():
    # Road Segments
    csv_path = './data/traffic_speed.csv'
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        
        count = 0
        for row in reader:
            try:
                id, start_lon, start_lat, end_lon, end_lat, length, speed = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                
                RoadSegment.objects.create(
                    start_point=Point(float(start_lon), float(start_lat)),
                    end_point=Point(float(end_lon), float(end_lat)),
                    length=float(length)
                )
                SpeedReading.objects.create(
                    road_segment=road_segment,
                    speed=float(speed)
                )
                count += 1
            except Exception as e:
                print(f"Error in row {row}: {e}")
                continue

    print(f"{count} road segments imported")

def import_sensors():
    # Speed Readings
    csv_path = './data/sensors.csv'
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        
        count = 0
        for row in reader:
            try:
                id, name, uuid = row[0], row[1], row[2]
                
                Sensor.objects.create(
                    name=name,
                    uuid=uuid
                )
                count += 1
            except Exception as e:
                print(f"Error in row {row}: {e}")
                continue

    print(f"{count} sensores imported")

if __name__ == '__main__':
    create_admin()
    import_road_segments()
    import_sensors()
