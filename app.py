import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
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
import seaborn as sns
from geopy.distance import geodesic
from scipy import interpolate, stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
from dataclasses import dataclass
from typing import Dict, Any, Optional

warnings.filterwarnings('ignore')

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Enhanced main header with vibrant gradient */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #ffeaa7 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease-in-out infinite;
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 60px rgba(255, 107, 107, 0.3);
        position: relative;
        overflow: hidden;
        border: none;
        transform: perspective(1000px) rotateX(2deg);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.08' fill-rule='evenodd'/%3E%3C/svg%3E");
        animation: floatPattern 20s linear infinite;
    }
    
    @keyframes floatPattern {
        0% { transform: translateX(0) translateY(0); }
        25% { transform: translateX(-10px) translateY(-5px); }
        50% { transform: translateX(10px) translateY(-10px); }
        75% { transform: translateX(-5px) translateY(-5px); }
        100% { transform: translateX(0) translateY(0); }
    }
    
    .header-title {
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        0% { text-shadow: 0 4px 8px rgba(255,255,255,0.2); }
        100% { text-shadow: 0 4px 20px rgba(255,255,255,0.4); }
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        font-weight: 500;
        opacity: 0.95;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        animation: subtitleFloat 4s ease-in-out infinite;
    }
    
    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    /* Enhanced stats grid with rainbow accent */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        border: 2px solid transparent;
        background-clip: padding-box;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #fd79a8);
        background-size: 200% 100%;
        animation: rainbowSlide 3s linear infinite;
    }
    
    @keyframes rainbowSlide {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #fd79a8);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        opacity: 0;
        animation: gradientRotate 6s ease infinite;
        transition: opacity 0.4s ease;
    }
    
    @keyframes gradientRotate {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(255, 107, 107, 0.3);
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #bbb;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-label {
        color: #4ecdc4;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.8rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover .metric-value {
        transform: scale(1.05);
    }
    
    .metric-description {
        font-size: 1rem;
        color: #aaa;
        margin: 0;
        line-height: 1.6;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-description {
        color: #ddd;
    }
    
    /* Dynamic live indicator */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: radial-gradient(circle, #10b981, #059669);
        border-radius: 50%;
        margin-right: 10px;
        animation: livePulse 2s ease-in-out infinite;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.6);
        position: relative;
    }
    
    .live-indicator::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        background: radial-gradient(circle, transparent 40%, #10b981 80%);
        animation: livePulse 2s ease-in-out infinite 0.5s;
    }
    
    @keyframes livePulse {
        0% {
            transform: scale(0.8);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8);
        }
        50% {
            transform: scale(1.1);
            box-shadow: 0 0 0 15px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.8);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    /* Spectacular button enhancements */
    .query-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
        background-size: 200% 200%;
        border: none;
        border-radius: 16px;
        padding: 1.2rem 2.5rem;
        color: white;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        font-size: 1.1rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
        animation: buttonBreathe 3s ease-in-out infinite;
    }
    
    @keyframes buttonBreathe {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
        }
    }
    
    .query-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s ease;
    }
    
    .query-button:hover {
        transform: translateY(-6px) scale(1.05);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.6);
        background-position: 100% 50%;
    }
    
    .query-button:hover::before {
        left: 100%;
    }
    
    .query-button:active {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.5);
    }
    
    /* Enhanced Streamlit buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 14px;
        padding: 1rem 2rem;
        font-weight: 700;
        color: white;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.01);
    }
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Ocean animation background */
    body, .stApp {
        background: linear-gradient(180deg, #001122 0%, #003366 30%, #004080 60%, #0066cc 100%);
        position: relative;
        min-height: 100vh;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(0, 100, 200, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 30%, rgba(0, 150, 255, 0.2) 0%, transparent 60%),
            radial-gradient(ellipse at 40% 80%, rgba(100, 200, 255, 0.1) 0%, transparent 50%);
        animation: oceanCurrent 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -2;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 200%;
        background-image: 
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(255, 255, 255, 0.03) 2px,
                rgba(255, 255, 255, 0.03) 4px
            ),
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 2px,
                rgba(255, 255, 255, 0.02) 2px,
                rgba(255, 255, 255, 0.02) 4px
            );
        animation: oceanWaves 15s linear infinite;
        pointer-events: none;
        z-index: -1;
        transform: translateZ(0);
    }
    
    @keyframes oceanCurrent {
        0%, 100% { 
            transform: translateX(0) translateY(0) scale(1);
            filter: hue-rotate(0deg);
        }
        25% { 
            transform: translateX(-20px) translateY(-10px) scale(1.05);
            filter: hue-rotate(30deg);
        }
        50% { 
            transform: translateX(20px) translateY(-20px) scale(1.1);
            filter: hue-rotate(60deg);
        }
        75% { 
            transform: translateX(-10px) translateY(10px) scale(1.05);
            filter: hue-rotate(30deg);
        }
    }
    
    @keyframes oceanWaves {
        0% { transform: translateY(0) rotateZ(0deg); }
        100% { transform: translateY(-50px) rotateZ(1deg); }
    }
    
    /* Scroll-responsive ocean effect */
    .ocean-scroll-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
                rgba(0, 200, 255, 0.1) 0%, 
                transparent 50%),
            linear-gradient(45deg, 
                transparent 0%, 
                rgba(100, 200, 255, 0.05) 25%, 
                transparent 50%, 
                rgba(0, 150, 255, 0.05) 75%, 
                transparent 100%);
        background-size: 200px 200px, 400px 400px;
        animation: oceanFlow 25s linear infinite;
        pointer-events: none;
        z-index: -3;
        will-change: transform;
    }
    
    @keyframes oceanFlow {
        0% { 
            background-position: 0% 0%, 0% 0%;
            transform: translateY(0) scale(1);
        }
        25% { 
            background-position: 25% 25%, 100% 0%;
            transform: translateY(-10px) scale(1.02);
        }
        50% { 
            background-position: 50% 50%, 200% 100%;
            transform: translateY(-20px) scale(1.05);
        }
        75% { 
            background-position: 75% 25%, 100% 200%;
            transform: translateY(-10px) scale(1.02);
        }
        100% { 
            background-position: 100% 0%, 0% 300%;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Floating bubbles effect */
    .bubble-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 20% 80%, rgba(200, 255, 255, 0.08) 2px, transparent 2px),
            radial-gradient(circle at 80% 40%, rgba(150, 220, 255, 0.06) 1.5px, transparent 1.5px),
            radial-gradient(circle at 40% 60%, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 90% 10%, rgba(180, 240, 255, 0.07) 2px, transparent 2px);
        background-size: 300px 300px, 200px 200px, 400px 400px, 250px 250px, 350px 350px;
        animation: bubbleFloat 30s linear infinite;
        pointer-events: none;
        z-index: -4;
        opacity: 0.6;
    }
    
    @keyframes bubbleFloat {
        0% { 
            background-position: 0% 100%, 0% 0%, 0% 100%, 0% 0%, 0% 100%;
            transform: translateY(0);
        }
        100% { 
            background-position: 100% 0%, 100% 100%, 100% 0%, 100% 100%, 100% 0%;
            transform: translateY(-100px);
        }
    }
    
    .sample-query::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        opacity: 0;
        transition: opacity 0.4s ease;
        animation: gradientShift 4s ease infinite;
        z-index: -1;
    }
    
    .sample-query:hover {
        color: white;
        border-color: transparent;
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
    }
    
    .sample-query:hover::before {
        opacity: 0.9;
    }
    
    /* Enhanced download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        background-size: 200% 200%;
        border: none;
        border-radius: 14px;
        color: white;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        padding: 1rem 2rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        overflow: hidden;
        animation: downloadPulse 3s ease-in-out infinite;
    }
    
    @keyframes downloadPulse {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 6px 20px rgba(4, 120, 87, 0.4);
        }
    }
    
    .stDownloadButton > button::before {
        content: '⬇';
        position: absolute;
        top: 50%;
        left: 1rem;
        transform: translateY(-50%);
        font-size: 1.2rem;
        transition: transform 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.6);
        background-position: 100% 50%;
    }
    
    .stDownloadButton > button:hover::before {
        transform: translateY(-50%) translateX(2px);
        animation: downloadBounce 0.6s ease infinite;
    }
    
    @keyframes downloadBounce {
        0%, 100% { transform: translateY(-50%) translateX(2px); }
        50% { transform: translateY(-40%) translateX(2px); }
    }
    
    /* Enhanced metric cards with unique colors */
   
    
    /* Enhanced input fields */
    .query-input {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        border: 2px solid #555;
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        width: 100%;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: inset 0 4px 8px rgba(0,0,0,0.15);
        position: relative;
    }
    
    .query-input:focus {
        outline: none;
        border-color: #4ecdc4;
        box-shadow: 0 0 0 4px rgba(78, 205, 196, 0.25), inset 0 4px 8px rgba(0,0,0,0.15);
        transform: scale(1.02);
        background: linear-gradient(145deg, #404040, #353535);
    }
    
    /* Enhanced panels */
    .data-panel {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        border: 1px solid #404040;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .data-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 20%, rgba(255, 107, 107, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(78, 205, 196, 0.05) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .data-panel:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.2);
    }
    
    .panel-title {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 2rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #ff6b6b, #4ecdc4) 1;
        padding-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: titleShimmer 3s ease-in-out infinite;
    }
    
    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    /* Enhanced NASA panel */
    .nasa-panel {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 25%, #60a5fa 50%, #93c5fd 75%, #dbeafe 100%);
        background-size: 300% 300%;
        animation: nasaGradient 6s ease infinite;
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 45px rgba(59, 130, 246, 0.3);
        border: none;
        position: relative;
        overflow: hidden;
        transform: perspective(1000px) rotateX(1deg);
    }
    
    @keyframes nasaGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .nasa-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        animation: starTwinkle 4s linear infinite;
    }
    
    @keyframes starTwinkle {
        0%, 100% { opacity: 0.05; transform: rotate(0deg); }
        50% { opacity: 0.15; transform: rotate(180deg); }
    }
    
    /* Enhanced status indicators */
    .api-status {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        gap: 0.6rem;
        transition: all 0.3s ease;
        cursor: pointer;
        animation: statusGlow 2s ease-in-out infinite;
    }
    
    .status-active {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.3));
        color: #10b981;
        border: 2px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .status-active:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(5, 150, 105, 0.4));
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        transform: scale(1.05);
    }
    
    .status-inactive {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.3));
        color: #f59e0b;
        border: 2px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .status-inactive:hover {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(217, 119, 6, 0.4));
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
        transform: scale(1.05);
    }
    
    @keyframes statusGlow {
        0%, 100% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2); }
        50% { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); }
    }
    
    /* Enhanced cesium container */
    .cesium-container {
        height: 650px;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        border: 2px solid transparent;
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        margin: 2rem 0;
        position: relative;
        transition: all 0.4s ease;
    }
    
    .cesium-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        animation: borderGlow 8s ease infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .cesium-container:hover {
        transform: scale(1.01);
        box-shadow: 0 25px 70px rgba(0,0,0,0.3);
    }
    
    /* Enhanced chat interface */
    .chat-interface {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2.5rem 0;
        border: 2px solid transparent;
        color: white;
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .chat-interface::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        animation: chatBorderFlow 10s ease infinite;
    }
    
    @keyframes chatBorderFlow {
        0%, 100% { background-position: 0% 50%; }
        25% { background-position: 100% 0%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
    }
    
    /* Enhanced tabs with neon effect */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-bottom: 2px solid #404040;
        padding: 0.5rem;
        border-radius: 16px 16px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        color: #888;
        border-radius: 12px;
        border: 2px solid transparent;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(78, 205, 196, 0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #4a4a4a, #3a3a3a);
        color: #4ecdc4;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(78, 205, 196, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4ecdc4, #45b7d1);
        color: white;
        border-color: #4ecdc4;
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(78, 205, 196, 0.4);
        animation: tabGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes tabGlow {
        0% { box-shadow: 0 12px 30px rgba(78, 205, 196, 0.4); }
        100% { box-shadow: 0 12px 30px rgba(78, 205, 196, 0.6); }
    }
    
    /* Enhanced data tables with ocean glass effect */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        animation: tableFloat 8s ease-in-out infinite;
    }
    
    @keyframes tableFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    .stDataFrame:hover {
        border-color: #FFD700;
        box-shadow: 0 25px 60px rgba(255, 215, 0, 0.2);
        transform: translateY(-12px);
    }
    
    /* Enhanced select boxes */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 30%, #FFF8DC 60%, #FFEB3B 100%);
        border: 2px solid rgba(255,215,0,0.4);
        border-radius: 16px;
        color: #004080;
        font-weight: 600;
        transition: all 0.4s ease;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.2);
        min-height: 60px;
        display: flex;
        align-items: center;
        animation: selectFloat 7s ease-in-out infinite;
    }
    
    @keyframes selectFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    
    .stSelectbox > div > div:hover {
        border-color: #FFFFFF;
        box-shadow: 0 12px 30px rgba(255, 215, 0, 0.4);
        transform: translateY(-10px) scale(1.02);
    }
    
    /* Enhanced multiselect */
    .stMultiSelect > div > div {
        background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 30%, #FFF8DC 60%, #FFEB3B 100%);
        border: 2px solid rgba(255,215,0,0.4);
        border-radius: 16px;
        color: #004080;
        font-weight: 600;
        transition: all 0.4s ease;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.2);
        min-height: 60px;
        animation: multiselectFloat 6s ease-in-out infinite;
    }
    
    @keyframes multiselectFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-7px) rotate(0.2deg); }
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #FFFFFF;
        box-shadow: 0 12px 30px rgba(255, 215, 0, 0.4);
        transform: translateY(-12px) scale(1.03);
    }
    
    /* Enhanced expander with wave animation */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 50%, #FFEB3B 100%);
        border-radius: 18px;
        padding: 1.5rem;
        border: 2px solid rgba(255,215,0,0.4);
        font-weight: 700;
        color: #004080;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        min-height: 60px;
        display: flex;
        align-items: center;
        animation: expanderFloat 8s ease-in-out infinite;
    }
    
    @keyframes expanderFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        50% { 
            transform: translateY(-10px) rotate(0.3deg);
        }
    }
    
    .streamlit-expanderHeader:hover {
        transform: translateY(-15px) scale(1.03) rotate(0.5deg);
        box-shadow: 0 20px 50px rgba(255, 215, 0, 0.5);
        background: linear-gradient(135deg, #FFEB3B 0%, #FFFFFF 50%, #FFD700 100%);
        animation: expanderWaveFloat 2s ease-in-out infinite;
    }
    
    @keyframes expanderWaveFloat {
        0%, 100% { 
            transform: translateY(-15px) scale(1.03) rotate(0.5deg);
        }
        50% { 
            transform: translateY(-22px) scale(1.05) rotate(-0.2deg);
        }
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 0 0 18px 18px;
        padding: 2rem;
        border: 2px solid rgba(255,215,0,0.3);
        border-top: none;
        animation: contentWave 0.8s ease-out;
        color: white;
    }
    
    @keyframes contentWave {
        0% { 
            opacity: 0; 
            transform: translateY(-20px) scale(0.95); 
        }
        100% { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    /* Enhanced sidebar with ocean theme */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(0, 61, 130, 0.8), rgba(0, 100, 200, 0.6));
        backdrop-filter: blur(25px);
        border-right: 2px solid rgba(255,215,0,0.3);
    }
    
    /* Enhanced code blocks */
    .stCodeBlock {
        border-radius: 18px;
        border: 2px solid rgba(255,215,0,0.3);
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        animation: codeFloat 10s ease-in-out infinite;
    }
    
    @keyframes codeFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    .stCodeBlock:hover {
        border-color: #FFD700;
        box-shadow: 0 15px 40px rgba(255, 215, 0, 0.2);
        transform: translateY(-12px);
    }
    
    code {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(255, 215, 0, 0.2);
        padding: 6px 10px;
        border-radius: 8px;
        color: #FFD700;
        font-size: 0.95em;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    code:hover {
        background: rgba(255, 255, 255, 0.3);
        color: #004080;
        transform: scale(1.05);
    }
    
    pre {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 2rem;
        border: 2px solid rgba(255,215,0,0.3);
        overflow-x: auto;
        transition: all 0.3s ease;
        color: white;
    }
    
    pre:hover {
        border-color: #FFD700;
        box-shadow: 0 12px 35px rgba(255, 215, 0, 0.2);
    }
    
    /* Status indicators with ocean theme */
    .api-status {
        display: inline-flex;
        align-items: center;
        padding: 10px 18px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        gap: 0.6rem;
        transition: all 0.4s ease;
        cursor: pointer;
        min-height: 40px;
        animation: statusFloat 6s ease-in-out infinite;
    }
    
    @keyframes statusFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .status-active {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.3), rgba(0, 204, 102, 0.4));
        color: #00FF88;
        border: 2px solid rgba(0, 255, 136, 0.5);
        box-shadow: 0 8px 20px rgba(0, 255, 136, 0.3);
        backdrop-filter: blur(15px);
    }
    
    .status-active:hover {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.4), rgba(0, 204, 102, 0.5));
        box-shadow: 0 12px 30px rgba(0, 255, 136, 0.4);
        transform: translateY(-8px) scale(1.05);
    }
    
    .status-inactive {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.3), rgba(255, 152, 0, 0.4));
        color: #FFC107;
        border: 2px solid rgba(255, 193, 7, 0.5);
        box-shadow: 0 8px 20px rgba(255, 193, 7, 0.3);
        backdrop-filter: blur(15px);
    }
    
    .status-inactive:hover {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.4), rgba(255, 152, 0, 0.5));
        box-shadow: 0 12px 30px rgba(255, 193, 7, 0.4);
        transform: translateY(-8px) scale(1.05);
    }
    
    /* Enhanced ag-grid styling with ocean theme */
    .ag-theme-alpine-dark {
        --ag-background-color: rgba(0, 0, 0, 0.2);
        --ag-border-color: rgba(255,215,0,0.3);
        --ag-header-background-color: rgba(255, 215, 0, 0.2);
        --ag-odd-row-background-color: rgba(255, 255, 255, 0.05);
        --ag-row-hover-color: rgba(255, 215, 0, 0.1);
        --ag-header-column-separator-color: #FFD700;
        border-radius: 20px;
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    
    .ag-theme-alpine-dark:hover {
        border-color: #FFD700;
        box-shadow: 0 25px 60px rgba(255, 215, 0, 0.2);
        transform: translateY(-5px);
    }
    
    /* Enhanced tooltips with ocean theme */
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background: rgba(0, 61, 130, 0.9);
        backdrop-filter: blur(25px);
        color: white;
        text-align: center;
        border-radius: 15px;
        padding: 18px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid rgba(255,215,0,0.4);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        font-size: 0.95rem;
        line-height: 1.6;
        transform: translateY(15px) scale(0.8);
    }
    
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -10px;
        border-width: 10px;
        border-style: solid;
        border-color: rgba(255,215,0,0.4) transparent transparent transparent;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
        transform: translateY(0) scale(1);
        animation: tooltipWave 2s ease-in-out infinite;
    }
    
    @keyframes tooltipWave {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-5px) scale(1.02); }
    }
    
    /* Enhanced success/error messages */
    .stSuccess {
        background: rgba(0, 255, 136, 0.15);
        backdrop-filter: blur(20px);
        border: 2px solid #00FF88;
        border-radius: 16px;
        animation: successWave 3s ease-in-out infinite;
        color: white;
    }
    
    @keyframes successWave {
        0%, 100% { 
            box-shadow: 0 0 0 rgba(0, 255, 136, 0.4);
            transform: translateY(0);
        }
        50% { 
            box-shadow: 0 0 25px rgba(0, 255, 136, 0.6);
            transform: translateY(-5px);
        }
    }
    
    .stError {
        background: rgba(255, 68, 68, 0.15);
        backdrop-filter: blur(20px);
        border: 2px solid #FF4444;
        border-radius: 16px;
        animation: errorBob 2s ease-in-out infinite;
        color: white;
    }
    
    @keyframes errorBob {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-3px) rotate(0.5deg); }
        75% { transform: translateY(-3px) rotate(-0.5deg); }
    }
    
    /* Progress bar with ocean wave */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FFD700, #FFFFFF, #FFEB3B, #FFD700) !important;
        background-size: 300% 100%;
        animation: progressWave 2.5s linear infinite;
        border-radius: 12px;
        height: 15px !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    @keyframes progressWave {
        0% { background-position: 0% 0%; }
        100% { background-position: 300% 0%; }
    }
    
    /* Custom scrollbar with ocean theme */
    ::-webkit-scrollbar {
        width: 14px;
        height: 14px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 61, 130, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #FFD700, #FFFFFF);
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,215,0,0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #FFFFFF, #FFD700);
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        transform: scale(1.1);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .cesium-container {
            height: 450px;
            border-radius: 20px;
        }
        
        .main-header {
            padding: 2rem;
            border-radius: 20px;
        }
        
        .header-title {
            font-size: 2.5rem;
        }
        
        .header-subtitle {
            font-size: 1.1rem;
        }
        
        .metric-card {
            padding: 2rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
        }
        
        .sample-queries {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .sample-query {
            height: 80px;
            font-size: 0.9rem;
            padding: 1rem;
        }
        
        .data-panel, .chat-interface {
            padding: 2rem;
        }
        
        .query-button, 
        .stButton > button, 
        .stDownloadButton > button {
            min-height: 50px;
            padding: 1rem 1.5rem;
            font-size: 0.9rem;
        }
    }
    
    @media (max-width: 480px) {
        .sample-queries {
            grid-template-columns: 1fr;
        }
        
        .sample-query {
            height: 70px;
            font-size: 0.85rem;
        }
        
        body, .stApp {
            background: linear-gradient(180deg, #87CEEB 0%, #4682B4 30%, #1E90FF 70%, #003D82 100%);
        }
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Enhanced focus indicators */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid #FFD700;
        outline-offset: 3px;
        box-shadow: 0 0 0 6px rgba(255, 215, 0, 0.3);
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .main-header, .metric-card, .data-panel {
            border: 3px solid white;
        }
        
        .query-button, .stButton > button {
            border: 3px solid #FFD700;
        }
    }
    
    /* Ocean depth scroll effect */
    @media (min-width: 769px) {
        .stApp {
            background-attachment: fixed;
        }
    }
    
    /* Initialize ocean bubble layer */
    .stApp {
        position: relative;
    }
    
    .stApp .ocean-bubbles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle 4px at 15% 25%, rgba(255,255,255,0.4), transparent),
            radial-gradient(circle 2px at 85% 35%, rgba(255,255,255,0.3), transparent),
            radial-gradient(circle 6px at 45% 75%, rgba(255,255,255,0.5), transparent),
            radial-gradient(circle 3px at 75% 85%, rgba(255,255,255,0.3), transparent),
            radial-gradient(circle 5px at 25% 95%, rgba(255,255,255,0.4), transparent),
            radial-gradient(circle 2px at 95% 15%, rgba(255,255,255,0.2), transparent);
        background-size: 500px 500px, 300px 300px, 700px 700px, 400px 400px, 600px 600px, 200px 200px;
        animation: bubbleRise 20s linear infinite;
        pointer-events: none;
        z-index: -1;
    }
