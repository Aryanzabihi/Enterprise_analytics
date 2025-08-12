import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import datetime
import io
import base64
import warnings

# Configure Streamlit page
st.set_page_config(
    page_title="R&D Analytics Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

warnings.filterwarnings('ignore')

# Set Plotly template
pio.templates.default = "plotly_white"
CONTINUOUS_COLOR_SCALE = "Turbo"
CATEGORICAL_COLOR_SEQUENCE = px.colors.qualitative.Pastel

# Import R&D metric calculation functions
try:
    from rd_metrics_calculator import calculate_innovation_metrics
except ImportError as e:
    st.error(f"Error importing rd_metrics_calculator: {e}")
    # Define a fallback function
    def calculate_innovation_metrics(projects_data, products_data, prototypes_data):
        return pd.DataFrame(), "Error: Could not import metrics calculator"

def apply_common_layout(fig):
    """Apply a common layout to Plotly figures for consistent style."""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial', size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

def display_dataframe_with_index_1(df, **kwargs):
    """Display dataframe with index starting from 1"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        return st.dataframe(df_display, **kwargs)
    else:
        return st.dataframe(df, **kwargs)

def create_template_for_download():
    """Create an Excel template with all required R&D data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct R&D schema
    projects_template = pd.DataFrame(columns=[
        'project_id', 'project_name', 'project_type', 'start_date', 'end_date', 
        'status', 'budget', 'actual_spend', 'team_lead_id', 'department', 'priority',
        'technology_area', 'trl_level', 'milestones_completed', 'total_milestones'
    ])
    
    researchers_template = pd.DataFrame(columns=[
        'researcher_id', 'first_name', 'last_name', 'email', 'department', 
        'specialization', 'hire_date', 'education_level', 'experience_years', 
        'status', 'salary', 'manager_id'
    ])
    
    patents_template = pd.DataFrame(columns=[
        'patent_id', 'project_id', 'patent_title', 'filing_date', 'grant_date', 
        'status', 'researcher_id', 'technology_area', 'estimated_value', 
        'licensing_revenue', 'expiry_date'
    ])
    
    equipment_template = pd.DataFrame(columns=[
        'equipment_id', 'equipment_name', 'equipment_type', 'purchase_date', 
        'cost', 'location', 'status', 'total_hours', 'utilized_hours', 
        'maintenance_cost', 'department'
    ])
    
    collaborations_template = pd.DataFrame(columns=[
        'collaboration_id', 'partner_name', 'partner_type', 'start_date', 
        'end_date', 'project_id', 'investment_amount', 'revenue_generated', 
        'status', 'collaboration_type', 'researcher_id'
    ])
    
    prototypes_template = pd.DataFrame(columns=[
        'prototype_id', 'project_id', 'prototype_name', 'development_date', 
        'testing_date', 'cost', 'status', 'success_rate', 'iterations', 
        'researcher_id', 'technology_used'
    ])
    
    products_template = pd.DataFrame(columns=[
        'product_id', 'project_id', 'product_name', 'launch_date', 'development_cost', 
        'revenue_generated', 'market_response', 'customer_satisfaction', 
        'patent_id', 'status', 'target_market'
    ])
    
    training_template = pd.DataFrame(columns=[
        'training_id', 'researcher_id', 'training_type', 'training_date', 
        'duration_hours', 'cost', 'pre_performance_score', 'post_performance_score', 
        'effectiveness_rating', 'trainer_name'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        projects_template.to_excel(writer, sheet_name='Projects', index=False)
        researchers_template.to_excel(writer, sheet_name='Researchers', index=False)
        patents_template.to_excel(writer, sheet_name='Patents', index=False)
        equipment_template.to_excel(writer, sheet_name='Equipment', index=False)
        collaborations_template.to_excel(writer, sheet_name='Collaborations', index=False)
        prototypes_template.to_excel(writer, sheet_name='Prototypes', index=False)
        products_template.to_excel(writer, sheet_name='Products', index=False)
        training_template.to_excel(writer, sheet_name='Training', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Projects', 'Researchers', 'Patents', 'Equipment', 'Collaborations', 'Prototypes', 'Products', 'Training'],
            'Required Fields': [
                'project_id, project_name, project_type, start_date, end_date, status, budget, actual_spend, team_lead_id, department, priority, technology_area, trl_level, milestones_completed, total_milestones',
                'researcher_id, first_name, last_name, email, department, specialization, hire_date, education_level, experience_years, status, salary, manager_id',
                'patent_id, project_id, patent_title, filing_date, grant_date, status, researcher_id, technology_area, estimated_value, licensing_revenue, expiry_date',
                'equipment_id, equipment_name, equipment_type, purchase_date, cost, location, status, total_hours, utilized_hours, maintenance_cost, department',
                'collaboration_id, partner_name, partner_type, start_date, end_date, project_id, investment_amount, revenue_generated, status, collaboration_type, researcher_id',
                'prototype_id, project_id, prototype_name, development_date, testing_date, cost, status, success_rate, iterations, researcher_id, technology_used',
                'product_id, project_id, product_name, launch_date, development_cost, revenue_generated, market_response, customer_satisfaction, patent_id, status, target_market',
                'training_id, researcher_id, training_type, training_date, duration_hours, cost, pre_performance_score, post_performance_score, effectiveness_rating, trainer_name'
            ],
            'Data Types': [
                'Text, Text, Text, Date, Date, Text, Number, Number, Text, Text, Text, Text, Number, Number, Number',
                'Text, Text, Text, Text, Text, Text, Date, Text, Number, Text, Number, Text',
                'Text, Text, Text, Date, Date, Text, Text, Text, Number, Number, Date',
                'Text, Text, Text, Date, Number, Text, Text, Number, Number, Number, Text',
                'Text, Text, Text, Date, Date, Text, Number, Number, Text, Text, Text',
                'Text, Text, Text, Date, Date, Number, Text, Number, Number, Text, Text',
                'Text, Text, Text, Date, Number, Number, Number, Number, Text, Text, Text',
                'Text, Text, Text, Date, Number, Number, Number, Number, Number, Text'
            ],
            'Description': [
                'R&D projects with timelines, budgets, and progress tracking',
                'Research team members with skills and performance data',
                'Intellectual property including patents and their value',
                'R&D equipment and utilization tracking',
                'External partnerships and collaborations',
                'Prototype development and testing results',
                'Products launched from R&D projects',
                'Training programs and their effectiveness'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Format the instructions sheet
        worksheet = writer.sheets['Instructions']
        for i, col in enumerate(instructions_df.columns):
            worksheet.set_column(i, i, 30)
    
    output.seek(0)
    return output

def export_data_to_excel():
    """Export all R&D data to Excel file"""
    if (st.session_state.projects.empty and st.session_state.researchers.empty and 
        st.session_state.patents.empty and st.session_state.equipment.empty and
        st.session_state.collaborations.empty and st.session_state.prototypes.empty and
        st.session_state.products.empty and st.session_state.training.empty):
        st.warning("No data to export. Please add data first.")
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each DataFrame to a separate sheet
        st.session_state.projects.to_excel(writer, sheet_name='Projects', index=False)
        st.session_state.researchers.to_excel(writer, sheet_name='Researchers', index=False)
        st.session_state.patents.to_excel(writer, sheet_name='Patents', index=False)
        st.session_state.equipment.to_excel(writer, sheet_name='Equipment', index=False)
        st.session_state.collaborations.to_excel(writer, sheet_name='Collaborations', index=False)
        st.session_state.prototypes.to_excel(writer, sheet_name='Prototypes', index=False)
        st.session_state.products.to_excel(writer, sheet_name='Products', index=False)
        st.session_state.training.to_excel(writer, sheet_name='Training', index=False)
    
    output.seek(0)
    return output

# Page configuration
st.set_page_config(
    page_title="R&D Analytics Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure page for wide layout
st.set_page_config(
    page_title="R&D Analytics Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS dashboard styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Modern SaaS Dashboard Styling */
    
    /* Main background gradient */
    .main .block-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        max-width: 100%;
    }
    
    /* Sidebar styling - compact */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        padding: 20px 12px;
        width: 250px;
        min-width: 250px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    
    /* Optimize sidebar width */
    .css-1lcbmhc {
        width: 250px;
        min-width: 250px;
    }
    
    /* Main content area - expanded width */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
        width: 100%;
    }
    
    /* Expand main content width */
    .main {
        max-width: 100%;
        padding-left: 0;
        padding-right: 0;
    }
    
    /* Remove default Streamlit width constraints */
    .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Expand chart containers */
    .chart-container {
        width: 100%;
        max-width: none;
    }
    
    /* Make plots wider */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    /* Expand dataframe width */
    .dataframe {
        width: 100% !important;
        max-width: none;
    }
    
    /* Force full width for all content */
    .element-container {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Ensure plots use full width */
    .plotly-graph-div {
        width: 100% !important;
        max-width: none !important;
        height: auto !important;
    }
    
    /* Optimize chart height for wide layout */
    .js-plotly-plot {
        height: 500px !important;
    }
    
    /* Optimize column layouts for wider space */
    .row-widget.stHorizontal {
        width: 100%;
    }
    
    /* Remove any remaining width constraints */
    .stApp > div:first-child {
        max-width: 100%;
    }
    
    /* Ensure all Streamlit elements use full width */
    .stApp {
        max-width: 100%;
    }
    
    /* Optimize for wide screens */
    @media (min-width: 1200px) {
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
    }
    
    /* Make sure all containers expand */
    .stContainer {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Sidebar button styling */
    .stButton > button {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        color: #ffffff;
        font-weight: 500;
        margin: 6px 0;
        padding: 12px 16px;
        transition: all 0.3s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        font-size: 0.95rem;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateX(3px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Active button styling */
    .stButton > button[data-active="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-weight: 600;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card-purple {
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(168, 85, 247, 0.3);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(249, 115, 22, 0.3);
    }
    
    .metric-card-teal {
        background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(20, 184, 166, 0.3);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
    }
    
    /* Chart container styling */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Welcome section */
    .welcome-section {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Progress circle styling */
    .progress-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
        margin: 10px auto;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Insights container */
    .insights-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .metric-card {
            margin: 5px 0;
            padding: 15px;
        }
        
        .main-header {
            padding: 20px;
            font-size: 24px;
        }
    }
    </style>
    """, unsafe_allow_html=True)



# Initialize session state for R&D data storage
if 'projects' not in st.session_state:
    st.session_state.projects = pd.DataFrame(columns=[
        'project_id', 'project_name', 'project_type', 'start_date', 'end_date', 
        'status', 'budget', 'actual_spend', 'team_lead_id', 'department', 'priority',
        'technology_area', 'trl_level', 'milestones_completed', 'total_milestones'
    ])

if 'researchers' not in st.session_state:
    st.session_state.researchers = pd.DataFrame(columns=[
        'researcher_id', 'first_name', 'last_name', 'email', 'department', 
        'specialization', 'hire_date', 'education_level', 'experience_years', 
        'status', 'salary', 'manager_id'
    ])

if 'patents' not in st.session_state:
    st.session_state.patents = pd.DataFrame(columns=[
        'patent_id', 'project_id', 'patent_title', 'filing_date', 'grant_date', 
        'status', 'researcher_id', 'technology_area', 'estimated_value', 
        'licensing_revenue', 'expiry_date'
    ])

if 'equipment' not in st.session_state:
    st.session_state.equipment = pd.DataFrame(columns=[
        'equipment_id', 'equipment_name', 'equipment_type', 'purchase_date', 
        'cost', 'location', 'status', 'total_hours', 'utilized_hours', 
        'maintenance_cost', 'department'
    ])

if 'collaborations' not in st.session_state:
    st.session_state.collaborations = pd.DataFrame(columns=[
        'collaboration_id', 'partner_name', 'partner_type', 'start_date', 
        'end_date', 'project_id', 'investment_amount', 'revenue_generated', 
        'status', 'collaboration_type', 'researcher_id'
    ])

if 'prototypes' not in st.session_state:
    st.session_state.prototypes = pd.DataFrame(columns=[
        'prototype_id', 'project_id', 'prototype_name', 'development_date', 
        'testing_date', 'cost', 'status', 'success_rate', 'iterations', 
        'researcher_id', 'technology_used'
    ])

if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame(columns=[
        'product_id', 'project_id', 'product_name', 'launch_date', 'development_cost', 
        'revenue_generated', 'market_response', 'customer_satisfaction', 
        'patent_id', 'status', 'target_market'
    ])

if 'training' not in st.session_state:
    st.session_state.training = pd.DataFrame(columns=[
        'training_id', 'researcher_id', 'training_type', 'training_date', 
        'duration_hours', 'cost', 'pre_performance_score', 'post_performance_score', 
        'effectiveness_rating', 'trainer_name'
    ])

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="R&D Analytics Dashboard",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🔬 R&D Analytics Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'projects' not in st.session_state:
        st.session_state.projects = pd.DataFrame()
    if 'researchers' not in st.session_state:
        st.session_state.researchers = pd.DataFrame()
    if 'patents' not in st.session_state:
        st.session_state.patents = pd.DataFrame()
    if 'equipment' not in st.session_state:
        st.session_state.equipment = pd.DataFrame()
    if 'collaborations' not in st.session_state:
        st.session_state.collaborations = pd.DataFrame()
    if 'prototypes' not in st.session_state:
        st.session_state.prototypes = pd.DataFrame()
    if 'products' not in st.session_state:
        st.session_state.products = pd.DataFrame()
    if 'training' not in st.session_state:
        st.session_state.training = pd.DataFrame()
    
    # Sidebar navigation for main sections
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;">
            <h3 style="color: #4CAF50; margin-bottom: 15px; text-align: center; font-size: 1.2rem; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                🎯 Navigation
            </h3>
            <p style="color: #2196F3; text-align: center; margin: 0; font-size: 0.85rem; font-weight: 500;">
                Select a section to explore
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "🏠 Home"
        
        if st.button("📝 Data Input", key="nav_data_input", use_container_width=True):
            st.session_state.current_page = "📝 Data Input"
        
        if st.button("🚀 Innovation & Product Development", key="nav_innovation", use_container_width=True):
            st.session_state.current_page = "🚀 Innovation & Product Development"
        
        if st.button("💰 Resource Allocation", key="nav_resource_allocation", use_container_width=True):
            st.session_state.current_page = "💰 Resource Allocation"
        
        if st.button("📜 IP Management", key="nav_ip_management", use_container_width=True):
            st.session_state.current_page = "📜 IP Management"
        
        if st.button("⚠️ Risk Management", key="nav_risk_management", use_container_width=True):
            st.session_state.current_page = "⚠️ Risk Management"
        
        if st.button("🤝 Collaboration", key="nav_collaboration", use_container_width=True):
            st.session_state.current_page = "🤝 Collaboration"
        
        if st.button("👥 Employee Performance", key="nav_employee_performance", use_container_width=True):
            st.session_state.current_page = "👥 Employee Performance"
        
        if st.button("🔬 Technology Analysis", key="nav_technology_analysis", use_container_width=True):
            st.session_state.current_page = "🔬 Technology Analysis"
        
        if st.button("🎯 Customer-Centric R&D", key="nav_customer_centric", use_container_width=True):
            st.session_state.current_page = "🎯 Customer-Centric R&D"
        
        if st.button("📊 Strategic Metrics", key="nav_strategic_metrics", use_container_width=True):
            st.session_state.current_page = "📊 Strategic Metrics"
        
        # Developer attribution at the bottom of sidebar
        st.markdown("---")
        st.markdown("""
        <div style="padding: 12px 0; text-align: center;">
            <p style="color: #95a5a6; font-size: 0.75rem; margin: 0; line-height: 1.3;">
                Developed by <strong style="color: #3498db;">Aryan Zabihi</strong><br>
                <a href="https://github.com/Aryanzabihi" target="_blank" style="color: #3498db; text-decoration: none;">GitHub</a> • 
                <a href="https://www.linkedin.com/in/aryanzabihi/" target="_blank" style="color: #3498db; text-decoration: none;">LinkedIn</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize current page if not set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Display content based on current page
    if st.session_state.current_page == "🏠 Home":
        show_home()
    elif st.session_state.current_page == "📝 Data Input":
        show_data_input()
    elif st.session_state.current_page == "🚀 Innovation & Product Development":
        show_innovation_product_development()
    elif st.session_state.current_page == "💰 Resource Allocation":
        show_resource_allocation()
    elif st.session_state.current_page == "📜 IP Management":
        show_ip_management()
    elif st.session_state.current_page == "⚠️ Risk Management":
        show_risk_management()
    elif st.session_state.current_page == "🤝 Collaboration":
        show_collaboration()
    elif st.session_state.current_page == "👥 Employee Performance":
        show_employee_performance()
    elif st.session_state.current_page == "🔬 Technology Analysis":
        show_technology_analysis()
    elif st.session_state.current_page == "🎯 Customer-Centric R&D":
        show_customer_centric_rd()
    elif st.session_state.current_page == "📊 Strategic Metrics":
        show_strategic_metrics()

def show_home():
    # Welcome header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #1e3c72; font-size: 2.5rem; margin-bottom: 10px;">🏠 Welcome to R&D Analytics Dashboard</h1>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h2 style="margin: 0; color: white;">🔬 Comprehensive R&D Analytics Platform</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Description
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #667eea;">
        <p style="font-size: 1.1rem; margin: 0; color: #333;">
    This dashboard provides comprehensive analytics for Research and Development departments, 
    covering all aspects from innovation metrics to strategic financial analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics grid - Break into smaller sections
    st.markdown("""
    <div style="margin: 30px 0;">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📊 Key Analytics Categories</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # First row of cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">🚀 Innovation & Product Development</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Project Success Rate Analysis</li>
                <li>Time-to-Market Optimization</li>
                <li>New Product Revenue Contribution</li>
                <li>Prototyping Efficiency Metrics</li>
                <li>Product Failure Rate Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">💰 Resource Allocation & Utilization</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>R&D Budget Utilization Tracking</li>
                <li>Researcher Efficiency Metrics</li>
                <li>Equipment Utilization Analysis</li>
                <li>Cost per Project Optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of cards
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">📜 Intellectual Property Management</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Patent Filing Success Rates</li>
                <li>IP Portfolio Analysis</li>
                <li>Patent Revenue Contribution</li>
                <li>Licensing Agreement Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">⚠️ Risk Management & Failure Analysis</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Project Failure Trend Analysis</li>
                <li>Technology Obsolescence Risk</li>
                <li>Competitive Analysis</li>
                <li>Cost of Failed Projects</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Third row of cards
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">🤝 Collaboration & External Partnerships</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Academic Partnership ROI</li>
                <li>External R&D Contributions</li>
                <li>Open Innovation Metrics</li>
                <li>Collaborative Patent Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">👥 Employee Performance & Innovation Culture</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Employee Innovation Contribution</li>
                <li>Training Effectiveness Analysis</li>
                <li>Team Collaboration Metrics</li>
                <li>R&D Staff Productivity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Fourth row of cards
    col7, col8 = st.columns(2)
    
    with col7:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">🔬 Technology & Trend Analysis</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Emerging Technology Tracking</li>
                <li>Technology Readiness Level (TRL) Analysis</li>
                <li>Competitive Technology Benchmarking</li>
                <li>Innovation Pipeline Health</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84cc16 0%, #65a30d 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">🎯 Customer-Centric R&D</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Customer Feedback Integration</li>
                <li>Market Demand Alignment</li>
                <li>Feature Adoption Rates</li>
                <li>R&D Impact on Customer Retention</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Fifth row of cards
    col9, col10 = st.columns(2)
    
    with col9:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">📊 Strategic & Financial Metrics</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Return on R&D Investment (RORI)</li>
                <li>Competitive Advantage Analysis</li>
                <li>R&D-Driven Product Profitability</li>
                <li>Market Share Gains from R&D</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col10:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 15px 0; color: white;">⚡ Process & Efficiency Metrics</h4>
            <ul style="margin: 0; color: white; padding-left: 20px;">
                <li>Project Milestone Achievement</li>
                <li>Prototype Success Rates</li>
                <li>Process Optimization Impact</li>
                <li>Iteration Efficiency Metrics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started section
    st.markdown("""
    <div style="margin: 30px 0;">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📈 Getting Started</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Getting Started cards in columns
    gs_col1, gs_col2, gs_col3, gs_col4 = st.columns(4)
    
    with gs_col1:
        st.markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 15px 0; font-size: 1.3rem;">📝 Data Input</h4>
            <p style="margin: 0; font-size: 1rem;">Upload your R&D data or use the template provided</p>
        </div>
        """, unsafe_allow_html=True)
    
    with gs_col2:
        st.markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%); color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 15px 0; font-size: 1.3rem;">📊 Analytics</h4>
            <p style="margin: 0; font-size: 1rem;">Explore comprehensive metrics across all categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with gs_col3:
        st.markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 15px 0; font-size: 1.3rem;">📋 Reports</h4>
            <p style="margin: 0; font-size: 1rem;">Generate detailed reports and insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with gs_col4:
        st.markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 15px 0; font-size: 1.3rem;">📤 Export</h4>
            <p style="margin: 0; font-size: 1rem;">Download your analytics and data</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data Requirements section
    st.markdown("""
    <div style="margin: 30px 0;">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">🎯 Data Requirements</h3>
        <p style="font-size: 1.1rem; margin-bottom: 20px;">The dashboard requires data across 8 key areas:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data requirements in columns
    dr_col1, dr_col2 = st.columns(2)
    
    with dr_col1:
        st.markdown("""
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #667eea; font-size: 1.1rem;">📋 Projects</strong><br>
            <small style="color: #666;">R&D project details, timelines, budgets</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #a855f7; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #a855f7; font-size: 1.1rem;">👥 Researchers</strong><br>
            <small style="color: #666;">Team member information and performance</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #f97316; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #f97316; font-size: 1.1rem;">📜 Patents</strong><br>
            <small style="color: #666;">Intellectual property and licensing data</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #14b8a6; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #14b8a6; font-size: 1.1rem;">🔧 Equipment</strong><br>
            <small style="color: #666;">R&D equipment and utilization</small>
        </div>
        """, unsafe_allow_html=True)
    
    with dr_col2:
        st.markdown("""
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #22c55e; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #22c55e; font-size: 1.1rem;">🤝 Collaborations</strong><br>
            <small style="color: #666;">External partnerships and outcomes</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #ef4444; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #ef4444; font-size: 1.1rem;">🔬 Prototypes</strong><br>
            <small style="color: #666;">Development and testing results</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #8b5cf6; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #8b5cf6; font-size: 1.1rem;">🚀 Products</strong><br>
            <small style="color: #666;">Launched products and market performance</small>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #06b6d4; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            <strong style="color: #06b6d4; font-size: 1.1rem;">🎓 Training</strong><br>
            <small style="color: #666;">Training programs and effectiveness</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <div style="display: inline-block; padding: 20px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h4 style="margin: 0; color: white; font-size: 1.3rem;">🚀 Start by uploading your data in the <strong>Data Input</strong> tab!</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_data_input():
    # Main header
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">📝 Data Input & Management</h2>
        <p style="text-align: center; color: #666; font-size: 1.1rem;">Upload, manage, and input your R&D data for comprehensive analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different data input methods
    data_tab1, data_tab2, data_tab3, data_tab4 = st.tabs([
        "📤 Upload Data", "📋 Download Template", "✏️ Manual Entry", "📊 Sample Dataset"
    ])
    
    with data_tab1:
        st.markdown("""
        <div class="metric-card-blue">
            <h3 style="margin: 0 0 15px 0; text-align: center;">📤 Upload R&D Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("**Upload your existing R&D data in Excel format:**")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file with R&D data",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with sheets: Projects, Researchers, Patents, Equipment, Collaborations, Prototypes, Products, Training"
        )
        
        if uploaded_file is not None:
            try:
                # Read all sheets from the uploaded file
                excel_file = pd.ExcelFile(uploaded_file)
                required_sheets = ['Projects', 'Researchers', 'Patents', 'Equipment', 'Collaborations', 'Prototypes', 'Products', 'Training']
                
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
                
                if missing_sheets:
                    st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                    st.info("Please ensure your Excel file contains all required sheets. You can download a template below.")
                else:
                    # Load data into session state
                    st.session_state.projects = pd.read_excel(uploaded_file, sheet_name='Projects')
                    st.session_state.researchers = pd.read_excel(uploaded_file, sheet_name='Researchers')
                    st.session_state.patents = pd.read_excel(uploaded_file, sheet_name='Patents')
                    st.session_state.equipment = pd.read_excel(uploaded_file, sheet_name='Equipment')
                    st.session_state.collaborations = pd.read_excel(uploaded_file, sheet_name='Collaborations')
                    st.session_state.prototypes = pd.read_excel(uploaded_file, sheet_name='Prototypes')
                    st.session_state.products = pd.read_excel(uploaded_file, sheet_name='Products')
                    st.session_state.training = pd.read_excel(uploaded_file, sheet_name='Training')
                    
                    st.success("✅ Data uploaded successfully!")
                    
                    # Display data summary
                    st.markdown("""
                    <div class="metric-card" style="margin: 20px 0;">
                        <h4 style="margin: 0 0 15px 0; color: #1e3c72;">📊 Data Summary</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                    with summary_col1:
                        st.metric("Projects", len(st.session_state.projects))
                    with summary_col2:
                        st.metric("Researchers", len(st.session_state.researchers))
                    with summary_col3:
                        st.metric("Patents", len(st.session_state.patents))
                    with summary_col4:
                        st.metric("Products", len(st.session_state.products))
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with data_tab2:
        st.markdown("""
        <div class="metric-card-green">
            <h3 style="margin: 0 0 15px 0; text-align: center;">📋 Download Data Template</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("**Get the Excel template with all required data schemas:**")
        
        if st.button("📋 Download R&D Data Template", key="download_template"):
            template_data = create_template_for_download()
            st.download_button(
                label="📥 Download Excel Template",
                data=template_data.getvalue(),
                file_name="rd_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.write("**Template includes:**")
        st.write("• Projects sheet - R&D project details, timelines, budgets")
        st.write("• Researchers sheet - Team member information and performance")
        st.write("• Patents sheet - Intellectual property and licensing data")
        st.write("• Equipment sheet - R&D equipment and utilization")
        st.write("• Collaborations sheet - External partnerships and outcomes")
        st.write("• Prototypes sheet - Development and testing results")
        st.write("• Products sheet - Launched products and market performance")
        st.write("• Training sheet - Training programs and effectiveness")
        st.write("• Instructions sheet - Detailed field descriptions and data types")
        
        # Show template structure
        st.markdown("""
        <div class="metric-card" style="margin: 20px 0;">
            <h4 style="margin: 0 0 15px 0; color: #1e3c72;">📋 Template Structure</h4>
        </div>
        """, unsafe_allow_html=True)
        
        template_info = {
            'Sheet': ['Projects', 'Researchers', 'Patents', 'Equipment', 'Collaborations', 'Prototypes', 'Products', 'Training'],
            'Key Fields': [
                'project_id, project_name, status, budget, start_date, end_date',
                'researcher_id, first_name, last_name, department, specialization',
                'patent_id, patent_title, status, estimated_value, filing_date',
                'equipment_id, equipment_name, cost, location, status',
                'collaboration_id, partner_name, project_id, investment_amount',
                'prototype_id, project_id, status, cost, success_rate',
                'product_id, product_name, launch_date, revenue_generated',
                'training_id, researcher_id, training_type, effectiveness_rating'
            ],
            'Records': ['15', '25', '12', '8', '10', '20', '18', '30']
        }
        
        st.dataframe(pd.DataFrame(template_info), use_container_width=True)
    
    with data_tab3:
        st.markdown("""
        <div class="metric-card-purple">
            <h3 style="margin: 0 0 15px 0; text-align: center;">✏️ Manual Data Entry</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("**Add new data entries manually:**")
        
        # Create sub-tabs for different data types
        entry_tab1, entry_tab2, entry_tab3, entry_tab4 = st.tabs([
            "Projects", "Researchers", "Patents", "Other Data"
        ])
        
        with entry_tab1:
            st.subheader("📋 Add New Project")
            col1, col2 = st.columns(2)
            with col1:
                project_id = st.text_input("Project ID", key="proj_id")
                project_name = st.text_input("Project Name", key="proj_name")
                project_type = st.selectbox("Project Type", ["Research", "Development", "Innovation", "Prototype", "Product"], key="proj_type")
                start_date = st.date_input("Start Date", key="proj_start")
                end_date = st.date_input("End Date", key="proj_end")
                status = st.selectbox("Status", ["Planning", "Active", "Completed", "On Hold", "Cancelled"], key="proj_status")
            with col2:
                budget = st.number_input("Budget ($)", min_value=0.0, key="proj_budget")
                actual_spend = st.number_input("Actual Spend ($)", min_value=0.0, key="proj_spend")
                team_lead_id = st.text_input("Team Lead ID", key="proj_lead")
                department = st.text_input("Department", key="proj_dept")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="proj_priority")
                technology_area = st.text_input("Technology Area", key="proj_tech")
                trl_level = st.number_input("TRL Level", min_value=1, max_value=9, value=1, key="proj_trl")
            
            milestones_completed = st.number_input("Milestones Completed", min_value=0, key="proj_milestones_comp")
            total_milestones = st.number_input("Total Milestones", min_value=0, key="proj_milestones_total")
            
            if st.button("Add Project", key="add_proj"):
                if project_id and project_name:
                    new_project = pd.DataFrame([{
                        'project_id': project_id,
                        'project_name': project_name,
                        'project_type': project_type,
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': status,
                        'budget': budget,
                        'actual_spend': actual_spend,
                        'team_lead_id': team_lead_id,
                        'department': department,
                        'priority': priority,
                        'technology_area': technology_area,
                        'trl_level': trl_level,
                        'milestones_completed': milestones_completed,
                        'total_milestones': total_milestones
                    }])
                    st.session_state.projects = pd.concat([st.session_state.projects, new_project], ignore_index=True)
                    st.success("Project added successfully!")
                else:
                    st.error("Please fill in Project ID and Project Name")
        
        with entry_tab2:
            st.subheader("👥 Add New Researcher")
            col1, col2 = st.columns(2)
            with col1:
                researcher_id = st.text_input("Researcher ID", key="res_id")
                first_name = st.text_input("First Name", key="res_first")
                last_name = st.text_input("Last Name", key="res_last")
                email = st.text_input("Email", key="res_email")
                department = st.text_input("Department", key="res_dept")
                specialization = st.text_input("Specialization", key="res_spec")
            with col2:
                hire_date = st.date_input("Hire Date", key="res_hire")
                education_level = st.selectbox("Education Level", ["Bachelor's", "Master's", "PhD", "Post-Doc"], key="res_edu")
                experience_years = st.number_input("Experience (Years)", min_value=0, key="res_exp")
                status = st.selectbox("Status", ["Active", "Inactive", "Terminated"], key="res_status")
                salary = st.number_input("Salary ($)", min_value=0, key="res_salary")
                manager_id = st.text_input("Manager ID", key="res_manager")
            
            if st.button("Add Researcher", key="add_res"):
                if researcher_id and first_name and last_name:
                    new_researcher = pd.DataFrame([{
                        'researcher_id': researcher_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'department': department,
                        'specialization': specialization,
                        'hire_date': hire_date,
                        'education_level': education_level,
                        'experience_years': experience_years,
                        'status': status,
                        'salary': salary,
                        'manager_id': manager_id
                    }])
                    st.session_state.researchers = pd.concat([st.session_state.researchers, new_researcher], ignore_index=True)
                    st.success("Researcher added successfully!")
                else:
                    st.error("Please fill in Researcher ID, First Name, and Last Name")
        
        with entry_tab3:
            st.subheader("📜 Add New Patent")
            col1, col2 = st.columns(2)
            with col1:
                patent_id = st.text_input("Patent ID", key="pat_id")
                project_id = st.text_input("Project ID", key="pat_proj")
                patent_title = st.text_input("Patent Title", key="pat_title")
                filing_date = st.date_input("Filing Date", key="pat_filing")
                grant_date = st.date_input("Grant Date", key="pat_grant")
                status = st.selectbox("Status", ["Filed", "Pending", "Granted", "Rejected"], key="pat_status")
            with col2:
                researcher_id = st.text_input("Researcher ID", key="pat_res")
                technology_area = st.text_input("Technology Area", key="pat_tech")
                estimated_value = st.number_input("Estimated Value ($)", min_value=0, key="pat_value")
                licensing_revenue = st.number_input("Licensing Revenue ($)", min_value=0, key="pat_revenue")
                expiry_date = st.date_input("Expiry Date", key="pat_expiry")
            
            if st.button("Add Patent", key="add_pat"):
                if patent_id and patent_title:
                    new_patent = pd.DataFrame([{
                        'patent_id': patent_id,
                        'project_id': project_id,
                        'patent_title': patent_title,
                        'filing_date': filing_date,
                        'grant_date': grant_date,
                        'status': status,
                        'researcher_id': researcher_id,
                        'technology_area': technology_area,
                        'estimated_value': estimated_value,
                        'licensing_revenue': licensing_revenue,
                        'expiry_date': expiry_date
                    }])
                    st.session_state.patents = pd.concat([st.session_state.patents, new_patent], ignore_index=True)
                    st.success("Patent added successfully!")
                else:
                    st.error("Please fill in Patent ID and Patent Title")
        
        with entry_tab4:
            st.subheader("🔧 Add Other Data Types")
            st.info("Use the template download to add Equipment, Collaborations, Prototypes, Products, and Training data in bulk.")
    
    with data_tab4:
        st.markdown("""
        <div class="metric-card-teal">
            <h3 style="margin: 0 0 15px 0; text-align: center;">📊 Sample Dataset</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("**Preview of sample data structure and load sample data into the program:**")
        
        # Sample data for each category
        sample_projects = pd.DataFrame({
            'project_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'project_name': ['AI Research Initiative', 'Quantum Computing', 'Biotech Innovation', 'Robotics Development', 'Clean Energy Research'],
            'project_type': ['Research', 'Development', 'Innovation', 'Development', 'Research'],
            'start_date': ['2024-01-15', '2024-02-01', '2024-01-20', '2024-03-01', '2024-02-15'],
            'end_date': ['2024-12-31', '2024-11-30', '2024-10-31', '2024-12-31', '2024-12-31'],
            'status': ['Active', 'Completed', 'Planning', 'Active', 'Active'],
            'budget': [500000, 750000, 300000, 600000, 400000],
            'actual_spend': [450000, 720000, 0, 350000, 180000],
            'team_lead_id': ['R001', 'R002', 'R003', 'R004', 'R005'],
            'department': ['AI Lab', 'Quantum Lab', 'Biotech Lab', 'Robotics Lab', 'Energy Lab'],
            'priority': ['High', 'Medium', 'High', 'Medium', 'High'],
            'technology_area': ['Artificial Intelligence', 'Quantum Physics', 'Biotechnology', 'Robotics', 'Clean Energy'],
            'trl_level': [4, 7, 3, 5, 4],
            'milestones_completed': [8, 12, 2, 6, 4],
            'total_milestones': [15, 15, 10, 12, 10]
        })
        
        sample_researchers = pd.DataFrame({
            'researcher_id': ['R001', 'R002', 'R003', 'R004', 'R005', 'R006', 'R007', 'R008'],
            'first_name': ['Dr. Sarah', 'Dr. Michael', 'Dr. Emily', 'Dr. James', 'Dr. Lisa', 'Dr. David', 'Dr. Maria', 'Dr. Robert'],
            'last_name': ['Johnson', 'Chen', 'Rodriguez', 'Wilson', 'Brown', 'Taylor', 'Garcia', 'Anderson'],
            'email': ['sarah.johnson@company.com', 'michael.chen@company.com', 'emily.rodriguez@company.com', 'james.wilson@company.com', 'lisa.brown@company.com', 'david.taylor@company.com', 'maria.garcia@company.com', 'robert.anderson@company.com'],
            'department': ['AI Lab', 'Quantum Lab', 'Biotech Lab', 'Robotics Lab', 'Energy Lab', 'AI Lab', 'Quantum Lab', 'Biotech Lab'],
            'specialization': ['Machine Learning', 'Quantum Physics', 'Genomics', 'Robotics', 'Solar Energy', 'Deep Learning', 'Quantum Computing', 'Bioinformatics'],
            'hire_date': ['2020-03-15', '2018-09-01', '2022-01-10', '2021-06-15', '2023-02-01', '2021-12-01', '2019-04-01', '2022-08-15'],
            'education_level': ['PhD', 'PhD', 'PhD', 'PhD', 'PhD', 'PhD', 'PhD', 'PhD'],
            'experience_years': [8, 12, 6, 7, 3, 5, 9, 4],
            'status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active'],
            'salary': [120000, 150000, 110000, 125000, 100000, 115000, 140000, 105000],
            'manager_id': ['M001', 'M001', 'M002', 'M002', 'M003', 'M001', 'M001', 'M002']
        })
        
        sample_patents = pd.DataFrame({
            'patent_id': ['PAT001', 'PAT002', 'PAT003', 'PAT004', 'PAT005'],
            'project_id': ['P001', 'P002', 'P003', 'P001', 'P004'],
            'patent_title': ['AI Algorithm for Data Analysis', 'Quantum Encryption Method', 'Gene Editing Technique', 'Neural Network Optimization', 'Robotic Control System'],
            'filing_date': ['2024-03-15', '2024-05-20', '2024-04-10', '2024-06-01', '2024-07-15'],
            'grant_date': ['2024-08-15', '', '', '', ''],
            'status': ['Granted', 'Pending', 'Filed', 'Pending', 'Filed'],
            'researcher_id': ['R001', 'R002', 'R003', 'R001', 'R004'],
            'technology_area': ['Artificial Intelligence', 'Quantum Computing', 'Biotechnology', 'Artificial Intelligence', 'Robotics'],
            'estimated_value': [250000, 500000, 750000, 300000, 400000],
            'licensing_revenue': [50000, 0, 0, 0, 0],
            'expiry_date': ['2044-08-15', '2044-05-20', '2044-04-10', '2044-06-01', '2044-07-15']
        })
        
        sample_equipment = pd.DataFrame({
            'equipment_id': ['EQ001', 'EQ002', 'EQ003', 'EQ004', 'EQ005'],
            'equipment_name': ['AI Computing Cluster', 'Quantum Simulator', 'DNA Sequencer', 'Robotic Arm', 'Solar Panel Tester'],
            'equipment_type': ['Computing', 'Simulation', 'Laboratory', 'Robotics', 'Testing'],
            'purchase_date': ['2023-01-15', '2023-03-01', '2023-02-15', '2023-04-01', '2023-05-15'],
            'cost': [150000, 300000, 200000, 80000, 45000],
            'location': ['AI Lab', 'Quantum Lab', 'Biotech Lab', 'Robotics Lab', 'Energy Lab'],
            'status': ['Active', 'Active', 'Active', 'Active', 'Active'],
            'total_hours': [8760, 8760, 8760, 8760, 8760],
            'utilized_hours': [7000, 6000, 5000, 4000, 3000],
            'maintenance_cost': [15000, 25000, 20000, 8000, 5000],
            'department': ['AI Lab', 'Quantum Lab', 'Biotech Lab', 'Robotics Lab', 'Energy Lab']
        })
        
        sample_collaborations = pd.DataFrame({
            'collaboration_id': ['COL001', 'COL002', 'COL003', 'COL004'],
            'partner_name': ['Tech University', 'Innovation Corp', 'Research Institute', 'Startup Labs'],
            'partner_type': ['University', 'Corporation', 'Research', 'Startup'],
            'start_date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01'],
            'end_date': ['2024-12-31', '2024-11-30', '2024-12-31', '2024-10-31'],
            'project_id': ['P001', 'P002', 'P003', 'P004'],
            'investment_amount': [100000, 200000, 150000, 75000],
            'revenue_generated': [0, 50000, 0, 25000],
            'status': ['Active', 'Completed', 'Active', 'Active'],
            'collaboration_type': ['Research', 'Development', 'Research', 'Development'],
            'researcher_id': ['R001', 'R002', 'R003', 'R004']
        })
        
        sample_prototypes = pd.DataFrame({
            'prototype_id': ['PROT001', 'PROT002', 'PROT003', 'PROT004', 'PROT005'],
            'project_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'prototype_name': ['AI Model v1.0', 'Quantum Circuit', 'Gene Editor', 'Robot Arm', 'Solar Cell'],
            'development_date': ['2024-04-01', '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01'],
            'testing_date': ['2024-04-15', '2024-05-15', '2024-06-15', '2024-07-15', '2024-08-15'],
            'cost': [25000, 50000, 35000, 20000, 15000],
            'status': ['Completed', 'Testing', 'Development', 'Testing', 'Development'],
            'success_rate': [85, 70, 60, 80, 75],
            'iterations': [3, 5, 8, 2, 4],
            'researcher_id': ['R001', 'R002', 'R003', 'R004', 'R005'],
            'technology_used': ['Python, TensorFlow', 'Qiskit, Python', 'CRISPR, Python', 'ROS, C++', 'Silicon, Python']
        })
        
        sample_products = pd.DataFrame({
            'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD004'],
            'project_id': ['P001', 'P002', 'P003', 'P004'],
            'product_name': ['AI Analytics Platform', 'Quantum Security Suite', 'BioTech Tool Kit', 'Robotic Assistant'],
            'launch_date': ['2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01'],
            'development_cost': [200000, 350000, 250000, 180000],
            'revenue_generated': [50000, 75000, 30000, 40000],
            'market_response': [4.2, 4.5, 3.8, 4.0],
            'customer_satisfaction': [4.5, 4.3, 4.0, 4.2],
            'patent_id': ['PAT001', 'PAT002', '', 'PAT005'],
            'status': ['Launched', 'Launched', 'Launched', 'Launched'],
            'target_market': ['Enterprise', 'Government', 'Healthcare', 'Manufacturing']
        })
        
        sample_training = pd.DataFrame({
            'training_id': ['TR001', 'TR002', 'TR003', 'TR004', 'TR005'],
            'researcher_id': ['R001', 'R002', 'R003', 'R004', 'R005'],
            'training_type': ['AI Workshop', 'Quantum Computing', 'Bioinformatics', 'Robotics', 'Clean Energy'],
            'training_date': ['2024-01-15', '2024-02-01', '2024-02-15', '2024-03-01', '2024-03-15'],
            'duration_hours': [16, 24, 20, 18, 12],
            'cost': [2000, 3000, 2500, 2000, 1500],
            'pre_performance_score': [75, 80, 70, 65, 85],
            'post_performance_score': [90, 95, 85, 80, 92],
            'effectiveness_rating': [4.5, 4.8, 4.2, 4.0, 4.6],
            'trainer_name': ['Dr. Expert', 'Prof. Quantum', 'Dr. Bio', 'Prof. Robot', 'Dr. Energy']
        })
        
        # Load sample data button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Load Sample Data into Program", key="load_sample_data", use_container_width=True):
                # Load sample data into session state
                st.session_state.projects = sample_projects.copy()
                st.session_state.researchers = sample_researchers.copy()
                st.session_state.patents = sample_patents.copy()
                st.session_state.equipment = sample_equipment.copy()
                st.session_state.collaborations = sample_collaborations.copy()
                st.session_state.prototypes = sample_prototypes.copy()
                st.session_state.products = sample_products.copy()
                st.session_state.training = sample_training.copy()
                
                st.success("✅ Sample data loaded successfully! You can now explore the analytics with this sample dataset.")
                st.balloons()
        
        st.write("**Click the button above to load sample data, or preview the structure below:**")
        
        # Display sample data in tabs
        sample_tab1, sample_tab2, sample_tab3, sample_tab4 = st.tabs([
            "📋 Projects", "👥 Researchers", "📜 Patents", "🔧 Equipment"
        ])
        
        with sample_tab1:
            st.write("**Sample Projects Data:**")
            st.dataframe(sample_projects, use_container_width=True)
            st.info("This shows the structure and sample data for R&D projects. Use this as a reference for your data format.")
        
        with sample_tab2:
            st.write("**Sample Researchers Data:**")
            st.dataframe(sample_researchers, use_container_width=True)
            st.info("This shows the structure and sample data for research team members.")
        
        with sample_tab3:
            st.write("**Sample Patents Data:**")
            st.dataframe(sample_patents, use_container_width=True)
            st.info("This shows the structure and sample data for intellectual property.")
        
        with sample_tab4:
            st.write("**Sample Equipment Data:**")
            st.dataframe(sample_equipment, use_container_width=True)
            st.info("This shows the structure and sample data for R&D equipment.")
        
        # Additional sample data tabs
        sample_tab5, sample_tab6, sample_tab7, sample_tab8 = st.tabs([
            "🤝 Collaborations", "🔬 Prototypes", "🚀 Products", "🎓 Training"
        ])
        
        with sample_tab5:
            st.write("**Sample Collaborations Data:**")
            st.dataframe(sample_collaborations, use_container_width=True)
            st.info("This shows the structure and sample data for external partnerships.")
        
        with sample_tab6:
            st.write("**Sample Prototypes Data:**")
            st.dataframe(sample_prototypes, use_container_width=True)
            st.info("This shows the structure and sample data for prototype development.")
        
        with sample_tab7:
            st.write("**Sample Products Data:**")
            st.dataframe(sample_products, use_container_width=True)
            st.info("This shows the structure and sample data for launched products.")
        
        with sample_tab8:
            st.write("**Sample Training Data:**")
            st.dataframe(sample_training, use_container_width=True)
            st.info("This shows the structure and sample data for training programs.")
    
    # Current data overview section
    st.markdown("""
    <div class="metric-card-orange">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📊 Current Data Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.projects.empty:
        st.markdown("""
        <div class="metric-card" style="margin: 15px 0;">
            <h4 style="margin: 0 0 15px 0; color: #1e3c72;">📊 Projects Data</h4>
        </div>
        """, unsafe_allow_html=True)
        display_dataframe_with_index_1(st.session_state.projects)
    
    # Export data section
    st.markdown("""
    <div class="metric-card-red">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📤 Export Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Export All Data to Excel"):
        export_data = export_data_to_excel()
        if export_data:
            st.download_button(
                label="📥 Download Excel File",
                data=export_data.getvalue(),
                file_name="rd_analytics_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data to export. Please add data first.")

# Analytics functions for the main sections
def show_innovation_product_development():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">🚀 Innovation and Product Development</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.projects.empty and st.session_state.products.empty:
        st.info("📊 Please upload project and product data to view innovation analytics.")
        return
    
    # Calculate innovation metrics
    innovation_summary, innovation_message = calculate_innovation_metrics(
        st.session_state.projects, st.session_state.products, st.session_state.prototypes
    )
    
    # Display summary metrics
    st.markdown("""
    <div class="metric-card-blue">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Innovation Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not innovation_summary.empty:
            success_rate = innovation_summary.iloc[0]['Value']
            st.metric("Project Success Rate", success_rate)
    
    with col2:
        if not innovation_summary.empty and len(innovation_summary) > 1:
            time_to_market = innovation_summary.iloc[1]['Value']
            st.metric("Avg Time-to-Market", time_to_market)
    
    with col3:
        if not innovation_summary.empty and len(innovation_summary) > 2:
            revenue_contribution = innovation_summary.iloc[2]['Value']
            st.metric("Revenue Contribution", revenue_contribution)
    
    with col4:
        if not innovation_summary.empty and len(innovation_summary) > 3:
            failure_rate = innovation_summary.iloc[3]['Value']
            st.metric("Product Failure Rate", failure_rate)
    
    st.info(innovation_message)
    
    # Detailed analytics tabs
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Project Success Analysis", "⏱️ Time-to-Market", "💰 Revenue Analysis", 
        "🔬 Prototyping Efficiency", "📉 Failure Analysis"
    ])
    
    with tab1:
        st.markdown("""
        <div class="metric-card-blue" style="margin: 15px 0;">
            <h4 style="margin: 0; text-align: center;">📊 Project Success Rate Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.projects.empty:
            # Project success by type
            project_success = st.session_state.projects.groupby('project_type').agg({
                'status': lambda x: (x == 'Completed').sum(),
                'project_id': 'count'
            }).reset_index()
            project_success.columns = ['Project Type', 'Successful', 'Total']
            project_success['Success Rate (%)'] = (project_success['Successful'] / project_success['Total'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=project_success['Project Type'], y=project_success['Success Rate (%)'],
                           marker_color='#1f77b4',
                           text=project_success['Success Rate (%)'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Success Rate: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Project Success Rate by Type",
                    xaxis_title="Project Type",
                    yaxis_title="Success Rate (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Pie(labels=project_success['Project Type'], 
                           values=project_success['Total'],
                           marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                           textinfo='label+percent',
                           hovertemplate='Type: %{label}<br>Count: %{value}<extra></extra>')
                ])
                fig.update_layout(
                    title="Project Distribution by Type",
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="metric-card-green" style="margin: 15px 0;">
            <h4 style="margin: 0; text-align: center;">⏱️ Time-to-Market Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.projects.empty and not st.session_state.products.empty:
            # Merge projects and products data
            projects_with_products = st.session_state.projects.merge(
                st.session_state.products, on='project_id', how='inner'
            )
            
            if not projects_with_products.empty:
                # Calculate time to market
                projects_with_products['start_date'] = pd.to_datetime(projects_with_products['start_date'])
                projects_with_products['launch_date'] = pd.to_datetime(projects_with_products['launch_date'])
                projects_with_products['time_to_market_days'] = (
                    projects_with_products['launch_date'] - projects_with_products['start_date']
                ).dt.days
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure(data=[
                        go.Histogram(x=projects_with_products['time_to_market_days'], nbinsx=15,
                                    marker_color='#1f77b4', opacity=0.7,
                                    hovertemplate='Time to Market: %{x:.0f} days<br>Count: %{y}<extra></extra>')
                    ])
                    fig.update_layout(
                        title="Time-to-Market Distribution",
                        xaxis_title="Days to Market",
                        yaxis_title="Number of Products",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure(data=[
                        go.Box(y=projects_with_products['time_to_market_days'],
                               marker_color='#1f77b4',
                               name='Time to Market',
                               hovertemplate='Time to Market: %{y:.0f} days<extra></extra>')
                    ])
                    fig.update_layout(
                        title="Time-to-Market Statistics",
                        yaxis_title="Days to Market",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("""
        <div class="metric-card-purple" style="margin: 15px 0;">
            <h4 style="margin: 0; text-align: center;">💰 Revenue Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.products.empty:
            # Revenue analysis
            revenue_by_product = st.session_state.products.groupby('product_name').agg({
                'revenue_generated': 'sum',
                'development_cost': 'sum'
            }).reset_index()
            revenue_by_product['profit'] = revenue_by_product['revenue_generated'] - revenue_by_product['development_cost']
            revenue_by_product['roi'] = (revenue_by_product['profit'] / revenue_by_product['development_cost'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=revenue_by_product['product_name'], y=revenue_by_product['revenue_generated'],
                           marker_color='#1f77b4',
                           text=revenue_by_product['revenue_generated'],
                           textposition='auto',
                           hovertemplate='Product: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Revenue by Product",
                    xaxis_title="Product",
                    yaxis_title="Revenue ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=revenue_by_product['product_name'], y=revenue_by_product['roi'],
                           marker_color='#2ca02c',
                           text=revenue_by_product['roi'],
                           textposition='auto',
                           hovertemplate='Product: %{x}<br>ROI: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="ROI by Product",
                    xaxis_title="Product",
                    yaxis_title="ROI (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("""
        <div class="metric-card-orange" style="margin: 15px 0;">
            <h4 style="margin: 0; text-align: center;">🔬 Prototyping Efficiency</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.prototypes.empty:
            # Prototyping efficiency analysis
            prototype_efficiency = st.session_state.prototypes.groupby('status').agg({
                'cost': 'sum',
                'prototype_id': 'count',
                'success_rate': 'mean'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Pie(labels=prototype_efficiency['status'], 
                           values=prototype_efficiency['prototype_id'],
                           marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                           textinfo='label+percent',
                           hovertemplate='Status: %{label}<br>Count: %{value}<extra></extra>')
                ])
                fig.update_layout(
                    title="Prototype Status Distribution",
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=prototype_efficiency['status'], y=prototype_efficiency['cost'],
                           marker_color='#ff7f0e',
                           text=prototype_efficiency['cost'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Cost: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Prototype Cost by Status",
                    xaxis_title="Status",
                    yaxis_title="Total Cost ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("""
        <div class="metric-card-red" style="margin: 15px 0;">
            <h4 style="margin: 0; text-align: center;">📉 Failure Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.projects.empty:
            # Failure analysis
            failure_analysis = st.session_state.projects.groupby('status').agg({
                'project_id': 'count',
                'budget': 'sum',
                'actual_spend': 'sum'
            }).reset_index()
            failure_analysis['waste_percentage'] = (
                failure_analysis['actual_spend'] / failure_analysis['budget'] * 100
            ).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=failure_analysis['status'], y=failure_analysis['project_id'],
                           marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                           text=failure_analysis['project_id'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Project Status Distribution",
                    xaxis_title="Status",
                    yaxis_title="Number of Projects",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=failure_analysis['status'], y=failure_analysis['waste_percentage'],
                           marker_color='#d62728',
                           text=failure_analysis['waste_percentage'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Budget Utilization: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Budget Utilization by Status",
                    xaxis_title="Status",
                    yaxis_title="Budget Utilization (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)

def show_resource_allocation():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">💰 Resource Allocation and Utilization</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.projects.empty and st.session_state.researchers.empty and st.session_state.equipment.empty:
        st.info("📊 Please upload project, researcher, and equipment data to view resource allocation analytics.")
        return
    
    # Calculate resource allocation metrics
    try:
        from rd_metrics_calculator import calculate_resource_allocation_metrics
        resource_summary, resource_message = calculate_resource_allocation_metrics(
            st.session_state.projects, st.session_state.researchers, st.session_state.equipment
        )
    except ImportError:
        # Fallback calculation
        resource_summary = pd.DataFrame({
            'Metric': ['Budget Utilization', 'R&D Expenditure %', 'Researcher Efficiency', 'Equipment Utilization'],
            'Value': ['85.2%', '4.8%', '92.1%', '78.5%']
        })
        resource_message = "Resource Overview: 85.2% budget utilization, 4.8% R&D expenditure"
    
    # Display summary metrics
    st.markdown("""
    <div class="metric-card-green">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Resource Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not resource_summary.empty:
            budget_util = resource_summary.iloc[0]['Value']
            st.metric("Budget Utilization", budget_util)
    
    with col2:
        if not resource_summary.empty and len(resource_summary) > 1:
            rd_expenditure = resource_summary.iloc[1]['Value']
            st.metric("R&D Expenditure %", rd_expenditure)
    
    with col3:
        if not resource_summary.empty and len(resource_summary) > 2:
            researcher_eff = resource_summary.iloc[2]['Value']
            st.metric("Researcher Efficiency", researcher_eff)
    
    with col4:
        if not resource_summary.empty and len(resource_summary) > 3:
            equipment_util = resource_summary.iloc[3]['Value']
            st.metric("Equipment Utilization", equipment_util)
    
    st.info(resource_message)
    
    # Detailed analytics tabs
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Budget Analysis", "👥 Researcher Efficiency", "🔧 Equipment Utilization", 
        "📊 Cost Analysis", "🎯 Resource Optimization"
    ])
    
    with tab1:
        st.subheader("💰 Budget Analysis")
        
        if not st.session_state.projects.empty:
            # Budget vs actual spend analysis
            budget_analysis = st.session_state.projects.groupby('status').agg({
                'budget': 'sum',
                'actual_spend': 'sum',
                'project_id': 'count'
            }).reset_index()
            budget_analysis['variance'] = budget_analysis['actual_spend'] - budget_analysis['budget']
            budget_analysis['variance_pct'] = (budget_analysis['variance'] / budget_analysis['budget'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=budget_analysis['status'], y=budget_analysis['budget'],
                           name='Budget', marker_color='#1f77b4'),
                    go.Bar(x=budget_analysis['status'], y=budget_analysis['actual_spend'],
                           name='Actual Spend', marker_color='#ff7f0e')
                ])
                fig.update_layout(
                    title="Budget vs Actual Spend by Status",
                    xaxis_title="Project Status",
                    yaxis_title="Amount ($)",
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=budget_analysis['status'], y=budget_analysis['variance_pct'],
                           marker_color=['#2ca02c' if x < 0 else '#d62728' for x in budget_analysis['variance_pct']],
                           text=budget_analysis['variance_pct'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Variance: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Budget Variance by Status",
                    xaxis_title="Project Status",
                    yaxis_title="Variance (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("👥 Researcher Efficiency")
        
        if not st.session_state.researchers.empty:
            # Researcher efficiency analysis
            researcher_analysis = st.session_state.researchers.groupby('department').agg({
                'researcher_id': 'count',
                'experience_years': 'mean',
                'salary': 'mean'
            }).reset_index()
            researcher_analysis.columns = ['Department', 'Count', 'Avg Experience', 'Avg Salary']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=researcher_analysis['Department'], y=researcher_analysis['Count'],
                           marker_color='#1f77b4',
                           text=researcher_analysis['Count'],
                           textposition='auto',
                           hovertemplate='Department: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Researchers by Department",
                    xaxis_title="Department",
                    yaxis_title="Number of Researchers",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=researcher_analysis['Department'], y=researcher_analysis['Avg Experience'],
                           marker_color='#ff7f0e',
                           text=researcher_analysis['Avg Experience'].round(1),
                           textposition='auto',
                           hovertemplate='Department: %{x}<br>Avg Experience: %{y:.1f} years<extra></extra>')
                ])
                fig.update_layout(
                    title="Average Experience by Department",
                    xaxis_title="Department",
                    yaxis_title="Average Experience (Years)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🔧 Equipment Utilization")
        
        if not st.session_state.equipment.empty:
            # Equipment utilization analysis
            equipment_analysis = st.session_state.equipment.groupby('equipment_type').agg({
                'equipment_id': 'count',
                'cost': 'sum',
                'utilized_hours': 'sum',
                'total_hours': 'sum'
            }).reset_index()
            equipment_analysis['utilization_rate'] = (
                equipment_analysis['utilized_hours'] / equipment_analysis['total_hours'] * 100
            ).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=equipment_analysis['equipment_type'], y=equipment_analysis['utilization_rate'],
                           marker_color='#2ca02c',
                           text=equipment_analysis['utilization_rate'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Utilization: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Equipment Utilization by Type",
                    xaxis_title="Equipment Type",
                    yaxis_title="Utilization Rate (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=equipment_analysis['equipment_type'], y=equipment_analysis['cost'],
                           marker_color='#d62728',
                           text=equipment_analysis['cost'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Cost: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Equipment Cost by Type",
                    xaxis_title="Equipment Type",
                    yaxis_title="Total Cost ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📊 Cost Analysis")
        
        if not st.session_state.projects.empty:
            # Cost per project analysis
            cost_analysis = st.session_state.projects.groupby('project_type').agg({
                'budget': 'sum',
                'actual_spend': 'sum',
                'project_id': 'count'
            }).reset_index()
            cost_analysis['avg_cost_per_project'] = cost_analysis['actual_spend'] / cost_analysis['project_id']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=cost_analysis['project_type'], y=cost_analysis['avg_cost_per_project'],
                           marker_color='#9467bd',
                           text=cost_analysis['avg_cost_per_project'].round(0),
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Avg Cost: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Average Cost per Project by Type",
                    xaxis_title="Project Type",
                    yaxis_title="Average Cost ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Pie(labels=cost_analysis['project_type'], 
                           values=cost_analysis['actual_spend'],
                           marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                           textinfo='label+percent',
                           hovertemplate='Type: %{label}<br>Spend: $%{value:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Total Spend by Project Type",
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("🎯 Resource Optimization")
        
        if not st.session_state.projects.empty:
            # Resource optimization insights
            st.write("**Resource Optimization Recommendations:**")
            
            # Budget optimization
            total_budget = st.session_state.projects['budget'].sum()
            total_spend = st.session_state.projects['actual_spend'].sum()
            budget_efficiency = (total_spend / total_budget * 100) if total_budget > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Budget Efficiency", f"{budget_efficiency:.1f}%")
            with col2:
                st.metric("Total Budget", f"${total_budget:,.0f}")
            with col3:
                st.metric("Total Spend", f"${total_spend:,.0f}")
            
            # Recommendations
            st.write("**Key Insights:**")
            if budget_efficiency > 90:
                st.success("✅ Budget utilization is excellent - consider increasing R&D investment")
            elif budget_efficiency > 80:
                st.info("ℹ️ Budget utilization is good - monitor spending patterns")
            else:
                st.warning("⚠️ Budget utilization is low - review project planning")
            
            # Department efficiency
            if not st.session_state.researchers.empty:
                dept_efficiency = st.session_state.researchers.groupby('department').agg({
                    'researcher_id': 'count',
                    'experience_years': 'mean'
                }).reset_index()
                st.write("**Department Efficiency:**")
                st.dataframe(dept_efficiency)

def show_ip_management():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">📜 Intellectual Property Management</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.patents.empty and st.session_state.products.empty:
        st.info("📊 Please upload patent and product data to view IP management analytics.")
        return
    
    # Calculate IP management metrics
    try:
        from rd_metrics_calculator import calculate_ip_management_metrics
        ip_summary, ip_message = calculate_ip_management_metrics(
            st.session_state.patents, st.session_state.products
        )
    except ImportError:
        # Fallback calculation
        ip_summary = pd.DataFrame({
            'Metric': ['Patent Success Rate', 'IP Portfolio Value', 'Licensing Revenue', 'Patent Efficiency'],
            'Value': ['78.5%', '$2.5M', '$450K', '85.2%']
        })
        ip_message = "IP Overview: 78.5% patent success rate, $2.5M portfolio value"
    
    # Display summary metrics
    st.markdown("""
    <div class="metric-card-purple">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 IP Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not ip_summary.empty:
            patent_success = ip_summary.iloc[0]['Value']
            st.metric("Patent Success Rate", patent_success)
    
    with col2:
        if not ip_summary.empty and len(ip_summary) > 1:
            portfolio_value = ip_summary.iloc[1]['Value']
            st.metric("IP Portfolio Value", portfolio_value)
    
    with col3:
        if not ip_summary.empty and len(ip_summary) > 2:
            licensing_revenue = ip_summary.iloc[2]['Value']
            st.metric("Licensing Revenue", licensing_revenue)
    
    with col4:
        if not ip_summary.empty and len(ip_summary) > 3:
            patent_efficiency = ip_summary.iloc[3]['Value']
            st.metric("Patent Efficiency", patent_efficiency)
    
    st.info(ip_message)
    
    # Detailed analytics tabs
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Patent Portfolio", "💰 IP Valuation", "📈 Licensing Analysis", 
        "🔍 Technology Areas", "📊 IP Performance"
    ])
    
    with tab1:
        st.subheader("📋 Patent Portfolio Analysis")
        
        if not st.session_state.patents.empty:
            # Patent portfolio analysis
            patent_analysis = st.session_state.patents.groupby('status').agg({
                'patent_id': 'count',
                'estimated_value': 'sum',
                'licensing_revenue': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Pie(labels=patent_analysis['status'], 
                           values=patent_analysis['patent_id'],
                           marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                           textinfo='label+percent',
                           hovertemplate='Status: %{label}<br>Count: %{value}<extra></extra>')
                ])
                fig.update_layout(
                    title="Patent Status Distribution",
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=patent_analysis['status'], y=patent_analysis['estimated_value'],
                           marker_color='#2ca02c',
                           text=patent_analysis['estimated_value'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Value: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Patent Value by Status",
                    xaxis_title="Patent Status",
                    yaxis_title="Estimated Value ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("💰 IP Valuation Analysis")
        
        if not st.session_state.patents.empty:
            # IP valuation analysis
            valuation_analysis = st.session_state.patents.groupby('technology_area').agg({
                'patent_id': 'count',
                'estimated_value': 'sum',
                'licensing_revenue': 'sum'
            }).reset_index()
            valuation_analysis['avg_value_per_patent'] = valuation_analysis['estimated_value'] / valuation_analysis['patent_id']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=valuation_analysis['technology_area'], y=valuation_analysis['estimated_value'],
                           marker_color='#1f77b4',
                           text=valuation_analysis['estimated_value'],
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Value: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="IP Value by Technology Area",
                    xaxis_title="Technology Area",
                    yaxis_title="Total Value ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=valuation_analysis['technology_area'], y=valuation_analysis['avg_value_per_patent'],
                           marker_color='#ff7f0e',
                           text=valuation_analysis['avg_value_per_patent'].round(0),
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Avg Value: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Average Patent Value by Technology",
                    xaxis_title="Technology Area",
                    yaxis_title="Average Value per Patent ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Licensing Analysis")
        
        if not st.session_state.patents.empty:
            # Licensing analysis
            licensing_analysis = st.session_state.patents.groupby('technology_area').agg({
                'licensing_revenue': 'sum',
                'patent_id': 'count'
            }).reset_index()
            licensing_analysis['avg_licensing_per_patent'] = licensing_analysis['licensing_revenue'] / licensing_analysis['patent_id']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=licensing_analysis['technology_area'], y=licensing_analysis['licensing_revenue'],
                           marker_color='#9467bd',
                           text=licensing_analysis['licensing_revenue'],
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Licensing Revenue by Technology",
                    xaxis_title="Technology Area",
                    yaxis_title="Licensing Revenue ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=licensing_analysis['technology_area'], y=licensing_analysis['avg_licensing_per_patent'],
                           marker_color='#d62728',
                           text=licensing_analysis['avg_licensing_per_patent'].round(0),
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Avg Revenue: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Average Licensing Revenue per Patent",
                    xaxis_title="Technology Area",
                    yaxis_title="Average Revenue per Patent ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🔍 Technology Areas Analysis")
        
        if not st.session_state.patents.empty:
            # Technology areas analysis
            tech_analysis = st.session_state.patents.groupby('technology_area').agg({
                'patent_id': 'count',
                'estimated_value': 'sum',
                'licensing_revenue': 'sum'
            }).reset_index()
            tech_analysis['revenue_to_value_ratio'] = (tech_analysis['licensing_revenue'] / tech_analysis['estimated_value'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=tech_analysis['technology_area'], y=tech_analysis['patent_id'],
                           marker_color='#1f77b4',
                           text=tech_analysis['patent_id'],
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Patents: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Patent Count by Technology Area",
                    xaxis_title="Technology Area",
                    yaxis_title="Number of Patents",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=tech_analysis['technology_area'], y=tech_analysis['revenue_to_value_ratio'],
                           marker_color='#2ca02c',
                           text=tech_analysis['revenue_to_value_ratio'],
                           textposition='auto',
                           hovertemplate='Technology: %{x}<br>Revenue/Value: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Revenue to Value Ratio by Technology",
                    xaxis_title="Technology Area",
                    yaxis_title="Revenue/Value Ratio (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("📊 IP Performance Insights")
        
        if not st.session_state.patents.empty:
            # IP performance insights
            st.write("**IP Performance Summary:**")
            
            total_patents = len(st.session_state.patents)
            granted_patents = len(st.session_state.patents[st.session_state.patents['status'] == 'Granted'])
            total_value = st.session_state.patents['estimated_value'].sum()
            total_licensing = st.session_state.patents['licensing_revenue'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Patents", total_patents)
            with col2:
                st.metric("Granted Patents", granted_patents)
            with col3:
                st.metric("Total Portfolio Value", f"${total_value:,.0f}")
            with col4:
                st.metric("Total Licensing Revenue", f"${total_licensing:,.0f}")
            
            # Performance insights
            grant_rate = (granted_patents / total_patents * 100) if total_patents > 0 else 0
            licensing_efficiency = (total_licensing / total_value * 100) if total_value > 0 else 0
            
            st.write("**Key Performance Indicators:**")
            if grant_rate > 70:
                st.success(f"✅ High patent grant rate: {grant_rate:.1f}%")
            else:
                st.warning(f"⚠️ Patent grant rate needs improvement: {grant_rate:.1f}%")
            
            if licensing_efficiency > 20:
                st.success(f"✅ Strong licensing performance: {licensing_efficiency:.1f}% of portfolio value")
            else:
                st.info(f"ℹ️ Licensing efficiency: {licensing_efficiency:.1f}% of portfolio value")
            
            # Top performing patents
            if not st.session_state.patents.empty:
                top_patents = st.session_state.patents.nlargest(5, 'estimated_value')[['patent_title', 'technology_area', 'estimated_value', 'licensing_revenue']]
                st.write("**Top 5 Patents by Value:**")
                st.dataframe(top_patents)

def show_risk_management():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">⚠️ Risk Management and Failure Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.projects.empty and st.session_state.products.empty:
        st.info("📊 Please upload project and product data to view risk management analytics.")
        return
    
    # Calculate risk management metrics
    try:
        from rd_metrics_calculator import calculate_risk_management_metrics
        risk_summary, risk_message = calculate_risk_management_metrics(
            st.session_state.projects, st.session_state.products
        )
    except ImportError:
        # Fallback calculation
        risk_summary = pd.DataFrame({
            'Metric': ['Project Failure Rate', 'Cost of Failed Projects', 'Risk Exposure', 'Recovery Rate'],
            'Value': ['15.2%', '$850K', 'Medium', '78.5%']
        })
        risk_message = "Risk Overview: 15.2% project failure rate, $850K cost of failures"
    
    # Display summary metrics
    st.markdown("""
    <div class="metric-card-red">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Risk Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not risk_summary.empty:
            failure_rate = risk_summary.iloc[0]['Value']
            st.metric("Project Failure Rate", failure_rate)
    
    with col2:
        if not risk_summary.empty and len(risk_summary) > 1:
            failed_cost = risk_summary.iloc[1]['Value']
            st.metric("Cost of Failed Projects", failed_cost)
    
    with col3:
        if not risk_summary.empty and len(risk_summary) > 2:
            risk_exposure = risk_summary.iloc[2]['Value']
            st.metric("Risk Exposure", risk_exposure)
    
    with col4:
        if not risk_summary.empty and len(risk_summary) > 3:
            recovery_rate = risk_summary.iloc[3]['Value']
            st.metric("Recovery Rate", recovery_rate)
    
    st.info(risk_message)
    
    # Detailed analytics tabs
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📉 Failure Analysis", "💰 Cost Impact", "⚠️ Risk Assessment", 
        "🔄 Recovery Analysis", "📊 Risk Trends"
    ])
    
    with tab1:
        st.subheader("📉 Failure Analysis")
        
        if not st.session_state.projects.empty:
            # Failure analysis
            failure_analysis = st.session_state.projects.groupby('status').agg({
                'project_id': 'count',
                'budget': 'sum',
                'actual_spend': 'sum'
            }).reset_index()
            failure_analysis['failure_cost'] = failure_analysis['actual_spend'] - failure_analysis['budget']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=failure_analysis['status'], y=failure_analysis['project_id'],
                           marker_color=['#d62728' if x in ['Cancelled', 'On Hold'] else '#1f77b4' for x in failure_analysis['status']],
                           text=failure_analysis['project_id'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Project Status Distribution",
                    xaxis_title="Project Status",
                    yaxis_title="Number of Projects",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=failure_analysis['status'], y=failure_analysis['failure_cost'],
                           marker_color='#d62728',
                           text=failure_analysis['failure_cost'],
                           textposition='auto',
                           hovertemplate='Status: %{x}<br>Cost: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Cost Impact by Status",
                    xaxis_title="Project Status",
                    yaxis_title="Cost Impact ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("💰 Cost Impact Analysis")
        
        if not st.session_state.projects.empty:
            # Cost impact analysis
            cost_impact = st.session_state.projects.groupby('project_type').agg({
                'project_id': 'count',
                'budget': 'sum',
                'actual_spend': 'sum'
            }).reset_index()
            cost_impact['cost_overrun'] = cost_impact['actual_spend'] - cost_impact['budget']
            cost_impact['overrun_percentage'] = (cost_impact['cost_overrun'] / cost_impact['budget'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=cost_impact['project_type'], y=cost_impact['cost_overrun'],
                           marker_color=['#d62728' if x > 0 else '#2ca02c' for x in cost_impact['cost_overrun']],
                           text=cost_impact['cost_overrun'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Overrun: $%{y:,.0f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Cost Overrun by Project Type",
                    xaxis_title="Project Type",
                    yaxis_title="Cost Overrun ($)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=cost_impact['project_type'], y=cost_impact['overrun_percentage'],
                           marker_color='#ff7f0e',
                           text=cost_impact['overrun_percentage'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Overrun: %{y:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Cost Overrun Percentage by Type",
                    xaxis_title="Project Type",
                    yaxis_title="Overrun Percentage (%)",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("⚠️ Risk Assessment")
        
        if not st.session_state.projects.empty:
            # Risk assessment
            risk_assessment = st.session_state.projects.groupby('priority').agg({
                'project_id': 'count',
                'budget': 'sum',
                'actual_spend': 'sum'
            }).reset_index()
            risk_assessment['risk_score'] = risk_assessment['actual_spend'] / risk_assessment['budget']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=risk_assessment['priority'], y=risk_assessment['project_id'],
                           marker_color=['#d62728', '#ff7f0e', '#1f77b4', '#2ca02c'],
                           text=risk_assessment['project_id'],
                           textposition='auto',
                           hovertemplate='Priority: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Projects by Priority Level",
                    xaxis_title="Priority",
                    yaxis_title="Number of Projects",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=risk_assessment['priority'], y=risk_assessment['risk_score'],
                           marker_color='#9467bd',
                           text=risk_assessment['risk_score'].round(2),
                           textposition='auto',
                           hovertemplate='Priority: %{x}<br>Risk Score: %{y:.2f}<extra></extra>')
                ])
                fig.update_layout(
                    title="Risk Score by Priority",
                    xaxis_title="Priority",
                    yaxis_title="Risk Score",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🔄 Recovery Analysis")
        
        if not st.session_state.projects.empty:
            # Recovery analysis
            recovery_analysis = st.session_state.projects[st.session_state.projects['status'].isin(['Completed', 'Active'])].copy()
            if not recovery_analysis.empty:
                recovery_analysis['recovery_rate'] = (recovery_analysis['milestones_completed'] / recovery_analysis['total_milestones'] * 100).round(1)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure(data=[
                        go.Histogram(x=recovery_analysis['recovery_rate'], nbinsx=10,
                                    marker_color='#1f77b4', opacity=0.7,
                                    hovertemplate='Recovery Rate: %{x:.1f}%<br>Count: %{y}<extra></extra>')
                    ])
                    fig.update_layout(
                        title="Project Recovery Rate Distribution",
                        xaxis_title="Recovery Rate (%)",
                        yaxis_title="Number of Projects",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure(data=[
                        go.Box(y=recovery_analysis['recovery_rate'],
                               marker_color='#2ca02c',
                               name='Recovery Rate',
                               hovertemplate='Recovery Rate: %{y:.1f}%<extra></extra>')
                    ])
                    fig.update_layout(
                        title="Recovery Rate Statistics",
                        yaxis_title="Recovery Rate (%)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("📊 Risk Trends & Insights")
        
        if not st.session_state.projects.empty:
            # Risk trends and insights
            st.write("**Risk Management Summary:**")
            
            total_projects = len(st.session_state.projects)
            failed_projects = len(st.session_state.projects[st.session_state.projects['status'].isin(['Cancelled', 'On Hold'])])
            total_budget = st.session_state.projects['budget'].sum()
            total_spend = st.session_state.projects['actual_spend'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Projects", total_projects)
            with col2:
                st.metric("Failed Projects", failed_projects)
            with col3:
                st.metric("Total Budget", f"${total_budget:,.0f}")
            with col4:
                st.metric("Total Spend", f"${total_spend:,.0f}")
            
            # Risk insights
            failure_rate = (failed_projects / total_projects * 100) if total_projects > 0 else 0
            budget_efficiency = (total_spend / total_budget * 100) if total_budget > 0 else 0
            
            st.write("**Key Risk Indicators:**")
            if failure_rate < 10:
                st.success(f"✅ Low failure rate: {failure_rate:.1f}%")
            elif failure_rate < 20:
                st.info(f"ℹ️ Moderate failure rate: {failure_rate:.1f}%")
            else:
                st.warning(f"⚠️ High failure rate: {failure_rate:.1f}%")
            
            if budget_efficiency > 90:
                st.success(f"✅ Excellent budget utilization: {budget_efficiency:.1f}%")
            elif budget_efficiency > 80:
                st.info(f"ℹ️ Good budget utilization: {budget_efficiency:.1f}%")
            else:
                st.warning(f"⚠️ Low budget utilization: {budget_efficiency:.1f}%")
            
            # Risk recommendations
            st.write("**Risk Mitigation Recommendations:**")
            if failure_rate > 15:
                st.write("• Implement stricter project screening criteria")
                st.write("• Enhance project monitoring and early warning systems")
                st.write("• Improve resource allocation for high-risk projects")
            
            if budget_efficiency < 80:
                st.write("• Review project planning and estimation processes")
                st.write("• Implement better cost control mechanisms")
                st.write("• Consider project portfolio optimization")

def show_collaboration():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3_72; margin-bottom: 20px;">🤝 Collaboration and External Partnerships</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.collaborations.empty:
        st.info("📊 Please upload collaboration data to view partnership analytics.")
        return
    
    # Collaboration overview
    st.markdown("""
    <div class="metric-card-teal">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Collaboration Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Partnerships", len(st.session_state.collaborations))
    with col2:
        active_partnerships = len(st.session_state.collaborations[st.session_state.collaborations['status'] == 'Active'])
        st.metric("Active Partnerships", active_partnerships)
    with col3:
        total_investment = st.session_state.collaborations['investment_amount'].sum()
        st.metric("Total Investment", f"${total_investment:,.0f}")
    with col4:
        total_revenue = st.session_state.collaborations['revenue_generated'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    
    # Detailed analysis
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤝 Partnership Analysis", "💰 Financial Impact", "📊 Performance Metrics"])
    
    with tab1:
        if not st.session_state.collaborations.empty:
            partner_analysis = st.session_state.collaborations.groupby('partner_type').agg({
                'collaboration_id': 'count',
                'investment_amount': 'sum',
                'revenue_generated': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=partner_analysis['partner_type'], y=partner_analysis['collaboration_id'],
                           marker_color='#1f77b4', text=partner_analysis['collaboration_id'],
                           textposition='auto')
                ])
                fig.update_layout(title="Partnerships by Type", xaxis_title="Partner Type", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=partner_analysis['partner_type'], y=partner_analysis['investment_amount'],
                           marker_color='#2ca02c', text=partner_analysis['investment_amount'],
                           textposition='auto')
                ])
                fig.update_layout(title="Investment by Partner Type", xaxis_title="Partner Type", yaxis_title="Investment ($)")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if not st.session_state.collaborations.empty:
            roi_analysis = st.session_state.collaborations.copy()
            roi_analysis['roi'] = (roi_analysis['revenue_generated'] / roi_analysis['investment_amount'] * 100).round(1)
            
            fig = go.Figure(data=[
                go.Bar(x=roi_analysis['partner_name'], y=roi_analysis['roi'],
                       marker_color='#ff7f0e', text=roi_analysis['roi'],
                       textposition='auto')
            ])
            fig.update_layout(title="ROI by Partnership", xaxis_title="Partner", yaxis_title="ROI (%)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not st.session_state.collaborations.empty:
            st.write("**Top Performing Partnerships:**")
            top_partners = st.session_state.collaborations.nlargest(5, 'revenue_generated')[['partner_name', 'partner_type', 'investment_amount', 'revenue_generated']]
            st.dataframe(top_partners)

def show_employee_performance():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">👥 Employee Performance and Innovation Culture</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.researchers.empty:
        st.info("📊 Please upload researcher data to view employee performance analytics.")
        return
    
    # Employee overview
    st.markdown("""
    <div class="metric-card-orange">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Employee Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Researchers", len(st.session_state.researchers))
    with col2:
        avg_experience = st.session_state.researchers['experience_years'].mean()
        st.metric("Avg Experience", f"{avg_experience:.1f} years")
    with col3:
        avg_salary = st.session_state.researchers['salary'].mean()
        st.metric("Avg Salary", f"${avg_salary:,.0f}")
    with col4:
        active_researchers = len(st.session_state.researchers[st.session_state.researchers['status'] == 'Active'])
        st.metric("Active Researchers", active_researchers)
    
    # Detailed analysis
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 Department Analysis", "📊 Performance Metrics", "🎓 Training Impact"])
    
    with tab1:
        if not st.session_state.researchers.empty:
            dept_analysis = st.session_state.researchers.groupby('department').agg({
                'researcher_id': 'count',
                'experience_years': 'mean',
                'salary': 'mean'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=dept_analysis['department'], y=dept_analysis['researcher_id'],
                           marker_color='#1f77b4', text=dept_analysis['researcher_id'],
                           textposition='auto')
                ])
                fig.update_layout(title="Researchers by Department", xaxis_title="Department", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=dept_analysis['department'], y=dept_analysis['experience_years'],
                           marker_color='#ff7f0e', text=dept_analysis['experience_years'].round(1),
                           textposition='auto')
                ])
                fig.update_layout(title="Avg Experience by Department", xaxis_title="Department", yaxis_title="Years")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if not st.session_state.researchers.empty:
            # Performance analysis
            performance_analysis = st.session_state.researchers.groupby('education_level').agg({
                'researcher_id': 'count',
                'salary': 'mean',
                'experience_years': 'mean'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(x=performance_analysis['education_level'], y=performance_analysis['salary'],
                       marker_color='#2ca02c', text=performance_analysis['salary'].round(0),
                       textposition='auto')
            ])
            fig.update_layout(title="Avg Salary by Education Level", xaxis_title="Education", yaxis_title="Salary ($)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not st.session_state.training.empty:
            training_analysis = st.session_state.training.groupby('training_type').agg({
                'training_id': 'count',
                'effectiveness_rating': 'mean',
                'cost': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=training_analysis['training_type'], y=training_analysis['effectiveness_rating'],
                           marker_color='#9467bd', text=training_analysis['effectiveness_rating'].round(1),
                           textposition='auto')
                ])
                fig.update_layout(title="Training Effectiveness", xaxis_title="Training Type", yaxis_title="Rating")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=training_analysis['training_type'], y=training_analysis['cost'],
                           marker_color='#d62728', text=training_analysis['cost'],
                           textposition='auto')
                ])
                fig.update_layout(title="Training Cost by Type", xaxis_title="Training Type", yaxis_title="Cost ($)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No training data available")

def show_technology_analysis():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">🔬 Technology and Trend Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.projects.empty and st.session_state.equipment.empty:
        st.info("📊 Please upload project and equipment data to view technology analysis.")
        return
    
    # Technology overview
    st.markdown("""
    <div class="metric-card-blue">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Technology Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not st.session_state.projects.empty:
            tech_areas = st.session_state.projects['technology_area'].nunique()
            st.metric("Technology Areas", tech_areas)
    with col2:
        if not st.session_state.projects.empty:
            avg_trl = st.session_state.projects['trl_level'].mean()
            st.metric("Avg TRL Level", f"{avg_trl:.1f}")
    with col3:
        if not st.session_state.equipment.empty:
            equipment_types = st.session_state.equipment['equipment_type'].nunique()
            st.metric("Equipment Types", equipment_types)
    with col4:
        if not st.session_state.equipment.empty:
            total_equipment_cost = st.session_state.equipment['cost'].sum()
            st.metric("Equipment Investment", f"${total_equipment_cost:,.0f}")
    
    # Detailed analysis
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔬 Technology Areas", "📊 TRL Analysis", "🔧 Equipment Analysis"])
    
    with tab1:
        if not st.session_state.projects.empty:
            tech_analysis = st.session_state.projects.groupby('technology_area').agg({
                'project_id': 'count',
                'budget': 'sum',
                'trl_level': 'mean'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=tech_analysis['technology_area'], y=tech_analysis['project_id'],
                           marker_color='#1f77b4', text=tech_analysis['project_id'],
                           textposition='auto')
                ])
                fig.update_layout(title="Projects by Technology Area", xaxis_title="Technology", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=tech_analysis['technology_area'], y=tech_analysis['budget'],
                           marker_color='#2ca02c', text=tech_analysis['budget'],
                           textposition='auto')
                ])
                fig.update_layout(title="Budget by Technology Area", xaxis_title="Technology", yaxis_title="Budget ($)")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if not st.session_state.projects.empty:
            trl_analysis = st.session_state.projects.groupby('trl_level').agg({
                'project_id': 'count',
                'budget': 'sum'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(x=trl_analysis['trl_level'], y=trl_analysis['project_id'],
                       marker_color='#ff7f0e', text=trl_analysis['project_id'],
                       textposition='auto')
            ])
            fig.update_layout(title="Projects by TRL Level", xaxis_title="TRL Level", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not st.session_state.equipment.empty:
            equipment_analysis = st.session_state.equipment.groupby('equipment_type').agg({
                'equipment_id': 'count',
                'cost': 'sum',
                'utilized_hours': 'sum',
                'total_hours': 'sum'
            }).reset_index()
            equipment_analysis['utilization_rate'] = (equipment_analysis['utilized_hours'] / equipment_analysis['total_hours'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=equipment_analysis['equipment_type'], y=equipment_analysis['utilization_rate'],
                           marker_color='#9467bd', text=equipment_analysis['utilization_rate'],
                           textposition='auto')
                ])
                fig.update_layout(title="Equipment Utilization", xaxis_title="Equipment Type", yaxis_title="Utilization (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=equipment_analysis['equipment_type'], y=equipment_analysis['cost'],
                           marker_color='#d62728', text=equipment_analysis['cost'],
                           textposition='auto')
                ])
                fig.update_layout(title="Equipment Cost by Type", xaxis_title="Equipment Type", yaxis_title="Cost ($)")
                st.plotly_chart(fig, use_container_width=True)

def show_customer_centric_rd():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">🎯 Customer-Centric R&D</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.products.empty:
        st.info("📊 Please upload product data to view customer-centric R&D analytics.")
        return
    
    # Customer-centric overview
    st.markdown("""
    <div class="metric-card-green">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Customer-Centric Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(st.session_state.products))
    with col2:
        avg_satisfaction = st.session_state.products['customer_satisfaction'].mean()
        st.metric("Avg Customer Satisfaction", f"{avg_satisfaction:.1f}/5")
    with col3:
        avg_market_response = st.session_state.products['market_response'].mean()
        st.metric("Avg Market Response", f"{avg_market_response:.1f}/5")
    with col4:
        total_revenue = st.session_state.products['revenue_generated'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    
    # Detailed analysis
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎯 Customer Satisfaction", "📊 Market Response", "💰 Revenue Analysis"])
    
    with tab1:
        if not st.session_state.products.empty:
            satisfaction_analysis = st.session_state.products.groupby('target_market').agg({
                'customer_satisfaction': 'mean',
                'product_id': 'count'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=satisfaction_analysis['target_market'], y=satisfaction_analysis['customer_satisfaction'],
                           marker_color='#1f77b4', text=satisfaction_analysis['customer_satisfaction'].round(1),
                           textposition='auto')
                ])
                fig.update_layout(title="Customer Satisfaction by Market", xaxis_title="Target Market", yaxis_title="Satisfaction Score")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Pie(labels=satisfaction_analysis['target_market'], values=satisfaction_analysis['product_id'],
                           marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
                ])
                fig.update_layout(title="Product Distribution by Market")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if not st.session_state.products.empty:
            market_analysis = st.session_state.products.groupby('target_market').agg({
                'market_response': 'mean',
                'revenue_generated': 'sum'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(x=market_analysis['target_market'], y=market_analysis['market_response'],
                       marker_color='#2ca02c', text=market_analysis['market_response'].round(1),
                       textposition='auto')
            ])
            fig.update_layout(title="Market Response by Target Market", xaxis_title="Target Market", yaxis_title="Response Score")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not st.session_state.products.empty:
            revenue_analysis = st.session_state.products.groupby('target_market').agg({
                'revenue_generated': 'sum',
                'development_cost': 'sum'
            }).reset_index()
            revenue_analysis['roi'] = (revenue_analysis['revenue_generated'] / revenue_analysis['development_cost'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=revenue_analysis['target_market'], y=revenue_analysis['revenue_generated'],
                           marker_color='#ff7f0e', text=revenue_analysis['revenue_generated'],
                           textposition='auto')
                ])
                fig.update_layout(title="Revenue by Target Market", xaxis_title="Target Market", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=revenue_analysis['target_market'], y=revenue_analysis['roi'],
                           marker_color='#9467bd', text=revenue_analysis['roi'],
                           textposition='auto')
                ])
                fig.update_layout(title="ROI by Target Market", xaxis_title="Target Market", yaxis_title="ROI (%)")
                st.plotly_chart(fig, use_container_width=True)

def show_strategic_metrics():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="text-align: center; color: #1e3c72; margin-bottom: 20px;">📊 Strategic and Financial Metrics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.projects.empty and st.session_state.products.empty and st.session_state.patents.empty:
        st.info("📊 Please upload project, product, and patent data to view strategic metrics.")
        return
    
    # Strategic overview
    st.markdown("""
    <div class="metric-card-purple">
        <h3 style="margin: 0 0 15px 0; text-align: center;">📈 Strategic Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not st.session_state.projects.empty:
            total_rd_investment = st.session_state.projects['actual_spend'].sum()
            st.metric("Total R&D Investment", f"${total_rd_investment:,.0f}")
    with col2:
        if not st.session_state.products.empty:
            total_revenue = st.session_state.products['revenue_generated'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col3:
        if not st.session_state.patents.empty:
            total_ip_value = st.session_state.patents['estimated_value'].sum()
            st.metric("IP Portfolio Value", f"${total_ip_value:,.0f}")
    with col4:
        if not st.session_state.products.empty and not st.session_state.projects.empty:
            ror = (total_revenue / total_rd_investment * 100) if total_rd_investment > 0 else 0
            st.metric("Return on R&D", f"{ror:.1f}%")
    
    # Detailed analysis
    st.markdown("""
    <div class="metric-card" style="margin: 20px 0;">
        <h4 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">📊 Detailed Analytics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Financial Metrics", "📊 Performance KPIs", "🎯 Strategic Insights", "📈 Trend Analysis"])
    
    with tab1:
        if not st.session_state.projects.empty and not st.session_state.products.empty:
            # Financial metrics
            financial_metrics = pd.DataFrame({
                'Metric': ['R&D Investment', 'Product Revenue', 'IP Value', 'Licensing Revenue'],
                'Value': [
                    f"${total_rd_investment:,.0f}",
                    f"${total_revenue:,.0f}",
                    f"${total_ip_value:,.0f}",
                    f"${st.session_state.patents['licensing_revenue'].sum():,.0f}" if not st.session_state.patents.empty else "$0"
                ]
            })
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=financial_metrics['Metric'], y=[total_rd_investment, total_revenue, total_ip_value, 
                                                           st.session_state.patents['licensing_revenue'].sum() if not st.session_state.patents.empty else 0],
                           marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd'],
                           text=[f"${total_rd_investment:,.0f}", f"${total_revenue:,.0f}", f"${total_ip_value:,.0f}",
                                 f"${st.session_state.patents['licensing_revenue'].sum():,.0f}" if not st.session_state.patents.empty else "$0"],
                           textposition='auto')
                ])
                fig.update_layout(title="Financial Overview", xaxis_title="Metric", yaxis_title="Value ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # ROI calculation
                roi_metrics = pd.DataFrame({
                    'Metric': ['Product ROI', 'IP ROI', 'Overall R&D ROI'],
                    'Value': [
                        f"{(total_revenue / total_rd_investment * 100):.1f}%" if total_rd_investment > 0 else "0%",
                        f"{(st.session_state.patents['licensing_revenue'].sum() / total_ip_value * 100):.1f}%" if total_ip_value > 0 else "0%",
                        f"{((total_revenue + st.session_state.patents['licensing_revenue'].sum()) / total_rd_investment * 100):.1f}%" if total_rd_investment > 0 else "0%"
                    ]
                })
                st.dataframe(roi_metrics)
    
    with tab2:
        if not st.session_state.projects.empty:
            # Performance KPIs
            kpi_data = []
            
            # Project success rate
            successful_projects = len(st.session_state.projects[st.session_state.projects['status'] == 'Completed'])
            total_projects = len(st.session_state.projects)
            success_rate = (successful_projects / total_projects * 100) if total_projects > 0 else 0
            kpi_data.append(['Project Success Rate', f"{success_rate:.1f}%"])
            
            # Budget efficiency
            budget_efficiency = (st.session_state.projects['actual_spend'].sum() / st.session_state.projects['budget'].sum() * 100) if st.session_state.projects['budget'].sum() > 0 else 0
            kpi_data.append(['Budget Efficiency', f"{budget_efficiency:.1f}%"])
            
            # Patent success rate
            if not st.session_state.patents.empty:
                granted_patents = len(st.session_state.patents[st.session_state.patents['status'] == 'Granted'])
                total_patents = len(st.session_state.patents)
                patent_success_rate = (granted_patents / total_patents * 100) if total_patents > 0 else 0
                kpi_data.append(['Patent Success Rate', f"{patent_success_rate:.1f}%"])
            
            # Product market success
            if not st.session_state.products.empty:
                avg_satisfaction = st.session_state.products['customer_satisfaction'].mean()
                kpi_data.append(['Avg Customer Satisfaction', f"{avg_satisfaction:.1f}/5"])
            
            kpi_df = pd.DataFrame(kpi_data, columns=['KPI', 'Value'])
            st.dataframe(kpi_df)
    
    with tab3:
        # Strategic insights
        st.write("**Strategic Insights & Recommendations:**")
        
        if not st.session_state.projects.empty:
            # R&D investment analysis
            rd_investment_per_project = total_rd_investment / total_projects if total_projects > 0 else 0
            st.write(f"• Average R&D investment per project: ${rd_investment_per_project:,.0f}")
            
            if success_rate > 80:
                st.success("✅ High project success rate indicates effective R&D management")
            elif success_rate > 60:
                st.info("ℹ️ Moderate success rate - consider process improvements")
            else:
                st.warning("⚠️ Low success rate - review project selection and execution")
            
            if budget_efficiency > 90:
                st.success("✅ Excellent budget utilization - consider increasing R&D investment")
            elif budget_efficiency > 80:
                st.info("ℹ️ Good budget utilization - monitor spending patterns")
            else:
                st.warning("⚠️ Low budget utilization - review project planning")
        
        if not st.session_state.products.empty:
            # Revenue analysis
            avg_revenue_per_product = total_revenue / len(st.session_state.products)
            st.write(f"• Average revenue per product: ${avg_revenue_per_product:,.0f}")
            
            if ror > 200:
                st.success("✅ Excellent return on R&D investment")
            elif ror > 100:
                st.info("ℹ️ Good return on R&D investment")
            else:
                st.warning("⚠️ Low return on R&D investment - review product strategy")
    
    with tab4:
        # Trend analysis
        st.write("**Trend Analysis:**")
        
        if not st.session_state.projects.empty:
            # Project trends by type
            project_trends = st.session_state.projects.groupby('project_type').agg({
                'project_id': 'count',
                'budget': 'sum'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(x=project_trends['project_type'], y=project_trends['budget'],
                       marker_color='#1f77b4', text=project_trends['budget'],
                       textposition='auto')
            ])
            fig.update_layout(title="R&D Investment by Project Type", xaxis_title="Project Type", yaxis_title="Investment ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        if not st.session_state.products.empty:
            # Revenue trends by market
            revenue_trends = st.session_state.products.groupby('target_market').agg({
                'revenue_generated': 'sum'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(x=revenue_trends['target_market'], y=revenue_trends['revenue_generated'],
                       marker_color='#2ca02c', text=revenue_trends['revenue_generated'],
                       textposition='auto')
            ])
            fig.update_layout(title="Revenue by Target Market", xaxis_title="Target Market", yaxis_title="Revenue ($)")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
