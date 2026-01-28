"""
UI Styles and Theme Management.
"""
import streamlit as st

def get_main_css() -> str:
    """Get global CSS styles."""
    return """
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Metric cards with dynamic colors */
    .metric-low {
        background: linear-gradient(135deg, #1a472a 0%, #2d5016 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #2d5016;
    }
    .metric-medium {
        background: linear-gradient(135deg, #5c4a1f 0%, #6b5b1f 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #6b5b1f;
    }
    .metric-high {
        background: linear-gradient(135deg, #5c1a1a 0%, #6b1f1f 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #6b1f1f;
    }
    
    /* Risk badge */
    .risk-badge {
        font-size: 0.9rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
    }
    .risk-high { background: #dc3545; color: white; }
    .risk-medium { background: #ffc107; color: black; }
    .risk-low { background: #28a745; color: white; }
    
    /* Analysis section */
    .analysis-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4a90d9;
    }
    
    /* Streaming text animation */
    .streaming-text {
        border-left: 3px solid #4a90d9;
        padding-left: 1rem;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { border-left-color: #4a90d9; }
        50% { border-left-color: #1a5490; }
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        padding: 1rem;
    }
</style>
"""


def apply_theme_css(is_dark: bool):
    """Apply dynamic theme CSS based on user selection."""
    if is_dark:
        theme_css = """
        <style>
            /* Dark Theme (default Streamlit dark) */
            .stApp { background-color: #0e1117; }
            .analysis-section { background: rgba(255, 255, 255, 0.05); }
        </style>
        """
    else:
        theme_css = """
        <style>
            /* Light Theme */
            .stApp { background-color: #ffffff; color: #1e1e1e; }
            .stMarkdown, .stText, p, span, label { color: #1e1e1e !important; }
            h1, h2, h3, h4, h5, h6 { color: #1a1a2e !important; }
            .analysis-section { 
                background: rgba(0, 0, 0, 0.03); 
                border-left: 4px solid #4a90d9;
            }
            .stTextArea textarea { 
                background-color: #f8f9fa !important; 
                color: #1e1e1e !important;
            }
            .stButton > button {
                background-color: #4a90d9 !important;
                color: white !important;
            }
            /* Sidebar light */
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6 !important;
            }
            section[data-testid="stSidebar"] * {
                color: #1e1e1e !important;
            }
        </style>
        """
    st.markdown(theme_css, unsafe_allow_html=True)
