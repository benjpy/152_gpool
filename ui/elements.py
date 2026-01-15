import streamlit as st
import pandas as pd
import pydeck as pdk

def render_header():
    st.markdown("""
        <h1 style='text-align: center; color: #007BFF;'>🏊 Pool Finder AI</h1>
        <p style='text-align: center; color: #666;'>Detect swimming pools from satellite imagery using Gemini 2.0 Flash</p>
        <hr>
    """, unsafe_allow_html=True)

def render_sidebar_info():
    with st.sidebar:
        st.header("Settings")
        google_maps_key = st.text_input("Google Maps API Key", type="password")
        google_ai_key = st.text_input("Google AI API Key", type="password")
        
        st.divider()
        
        radius = st.slider("Radius (meters)", min_value=50, max_value=500, value=200, step=50)
        
        st.divider()
        
        if 'usage' in st.session_state:
            st.header("Session Usage")
            u = st.session_state.usage
            st.metric("Total Cost", f"${u['total_cost']:.4f}")
            st.write(f"Input Tokens: {u['input_tokens']:,}")
            st.write(f"Output Tokens: {u['output_tokens']:,}")
            
        return google_maps_key, google_ai_key, radius

def display_results(pools, center_lat=None, center_lng=None):
    if not pools:
        st.info("No pools detected in this area.")
        return
        
    st.success(f"Detected {len(pools)} pools!")
    
    # Prepare data for map (explicitly dropping non-serializable image data for Pydeck)
    df = pd.DataFrame(pools)
    
    # Standardize column names
    rename_cols = {}
    if 'lat' in df.columns: rename_cols['lat'] = 'latitude'
    if 'lng' in df.columns: rename_cols['lng'] = 'longitude'
    if rename_cols:
        df = df.rename(columns=rename_cols)
    
    # Drop PIL images which cause Pydeck serialization errors
    map_df = df[['latitude', 'longitude']].copy()
    
    # Create Pydeck view
    view_state = pdk.ViewState(
        latitude=center_lat if center_lat else map_df['latitude'].mean(),
        longitude=center_lng if center_lng else map_df['longitude'].mean(),
        zoom=17,
        pitch=0,
    )

    # Define the layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_df,
        get_position=["longitude", "latitude"],
        get_color="[255, 0, 0, 160]", # Red with some transparency
        get_radius=4, # 4 meters radius
        pickable=True,
    )

    # Render the deck
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Pool detected at: {latitude}, {longitude}"}
    ))
    
    with st.expander("Detected Pools Table"):
        st.dataframe(df)