</style>

<script>
// Ocean bubble layer injection
document.addEventListener('DOMContentLoaded', function() {
    const app = document.querySelector('.stApp');
    if (app && !app.querySelector('.ocean-bubbles')) {
        const bubbleLayer = document.createElement('div');
        bubbleLayer.className = 'ocean-bubbles';
        app.appendChild(bubbleLayer);
    }
});

// Scroll-responsive ocean effects
let ticking = false;
function updateOcean() {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.3;
    const maxScroll = document.body.scrollHeight - window.innerHeight;
    const scrollPercent = Math.min(scrolled / maxScroll, 1);
    
    // Change ocean depth and color based on scroll
    const hueShift = scrollPercent * 40;
    const brightness = 1 - (scrollPercent * 0.3);
    const saturation = 1 + (scrollPercent * 0.5);
    
    document.body.style.filter = `hue-rotate(${hueShift}deg) brightness(${brightness}) saturate(${saturation})`;
    
    // Move bubble layer with scroll
    const bubbleLayer = document.querySelector('.ocean-bubbles');
    if (bubbleLayer) {
        bubbleLayer.style.transform = `translateY(${rate}px) scale(${1 + scrollPercent * 0.1})`;
    }
    
    ticking = false;
}

function requestTick() {
    if (!ticking) {
        requestAnimationFrame(updateOcean);
        ticking = true;
    }
}

