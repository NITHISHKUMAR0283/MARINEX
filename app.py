import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from groq import Groq
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import numpy as np
import streamlit.components.v1 as components
import logging
from psycopg2.pool import SimpleConnectionPool
from functools import lru_cache
import time
import html
from st_aggrid import AgGrid, GridOptionsBuilder

# Set page configuration
st.set_page_config(
    page_title="Marinex - ARGO Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced CSS with the original styling plus improvements
st.markdown("""
<style>
    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stActionButton {display: none;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    .stAppViewContainer > .main > div {padding-top: 1rem;}
    
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles matching the original HTML */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #ff8c42, #ff6b35);
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
        margin: 0;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.8rem;
        color: white;
        border: 1px solid #404040;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 140, 66, 0.2);
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #ff8c42;
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .metric-description {
        font-size: 0.875rem;
        color: #888;
        margin: 0;
    }
    
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .cesium-container {
        height: 600px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border: 1px solid #404040;
        background: #1a1a1a;
    }
    
    .chat-interface {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        border: 1px solid #404040;
        color: white;
    }
    
    .query-input {
        background: #3a3a3a;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 1rem;
        color: white;
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .query-button {
        background: linear-gradient(135deg, #ff8c42, #ff6b35);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .query-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.3);
    }
    
    .sample-queries {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .sample-query {
        background: #3a3a3a;
        padding: 0.75rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        color: #f5f5f5;
        text-align: center;
        border: 1px solid #404040;
    }
    
    .sample-query:hover {
        background: #4a4a4a;
        color: #ff8c42;
        border-color: #ff8c42;
    }
    
    .data-panel {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        border: 1px solid #404040;
        margin: 1rem 0;
    }
    
    .panel-title {
        color: #ff8c42;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #404040;
        padding-bottom: 0.5rem;
    }
    
    .stTab {
        background: #2d2d2d;
        color: white;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #2d2d2d;
        border-bottom: 1px solid #404040;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2d2d2d;
        color: #888;
        border-color: #404040;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3a3a3a;
        color: #ff8c42;
        border-color: #ff8c42;
    }
    
    .stDataFrame {
        background: #2d2d2d;
        border-radius: 8px;
    }
    
    .nasa-panel {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
    }
    
    .api-status {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-active {
        background: #10b981;
        color: white;
    }
    
    .status-inactive {
        background: #f59e0b;
        color: white;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
        .cesium-container {
            height: 400px;
        }
        .chat-interface {
            width: 90%;
            right: 5%;
        }
        .main-header {
            padding: 1.5rem;
        }
        .header-title {
            font-size: 2rem;
        }
    }
    
    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #2d2d2d;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #404040;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Focus indicators for accessibility */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 2px solid #ff8c42;
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the Groq client
@st.cache_resource
def init_groq_client():
    return Groq(api_key="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")

# Database connection pool
@st.cache_resource
def init_db_pool():
    try:
        return SimpleConnectionPool(
            1, 10,
            "postgresql://neondb_owner:npg_qV9a3dQRAeBm@ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
    except Exception as e:
        logger.error(f"Database connection pool failed: {e}")
        st.warning(f"Database connection pool failed: {e}. Using sample data.")
        return None

# Sample ARGO float data (enhanced from the original HTML)
@st.cache_data
def get_sample_argo_data():
    np.random.seed(42)
    
    # Indian Ocean focused data
    indian_ocean_floats = [
        {'id': '2902755', 'lat': 15.234, 'lon': 68.456, 'temp': 28.5, 'salinity': 35.2, 'depth': 1847, 'status': 'Active'},
        {'id': '2902756', 'lat': 12.891, 'lon': 72.123, 'temp': 29.1, 'salinity': 34.8, 'depth': 1923, 'status': 'Active'},
        {'id': '2902757', 'lat': 8.567, 'lon': 76.789, 'temp': 30.2, 'salinity': 34.5, 'depth': 1756, 'status': 'Active'},
        {'id': '2902758', 'lat': 18.234, 'lon': 84.567, 'temp': 27.8, 'salinity': 35.6, 'depth': 1998, 'status': 'Active'},
        {'id': '2902759', 'lat': 5.789, 'lon': 80.123, 'temp': 31.1, 'salinity': 34.2, 'depth': 1678, 'status': 'Active'},
        {'id': '2902760', 'lat': 22.456, 'lon': 88.789, 'temp': 26.5, 'salinity': 35.8, 'depth': 2034, 'status': 'Active'},
        {'id': '2902761', 'lat': 13.678, 'lon': 65.234, 'temp': 28.9, 'salinity': 35.1, 'depth': 1845, 'status': 'Active'},
        {'id': '2902762', 'lat': 9.345, 'lon': 79.567, 'temp': 29.8, 'salinity': 34.6, 'depth': 1712, 'status': 'Active'},
    ]
    
    # Create expanded dataset
    all_floats = []
    base_time = datetime.now()
    
    for i, float_data in enumerate(indian_ocean_floats):
        for cycle in range(1, 51):  # 50 cycles per float
            measurement_time = base_time - timedelta(days=np.random.randint(0, 365))
            
            all_floats.append({
                'platform_number': float_data['id'],
                'cycle_number': cycle,
                'measurement_time': measurement_time,
                'latitude': float_data['lat'] + np.random.normal(0, 0.1),
                'longitude': float_data['lon'] + np.random.normal(0, 0.1),
                'pressure': np.random.uniform(0, float_data['depth']),
                'temperature': float_data['temp'] + np.random.normal(0, 2),
                'salinity': float_data['salinity'] + np.random.normal(0, 0.5),
                'region': 'Indian Ocean'
            })
    
    return pd.DataFrame(all_floats)

# Database connection function with connection pool
def get_db_connection():
    pool = init_db_pool()
    if pool is None:
        return None
    
    try:
        conn = pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"Failed to get connection from pool: {e}")
        st.warning(f"Database connection failed: {e}. Using sample data.")
        return None

# Enhanced Cesium component with proper configuration
def create_enhanced_cesium_map():
    """Create Cesium map with all ARGO float locations from database"""
    # Get all float locations
    float_locations = get_all_float_locations()
    
    # Prepare data for Cesium
    float_data_for_cesium = []
    
    for _, row in float_locations.iterrows():
        float_data_for_cesium.append({
            'id': row['platform_number'],
            'lat': row['latitude'],
            'lon': row['longitude'],
            'temp': round(row['temperature'], 1) if pd.notna(row['temperature']) else 'N/A',
            'salinity': round(row['salinity'], 1) if pd.notna(row['salinity']) else 'N/A'
        })
    
    cesium_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Cesium.js"></script>
        <link href="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
        <style>
            html, body, #cesiumContainer {{
                width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden;
                font-family: 'Inter', sans-serif;
                background: #1a1a1a;
            }}
            .cesium-widget-credits {{ display: none !important; }}
            .cesium-infoBox-description {{
                font-family: 'Inter', sans-serif;
            }}
        </style>
    </head>
    <body>
        <div id="cesiumContainer"></div>
        
        <script>
            // Set your Cesium Ion token
            Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3YTEzNTA0Yy0zYTQ5LTRiNDktYjNlOC03Y2ZkMTVkZDYyZjgiLCJpZCI6MzM2ODU4LCJpYXQiOjE3NTY2MTYxMjZ9.0vZQSC8KBvZBEHEleN_4V7T4CMYcyRQz4M5dZm4bARo';
            
            // Initialize with simpler configuration
            const viewer = new Cesium.Viewer('cesiumContainer', {{
                terrainProvider: Cesium.createWorldTerrain(),
                baseLayerPicker: false,
                geocoder: false,
                homeButton: false,
                sceneModePicker: false,
                navigationHelpButton: false,
                animation: false,
                timeline: false,
                fullscreenButton: false,
                infoBox: false,
                selectionIndicator: false
            }});
            
            // Set initial view to show all floats
            viewer.camera.setView({{
                destination: Cesium.Cartesian3.fromDegrees(75.0, 15.0, 8000000.0),
                orientation: {{
                    heading: 0,
                    pitch: -1.57,
                    roll: 0
                }}
            }});
            
            // Float data from Python
            const floatData = {json.dumps(float_data_for_cesium)};
            
            // Batch create entities for better performance
            const dataSource = new Cesium.CustomDataSource('floats');
            viewer.dataSources.add(dataSource);
            
            floatData.forEach(floatItem => {{
                const position = Cesium.Cartesian3.fromDegrees(floatItem.lon, floatItem.lat);
                
                const entity = dataSource.entities.add({{
                    position: position,
                    point: {{
                        pixelSize: 10,
                        color: Cesium.Color.fromCssColorString('#ff8c42'),
                        outlineColor: Cesium.Color.WHITE,
                        outlineWidth: 2,
                        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                    }},
                    label: {{
                        text: floatItem.id,
                        font: '12pt Inter, sans-serif',
                        pixelOffset: new Cesium.Cartesian2(0, -20),
                        fillColor: Cesium.Color.WHITE,
                        outlineColor: Cesium.Color.BLACK,
                        outlineWidth: 2,
                        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                        // Show labels only when zoomed in (distance less than 500,000 meters)
                        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 500000.0),
                        // Enable scaling with distance
                        scale: 0.5,
                        // Make labels transparent when far away
                        translucencyByDistance: new Cesium.NearFarScalar(100000, 1.0, 500000, 0.2)
                    }},
                    description: `
                        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                            <b>Float ${{floatItem.id}}</b><br>
                            <hr style="margin: 5px 0;">
                            <b>Temperature:</b> ${{floatItem.temp}}°C<br>
                            <b>Salinity:</b> ${{floatItem.salinity}} PSU<br>
                            <b>Position:</b> ${{floatItem.lat.toFixed(3)}}, ${{floatItem.lon.toFixed(3)}}
                        </div>
                    `
                }});
            }});
            
            // Add click event to zoom to float
            viewer.selectedEntityChanged.addEventListener(function(entity) {{
                if (Cesium.defined(entity)) {{
                    viewer.trackedEntity = entity;
                    
                    // Fly to the selected entity with a smooth animation
                    viewer.camera.flyTo({{
                        destination: entity.position.getValue(viewer.clock.currentTime),
                        duration: 1.0,
                        offset: {{
                            heading: 0,
                            pitch: -1.0,
                            range: 100000.0
                        }}
                    }});
                }}
            }});
            
            // Add event listener for camera changes to dynamically adjust label visibility
            viewer.camera.moveEnd.addEventListener(function() {{
                const cameraHeight = viewer.camera.positionCartographic.height;
                
                // Adjust label visibility based on camera height
                dataSource.entities.values.forEach(function(entity) {{
                    if (entity.label) {{
                        // Show labels when zoomed in (camera height less than 1,000,000 meters)
                        const showLabels = cameraHeight < 1000000;
                        entity.label.show = showLabels;
                        
                        // Adjust label scale based on zoom level
                        if (showLabels) {{
                            const scale = Math.max(0.3, Math.min(1.0, 1000000 / cameraHeight));
                            entity.label.scale = scale;
                        }}
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return cesium_html















# System prompt for LLM (from the original code)
system_prompt = """
You are FloatChat, an AI assistant for querying an ARGO ocean database. Your purpose is to translate natural language queries into precise PostgreSQL queries.

Database Schema for table 'argo_floats':
- platform_number (TEXT): The unique ID of the float (e.g., '2902743')
- cycle_number (INTEGER): The profile number from the float
- measurement_time (TIMESTAMP): UTC time of the observation. Use for all time filters
- latitude (FLOAT), longitude (FLOAT): Use for all location filters
- pressure (FLOAT): Depth in decibars (~meters). Lower values are shallower
- temperature (FLOAT): in °C
- salinity (FLOAT): Practical Salinity Units (PSU)
- region (TEXT): Pre-set region like 'Indian Ocean'

IMPORTANT LOCATIONS (latitude, longitude):
- Chennai, India: (13.0825, 80.2707)
- Mumbai, India: (19.0760, 72.8777)
- Kochi, India: (9.9312, 76.2673)
- Andaman Islands: (11.7401, 92.6586)
- Lakshadweep Islands: (10.5667, 72.6417)

RULES:
1. Your output MUST be structured as:
   <response>[Natural language explanation of the query]</response>
   <sql>[Valid PostgreSQL SELECT query]</sql>

2. For ALL queries:
   - Include a LIMIT clause (default LIMIT 100 unless user specifies "all" or similar)
   - Use appropriate WHERE clauses for filtering
   - Select only necessary columns (use * only when specifically requested)

Now, generate the appropriate response and SQL query for the following request:
"""
def get_all_float_locations():
    """Fetch all float locations from the database"""
    conn = get_db_connection()
    if conn is None:
        # Return sample data if DB connection fails
        sample_data = get_sample_argo_data()
        latest_positions = sample_data.groupby('platform_number').last().reset_index()
        return latest_positions[['platform_number', 'latitude', 'longitude', 'temperature', 'salinity']]
    
    try:
        # Query to get the latest position for each float
        query = """
        SELECT DISTINCT ON (platform_number) 
            platform_number, latitude, longitude, temperature, salinity
        FROM argo_floats 
        ORDER BY platform_number, measurement_time DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error(f"Error fetching float locations: {e}")
        st.error(f"Error fetching float locations: {e}")
        # Return sample data as fallback
        sample_data = get_sample_argo_data()
        latest_positions = sample_data.groupby('platform_number').last().reset_index()
        return latest_positions[['platform_number', 'latitude', 'longitude', 'temperature', 'salinity']]
    finally:
        # Return connection to pool
        pool = init_db_pool()
        if pool and conn:
            pool.putconn(conn)
def extract_sql(response):
    sql_match = re.search(r'<sql>(.*?)</sql>', response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    return None

# Input sanitization function
def sanitize_input(user_input):
    return html.escape(user_input.strip())

# Enhanced execute_sql_query with better error handling
def execute_sql_query(sql_query):
    conn = get_db_connection()
    if conn is None:
        # Use sample data and simulate query execution
        df = get_sample_argo_data()
        try:
            # Simple query simulation for common patterns
            if "temperature" in sql_query.lower() and ">" in sql_query:
                temp_threshold = float(re.findall(r'temperature\s*>\s*(\d+(?:\.\d+)?)', sql_query.lower())[0])
                df = df[df['temperature'] > temp_threshold]
            elif "salinity" in sql_query.lower() and ">" in sql_query:
                sal_threshold = float(re.findall(r'salinity\s*>\s*(\d+(?:\.\d+)?)', sql_query.lower())[0])
                df = df[df['salinity'] > sal_threshold]
            elif "recent" in sql_query.lower() or "last" in sql_query.lower():
                df = df[df['measurement_time'] > (datetime.now() - timedelta(days=7))]
            
            return df.head(100)
        except Exception as e:
            logger.error(f"Error simulating query: {e}")
            return df.head(100)
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        # Return connection to pool
        pool = init_db_pool()
        if pool:
            pool.putconn(conn)
        return df
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        st.error(f"Error executing SQL query: {e}")
        # Provide helpful suggestions based on error type
        if "syntax" in str(e).lower():
            st.info("Try simplifying your query or check for syntax errors")
        
        # Return connection to pool in case of error
        pool = init_db_pool()
        if pool:
            pool.putconn(conn)
        return get_sample_argo_data().head(100)

# Cached and rate-limited version of process_user_query
@lru_cache(maxsize=100)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def process_user_query_cached(user_query):
    # Add a small delay to prevent rate limiting
    time.sleep(0.5)
    return process_user_query(user_query)

def process_user_query(user_query):
    try:
        groq_client = init_groq_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        with st.spinner("Generating SQL query..."):
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
        
        llm_response = completion.choices[0].message.content
        sql_query = extract_sql(llm_response)
        
        if not sql_query:
            st.error("Could not generate a valid SQL query for your request.")
            return None, None, None
        
        with st.spinner("Executing query..."):
            df = execute_sql_query(sql_query)
        
        if df is None or df.empty:
            st.warning("No data found for your query.")
            return None, None, None
        
        response_match = re.search(r'<response>(.*?)</response>', llm_response, re.DOTALL)
        natural_response = response_match.group(1).strip() if response_match else "Here are the results:"
        
        return natural_response, df, sql_query
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        st.error(f"Error processing request: {str(e)}")
        return None, None, None

# NASA PODAAC API Integration
def get_nasa_datasets():
    """Fetch available NASA PODAAC datasets"""
    try:
        url = "https://cmr.earthdata.nasa.gov/search/collections.json"
        params = {
            'provider': 'PODAAC',
            'has_granules': 'true',
            'page_size': 10,
            'sort_key': 'start_date'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('feed', {}).get('entry', [])
    except Exception as e:
        logger.error(f"Error fetching NASA datasets: {e}")
        st.error(f"Error fetching NASA datasets: {e}")
    return []

def search_satellite_data(dataset_id, bbox=None, temporal=None):
    """Search for satellite data granules"""
    try:
        url = "https://cmr.earthdata.nasa.gov/search/granules.json"
        params = {
            'collection_concept_id': dataset_id,
            'page_size': 20
        }
        
        if bbox:
            params['bounding_box'] = f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}"
        
        if temporal:
            params['temporal'] = f"{temporal['start']},{temporal['end']}"
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('feed', {}).get('entry', [])
    except Exception as e:
        logger.error(f"Error searching satellite data: {e}")
        st.error(f"Error searching satellite data: {e}")
    return []

def create_correlation_analysis(argo_data, satellite_data=None):
    """Create correlation analysis between ARGO and satellite data"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature vs Salinity', 'Temperature vs Depth', 
                       'Temporal Temperature Trends', 'Geographic Distribution'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "mapbox"}]]
    )
    
    # Temperature vs Salinity scatter
    fig.add_trace(
        go.Scatter(x=argo_data['temperature'], y=argo_data['salinity'],
                  mode='markers', name='ARGO Data',
                  marker=dict(color='#ff8c42', size=6)),
        row=1, col=1
    )
    
    # Temperature vs Depth
    fig.add_trace(
        
        go.Scatter(x=argo_data['temperature'], y=argo_data['pressure'],
                  mode='markers', name='Temp vs Depth',
                  marker=dict(color='#ff6b35', size=6)),
        row=1, col=2
    )
    
    # Temporal trends
    if 'measurement_time' in argo_data.columns:
        daily_temp = argo_data.groupby(argo_data['measurement_time'].dt.date)['temperature'].mean()
        fig.add_trace(
            go.Scatter(x=daily_temp.index, y=daily_temp.values,
                      mode='lines+markers', name='Daily Avg Temp',
                      line=dict(color='#10b981')),
            row=2, col=1
        )
    
    # Geographic distribution
    if 'latitude' in argo_data.columns and 'longitude' in argo_data.columns:
        fig.add_trace(
            go.Scattermapbox(
                lat=argo_data['latitude'], lon=argo_data['longitude'],
                mode='markers', name='Float Locations',
                marker=dict(size=8, color=argo_data['temperature'],
                           colorscale='RdYlBu_r', showscale=True)),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        title_text="ARGO Data Analysis Dashboard",
        showlegend=True,
        mapbox=dict(style="carto-darkmatter", center=dict(lat=10, lon=75), zoom=3),
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    return fig

def create_temperature_depth_profile(df):
    """Create temperature-depth profile visualization"""
    if 'temperature' not in df.columns or 'pressure' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # Group by platform for different profiles
    for platform in df['platform_number'].unique()[:5]:  # Show top 5 platforms
        platform_data = df[df['platform_number'] == platform]
        fig.add_trace(go.Scatter(
            x=platform_data['temperature'],
            y=platform_data['pressure'],
            mode='lines+markers',
            name=f'Float {platform}',
            line=dict(width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Temperature-Depth Profiles",
        xaxis_title="Temperature (°C)",
        yaxis_title="Pressure (dbar)",
        yaxis=dict(autorange='reversed'),  # Depth increases downward
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_geographic_heatmap(df):
    """Create geographic heatmap of measurements"""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None
    
    # Use the new mapbox_style parameter with MapLibre styles
    fig = px.density_mapbox(
        df, lat='latitude', lon='longitude',
        z='temperature' if 'temperature' in df.columns else None,
        radius=20,
        center=dict(lat=df['latitude'].mean(), lon=df['longitude'].mean()),
        zoom=3,
        mapbox_style="carto-darkmatter",  # This should work with the new MapLibre backend
        color_continuous_scale="RdYlBu_r",
        title="Geographic Distribution of Measurements"
    )
    
    fig.update_layout(
        paper_bgcolor='#2d2d2d',
        font=dict(color='white'),
        height=500
    )
    
    return fig

# Tooltip component for better UX
def tooltip(text, help_text):
    st.markdown(f"""
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{help_text}</span>
    </div>
    """, unsafe_allow_html=True)

# Main function with all enhancements
def main():
    # Initialize session state
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'chat_minimized' not in st.session_state:
        st.session_state.chat_minimized = False
    
    if 'realtime_updates' not in st.session_state:
        st.session_state.realtime_updates = False
    
    # Header (matching original design)
    st.markdown("""
    <div class="main-header">
        <h1 class="header-title">Marinex</h1>
        <p class="header-subtitle">AI-Powered ARGO Float Discovery & Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get sample data for display
    sample_data = get_sample_argo_data()
    
    # Statistics grid (matching original style)
    unique_floats = sample_data['platform_number'].nunique()
    total_records = len(sample_data)
    recent_data = len(sample_data[sample_data['measurement_time'] > (datetime.now() - timedelta(days=1))])
    avg_temp = sample_data['temperature'].mean()
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-label">Active Floats</div>
            <div class="metric-value">{unique_floats}</div>
            <div class="metric-description">Currently deployed platforms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total_records:,}</div>
            <div class="metric-description">Oceanographic measurements</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Recent Data</div>
            <div class="metric-value"><span class="live-indicator"></span>{recent_data}</div>
            <div class="metric-description">Last 24 hours</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Temperature</div>
            <div class="metric-value">{avg_temp:.1f}°C</div>
            <div class="metric-description">Current ocean conditions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time updates toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Enable Real-time Updates" if not st.session_state.realtime_updates else "⏹️ Disable Real-time Updates"):
            st.session_state.realtime_updates = not st.session_state.realtime_updates
            st.rerun()
    
    # Enhanced 3D Globe Visualization
    st.markdown('<div class="panel-title">🌍 Global ARGO Float Network - 3D Visualization</div>', unsafe_allow_html=True)
    # Prepare data for Cesium (using latest position for each float)
    latest_positions = sample_data.groupby('platform_number').last().reset_index()
    float_data_for_cesium = []
    
    for _, row in latest_positions.iterrows():
        float_data_for_cesium.append({
            'id': row['platform_number'],
            'lat': row['latitude'],
            'lon': row['longitude'],
            'temp': round(row['temperature'], 1),
            'salinity': round(row['salinity'], 1),
            'depth': 2000,  # Approximate max depth
            'status': 'Active'
        })
    
    # Create and display Cesium map
    cesium_html = create_enhanced_cesium_map()
    components.html(cesium_html, height=600)
    
    # AI Chat Interface
 
    
    # Query input with tooltip
    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input(
            "Ask about ARGO floats, oceanographic data, or specific analyses:",
            placeholder="e.g., Show temperature profiles near Chennai",
            key="main_query"
        )
    
    with col2:
        execute_query = st.button("🔍 Execute", key="execute_main", help="Execute your query")
        tooltip("💡", "Ask natural language questions about ARGO float data")
    
    # Sample queries (matching original design)
    st.markdown("**Sample Queries:**")
    
    sample_queries = [
        "Show floats near Arabian Sea",
        "Temperature above 28°C", 
        "Salinity profiles in Indian Ocean",
        "Recent measurements from last week"
    ]
    
    query_cols = st.columns(len(sample_queries))
    selected_sample = None
    
    for i, query in enumerate(sample_queries):
        with query_cols[i]:
            if st.button(query, key=f"sample_{i}"):
                selected_sample = query
    
    # Process selected sample query
    if selected_sample:
        user_query = selected_sample
        execute_query = True
    
    # Process query if submitted
    if execute_query and user_query:
        # Sanitize input
        user_query = sanitize_input(user_query)
        
        # Add to query history
        st.session_state.query_history.append({
            'query': user_query,
            'timestamp': datetime.now()
        })
        
        # Process query with caching
        natural_response, df, sql_query = process_user_query_cached(user_query)
        
        if df is not None:
            # Display results
            st.markdown(f"""
            <div class="data-panel">
                <div class="panel-title"> Query Results</div>
                <p style=" margin-bottom: 1rem;">{natural_response}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Results tabs
            tab1, tab2, tab3, tab4 = st.tabs([" Data Table", "🗺️ Geographic View", "📈 Analysis", "🔬 Advanced"])
            
            with tab1:
               
                # Show SQL query
                if sql_query:
                    with st.expander("View Generated SQL Query"):
                        st.code(sql_query, language="sql")
                
                # Data summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Records Found", len(df))
                with col2:
                    if 'temperature' in df.columns:
                        st.metric("Avg Temperature", f"{df['temperature'].mean():.1f}°C")
                with col3:
                    if 'platform_number' in df.columns:
                        st.metric("Unique Floats", df['platform_number'].nunique())
                
                # Data table with pagination
                st.subheader("Data Results")
                display_dataframe_with_pagination(df)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"argo_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    # Create Folium map for query results
                    center_lat = df['latitude'].mean()
                    center_lon = df['longitude'].mean()
                    
                    m = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=5,
                        tiles='CartoDB dark_matter'
                    )
                    
                    # Add markers with color coding based on temperature
                    for _, row in df.iterrows():
                        # Color based on temperature if available
                        if 'temperature' in df.columns:
                            temp = row['temperature']
                            if temp > 30:
                                color = 'red'
                            elif temp > 28:
                                color = 'orange'
                            elif temp > 26:
                                color = 'yellow'
                            elif temp > 24:
                                color = 'lightgreen'
                            else:
                                color = 'lightblue'
                        else:
                            color = 'blue'
                        
                        popup_text = f"""
                        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                            <b>Float {row.get('platform_number', 'N/A')}</b><br>
                            <hr style="margin: 5px 0;">
                            <b>Temperature:</b> {row.get('temperature', 'N/A')}°C<br>
                            <b>Salinity:</b> {row.get('salinity', 'N/A')} PSU<br>
                            <b>Pressure:</b> {row.get('pressure', 'N/A')} dbar<br>
                            <b>Time:</b> {row.get('measurement_time', 'N/A')}
                        </div>
                        """
                        
                        folium.CircleMarker(
                            [row['latitude'], row['longitude']],
                            radius=8,
                            color='white',
                            fillColor=color,
                            fillOpacity=0.8,
                            weight=2,
                            popup=folium.Popup(popup_text, max_width=300)
                        ).add_to(m)
                    
                    # Display map
                    folium_static(m, width=None, height=500)
                    
                    # Geographic heatmap
                    if len(df) > 10:
                        st.subheader("Data Density Heatmap")
                        heatmap_fig = create_geographic_heatmap(df)
                        if heatmap_fig:
                            st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    st.info("Geographic coordinates not available for mapping.")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                
                # Create analysis visualizations
                if len(df) > 0:
                    # Temperature-Depth Profile
                    if 'temperature' in df.columns and 'pressure' in df.columns:
                        st.subheader("Temperature-Depth Profiles")
                        profile_fig = create_temperature_depth_profile(df)
                        if profile_fig:
                            st.plotly_chart(profile_fig, use_container_width=True)
                    
                    # Statistical summary
                    st.subheader("Statistical Summary")
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        stats_df = df[numeric_cols].describe()
                        st.dataframe(stats_df, use_container_width=True)
                    
                    # Correlation analysis
                    if len(numeric_cols) > 1:
                        st.subheader("Correlation Analysis")
                        correlation_fig = create_correlation_analysis(df)
                        st.plotly_chart(correlation_fig, use_container_width=True)
                    
                    # Time series analysis if temporal data exists
                    if 'measurement_time' in df.columns:
                        st.subheader("Temporal Analysis")
                        
                        # Daily averages
                        if 'temperature' in df.columns:
                            daily_data = df.groupby(df['measurement_time'].dt.date).agg({
                                'temperature': 'mean',
                                'salinity': 'mean' if 'salinity' in df.columns else lambda x: None
                            }).reset_index()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=daily_data['measurement_time'],
                                y=daily_data['temperature'],
                                mode='lines+markers',
                                name='Temperature',
                                line=dict(color='#ff8c42')
                            ))
                            
                            fig.update_layout(
                                title="Daily Temperature Trends",
                                xaxis_title="Date",
                                yaxis_title="Temperature (°C)",
                                paper_bgcolor='#2d2d2d',
                                plot_bgcolor='#2d2d2d',
                                font=dict(color='white'),
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab4:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                st.subheader("Advanced Analysis & NASA Integration")
                
                # NASA PODAAC Integration
                st.markdown("""
                <div class="nasa-panel">
                    <h3>🛰️ NASA PODAAC Satellite Data Integration</h3>
                    <p>Correlate ARGO float measurements with satellite observations for comprehensive ocean analysis.</p>
                </div>
                """, unsafe_allow_html=True)
                
                nasa_col1, nasa_col2 = st.columns(2)
                
                with nasa_col1:
                    if st.button("🔍 Browse NASA Datasets", key="browse_nasa"):
                        with st.spinner("Fetching NASA datasets..."):
                            datasets = get_nasa_datasets()
                            if datasets:
                                st.success(f"Found {len(datasets)} datasets")
                                for i, dataset in enumerate(datasets[:5]):
                                    with st.expander(f"Dataset {i+1}: {dataset.get('title', 'Unknown')}"):
                                        st.write(f"**Provider:** {dataset.get('data_center', 'N/A')}")
                                        st.write(f"**Summary:** {dataset.get('summary', 'No description available')[:200]}...")
                                        if 'id' in dataset:
                                            st.code(dataset['id'])
                            else:
                                st.warning("No datasets found or API unavailable")
                
                with nasa_col2:
                    st.info("""
                    **Available NASA Data Types:**
                    - Sea Surface Temperature (SST)
                    - Sea Surface Height (SSH) 
                    - Ocean Color (Chlorophyll)
                    - Sea Surface Salinity (SSS)
                    - Ocean Wind Speed
                    """)
                
                # Advanced analytics options
                st.subheader("Advanced Analytics Options")
                
                analysis_options = st.multiselect(
                    "Select analysis types:",
                    ["Machine Learning Clustering", "Anomaly Detection", "Predictive Modeling", 
                     "Spectral Analysis", "Cross-correlation with Satellite Data"],
                    default=[]
                )
                
                if "Machine Learning Clustering" in analysis_options:
                    if len(df) > 20 and 'temperature' in df.columns and 'salinity' in df.columns:
                        from sklearn.cluster import KMeans
                        from sklearn.preprocessing import StandardScaler
                        
                        # Prepare data for clustering
                        features = df[['temperature', 'salinity']].dropna()
                        scaler = StandardScaler()
                        features_scaled = scaler.fit_transform(features)
                        
                        # K-means clustering
                        n_clusters = st.slider("Number of clusters:", 2, 8, 3)
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(features_scaled)
                        
                        # Visualization
                        fig = px.scatter(
                            features, x='temperature', y='salinity', 
                            color=clusters, title="Water Mass Clustering Analysis",
                            color_continuous_scale='viridis'
                        )
                        fig.update_layout(
                            paper_bgcolor='#2d2d2d',
                            plot_bgcolor='#2d2d2d',
                            font=dict(color='white')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                if "Anomaly Detection" in analysis_options:
                    if 'temperature' in df.columns:
                        # Simple anomaly detection using IQR
                        Q1 = df['temperature'].quantile(0.25)
                        Q3 = df['temperature'].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        anomalies = df[(df['temperature'] < lower_bound) | (df['temperature'] > upper_bound)]
                        
                        if len(anomalies) > 0:
                            st.warning(f"🚨 Found {len(anomalies)} temperature anomalies")
                            st.dataframe(anomalies[['platform_number', 'temperature', 'measurement_time']], use_container_width=True)
                        else:
                            st.success("✅ No significant temperature anomalies detected")
                
                # Export options
                st.subheader("Export & Integration")
                export_col1, export_col2, export_col3 = st.columns(3)
                
                with export_col1:
                    if st.button("📊 Export to NetCDF"):
                        st.info("NetCDF export functionality would be implemented here")
                
                with export_col2:
                    if st.button("🔗 Generate API Endpoint"):
                        st.info("API endpoint generation would be implemented here")
                
                with export_col3:
                    if st.button("📧 Schedule Report"):
                        st.info("Report scheduling functionality would be implemented here")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Query History Sidebar
    with st.sidebar:
        st.markdown("### 📋 Query History")
        if st.session_state.query_history:
            for i, query_item in enumerate(reversed(st.session_state.query_history[-10:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Query:** {query_item['query']}")
                    st.write(f"**Time:** {query_item['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                    if st.button("🔄 Run Again", key=f"rerun_{i}"):
                        st.session_state.main_query = query_item['query']
                        st.rerun()
        else:
            st.info("No queries yet. Try asking something above!")
        
        # API Status
        st.markdown("### 🔌 System Status")
        
        # Database status
        pool = init_db_pool()
        if pool:
            db_status = "🟢 Connected"
        else:
            db_status = "🟡 Sample Data"
        
        st.markdown(f"**Database:** {db_status}")
        st.markdown("**AI Model:** 🟢 Online")
        st.markdown("**NASA API:** 🟢 Available")
        st.markdown("**Cesium Maps:** 🟢 Active")
        
        # Help section
        st.markdown("### ❓ Help & Tips")
        with st.expander("How to use this platform"):
            st.write("""
            1. **Ask questions** in natural language about ARGO float data
            2. **Explore results** through interactive visualizations
            3. **Download data** for further analysis
            4. **Use sample queries** to get started quickly
            """)
        
        with st.expander("Sample query examples"):
            st.write("""
            - "Show floats near Chennai"
            - "Temperature above 28°C"
            - "Salinity profiles from last month"
            - "Deepest measurements in Indian Ocean"
            """)

# Function to display dataframe with pagination
def display_dataframe_with_pagination(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
    gridOptions = gb.build()
    
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, height=400)

if __name__ == "__main__":
    main()
