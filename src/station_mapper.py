import json
from datetime import datetime
import threading
import time
import requests
from scipy.spatial import KDTree

class StationMapper:
    def __init__(self, cStation_source, cUpdate_interval):
        self.stations:dict = None
        self.station_list:list = []
        self.station_source:str = cStation_source
        self.update_interval:int = cUpdate_interval
        self.tree:KDTree = None
        
        thread = threading.Thread(target=self.worker_loop, daemon=True)
        thread.start()

    def map_coordinates_to_station(self, coordinates):
        if coordinates is None: return
        
        lat, lon = coordinates

        closest = self.find_closest(lat,lon)
        return closest

    def find_closest(self, lat, lon):
        _, idx = self.tree.query((lat, lon))
        stations = self.stations.get('stations')
        return stations[idx]  
    
    def worker_loop(self):
        while True:
            response = requests.get(self.station_source)

            if response.status_code != 200:
                print("Failed to fetch stations")
                time.sleep(self.update_interval)
                continue

            all_stations = json.loads(response.content)

            if self.stations_unchanged(all_stations): return
            self.stations = all_stations

            points = []
            self.station_list = []
            
            for s in self.stations.get('stations', []):
                lat = s.get('lat') if s.get('lat') is not None else s.get('latitude')
                lon = s.get('lon') if s.get('lon') is not None else s.get('longitude')

                if lat is None or lon is None:
                    continue

                points.append((lat, lon))
                self.station_list.append(s)

            self.tree = KDTree(points)
            
            print(f"Loaded {len(self.station_list)} entries...")
            time.sleep(self.update_interval)
    
    def stations_unchanged(self, all_stations):
        if self.stations is None: return False

        curdate = self.stations.get('exportedAt','')
        date = all_stations.get('exportedAt','')

        def iso_normalize(input:str):
            if input.endswith("Z"):
                input.replace("Z", "+00:00")
            return datetime.fromisoformat(input)

        curdate_obj = iso_normalize(curdate)
        date_obj = iso_normalize(date)

        return (curdate_obj - date_obj).total_seconds() > 0