window.addEventListener('scroll', requestTick);
</script>
""", unsafe_allow_html=True)# Enhanced CSS with Ocean Waves and Yellow-White Floating Buttons
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global styles with ocean background */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Ocean wave background */
    body, .stApp {
        background: linear-gradient(180deg, #87CEEB 0%, #4682B4 25%, #1E90FF 50%, #0066CC 75%, #003D82 100%);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated ocean waves */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: 
            radial-gradient(ellipse 800px 50px at 400px 50px, rgba(255,255,255,0.3), transparent),
            radial-gradient(ellipse 600px 40px at 200px 150px, rgba(255,255,255,0.2), transparent),
            radial-gradient(ellipse 700px 45px at 600px 250px, rgba(255,255,255,0.25), transparent),
            radial-gradient(ellipse 500px 35px at 800px 350px, rgba(255,255,255,0.2), transparent),
            radial-gradient(ellipse 900px 60px at 300px 450px, rgba(255,255,255,0.3), transparent);
        animation: oceanWaves 12s ease-in-out infinite;
        pointer-events: none;
        z-index: -2;
        opacity: 0.6;
    }
    
    @keyframes oceanWaves {
        0%, 100% { 
            transform: translateX(0) translateY(0);
        }
        25% { 
            transform: translateX(-100px) translateY(-20px);
        }
        50% { 
            transform: translateX(-200px) translateY(-40px);
        }
        75% { 
            transform: translateX(-300px) translateY(-20px);
        }
    }
    
    /* Deeper wave layers */
    .stApp::after {
        content: '';
        position: fixed;
        top: 50px;
        left: 0;
        width: 200%;
        height: 100%;
        background: 
            radial-gradient(ellipse 600px 30px at 500px 100px, rgba(255,255,255,0.15), transparent),
            radial-gradient(ellipse 800px 40px at 100px 200px, rgba(255,255,255,0.1), transparent),
            radial-gradient(ellipse 400px 25px at 700px 300px, rgba(255,255,255,0.12), transparent),
            radial-gradient(ellipse 650px 35px at 200px 400px, rgba(255,255,255,0.08), transparent);
        animation: deepWaves 18s ease-in-out infinite reverse;
        pointer-events: none;
        z-index: -3;
        opacity: 0.4;
    }
    
    @keyframes deepWaves {
        0%, 100% { 
            transform: translateX(0) translateY(10px);
        }
        33% { 
            transform: translateX(-150px) translateY(-10px);
        }
        66% { 
            transform: translateX(-250px) translateY(5px);
        }
    }
    
    /* Underwater bubbles */
    .ocean-bubbles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle 3px at 10% 20%, rgba(255,255,255,0.3), transparent),
            radial-gradient(circle 2px at 80% 30%, rgba(255,255,255,0.2), transparent),
            radial-gradient(circle 4px at 40% 70%, rgba(255,255,255,0.25), transparent),
            radial-gradient(circle 2px at 90% 80%, rgba(255,255,255,0.2), transparent),
            radial-gradient(circle 3px at 20% 90%, rgba(255,255,255,0.3), transparent);
        background-size: 400px 400px, 300px 300px, 500px 500px, 200px 200px, 350px 350px;
        animation: bubbleRise 15s linear infinite;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes bubbleRise {
        0% { 
            background-position: 0% 100%, 0% 100%, 0% 100%, 0% 100%, 0% 100%;
            opacity: 0.6;
        }
        50% {
            opacity: 0.8;
        }
        100% { 
            background-position: 100% -100%, -100% -100%, 50% -100%, 200% -100%, -50% -100%;
            opacity: 0.6;
        }
    }
    
    /* Enhanced main header */
    .main-header {
        background: linear-gradient(135deg, rgba(255,215,0,0.9) 0%, rgba(255,255,255,0.8) 50%, rgba(255,235,59,0.9) 100%);
        backdrop-filter: blur(20px);
        padding: 3rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        color: #003D82;
        box-shadow: 0 20px 60px rgba(255, 215, 0, 0.3);
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255,255,255,0.3);
        animation: headerFloat 6s ease-in-out infinite;
    }
    
    @keyframes headerFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
            box-shadow: 0 20px 60px rgba(255, 215, 0, 0.3);
        }
        50% { 
            transform: translateY(-10px) rotate(0.5deg);
            box-shadow: 0 30px 80px rgba(255, 215, 0, 0.4);
        }
    }
    
    .header-title {
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        color: #003D82;
        animation: titleWave 4s ease-in-out infinite;
    }
    
    @keyframes titleWave {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        font-weight: 500;
        opacity: 0.8;
        margin: 0;
        color: #004080;
        animation: subtitleFloat 5s ease-in-out infinite;
    }
    
    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0) translateX(0); }
        33% { transform: translateY(-3px) translateX(2px); }
        66% { transform: translateY(3px) translateX(-2px); }
    }
    
    /* Unified button styling - all buttons same size with yellow-white theme */
    .query-button, 
    .stButton > button, 
    .stDownloadButton > button,
    .sample-query {
        background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 30%, #FFF8DC 60%, #FFEB3B 100%);
        background-size: 300% 300%;
        border: 2px solid rgba(255,215,0,0.4);
        border-radius: 18px;
        padding: 1.2rem 2rem;
        color: #004080;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        position: relative;
        overflow: hidden;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        animation: buttonFloat 4s ease-in-out infinite;
        backdrop-filter: blur(10px);
    }
    
    @keyframes buttonFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
            background-position: 0% 50%;
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        }
        25% { 
            transform: translateY(-5px) rotate(0.5deg);
            background-position: 50% 0%;
            box-shadow: 0 12px 35px rgba(255, 215, 0, 0.4);
        }
        50% { 
            transform: translateY(-8px) rotate(0deg);
            background-position: 100% 50%;
            box-shadow: 0 15px 40px rgba(255, 215, 0, 0.5);
        }
        75% { 
            transform: translateY(-3px) rotate(-0.5deg);
            background-position: 50% 100%;
            box-shadow: 0 12px 35px rgba(255, 215, 0, 0.4);
        }
    }
    
    /* Wave animation on button surfaces */
    .query-button::before, 
    .stButton > button::before, 
    .stDownloadButton > button::before,
    .sample-query::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255,255,255,0.4), 
            transparent);
        animation: waveRipple 3s ease-in-out infinite;
        transition: left 0.6s ease;
    }
    
    @keyframes waveRipple {
        0% { left: -100%; }
        50% { left: 0%; }
        100% { left: 100%; }
    }
    
    /* Enhanced hover effects for floating in waves */
    .query-button:hover, 
    .stButton > button:hover, 
    .stDownloadButton > button:hover,
    .sample-query:hover {
        transform: translateY(-12px) scale(1.05) rotate(1deg);
        box-shadow: 0 20px 50px rgba(255, 215, 0, 0.6);
        background: linear-gradient(135deg, #FFEB3B 0%, #FFFFFF 50%, #FFD700 100%);
        border-color: rgba(255,255,255,0.8);
        animation: floatingWave 2s ease-in-out infinite;
    }
    
    @keyframes floatingWave {
        0%, 100% { 
            transform: translateY(-12px) scale(1.05) rotate(1deg);
        }
        50% { 
            transform: translateY(-18px) scale(1.08) rotate(-0.5deg);
        }
    }
    
    .query-button:active, 
    .stButton > button:active, 
    .stDownloadButton > button:active,
    .sample-query:active {
        transform: translateY(-6px) scale(1.02);
        animation: buttonSplash 0.3s ease-out;
    }
    
    @keyframes buttonSplash {
        0% { box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 15px 40px rgba(255, 255, 255, 0.6); }
        100% { box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3); }
    }
    
    /* Enhanced stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2.5rem;
        color: white;
        border: 2px solid rgba(255,255,255,0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        cursor: pointer;
        animation: cardFloat 8s ease-in-out infinite;
    }
    
    @keyframes cardFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        25% { 
            transform: translateY(-8px) rotate(0.5deg);
        }
        50% { 
            transform: translateY(-15px) rotate(0deg);
        }
        75% { 
            transform: translateY(-5px) rotate(-0.5deg);
        }
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #FFD700, #FFFFFF, #FFEB3B);
        background-size: 200% 100%;
        animation: waveShimmer 4s linear infinite;
    }
    
    @keyframes waveShimmer {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    .metric-card:hover {
        transform: translateY(-15px) scale(1.03) rotate(1deg);
        box-shadow: 0 25px 60px rgba(255, 215, 0, 0.3);
        border-color: rgba(255,255,255,0.5);
        animation: cardWaveFloat 3s ease-in-out infinite;
    }
    
    @keyframes cardWaveFloat {
        0%, 100% { 
            transform: translateY(-15px) scale(1.03) rotate(1deg);
        }
        50% { 
            transform: translateY(-22px) scale(1.05) rotate(-0.5deg);
        }
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #E6F3FF;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-label {
        color: #FFD700;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(45deg, #FFD700, #FFFFFF);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.8rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
        animation: valueGlow 3s ease-in-out infinite;
    }
    
    @keyframes valueGlow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    .metric-card:hover .metric-value {
        transform: scale(1.08);
        animation: valueWave 1.5s ease-in-out infinite;
    }
    
    @keyframes valueWave {
        0%, 100% { transform: scale(1.08) translateY(0); }
        50% { transform: scale(1.1) translateY(-3px); }
    }
    
    .metric-description {
        font-size: 1rem;
        color: #B3D9FF;
        margin: 0;
        line-height: 1.6;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-description {
        color: #FFFFFF;
    }
    
    /* Dynamic live indicator with ocean theme */
    .live-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        background: radial-gradient(circle, #00FF88, #00CC66);
        border-radius: 50%;
        margin-right: 10px;
        animation: oceanPulse 2.5s ease-in-out infinite;
        box-shadow: 0 0 0 rgba(0, 255, 136, 0.6);
        position: relative;
    }
    
    .live-indicator::after {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        border-radius: 50%;
        background: radial-gradient(circle, transparent 40%, #00FF88 80%);
        animation: oceanRipple 2.5s ease-in-out infinite 0.8s;
    }
    
    @keyframes oceanPulse {
        0% {
            transform: scale(0.9);
            box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.8);
        }
        50% {
            transform: scale(1.2);
            box-shadow: 0 0 0 20px rgba(0, 255, 136, 0);
        }
        100% {
            transform: scale(0.9);
            box-shadow: 0 0 0 0 rgba(0, 255, 136, 0);
        }
    }
    
    @keyframes oceanRipple {
        0% {
            transform: scale(0.5);
            opacity: 1;
        }
        100% {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    /* Sample queries with consistent sizing and wave floating */
    .sample-queries {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .sample-query {
        height: 100px;
        animation-delay: calc(var(--index, 0) * 0.2s);
    }
    
    .sample-query:nth-child(1) { --index: 0; }
    .sample-query:nth-child(2) { --index: 1; }
    .sample-query:nth-child(3) { --index: 2; }
    .sample-query:nth-child(4) { --index: 3; }
    
    /* Enhanced input fields with ocean theme */
    .query-input {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255,215,0,0.3);
        border-radius: 18px;
        padding: 1.5rem;
        color: white;
        width: 100%;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        position: relative;
        animation: inputFloat 6s ease-in-out infinite;
    }
    
    @keyframes inputFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .query-input:focus {
        outline: none;
        border-color: #FFD700;
        box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.25), 0 15px 35px rgba(255,215,0,0.2);
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.25);
    }
    
    .query-input::placeholder {
        color: rgba(255,255,255,0.7);
    }
    
    /* Enhanced panels with ocean glass effect */
    .data-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 2.5rem;
        color: white;
        border: 2px solid rgba(255,255,255,0.2);
        margin: 2rem 0;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
        animation: panelFloat 10s ease-in-out infinite;
    }
    
    @keyframes panelFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        33% { 
            transform: translateY(-8px) rotate(0.3deg);
        }
        66% { 
            transform: translateY(-12px) rotate(-0.3deg);
        }
    }
    
    .data-panel:hover {
        transform: translateY(-15px) rotate(0.5deg);
        box-shadow: 0 30px 70px rgba(255, 215, 0, 0.2);
        border-color: rgba(255,215,0,0.4);
    }
    
    .panel-title {
        background: linear-gradient(45deg, #FFD700, #FFFFFF);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 2rem;
        border-bottom: 3px solid rgba(255,215,0,0.3);
        padding-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: titleShimmer 4s ease-in-out infinite;
    }
    
    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    /* Enhanced NASA panel with ocean theme */
    .nasa-panel {
        background: rgba(30, 58, 138, 0.3);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 2.5rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.4);
        border: 2px solid rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
        animation: nasaFloat 12s ease-in-out infinite;
    }
    
    @keyframes nasaFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        25% { 
            transform: translateY(-10px) rotate(0.5deg);
        }
        50% { 
            transform: translateY(-18px) rotate(0deg);
        }
        75% { 
            transform: translateY(-8px) rotate(-0.5deg);
        }
    }
    
    /* Enhanced tabs with wave theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-bottom: 2px solid rgba(255,215,0,0.3);
        padding: 0.5rem;
        border-radius: 20px 20px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 30%, #FFF8DC 60%, #FFEB3B 100%);
        color: #004080;
        border-radius: 15px;
        border: 2px solid rgba(255,215,0,0.4);
        padding: 1rem 2rem;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: tabFloat 5s ease-in-out infinite;
    }
    
    @keyframes tabFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #FFEB3B 0%, #FFFFFF 50%, #FFD700 100%);
        color: #003D82;
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.4);
        animation: tabWaveFloat 2s ease-in-out infinite;
    }
    
    @keyframes tabWaveFloat {
        0%, 100% { 
            transform: translateY(-8px) scale(1.05);
        }
        50% { 
            transform: translateY(-15px) scale(1.08);
        }
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFD700 50%, #FFEB3B 100%);
        color: #003D82;
        border-color: #FFD700;
        transform: translateY(-10px);
        box-shadow: 0 20px 45px rgba(255, 215, 0, 0.5);
        animation: activeTabWave 3s ease-in-out infinite;
    }
    
    @keyframes activeTabWave {
        0%, 100% { 
            transform: translateY(-10px) rotate(0deg);
            box-shadow: 0 20px 45px rgba(255, 215, 0, 0.5);
        }
        50% { 
            transform: translateY(-18px) rotate(0.5deg);
            box-shadow: 0 25px 55px rgba(255, 215, 0, 0.7);
        }
    }
    
    /* Enhanced cesium container */
    .cesium-container {
        height: 650px;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 25px 70px rgba(0,0,0,0.3);
        border: 3px solid rgba(255,215,0,0.4);
        background: rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
        position: relative;
        transition: all 0.4s ease;
        animation: containerFloat 15s ease-in-out infinite;
    }
    
    @keyframes containerFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        33% { 
            transform: translateY(-12px) rotate(0.3deg);
        }
        66% { 
            transform: translateY(-20px) rotate(-0.3deg);
        }
    }
    
    .cesium-container:hover {
        transform: translateY(-25px) scale(1.02);
        box-shadow: 0 35px 90px rgba(255, 215, 0, 0.3);
        border-color: #FFD700;
    }
    
    /* Enhanced chat interface */
    .chat-interface {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2.5rem 0;
        border: 2px solid rgba(255,215,0,0.3);
        color: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        animation: chatFloat 9s ease-in-out infinite;
    }
    
    @keyframes chatFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        50% { 
            transform: translateY(-12px) rotate(0.3deg);
        }
    }
</style>
""", unsafe_allow_html=True)

