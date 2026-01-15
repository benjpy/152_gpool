import googlemaps
import requests
import math
import os
from PIL import Image
from io import BytesIO
from utils.timing import time_execution

class GoogleMapsService:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
        self.api_key = api_key

    @time_execution
    def get_coordinates(self, address):
        """Converts an address or location name to latitude and longitude."""
        try:
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                return None
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def get_satellite_tile(self, lat, lng, zoom=20, size="640x640", scale=2):
        """Fetches a single satellite map tile."""
        url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "center": f"{lat},{lng}",
            "zoom": zoom,
            "size": size,
            "maptype": "satellite",
            "scale": scale,
            "key": self.api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print(f"Error fetching tile: {response.status_code} - {response.text}")
            return None

    def get_tiles_for_radius(self, center_lat, center_lng, radius_meters, zoom=20):
        """
        Calculates and fetches tiles to cover a radius.
        For simplicity in this version, we'll start with a small grid. 
        Zoom 20 is ~0.15m/pixel. Zoom 19 is ~0.3m/pixel.
        A 640x640 tile at Zoom 19 is roughly 190m across.
        """
        # Calculate how many meters per pixel at this latitude and zoom
        # Formula: meters_per_pixel = 156543.03392 * cos(lat * PI / 180) / 2^zoom
        meters_per_pixel = 156543.03392 * math.cos(center_lat * math.pi / 180) / math.pow(2, zoom)
        tile_size_meters = 640 * meters_per_pixel # At scale 1. Scale 2 doubles resolution but area stays same if size=640x640
        
        # Determine grid size (simplistic square grid for now)
        tiles_needed = math.ceil((radius_meters * 2) / tile_size_meters)
        if tiles_needed % 2 == 0: tiles_needed += 1 # Ensure odd number for center
        
        half_grid = tiles_needed // 2
        
        tiles = []
        
        # Degree per meter (approximate)
        lat_step = (1 / 111111) * tile_size_meters
        lng_step = (1 / (111111 * math.cos(center_lat * math.pi / 180))) * tile_size_meters
        
        for i in range(-half_grid, half_grid + 1):
            for j in range(-half_grid, half_grid + 1):
                lat = center_lat + i * lat_step
                lng = center_lng + j * lng_step
                
                # Fetch tile
                img = self.get_satellite_tile(lat, lng, zoom=zoom)
                if img:
                    tiles.append({
                        "image": img,
                        "center_lat": lat,
                        "center_lng": lng,
                        "meters_per_pixel": meters_per_pixel,
                        "zoom": zoom
                    })
        
        return tiles

    @staticmethod
    def pixel_to_coords(px_x, px_y, tile_center_lat, tile_center_lng, meters_per_pixel, img_width, img_height):
        """Converts pixel coordinates in a tile back to global lat/lng."""
        # Offset from center in pixels
        dx_px = px_x - (img_width / 2)
        dy_px = (img_height / 2) - px_y # Y is inverted in images
        
        # Offset in meters
        dx_m = dx_px * meters_per_pixel
        dy_m = dy_px * meters_per_pixel
        
        # Offset in degrees
        d_lat = dy_m / 111111
        d_lng = dx_m / (111111 * math.cos(tile_center_lat * math.pi / 180))
        
        return tile_center_lat + d_lat, tile_center_lng + d_lng
