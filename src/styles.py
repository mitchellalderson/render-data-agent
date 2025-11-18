"""Custom CSS styles matching Render.com design."""


def get_render_css() -> str:
    """
    Get custom CSS styles matching Render.com aesthetic.
    
    Returns:
        CSS string to inject into Streamlit app
    """
    return """
    <style>
    /* Import Inter font (similar to Render's font) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background-color: #FAFAFA;
    }
    
    /* Headers */
    h1 {
        font-weight: 700;
        font-size: 3rem;
        line-height: 1.2;
        color: #0A0A0A;
        margin-bottom: 1rem;
    }
    
    h2 {
        font-weight: 600;
        font-size: 2rem;
        color: #0A0A0A;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-weight: 600;
        font-size: 1.5rem;
        color: #0A0A0A;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E5E5;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0A0A0A;
    }
    
    /* Primary button styling (Render's black button) */
    .stButton > button {
        background-color: #0A0A0A;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background-color: #2A2A2A;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        color: #0A0A0A;
        border: 1px solid #D4D4D4;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #F5F5F5;
        border-color: #A3A3A3;
    }
    
    /* Purple accent for special elements */
    .purple-accent {
        color: #A855F7;
        font-weight: 600;
    }
    
    /* Card-like containers */
    .element-container {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #0A0A0A;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #737373;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #D4D4D4;
        border-radius: 8px;
        padding: 2rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #A855F7;
        background-color: #FAFAFA;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #E5E5E5;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .dataframe thead th {
        background-color: #FAFAFA;
        color: #0A0A0A;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 0.75rem;
    }
    
    .dataframe tbody td {
        padding: 0.75rem;
        border-top: 1px solid #F5F5F5;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 6px;
        font-weight: 500;
        color: #0A0A0A;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #FAFAFA;
        border-color: #D4D4D4;
    }
    
    /* Success/Info/Warning/Error message styling */
    .stSuccess {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        color: #166534;
    }
    
    .stInfo {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        color: #1E40AF;
    }
    
    .stWarning {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        color: #92400E;
    }
    
    .stError {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        color: #991B1B;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: #737373;
        font-weight: 500;
        padding: 0.75rem 1rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #0A0A0A;
        border-bottom-color: #D4D4D4;
    }
    
    .stTabs [aria-selected="true"] {
        color: #0A0A0A;
        border-bottom-color: #A855F7;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #A855F7;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 1px solid #D4D4D4;
        border-radius: 6px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #A855F7;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
        background-color: #F3E8FF;
        color: #7C3AED;
    }
    
    /* Separator line */
    hr {
        border: none;
        border-top: 1px solid #E5E5E5;
        margin: 2rem 0;
    }
    </style>
    """


def render_header() -> str:
    """
    Get HTML for the app header with Render-style branding.
    
    Returns:
        HTML string for the header
    """
    return """
    <div style="padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem;">
            <span style="background: linear-gradient(135deg, #A855F7 0%, #7C3AED 100%); 
                         -webkit-background-clip: text; 
                         -webkit-text-fill-color: transparent;">
                ICP Analysis Dashboard
            </span>
        </h1>
        <p style="font-size: 1.125rem; color: #737373; margin: 0;">
            Compare user signups with customer data to identify your ideal customer profile
        </p>
    </div>
    """


def render_section_header(title: str, description: str = "") -> str:
    """
    Get HTML for a section header.
    
    Args:
        title: Section title
        description: Optional description text
        
    Returns:
        HTML string for the section header
    """
    desc_html = f'<p style="color: #737373; margin-top: 0.5rem;">{description}</p>' if description else ""
    
    return f"""
    <div style="margin: 2rem 0 1rem 0;">
        <h2>{title}</h2>
        {desc_html}
    </div>
    """