# Database configuration
# Database configuration with multiple options
DB_CONFIGS = [
    # Primary pooled connection
    {
        "host": "ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech",
        "database": "neondb",
        "user": "neondb_owner",
        "password": "npg_qV9a3dQRAeBm",
        "port": "5432",
        "sslmode": "require"
    },
    # Alternative direct connection
    {
        "host": "ep-still-field-a17hi4xm.ap-southeast-1.aws.neon.tech",  # Direct endpoint
        "database": "neondb",
        "user": "neondb_owner",
        "password": "npg_qV9a3dQRAeBm",
        "port": "5432",
        "sslmode": "require"
    }
]

# Use the first config as default
DB_CONFIG = DB_CONFIGS[0]

# Reference coordinates for major locations
REFERENCE_LOCATIONS = {
    "Chennai": (13.0827, 80.2707),
    "Mumbai": (19.0760, 72.8777),
    "Kochi": (9.9312, 76.2673),
    "Kolkata": (22.5726, 88.3639),
    "Visakhapatnam": (17.6868, 83.2185),
    "Bengaluru": (12.9716, 77.5946),
    "Arabian Sea": (15.0, 65.0),
    "Bay of Bengal": (15.0, 87.0),
    "Indian Ocean": (-20.0, 80.0),
    "Equator": (0.0, 80.0),
    "Maldives": (3.2028, 73.2207),
    "Sri Lanka": (7.8731, 80.7718)
}

