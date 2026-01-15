import google.generativeai as genai
import json
import re
from PIL import Image
from utils.timing import time_execution
from utils.tokens import track_usage

class PoolDetector:
    def __init__(self, api_key, model_name="gemini-3-pro-preview"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    @time_execution
    def detect_pools(self, image):
        """
        Pass 1: Detect potential pools in a wide satellite tile.
        """
        prompt = """
        Analyze this satellite image. Identify all outdoor swimming pools.
        
        CRITICAL IDENTIFICATION RULES:
        1. CONTEXT MATTERS: Pools are almost always in private backyards, hotel courtyards, or rooftops. They are ALMOST NEVER directly adjacent to a public road.
        2. WATER SIGNATURE: Look for clear water (deep blue/turquoise). 
        
        STRICT EXCLUSIONS:
        - BLUE TARPS ON ROOFS: If a blue rectangle is on a roof with no visible border, steps, or access, it is likely a tarp or utility cover. EXCLUDE IT.
        - SPORTS COURTS: Basketball, tennis, or padel courts.
        - PLAYGROUNDS: Blue rubber safety surfaces.
        
        For each potential pool found, provide its bounding box coordinates in a JSON list:
        [
          {"box_2d": [ymin, xmin, ymax, xmax], "label": "potential_pool"}
        ]
        The coordinates should be normalized from 0 to 1000.
        If no pools are found, return []. ONLY return the JSON.
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            track_usage(
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.candidates_token_count
            )
            
            text = response.text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            print(f"Error in detect_pools: {e}")
            return []

    @time_execution
    def verify_pool(self, image_crop):
        """
        Pass 2: Confirm if a tight crop actually contains a pool.
        """
        prompt = """
        This is a tight zoom of a potential swimming pool. 
        Analyze it carefully to decide if it is a REAL swimming pool or a false positive (like a blue roof tarp, blue bin, or sports court).
        
        Pool Indicators:
        - Visible coping (the stone or tile border around the edge).
        - Visible steps, ladders, or underwater lights.
        - Texture of water (ripples, depth, clarity).
        - Decking or lounge area surrounding it.
        
        False Positive Indicators:
        - Flat, uniform texture (like a plastic tarp).
        - No border or coping; seems to be part of the roof structure.
        - EXCLUSIVE ROOFTOP RULE: If a blue rectangle is embedded in a roof with NO visible pedestrian access (no stairs, no deck, no clear path), it is a tarp.
        - Located in a strange place (e.g., middle of a road, immediately adjacent to a road, or industrial roof with no access).
        
        Return ONLY 'TRUE' if it is definitely a pool, or 'FALSE' if it is a false positive.
        """
        
        try:
            response = self.model.generate_content([prompt, image_crop])
            track_usage(
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.candidates_token_count
            )
            
            result = response.text.strip().upper()
            return "TRUE" in result
        except Exception as e:
            print(f"Error in verify_pool: {e}")
            return False

    def process_tile(self, tile_data):
        """
        Detects pools in a tile and converts their coordinates to latitude/longitude.
        This now only performs Pass 1. Pass 2 should be handled by the orchestrator (app.py).
        """
        image = tile_data["image"]
        candidates = self.detect_pools(image)
        
        results = []
        img_width, img_height = image.size
        
        for cand in candidates:
            box = cand.get("box_2d")
            if not box or len(box) != 4: continue
                
            ymin, xmin, ymax, xmax = box
            
            # Center of the box in normalized coordinates
            center_y_norm = (ymin + ymax) / 2
            center_x_norm = (xmin + xmax) / 2
            
            # Map normalized 0-1000 to pixels
            px_x = (center_x_norm / 1000) * img_width
            px_y = (center_y_norm / 1000) * img_height
            
            from services.google_maps import GoogleMapsService
            lat, lng = GoogleMapsService.pixel_to_coords(
                px_x, px_y,
                tile_data["center_lat"],
                tile_data["center_lng"],
                tile_data["meters_per_pixel"] / 2, # Division by 2 because of scale=2
                img_width,
                img_height
            )
            
            # Crop the candidate for verification (scaled coordinates)
            left = (xmin / 1000) * img_width
            top = (ymin / 1000) * img_height
            right = (xmax / 1000) * img_width
            bottom = (ymax / 1000) * img_height
            
            # Add some padding to the crop
            pad_w = (right - left) * 0.5
            pad_h = (bottom - top) * 0.5
            crop_box = (
                max(0, left - pad_w),
                max(0, top - pad_h),
                min(img_width, right + pad_w),
                min(img_height, bottom + pad_h)
            )
            crop_img = image.crop(crop_box)
            
            results.append({
                "latitude": lat,
                "longitude": lng,
                "box": box,
                "crop_img": crop_img
            })
            
        return results
