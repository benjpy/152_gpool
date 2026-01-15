import streamlit as st
import os
from dotenv import load_dotenv
from ui.elements import render_header, render_sidebar_info, display_results
from services.google_maps import GoogleMapsService
from services.pool_detector import PoolDetector
from utils.tokens import get_current_usage
from concurrent.futures import ThreadPoolExecutor, as_completed
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# Load local .env if available
load_dotenv()

# Capture the script context for background threads
ctx = get_script_run_ctx()

def thread_wrapper(func, *args, **kwargs):
    """Wraps a function to include Streamlit script context in background threads."""
    add_script_run_ctx(ctx=ctx)
    return func(*args, **kwargs)

st.set_page_config(
    page_title="Pool Finder AI",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_secret(key, default=None):
    """Retrieves a secret from Streamlit secrets or environment variables."""
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

def main():
    render_header()
    
    # Get API keys from sidebar or env/secrets
    sb_gmaps_key, sb_gai_key, radius = render_sidebar_info()
    
    gmaps_key = sb_gmaps_key or get_secret("GOOGLE_MAPS_API_KEY")
    gai_key = sb_gai_key or get_secret("GOOGLE_AI_API_KEY") or get_secret("GEMINI_API_KEY")
    
    if not gmaps_key or not gai_key:
        st.warning("Please provide both Google Maps and Google AI API keys in the sidebar, Streamlit secrets, or .env file.")
        return

    # Initialize services
    gmaps_service = GoogleMapsService(gmaps_key)
    detector = PoolDetector(gai_key)

    # Search Bar
    col1, col2 = st.columns([3, 1])
    with col1:
        address = st.text_input("Enter a location (e.g., 'Beverly Hills, CA' or a specific address)", placeholder="Search address...")
    with col2:
        st.write("##")
        search_clicked = st.button("Find Pools", type="primary", use_container_width=True)

    if search_clicked and address:
        with st.status("Analyzing area...", expanded=True) as status:
            st.write("Geocoding location...")
            coords = gmaps_service.get_coordinates(address)
            
            if not coords:
                st.error("Could not find coordinates for that location.")
                status.update(label="Analysis failed.", state="error")
                return
                
            lat, lng = coords
            st.write(f"Location found: {lat:.5f}, {lng:.5f}")
            
            st.write("Fetching satellite imagery...")
            tiles = gmaps_service.get_tiles_for_radius(lat, lng, radius)
            
            # --- PASS 1: DETECTION ---
            st.write(f"Pass 1: Detecting candidates in {len(tiles)} tiles...")
            candidates = []
            
            progress_bar = st.progress(0)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for tile in tiles:
                    f = executor.submit(thread_wrapper, detector.process_tile, tile)
                    futures.append(f)
                
                for idx, future in enumerate(as_completed(futures)):
                    try:
                        results = future.result()
                        candidates.extend(results)
                    except Exception as e:
                        st.error(f"Error in Pass 1: {e}")
                    progress_bar.progress((idx + 1) / (len(tiles) * 2)) # Occupy half progress

            # --- PASS 2: VERIFICATION ---
            if candidates:
                st.write(f"Pass 2: Verifying {len(candidates)} detections...")
                verified_pools = []
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for cand in candidates:
                        f = executor.submit(thread_wrapper, detector.verify_pool, cand["crop_img"])
                        futures.append((f, cand))
                    
                    for idx, (f, cand) in enumerate(futures):
                        try:
                            if f.result():
                                verified_pools.append(cand)
                        except Exception as e:
                            st.error(f"Error in Pass 2: {e}")
                        progress_bar.progress(0.5 + (idx + 1) / (len(candidates) * 2))
                
                st.session_state.detected_pools = verified_pools
            else:
                st.session_state.detected_pools = []
                
            status.update(label=f"Analysis complete! Found {len(st.session_state.detected_pools)} verified pools.", state="complete")
        
        st.session_state.last_coords = coords

    # Display results if they exist
    if 'detected_pools' in st.session_state:
        lat, lng = st.session_state.get('last_coords', (None, None))
        display_results(st.session_state.detected_pools, center_lat=lat, center_lng=lng)

if __name__ == "__main__":
    main()