@dataclass
class OceanographicAnalysis:
    """Class to hold oceanographic analysis results"""
    mixed_layer_depth: Optional[float] = None
    thermocline_depth: Optional[float] = None
    halocline_depth: Optional[float] = None
    temperature_gradient: Optional[float] = None
    salinity_gradient: Optional[float] = None
    water_mass_classification: Optional[str] = None

class ArgoAIIntelligence:
    def __init__(self):
        self.db_connection = None
        
        # Enhanced schema with oceanographic context
        self.schema_info = """
        ARGO Floats Database Schema:
        
        Table: argo_floats
        Core Columns:
        - platform_number (integer): Unique ARGO float identifier
        - cycle_number (integer): Profile cycle number
        - measurement_time (timestamp): UTC measurement time
        - latitude (float): Decimal degrees (-90 to 90)
        - longitude (float): Decimal degrees (-180 to 180)
        - pressure (float): Water pressure in decibars (dbar)
        - temperature (float): In-situ temperature in Celsius
        - salinity (float): Practical Salinity Units (PSU)
        - data_quality (text): Quality control flag
        
        Oceanographic Context:
        - Indian Ocean coverage with 85 active floats
        - Depth profiles from surface to ~2000m
        - Temperature range: ~15-35°C
        - Salinity range: ~33-37 PSU
        - Mixed layer depth typically 20-100m
        - Thermocline at 100-500m depth
        """

    def connect_db(self) -> bool:
        """Establish database connection"""
        try:
            if self.db_connection is None or self.db_connection.closed:
                self.db_connection = psycopg2.connect(**DB_CONFIG)
            return True
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            return False

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            if self.connect_db():
                df = pd.read_sql_query(query, self.db_connection)
                return df
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()

    def advanced_nlp_to_sql(self, user_query: str, api_key: str = None) -> Dict[str, Any]:
        """Advanced natural language to SQL with pattern matching"""
        
        # Enhanced pattern matching with oceanographic domain knowledge
        patterns = {
            # Location-based queries
            r"(?:nearest|closest|near)\s+(?:to\s+)?(.+)": self._handle_location_query,
            r"floats?\s+(?:in|around|near)\s+(.+)": self._handle_area_query,
            
            # Oceanographic analysis
            r"(?:t-s|temperature.salinity)\s+diagram": self._handle_ts_diagram,
            r"(?:mixed\s+layer|mld)\s+depth": self._handle_mixed_layer_depth,
            r"(?:depth\s+profile|vertical\s+profile)": self._handle_depth_profile,
            r"(?:thermocline|halocline)": self._handle_cline_analysis,
            r"water\s+mass": self._handle_water_mass,
            
            # Temporal queries
            r"(?:seasonal|monthly)\s+(?:trend|cycle|variation)": self._handle_seasonal_analysis,
            r"(?:recent|latest|last\s+\d+)\s+(?:days?|weeks?|months?)": self._handle_recent_data,
            r"(?:compare|comparison)\s+.*(?:between|vs)": self._handle_comparison,
            
            # Parameter-based queries
            r"temperature\s+(?:above|greater than|>)\s+([\d.]+)": self._handle_temp_threshold,
            r"temperature\s+(?:below|less than|<)\s+([\d.]+)": self._handle_temp_threshold,
            r"salinity\s+(?:above|greater than|>)\s+([\d.]+)": self._handle_sal_threshold,
            r"salinity\s+(?:below|less than|<)\s+([\d.]+)": self._handle_sal_threshold,
            
            # Statistical queries
            r"(?:statistics|stats|summary)": self._handle_statistics,
            r"(?:correlation|relationship)\s+between": self._handle_correlation,
            
            # Default patterns
            r"(?:show|display|get|find)\s+all\s+floats?": lambda x: self._get_all_floats_query(),
            r"(?:count|how many)\s+floats?": lambda x: "SELECT COUNT(DISTINCT platform_number) as total_floats FROM argo_floats;",
        }
        
        query_lower = user_query.lower().strip()
        sql_query = None
        analysis_type = "general"
        
        # Try pattern matching
        for pattern, handler in patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                if callable(handler):
                    result = handler(match.groups()[0] if match.groups() else None)
                    if isinstance(result, dict):
                        sql_query = result.get('sql', '')
                        analysis_type = result.get('type', 'general')
                    else:
                        sql_query = result
                        analysis_type = pattern.split(r"\s+")[0] if r"\s+" in pattern else "general"
                break
        
        # Fallback for API-based generation
        if not sql_query and api_key:
            sql_query = self._generate_with_openai(user_query, api_key)
        
        # Final fallback
        if not sql_query:
            sql_query = "SELECT * FROM argo_floats ORDER BY measurement_time DESC LIMIT 20;"
            analysis_type = "general"
        
        return {
            "sql": sql_query,
            "analysis_type": analysis_type,
            "query_interpretation": self._interpret_query(user_query, analysis_type)
        }

    def _handle_location_query(self, location: str) -> Dict[str, Any]:
        """Handle location-based queries with distance calculation"""
        location_clean = location.strip().title()
        
        if location_clean in REFERENCE_LOCATIONS:
            lat, lon = REFERENCE_LOCATIONS[location_clean]
            sql = f"""
            SELECT 
                platform_number, 
                latitude, 
                longitude, 
                temperature, 
                salinity,
                pressure,
                measurement_time,
                SQRT(POW(latitude - {lat}, 2) + POW(longitude - {lon}, 2)) * 111 as distance_km
            FROM argo_floats 
            ORDER BY distance_km ASC 
            LIMIT 20;
            """
            return {"sql": sql, "type": "location_analysis"}
        
        return {"sql": "SELECT * FROM argo_floats LIMIT 20;", "type": "general"}

    def _handle_area_query(self, location: str) -> Dict[str, Any]:
        """Handle area-based queries"""
        return self._handle_location_query(location)

    def _handle_ts_diagram(self, _) -> Dict[str, Any]:
        """Handle T-S diagram requests"""
        sql = """
        SELECT 
            platform_number,
            temperature,
            salinity,
            pressure,
            latitude,
            longitude,
            measurement_time
        FROM argo_floats 
        WHERE temperature IS NOT NULL 
        AND salinity IS NOT NULL
        ORDER BY platform_number, pressure;
        """
        return {"sql": sql, "type": "ts_diagram"}

    def _handle_mixed_layer_depth(self, _) -> Dict[str, Any]:
        """Handle mixed layer depth analysis"""
        sql = """
        WITH depth_profiles AS (
            SELECT 
                platform_number,
                cycle_number,
                pressure as depth,
                temperature,
                salinity,
                ROW_NUMBER() OVER (PARTITION BY platform_number, cycle_number ORDER BY pressure) as depth_rank
            FROM argo_floats
            WHERE pressure <= 200  -- Focus on upper ocean
            AND temperature IS NOT NULL
        )
        SELECT * FROM depth_profiles
        ORDER BY platform_number, cycle_number, depth;
        """
        return {"sql": sql, "type": "mixed_layer_depth"}

    def _handle_depth_profile(self, _) -> Dict[str, Any]:
        """Handle depth profile visualization"""
        sql = """
        SELECT 
            platform_number,
            cycle_number,
            pressure as depth,
            temperature,
            salinity,
            measurement_time,
            latitude,
            longitude
        FROM argo_floats
        ORDER BY platform_number, cycle_number, pressure;
        """
        return {"sql": sql, "type": "depth_profile"}

    def _handle_cline_analysis(self, _) -> Dict[str, Any]:
        """Handle thermocline/halocline analysis"""
        return self._handle_depth_profile(_)

    def _handle_water_mass(self, _) -> Dict[str, Any]:
        """Handle water mass identification"""
        return self._handle_ts_diagram(_)

    def _handle_seasonal_analysis(self, _) -> Dict[str, Any]:
        """Handle seasonal trend analysis"""
        sql = """
        SELECT 
            EXTRACT(MONTH FROM measurement_time) as month,
            EXTRACT(YEAR FROM measurement_time) as year,
            platform_number,
            AVG(temperature) as avg_temperature,
            AVG(salinity) as avg_salinity,
            COUNT(*) as measurements,
            AVG(latitude) as avg_lat,
            AVG(longitude) as avg_lon
        FROM argo_floats
        GROUP BY year, month, platform_number
        ORDER BY year, month, platform_number;
        """
        return {"sql": sql, "type": "seasonal_analysis"}

    def _handle_recent_data(self, _) -> Dict[str, Any]:
        """Handle recent data queries"""
        sql = """
        SELECT * FROM argo_floats 
        WHERE measurement_time >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY measurement_time DESC
        LIMIT 50;
        """
        return {"sql": sql, "type": "recent_data"}

    def _handle_comparison(self, _) -> Dict[str, Any]:
        """Handle comparison queries"""
        return self._handle_seasonal_analysis(_)

    def _handle_temp_threshold(self, temp: str) -> Dict[str, Any]:
        """Handle temperature threshold queries"""
        try:
            temp_val = float(temp)
            sql = f"SELECT * FROM argo_floats WHERE temperature > {temp_val} ORDER BY temperature DESC LIMIT 50;"
            return {"sql": sql, "type": "temperature_analysis"}
        except:
            return {"sql": "SELECT * FROM argo_floats WHERE temperature > 25 ORDER BY temperature DESC LIMIT 50;", "type": "temperature_analysis"}

    def _handle_sal_threshold(self, sal: str) -> Dict[str, Any]:
        """Handle salinity threshold queries"""
        try:
            sal_val = float(sal)
            sql = f"SELECT * FROM argo_floats WHERE salinity > {sal_val} ORDER BY salinity DESC LIMIT 50;"
            return {"sql": sql, "type": "salinity_analysis"}
        except:
            return {"sql": "SELECT * FROM argo_floats WHERE salinity > 35 ORDER BY salinity DESC LIMIT 50;", "type": "salinity_analysis"}

    def _handle_statistics(self, _) -> Dict[str, Any]:
        """Handle statistical summary requests"""
        sql = """
        SELECT 
            COUNT(DISTINCT platform_number) as unique_floats,
            COUNT(*) as total_measurements,
            AVG(temperature) as mean_temperature,
            STDDEV(temperature) as std_temperature,
            MIN(temperature) as min_temperature,
            MAX(temperature) as max_temperature,
            AVG(salinity) as mean_salinity,
            STDDEV(salinity) as std_salinity,
            MIN(salinity) as min_salinity,
            MAX(salinity) as max_salinity,
            AVG(pressure) as mean_pressure,
            MAX(pressure) as max_pressure,
            MIN(measurement_time) as earliest_measurement,
            MAX(measurement_time) as latest_measurement
        FROM argo_floats;
        """
        return {"sql": sql, "type": "statistics"}

    def _handle_correlation(self, _) -> Dict[str, Any]:
        """Handle correlation analysis"""
        sql = """
        SELECT temperature, salinity, pressure, latitude, longitude 
        FROM argo_floats 
        WHERE temperature IS NOT NULL AND salinity IS NOT NULL;
        """
        return {"sql": sql, "type": "correlation"}

    def _get_all_floats_query(self) -> str:
        """Get all floats query"""
        return "SELECT DISTINCT platform_number, AVG(latitude) as avg_lat, AVG(longitude) as avg_lon FROM argo_floats GROUP BY platform_number ORDER BY platform_number;"

    def _generate_with_openai(self, query: str, api_key: str) -> str:
        """Generate SQL using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            You are an expert oceanographer and SQL developer. Generate a PostgreSQL query for ARGO float data.

            Database Schema:
            {self.schema_info}

            User Query: "{query}"

            Generate a SQL query that:
            1. Answers the user's question accurately
            2. Uses proper oceanographic terminology
            3. Includes relevant columns for visualization
            4. Handles NULL values appropriately
            5. Uses appropriate LIMIT clauses for performance

            Return only the SQL query, no explanations.
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                st.warning(f"OpenAI API error: {response.status_code}")
                
        except Exception as e:
            st.warning(f"AI query generation failed: {e}")
        
        return "SELECT * FROM argo_floats ORDER BY measurement_time DESC LIMIT 20;"

    def _interpret_query(self, query: str, analysis_type: str) -> str:
        """Provide human-readable interpretation of the query"""
        interpretations = {
            "location_analysis": f"Finding ARGO floats nearest to the specified location with distance calculations.",
            "ts_diagram": "Generating Temperature-Salinity diagram data for water mass analysis.",
            "mixed_layer_depth": "Analyzing mixed layer depth from temperature and salinity profiles.",
            "depth_profile": "Creating vertical ocean profiles showing temperature and salinity vs depth.",
            "seasonal_analysis": "Examining seasonal trends and cycles in oceanographic parameters.",
            "statistics": "Computing comprehensive statistical summary of all ARGO float measurements.",
            "general": f"Processing general query: {query}"
        }
        
        return interpretations.get(analysis_type, f"Analyzing: {query}")

    def create_ts_diagram(self, df: pd.DataFrame) -> go.Figure:
        """Create Temperature-Salinity diagram"""
        if df.empty or 'temperature' not in df.columns or 'salinity' not in df.columns:
            return go.Figure().add_annotation(text="No T-S data available", 
                                            xref="paper", yref="paper", 
                                            x=0.5, y=0.5, showarrow=False)
        
        fig = go.Figure()
        
        # Color by depth (pressure)
        if 'pressure' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['salinity'],
                y=df['temperature'],
                mode='markers',
                marker=dict(
                    size=4,
                    color=df['pressure'],
                    colorscale='Viridis',
                    colorbar=dict(title="Pressure (dbar)"),
                    opacity=0.7
                ),
                text=df.apply(lambda row: f"Float: {row.get('platform_number', 'N/A')}<br>"
                                        f"Depth: {row.get('pressure', 'N/A')} dbar<br>"
                                        f"T: {row['temperature']:.2f}°C<br>"
                                        f"S: {row['salinity']:.2f} PSU", axis=1),
                hovertemplate="%{text}<extra></extra>",
                name="T-S Data"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df['salinity'],
                y=df['temperature'],
                mode='markers',
                marker=dict(size=4, opacity=0.7),
                name="T-S Data"
            ))
        
        fig.update_layout(
            title="Temperature-Salinity Diagram",
            xaxis_title="Salinity (PSU)",
            yaxis_title="Temperature (°C)",
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig

    def create_depth_profile(self, df: pd.DataFrame) -> go.Figure:
        """Create depth profile visualization"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Temperature Profile', 'Salinity Profile'),
            shared_yaxes=True
        )
        
        # Group by float and cycle
        colors = px.colors.qualitative.Set3
        color_idx = 0
        
        for (platform, cycle), group in df.groupby(['platform_number', 'cycle_number']):
            if color_idx > 20:  # Limit number of profiles for readability
                break
                
            group = group.sort_values('pressure')
            color = colors[color_idx % len(colors)]
            
            if 'temperature' in group.columns:
                fig.add_trace(
                    go.Scatter(
                        x=group['temperature'],
                        y=-group['pressure'],  # Negative for depth
                        mode='lines+markers',
                        name=f"Float {platform} Cycle {cycle}",
                        line=dict(color=color),
                        showlegend=(color_idx < 10)  # Only show legend for first 10
                    ),
                    row=1, col=1
                )
            
            if 'salinity' in group.columns:
                fig.add_trace(
                    go.Scatter(
                        x=group['salinity'],
                        y=-group['pressure'],
                        mode='lines+markers',
                        name=f"Float {platform} Cycle {cycle}",
                        line=dict(color=color),
                        showlegend=False
                    ),
                    row=1, col=2
                )
            
            color_idx += 1
        
        fig.update_xaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_xaxes(title_text="Salinity (PSU)", row=1, col=2)
        fig.update_yaxes(title_text="Depth (m)", row=1, col=1)
        
        fig.update_layout(
            title="Ocean Depth Profiles",
            height=600,
            hovermode='closest'
        )
        
        return fig

    def create_advanced_map(self, df: pd.DataFrame, analysis_type: str = "general") -> folium.Map:
        """Create advanced interactive map"""
        if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
            return None
        
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('CartoDB Positron', name='Light Map').add_to(m)
        folium.TileLayer('CartoDB Dark_Matter', name='Dark Map').add_to(m)
        
        # Add markers
        for idx, row in df.iterrows():
            popup_content = f"""
            <div style="width: 200px;">
                <h4>ARGO Float {row['platform_number']}</h4>
                <p><b>Location:</b> {row['latitude']:.4f}°N, {row['longitude']:.4f}°E</p>
                <p><b>Temperature:</b> {row.get('temperature', 'N/A')}°C</p>
                <p><b>Salinity:</b> {row.get('salinity', 'N/A')} PSU</p>
                <p><b>Depth:</b> {row.get('pressure', 'N/A')} dbar</p>
                <p><b>Time:</b> {str(row.get('measurement_time', 'N/A'))}</p>
            </div>
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color='blue', icon='tint')
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m

# Database connection pool
@st.cache_resource
# Database connection pool with better error handling
@st.cache_resource
def init_db_pool():
    try:
        # Try the pooled connection first
        pool = SimpleConnectionPool(
            1, 10,
            "postgresql://neondb_owner:npg_qV9a3dQRAeBm@ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
        
        # Test the connection
        conn = pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        pool.putconn(conn)
        
        logger.info("Database connection pool established successfully")
        return pool
        
    except Exception as e:
        logger.warning(f"Database connection pool failed: {e}. Using fallback connection.")
        
        # Try direct connection as fallback
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            logger.info("Direct database connection successful")
            # Create a simple pool wrapper for direct connections
            return SimpleDirectConnectionPool(DB_CONFIG)
        except Exception as direct_error:
            logger.error(f"Direct connection also failed: {direct_error}. Using sample data.")
            st.warning("Database connection unavailable. Using sample data for demonstration.")
            return None

# Fallback connection pool class for direct connections
class SimpleDirectConnectionPool:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connections = 0
        self.max_connections = 5
    
    def getconn(self):
        if self.connections >= self.max_connections:
            raise Exception("Connection limit reached")
        self.connections += 1
        return psycopg2.connect(**self.db_config)
    
    def putconn(self, conn):
        conn.close()
        self.connections -= 1
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
# Database connection function with connection pool and retry logic
def get_db_connection():
    pool = init_db_pool()
    if pool is None:
        return None
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = pool.getconn()
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            return conn
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All connection attempts failed: {e}")
                st.warning(f"Database connection failed: {e}. Using sample data.")
                return None
            time.sleep(1)  # Wait before retrying
    
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

# Input sanitization function
def sanitize_input(user_input):
    return html.escape(user_input.strip())

# Enhanced execute_sql_query with better error handling
# Enhanced execute_sql_query with better error handling and fallback
def execute_sql_query(sql_query):
    conn = get_db_connection()
    
    # If no connection, use sample data
    if conn is None:
        logger.info("Using sample data due to connection issues")
        return execute_sql_query_on_sample(sql_query)
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        logger.info(f"Query executed successfully, returned {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        st.error(f"Error executing SQL query: {e}")
        
        # Provide helpful suggestions based on error type
        if "syntax" in str(e).lower():
            st.info("Try simplifying your query or check for syntax errors")
        elif "connection" in str(e).lower():
            st.warning("Database connection issue. Using sample data.")
            return execute_sql_query_on_sample(sql_query)
        
        # Return connection to pool in case of error
        pool = init_db_pool()
        if pool and conn:
            try:
                pool.putconn(conn)
            except:
                pass
                
        return execute_sql_query_on_sample(sql_query)
    finally:
        # Always try to return connection to pool
        pool = init_db_pool()
        if pool and conn:
            try:
                pool.putconn(conn)
            except:
                pass

# Execute query on sample data when DB is unavailable
def execute_sql_query_on_sample(sql_query):
    df = get_sample_argo_data()
    
    # Simple query simulation for common patterns
    try:
        query_lower = sql_query.lower()
        
        # Handle WHERE clauses
        if "where" in query_lower:
            # Temperature conditions
            if "temperature" in query_lower:
                if ">" in query_lower:
                    match = re.search(r'temperature\s*>\s*(\d+(?:\.\d+)?)', query_lower)
                    if match:
                        temp_threshold = float(match.group(1))
                        df = df[df['temperature'] > temp_threshold]
                elif "<" in query_lower:
                    match = re.search(r'temperature\s*<\s*(\d+(?:\.\d+)?)', query_lower)
                    if match:
                        temp_threshold = float(match.group(1))
                        df = df[df['temperature'] < temp_threshold]
            
            # Salinity conditions
            if "salinity" in query_lower:
                if ">" in query_lower:
                    match = re.search(r'salinity\s*>\s*(\d+(?:\.\d+)?)', query_lower)
                    if match:
                        sal_threshold = float(match.group(1))
                        df = df[df['salinity'] > sal_threshold]
                elif "<" in query_lower:
                    match = re.search(r'salinity\s*<\s*(\d+(?:\.\d+)?)', query_lower)
                    if match:
                        sal_threshold = float(match.group(1))
                        df = df[df['salinity'] < sal_threshold]
            
            # Time conditions
            if "recent" in query_lower or "last" in query_lower:
                days_match = re.search(r'last\s+(\d+)\s+days?', query_lower)
                if days_match:
                    days = int(days_match.group(1))
                else:
                    days = 7  # Default to 7 days
                df = df[df['measurement_time'] > (datetime.now() - timedelta(days=days))]
        
        # Handle ORDER BY
        if "order by" in query_lower:
            if "temperature" in query_lower and "desc" in query_lower:
                df = df.sort_values('temperature', ascending=False)
            elif "temperature" in query_lower:
                df = df.sort_values('temperature', ascending=True)
            elif "salinity" in query_lower and "desc" in query_lower:
                df = df.sort_values('salinity', ascending=False)
            elif "salinity" in query_lower:
                df = df.sort_values('salinity', ascending=True)
            elif "measurement_time" in query_lower and "desc" in query_lower:
                df = df.sort_values('measurement_time', ascending=False)
            elif "measurement_time" in query_lower:
                df = df.sort_values('measurement_time', ascending=True)
        
        # Handle LIMIT
        limit_match = re.search(r'limit\s+(\d+)', query_lower)
        if limit_match:
            limit = int(limit_match.group(1))
            df = df.head(limit)
        else:
            df = df.head(100)  # Default limit for sample data
            
    except Exception as e:
        logger.error(f"Error simulating query on sample data: {e}")
        # Return limited sample data as fallback
        return df.head(100)
    
    return df

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

# Add specialized visualization functions
def create_ts_diagram(df):
    """Create Temperature-Salinity diagram for water mass analysis"""
    if 'temperature' not in df.columns or 'salinity' not in df.columns:
        return None
    
    fig = px.scatter(
        df, x='salinity', y='temperature',
        color='pressure' if 'pressure' in df.columns else None,
        title="Temperature-Salinity Diagram",
        labels={'salinity': 'Salinity (PSU)', 'temperature': 'Temperature (°C)'},
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_vertical_profile(df, parameter='temperature'):
    """Create vertical profile of a parameter"""
    if parameter not in df.columns or 'pressure' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # Group by platform for different profiles
    for platform in df['platform_number'].unique()[:10]:  # Show top 10 platforms
        platform_data = df[df['platform_number'] == platform]
        fig.add_trace(go.Scatter(
            x=platform_data[parameter],
            y=platform_data['pressure'],
            mode='lines+markers',
            name=f'Float {platform}',
            line=dict(width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title=f"Vertical Profile of {parameter.capitalize()}",
        xaxis_title=parameter.capitalize(),
        yaxis_title="Pressure (dbar)",
        yaxis=dict(autorange='reversed'),  # Depth increases downward
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
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

# Function to display dataframe with pagination
def display_dataframe_with_pagination(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
    gridOptions = gb.build()
    
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, height=400)

# Cached and rate-limited version of process_user_query
@lru_cache(maxsize=100)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def process_user_query_cached(user_query, openai_key=None):
    # Add a small delay to prevent rate limiting
    time.sleep(0.5)
    return process_user_query(user_query, openai_key)

def process_user_query(user_query, openai_key=None):
    try:
        # Initialize the assistant if not already in session state
        if 'assistant' not in st.session_state:
            st.session_state.assistant = ArgoAIIntelligence()
        
        assistant = st.session_state.assistant
        
        # Generate enhanced query
        query_result = assistant.advanced_nlp_to_sql(user_query, openai_key)
        sql_query = query_result['sql']
        analysis_type = query_result['analysis_type']
        interpretation = query_result['query_interpretation']
        
        # Execute query using your existing execute_sql_query function
        df = execute_sql_query(sql_query)
        
        if df is None or df.empty:
            st.warning("No data found for your query.")
            return None, None, None, None
        
        return interpretation, df, sql_query, analysis_type
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        st.error(f"Error processing request: {str(e)}")
        return None, None, None, None

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
    
    if 'assistant' not in st.session_state:
        st.session_state.assistant = ArgoAIIntelligence()
    
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
    st.markdown('<div class="panel-title"> AI-Powered Query Interface</div>', unsafe_allow_html=True)
    
    # Query input with tooltip
    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input(
    label="",
    placeholder="e.g., Show temperature profiles near Chennai",
    key="main_query",
    label_visibility="collapsed"
)
    
    with col2:
        execute_query = st.button("🔍 ", key="execute_main", help="Execute your query")
    
    # Sample queries (matching original design)
    st.markdown("**Sample Queries:**")
    
    sample_queries = [
        "Show floats near Arabian Sea",
        "Salinity < 35 PSU",
        "Find where temperature > 30°C", 
        "What floats are closest to Mumbai?",
        "Recent measurements from last week",
        "Find thermocline depth in Bay of Bengal",
        "Compare water masses in different ocean regions",
        "Show monsoon effects on surface temperature",
        "show floats near chennai"
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
    
    # Add OpenAI API key to sidebar
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        openai_key = st.text_input("OpenAI API Key (optional)", type="password", 
                                  help="Optional for enhanced AI capabilities")
    
    # Process query if submitted
    if execute_query and user_query:
        # Sanitize input
        user_query = sanitize_input(user_query)
        
        # Add to query history
        st.session_state.query_history.append({
            'query': user_query,
            'timestamp': datetime.now()
        })
        
        # Process query with caching (pass openai_key)
        natural_response, df, sql_query, analysis_type = process_user_query_cached(user_query, openai_key)
        
        # Store analysis_type in session state for later use
        if analysis_type:
            st.session_state.last_analysis_type = analysis_type
        
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
                    # Temperature-Salinity diagram
                    if 'temperature' in df.columns and 'salinity' in df.columns:
                        st.subheader("Water Mass Analysis (T-S Diagram)")
                        ts_fig = create_ts_diagram(df)
                        if ts_fig:
                            st.plotly_chart(ts_fig, use_container_width=True)
                    
                    # Vertical profiles for different parameters
                    profile_params = st.multiselect(
                        "Select parameters for vertical profiles:",
                        ['temperature', 'salinity', 'oxygen', 'chlorophyll', 'nitrate'],
                        default=['temperature', 'salinity']
                    )
                    
                    for param in profile_params:
                        if param in df.columns:
                            st.subheader(f"Vertical Profile of {param.capitalize()}")
                            profile_fig = create_vertical_profile(df, param)
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
                        if 'temperature' in df.columns and 'measurement_time' in df.columns:
    # Make sure measurement_time is datetime
                            df['measurement_time'] = pd.to_datetime(df['measurement_time'], errors='coerce')

                            # Build aggregation dictionary dynamically
                            agg_dict = {'temperature': 'mean'}
                            if 'salinity' in df.columns:
                                agg_dict['salinity'] = 'mean'

                            # Group by date and aggregate
                            daily_data = (
                                df.groupby(df['measurement_time'].dt.date)
                                .agg(agg_dict)
                                .reset_index()
                                .rename(columns={'measurement_time': 'date'})  # optional rename
                            )

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
            - "Find thermocline depth in Bay of Bengal"
            - "Compare water masses in different regions"
            - "Show monsoon effects on surface temperature"
            """)

if __name__ == "__main__":
    main()
