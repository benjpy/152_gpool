# 🏊 Pool Finder AI

Detect swimming pools from Google Maps satellite view using Gemini 2.0 Flash.

## 🚀 Features
- **Geocoding**: Search for any address or city.
- **Satellite Tiling**: Automatically fetches enough satellite tiles to cover the requested radius.
- **AI Detection**: Uses Gemini 2.0 Flash to visually identify outdoor pools.
- **Interactive Map**: Displays detected pools on an interactive map.
- **Cost Tracking**: Monitored API costs for Gemini usage.

## 🛠️ Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API Keys**:
   Create a `.env` file or enter them in the app sidebar:
   ```env
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   GEMINI_API_KEY=your_gemini_key
   ```
   *Note: Ensure Google Maps Static API and Geocoding API are enabled.*

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 🏗️ Architecture
- `app.py`: Main entry point and orchestration.
- `services/`: Core logic for Google Maps and Gemini Pool Detection.
- `ui/`: Streamlit UI components.
- `utils/`: Helpers for timing and token/cost tracking.
