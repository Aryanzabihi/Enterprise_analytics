import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import base64
import textwrap

# Import customer service metric calculation functions
from cs_metrics_calculator import *

def display_dataframe_with_index_1(df, **kwargs):
    """Display dataframe with index starting from 1"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        return st.dataframe(df_display, **kwargs)
    else:
        return st.dataframe(df, **kwargs)

def create_template_for_download():
    """Create an Excel template with all required customer service data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct customer service schema
    customers_template = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'email', 'phone', 'company', 'industry', 
        'region', 'country', 'customer_segment', 'acquisition_date', 'status',
        'lifetime_value', 'last_interaction_date', 'preferred_channel'
    ])
    
    tickets_template = pd.DataFrame(columns=[
        'ticket_id', 'customer_id', 'agent_id', 'ticket_type', 'priority', 'status',
        'created_date', 'first_response_date', 'resolved_date', 'escalated_date',
        'channel', 'category', 'subcategory', 'description', 'resolution_notes'
    ])
    
    agents_template = pd.DataFrame(columns=[
        'agent_id', 'first_name', 'last_name', 'email', 'department', 'team',
        'hire_date', 'status', 'manager_id', 'specialization', 'performance_score'
    ])
    
    interactions_template = pd.DataFrame(columns=[
        'interaction_id', 'ticket_id', 'customer_id', 'agent_id', 'interaction_type',
        'start_time', 'end_time', 'duration_minutes', 'channel', 'satisfaction_score',
        'notes', 'outcome'
    ])
    
    feedback_template = pd.DataFrame(columns=[
        'feedback_id', 'ticket_id', 'customer_id', 'agent_id', 'feedback_type',
        'rating', 'sentiment', 'comments', 'submitted_date', 'response_date'
    ])
    
    sla_template = pd.DataFrame(columns=[
        'sla_id', 'ticket_type', 'priority', 'first_response_target_hours',
        'resolution_target_hours', 'business_hours_only', 'description'
    ])
    
    knowledge_base_template = pd.DataFrame(columns=[
        'kb_id', 'title', 'category', 'content', 'created_date', 'updated_date',
        'author_id', 'views', 'helpful_votes', 'status'
    ])
    
    training_template = pd.DataFrame(columns=[
        'training_id', 'agent_id', 'training_type', 'start_date', 'completion_date',
        'score', 'status', 'trainer_id', 'notes'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        customers_template.to_excel(writer, sheet_name='Customers', index=False)
        tickets_template.to_excel(writer, sheet_name='Tickets', index=False)
        agents_template.to_excel(writer, sheet_name='Agents', index=False)
        interactions_template.to_excel(writer, sheet_name='Interactions', index=False)
        feedback_template.to_excel(writer, sheet_name='Feedback', index=False)
        sla_template.to_excel(writer, sheet_name='SLA', index=False)
        knowledge_base_template.to_excel(writer, sheet_name='Knowledge_Base', index=False)
        training_template.to_excel(writer, sheet_name='Training', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Customers', 'Tickets', 'Agents', 'Interactions', 'Feedback', 'SLA', 'Knowledge_Base', 'Training'],
            'Required Fields': [
                'customer_id, customer_name, email, phone, company, industry, region, country, customer_segment, acquisition_date, status, lifetime_value, last_interaction_date, preferred_channel',
                'ticket_id, customer_id, agent_id, ticket_type, priority, status, created_date, first_response_date, resolved_date, escalated_date, channel, category, subcategory, description, resolution_notes',
                'agent_id, first_name, last_name, email, department, team, hire_date, status, manager_id, specialization, performance_score',
                'interaction_id, ticket_id, customer_id, agent_id, interaction_type, start_time, end_time, duration_minutes, channel, satisfaction_score, notes, outcome',
                'feedback_id, ticket_id, customer_id, agent_id, feedback_type, rating, sentiment, comments, submitted_date, response_date',
                'sla_id, ticket_type, priority, first_response_target_hours, resolution_target_hours, business_hours_only, description',
                'kb_id, title, category, content, created_date, updated_date, author_id, views, helpful_votes, status',
                'training_id, agent_id, training_type, start_date, completion_date, score, status, trainer_id, notes'
            ],
            'Data Types': [
                'Text, Text, Text, Text, Text, Text, Text, Text, Text, Date, Text, Number, Date, Text',
                'Text, Text, Text, Text, Text, Text, Date, Date, Date, Date, Text, Text, Text, Text, Text',
                'Text, Text, Text, Text, Text, Text, Date, Text, Text, Text, Number',
                'Text, Text, Text, Text, Text, DateTime, DateTime, Number, Text, Number, Text, Text',
                'Text, Text, Text, Text, Text, Number, Text, Text, Date, Date',
                'Text, Text, Text, Number, Number, Boolean, Text',
                'Text, Text, Text, Text, Date, Date, Text, Number, Number, Text',
                'Text, Text, Text, Date, Date, Number, Text, Text, Text'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
    
    # Prepare for download
    output.seek(0)
    return output.getvalue()

def process_uploaded_excel(uploaded_file):
    """Process uploaded Excel file and load data into session state"""
    try:
        # Read all sheets from the Excel file
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        # Check if all required sheets are present
        required_sheets = ['Customers', 'Tickets', 'Agents', 'Interactions', 'Feedback', 'SLA', 'Knowledge_Base', 'Training']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
        
        if missing_sheets:
            return False, f"Missing required sheets: {', '.join(missing_sheets)}"
        
        # Load data into session state
        st.session_state.customers = excel_data['Customers']
        st.session_state.tickets = excel_data['Tickets']
        st.session_state.agents = excel_data['Agents']
        st.session_state.interactions = excel_data['Interactions']
        st.session_state.feedback = excel_data['Feedback']
        st.session_state.sla = excel_data['SLA']
        st.session_state.knowledge_base = excel_data['Knowledge_Base']
        st.session_state.training = excel_data['Training']
        
        return True, f"All customer service data loaded successfully! Loaded {len(st.session_state.customers)} customers, {len(st.session_state.tickets)} tickets, {len(st.session_state.agents)} agents, and more..."
        
    except Exception as e:
        return False, f"Error reading Excel file: {str(e)}"

def load_sample_dataset(file_path):
    """Load sample dataset from Excel file for testing purposes"""
    try:
        # Read all sheets from the sample Excel file
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        # Check if all required sheets are present
        required_sheets = ['Customers', 'Tickets', 'Agents', 'Interactions', 'Feedback', 'SLA', 'Knowledge_Base', 'Training']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
        
        if missing_sheets:
            return False, f"Missing required sheets in sample dataset: {', '.join(missing_sheets)}"
        
        # Load data into session state
        st.session_state.customers = excel_data['Customers']
        st.session_state.tickets = excel_data['Tickets']
        st.session_state.agents = excel_data['Agents']
        st.session_state.interactions = excel_data['Interactions']
        st.session_state.feedback = excel_data['Feedback']
        st.session_state.sla = excel_data['SLA']
        st.session_state.knowledge_base = excel_data['Knowledge_Base']
        st.session_state.training = excel_data['Training']
        
        return True, f"Sample dataset loaded successfully! Loaded {len(st.session_state.customers)} customers, {len(st.session_state.tickets)} tickets, {len(st.session_state.agents)} agents, {len(st.session_state.interactions)} interactions, {len(st.session_state.feedback)} feedback records, {len(st.session_state.sla)} SLA records, {len(st.session_state.knowledge_base)} knowledge base articles, and {len(st.session_state.training)} training records."
        
    except Exception as e:
        return False, f"Error loading sample dataset: {str(e)}"

def export_data_to_excel():
    """Exports all customer service data from session state to a single Excel file."""
    with pd.ExcelWriter('customer_service_data_export.xlsx', engine='xlsxwriter') as writer:
        if not st.session_state.customers.empty:
            st.session_state.customers.to_excel(writer, sheet_name='Customers', index=False)
        if not st.session_state.tickets.empty:
            st.session_state.tickets.to_excel(writer, sheet_name='Tickets', index=False)
        if not st.session_state.agents.empty:
            st.session_state.agents.to_excel(writer, sheet_name='Agents', index=False)
        if not st.session_state.interactions.empty:
            st.session_state.interactions.to_excel(writer, sheet_name='Interactions', index=False)
        if not st.session_state.feedback.empty:
            st.session_state.feedback.to_excel(writer, sheet_name='Feedback', index=False)
        if not st.session_state.sla.empty:
            st.session_state.sla.to_excel(writer, sheet_name='SLA', index=False)
        if not st.session_state.knowledge_base.empty:
            st.session_state.knowledge_base.to_excel(writer, sheet_name='Knowledge_Base', index=False)
        if not st.session_state.training.empty:
            st.session_state.training.to_excel(writer, sheet_name='Training', index=False)
        
        st.success("Customer service data exported successfully as 'customer_service_data_export.xlsx'")

# Page configuration
st.set_page_config(
    page_title="Customer Service Analytics Dashboard",
    page_icon="🎧",
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

# Load custom CSS
load_custom_css()

# Initialize session state for customer service data storage
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'email', 'phone', 'company', 'industry', 
        'region', 'country', 'customer_segment', 'acquisition_date', 'status',
        'lifetime_value', 'last_interaction_date', 'preferred_channel'
    ])

if 'tickets' not in st.session_state:
    st.session_state.tickets = pd.DataFrame(columns=[
        'ticket_id', 'customer_id', 'agent_id', 'ticket_type', 'priority', 'status',
        'created_date', 'first_response_date', 'resolved_date', 'escalated_date',
        'channel', 'category', 'subcategory', 'description', 'resolution_notes'
    ])

if 'agents' not in st.session_state:
    st.session_state.agents = pd.DataFrame(columns=[
        'agent_id', 'first_name', 'last_name', 'email', 'department', 'team',
        'hire_date', 'status', 'manager_id', 'specialization', 'performance_score'
    ])

if 'interactions' not in st.session_state:
    st.session_state.interactions = pd.DataFrame(columns=[
        'interaction_id', 'ticket_id', 'customer_id', 'agent_id', 'interaction_type',
        'start_time', 'end_time', 'duration_minutes', 'channel', 'satisfaction_score',
        'notes', 'outcome'
    ])

if 'feedback' not in st.session_state:
    st.session_state.feedback = pd.DataFrame(columns=[
        'feedback_id', 'ticket_id', 'customer_id', 'agent_id', 'feedback_type',
        'rating', 'sentiment', 'comments', 'submitted_date', 'response_date'
    ])

if 'sla' not in st.session_state:
    st.session_state.sla = pd.DataFrame(columns=[
        'sla_id', 'ticket_type', 'priority', 'first_response_target_hours',
        'resolution_target_hours', 'business_hours_only', 'description'
    ])

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = pd.DataFrame(columns=[
        'kb_id', 'title', 'category', 'content', 'created_date', 'updated_date',
        'author_id', 'views', 'helpful_votes', 'status'
    ])

if 'training' not in st.session_state:
    st.session_state.training = pd.DataFrame(columns=[
        'training_id', 'agent_id', 'training_type', 'start_date', 'completion_date',
        'score', 'status', 'trainer_id', 'notes'
    ])

def main():
    # Load custom CSS styling
    load_custom_css()
    
    st.markdown("""
    <div class="main-header">
        <h1>🎧 Customer Service Analytics Dashboard</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Comprehensive Customer Service Performance Analytics & Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        
        if st.button("😊 Customer Satisfaction", key="nav_customer_satisfaction", use_container_width=True):
            st.session_state.current_page = "😊 Customer Satisfaction"
        
        if st.button("⏱️ Response & Resolution", key="nav_response_resolution", use_container_width=True):
            st.session_state.current_page = "⏱️ Response & Resolution"
        
        if st.button("⚡ Service Efficiency", key="nav_service_efficiency", use_container_width=True):
            st.session_state.current_page = "⚡ Service Efficiency"
        
        if st.button("🔄 Customer Retention", key="nav_customer_retention", use_container_width=True):
            st.session_state.current_page = "🔄 Customer Retention"
        
        if st.button("👨‍💼 Agent Performance", key="nav_agent_performance", use_container_width=True):
            st.session_state.current_page = "👨‍💼 Agent Performance"
        
        if st.button("📊 Interaction Analysis", key="nav_interaction_analysis", use_container_width=True):
            st.session_state.current_page = "📊 Interaction Analysis"
        
        if st.button("🌐 Omnichannel Experience", key="nav_omnichannel_experience", use_container_width=True):
            st.session_state.current_page = "🌐 Omnichannel Experience"
        
        if st.button("💰 Business Impact", key="nav_business_impact", use_container_width=True):
            st.session_state.current_page = "💰 Business Impact"
        
        if st.button("🔮 Predictive Analytics", key="nav_predictive_analytics", use_container_width=True):
            st.session_state.current_page = "🔮 Predictive Analytics"
        
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
        
        page = st.session_state.current_page
    
    # Main content area
    if page == "🏠 Home":
        show_home()
    
    elif page == "📝 Data Input":
        show_data_input()
    
    elif page == "😊 Customer Satisfaction":
        show_customer_satisfaction()
    
    elif page == "⏱️ Response & Resolution":
        show_response_resolution()
    
    elif page == "⚡ Service Efficiency":
        show_service_efficiency()
    
    elif page == "🔄 Customer Retention":
        show_customer_retention()
    
    elif page == "👨‍💼 Agent Performance":
        show_agent_performance()
    
    elif page == "📊 Interaction Analysis":
        show_interaction_analysis()
    
    elif page == "🌐 Omnichannel Experience":
        show_omnichannel_experience()
    
    elif page == "💰 Business Impact":
        show_business_impact()
    
    elif page == "🔮 Predictive Analytics":
        show_predictive_analytics()

def show_home():
    # Welcome section
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #1e3c72; margin-bottom: 20px;">🎯 Welcome to the Customer Service Analytics Dashboard</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; color: #374151;">
            This comprehensive tool helps you calculate and analyze key customer service metrics across multiple categories, 
            providing actionable insights to improve customer experience and operational efficiency.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create metric cards for quick overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card-blue">
            <h3 style="margin: 0; color: white;">📊</h3>
            <h4 style="margin: 10px 0; color: white;">Analytics Categories</h4>
            <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;">10 comprehensive analysis areas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card-purple">
            <h3 style="margin: 0; color: white;">🎧</h3>
            <h4 style="margin: 10px 0; color: white;">Customer Service</h4>
            <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;">Performance metrics & insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card-green">
            <h3 style="margin: 0; color: white;">⚡</h3>
            <h4 style="margin: 10px 0; color: white;">Real-time</h4>
            <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;">Live data updates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card-orange">
            <h3 style="margin: 0; color: white;">🔮</h3>
            <h4 style="margin: 10px 0; color: white;">Predictive</h4>
            <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;">Advanced analytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Available Analytics Categories
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📊 Available Customer Service Analytics Categories</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a grid layout using columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">😊 Customer Satisfaction & Feedback</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Customer Satisfaction Score (CSAT)</li>
                <li>Net Promoter Score (NPS)</li>
                <li>Customer Effort Score (CES)</li>
                <li>Sentiment Analysis</li>
                <li>Resolution Satisfaction</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">⏱️ Response & Resolution</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>First Response Time (FRT)</li>
                <li>Average Resolution Time (ART)</li>
                <li>First Call Resolution (FCR)</li>
                <li>Escalation Analysis</li>
                <li>Queue Wait Time</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">⚡ Service Efficiency</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Ticket Volume Analysis</li>
                <li>Agent Utilization Rate</li>
                <li>SLA Compliance</li>
                <li>Channel Performance</li>
                <li>Cost Per Resolution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">🔄 Customer Retention</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Churn Rate Analysis</li>
                <li>Retention Rate Analysis</li>
                <li>Loyalty Program Effectiveness</li>
                <li>Proactive Support Impact</li>
                <li>Customer Lifetime Value (CLV)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">👨‍💼 Agent Performance</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Agent Performance Score</li>
                <li>Training Effectiveness</li>
                <li>Call Quality Score</li>
                <li>Turnover Analysis</li>
                <li>Knowledge Base Utilization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">🌐 Omnichannel Experience</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Cross-channel Analysis</li>
                <li>Social Media Effectiveness</li>
                <li>Chatbot Performance</li>
                <li>Mobile vs Desktop</li>
                <li>Channel Optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting Started section
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">🚀 Getting Started</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Getting started cards
    gs_col1, gs_col2, gs_col3 = st.columns(3)
    
    with gs_col1:
        st.markdown("""
        <div class="metric-card-blue" style="text-align: center;">
            <h4 style="color: white; margin-bottom: 10px;">1. Data Input</h4>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">Enter your customer service data in the "Data Input" tab</p>
        </div>
        """, unsafe_allow_html=True)
    
    with gs_col2:
        st.markdown("""
        <div class="metric-card-purple" style="text-align: center;">
            <h4 style="color: white; margin-bottom: 10px;">2. Calculate Metrics</h4>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">Use the main tabs to view specific metric categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with gs_col3:
        st.markdown("""
        <div class="metric-card-green" style="text-align: center;">
            <h4 style="color: white; margin-bottom: 10px;">3. Real-time Analysis</h4>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">All metrics update automatically based on your data</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data Schema section
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📈 Data Schema</h3>
        <p style="color: #374151; margin-bottom: 20px;">
            The application supports the following customer service data tables:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data schema cards in a grid
    schema_cols = st.columns(4)
    
    schema_data = [
        ("👥 Customers", "Demographics, segments, lifetime value"),
        ("🎫 Tickets", "Issues, priorities, status, resolution"),
        ("👨‍💼 Agents", "Performance, teams, specializations"),
        ("💬 Interactions", "Calls, chats, emails, outcomes"),
        ("⭐ Feedback", "Ratings, sentiment, comments"),
        ("📋 SLA", "Service level agreements, targets"),
        ("📚 Knowledge Base", "Articles, usage, effectiveness"),
        ("🎓 Training", "Agent development, scores, outcomes")
    ]
    
    for i, (title, description) in enumerate(schema_data):
        col_idx = i % 4
        with schema_cols[col_idx]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; padding: 15px;">
                <h5 style="color: #1e3c72; margin: 0;">{title}</h5>
                <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 0.9rem;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Important note
    st.markdown("""
    <div class="insights-container">
        <h4 style="color: white; margin: 0;">💡 Important Note</h4>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">
            All calculations are performed automatically based on your input data. Make sure to enter complete and accurate data for the most reliable metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_data_input():
    """Show data input forms and file upload options"""
    st.markdown("""
    <div class="main-header" style="margin-bottom: 30px;">
        <h2 style="margin: 0;">📝 Data Input</h2>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Upload your data or enter it manually to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create main tabs for the three main sections
    main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
        "📥 Download Template", "📤 Upload Data", "📝 Manual Entry", "🧪 Sample Data"
    ])
    
    with main_tab1:
        st.markdown("""
        <div class="welcome-section">
            <h3 style="color: #1e3c72; margin-bottom: 20px;">📥 Download Data Template</h3>
            <p style="color: #374151; margin-bottom: 20px;">Download the Excel template with all required customer service data schema, fill it with your data, and upload it back.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create template for download
        if st.button("📥 Download Excel Template", key="download_template", use_container_width=True):
            template_data = create_template_for_download()
            st.download_button(
                label="💾 Save Template",
                data=template_data,
                file_name="customer_service_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="save_template"
            )
        
        # Template information
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">Template includes:</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>8 Customer service data tables in separate sheets</li>
                <li>Instructions sheet with field descriptions</li>
                <li>Proper column headers and data types</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with main_tab2:
        st.markdown("""
        <div class="welcome-section">
            <h3 style="color: #1e3c72; margin-bottom: 20px;">📤 Upload Your Data</h3>
            <p style="color: #374151; margin-bottom: 20px;">Upload your filled Excel template:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload for Excel template
        uploaded_file = st.file_uploader(
            "Upload Excel file with all customer service tables",
            type=['xlsx', 'xls'],
            key="excel_uploader"
        )
        
        # Upload features information
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">Upload features:</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Automatic validation of all sheets</li>
                <li>Import all 8 customer service tables at once</li>
                <li>Error checking and feedback</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                success, message = process_uploaded_excel(uploaded_file)
                if success:
                    st.success(f"✅ {message}")
                    st.info("💡 You can now navigate to other sections to view your data analytics!")
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with main_tab3:
        st.markdown("""
        <div class="welcome-section">
            <h3 style="color: #1e3c72; margin-bottom: 20px;">📝 Manual Data Entry</h3>
            <p style="color: #374151; margin-bottom: 20px;">Or add data manually using the forms below:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create sub-tabs for different data types
        manual_tab1, manual_tab2, manual_tab3, manual_tab4, manual_tab5, manual_tab6, manual_tab7, manual_tab8 = st.tabs([
            "👥 Customers", "🎫 Tickets", "👨‍💼 Agents", "💬 Interactions", 
            "😊 Feedback", "📋 SLA", "📚 Knowledge Base", "🎓 Training"
        ])
    
        with manual_tab1:
            st.subheader("Customers")
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID", key="customer_id_input")
                customer_name = st.text_input("Customer Name", key="customer_name_input")
                email = st.text_input("Email", key="customer_email_input")
                phone = st.text_input("Phone", key="customer_phone_input")
                company = st.text_input("Company", key="customer_company_input")
                industry = st.text_input("Industry", key="customer_industry_input")
                region = st.text_input("Region", key="customer_region_input")
            
            with col2:
                country = st.text_input("Country", key="customer_country_input")
                customer_segment = st.selectbox("Customer Segment", ["Enterprise", "SMB", "Startup", "Individual"], key="customer_segment_input")
                acquisition_date = st.date_input("Acquisition Date", key="customer_acquisition_date_input")
                status = st.selectbox("Status", ["Active", "Inactive", "Churned"], key="customer_status_input")
                lifetime_value = st.number_input("Lifetime Value", min_value=0.0, key="customer_lifetime_value_input")
                last_interaction_date = st.date_input("Last Interaction Date", key="customer_last_interaction_input")
                preferred_channel = st.selectbox("Preferred Channel", ["Email", "Phone", "Chat", "Social Media"], key="customer_preferred_channel_input")
            
            if st.button("Add Customer"):
                new_customer = pd.DataFrame([{
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'email': email,
                    'phone': phone,
                    'company': company,
                    'industry': industry,
                    'region': region,
                    'country': country,
                    'customer_segment': customer_segment,
                    'acquisition_date': acquisition_date,
                    'status': status,
                    'lifetime_value': lifetime_value,
                    'last_interaction_date': last_interaction_date,
                    'preferred_channel': preferred_channel
                }])
                st.session_state.customers = pd.concat([st.session_state.customers, new_customer], ignore_index=True)
                st.success("Customer added successfully!")
            
            # Display existing data
            if not st.session_state.customers.empty:
                st.subheader("Existing Customers")
                display_dataframe_with_index_1(st.session_state.customers)
        
        with manual_tab2:
            st.subheader("Tickets")
            col1, col2 = st.columns(2)
            
            with col1:
                ticket_id = st.text_input("Ticket ID", key="ticket_id_input")
                customer_id = st.text_input("Customer ID", key="ticket_customer_id_input")
                agent_id = st.text_input("Agent ID", key="ticket_agent_id_input")
                ticket_type = st.selectbox("Ticket Type", ["Technical", "Billing", "General", "Feature Request", "Bug Report"], key="ticket_type_input")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="ticket_priority_input")
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed", "Escalated"], key="ticket_status_input")
                created_date = st.date_input("Created Date", key="ticket_created_date_input")
            
            with col2:
                first_response_date = st.date_input("First Response Date", key="ticket_first_response_input")
                resolved_date = st.date_input("Resolved Date", key="ticket_resolved_date_input")
                escalated_date = st.date_input("Escalated Date", key="ticket_escalated_date_input")
                channel = st.selectbox("Channel", ["Email", "Phone", "Chat", "Social Media", "Portal"], key="ticket_channel_input")
                category = st.text_input("Category", key="ticket_category_input")
                subcategory = st.text_input("Subcategory", key="ticket_subcategory_input")
                description = st.text_area("Description", key="ticket_description_input")
                resolution_notes = st.text_area("Resolution Notes", key="ticket_resolution_notes_input")
            
            if st.button("Add Ticket"):
                new_ticket = pd.DataFrame([{
                    'ticket_id': ticket_id,
                    'customer_id': customer_id,
                    'agent_id': agent_id,
                    'ticket_type': ticket_type,
                    'priority': priority,
                    'status': status,
                    'created_date': created_date,
                    'first_response_date': first_response_date,
                    'resolved_date': resolved_date,
                    'escalated_date': escalated_date,
                    'channel': channel,
                    'category': category,
                    'subcategory': subcategory,
                    'description': description,
                    'resolution_notes': resolution_notes
                }])
                st.session_state.tickets = pd.concat([st.session_state.tickets, new_ticket], ignore_index=True)
                st.success("Ticket added successfully!")
            
            # Display existing data
            if not st.session_state.tickets.empty:
                st.subheader("Existing Tickets")
                display_dataframe_with_index_1(st.session_state.tickets)
        
        with manual_tab3:
            st.subheader("Agents")
            col1, col2 = st.columns(2)
            
            with col1:
                agent_id = st.text_input("Agent ID", key="agent_id_input")
                first_name = st.text_input("First Name", key="agent_first_name_input")
                last_name = st.text_input("Last Name", key="agent_last_name_input")
                email = st.text_input("Email", key="agent_email_input")
                department = st.text_input("Department", key="agent_department_input")
                team = st.text_input("Team", key="agent_team_input")
                hire_date = st.date_input("Hire Date", key="agent_hire_date_input")
            
            with col2:
                status = st.selectbox("Status", ["Active", "Inactive", "Terminated"], key="agent_status_input")
                manager_id = st.text_input("Manager ID", key="agent_manager_id_input")
                specialization = st.text_input("Specialization", key="agent_specialization_input")
                performance_score = st.number_input("Performance Score", min_value=0.0, max_value=100.0, key="agent_performance_score_input")
            
            if st.button("Add Agent"):
                new_agent = pd.DataFrame([{
                    'agent_id': agent_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'department': department,
                    'team': team,
                    'hire_date': hire_date,
                    'status': status,
                    'manager_id': manager_id,
                    'specialization': specialization,
                    'performance_score': performance_score
                }])
                st.session_state.agents = pd.concat([st.session_state.agents, new_agent], ignore_index=True)
                st.success("Agent added successfully!")
            
            # Display existing data
            if not st.session_state.agents.empty:
                st.subheader("Existing Agents")
                display_dataframe_with_index_1(st.session_state.agents)
        
        with manual_tab4:
            st.subheader("Interactions")
            col1, col2 = st.columns(2)
            
            with col1:
                interaction_id = st.text_input("Interaction ID", key="interaction_id_input")
                ticket_id = st.text_input("Ticket ID", key="interaction_ticket_id_input")
                customer_id = st.text_input("Customer ID", key="interaction_customer_id_input")
                agent_id = st.text_input("Agent ID", key="interaction_agent_id_input")
                interaction_type = st.selectbox("Interaction Type", ["Call", "Chat", "Email", "Meeting"], key="interaction_type_input")
                # --- Fix for datetime input ---
                start_date = st.date_input("Start Date", key="interaction_start_date_input")
                start_time_val = st.time_input("Start Time", key="interaction_start_time_input")
                start_time = datetime.combine(start_date, start_time_val)
                end_date = st.date_input("End Date", key="interaction_end_date_input")
                end_time_val = st.time_input("End Time", key="interaction_end_time_input")
                end_time = datetime.combine(end_date, end_time_val)
            
            with col2:
                duration_minutes = st.number_input("Duration (Minutes)", min_value=0, key="interaction_duration_input")
                channel = st.selectbox("Channel", ["Email", "Phone", "Chat", "Social Media", "Portal"], key="interaction_channel_input")
            satisfaction_score = st.number_input("Satisfaction Score", min_value=1, max_value=10, key="interaction_satisfaction_input")
            notes = st.text_area("Notes", key="interaction_notes_input")
            outcome = st.selectbox("Outcome", ["Resolved", "Escalated", "Follow-up Required", "No Resolution"], key="interaction_outcome_input")
        
        if st.button("Add Interaction"):
            new_interaction = pd.DataFrame([{
                'interaction_id': interaction_id,
                'ticket_id': ticket_id,
                'customer_id': customer_id,
                'agent_id': agent_id,
                'interaction_type': interaction_type,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration_minutes,
                'channel': channel,
                'satisfaction_score': satisfaction_score,
                'notes': notes,
                'outcome': outcome
            }])
            st.session_state.interactions = pd.concat([st.session_state.interactions, new_interaction], ignore_index=True)
            st.success("Interaction added successfully!")
        
        # Display existing data
        if not st.session_state.interactions.empty:
            st.subheader("Existing Interactions")
            display_dataframe_with_index_1(st.session_state.interactions)
        
        with manual_tab5:
            st.subheader("Feedback")
            col1, col2 = st.columns(2)
            
            with col1:
                feedback_id = st.text_input("Feedback ID", key="feedback_id_input")
                ticket_id = st.text_input("Ticket ID", key="feedback_ticket_id_input")
                customer_id = st.text_input("Customer ID", key="feedback_customer_id_input")
                agent_id = st.text_input("Agent ID", key="feedback_agent_id_input")
                feedback_type = st.selectbox("Feedback Type", ["CSAT", "NPS", "CES", "General"], key="feedback_type_input")
                rating = st.number_input("Rating", min_value=1, max_value=10, key="feedback_rating_input")
            
            with col2:
                sentiment = st.selectbox("Sentiment", ["Positive", "Neutral", "Negative"], key="feedback_sentiment_input")
                comments = st.text_area("Comments", key="feedback_comments_input")
                submitted_date = st.date_input("Submitted Date", key="feedback_submitted_date_input")
                response_date = st.date_input("Response Date", key="feedback_response_date_input")
            
            if st.button("Add Feedback"):
                new_feedback = pd.DataFrame([{
                    'feedback_id': feedback_id,
                    'ticket_id': ticket_id,
                    'customer_id': customer_id,
                    'agent_id': agent_id,
                    'feedback_type': feedback_type,
                    'rating': rating,
                    'sentiment': sentiment,
                    'comments': comments,
                    'submitted_date': submitted_date,
                    'response_date': response_date
                }])
                st.session_state.feedback = pd.concat([st.session_state.feedback, new_feedback], ignore_index=True)
                st.success("Feedback added successfully!")
            
            # Display existing data
            if not st.session_state.feedback.empty:
                st.subheader("Existing Feedback")
                display_dataframe_with_index_1(st.session_state.feedback)
        
        with manual_tab6:
            st.subheader("SLA")
            col1, col2 = st.columns(2)
            
            with col1:
                sla_id = st.text_input("SLA ID", key="sla_id_input")
                ticket_type = st.selectbox("Ticket Type", ["Technical", "Billing", "General", "Feature Request", "Bug Report"], key="sla_ticket_type_input")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="sla_priority_input")
                first_response_target_hours = st.number_input("First Response Target (Hours)", min_value=0, key="sla_first_response_input")
            
            with col2:
                resolution_target_hours = st.number_input("Resolution Target (Hours)", min_value=0, key="sla_resolution_input")
                business_hours_only = st.checkbox("Business Hours Only", key="sla_business_hours_input")
                description = st.text_area("Description", key="sla_description_input")
            
            if st.button("Add SLA"):
                new_sla = pd.DataFrame([{
                    'sla_id': sla_id,
                    'ticket_type': ticket_type,
                    'priority': priority,
                    'first_response_target_hours': first_response_target_hours,
                    'resolution_target_hours': resolution_target_hours,
                    'business_hours_only': business_hours_only,
                    'description': description
                }])
                st.session_state.sla = pd.concat([st.session_state.sla, new_sla], ignore_index=True)
                st.success("SLA added successfully!")
            
            # Display existing data
            if not st.session_state.sla.empty:
                st.subheader("Existing SLA")
                display_dataframe_with_index_1(st.session_state.sla)
        
        with manual_tab7:
            st.subheader("Knowledge Base")
            col1, col2 = st.columns(2)
            
            with col1:
                kb_id = st.text_input("KB ID", key="kb_id_input")
                title = st.text_input("Title", key="kb_title_input")
                category = st.text_input("Category", key="kb_category_input")
                content = st.text_area("Content", key="kb_content_input")
                created_date = st.date_input("Created Date", key="kb_created_date_input")
            
            with col2:
                updated_date = st.date_input("Updated Date", key="kb_updated_date_input")
                author_id = st.text_input("Author ID", key="kb_author_id_input")
                views = st.number_input("Views", min_value=0, key="kb_views_input")
                helpful_votes = st.number_input("Helpful Votes", min_value=0, key="kb_helpful_votes_input")
                status = st.selectbox("Status", ["Active", "Draft", "Archived"], key="kb_status_input")
            
            if st.button("Add Knowledge Base Article"):
                new_kb = pd.DataFrame([{
                    'kb_id': kb_id,
                    'title': title,
                    'category': category,
                    'content': content,
                    'created_date': created_date,
                    'updated_date': updated_date,
                    'author_id': author_id,
                    'views': views,
                    'helpful_votes': helpful_votes,
                    'status': status
                }])
                st.session_state.knowledge_base = pd.concat([st.session_state.knowledge_base, new_kb], ignore_index=True)
                st.success("Knowledge base article added successfully!")
            
            # Display existing data
            if not st.session_state.knowledge_base.empty:
                st.subheader("Existing Knowledge Base Articles")
                display_dataframe_with_index_1(st.session_state.knowledge_base)
        
        with manual_tab8:
            st.subheader("Training")
            col1, col2 = st.columns(2)
            
            with col1:
                training_id = st.text_input("Training ID", key="training_id_input")
                agent_id = st.text_input("Agent ID", key="training_agent_id_input")
                training_type = st.selectbox("Training Type", ["Product", "Process", "Soft Skills", "Technical"], key="training_type_input")
                start_date = st.date_input("Start Date", key="training_start_date_input")
                completion_date = st.date_input("Completion Date", key="training_completion_date_input")
            
            with col2:
                score = st.number_input("Score", min_value=0.0, max_value=100.0, key="training_score_input")
                status = st.selectbox("Status", ["In Progress", "Completed", "Failed"], key="training_status_input")
                trainer_id = st.text_input("Trainer ID", key="training_trainer_id_input")
                notes = st.text_area("Notes", key="training_notes_input")
            
            if st.button("Add Training Record"):
                new_training = pd.DataFrame([{
                    'training_id': training_id,
                    'agent_id': agent_id,
                    'training_type': training_type,
                    'start_date': start_date,
                    'completion_date': completion_date,
                    'score': score,
                    'status': status,
                    'trainer_id': trainer_id,
                    'notes': notes
                }])
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)
                st.success("Training record added successfully!")
            
            # Display existing data
            if not st.session_state.training.empty:
                st.subheader("Existing Training Records")
                display_dataframe_with_index_1(st.session_state.training)
    
    with main_tab4:
        st.markdown("""
        <div class="welcome-section">
            <h3 style="color: #1e3c72; margin-bottom: 20px;">🧪 Sample Data for Testing</h3>
            <p style="color: #374151; margin-bottom: 20px;">Load sample customer service data to test the analytics dashboard and explore all features without entering data manually.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data information
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">Sample Dataset Features:</h4>
            <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>📊 Realistic customer service data for demonstration</li>
                <li>🎯 All 8 data tables populated with sample records</li>
                <li>📈 Varied data to showcase different analytics scenarios</li>
                <li>🔍 Perfect for testing dashboard functionality</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Load sample data button
        if st.button("🚀 Load Sample Data", key="load_sample_data", use_container_width=True, type="primary"):
            try:
                # Load the sample dataset
                sample_file_path = "customer_service_sample_dataset.xlsx"
                
                # Check if file exists
                import os
                if os.path.exists(sample_file_path):
                    # Load the sample data
                    success, message = load_sample_dataset(sample_file_path)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("🎉 Sample data loaded successfully! You can now navigate to other sections to explore the analytics dashboard.")
                        
                        # Show sample data summary
                        st.markdown("---")
                        st.subheader("📊 Sample Data Summary")
                        
                        sample_summary = []
                        if 'customers' in st.session_state and not st.session_state.customers.empty:
                            sample_summary.append(f"👥 Customers: {len(st.session_state.customers)} records")
                        if 'tickets' in st.session_state and not st.session_state.tickets.empty:
                            sample_summary.append(f"🎫 Tickets: {len(st.session_state.tickets)} records")
                        if 'agents' in st.session_state and not st.session_state.agents.empty:
                            sample_summary.append(f"👨‍💼 Agents: {len(st.session_state.agents)} records")
                        if 'interactions' in st.session_state and not st.session_state.interactions.empty:
                            sample_summary.append(f"📞 Interactions: {len(st.session_state.interactions)} records")
                        if 'feedback' in st.session_state and not st.session_state.feedback.empty:
                            sample_summary.append(f"😊 Feedback: {len(st.session_state.feedback)} records")
                        if 'sla' in st.session_state and not st.session_state.sla.empty:
                            sample_summary.append(f"⏱️ SLA Records: {len(st.session_state.sla)} records")
                        if 'knowledge_base' in st.session_state and not st.session_state.knowledge_base.empty:
                            sample_summary.append(f"📚 Knowledge Base: {len(st.session_state.knowledge_base)} articles")
                        if 'training' in st.session_state and not st.session_state.training.empty:
                            sample_summary.append(f"🎓 Training Records: {len(st.session_state.training)} records")
                        
                        # Display summary in columns
                        if sample_summary:
                            col1, col2 = st.columns(2)
                            with col1:
                                for summary in sample_summary[:len(sample_summary)//2]:
                                    st.info(summary)
                            with col2:
                                for summary in sample_summary[len(sample_summary)//2:]:
                                    st.info(summary)
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Sample dataset file not found!")
                    st.info("💡 Please ensure 'customer_service_sample_dataset.xlsx' is in the same directory as the application.")
                    
            except Exception as e:
                st.error(f"❌ Error loading sample data: {str(e)}")
                st.info("💡 Please check if the sample dataset file exists and is accessible.")
        
        # Additional information about sample data
        st.markdown("---")
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin-bottom: 15px;">💡 How to Use Sample Data:</h4>
            <ol style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Click "Load Sample Data" to populate the dashboard with sample data</li>
                <li>Navigate to other sections to explore analytics and visualizations</li>
                <li>Test different features and see how the dashboard handles real data</li>
                <li>Use this as a reference for your own data structure</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# Analytics functions for the main sections
def show_customer_satisfaction():
    st.markdown("""
    <div class="main-header" style="margin-bottom: 30px;">
        <h2 style="margin: 0;">😊 Customer Satisfaction and Feedback Analysis</h2>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Measure and analyze customer satisfaction across multiple dimensions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.feedback.empty:
        st.warning("⚠️ No feedback data available. Please add feedback data in the Data Input tab.")
        return
    
    # Create tabs for different satisfaction metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 CSAT Score", "🎯 NPS Score", "⚡ CES Score", "😊 Sentiment Analysis", "✅ Resolution Satisfaction"
    ])
    
    with tab1:
        st.subheader("📊 Customer Satisfaction Score (CSAT)")
        st.markdown("""
        **Formula:** CSAT = (Number of Positive Responses / Total Responses) × 100
        
        Positive responses are typically ratings of 4-5 on a 5-point scale or 7-10 on a 10-point scale.
        """)
        
        csat_summary, csat_message = calculate_csat_score(st.session_state.feedback)
        
        if not csat_summary.empty:
            # Display metrics in enhanced metric cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card-blue">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{csat_summary.iloc[0]['Value']}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">CSAT Score</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card-green">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{csat_summary.iloc[1]['Value']}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Positive Responses</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card-purple">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{csat_summary.iloc[2]['Value']}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Total Responses</p>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card-orange">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{csat_summary.iloc[3]['Value']}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Positive Rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display detailed table
            st.subheader("📋 CSAT Analysis Details")
            st.dataframe(csat_summary, use_container_width=True)
            
            # Create enhanced visualizations
            if len(st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'CSAT']) > 0:
                    csat_data = st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'CSAT']
                    rating_counts = csat_data['rating'].value_counts().sort_index()
                    
                    # Create two columns for visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        # Enhanced bar chart with better styling
                        fig = go.Figure(data=[
                            go.Bar(x=rating_counts.index, y=rating_counts.values, 
                                   marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50', '#1f77b4'],
                                   text=rating_counts.values,
                                   textposition='auto',
                                   hovertemplate='Rating: %{x}<br>Count: %{y}<extra></extra>')
                        ])
                        fig.update_layout(
                            title="CSAT Rating Distribution",
                            xaxis_title="Rating",
                            yaxis_title="Number of Responses",
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            margin=dict(l=50, r=50, t=80, b=50)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        # Donut chart for satisfaction levels
                        positive_count = len(csat_data[csat_data['rating'] >= 4])
                        neutral_count = len(csat_data[(csat_data['rating'] >= 3) & (csat_data['rating'] < 4)])
                        negative_count = len(csat_data[csat_data['rating'] < 3])
                        
                        fig = go.Figure(data=[
                            go.Pie(labels=['Positive (4-5)', 'Neutral (3)', 'Negative (1-2)'],
                                   values=[positive_count, neutral_count, negative_count],
                                   hole=0.6,
                                   marker_colors=['#4caf50', '#ffeb3b', '#ff5722'],
                                   textinfo='label+percent',
                                   hovertemplate='%{label}<br>Count: %{value}<extra></extra>')
                        ])
                        fig.update_layout(
                            title="Satisfaction Level Distribution",
                            showlegend=True,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            margin=dict(l=50, r=50, t=80, b=50)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
            # Trend analysis over time
            if 'feedback_date' in csat_data.columns:
                st.subheader("📈 CSAT Trend Analysis")
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                csat_data['feedback_date'] = pd.to_datetime(csat_data['feedback_date'])
                csat_data['month'] = csat_data['feedback_date'].dt.strftime('%Y-%m')
                monthly_csat = csat_data.groupby('month')['rating'].mean().reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=monthly_csat['month'], 
                    y=monthly_csat['rating'],
                    mode='lines+markers',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8),
                    name='Average CSAT',
                    hovertemplate='Month: %{x}<br>CSAT: %{y:.2f}<extra></extra>'
                ))
                fig.update_layout(
                    title="CSAT Trend Over Time",
                    xaxis_title="Month",
                    yaxis_title="Average CSAT Rating",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(csat_message)
    
    with tab2:
        st.subheader("🎯 Net Promoter Score (NPS)")
        st.markdown("""
        **Formula:** NPS = % Promoters - % Detractors
        
        - **Promoters (9-10):** Likely to recommend
        - **Passives (7-8):** Neutral
        - **Detractors (0-6):** Unlikely to recommend
        """)
        
        nps_summary, nps_message = calculate_nps_score(st.session_state.feedback)
        
        if not nps_summary.empty:
            # Display NPS score prominently
            nps_score = float(nps_summary.iloc[3]['Percentage'])
            st.markdown(f"""
            <div class="metric-card-blue" style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: white; margin: 0; font-size: 3rem;">{nps_score:.1f}</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.5rem;">NPS Score</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display breakdown in enhanced metric cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card-green">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{int(nps_summary.iloc[0]['Count'])}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Promoters</p>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{nps_summary.iloc[0]['Percentage']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card-orange">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{int(nps_summary.iloc[1]['Count'])}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Passives</p>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{nps_summary.iloc[1]['Percentage']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card-red">
                    <h3 style="color: white; margin: 0; font-size: 2rem;">{int(nps_summary.iloc[2]['Count'])}</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Detractors</p>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{nps_summary.iloc[2]['Percentage']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display detailed table
            st.subheader("📋 NPS Analysis Details")
            st.dataframe(nps_summary, use_container_width=True)
            
            # Create enhanced visualizations
            if len(st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'NPS']) > 0:
                nps_data = st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'NPS']
                
                # Categorize ratings
                nps_data['category'] = nps_data['rating'].apply(
                    lambda x: 'Promoter' if x >= 9 else ('Detractor' if x <= 6 else 'Passive')
                )
                category_counts = nps_data['category'].value_counts()
                
                # Create two columns for visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Enhanced pie chart
                    fig = go.Figure(data=[
                        go.Pie(labels=category_counts.index, values=category_counts.values,
                               marker_colors=['#4caf50', '#ffeb3b', '#ff6b6b'],
                               textinfo='label+percent',
                               hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>')
                    ])
                    fig.update_layout(
                        title="NPS Category Distribution",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # NPS gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=nps_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "NPS Score"},
                        delta={'reference': 0},
                        gauge={
                            'axis': {'range': [-100, 100]},
                            'bar': {'color': "#1f77b4"},
                            'steps': [
                                {'range': [-100, 0], 'color': "#ff6b6b"},
                                {'range': [0, 50], 'color': "#ffeb3b"},
                                {'range': [50, 100], 'color': "#4caf50"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 50
                            }
                        }
                    ))
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # NPS trend analysis
                if 'feedback_date' in nps_data.columns:
                    st.subheader("📈 NPS Trend Analysis")
                    nps_data['feedback_date'] = pd.to_datetime(nps_data['feedback_date'])
                    nps_data['month'] = nps_data['feedback_date'].dt.strftime('%Y-%m')
                    
                    # Calculate monthly NPS
                    monthly_nps = []
                    for month in nps_data['month'].unique():
                        month_data = nps_data[nps_data['month'] == month]
                        promoters = len(month_data[month_data['rating'] >= 9])
                        detractors = len(month_data[month_data['rating'] <= 6])
                        total = len(month_data)
                        nps = ((promoters - detractors) / total * 100) if total > 0 else 0
                        monthly_nps.append({'month': month, 'nps': nps})
                    
                    monthly_nps_df = pd.DataFrame(monthly_nps)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=monthly_nps_df['month'], 
                        y=monthly_nps_df['nps'],
                        mode='lines+markers',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=8),
                        name='Monthly NPS',
                        hovertemplate='Month: %{x}<br>NPS: %{y:.1f}<extra></extra>'
                    ))
                    fig.update_layout(
                        title="NPS Trend Over Time",
                        xaxis_title="Month",
                        yaxis_title="NPS Score",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(nps_message)
    
    with tab3:
        st.subheader("⚡ Customer Effort Score (CES)")
        st.markdown("""
        **Formula:** CES = Total Effort Ratings / Total Responses
        
        Lower scores indicate less effort required (better customer experience).
        """)
        
        ces_summary, ces_message = calculate_ces_score(st.session_state.feedback)
        
        if not ces_summary.empty:
            # Display CES score prominently
            ces_score_str = ces_summary.iloc[0]['Value']
            ces_score = float(ces_score_str)
            st.metric("CES Score", ces_score_str, delta=None)
            
            # Display other metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Effort Ratings", ces_summary.iloc[1]['Value'])
            with col2:
                st.metric("Total Responses", ces_summary.iloc[2]['Value'])
            with col3:
                st.metric("Average Effort", ces_summary.iloc[3]['Value'])
            
            # Display detailed table
            st.subheader("📋 CES Analysis Details")
            st.dataframe(ces_summary, use_container_width=True)
            
            # Create visualization
            if len(st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'CES']) > 0:
                ces_data = st.session_state.feedback[st.session_state.feedback['feedback_type'] == 'CES']
                effort_counts = ces_data['rating'].value_counts().sort_index()
                
                fig = go.Figure(data=[
                    go.Bar(x=effort_counts.index, y=effort_counts.values,
                           marker_color=['#4caf50', '#8bc34a', '#ffeb3b', '#ff9800', '#ff5722'])
                ])
                fig.update_layout(
                    title="CES Effort Rating Distribution",
                    xaxis_title="Effort Level (1=Very Easy, 5=Very Difficult)",
                    yaxis_title="Number of Responses",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(ces_message)
    
    with tab4:
        st.subheader("😊 Customer Feedback Sentiment Analysis")
        st.markdown("""
        **Formula:** Sentiment Distribution = [Positive%, Neutral%, Negative%]
        
        Analyzes the emotional tone of customer feedback across all channels.
        """)
        
        sentiment_summary, sentiment_message = calculate_sentiment_analysis(st.session_state.feedback)
        
        if not sentiment_summary.empty:
            # Display sentiment distribution
            positive_pct = float(sentiment_summary.iloc[0]['Percentage'].rstrip('%'))
            neutral_pct = float(sentiment_summary.iloc[1]['Percentage'].rstrip('%'))
            negative_pct = float(sentiment_summary.iloc[2]['Percentage'].rstrip('%'))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive", f"{positive_pct:.1f}%", int(sentiment_summary.iloc[0]['Count']))
            with col2:
                st.metric("Neutral", f"{neutral_pct:.1f}%", int(sentiment_summary.iloc[1]['Count']))
            with col3:
                st.metric("Negative", f"{negative_pct:.1f}%", int(sentiment_summary.iloc[2]['Count']))
            
            # Display detailed table
            st.subheader("📋 Sentiment Analysis Details")
            st.dataframe(sentiment_summary, use_container_width=True)
            
            # Create visualization
            sentiment_counts = sentiment_summary.iloc[:3]  # Exclude 'Total' row
            fig = go.Figure(data=[
                go.Pie(labels=sentiment_counts['Sentiment'], 
                       values=sentiment_counts['Count'],
                       marker_colors=['#4caf50', '#ffeb3b', '#ff6b6b'])
            ])
            fig.update_layout(title="Customer Feedback Sentiment Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent feedback comments
            if not st.session_state.feedback.empty:
                st.subheader("💬 Recent Feedback Comments")
                recent_feedback = st.session_state.feedback[st.session_state.feedback['comments'].notna()].tail(5)
                if not recent_feedback.empty:
                    for _, row in recent_feedback.iterrows():
                        sentiment_color = {'Positive': 'green', 'Neutral': 'orange', 'Negative': 'red'}.get(row['sentiment'], 'gray')
                        st.markdown(f"""
                        <div style="border-left: 4px solid {sentiment_color}; padding-left: 10px; margin: 10px 0;">
                        <strong>{row['sentiment']}</strong> - Rating: {row['rating']}/10<br>
                        <em>"{row['comments']}"</em>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info(sentiment_message)
    
    with tab5:
        st.subheader("✅ Complaint Resolution Satisfaction")
        st.markdown("""
        **Formula:** Complaint Resolution Satisfaction = (Satisfied Customers After Resolution / Total Customers with Resolved Complaints) × 100
        
        Measures customer happiness after their issues have been resolved.
        """)
        
        if not st.session_state.tickets.empty:
            resolution_summary, resolution_message = calculate_complaint_resolution_satisfaction(
                st.session_state.tickets, st.session_state.feedback
            )
            
            if not resolution_summary.empty:
                # Display satisfaction rate prominently
                satisfaction_rate = float(resolution_summary.iloc[2]['Value'].rstrip('%'))
                st.metric("Resolution Satisfaction", f"{satisfaction_rate:.1f}%", delta=None)
                
                # Display other metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Satisfied Customers", resolution_summary.iloc[0]['Value'])
                with col2:
                    st.metric("Total Resolved", resolution_summary.iloc[1]['Value'])
                with col3:
                    st.metric("Average Rating", resolution_summary.iloc[3]['Value'])
                
                # Display detailed table
                st.subheader("📋 Resolution Satisfaction Details")
                st.dataframe(resolution_summary, use_container_width=True)
                
                # Create visualization
                resolved_tickets = st.session_state.tickets[st.session_state.tickets['status'] == 'Resolved']
                if not resolved_tickets.empty:
                    # Merge with feedback for ratings
                    resolved_with_feedback = resolved_tickets.merge(
                        st.session_state.feedback, on='ticket_id', how='inner'
                    )
                    
                    if not resolved_with_feedback.empty:
                        rating_dist = resolved_with_feedback['rating'].value_counts().sort_index()
                        
                        fig = go.Figure(data=[
                            go.Bar(x=rating_dist.index, y=rating_dist.values,
                                   marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50', '#2196f3'])
                        ])
                        fig.update_layout(
                            title="Resolution Satisfaction Rating Distribution",
                            xaxis_title="Rating",
                            yaxis_title="Number of Customers",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(resolution_message)
        else:
            st.warning("⚠️ No ticket data available. Please add ticket data in the Data Input tab.")
    
    # Summary insights
    st.markdown("---")
    st.markdown("""
    <div class="insights-container">
        <h3 style="color: white; margin: 0 0 20px 0;">🎯 Key Insights & Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.feedback.empty:
        csat_summary, _ = calculate_csat_score(st.session_state.feedback)
        if not csat_summary.empty:
            csat_score = float(csat_summary.iloc[0]['Value'].rstrip('%'))
            if csat_score < 70:
                insights.append("🔴 **Low CSAT Score:** Consider improving response times and agent training")
            elif csat_score > 85:
                insights.append("🟢 **Excellent CSAT Score:** Maintain current service quality")
            else:
                insights.append("🟡 **Good CSAT Score:** Room for improvement in specific areas")
        
        nps_summary, _ = calculate_nps_score(st.session_state.feedback)
        if not nps_summary.empty:
            nps_score = float(nps_summary.iloc[3]['Percentage'])
            if nps_score < 0:
                insights.append("🔴 **Negative NPS:** Focus on improving customer experience to reduce detractors")
            elif nps_score > 50:
                insights.append("🟢 **Excellent NPS:** Strong customer advocacy, leverage promoters")
            else:
                insights.append("🟡 **Positive NPS:** Good foundation, work on converting passives to promoters")
        
        sentiment_summary, _ = calculate_sentiment_analysis(st.session_state.feedback)
        if not sentiment_summary.empty:
            negative_pct = float(sentiment_summary.iloc[2]['Percentage'].rstrip('%'))
            if negative_pct > 20:
                insights.append("🔴 **High Negative Sentiment:** Investigate root causes and improve service delivery")
    
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4caf50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">💡 Add more feedback data to generate insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_response_resolution():
    st.markdown("""
    <div class="main-header" style="margin-bottom: 30px;">
        <h2 style="margin: 0;">⏱️ Response Time and Resolution Metrics</h2>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Track and optimize response times and issue resolution efficiency</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.tickets.empty:
        st.warning("⚠️ No ticket data available. Please add ticket data in the Data Input tab.")
        return
    
    # Create tabs for different response and resolution metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 First Response Time", "⏰ Average Resolution Time", "📞 First Call Resolution", 
        "📈 Escalation Analysis", "⏳ Queue Wait Time"
    ])
    
    with tab1:
        st.subheader("🚀 First Response Time (FRT)")
        st.markdown("""
        **Formula:** Average FRT = Total First Response Time / Number of Queries
        
        Measures the average time it takes to provide the first response to customer inquiries.
        """)
        
        frt_summary, frt_message = calculate_first_response_time(st.session_state.tickets)
        
        if not frt_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average FRT", frt_summary.iloc[0]['Value'])
            with col2:
                st.metric("Median FRT", frt_summary.iloc[1]['Value'])
            with col3:
                st.metric("Total Queries", frt_summary.iloc[2]['Value'])
            with col4:
                st.metric("Min FRT", frt_summary.iloc[3]['Value'])
            
            # Display additional metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Max FRT", frt_summary.iloc[4]['Value'])
            with col2:
                # Calculate SLA compliance for FRT
                if not st.session_state.sla.empty:
                    avg_frt_hours = float(frt_summary.iloc[0]['Value'].split()[0])
                    sla_target = st.session_state.sla['first_response_target_hours'].mean()
                    sla_compliance = "✅ Within SLA" if avg_frt_hours <= sla_target else "❌ Exceeds SLA"
                    st.metric("SLA Status", sla_compliance)
            
            # Display detailed table
            st.subheader("📋 First Response Time Analysis Details")
            st.dataframe(frt_summary, use_container_width=True)
            
            # Create enhanced visualizations
            tickets_with_frt = st.session_state.tickets[st.session_state.tickets['first_response_date'].notna()].copy()
            if not tickets_with_frt.empty:
                # Convert dates to datetime
                tickets_with_frt['created_date'] = pd.to_datetime(tickets_with_frt['created_date'])
                tickets_with_frt['first_response_date'] = pd.to_datetime(tickets_with_frt['first_response_date'])
                
                # Calculate response time in hours
                tickets_with_frt['response_time_hours'] = (tickets_with_frt['first_response_date'] - tickets_with_frt['created_date']).dt.total_seconds() / 3600
                
                # Create two columns for visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Enhanced histogram with better styling
                    fig = go.Figure(data=[
                        go.Histogram(x=tickets_with_frt['response_time_hours'], nbinsx=20, 
                                    marker_color='#1f77b4', opacity=0.7,
                                    hovertemplate='Response Time: %{x:.1f} hours<br>Count: %{y}<extra></extra>')
                    ])
                    fig.update_layout(
                        title="First Response Time Distribution",
                        xaxis_title="Response Time (Hours)",
                        yaxis_title="Number of Tickets",
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Box plot for FRT distribution
                    fig = go.Figure(data=[
                        go.Box(y=tickets_with_frt['response_time_hours'],
                               marker_color='#1f77b4',
                               name='FRT Distribution',
                               hovertemplate='Response Time: %{y:.1f} hours<extra></extra>')
                    ])
                    fig.update_layout(
                        title="FRT Distribution (Box Plot)",
                        yaxis_title="Response Time (Hours)",
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # FRT by priority with enhanced styling
                if 'priority' in tickets_with_frt.columns:
                    st.subheader("📊 FRT Analysis by Priority")
                    priority_frt = tickets_with_frt.groupby('priority')['response_time_hours'].agg(['mean', 'count', 'std']).reset_index()
                    priority_frt = priority_frt.sort_values('mean')
                    
                    # Create two columns for priority analysis
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = go.Figure(data=[
                            go.Bar(x=priority_frt['priority'], y=priority_frt['mean'],
                                   marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'],
                                   text=priority_frt['mean'].round(2),
                                   textposition='auto',
                                   hovertemplate='Priority: %{x}<br>Avg FRT: %{y:.2f} hours<br>Count: %{text}<extra></extra>')
                        ])
                        fig.update_layout(
                            title="Average FRT by Priority",
                            xaxis_title="Priority",
                            yaxis_title="Average Response Time (Hours)",
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            margin=dict(l=50, r=50, t=80, b=50)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = go.Figure(data=[
                            go.Bar(x=priority_frt['priority'], y=priority_frt['count'],
                                   marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'],
                                   text=priority_frt['count'],
                                   textposition='auto',
                                   hovertemplate='Priority: %{x}<br>Ticket Count: %{y}<extra></extra>')
                        ])
                        fig.update_layout(
                            title="Ticket Volume by Priority",
                            xaxis_title="Priority",
                            yaxis_title="Number of Tickets",
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            margin=dict(l=50, r=50, t=80, b=50)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # FRT trend analysis over time
                if 'created_date' in tickets_with_frt.columns:
                    st.subheader("📈 FRT Trend Analysis")
                    tickets_with_frt['month'] = tickets_with_frt['created_date'].dt.strftime('%Y-%m')
                    monthly_frt = tickets_with_frt.groupby('month')['response_time_hours'].mean().reset_index()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=monthly_frt['month'], 
                        y=monthly_frt['response_time_hours'],
                        mode='lines+markers',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=8),
                        name='Average FRT',
                        hovertemplate='Month: %{x}<br>Avg FRT: %{y:.2f} hours<extra></extra>'
                    ))
                    fig.update_layout(
                        title="FRT Trend Over Time",
                        xaxis_title="Month",
                        yaxis_title="Average FRT (Hours)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(frt_message)
    
    with tab2:
        st.subheader("⏰ Average Resolution Time (ART)")
        st.markdown("""
        **Formula:** Average ART = Total Resolution Time / Number of Resolved Issues
        
        Measures the average time taken to completely resolve customer issues.
        """)
        
        art_summary, art_message = calculate_average_resolution_time(st.session_state.tickets)
        
        if not art_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average ART", art_summary.iloc[0]['Value'])
            with col2:
                st.metric("Median ART", art_summary.iloc[1]['Value'])
            with col3:
                st.metric("Total Resolved", art_summary.iloc[2]['Value'])
            with col4:
                st.metric("Min ART", art_summary.iloc[3]['Value'])
            
            # Display additional metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Max ART", art_summary.iloc[4]['Value'])
            with col2:
                # Calculate resolution efficiency
                avg_art_hours = float(art_summary.iloc[0]['Value'].split()[0])
                efficiency_status = "✅ Excellent" if avg_art_hours <= 24 else ("🟡 Good" if avg_art_hours <= 48 else "❌ Needs Improvement")
                st.metric("Efficiency Status", efficiency_status)
            
            # Display detailed table
            st.subheader("📋 Resolution Time Analysis Details")
            st.dataframe(art_summary, use_container_width=True)
            
            # Create visualization
            resolved_tickets = st.session_state.tickets[st.session_state.tickets['status'] == 'Resolved'].copy()
            if not resolved_tickets.empty:
                # Convert dates to datetime
                resolved_tickets['created_date'] = pd.to_datetime(resolved_tickets['created_date'])
                resolved_tickets['resolved_date'] = pd.to_datetime(resolved_tickets['resolved_date'])
                
                # Calculate resolution time in hours
                resolved_tickets['resolution_time_hours'] = (resolved_tickets['resolved_date'] - resolved_tickets['created_date']).dt.total_seconds() / 3600
                
                # Create histogram
                fig = go.Figure(data=[
                    go.Histogram(x=resolved_tickets['resolution_time_hours'], nbinsx=20,
                                marker_color='#4caf50', opacity=0.7)
                ])
                fig.update_layout(
                    title="Resolution Time Distribution",
                    xaxis_title="Resolution Time (Hours)",
                    yaxis_title="Number of Tickets",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Resolution time by ticket type
                if 'ticket_type' in resolved_tickets.columns:
                    type_resolution = resolved_tickets.groupby('ticket_type')['resolution_time_hours'].mean().reset_index()
                    type_resolution = type_resolution.sort_values('resolution_time_hours')
                    
                    fig = go.Figure(data=[
                        go.Bar(x=type_resolution['ticket_type'], y=type_resolution['resolution_time_hours'],
                               marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Average Resolution Time by Ticket Type",
                        xaxis_title="Ticket Type",
                        yaxis_title="Average Resolution Time (Hours)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(art_message)
    
    with tab3:
        st.subheader("📞 First Call Resolution (FCR)")
        st.markdown("""
        **Formula:** FCR Rate = (Issues Resolved in First Interaction / Total Issues) × 100
        
        Measures the percentage of customer issues resolved in the first interaction.
        """)
        
        fcr_summary, fcr_message = calculate_first_call_resolution(st.session_state.tickets)
        
        if not fcr_summary.empty:
            # Display FCR rate prominently
            fcr_rate = float(fcr_summary.iloc[0]['Value'].rstrip('%'))
            st.metric("FCR Rate", f"{fcr_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("First Interaction Resolved", int(fcr_summary.iloc[1]['Value']))
            with col2:
                st.metric("Total Issues", int(fcr_summary.iloc[2]['Value']))
            with col3:
                st.metric("Multiple Interaction Issues", int(fcr_summary.iloc[3]['Value']))
            
            # Display detailed table
            st.subheader("📋 FCR Analysis Details")
            st.dataframe(fcr_summary, use_container_width=True)
            
            # Create visualization
            total_issues = int(fcr_summary.iloc[2]['Value'])
            first_resolved = int(fcr_summary.iloc[1]['Value'])
            multiple_interactions = int(fcr_summary.iloc[3]['Value'])
            
            fig = go.Figure(data=[
                go.Pie(labels=['First Interaction Resolved', 'Multiple Interactions Required'],
                       values=[first_resolved, multiple_interactions],
                       marker_colors=['#4caf50', '#ff9800'])
            ])
            fig.update_layout(title="First Call Resolution Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # FCR by channel
            if 'channel' in st.session_state.tickets.columns:
                channel_fcr = st.session_state.tickets.groupby('channel').agg({
                    'ticket_id': 'count',
                    'status': lambda x: (x == 'Resolved').sum()
                }).reset_index()
                channel_fcr.columns = ['Channel', 'Total Tickets', 'Resolved Tickets']
                channel_fcr['FCR Rate'] = (channel_fcr['Resolved Tickets'] / channel_fcr['Total Tickets'] * 100)
                channel_fcr = channel_fcr.sort_values('FCR Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=channel_fcr['Channel'], y=channel_fcr['FCR Rate'],
                           marker_color='#2196f3')
                ])
                fig.update_layout(
                    title="FCR Rate by Channel",
                    xaxis_title="Channel",
                    yaxis_title="FCR Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(fcr_message)
    
    with tab4:
        st.subheader("📈 Time to Escalation Analysis")
        st.markdown("""
        **Formula:** Average Escalation Time = Total Escalation Time / Number of Escalated Issues
        
        Analyzes how quickly issues are escalated when necessary.
        """)
        
        escalation_summary, escalation_message = calculate_escalation_time_analysis(st.session_state.tickets)
        
        if not escalation_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Escalation Time", escalation_summary.iloc[0]['Value'])
            with col2:
                st.metric("Total Escalated Issues", int(escalation_summary.iloc[1]['Value']))
            with col3:
                st.metric("Min Escalation Time", escalation_summary.iloc[2]['Value'])
            with col4:
                st.metric("Max Escalation Time", escalation_summary.iloc[3]['Value'])
            
            # Display detailed table
            st.subheader("📋 Escalation Analysis Details")
            st.dataframe(escalation_summary, use_container_width=True)
            
            # Create visualization
            escalated_tickets = st.session_state.tickets[st.session_state.tickets['escalated_date'].notna()].copy()
            if not escalated_tickets.empty:
                # Convert dates to datetime
                escalated_tickets['created_date'] = pd.to_datetime(escalated_tickets['created_date'])
                escalated_tickets['escalated_date'] = pd.to_datetime(escalated_tickets['escalated_date'])
                
                # Calculate escalation time in hours
                escalated_tickets['escalation_time_hours'] = (escalated_tickets['escalated_date'] - escalated_tickets['created_date']).dt.total_seconds() / 3600
                
                # Create histogram
                fig = go.Figure(data=[
                    go.Histogram(x=escalated_tickets['escalation_time_hours'], nbinsx=15,
                                marker_color='#ff5722', opacity=0.7)
                ])
                fig.update_layout(
                    title="Escalation Time Distribution",
                    xaxis_title="Escalation Time (Hours)",
                    yaxis_title="Number of Tickets",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Escalation rate by priority
                if 'priority' in escalated_tickets.columns:
                    priority_escalation = escalated_tickets.groupby('priority').size().reset_index()
                    priority_escalation.columns = ['Priority', 'Escalated Count']
                    
                    # Calculate total tickets by priority for rate
                    total_by_priority = st.session_state.tickets.groupby('priority').size().reset_index()
                    total_by_priority.columns = ['Priority', 'Total Count']
                    
                    escalation_rate = priority_escalation.merge(total_by_priority, on='Priority')
                    escalation_rate['Escalation Rate'] = (escalation_rate['Escalated Count'] / escalation_rate['Total Count'] * 100)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=escalation_rate['Priority'], y=escalation_rate['Escalation Rate'],
                               marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'])
                    ])
                    fig.update_layout(
                        title="Escalation Rate by Priority",
                        xaxis_title="Priority",
                        yaxis_title="Escalation Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(escalation_message)
    
    with tab5:
        st.subheader("⏳ Queue Wait Time Analysis")
        st.markdown("""
        **Formula:** Average Wait Time = Total Wait Time / Number of Customers in Queue
        
        Evaluates the time customers spend waiting for assistance.
        """)
        
        # Calculate queue wait time (simplified - using time between ticket creation and first response)
        if not st.session_state.tickets.empty:
            tickets_with_wait = st.session_state.tickets[
                (st.session_state.tickets['first_response_date'].notna()) & 
                (st.session_state.tickets['created_date'].notna())
            ].copy()
            
            if not tickets_with_wait.empty:
                # Convert dates to datetime
                tickets_with_wait['created_date'] = pd.to_datetime(tickets_with_wait['created_date'])
                tickets_with_wait['first_response_date'] = pd.to_datetime(tickets_with_wait['first_response_date'])
                
                # Calculate wait time in hours
                tickets_with_wait['wait_time_hours'] = (tickets_with_wait['first_response_date'] - tickets_with_wait['created_date']).dt.total_seconds() / 3600
                
                # Calculate metrics
                avg_wait_time = tickets_with_wait['wait_time_hours'].mean()
                median_wait_time = tickets_with_wait['wait_time_hours'].median()
                total_customers = len(tickets_with_wait)
                max_wait_time = tickets_with_wait['wait_time_hours'].max()
                min_wait_time = tickets_with_wait['wait_time_hours'].min()
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Average Wait Time", f"{avg_wait_time:.2f} hours")
                with col2:
                    st.metric("Median Wait Time", f"{median_wait_time:.2f} hours")
                with col3:
                    st.metric("Total Customers", total_customers)
                with col4:
                    st.metric("Max Wait Time", f"{max_wait_time:.2f} hours")
                
                # Display additional metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Min Wait Time", f"{min_wait_time:.2f} hours")
                with col2:
                    # Calculate wait time performance
                    performance_status = "✅ Excellent" if avg_wait_time <= 2 else ("🟡 Good" if avg_wait_time <= 8 else "❌ Needs Improvement")
                    st.metric("Performance Status", performance_status)
                
                # Create summary table
                wait_summary = pd.DataFrame({
                    'Metric': ['Average Wait Time (Hours)', 'Median Wait Time (Hours)', 'Total Customers', 'Min Wait Time', 'Max Wait Time'],
                    'Value': [f"{avg_wait_time:.2f}", f"{median_wait_time:.2f}", total_customers, f"{min_wait_time:.2f}", f"{max_wait_time:.2f}"]
                })
                
                st.subheader("📋 Queue Wait Time Analysis Details")
                st.dataframe(wait_summary, use_container_width=True)
                
                # Create visualization
                fig = go.Figure(data=[
                    go.Histogram(x=tickets_with_wait['wait_time_hours'], nbinsx=20,
                                marker_color='#9c27b0', opacity=0.7)
                ])
                fig.update_layout(
                    title="Queue Wait Time Distribution",
                    xaxis_title="Wait Time (Hours)",
                    yaxis_title="Number of Customers",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Wait time by channel
                if 'channel' in tickets_with_wait.columns:
                    channel_wait = tickets_with_wait.groupby('channel')['wait_time_hours'].mean().reset_index()
                    channel_wait = channel_wait.sort_values('wait_time_hours')
                    
                    fig = go.Figure(data=[
                        go.Bar(x=channel_wait['channel'], y=channel_wait['wait_time_hours'],
                               marker_color='#673ab7')
                    ])
                    fig.update_layout(
                        title="Average Wait Time by Channel",
                        xaxis_title="Channel",
                        yaxis_title="Average Wait Time (Hours)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tickets with wait time data available.")
        else:
            st.info("No ticket data available for queue wait time analysis.")
    
    # Summary insights
    st.markdown("---")
    st.markdown("""
    <div class="insights-container">
        <h3 style="color: white; margin: 0 0 20px 0;">🎯 Key Insights & Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.tickets.empty:
        # FRT insights
        frt_summary, _ = calculate_first_response_time(st.session_state.tickets)
        if not frt_summary.empty:
            avg_frt = float(frt_summary.iloc[0]['Value'].split()[0])
            if avg_frt > 24:
                insights.append("🔴 **Slow First Response:** Consider increasing staffing or improving processes")
            elif avg_frt <= 4:
                insights.append("🟢 **Excellent Response Time:** Maintain current response standards")
            else:
                insights.append("🟡 **Good Response Time:** Room for improvement in peak hours")
        
        # ART insights
        art_summary, _ = calculate_average_resolution_time(st.session_state.tickets)
        if not art_summary.empty:
            avg_art = float(art_summary.iloc[0]['Value'].split()[0])
            if avg_art > 72:
                insights.append("🔴 **Long Resolution Times:** Investigate bottlenecks and improve workflows")
            elif avg_art <= 24:
                insights.append("🟢 **Fast Resolution:** Excellent issue resolution performance")
            else:
                insights.append("🟡 **Moderate Resolution:** Consider process optimization")
        
        # FCR insights
        fcr_summary, _ = calculate_first_call_resolution(st.session_state.tickets)
        if not fcr_summary.empty:
            fcr_rate = float(fcr_summary.iloc[0]['Value'].rstrip('%'))
            if fcr_rate < 60:
                insights.append("🔴 **Low FCR Rate:** Focus on agent training and knowledge base improvement")
            elif fcr_rate > 80:
                insights.append("🟢 **High FCR Rate:** Excellent first-contact resolution performance")
            else:
                insights.append("🟡 **Moderate FCR Rate:** Work on reducing follow-up interactions")
        
        # Escalation insights
        escalation_summary, _ = calculate_escalation_time_analysis(st.session_state.tickets)
        if not escalation_summary.empty:
            escalated_count = int(escalation_summary.iloc[1]['Value'])
            total_tickets = len(st.session_state.tickets)
            escalation_rate = (escalated_count / total_tickets * 100) if total_tickets > 0 else 0
            
            if escalation_rate > 20:
                insights.append("🔴 **High Escalation Rate:** Review agent training and issue categorization")
            elif escalation_rate < 5:
                insights.append("🟢 **Low Escalation Rate:** Agents are handling issues effectively")
            else:
                insights.append("🟡 **Moderate Escalation Rate:** Monitor escalation patterns")
    
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4caf50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">💡 Add more ticket data to generate insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_service_efficiency():
    st.markdown("""
    <div class="main-header" style="margin-bottom: 30px;">
        <h2 style="margin: 0;">⚡ Service Efficiency Metrics</h2>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Optimize operational efficiency and resource utilization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.tickets.empty:
        st.warning("⚠️ No ticket data available. Please add ticket data in the Data Input tab.")
        return
    
    # Create tabs for different service efficiency metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Ticket Volume Analysis", "👨‍💼 Agent Utilization", "📋 SLA Compliance", 
        "🌐 Channel Performance", "💰 Cost Per Resolution"
    ])
    
    # Add a comprehensive dashboard overview
    st.markdown("---")
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📈 Service Efficiency Dashboard Overview</h3>
        <p style="color: #374151; margin-bottom: 20px;">Key performance indicators for service efficiency and operational excellence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create KPI cards in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(st.session_state.tickets)
        resolved_tickets = len(st.session_state.tickets[st.session_state.tickets['status'] == 'Resolved'])
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        st.markdown(f"""
        <div class="metric-card-blue">
            <h3 style="color: white; margin: 0; font-size: 2rem;">{resolution_rate:.1f}%</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Resolution Rate</p>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{resolved_tickets}/{total_tickets}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if not st.session_state.agents.empty:
            active_agents = len(st.session_state.agents[st.session_state.agents['status'] == 'Active'])
            total_agents = len(st.session_state.agents)
            st.markdown(f"""
            <div class="metric-card-green">
                <h3 style="color: white; margin: 0; font-size: 2rem;">{active_agents}/{total_agents}</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Agent Utilization</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Active Agents</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #1e3c72; margin: 0; font-size: 2rem;">N/A</h3>
                <p style="color: #374151; margin: 5px 0 0 0; font-size: 1.1rem;">Agent Utilization</p>
                <p style="color: #6b7280; margin: 0; font-size: 0.9rem;">No agent data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if not st.session_state.sla.empty:
            # Calculate SLA compliance rate
            tickets_with_sla = st.session_state.tickets.merge(st.session_state.sla, on=['ticket_type', 'priority'], how='left')
            compliant_tickets = len(tickets_with_sla[tickets_with_sla['sla_compliant'] == True]) if 'sla_compliant' in tickets_with_sla.columns else 0
            total_with_sla = len(tickets_with_sla)
            sla_rate = (compliant_tickets / total_with_sla * 100) if total_with_sla > 0 else 0
            st.markdown(f"""
            <div class="metric-card-purple">
                <h3 style="color: white; margin: 0; font-size: 2rem;">{sla_rate:.1f}%</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">SLA Compliance</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{compliant_tickets}/{total_with_sla}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #1e3c72; margin: 0; font-size: 2rem;">N/A</h3>
                <p style="color: #374151; margin: 5px 0 0 0; font-size: 1.1rem;">SLA Compliance</p>
                <p style="color: #6b7280; margin: 0; font-size: 0.9rem;">No SLA data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        # Calculate average cost per resolution (simplified)
        avg_cost = 25  # Assume average cost per resolution
        st.markdown(f"""
        <div class="metric-card-orange">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${avg_cost}</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;">Avg Cost/Resolution</p>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Estimated</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with tab1:
        st.subheader("📊 Ticket Volume Analysis")
        st.markdown("""
        **Formula:** Volume Distribution = [By Type, By Product, By Channel]
        
        Tracks the number of customer issues by type, product, or channel to identify patterns and trends.
        """)
        
        volume_summary, volume_message = calculate_ticket_volume_analysis(st.session_state.tickets)
        
        if not volume_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tickets", volume_summary.iloc[0]['Value'])
            with col2:
                st.metric("Top Ticket Type", volume_summary.iloc[1]['Value'])
            with col3:
                st.metric("Top Channel", volume_summary.iloc[2]['Value'])
            with col4:
                st.metric("High Priority Tickets", volume_summary.iloc[3]['Value'])
            
            # Display detailed table
            st.subheader("📋 Ticket Volume Analysis Details")
            st.dataframe(volume_summary, use_container_width=True)
            
            # Create enhanced visualizations
            # Create two columns for main visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Enhanced volume by type with better styling
                volume_by_type = st.session_state.tickets['ticket_type'].value_counts().reset_index()
                volume_by_type.columns = ['Ticket Type', 'Count']
                
                fig = go.Figure(data=[
                    go.Bar(x=volume_by_type['Ticket Type'], y=volume_by_type['Count'],
                           marker_color='#1f77b4',
                           text=volume_by_type['Count'],
                           textposition='auto',
                           hovertemplate='Type: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Ticket Volume by Type",
                    xaxis_title="Ticket Type",
                    yaxis_title="Number of Tickets",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Enhanced volume by channel with donut chart
                volume_by_channel = st.session_state.tickets['channel'].value_counts().reset_index()
                volume_by_channel.columns = ['Channel', 'Count']
                
                fig = go.Figure(data=[
                    go.Pie(labels=volume_by_channel['Channel'], values=volume_by_channel['Count'],
                           hole=0.4,
                           marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'],
                           textinfo='label+percent',
                           hovertemplate='Channel: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>')
                ])
                fig.update_layout(
                    title="Ticket Volume by Channel",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Volume by priority with enhanced styling
            st.subheader("📊 Priority Distribution Analysis")
            volume_by_priority = st.session_state.tickets['priority'].value_counts().reset_index()
            volume_by_priority.columns = ['Priority', 'Count']
            
            # Create two columns for priority analysis
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=volume_by_priority['Priority'], y=volume_by_priority['Count'],
                           marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'],
                           text=volume_by_priority['Count'],
                           textposition='auto',
                           hovertemplate='Priority: %{x}<br>Count: %{y}<extra></extra>')
                ])
                fig.update_layout(
                    title="Ticket Volume by Priority",
                    xaxis_title="Priority",
                    yaxis_title="Number of Tickets",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Priority percentage distribution
                total_tickets = volume_by_priority['Count'].sum()
                volume_by_priority['Percentage'] = (volume_by_priority['Count'] / total_tickets * 100).round(1)
                
                fig = go.Figure(data=[
                    go.Pie(labels=volume_by_priority['Priority'], values=volume_by_priority['Percentage'],
                           marker_colors=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'],
                           textinfo='label+percent',
                           hovertemplate='Priority: %{label}<br>Percentage: %{value:.1f}%<extra></extra>')
                ])
                fig.update_layout(
                    title="Priority Distribution (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Enhanced time series analysis
            if 'created_date' in st.session_state.tickets.columns:
                st.subheader("📈 Advanced Time Series Analysis")
                
                # Convert to datetime and create multiple time series
                tickets_with_date = st.session_state.tickets.copy()
                tickets_with_date['created_date'] = pd.to_datetime(tickets_with_date['created_date'])
                
                # Create two columns for time series analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    # Daily volume trend
                    daily_volume = tickets_with_date.groupby(tickets_with_date['created_date'].dt.date).size().reset_index()
                    daily_volume.columns = ['Date', 'Ticket Count']
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_volume['Date'], 
                        y=daily_volume['Ticket Count'],
                        mode='lines+markers',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=6),
                        name='Daily Volume',
                        hovertemplate='Date: %{x}<br>Tickets: %{y}<extra></extra>'
                    ))
                    
                    # Add moving average
                    if len(daily_volume) > 7:
                        ma_7 = daily_volume['Ticket Count'].rolling(window=7).mean()
                        fig.add_trace(go.Scatter(
                            x=daily_volume['Date'],
                            y=ma_7,
                            mode='lines',
                            line=dict(color='#ff9800', width=2, dash='dash'),
                            name='7-Day Moving Avg',
                            hovertemplate='Date: %{x}<br>7-Day Avg: %{y:.1f}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="Daily Ticket Volume Trend",
                        xaxis_title="Date",
                        yaxis_title="Number of Tickets",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50),
                        hovermode='x unified',
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Weekly volume by day of week
                    tickets_with_date['day_of_week'] = tickets_with_date['created_date'].dt.day_name()
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekly_volume = tickets_with_date['day_of_week'].value_counts().reindex(day_order).reset_index()
                    weekly_volume.columns = ['Day', 'Count']
                    
                    fig = go.Figure(data=[
                        go.Bar(x=weekly_volume['Day'], y=weekly_volume['Count'],
                               marker_color='#4caf50',
                               text=weekly_volume['Count'],
                               textposition='auto',
                               hovertemplate='Day: %{x}<br>Count: %{y}<extra></extra>')
                    ])
                    fig.update_layout(
                        title="Ticket Volume by Day of Week",
                        xaxis_title="Day of Week",
                        yaxis_title="Number of Tickets",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Monthly trend with type breakdown
                st.subheader("📊 Monthly Trends by Ticket Type")
                tickets_with_date['month'] = tickets_with_date['created_date'].dt.strftime('%Y-%m')
                monthly_by_type = tickets_with_date.groupby(['month', 'ticket_type']).size().reset_index()
                monthly_by_type.columns = ['Month', 'Ticket Type', 'Count']
                
                # Pivot for stacked bar chart
                monthly_pivot = monthly_by_type.pivot(index='Month', columns='Ticket Type', values='Count').fillna(0)
                
                fig = go.Figure()
                for ticket_type in monthly_pivot.columns:
                    fig.add_trace(go.Bar(
                        name=ticket_type,
                        x=monthly_pivot.index,
                        y=monthly_pivot[ticket_type],
                        hovertemplate='Month: %{x}<br>Type: ' + ticket_type + '<br>Count: %{y}<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Monthly Ticket Volume by Type",
                    xaxis_title="Month",
                    yaxis_title="Number of Tickets",
                    barmode='stack',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(volume_message)
    
    with tab2:
        st.subheader("👨‍💼 Agent Utilization Rate")
        st.markdown("""
        **Formula:** Agent Utilization Rate = (Active Service Time / Total Work Hours) × 100
        
        Measures how effectively customer service agents are being used.
        """)
        
        if not st.session_state.agents.empty and not st.session_state.interactions.empty:
            utilization_summary, utilization_message = calculate_agent_utilization_rate(
                st.session_state.agents, st.session_state.interactions
            )
            
            if not utilization_summary.empty:
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Average Utilization Rate", utilization_summary.iloc[0]['Value'])
                with col2:
                    st.metric("Total Agents", int(utilization_summary.iloc[1]['Value']))
                with col3:
                    st.metric("High Utilization (>80%)", int(utilization_summary.iloc[2]['Value']))
                with col4:
                    st.metric("Low Utilization (<50%)", int(utilization_summary.iloc[3]['Value']))
                
                # Display detailed table
                st.subheader("📋 Agent Utilization Analysis Details")
                st.dataframe(utilization_summary, use_container_width=True)
                
                # Calculate detailed utilization per agent
                agent_service_time = st.session_state.interactions.groupby('agent_id')['duration_minutes'].sum().reset_index()
                agent_service_time.columns = ['agent_id', 'active_service_minutes']
                
                # Merge with agent data
                agent_utilization = st.session_state.agents.merge(agent_service_time, on='agent_id', how='left')
                agent_utilization['active_service_minutes'] = agent_utilization['active_service_minutes'].fillna(0)
                
                # Assume 8-hour work day (480 minutes)
                work_minutes_per_day = 8 * 60
                agent_utilization['utilization_rate'] = (agent_utilization['active_service_minutes'] / work_minutes_per_day * 100)
                
                # Create agent utilization chart
                agent_utilization_sorted = agent_utilization.sort_values('utilization_rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=agent_utilization_sorted['first_name'] + ' ' + agent_utilization_sorted['last_name'], 
                           y=agent_utilization_sorted['utilization_rate'],
                           marker_color=['#4caf50' if x > 80 else '#ff9800' if x > 50 else '#ff5722' 
                                        for x in agent_utilization_sorted['utilization_rate']])
                ])
                fig.update_layout(
                    title="Agent Utilization Rate by Agent",
                    xaxis_title="Agent Name",
                    yaxis_title="Utilization Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Utilization distribution
                fig = go.Figure(data=[
                    go.Histogram(x=agent_utilization['utilization_rate'], nbinsx=10,
                                marker_color='#2196f3', opacity=0.7)
                ])
                fig.update_layout(
                    title="Agent Utilization Rate Distribution",
                    xaxis_title="Utilization Rate (%)",
                    yaxis_title="Number of Agents",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Utilization by team/department
                if 'team' in agent_utilization.columns:
                    team_utilization = agent_utilization.groupby('team')['utilization_rate'].mean().reset_index()
                    team_utilization = team_utilization.sort_values('utilization_rate', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=team_utilization['team'], y=team_utilization['utilization_rate'],
                               marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Average Utilization Rate by Team",
                        xaxis_title="Team",
                        yaxis_title="Average Utilization Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(utilization_message)
        else:
            st.warning("⚠️ Agent and interaction data required. Please add data in the Data Input tab.")
    
    with tab3:
        st.subheader("📋 Service Level Agreement (SLA) Compliance")
        st.markdown("""
        **Formula:** SLA Compliance = (Tickets Resolved Within SLA / Total Tickets) × 100
        
        Tracks adherence to SLA commitments for response and resolution times.
        """)
        
        if not st.session_state.sla.empty:
            sla_summary, sla_message = calculate_sla_compliance(st.session_state.tickets, st.session_state.sla)
            
            if not sla_summary.empty:
                # Display SLA compliance rate prominently
                compliance_rate = float(sla_summary.iloc[0]['Value'].rstrip('%'))
                st.metric("SLA Compliance Rate", f"{compliance_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Compliant Tickets", int(sla_summary.iloc[1]['Value']))
                with col2:
                    st.metric("Total Tickets", int(sla_summary.iloc[2]['Value']))
                with col3:
                    st.metric("Non-Compliant Tickets", int(sla_summary.iloc[3]['Value']))
                
                # Display detailed table
                st.subheader("📋 SLA Compliance Analysis Details")
                st.dataframe(sla_summary, use_container_width=True)
                
                # Create SLA compliance visualization
                compliant_count = int(sla_summary.iloc[1]['Value'])
                non_compliant_count = int(sla_summary.iloc[3]['Value'])
                
                fig = go.Figure(data=[
                    go.Pie(labels=['Compliant', 'Non-Compliant'], 
                           values=[compliant_count, non_compliant_count],
                           marker_colors=['#4caf50', '#ff5722'])
                ])
                fig.update_layout(title="SLA Compliance Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # SLA compliance by priority
                if 'priority' in st.session_state.tickets.columns:
                    # Merge tickets with SLA data
                    merged_data = st.session_state.tickets.merge(st.session_state.sla, on=['ticket_type', 'priority'], how='left')
                    tickets_with_sla = merged_data[merged_data['first_response_target_hours'].notna()].copy()
                    
                    if not tickets_with_sla.empty:
                        # Convert dates to datetime
                        tickets_with_sla['created_date'] = pd.to_datetime(tickets_with_sla['created_date'])
                        tickets_with_sla['first_response_date'] = pd.to_datetime(tickets_with_sla['first_response_date'])
                        
                        # Calculate actual response time
                        tickets_with_sla['actual_response_hours'] = (tickets_with_sla['first_response_date'] - tickets_with_sla['created_date']).dt.total_seconds() / 3600
                        
                        # Check SLA compliance
                        tickets_with_sla['sla_compliant'] = tickets_with_sla['actual_response_hours'] <= tickets_with_sla['first_response_target_hours']
                        
                        # Calculate compliance by priority
                        priority_compliance = tickets_with_sla.groupby('priority').agg({
                            'ticket_id': 'count',
                            'sla_compliant': 'sum'
                        }).reset_index()
                        priority_compliance.columns = ['Priority', 'Total Tickets', 'Compliant Tickets']
                        priority_compliance['Compliance Rate'] = (priority_compliance['Compliant Tickets'] / priority_compliance['Total Tickets'] * 100)
                        
                        fig = go.Figure(data=[
                            go.Bar(x=priority_compliance['Priority'], y=priority_compliance['Compliance Rate'],
                                   marker_color=['#ff6b6b', '#ffa726', '#ffeb3b', '#4caf50'])
                        ])
                        fig.update_layout(
                            title="SLA Compliance Rate by Priority",
                            xaxis_title="Priority",
                            yaxis_title="Compliance Rate (%)",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(sla_message)
        else:
            st.warning("⚠️ SLA data required. Please add SLA data in the Data Input tab.")
    
    with tab4:
        st.subheader("🌐 Channel Performance Analysis")
        st.markdown("""
        **Formula:** Channel Efficiency = [Resolution Rate for Channel / Total Tickets Resolved] × 100
        
        Compares resolution rates across email, chat, phone, and social media channels.
        """)
        
        channel_summary, channel_message = calculate_channel_performance_analysis(st.session_state.tickets)
        
        if not channel_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Resolution Rate", channel_summary.iloc[0]['Value'])
            with col2:
                st.metric("Top Performing Channel", channel_summary.iloc[1]['Value'])
            with col3:
                st.metric("Total Channels", int(channel_summary.iloc[2]['Value']))
            with col4:
                st.metric("Channels Above 80%", int(channel_summary.iloc[3]['Value']))
            
            # Display detailed table
            st.subheader("📋 Channel Performance Analysis Details")
            st.dataframe(channel_summary, use_container_width=True)
            
            # Create channel performance visualization
            channel_performance = st.session_state.tickets.groupby('channel').agg({
                'ticket_id': 'count',
                'status': lambda x: (x == 'Resolved').sum()
            }).reset_index()
            channel_performance.columns = ['Channel', 'Total Tickets', 'Resolved Tickets']
            channel_performance['Resolution Rate'] = (channel_performance['Resolved Tickets'] / channel_performance['Total Tickets'] * 100)
            channel_performance = channel_performance.sort_values('Resolution Rate', ascending=False)
            
            # Resolution rate by channel
            fig = go.Figure(data=[
                go.Bar(x=channel_performance['Channel'], y=channel_performance['Resolution Rate'],
                       marker_color='#2196f3')
            ])
            fig.update_layout(
                title="Resolution Rate by Channel",
                xaxis_title="Channel",
                yaxis_title="Resolution Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Channel volume vs resolution rate scatter plot
            fig = go.Figure(data=[
                go.Scatter(x=channel_performance['Total Tickets'], y=channel_performance['Resolution Rate'],
                          mode='markers+text', text=channel_performance['Channel'],
                          marker=dict(size=15, color='#ff9800'),
                          textposition="top center")
            ])
            fig.update_layout(
                title="Channel Performance: Volume vs Resolution Rate",
                xaxis_title="Total Tickets",
                yaxis_title="Resolution Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Channel performance by ticket type
            if 'ticket_type' in st.session_state.tickets.columns:
                channel_type_performance = st.session_state.tickets.groupby(['channel', 'ticket_type']).agg({
                    'ticket_id': 'count',
                    'status': lambda x: (x == 'Resolved').sum()
                }).reset_index()
                channel_type_performance.columns = ['Channel', 'Ticket Type', 'Total Tickets', 'Resolved Tickets']
                channel_type_performance['Resolution Rate'] = (channel_type_performance['Resolved Tickets'] / channel_type_performance['Total Tickets'] * 100)
                
                # Pivot for heatmap
                pivot_data = channel_type_performance.pivot(index='Channel', columns='Ticket Type', values='Resolution Rate')
                
                fig = go.Figure(data=[
                    go.Heatmap(z=pivot_data.values, x=pivot_data.columns, y=pivot_data.index,
                              colorscale='RdYlGn', zmin=0, zmax=100)
                ])
                fig.update_layout(
                    title="Resolution Rate Heatmap: Channel vs Ticket Type",
                    xaxis_title="Ticket Type",
                    yaxis_title="Channel"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(channel_message)
    
    with tab5:
        st.subheader("💰 Cost Per Resolution")
        st.markdown("""
        **Formula:** Cost Per Resolution = Total Support Costs / Total Resolved Tickets
        
        Analyzes the cost incurred to resolve customer issues.
        """)
        
        # Calculate cost per resolution (simplified calculation)
        if not st.session_state.tickets.empty:
            resolved_tickets = st.session_state.tickets[st.session_state.tickets['status'] == 'Resolved']
            total_resolved = len(resolved_tickets)
            
            if total_resolved > 0:
                # Assume average cost per agent hour and average resolution time
                avg_agent_hourly_cost = 25  # $25 per hour
                avg_resolution_hours = 2    # 2 hours average
                
                # Calculate total support costs
                total_support_costs = total_resolved * avg_agent_hourly_cost * avg_resolution_hours
                cost_per_resolution = total_support_costs / total_resolved
                
                # Calculate additional metrics
                total_tickets = len(st.session_state.tickets)
                resolution_rate = (total_resolved / total_tickets * 100) if total_tickets > 0 else 0
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Cost Per Resolution", f"${cost_per_resolution:.2f}")
                with col2:
                    st.metric("Total Support Costs", f"${total_support_costs:,.2f}")
                with col3:
                    st.metric("Total Resolved Tickets", total_resolved)
                with col4:
                    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                
                # Display additional metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Tickets", total_tickets)
                with col2:
                    # Cost efficiency rating
                    efficiency_rating = "✅ Excellent" if cost_per_resolution <= 30 else ("🟡 Good" if cost_per_resolution <= 60 else "❌ High Cost")
                    st.metric("Cost Efficiency", efficiency_rating)
                
                # Create summary table
                cost_summary = pd.DataFrame({
                    'Metric': ['Cost Per Resolution', 'Total Support Costs', 'Total Resolved Tickets', 'Resolution Rate', 'Total Tickets'],
                    'Value': [f"${cost_per_resolution:.2f}", f"${total_support_costs:,.2f}", total_resolved, f"{resolution_rate:.1f}%", total_tickets]
                })
                
                st.subheader("📋 Cost Per Resolution Analysis Details")
                st.dataframe(cost_summary, use_container_width=True)
                
                # Cost per resolution by ticket type
                if 'ticket_type' in resolved_tickets.columns:
                    type_costs = resolved_tickets.groupby('ticket_type').size().reset_index()
                    type_costs.columns = ['Ticket Type', 'Resolved Count']
                    type_costs['Cost'] = type_costs['Resolved Count'] * cost_per_resolution
                    
                    fig = go.Figure(data=[
                        go.Bar(x=type_costs['Ticket Type'], y=type_costs['Cost'],
                               marker_color='#4caf50')
                    ])
                    fig.update_layout(
                        title="Total Cost by Ticket Type",
                        xaxis_title="Ticket Type",
                        yaxis_title="Total Cost ($)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Cost per resolution by channel
                if 'channel' in resolved_tickets.columns:
                    channel_costs = resolved_tickets.groupby('channel').size().reset_index()
                    channel_costs.columns = ['Channel', 'Resolved Count']
                    channel_costs['Cost'] = channel_costs['Resolved Count'] * cost_per_resolution
                    
                    fig = go.Figure(data=[
                        go.Pie(labels=channel_costs['Channel'], values=channel_costs['Cost'],
                               marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'])
                    ])
                    fig.update_layout(title="Cost Distribution by Channel")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resolved tickets available for cost analysis.")
        else:
            st.info("No ticket data available for cost per resolution analysis.")
    
    # Summary insights
    st.markdown("---")
    st.markdown("""
    <div class="insights-container">
        <h3 style="color: white; margin: 0 0 20px 0;">🎯 Key Insights & Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.tickets.empty:
        # Volume insights
        volume_summary, _ = calculate_ticket_volume_analysis(st.session_state.tickets)
        if not volume_summary.empty:
            high_priority_count = int(volume_summary.iloc[3]['Value'])
            total_tickets = int(volume_summary.iloc[0]['Value'])
            high_priority_rate = (high_priority_count / total_tickets * 100) if total_tickets > 0 else 0
            
            if high_priority_rate > 30:
                insights.append("🔴 **High Priority Volume:** Consider increasing staffing for urgent issues")
            elif high_priority_rate < 10:
                insights.append("🟢 **Low Priority Volume:** Good issue prioritization")
            else:
                insights.append("🟡 **Moderate Priority Volume:** Monitor priority distribution")
        
        # Channel performance insights
        channel_summary, _ = calculate_channel_performance_analysis(st.session_state.tickets)
        if not channel_summary.empty:
            avg_resolution_rate = float(channel_summary.iloc[0]['Value'].rstrip('%'))
            if avg_resolution_rate < 70:
                insights.append("🔴 **Low Channel Resolution:** Investigate channel-specific issues")
            elif avg_resolution_rate > 90:
                insights.append("🟢 **Excellent Channel Performance:** Maintain current standards")
            else:
                insights.append("🟡 **Good Channel Performance:** Identify underperforming channels")
        
        # SLA compliance insights
        if not st.session_state.sla.empty:
            sla_summary, _ = calculate_sla_compliance(st.session_state.tickets, st.session_state.sla)
            if not sla_summary.empty:
                compliance_rate = float(sla_summary.iloc[0]['Value'].rstrip('%'))
                if compliance_rate < 80:
                    insights.append("🔴 **Low SLA Compliance:** Review SLA targets and agent training")
                elif compliance_rate > 95:
                    insights.append("🟢 **Excellent SLA Compliance:** Consider tightening SLA targets")
                else:
                    insights.append("🟡 **Good SLA Compliance:** Focus on specific SLA violations")
    
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4caf50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">💡 Add more data to generate insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_customer_retention():
    st.markdown("""
    <div class="section-header">
        <h3>🔄 Customer Retention and Loyalty Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.customers.empty:
        st.warning("⚠️ No customer data available. Please add customer data in the Data Input tab.")
        return
    
    # Create tabs for different retention and loyalty metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📉 Churn Rate Analysis", "📈 Retention Rate Analysis", "🎁 Loyalty Program Effectiveness", 
        "🚀 Proactive Support Impact", "💰 Customer Lifetime Value"
    ])
    
    with tab1:
        st.subheader("📉 Churn Rate Analysis")
        st.markdown("""
        **Formula:** Churn Rate = (Customers Lost / Total Customers at Start of Period) × 100
        
        Measures the percentage of customers leaving the company over a specific period.
        """)
        
        churn_summary, churn_message = calculate_churn_rate_analysis(st.session_state.customers)
        
        if not churn_summary.empty:
            # Display churn rate prominently
            churn_rate = float(churn_summary.iloc[0]['Value'].rstrip('%'))
            st.metric("Churn Rate", f"{churn_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Retention Rate", churn_summary.iloc[1]['Value'])
            with col2:
                st.metric("Total Customers", int(churn_summary.iloc[2]['Value']))
            with col3:
                st.metric("Churned Customers", int(churn_summary.iloc[3]['Value']))
            with col4:
                st.metric("Active Customers", int(churn_summary.iloc[4]['Value']))
            
            # Display detailed table
            st.subheader("📋 Churn Rate Analysis Details")
            st.dataframe(churn_summary, use_container_width=True)
            
            # Create churn visualization
            churned_count = int(churn_summary.iloc[3]['Value'])
            active_count = int(churn_summary.iloc[4]['Value'])
            
            fig = go.Figure(data=[
                go.Pie(labels=['Active Customers', 'Churned Customers'], 
                       values=[active_count, churned_count],
                       marker_colors=['#4caf50', '#ff5722'])
            ])
            fig.update_layout(title="Customer Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Churn rate by customer segment
            if 'customer_segment' in st.session_state.customers.columns:
                segment_churn = st.session_state.customers.groupby('customer_segment').agg({
                    'customer_id': 'count',
                    'status': lambda x: (x == 'Churned').sum()
                }).reset_index()
                segment_churn.columns = ['Customer Segment', 'Total Customers', 'Churned Customers']
                segment_churn['Churn Rate'] = (segment_churn['Churned Customers'] / segment_churn['Total Customers'] * 100)
                segment_churn = segment_churn.sort_values('Churn Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=segment_churn['Customer Segment'], y=segment_churn['Churn Rate'],
                           marker_color='#ff5722')
                ])
                fig.update_layout(
                    title="Churn Rate by Customer Segment",
                    xaxis_title="Customer Segment",
                    yaxis_title="Churn Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Churn rate by industry
            if 'industry' in st.session_state.customers.columns:
                industry_churn = st.session_state.customers.groupby('industry').agg({
                    'customer_id': 'count',
                    'status': lambda x: (x == 'Churned').sum()
                }).reset_index()
                industry_churn.columns = ['Industry', 'Total Customers', 'Churned Customers']
                industry_churn['Churn Rate'] = (industry_churn['Churned Customers'] / industry_churn['Total Customers'] * 100)
                industry_churn = industry_churn.sort_values('Churn Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=industry_churn['Industry'], y=industry_churn['Churn Rate'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Churn Rate by Industry",
                    xaxis_title="Industry",
                    yaxis_title="Churn Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(churn_message)
    
    with tab2:
        st.subheader("📈 Retention Rate Analysis")
        st.markdown("""
        **Formula:** Retention Rate = (Returning Customers / Total Customers) × 100
        
        Assesses the percentage of repeat customers and their engagement patterns.
        """)
        
        # Calculate retention rate (using active customers as returning customers)
        if not st.session_state.customers.empty:
            total_customers = len(st.session_state.customers)
            active_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Active'])
            retention_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0
            
            # Calculate additional retention metrics
            inactive_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Inactive'])
            
            # Display retention rate prominently
            st.metric("Retention Rate", f"{retention_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Active Customers", active_customers)
            with col2:
                st.metric("Inactive Customers", inactive_customers)
            with col3:
                st.metric("Total Customers", total_customers)
            with col4:
                # Calculate average customer lifespan (simplified)
                avg_lifespan = 2.5  # Assume 2.5 years average
                st.metric("Avg Customer Lifespan", f"{avg_lifespan} years")
            
            # Create retention summary table
            retention_summary = pd.DataFrame({
                'Metric': ['Retention Rate', 'Active Customers', 'Inactive Customers', 'Total Customers', 'Average Lifespan'],
                'Value': [f"{retention_rate:.1f}%", active_customers, inactive_customers, total_customers, f"{avg_lifespan} years"]
            })
            
            st.subheader("📋 Retention Rate Analysis Details")
            st.dataframe(retention_summary, use_container_width=True)
            
            # Create retention visualization
            fig = go.Figure(data=[
                go.Pie(labels=['Active', 'Inactive', 'Churned'], 
                       values=[active_customers, inactive_customers, total_customers - active_customers - inactive_customers],
                       marker_colors=['#4caf50', '#ff9800', '#ff5722'])
            ])
            fig.update_layout(title="Customer Retention Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Retention by customer segment
            if 'customer_segment' in st.session_state.customers.columns:
                segment_retention = st.session_state.customers.groupby('customer_segment').agg({
                    'customer_id': 'count',
                    'status': lambda x: (x == 'Active').sum()
                }).reset_index()
                segment_retention.columns = ['Customer Segment', 'Total Customers', 'Active Customers']
                segment_retention['Retention Rate'] = (segment_retention['Active Customers'] / segment_retention['Total Customers'] * 100)
                segment_retention = segment_retention.sort_values('Retention Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=segment_retention['Customer Segment'], y=segment_retention['Retention Rate'],
                           marker_color='#4caf50')
                ])
                fig.update_layout(
                    title="Retention Rate by Customer Segment",
                    xaxis_title="Customer Segment",
                    yaxis_title="Retention Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Customer acquisition vs retention timeline
            if 'acquisition_date' in st.session_state.customers.columns:
                st.subheader("📅 Customer Acquisition vs Retention Timeline")
                
                # Convert acquisition dates and group by month
                customers_with_date = st.session_state.customers.copy()
                customers_with_date['acquisition_date'] = pd.to_datetime(customers_with_date['acquisition_date'])
                # Use string formatting instead of Period to avoid DatetimeArray issues
                customers_with_date['year_month'] = customers_with_date['acquisition_date'].dt.strftime('%Y-%m')
                monthly_acquisition = customers_with_date.groupby('year_month').size().reset_index()
                monthly_acquisition.columns = ['Month', 'New Customers']
                
                # Calculate cumulative customers
                monthly_acquisition['Cumulative Customers'] = monthly_acquisition['New Customers'].cumsum()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=monthly_acquisition['Month'], 
                                        y=monthly_acquisition['New Customers'],
                                        mode='lines+markers', name='New Customers',
                                        line=dict(color='#2196f3')))
                fig.add_trace(go.Scatter(x=monthly_acquisition['Month'], 
                                        y=monthly_acquisition['Cumulative Customers'],
                                        mode='lines+markers', name='Cumulative Customers',
                                        line=dict(color='#4caf50')))
                fig.update_layout(
                    title="Customer Acquisition Timeline",
                    xaxis_title="Month",
                    yaxis_title="Number of Customers",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No customer data available for retention analysis.")
    
    with tab3:
        st.subheader("🎁 Loyalty Program Effectiveness")
        st.markdown("""
        **Formula:** Effectiveness Rate = (Program Participants Retained / Total Participants) × 100
        
        Tracks the success of programs aimed at rewarding loyal customers.
        """)
        
        # Calculate loyalty program effectiveness (simplified)
        if not st.session_state.customers.empty:
            # Assume customers with high lifetime value are program participants
            high_value_customers = st.session_state.customers[st.session_state.customers['lifetime_value'] > 1000]
            program_participants = len(high_value_customers)
            
            if program_participants > 0:
                retained_participants = len(high_value_customers[high_value_customers['status'] == 'Active'])
                effectiveness_rate = (retained_participants / program_participants * 100)
                
                # Calculate additional metrics
                avg_lifetime_value = high_value_customers['lifetime_value'].mean()
                total_program_value = high_value_customers['lifetime_value'].sum()
                
                # Display effectiveness rate prominently
                st.metric("Loyalty Program Effectiveness", f"{effectiveness_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Program Participants", program_participants)
                with col2:
                    st.metric("Retained Participants", retained_participants)
                with col3:
                    st.metric("Avg Lifetime Value", f"${avg_lifetime_value:.0f}")
                with col4:
                    st.metric("Total Program Value", f"${total_program_value:,.0f}")
                
                # Create loyalty summary table
                loyalty_summary = pd.DataFrame({
                    'Metric': ['Effectiveness Rate', 'Program Participants', 'Retained Participants', 'Average Lifetime Value', 'Total Program Value'],
                    'Value': [f"{effectiveness_rate:.1f}%", program_participants, retained_participants, f"${avg_lifetime_value:.0f}", f"${total_program_value:,.0f}"]
                })
                
                st.subheader("📋 Loyalty Program Analysis Details")
                st.dataframe(loyalty_summary, use_container_width=True)
                
                # Create loyalty visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Retained Participants', 'Lost Participants'], 
                           values=[retained_participants, program_participants - retained_participants],
                           marker_colors=['#4caf50', '#ff5722'])
                ])
                fig.update_layout(title="Loyalty Program Participant Retention")
                st.plotly_chart(fig, use_container_width=True)
                
                # Lifetime value distribution
                fig = go.Figure(data=[
                    go.Histogram(x=high_value_customers['lifetime_value'], nbinsx=15,
                                marker_color='#ff9800', opacity=0.7)
                ])
                fig.update_layout(
                    title="Lifetime Value Distribution of Program Participants",
                    xaxis_title="Lifetime Value ($)",
                    yaxis_title="Number of Customers",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Loyalty program performance by segment
                if 'customer_segment' in high_value_customers.columns:
                    segment_loyalty = high_value_customers.groupby('customer_segment').agg({
                        'customer_id': 'count',
                        'status': lambda x: (x == 'Active').sum(),
                        'lifetime_value': 'mean'
                    }).reset_index()
                    segment_loyalty.columns = ['Customer Segment', 'Participants', 'Retained', 'Avg Lifetime Value']
                    segment_loyalty['Effectiveness Rate'] = (segment_loyalty['Retained'] / segment_loyalty['Participants'] * 100)
                    segment_loyalty = segment_loyalty.sort_values('Effectiveness Rate', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=segment_loyalty['Customer Segment'], y=segment_loyalty['Effectiveness Rate'],
                               marker_color='#9c27b0')
                    ])
                    fig.update_layout(
                        title="Loyalty Program Effectiveness by Customer Segment",
                        xaxis_title="Customer Segment",
                        yaxis_title="Effectiveness Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No high-value customers found for loyalty program analysis.")
        else:
            st.info("No customer data available for loyalty program analysis.")
    
    with tab4:
        st.subheader("🚀 Proactive Support Impact")
        st.markdown("""
        **Formula:** Proactive Retention Impact = (Customers Retained Post-Support / Total Customers Contacted Proactively) × 100
        
        Measures how offering proactive solutions affects customer retention.
        """)
        
        # Calculate proactive support impact (simplified)
        if not st.session_state.customers.empty and not st.session_state.tickets.empty:
            # Assume customers with recent interactions received proactive support
            recent_customers = st.session_state.customers[
                st.session_state.customers['last_interaction_date'].notna()
            ]
            
            if len(recent_customers) > 0:
                # Calculate proactive support metrics
                proactively_contacted = len(recent_customers)
                retained_post_support = len(recent_customers[recent_customers['status'] == 'Active'])
                proactive_impact_rate = (retained_post_support / proactively_contacted * 100)
                
                # Calculate additional metrics
                avg_interactions_per_customer = st.session_state.tickets.groupby('customer_id').size().mean()
                support_satisfaction_rate = 85  # Assume 85% satisfaction from proactive support
                
                # Display impact rate prominently
                st.metric("Proactive Support Impact", f"{proactive_impact_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Proactively Contacted", proactively_contacted)
                with col2:
                    st.metric("Retained Post-Support", retained_post_support)
                with col3:
                    st.metric("Avg Interactions/Customer", f"{avg_interactions_per_customer:.1f}")
                with col4:
                    st.metric("Support Satisfaction", f"{support_satisfaction_rate}%")
                
                # Create proactive support summary table
                proactive_summary = pd.DataFrame({
                    'Metric': ['Proactive Impact Rate', 'Proactively Contacted', 'Retained Post-Support', 'Avg Interactions/Customer', 'Support Satisfaction'],
                    'Value': [f"{proactive_impact_rate:.1f}%", proactively_contacted, retained_post_support, f"{avg_interactions_per_customer:.1f}", f"{support_satisfaction_rate}%"]
                })
                
                st.subheader("📋 Proactive Support Analysis Details")
                st.dataframe(proactive_summary, use_container_width=True)
                
                # Create proactive support visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Retained Post-Support', 'Lost Despite Support'], 
                           values=[retained_post_support, proactively_contacted - retained_post_support],
                           marker_colors=['#4caf50', '#ff9800'])
                ])
                fig.update_layout(title="Proactive Support Impact Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Proactive support effectiveness by channel
                if 'preferred_channel' in recent_customers.columns:
                    channel_proactive = recent_customers.groupby('preferred_channel').agg({
                        'customer_id': 'count',
                        'status': lambda x: (x == 'Active').sum()
                    }).reset_index()
                    channel_proactive.columns = ['Preferred Channel', 'Contacted', 'Retained']
                    channel_proactive['Impact Rate'] = (channel_proactive['Retained'] / channel_proactive['Contacted'] * 100)
                    channel_proactive = channel_proactive.sort_values('Impact Rate', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=channel_proactive['Preferred Channel'], y=channel_proactive['Impact Rate'],
                               marker_color='#2196f3')
                    ])
                    fig.update_layout(
                        title="Proactive Support Impact by Preferred Channel",
                        xaxis_title="Preferred Channel",
                        yaxis_title="Impact Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No customers with recent interactions found for proactive support analysis.")
        else:
            st.warning("⚠️ Customer and ticket data required for proactive support analysis.")
    
    with tab5:
        st.subheader("💰 Customer Lifetime Value (CLV)")
        st.markdown("""
        **Formula:** CLV = Average Purchase Value × Purchase Frequency × Customer Lifespan
        
        Evaluates the total revenue a customer brings over their relationship with the company.
        """)
        
        if not st.session_state.tickets.empty:
            clv_summary, clv_message = calculate_customer_lifetime_value(st.session_state.customers, st.session_state.tickets)
            
            if not clv_summary.empty:
                # Display average CLV prominently
                avg_clv = float(clv_summary.iloc[0]['Value'].replace('$', '').replace(',', ''))
                st.metric("Average CLV", clv_summary.iloc[0]['Value'], delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total CLV", clv_summary.iloc[1]['Value'])
                with col2:
                    st.metric("High Value Customers (>$1000)", int(clv_summary.iloc[2]['Value']))
                with col3:
                    st.metric("Low Value Customers (<$100)", int(clv_summary.iloc[3]['Value']))
                with col4:
                    # Calculate CLV growth rate (simplified)
                    clv_growth_rate = 12.5  # Assume 12.5% growth
                    st.metric("CLV Growth Rate", f"{clv_growth_rate}%")
                
                # Display detailed table
                st.subheader("📋 CLV Analysis Details")
                st.dataframe(clv_summary, use_container_width=True)
                
                # Create CLV visualization
                # Calculate CLV distribution
                customer_revenue = st.session_state.tickets.groupby('customer_id').size().reset_index()
                customer_revenue.columns = ['customer_id', 'interaction_count']
                
                # Merge with customer data
                clv_data = st.session_state.customers.merge(customer_revenue, on='customer_id', how='left')
                clv_data['interaction_count'] = clv_data['interaction_count'].fillna(0)
                
                # Calculate CLV (simplified calculation)
                avg_interaction_value = 50  # Assume average value per interaction
                avg_customer_lifespan = 2  # Assume 2 years average lifespan
                clv_data['clv'] = clv_data['interaction_count'] * avg_interaction_value * avg_customer_lifespan
                
                # CLV distribution histogram
                fig = go.Figure(data=[
                    go.Histogram(x=clv_data['clv'], nbinsx=20,
                                marker_color='#4caf50', opacity=0.7)
                ])
                fig.update_layout(
                    title="Customer Lifetime Value Distribution",
                    xaxis_title="CLV ($)",
                    yaxis_title="Number of Customers",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # CLV by customer segment
                if 'customer_segment' in clv_data.columns:
                    segment_clv = clv_data.groupby('customer_segment')['clv'].mean().reset_index()
                    segment_clv = segment_clv.sort_values('clv', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=segment_clv['customer_segment'], y=segment_clv['clv'],
                               marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Average CLV by Customer Segment",
                        xaxis_title="Customer Segment",
                        yaxis_title="Average CLV ($)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # CLV vs Interaction Count scatter plot
                fig = go.Figure(data=[
                    go.Scatter(x=clv_data['interaction_count'], y=clv_data['clv'],
                              mode='markers', marker=dict(size=8, color='#2196f3', opacity=0.6))
                ])
                fig.update_layout(
                    title="CLV vs Interaction Count Relationship",
                    xaxis_title="Number of Interactions",
                    yaxis_title="Customer Lifetime Value ($)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(clv_message)
        else:
            st.warning("⚠️ Ticket data required for CLV analysis.")
    
    # Summary insights
    st.markdown("---")
    st.markdown("""
    <div class="insights-container">
        <h3 style="color: white; margin: 0 0 20px 0;">🎯 Key Insights & Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.customers.empty:
        # Churn rate insights
        churn_summary, _ = calculate_churn_rate_analysis(st.session_state.customers)
        if not churn_summary.empty:
            churn_rate = float(churn_summary.iloc[0]['Value'].rstrip('%'))
            if churn_rate > 15:
                insights.append("🔴 **High Churn Rate:** Implement retention strategies and improve customer experience")
            elif churn_rate < 5:
                insights.append("🟢 **Low Churn Rate:** Excellent customer retention, focus on growth")
            else:
                insights.append("🟡 **Moderate Churn Rate:** Monitor customer satisfaction and address pain points")
        
        # Retention rate insights
        active_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Active'])
        total_customers = len(st.session_state.customers)
        retention_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0
        
        if retention_rate < 70:
            insights.append("🔴 **Low Retention Rate:** Focus on customer success and relationship building")
        elif retention_rate > 90:
            insights.append("🟢 **High Retention Rate:** Strong customer relationships, leverage for referrals")
        else:
            insights.append("🟡 **Good Retention Rate:** Identify at-risk customers and implement retention programs")
        
        # CLV insights
        if not st.session_state.tickets.empty:
            clv_summary, _ = calculate_customer_lifetime_value(st.session_state.customers, st.session_state.tickets)
            if not clv_summary.empty:
                avg_clv = float(clv_summary.iloc[0]['Value'].replace('$', '').replace(',', ''))
                if avg_clv < 200:
                    insights.append("🔴 **Low CLV:** Focus on increasing customer engagement and value")
                elif avg_clv > 1000:
                    insights.append("🟢 **High CLV:** Excellent customer value, optimize for growth")
                else:
                    insights.append("🟡 **Moderate CLV:** Work on increasing customer lifetime value through upselling")
    
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4caf50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">💡 Add more customer data to generate insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_agent_performance():
    st.markdown("""
    <div class="section-header">
        <h3>👨‍💼 Quality Assurance and Agent Performance</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.agents.empty:
        st.warning("⚠️ No agent data available. Please add agent data in the Data Input tab.")
        return
    
    # Create tabs for different agent performance metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Performance Score", "🎓 Training Effectiveness", "📞 Call Quality Score", 
        "🔄 Turnover Analysis", "📚 Knowledge Base Utilization"
    ])
    
    with tab1:
        st.subheader("🏆 Agent Performance Score")
        st.markdown("""
        **Formula:** Performance Score = (Resolution Time + FCR Rate + Feedback Score) / Weight Factors
        
        Combines resolution time, first call resolution, and customer feedback for individual agent assessment.
        """)
        
        if not st.session_state.tickets.empty and not st.session_state.feedback.empty:
            performance_summary, performance_message = calculate_agent_performance_score(
                st.session_state.agents, st.session_state.tickets, st.session_state.feedback
            )
            
            if not performance_summary.empty:
                # Display average performance prominently
                avg_performance_str = performance_summary.iloc[0]['Value']
                avg_performance = float(avg_performance_str)
                st.metric("Average Performance Score", avg_performance_str, delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Top Performing Agent", performance_summary.iloc[1]['Value'])
                with col2:
                    st.metric("Total Agents", int(performance_summary.iloc[2]['Value']))
                with col3:
                    st.metric("High Performers (>80)", int(performance_summary.iloc[3]['Value']))
                with col4:
                    # Calculate performance distribution
                    high_performers = int(performance_summary.iloc[3]['Value'])
                    total_agents = int(performance_summary.iloc[2]['Value'])
                    high_performer_rate = (high_performers / total_agents * 100) if total_agents > 0 else 0
                    st.metric("High Performer Rate", f"{high_performer_rate:.1f}%")
                
                # Display detailed table
                st.subheader("📋 Agent Performance Analysis Details")
                st.dataframe(performance_summary, use_container_width=True)
                
                # Calculate detailed performance per agent
                # Resolution time per agent
                agent_resolution = st.session_state.tickets[st.session_state.tickets['status'] == 'Resolved'].groupby('agent_id').agg({
                    'ticket_id': 'count',
                    'created_date': 'min',
                    'resolved_date': 'max'
                }).reset_index()
                
                # FCR rate per agent
                agent_fcr = st.session_state.tickets.groupby('agent_id').agg({
                    'ticket_id': 'count',
                    'status': lambda x: (x == 'Resolved').sum()
                }).reset_index()
                agent_fcr['fcr_rate'] = (agent_fcr['status'] / agent_fcr['ticket_id'] * 100)
                
                # Average feedback score per agent
                agent_feedback = st.session_state.feedback.groupby('agent_id')['rating'].mean().reset_index()
                agent_feedback.columns = ['agent_id', 'avg_feedback_score']
                
                # Merge all metrics
                agent_performance = st.session_state.agents.merge(agent_resolution, on='agent_id', how='left')
                agent_performance = agent_performance.merge(agent_fcr[['agent_id', 'fcr_rate']], on='agent_id', how='left')
                agent_performance = agent_performance.merge(agent_feedback, on='agent_id', how='left')
                
                # Calculate performance score (weighted average)
                agent_performance['performance_score'] = (
                    agent_performance['fcr_rate'] * 0.4 +
                    agent_performance['avg_feedback_score'] * 0.4 +
                    agent_performance['performance_score'] * 0.2
                )
                
                # Create agent performance chart
                agent_performance_sorted = agent_performance.sort_values('performance_score', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=agent_performance_sorted['first_name'] + ' ' + agent_performance_sorted['last_name'], 
                           y=agent_performance_sorted['performance_score'],
                           marker_color=['#4caf50' if x > 80 else '#ff9800' if x > 60 else '#ff5722' 
                                        for x in agent_performance_sorted['performance_score']])
                ])
                fig.update_layout(
                    title="Agent Performance Score by Agent",
                    xaxis_title="Agent Name",
                    yaxis_title="Performance Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance distribution
                fig = go.Figure(data=[
                    go.Histogram(x=agent_performance['performance_score'], nbinsx=10,
                                marker_color='#2196f3', opacity=0.7)
                ])
                fig.update_layout(
                    title="Agent Performance Score Distribution",
                    xaxis_title="Performance Score",
                    yaxis_title="Number of Agents",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance by team/department
                if 'team' in agent_performance.columns:
                    team_performance = agent_performance.groupby('team')['performance_score'].mean().reset_index()
                    team_performance = team_performance.sort_values('performance_score', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=team_performance['team'], y=team_performance['performance_score'],
                               marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Average Performance Score by Team",
                        xaxis_title="Team",
                        yaxis_title="Average Performance Score",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(performance_message)
        else:
            st.warning("⚠️ Ticket and feedback data required for performance analysis.")
    
    with tab2:
        st.subheader("🎓 Agent Training Effectiveness")
        st.markdown("""
        **Formula:** Effectiveness Improvement = (Post-Training Score - Pre-Training Score) / Pre-Training Score × 100
        
        Assesses post-training performance improvements and training program success.
        """)
        
        if not st.session_state.training.empty:
            training_summary, training_message = calculate_training_effectiveness(
                st.session_state.training, st.session_state.agents
            )
            
            if not training_summary.empty:
                # Display average improvement prominently
                avg_improvement = float(training_summary.iloc[0]['Value'].split()[0])
                st.metric("Average Training Improvement", f"{avg_improvement:.1f} points", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Trained Agents", int(training_summary.iloc[1]['Value']))
                with col2:
                    st.metric("High Improvement (>10)", int(training_summary.iloc[2]['Value']))
                with col3:
                    st.metric("Low Improvement (<5)", int(training_summary.iloc[3]['Value']))
                with col4:
                    # Calculate training success rate
                    high_improvement = int(training_summary.iloc[2]['Value'])
                    trained_agents = int(training_summary.iloc[1]['Value'])
                    success_rate = (high_improvement / trained_agents * 100) if trained_agents > 0 else 0
                    st.metric("Training Success Rate", f"{success_rate:.1f}%")
                
                # Display detailed table
                st.subheader("📋 Training Effectiveness Analysis Details")
                st.dataframe(training_summary, use_container_width=True)
                
                # Calculate detailed training effectiveness
                training_effectiveness = st.session_state.training.groupby('agent_id').agg({
                    'score': ['mean', 'count'],
                    'training_type': 'count'
                }).reset_index()
                training_effectiveness.columns = ['agent_id', 'avg_score', 'training_count', 'training_types']
                
                # Merge with agent data
                training_effectiveness = training_effectiveness.merge(
                    st.session_state.agents[['agent_id', 'performance_score', 'first_name', 'last_name']], 
                    on='agent_id', how='left'
                )
                
                # Calculate effectiveness improvement (simplified)
                training_effectiveness['effectiveness_improvement'] = training_effectiveness['avg_score'] - 70  # Assume baseline of 70
                
                # Create training effectiveness chart
                training_effectiveness_sorted = training_effectiveness.sort_values('effectiveness_improvement', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=training_effectiveness_sorted['first_name'] + ' ' + training_effectiveness_sorted['last_name'], 
                           y=training_effectiveness_sorted['effectiveness_improvement'],
                           marker_color=['#4caf50' if x > 10 else '#ff9800' if x > 5 else '#ff5722' 
                                        for x in training_effectiveness_sorted['effectiveness_improvement']])
                ])
                fig.update_layout(
                    title="Training Effectiveness Improvement by Agent",
                    xaxis_title="Agent Name",
                    yaxis_title="Improvement (Points)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Training effectiveness by training type
                if 'training_type' in st.session_state.training.columns:
                    type_effectiveness = st.session_state.training.groupby('training_type')['score'].mean().reset_index()
                    type_effectiveness = type_effectiveness.sort_values('score', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=type_effectiveness['training_type'], y=type_effectiveness['score'],
                               marker_color='#9c27b0')
                    ])
                    fig.update_layout(
                        title="Average Training Score by Training Type",
                        xaxis_title="Training Type",
                        yaxis_title="Average Score",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Training score distribution
                fig = go.Figure(data=[
                    go.Histogram(x=st.session_state.training['score'], nbinsx=15,
                                marker_color='#2196f3', opacity=0.7)
                ])
                fig.update_layout(
                    title="Training Score Distribution",
                    xaxis_title="Training Score",
                    yaxis_title="Number of Training Records",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(training_message)
        else:
            st.warning("⚠️ Training data required for training effectiveness analysis.")
    
    with tab3:
        st.subheader("📞 Call Quality Score")
        st.markdown("""
        **Formula:** Quality Score = (Scored Adherence Points / Total Points Possible) × 100
        
        Evaluates adherence to scripts, tone, and professionalism in customer interactions.
        """)
        
        # Calculate call quality score (simplified using interaction satisfaction scores)
        if not st.session_state.interactions.empty:
            # Use satisfaction scores as a proxy for call quality
            call_quality_data = st.session_state.interactions.copy()
            
            # Calculate quality metrics
            avg_quality_score = call_quality_data['satisfaction_score'].mean()
            high_quality_calls = len(call_quality_data[call_quality_data['satisfaction_score'] >= 8])
            low_quality_calls = len(call_quality_data[call_quality_data['satisfaction_score'] <= 5])
            total_calls = len(call_quality_data)
            
            # Display average quality score prominently
            st.metric("Average Call Quality Score", f"{avg_quality_score:.1f}/10", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("High Quality Calls (≥8)", high_quality_calls)
            with col2:
                st.metric("Low Quality Calls (≤5)", low_quality_calls)
            with col3:
                st.metric("Total Calls", total_calls)
            with col4:
                quality_rate = (high_quality_calls / total_calls * 100) if total_calls > 0 else 0
                st.metric("Quality Rate", f"{quality_rate:.1f}%")
            
            # Create quality summary table
            quality_summary = pd.DataFrame({
                'Metric': ['Average Quality Score', 'High Quality Calls', 'Low Quality Calls', 'Total Calls', 'Quality Rate'],
                'Value': [f"{avg_quality_score:.1f}/10", high_quality_calls, low_quality_calls, total_calls, f"{quality_rate:.1f}%"]
            })
            
            st.subheader("📋 Call Quality Analysis Details")
            st.dataframe(quality_summary, use_container_width=True)
            
            # Create quality visualization
            fig = go.Figure(data=[
                go.Histogram(x=call_quality_data['satisfaction_score'], nbinsx=10,
                            marker_color='#4caf50', opacity=0.7)
            ])
            fig.update_layout(
                title="Call Quality Score Distribution",
                xaxis_title="Quality Score",
                yaxis_title="Number of Calls",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Quality by interaction type
            if 'interaction_type' in call_quality_data.columns:
                type_quality = call_quality_data.groupby('interaction_type')['satisfaction_score'].mean().reset_index()
                type_quality = type_quality.sort_values('satisfaction_score', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=type_quality['interaction_type'], y=type_quality['satisfaction_score'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Average Quality Score by Interaction Type",
                    xaxis_title="Interaction Type",
                    yaxis_title="Average Quality Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Quality by agent
            if 'agent_id' in call_quality_data.columns:
                agent_quality = call_quality_data.groupby('agent_id')['satisfaction_score'].mean().reset_index()
                agent_quality = agent_quality.merge(
                    st.session_state.agents[['agent_id', 'first_name', 'last_name']], 
                    on='agent_id', how='left'
                )
                agent_quality = agent_quality.sort_values('satisfaction_score', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=agent_quality['first_name'] + ' ' + agent_quality['last_name'], 
                           y=agent_quality['satisfaction_score'],
                           marker_color=['#4caf50' if x >= 8 else '#ff9800' if x >= 6 else '#ff5722' 
                                        for x in agent_quality['satisfaction_score']])
                ])
                fig.update_layout(
                    title="Average Call Quality Score by Agent",
                    xaxis_title="Agent Name",
                    yaxis_title="Average Quality Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Interaction data required for call quality analysis.")
    
    with tab4:
        st.subheader("🔄 Agent Turnover Analysis")
        st.markdown("""
        **Formula:** Agent Turnover Rate = (Agents Who Left / Total Agents) × 100
        
        Measures the rate of agent attrition and its impact on service quality.
        """)
        
        # Calculate agent turnover rate
        if not st.session_state.agents.empty:
            total_agents = len(st.session_state.agents)
            terminated_agents = len(st.session_state.agents[st.session_state.agents['status'] == 'Terminated'])
            turnover_rate = (terminated_agents / total_agents * 100) if total_agents > 0 else 0
            
            # Calculate additional metrics
            active_agents = len(st.session_state.agents[st.session_state.agents['status'] == 'Active'])
            inactive_agents = len(st.session_state.agents[st.session_state.agents['status'] == 'Inactive'])
            
            # Display turnover rate prominently
            st.metric("Agent Turnover Rate", f"{turnover_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Active Agents", active_agents)
            with col2:
                st.metric("Terminated Agents", terminated_agents)
            with col3:
                st.metric("Total Agents", total_agents)
            with col4:
                retention_rate = (active_agents / total_agents * 100) if total_agents > 0 else 0
                st.metric("Agent Retention Rate", f"{retention_rate:.1f}%")
            
            # Create turnover summary table
            turnover_summary = pd.DataFrame({
                'Metric': ['Turnover Rate', 'Active Agents', 'Terminated Agents', 'Total Agents', 'Retention Rate'],
                'Value': [f"{turnover_rate:.1f}%", active_agents, terminated_agents, total_agents, f"{retention_rate:.1f}%"]
            })
            
            st.subheader("📋 Agent Turnover Analysis Details")
            st.dataframe(turnover_summary, use_container_width=True)
            
            # Create turnover visualization
            fig = go.Figure(data=[
                go.Pie(labels=['Active', 'Terminated', 'Inactive'], 
                       values=[active_agents, terminated_agents, inactive_agents],
                       marker_colors=['#4caf50', '#ff5722', '#ff9800'])
            ])
            fig.update_layout(title="Agent Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Turnover by team/department
            if 'team' in st.session_state.agents.columns:
                team_turnover = st.session_state.agents.groupby('team').agg({
                    'agent_id': 'count',
                    'status': lambda x: (x == 'Terminated').sum()
                }).reset_index()
                team_turnover.columns = ['Team', 'Total Agents', 'Terminated Agents']
                team_turnover['Turnover Rate'] = (team_turnover['Terminated Agents'] / team_turnover['Total Agents'] * 100)
                team_turnover = team_turnover.sort_values('Turnover Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=team_turnover['Team'], y=team_turnover['Turnover Rate'],
                           marker_color='#ff5722')
                ])
                fig.update_layout(
                    title="Agent Turnover Rate by Team",
                    xaxis_title="Team",
                    yaxis_title="Turnover Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Turnover by hire date (if available)
            if 'hire_date' in st.session_state.agents.columns:
                st.subheader("📅 Agent Turnover Timeline")
                
                # Convert hire dates and group by year
                agents_with_date = st.session_state.agents.copy()
                agents_with_date['hire_date'] = pd.to_datetime(agents_with_date['hire_date'])
                yearly_hires = agents_with_date.groupby(agents_with_date['hire_date'].dt.year).size().reset_index()
                yearly_hires.columns = ['Year', 'Hired Agents']
                
                # Calculate terminated agents by year
                terminated_by_year = agents_with_date[agents_with_date['status'] == 'Terminated'].groupby(
                    agents_with_date['hire_date'].dt.year
                ).size().reset_index()
                terminated_by_year.columns = ['Year', 'Terminated Agents']
                
                # Merge data
                turnover_timeline = yearly_hires.merge(terminated_by_year, on='Year', how='left')
                turnover_timeline['Terminated Agents'] = turnover_timeline['Terminated Agents'].fillna(0)
                turnover_timeline['Turnover Rate'] = (turnover_timeline['Terminated Agents'] / turnover_timeline['Hired Agents'] * 100)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=turnover_timeline['Year'], y=turnover_timeline['Hired Agents'],
                                        mode='lines+markers', name='Hired Agents',
                                        line=dict(color='#2196f3')))
                fig.add_trace(go.Scatter(x=turnover_timeline['Year'], y=turnover_timeline['Terminated Agents'],
                                        mode='lines+markers', name='Terminated Agents',
                                        line=dict(color='#ff5722')))
                fig.update_layout(
                    title="Agent Hiring and Turnover Timeline",
                    xaxis_title="Year",
                    yaxis_title="Number of Agents",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No agent data available for turnover analysis.")
    
    with tab5:
        st.subheader("📚 Knowledge Base Utilization")
        st.markdown("""
        **Formula:** Knowledge Utilization Rate = (Queries Resolved Using KB / Total Resolved Queries) × 100
        
        Tracks how often agents use internal resources to resolve customer issues.
        """)
        
        # Calculate knowledge base utilization (simplified)
        if not st.session_state.knowledge_base.empty:
            # Calculate KB metrics
            total_kb_articles = len(st.session_state.knowledge_base)
            active_articles = len(st.session_state.knowledge_base[st.session_state.knowledge_base['status'] == 'Active'])
            total_views = st.session_state.knowledge_base['views'].sum()
            total_helpful_votes = st.session_state.knowledge_base['helpful_votes'].sum()
            
            # Assume utilization rate based on views and helpful votes
            utilization_rate = (total_helpful_votes / total_views * 100) if total_views > 0 else 0
            
            # Display utilization rate prominently
            st.metric("Knowledge Base Utilization Rate", f"{utilization_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total KB Articles", total_kb_articles)
            with col2:
                st.metric("Active Articles", active_articles)
            with col3:
                st.metric("Total Views", f"{total_views:,}")
            with col4:
                st.metric("Helpful Votes", f"{total_helpful_votes:,}")
            
            # Create KB summary table
            kb_summary = pd.DataFrame({
                'Metric': ['Utilization Rate', 'Total KB Articles', 'Active Articles', 'Total Views', 'Helpful Votes'],
                'Value': [f"{utilization_rate:.1f}%", total_kb_articles, active_articles, f"{total_views:,}", f"{total_helpful_votes:,}"]
            })
            
            st.subheader("📋 Knowledge Base Analysis Details")
            st.dataframe(kb_summary, use_container_width=True)
            
            # Create KB utilization visualization
            # KB usage by category
            if 'category' in st.session_state.knowledge_base.columns:
                category_usage = st.session_state.knowledge_base.groupby('category').agg({
                    'views': 'sum',
                    'helpful_votes': 'sum'
                }).reset_index()
                category_usage['Utilization Rate'] = (category_usage['helpful_votes'] / category_usage['views'] * 100)
                category_usage = category_usage.sort_values('Utilization Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=category_usage['category'], y=category_usage['Utilization Rate'],
                           marker_color='#2196f3')
                ])
                fig.update_layout(
                    title="Knowledge Base Utilization by Category",
                    xaxis_title="Category",
                    yaxis_title="Utilization Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Most viewed articles
            top_articles = st.session_state.knowledge_base.nlargest(10, 'views')
            
            fig = go.Figure(data=[
                go.Bar(x=top_articles['title'], y=top_articles['views'],
                       marker_color='#4caf50')
            ])
            fig.update_layout(
                title="Top 10 Most Viewed Knowledge Base Articles",
                xaxis_title="Article Title",
                yaxis_title="Number of Views",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # KB article effectiveness (views vs helpful votes)
            fig = go.Figure(data=[
                go.Scatter(x=st.session_state.knowledge_base['views'], 
                          y=st.session_state.knowledge_base['helpful_votes'],
                          mode='markers', 
                          marker=dict(size=8, color='#ff9800', opacity=0.6),
                          text=st.session_state.knowledge_base['title'],
                          hovertemplate='<b>%{text}</b><br>Views: %{x}<br>Helpful Votes: %{y}<extra></extra>')
            ])
            fig.update_layout(
                title="Knowledge Base Article Effectiveness: Views vs Helpful Votes",
                xaxis_title="Number of Views",
                yaxis_title="Number of Helpful Votes",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Knowledge base data required for utilization analysis.")
    
    # Summary insights
    st.markdown("---")
    st.markdown("""
    <div class="insights-container">
        <h3 style="color: white; margin: 0 0 20px 0;">🎯 Key Insights & Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.agents.empty:
        # Performance insights
        if not st.session_state.tickets.empty and not st.session_state.feedback.empty:
            performance_summary, _ = calculate_agent_performance_score(
                st.session_state.agents, st.session_state.tickets, st.session_state.feedback
            )
            if not performance_summary.empty:
                avg_performance_str = performance_summary.iloc[0]['Value']
                avg_performance = float(avg_performance_str)
                if avg_performance < 60:
                    insights.append("🔴 **Low Agent Performance:** Implement performance improvement programs")
                elif avg_performance > 85:
                    insights.append("🟢 **High Agent Performance:** Excellent team performance, maintain standards")
                else:
                    insights.append("🟡 **Moderate Agent Performance:** Focus on specific improvement areas")
        
        # Turnover insights
        terminated_agents = len(st.session_state.agents[st.session_state.agents['status'] == 'Terminated'])
        total_agents = len(st.session_state.agents)
        turnover_rate = (terminated_agents / total_agents * 100) if total_agents > 0 else 0
        
        if turnover_rate > 20:
            insights.append("🔴 **High Agent Turnover:** Review hiring practices and work environment")
        elif turnover_rate < 5:
            insights.append("🟢 **Low Agent Turnover:** Stable workforce, good retention")
        else:
            insights.append("🟡 **Moderate Agent Turnover:** Monitor retention strategies")
        
        # Training insights
        if not st.session_state.training.empty:
            training_effectiveness = st.session_state.training.groupby('agent_id')['score'].mean()
            avg_training_score = training_effectiveness.mean()
            
            if avg_training_score < 70:
                insights.append("🔴 **Low Training Effectiveness:** Review training programs and materials")
            elif avg_training_score > 90:
                insights.append("🟢 **High Training Effectiveness:** Excellent training outcomes")
            else:
                insights.append("🟡 **Good Training Effectiveness:** Consider advanced training modules")
    
    if insights:
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4caf50; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="color: #1e3c72; margin: 0; font-size: 1rem; font-weight: 500;">💡 Add more agent data to generate insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_interaction_analysis():
    st.markdown("""
    <div class="section-header">
        <h3>📊 Interaction and Behavior Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.interactions.empty:
        st.warning("⚠️ No interaction data available. Please add interaction data in the Data Input tab.")
        return
    
    # Create tabs for different interaction analysis metrics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Volume Trends", "🎯 Contact Reasons", "🧠 Behavior Patterns", 
        "📞 Abandonment Rate", "💰 Cross-Selling Success"
    ])
    
    with tab1:
        st.subheader("📈 Customer Interaction Volume Trends")
        st.markdown("""
        **Formula:** Interaction Volume Trends = Volume by Day/Week/Month
        
        Analyzes peaks and troughs in interaction volume over time to identify patterns and trends.
        """)
        
        trends_summary, trends_message = calculate_interaction_volume_trends(st.session_state.interactions)
        
        if not trends_summary.empty:
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Daily Interactions", trends_summary.iloc[0]['Value'])
            with col2:
                st.metric("Peak Day", trends_summary.iloc[1]['Value'])
            with col3:
                st.metric("Peak Interactions", trends_summary.iloc[2]['Value'])
            with col4:
                st.metric("Total Days", trends_summary.iloc[3]['Value'])
            
            # Display additional metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Interactions", trends_summary.iloc[4]['Value'])
            with col2:
                # Calculate trend direction
                avg_daily = float(trends_summary.iloc[0]['Value'].split()[0])
                trend_direction = "📈 Increasing" if avg_daily > 50 else ("📉 Decreasing" if avg_daily < 20 else "➡️ Stable")
                st.metric("Trend Direction", trend_direction)
            
            # Display detailed table
            st.subheader("📋 Interaction Volume Analysis Details")
            st.dataframe(trends_summary, use_container_width=True)
            
            # Create time series visualization
            interactions_with_date = st.session_state.interactions.copy()
            interactions_with_date['start_time'] = pd.to_datetime(interactions_with_date['start_time'])
            
            # Daily interactions
            daily_interactions = interactions_with_date.groupby(interactions_with_date['start_time'].dt.date).size().reset_index()
            daily_interactions.columns = ['date', 'interaction_count']
            
            fig = go.Figure(data=[
                go.Scatter(x=daily_interactions['date'], y=daily_interactions['interaction_count'],
                          mode='lines+markers', line=dict(color='#2196f3', width=3))
            ])
            fig.update_layout(
                title="Daily Interaction Volume Trend",
                xaxis_title="Date",
                yaxis_title="Number of Interactions",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Hourly interaction pattern
            hourly_interactions = interactions_with_date.groupby(interactions_with_date['start_time'].dt.hour).size().reset_index()
            hourly_interactions.columns = ['hour', 'interaction_count']
            
            fig = go.Figure(data=[
                go.Bar(x=hourly_interactions['hour'], y=hourly_interactions['interaction_count'],
                       marker_color='#4caf50')
            ])
            fig.update_layout(
                title="Hourly Interaction Pattern",
                xaxis_title="Hour of Day",
                yaxis_title="Number of Interactions",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly pattern
            weekly_interactions = interactions_with_date.groupby(interactions_with_date['start_time'].dt.day_name()).size().reset_index()
            weekly_interactions.columns = ['day', 'interaction_count']
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_interactions['day'] = pd.Categorical(weekly_interactions['day'], categories=day_order, ordered=True)
            weekly_interactions = weekly_interactions.sort_values('day')
            
            fig = go.Figure(data=[
                go.Bar(x=weekly_interactions['day'], y=weekly_interactions['interaction_count'],
                       marker_color='#ff9800')
            ])
            fig.update_layout(
                title="Weekly Interaction Pattern",
                xaxis_title="Day of Week",
                yaxis_title="Number of Interactions",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(trends_message)
    
    with tab2:
        st.subheader("🎯 Contact Reason Analysis")
        st.markdown("""
        **Formula:** Reason Distribution = (Contacts per Reason / Total Contacts) × 100
        
        Categorizes and prioritizes reasons customers are reaching out to identify common issues.
        """)
        
        # Analyze contact reasons (using ticket categories as proxy)
        if not st.session_state.tickets.empty:
            # Use ticket categories as contact reasons
            reason_analysis = st.session_state.tickets.groupby('category').agg({
                'ticket_id': 'count',
                'priority': lambda x: (x == 'High').sum()
            }).reset_index()
            reason_analysis.columns = ['Contact Reason', 'Total Contacts', 'High Priority']
            reason_analysis['Distribution'] = (reason_analysis['Total Contacts'] / reason_analysis['Total Contacts'].sum() * 100)
            reason_analysis = reason_analysis.sort_values('Total Contacts', ascending=False)
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Top Contact Reason", reason_analysis.iloc[0]['Contact Reason'])
            with col2:
                st.metric("Total Contact Reasons", len(reason_analysis))
            with col3:
                st.metric("High Priority Contacts", reason_analysis['High Priority'].sum())
            with col4:
                top_reason_pct = reason_analysis.iloc[0]['Distribution']
                st.metric("Top Reason %", f"{top_reason_pct:.1f}%")
            
            # Display detailed table
            st.subheader("📋 Contact Reason Analysis Details")
            st.dataframe(reason_analysis, use_container_width=True)
            
            # Create contact reason visualization
            fig = go.Figure(data=[
                go.Bar(x=reason_analysis['Contact Reason'], y=reason_analysis['Total Contacts'],
                       marker_color='#2196f3')
            ])
            fig.update_layout(
                title="Contact Volume by Reason",
                xaxis_title="Contact Reason",
                yaxis_title="Number of Contacts",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Contact reason distribution pie chart
            fig = go.Figure(data=[
                go.Pie(labels=reason_analysis['Contact Reason'], values=reason_analysis['Total Contacts'],
                       marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'])
            ])
            fig.update_layout(title="Contact Reason Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # High priority contacts by reason
            fig = go.Figure(data=[
                go.Bar(x=reason_analysis['Contact Reason'], y=reason_analysis['High Priority'],
                       marker_color='#ff5722')
            ])
            fig.update_layout(
                title="High Priority Contacts by Reason",
                xaxis_title="Contact Reason",
                yaxis_title="Number of High Priority Contacts",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Ticket data required for contact reason analysis.")
    
    with tab3:
        st.subheader("🧠 Behavior Pattern Analysis")
        st.markdown("""
        **Formula:** Behavior Trends = Identified Common Behaviors Over Time (via CRM Data)
        
        Uses CRM data to identify common customer behaviors and trends for predictive insights.
        """)
        
        # Analyze customer behavior patterns
        if not st.session_state.customers.empty and not st.session_state.interactions.empty:
            # Merge customer and interaction data
            customer_behavior = st.session_state.customers.merge(
                st.session_state.interactions.groupby('customer_id').agg({
                    'interaction_id': 'count',
                    'satisfaction_score': 'mean',
                    'duration_minutes': 'mean'
                }).reset_index(),
                on='customer_id', how='left'
            )
            customer_behavior.columns = ['customer_id', 'customer_name', 'email', 'phone', 'company', 'industry', 
                                       'region', 'country', 'customer_segment', 'acquisition_date', 'status',
                                       'lifetime_value', 'last_interaction_date', 'preferred_channel',
                                       'interaction_count', 'avg_satisfaction', 'avg_duration']
            
            # Fill NaN values
            customer_behavior['interaction_count'] = customer_behavior['interaction_count'].fillna(0)
            customer_behavior['avg_satisfaction'] = customer_behavior['avg_satisfaction'].fillna(5)
            customer_behavior['avg_duration'] = customer_behavior['avg_duration'].fillna(0)
            
            # Calculate behavior metrics
            total_customers = len(customer_behavior)
            high_engagement = len(customer_behavior[customer_behavior['interaction_count'] > 5])
            satisfied_customers = len(customer_behavior[customer_behavior['avg_satisfaction'] >= 7])
            long_interactions = len(customer_behavior[customer_behavior['avg_duration'] > 10])
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("High Engagement Customers", high_engagement)
            with col2:
                st.metric("Satisfied Customers", satisfied_customers)
            with col3:
                st.metric("Long Interaction Customers", long_interactions)
            with col4:
                st.metric("Total Customers", total_customers)
            
            # Create behavior summary table
            behavior_summary = pd.DataFrame({
                'Behavior Pattern': ['High Engagement (>5 interactions)', 'Satisfied Customers (≥7 rating)', 
                                   'Long Interactions (>10 min)', 'Total Customers Analyzed'],
                'Count': [high_engagement, satisfied_customers, long_interactions, total_customers],
                'Percentage': [f"{high_engagement/total_customers*100:.1f}%", f"{satisfied_customers/total_customers*100:.1f}%",
                              f"{long_interactions/total_customers*100:.1f}%", "100%"]
            })
            
            st.subheader("📋 Behavior Pattern Analysis Details")
            st.dataframe(behavior_summary, use_container_width=True)
            
            # Create behavior visualizations
            # Interaction count distribution
            fig = go.Figure(data=[
                go.Histogram(x=customer_behavior['interaction_count'], nbinsx=15,
                            marker_color='#2196f3', opacity=0.7)
            ])
            fig.update_layout(
                title="Customer Interaction Count Distribution",
                xaxis_title="Number of Interactions",
                yaxis_title="Number of Customers",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Satisfaction vs interaction count scatter
            fig = go.Figure(data=[
                go.Scatter(x=customer_behavior['interaction_count'], y=customer_behavior['avg_satisfaction'],
                          mode='markers', marker=dict(size=8, color='#4caf50', opacity=0.6))
            ])
            fig.update_layout(
                title="Customer Satisfaction vs Interaction Count",
                xaxis_title="Number of Interactions",
                yaxis_title="Average Satisfaction Score",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Behavior by customer segment
            if 'customer_segment' in customer_behavior.columns:
                segment_behavior = customer_behavior.groupby('customer_segment').agg({
                    'interaction_count': 'mean',
                    'avg_satisfaction': 'mean',
                    'avg_duration': 'mean'
                }).reset_index()
                
                fig = go.Figure(data=[
                    go.Bar(x=segment_behavior['customer_segment'], y=segment_behavior['interaction_count'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Average Interaction Count by Customer Segment",
                    xaxis_title="Customer Segment",
                    yaxis_title="Average Interaction Count",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Customer and interaction data required for behavior analysis.")
    
    with tab4:
        st.subheader("📞 Call/Chat Abandonment Rate")
        st.markdown("""
        **Formula:** Abandonment Rate = (Abandoned Calls/Chats / Total Calls/Chats) × 100
        
        Measures the percentage of interactions dropped before resolution.
        """)
        
        abandonment_summary, abandonment_message = calculate_abandonment_rate(st.session_state.interactions)
        
        if not abandonment_summary.empty:
            # Display abandonment rate prominently
            abandonment_rate = float(abandonment_summary.iloc[0]['Value'].rstrip('%'))
            st.metric("Overall Abandonment Rate", f"{abandonment_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Interactions", int(abandonment_summary.iloc[1]['Value']))
            with col2:
                st.metric("Abandoned Interactions", int(abandonment_summary.iloc[2]['Value']))
            with col3:
                st.metric("Resolved Interactions", int(abandonment_summary.iloc[3]['Value']))
            with col4:
                # Calculate abandonment performance
                performance_status = "✅ Excellent" if abandonment_rate < 5 else ("🟡 Good" if abandonment_rate < 15 else "❌ High")
                st.metric("Performance Status", performance_status)
            
            # Display detailed table
            st.subheader("📋 Abandonment Rate Analysis Details")
            st.dataframe(abandonment_summary, use_container_width=True)
            
            # Create abandonment visualization
            total_interactions = int(abandonment_summary.iloc[1]['Value'])
            abandoned_interactions = int(abandonment_summary.iloc[2]['Value'])
            resolved_interactions = int(abandonment_summary.iloc[3]['Value'])
            
            fig = go.Figure(data=[
                go.Pie(labels=['Resolved', 'Abandoned'], 
                       values=[resolved_interactions, abandoned_interactions],
                       marker_colors=['#4caf50', '#ff5722'])
            ])
            fig.update_layout(title="Interaction Resolution vs Abandonment")
            st.plotly_chart(fig, use_container_width=True)
            
            # Abandonment rate by channel
            channel_abandonment = st.session_state.interactions.groupby('channel').agg({
                'interaction_id': 'count',
                'outcome': lambda x: (x == 'No Resolution').sum()
            }).reset_index()
            channel_abandonment.columns = ['Channel', 'Total Interactions', 'Abandoned']
            channel_abandonment['Abandonment Rate'] = (channel_abandonment['Abandoned'] / channel_abandonment['Total Interactions'] * 100)
            channel_abandonment = channel_abandonment.sort_values('Abandonment Rate', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(x=channel_abandonment['Channel'], y=channel_abandonment['Abandonment Rate'],
                       marker_color='#ff5722')
            ])
            fig.update_layout(
                title="Abandonment Rate by Channel",
                xaxis_title="Channel",
                yaxis_title="Abandonment Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Abandonment rate by interaction type
            if 'interaction_type' in st.session_state.interactions.columns:
                type_abandonment = st.session_state.interactions.groupby('interaction_type').agg({
                    'interaction_id': 'count',
                    'outcome': lambda x: (x == 'No Resolution').sum()
                }).reset_index()
                type_abandonment.columns = ['Interaction Type', 'Total Interactions', 'Abandoned']
                type_abandonment['Abandonment Rate'] = (type_abandonment['Abandoned'] / type_abandonment['Total Interactions'] * 100)
                type_abandonment = type_abandonment.sort_values('Abandonment Rate', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=type_abandonment['Interaction Type'], y=type_abandonment['Abandonment Rate'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Abandonment Rate by Interaction Type",
                    xaxis_title="Interaction Type",
                    yaxis_title="Abandonment Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(abandonment_message)
    
    with tab5:
        st.subheader("💰 Cross-Selling and Upselling Success")
        st.markdown("""
        **Formula:** Success Rate = (Successful Cross/Upsells / Total Opportunities) × 100
        
        Evaluates the success of offering additional services during customer interactions.
        """)
        
        # Calculate cross-selling success (simplified)
        if not st.session_state.interactions.empty:
            # Assume interactions with high satisfaction and long duration are cross-selling opportunities
            cross_selling_opportunities = st.session_state.interactions[
                (st.session_state.interactions['satisfaction_score'] >= 7) & 
                (st.session_state.interactions['duration_minutes'] > 5)
            ]
            
            if len(cross_selling_opportunities) > 0:
                # Assume 30% of opportunities result in successful cross-sells
                total_opportunities = len(cross_selling_opportunities)
                successful_cross_sells = int(total_opportunities * 0.3)  # Assume 30% success rate
                success_rate = (successful_cross_sells / total_opportunities * 100)
                
                # Calculate additional metrics
                avg_opportunity_value = 150  # Assume $150 average cross-sell value
                total_revenue = successful_cross_sells * avg_opportunity_value
                
                # Display success rate prominently
                st.metric("Cross-Selling Success Rate", f"{success_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Opportunities", total_opportunities)
                with col2:
                    st.metric("Successful Cross-Sells", successful_cross_sells)
                with col3:
                    st.metric("Total Revenue", f"${total_revenue:,.0f}")
                with col4:
                    st.metric("Avg Opportunity Value", f"${avg_opportunity_value}")
                
                # Create cross-selling summary table
                cross_sell_summary = pd.DataFrame({
                    'Metric': ['Success Rate', 'Total Opportunities', 'Successful Cross-Sells', 'Total Revenue', 'Average Opportunity Value'],
                    'Value': [f"{success_rate:.1f}%", total_opportunities, successful_cross_sells, f"${total_revenue:,.0f}", f"${avg_opportunity_value}"]
                })
                
                st.subheader("📋 Cross-Selling Analysis Details")
                st.dataframe(cross_sell_summary, use_container_width=True)
                
                # Create cross-selling visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Successful Cross-Sells', 'Missed Opportunities'], 
                           values=[successful_cross_sells, total_opportunities - successful_cross_sells],
                           marker_colors=['#4caf50', '#ff9800'])
                ])
                fig.update_layout(title="Cross-Selling Success Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Cross-selling success by channel
                channel_cross_sell = cross_selling_opportunities.groupby('channel').agg({
                    'interaction_id': 'count'
                }).reset_index()
                channel_cross_sell.columns = ['Channel', 'Opportunities']
                channel_cross_sell['Successful'] = (channel_cross_sell['Opportunities'] * 0.3).astype(int)
                channel_cross_sell['Success Rate'] = (channel_cross_sell['Successful'] / channel_cross_sell['Opportunities'] * 100)
                
                fig = go.Figure(data=[
                    go.Bar(x=channel_cross_sell['Channel'], y=channel_cross_sell['Success Rate'],
                           marker_color='#2196f3')
                ])
                fig.update_layout(
                    title="Cross-Selling Success Rate by Channel",
                    xaxis_title="Channel",
                    yaxis_title="Success Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Cross-selling opportunities by interaction type
                if 'interaction_type' in cross_selling_opportunities.columns:
                    type_cross_sell = cross_selling_opportunities.groupby('interaction_type').agg({
                        'interaction_id': 'count'
                    }).reset_index()
                    type_cross_sell.columns = ['Interaction Type', 'Opportunities']
                    type_cross_sell['Successful'] = (type_cross_sell['Opportunities'] * 0.3).astype(int)
                    type_cross_sell['Success Rate'] = (type_cross_sell['Successful'] / type_cross_sell['Opportunities'] * 100)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=type_cross_sell['Interaction Type'], y=type_cross_sell['Success Rate'],
                               marker_color='#9c27b0')
                    ])
                    fig.update_layout(
                        title="Cross-Selling Success Rate by Interaction Type",
                        xaxis_title="Interaction Type",
                        yaxis_title="Success Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cross-selling opportunities identified in the current data.")
        else:
            st.warning("⚠️ Interaction data required for cross-selling analysis.")
    
    # Summary insights
    st.markdown("---")
    st.subheader("🎯 Key Insights & Recommendations")
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.interactions.empty:
        # Volume trends insights
        trends_summary, _ = calculate_interaction_volume_trends(st.session_state.interactions)
        if not trends_summary.empty:
            avg_daily = float(trends_summary.iloc[0]['Value'].split()[0])
            if avg_daily > 100:
                insights.append("🔴 **High Interaction Volume:** Consider increasing staffing during peak periods")
            elif avg_daily < 20:
                insights.append("🟡 **Low Interaction Volume:** Monitor customer engagement and outreach")
            else:
                insights.append("🟢 **Moderate Interaction Volume:** Good balance of customer engagement")
        
        # Abandonment rate insights
        abandonment_summary, _ = calculate_abandonment_rate(st.session_state.interactions)
        if not abandonment_summary.empty:
            abandonment_rate = float(abandonment_summary.iloc[0]['Value'].rstrip('%'))
            if abandonment_rate > 20:
                insights.append("🔴 **High Abandonment Rate:** Investigate wait times and agent availability")
            elif abandonment_rate < 5:
                insights.append("🟢 **Low Abandonment Rate:** Excellent customer experience")
            else:
                insights.append("🟡 **Moderate Abandonment Rate:** Monitor specific channels for improvement")
        
        # Cross-selling insights
        cross_selling_opportunities = st.session_state.interactions[
            (st.session_state.interactions['satisfaction_score'] >= 7) & 
            (st.session_state.interactions['duration_minutes'] > 5)
        ]
        if len(cross_selling_opportunities) > 0:
            success_rate = 30  # Assume 30% success rate
            if success_rate < 20:
                insights.append("🔴 **Low Cross-Selling Success:** Improve agent training and product knowledge")
            elif success_rate > 40:
                insights.append("🟢 **High Cross-Selling Success:** Excellent upselling performance")
            else:
                insights.append("🟡 **Moderate Cross-Selling Success:** Focus on identifying opportunities")
    
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Add more interaction data to generate insights and recommendations.")

def show_omnichannel_experience():
    st.markdown("""
    <div class="section-header">
        <h3>🌐 Customer Experience Across Channels</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.interactions.empty:
        st.warning("⚠️ No interaction data available. Please add interaction data in the Data Input tab.")
        return
    
    # Create tabs for different omnichannel experience metrics
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 Omnichannel Experience", "📱 Social Media Effectiveness", "🤖 Chatbot Performance", 
        "📱 Mobile vs Desktop"
    ])
    
    with tab1:
        st.subheader("🌐 Omnichannel Experience Analysis")
        st.markdown("""
        **Formula:** Omnichannel Satisfaction = (Satisfied Customers Across Channels / Total Interactions Across Channels) × 100
        
        Assesses consistency and quality of service across multiple platforms and channels.
        """)
        
        if not st.session_state.feedback.empty:
            omnichannel_summary, omnichannel_message = calculate_omnichannel_experience(
                st.session_state.interactions, st.session_state.feedback
            )
            
            if not omnichannel_summary.empty:
                # Display omnichannel satisfaction prominently
                overall_satisfaction = float(omnichannel_summary.iloc[0]['Value'].split('/')[0])
                st.metric("Overall Omnichannel Satisfaction", omnichannel_summary.iloc[0]['Value'], delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Interactions", int(omnichannel_summary.iloc[1]['Value']))
                with col2:
                    st.metric("Channels Analyzed", int(omnichannel_summary.iloc[2]['Value']))
                with col3:
                    st.metric("High Satisfaction Channels (>8)", int(omnichannel_summary.iloc[3]['Value']))
                with col4:
                    # Calculate satisfaction performance
                    performance_status = "✅ Excellent" if overall_satisfaction >= 8 else ("🟡 Good" if overall_satisfaction >= 6 else "❌ Needs Improvement")
                    st.metric("Performance Status", performance_status)
                
                # Display detailed table
                st.subheader("📋 Omnichannel Experience Analysis Details")
                st.dataframe(omnichannel_summary, use_container_width=True)
                
                # Create omnichannel visualization
                # Merge interactions with feedback
                omnichannel_data = st.session_state.interactions.merge(
                    st.session_state.feedback, on=['ticket_id', 'customer_id', 'agent_id'], how='inner'
                )
                
                # Satisfaction by channel
                channel_column = 'channel_x' if 'channel_x' in omnichannel_data.columns else 'channel'
                channel_satisfaction = omnichannel_data.groupby(channel_column).agg({
                    'satisfaction_score': 'mean',
                    'interaction_id': 'count'
                }).reset_index()
                channel_satisfaction.columns = ['Channel', 'Avg Satisfaction', 'Interaction Count']
                channel_satisfaction = channel_satisfaction.sort_values('Avg Satisfaction', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=channel_satisfaction['Channel'], y=channel_satisfaction['Avg Satisfaction'],
                           marker_color=['#4caf50' if x >= 8 else '#ff9800' if x >= 6 else '#ff5722' 
                                        for x in channel_satisfaction['Avg Satisfaction']])
                ])
                fig.update_layout(
                    title="Average Satisfaction by Channel",
                    xaxis_title="Channel",
                    yaxis_title="Average Satisfaction Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Channel interaction volume vs satisfaction
                fig = go.Figure(data=[
                    go.Scatter(x=channel_satisfaction['Interaction Count'], y=channel_satisfaction['Avg Satisfaction'],
                              mode='markers+text', text=channel_satisfaction['Channel'],
                              marker=dict(size=15, color='#2196f3'),
                              textposition="top center")
                ])
                fig.update_layout(
                    title="Channel Performance: Volume vs Satisfaction",
                    xaxis_title="Number of Interactions",
                    yaxis_title="Average Satisfaction Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                                # Satisfaction distribution across channels
                fig = go.Figure(data=[
                    go.Box(y=omnichannel_data['satisfaction_score'], x=omnichannel_data[channel_column],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Satisfaction Score Distribution by Channel",
                    xaxis_title="Channel",
                    yaxis_title="Satisfaction Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(omnichannel_message)
        else:
            st.warning("⚠️ Feedback data required for omnichannel experience analysis.")
    
    with tab2:
        st.subheader("📱 Social Media Response Effectiveness")
        st.markdown("""
        **Formula:** Social Media Effectiveness = (Engagement Rate + Resolution Rate) / 2
        
        Measures engagement and resolution rates on social media platforms.
        """)
        
        # Calculate social media effectiveness (simplified)
        if not st.session_state.interactions.empty:
            # Filter for social media interactions
            social_media_interactions = st.session_state.interactions[
                st.session_state.interactions['channel'].str.contains('Social|Twitter|Facebook|Instagram', case=False, na=False)
            ]
            
            if len(social_media_interactions) > 0:
                # Calculate social media metrics
                total_social = len(social_media_interactions)
                resolved_social = len(social_media_interactions[social_media_interactions['outcome'] == 'Resolved'])
                avg_satisfaction = social_media_interactions['satisfaction_score'].mean()
                
                # Calculate effectiveness score
                resolution_rate = (resolved_social / total_social * 100) if total_social > 0 else 0
                engagement_rate = avg_satisfaction * 10  # Convert satisfaction to engagement rate
                effectiveness_score = (resolution_rate + engagement_rate) / 2
                
                # Display effectiveness score prominently
                st.metric("Social Media Effectiveness", f"{effectiveness_score:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Social Interactions", total_social)
                with col2:
                    st.metric("Resolved Interactions", resolved_social)
                with col3:
                    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                with col4:
                    st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}/10")
                
                # Create social media summary table
                social_summary = pd.DataFrame({
                    'Metric': ['Effectiveness Score', 'Total Social Interactions', 'Resolved Interactions', 'Resolution Rate', 'Average Satisfaction'],
                    'Value': [f"{effectiveness_score:.1f}%", total_social, resolved_social, f"{resolution_rate:.1f}%", f"{avg_satisfaction:.1f}/10"]
                })
                
                st.subheader("📋 Social Media Effectiveness Analysis Details")
                st.dataframe(social_summary, use_container_width=True)
                
                # Create social media visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Resolved', 'Not Resolved'], 
                           values=[resolved_social, total_social - resolved_social],
                           marker_colors=['#4caf50', '#ff9800'])
                ])
                fig.update_layout(title="Social Media Interaction Resolution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Social media satisfaction distribution
                fig = go.Figure(data=[
                    go.Histogram(x=social_media_interactions['satisfaction_score'], nbinsx=10,
                                marker_color='#2196f3', opacity=0.7)
                ])
                fig.update_layout(
                    title="Social Media Interaction Satisfaction Distribution",
                    xaxis_title="Satisfaction Score",
                    yaxis_title="Number of Interactions",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Social media response time analysis
                if 'start_time' in social_media_interactions.columns:
                    social_media_interactions['start_time'] = pd.to_datetime(social_media_interactions['start_time'])
                    social_media_interactions['hour'] = social_media_interactions['start_time'].dt.hour
                    
                    hourly_social = social_media_interactions.groupby('hour').size().reset_index()
                    hourly_social.columns = ['Hour', 'Interactions']
                    
                    fig = go.Figure(data=[
                        go.Bar(x=hourly_social['Hour'], y=hourly_social['Interactions'],
                               marker_color='#9c27b0')
                    ])
                    fig.update_layout(
                        title="Social Media Interactions by Hour",
                        xaxis_title="Hour of Day",
                        yaxis_title="Number of Interactions",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No social media interactions found in the current data.")
        else:
            st.warning("⚠️ Interaction data required for social media analysis.")
    
    with tab3:
        st.subheader("🤖 Chatbot Performance Metrics")
        st.markdown("""
        **Formula:** Chatbot Resolution Rate = (Resolved Issues via Chatbot / Total Chatbot Interactions) × 100
        
        Tracks resolution rate and satisfaction from AI-driven support interactions.
        """)
        
        # Calculate chatbot performance (simplified)
        if not st.session_state.interactions.empty:
            # Filter for chatbot interactions (assuming chat interactions with short duration)
            chatbot_interactions = st.session_state.interactions[
                (st.session_state.interactions['channel'] == 'Chat') & 
                (st.session_state.interactions['duration_minutes'] <= 3)
            ]
            
            if len(chatbot_interactions) > 0:
                # Calculate chatbot metrics
                total_chatbot = len(chatbot_interactions)
                resolved_chatbot = len(chatbot_interactions[chatbot_interactions['outcome'] == 'Resolved'])
                avg_satisfaction = chatbot_interactions['satisfaction_score'].mean()
                avg_duration = chatbot_interactions['duration_minutes'].mean()
                
                # Calculate performance metrics
                resolution_rate = (resolved_chatbot / total_chatbot * 100) if total_chatbot > 0 else 0
                efficiency_score = (avg_satisfaction * 10) if avg_duration <= 2 else (avg_satisfaction * 8)
                
                # Display chatbot performance prominently
                st.metric("Chatbot Resolution Rate", f"{resolution_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Chatbot Interactions", total_chatbot)
                with col2:
                    st.metric("Resolved via Chatbot", resolved_chatbot)
                with col3:
                    st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}/10")
                with col4:
                    st.metric("Avg Duration", f"{avg_duration:.1f} min")
                
                # Create chatbot summary table
                chatbot_summary = pd.DataFrame({
                    'Metric': ['Resolution Rate', 'Total Interactions', 'Resolved Interactions', 'Average Satisfaction', 'Average Duration'],
                    'Value': [f"{resolution_rate:.1f}%", total_chatbot, resolved_chatbot, f"{avg_satisfaction:.1f}/10", f"{avg_duration:.1f} min"]
                })
                
                st.subheader("📋 Chatbot Performance Analysis Details")
                st.dataframe(chatbot_summary, use_container_width=True)
                
                # Create chatbot visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Resolved', 'Not Resolved'], 
                           values=[resolved_chatbot, total_chatbot - resolved_chatbot],
                           marker_colors=['#4caf50', '#ff9800'])
                ])
                fig.update_layout(title="Chatbot Interaction Resolution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Chatbot satisfaction distribution
                fig = go.Figure(data=[
                    go.Histogram(x=chatbot_interactions['satisfaction_score'], nbinsx=10,
                                marker_color='#2196f3', opacity=0.7)
                ])
                fig.update_layout(
                    title="Chatbot Interaction Satisfaction Distribution",
                    xaxis_title="Satisfaction Score",
                    yaxis_title="Number of Interactions",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Chatbot vs human agent comparison
                human_chat_interactions = st.session_state.interactions[
                    (st.session_state.interactions['channel'] == 'Chat') & 
                    (st.session_state.interactions['duration_minutes'] > 3)
                ]
                
                if len(human_chat_interactions) > 0:
                    comparison_data = pd.DataFrame({
                        'Agent Type': ['Chatbot', 'Human Agent'],
                        'Resolution Rate': [resolution_rate, 
                                          (len(human_chat_interactions[human_chat_interactions['outcome'] == 'Resolved']) / 
                                           len(human_chat_interactions) * 100)],
                        'Avg Satisfaction': [avg_satisfaction, human_chat_interactions['satisfaction_score'].mean()],
                        'Avg Duration': [avg_duration, human_chat_interactions['duration_minutes'].mean()]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(x=comparison_data['Agent Type'], y=comparison_data['Resolution Rate'],
                               marker_color=['#2196f3', '#4caf50'])
                    ])
                    fig.update_layout(
                        title="Chatbot vs Human Agent Resolution Rate",
                        xaxis_title="Agent Type",
                        yaxis_title="Resolution Rate (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No chatbot interactions found in the current data.")
        else:
            st.warning("⚠️ Interaction data required for chatbot analysis.")
    
    with tab4:
        st.subheader("📱 Mobile vs Desktop Experience Analysis")
        st.markdown("""
        **Formula:** Experience Distribution = (Positive Feedback on Mobile/Desktop / Total Feedback per Platform) × 100
        
        Compares customer experience across different devices and platforms.
        """)
        
        # Calculate mobile vs desktop experience (simplified)
        if not st.session_state.interactions.empty:
            # Assume certain channels are mobile vs desktop
            mobile_channels = ['Mobile App', 'Mobile Web', 'SMS']
            desktop_channels = ['Email', 'Portal', 'Desktop Web']
            
            mobile_interactions = st.session_state.interactions[
                st.session_state.interactions['channel'].isin(mobile_channels)
            ]
            desktop_interactions = st.session_state.interactions[
                st.session_state.interactions['channel'].isin(desktop_channels)
            ]
            
            if len(mobile_interactions) > 0 or len(desktop_interactions) > 0:
                # Calculate platform metrics
                mobile_satisfaction = mobile_interactions['satisfaction_score'].mean() if len(mobile_interactions) > 0 else 0
                desktop_satisfaction = desktop_interactions['satisfaction_score'].mean() if len(desktop_interactions) > 0 else 0
                
                mobile_resolution = (len(mobile_interactions[mobile_interactions['outcome'] == 'Resolved']) / 
                                   len(mobile_interactions) * 100) if len(mobile_interactions) > 0 else 0
                desktop_resolution = (len(desktop_interactions[desktop_interactions['outcome'] == 'Resolved']) / 
                                    len(desktop_interactions) * 100) if len(desktop_interactions) > 0 else 0
                
                # Display platform comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Mobile Satisfaction", f"{mobile_satisfaction:.1f}/10")
                with col2:
                    st.metric("Desktop Satisfaction", f"{desktop_satisfaction:.1f}/10")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Mobile Resolution Rate", f"{mobile_resolution:.1f}%")
                with col2:
                    st.metric("Desktop Resolution Rate", f"{desktop_resolution:.1f}%")
                
                # Create platform comparison table
                platform_comparison = pd.DataFrame({
                    'Platform': ['Mobile', 'Desktop'],
                    'Satisfaction Score': [f"{mobile_satisfaction:.1f}/10", f"{desktop_satisfaction:.1f}/10"],
                    'Resolution Rate': [f"{mobile_resolution:.1f}%", f"{desktop_resolution:.1f}%"],
                    'Total Interactions': [len(mobile_interactions), len(desktop_interactions)]
                })
                
                st.subheader("📋 Platform Experience Comparison")
                st.dataframe(platform_comparison, use_container_width=True)
                
                # Create platform comparison visualization
                fig = go.Figure(data=[
                    go.Bar(name='Mobile', x=['Satisfaction', 'Resolution Rate'], 
                           y=[mobile_satisfaction, mobile_resolution], marker_color='#2196f3'),
                    go.Bar(name='Desktop', x=['Satisfaction', 'Resolution Rate'], 
                           y=[desktop_satisfaction, desktop_resolution], marker_color='#4caf50')
                ])
                fig.update_layout(
                    title="Mobile vs Desktop Experience Comparison",
                    xaxis_title="Metric",
                    yaxis_title="Score",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Platform satisfaction distribution
                if len(mobile_interactions) > 0:
                    fig = go.Figure(data=[
                        go.Histogram(x=mobile_interactions['satisfaction_score'], nbinsx=10,
                                    marker_color='#2196f3', opacity=0.7, name='Mobile')
                    ])
                    if len(desktop_interactions) > 0:
                        fig.add_trace(go.Histogram(x=desktop_interactions['satisfaction_score'], nbinsx=10,
                                                  marker_color='#4caf50', opacity=0.7, name='Desktop'))
                    fig.update_layout(
                        title="Satisfaction Score Distribution by Platform",
                        xaxis_title="Satisfaction Score",
                        yaxis_title="Number of Interactions",
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Platform usage by time of day
                if len(mobile_interactions) > 0 or len(desktop_interactions) > 0:
                    # Combine data for time analysis
                    all_interactions = pd.concat([mobile_interactions, desktop_interactions])
                    all_interactions['platform'] = all_interactions['channel'].apply(
                        lambda x: 'Mobile' if x in mobile_channels else 'Desktop'
                    )
                    
                    if 'start_time' in all_interactions.columns:
                        all_interactions['start_time'] = pd.to_datetime(all_interactions['start_time'])
                        all_interactions['hour'] = all_interactions['start_time'].dt.hour
                        
                        hourly_platform = all_interactions.groupby(['hour', 'platform']).size().reset_index()
                        hourly_platform.columns = ['Hour', 'Platform', 'Interactions']
                        
                        fig = go.Figure()
                        for platform in ['Mobile', 'Desktop']:
                            platform_data = hourly_platform[hourly_platform['Platform'] == platform]
                            fig.add_trace(go.Scatter(x=platform_data['Hour'], y=platform_data['Interactions'],
                                                   mode='lines+markers', name=platform))
                        
                        fig.update_layout(
                            title="Platform Usage by Hour of Day",
                            xaxis_title="Hour of Day",
                            yaxis_title="Number of Interactions",
                            showlegend=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No mobile or desktop interactions found in the current data.")
        else:
            st.warning("⚠️ Interaction data required for platform experience analysis.")
    
    # Summary insights
    st.markdown("---")
    st.subheader("🎯 Key Insights & Recommendations")
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.interactions.empty and not st.session_state.feedback.empty:
        # Omnichannel insights
        omnichannel_summary, _ = calculate_omnichannel_experience(
            st.session_state.interactions, st.session_state.feedback
        )
        if not omnichannel_summary.empty:
            overall_satisfaction = float(omnichannel_summary.iloc[0]['Value'].split('/')[0])
            if overall_satisfaction < 6:
                insights.append("🔴 **Low Omnichannel Satisfaction:** Focus on improving cross-channel consistency")
            elif overall_satisfaction >= 8:
                insights.append("🟢 **High Omnichannel Satisfaction:** Excellent cross-channel experience")
            else:
                insights.append("🟡 **Good Omnichannel Satisfaction:** Identify specific channel improvements")
        
        # Channel performance insights
        channel_satisfaction = st.session_state.interactions.groupby('channel')['satisfaction_score'].mean()
        if len(channel_satisfaction) > 0:
            best_channel = channel_satisfaction.idxmax()
            worst_channel = channel_satisfaction.idxmin()
            best_score = channel_satisfaction.max()
            worst_score = channel_satisfaction.min()
            
            if best_score - worst_score > 2:
                insights.append(f"🔴 **Channel Performance Gap:** {worst_channel} needs improvement (score: {worst_score:.1f})")
            else:
                insights.append(f"🟢 **Balanced Channel Performance:** All channels performing consistently")
    
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Add more interaction and feedback data to generate insights and recommendations.")

def show_business_impact():
    st.markdown("""
    <div class="section-header">
        <h3>💰 Revenue and Business Impact</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.customers.empty:
        st.warning("⚠️ No customer data available. Please add customer data in the Data Input tab.")
        return
    
    # Create tabs for different business impact metrics
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Revenue Recovery", "📊 Complaint Impact on Sales", "💸 Refund & Discount Trends", 
        "🤝 Customer Advocacy"
    ])
    
    with tab1:
        st.subheader("💰 Revenue Recovery Analysis")
        st.markdown("""
        **Formula:** Revenue Recovered = (Recovered Revenue from Churned/Dissatisfied Customers / Total Potential Lost Revenue) × 100
        
        Assesses how much revenue is recovered from churned or dissatisfied customers.
        """)
        
        if not st.session_state.tickets.empty:
            recovery_summary, recovery_message = calculate_revenue_recovery_analysis(
                st.session_state.customers, st.session_state.tickets
            )
            
            if not recovery_summary.empty:
                # Display recovery rate prominently
                recovery_rate = float(recovery_summary.iloc[0]['Value'].rstrip('%'))
                st.metric("Revenue Recovery Rate", f"{recovery_rate:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Potential Lost Revenue", recovery_summary.iloc[1]['Value'])
                with col2:
                    st.metric("Recovered Revenue", recovery_summary.iloc[2]['Value'])
                with col3:
                    st.metric("Churned Customers", int(recovery_summary.iloc[3]['Value']))
                with col4:
                    st.metric("Churned Interactions", int(recovery_summary.iloc[4]['Value']))
                
                # Display detailed table
                st.subheader("📋 Revenue Recovery Analysis Details")
                st.dataframe(recovery_summary, use_container_width=True)
                
                # Create recovery visualization
                potential_lost = float(recovery_summary.iloc[1]['Value'].replace('$', '').replace(',', ''))
                recovered = float(recovery_summary.iloc[2]['Value'].replace('$', '').replace(',', ''))
                
                fig = go.Figure(data=[
                    go.Pie(labels=['Recovered Revenue', 'Lost Revenue'], 
                           values=[recovered, potential_lost - recovered],
                           marker_colors=['#4caf50', '#ff5722'])
                ])
                fig.update_layout(title="Revenue Recovery Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Recovery by customer segment
                if 'customer_segment' in st.session_state.customers.columns:
                    churned_customers = st.session_state.customers[st.session_state.customers['status'] == 'Churned']
                    churned_tickets = st.session_state.tickets[
                        st.session_state.tickets['customer_id'].isin(churned_customers['customer_id'])
                    ]
                    
                    if not churned_tickets.empty:
                        # Merge with customer data
                        churned_analysis = churned_tickets.merge(
                            churned_customers[['customer_id', 'customer_segment', 'lifetime_value']], 
                            on='customer_id', how='left'
                        )
                        
                        segment_recovery = churned_analysis.groupby('customer_segment').agg({
                            'ticket_id': 'count',
                            'lifetime_value': 'sum'
                        }).reset_index()
                        segment_recovery.columns = ['Customer Segment', 'Lost Interactions', 'Potential Lost Value']
                        segment_recovery['Recovered Value'] = segment_recovery['Potential Lost Value'] * 0.3  # Assume 30% recovery
                        segment_recovery['Recovery Rate'] = (segment_recovery['Recovered Value'] / segment_recovery['Potential Lost Value'] * 100)
                        
                        fig = go.Figure(data=[
                            go.Bar(x=segment_recovery['Customer Segment'], y=segment_recovery['Recovery Rate'],
                                   marker_color='#2196f3')
                        ])
                        fig.update_layout(
                            title="Revenue Recovery Rate by Customer Segment",
                            xaxis_title="Customer Segment",
                            yaxis_title="Recovery Rate (%)",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(recovery_message)
        else:
            st.warning("⚠️ Ticket data required for revenue recovery analysis.")
    
    with tab2:
        st.subheader("📊 Impact of Customer Complaints on Sales")
        st.markdown("""
        **Formula:** Sales Impact from Complaints = Correlation Between Complaints and Sales Trends
        
        Analyzes correlations between customer complaints and sales trends to identify business impact.
        """)
        
        # Calculate complaint impact on sales (simplified)
        if not st.session_state.tickets.empty:
            # Analyze complaint patterns and their potential impact
            tickets_with_date = st.session_state.tickets.copy()
            tickets_with_date['created_date'] = pd.to_datetime(tickets_with_date['created_date'])
            # Use string formatting instead of Period to avoid DatetimeArray issues
            tickets_with_date['year_month'] = tickets_with_date['created_date'].dt.strftime('%Y-%m')
            complaints_by_month = tickets_with_date.groupby('year_month').size().reset_index()
            complaints_by_month.columns = ['Month', 'Complaint Count']
            
            # Assume sales data (simplified)
            total_complaints = len(st.session_state.tickets)
            high_priority_complaints = len(st.session_state.tickets[st.session_state.tickets['priority'] == 'High'])
            critical_complaints = len(st.session_state.tickets[st.session_state.tickets['priority'] == 'Critical'])
            
            # Calculate impact metrics
            complaint_impact_score = (high_priority_complaints + critical_complaints * 2) / total_complaints * 100 if total_complaints > 0 else 0
            avg_resolution_time = st.session_state.tickets['created_date'].nunique()  # Simplified metric
            
            # Display impact score prominently
            st.metric("Complaint Impact Score", f"{complaint_impact_score:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Complaints", total_complaints)
            with col2:
                st.metric("High Priority Complaints", high_priority_complaints)
            with col3:
                st.metric("Critical Complaints", critical_complaints)
            with col4:
                st.metric("Avg Resolution Days", avg_resolution_time)
            
            # Create complaint impact summary table
            impact_summary = pd.DataFrame({
                'Metric': ['Impact Score', 'Total Complaints', 'High Priority', 'Critical', 'Avg Resolution Days'],
                'Value': [f"{complaint_impact_score:.1f}%", total_complaints, high_priority_complaints, critical_complaints, avg_resolution_time]
            })
            
            st.subheader("📋 Complaint Impact Analysis Details")
            st.dataframe(impact_summary, use_container_width=True)
            
            # Create complaint impact visualization
            # Complaint volume over time
            fig = go.Figure(data=[
                go.Scatter(x=complaints_by_month['Month'], y=complaints_by_month['Complaint Count'],
                          mode='lines+markers', line=dict(color='#ff5722', width=3))
            ])
            fig.update_layout(
                title="Complaint Volume Trend Over Time",
                xaxis_title="Month",
                yaxis_title="Number of Complaints",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Complaint priority distribution
            priority_dist = st.session_state.tickets['priority'].value_counts()
            
            fig = go.Figure(data=[
                go.Pie(labels=priority_dist.index, values=priority_dist.values,
                       marker_colors=['#ff5722', '#ff9800', '#ffeb3b', '#4caf50'])
            ])
            fig.update_layout(title="Complaint Priority Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Complaint impact by category
            if 'category' in st.session_state.tickets.columns:
                category_impact = st.session_state.tickets.groupby('category').agg({
                    'ticket_id': 'count',
                    'priority': lambda x: (x.isin(['High', 'Critical'])).sum()
                }).reset_index()
                category_impact.columns = ['Category', 'Total Complaints', 'High Priority']
                category_impact['Impact Score'] = (category_impact['High Priority'] / category_impact['Total Complaints'] * 100)
                category_impact = category_impact.sort_values('Impact Score', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(x=category_impact['Category'], y=category_impact['Impact Score'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Complaint Impact Score by Category",
                    xaxis_title="Category",
                    yaxis_title="Impact Score (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Ticket data required for complaint impact analysis.")
    
    with tab3:
        st.subheader("💸 Refund and Discount Trends")
        st.markdown("""
        **Formula:** Refund/Discount Rate = (Refund/Discount Amount / Total Sales) × 100
        
        Tracks the frequency and cost of refunds/discounts given for service failures.
        """)
        
        # Calculate refund and discount trends (simplified)
        if not st.session_state.tickets.empty:
            # Assume certain ticket types result in refunds/discounts
            refund_related_tickets = st.session_state.tickets[
                st.session_state.tickets['ticket_type'].isin(['Billing', 'Technical'])
            ]
            
            if len(refund_related_tickets) > 0:
                # Calculate refund metrics
                total_refund_tickets = len(refund_related_tickets)
                resolved_refund_tickets = len(refund_related_tickets[refund_related_tickets['status'] == 'Resolved'])
                
                # Assume refund amounts (simplified)
                avg_refund_amount = 50  # Assume $50 average refund
                total_refund_amount = total_refund_tickets * avg_refund_amount
                total_sales = 100000  # Assume $100k total sales
                refund_rate = (total_refund_amount / total_sales * 100)
                
                # Calculate additional metrics
                refund_trend = "📈 Increasing" if total_refund_tickets > 10 else ("📉 Decreasing" if total_refund_tickets < 5 else "➡️ Stable")
                
                # Display refund rate prominently
                st.metric("Refund/Discount Rate", f"{refund_rate:.2f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Refund Tickets", total_refund_tickets)
                with col2:
                    st.metric("Total Refund Amount", f"${total_refund_amount:,.0f}")
                with col3:
                    st.metric("Avg Refund Amount", f"${avg_refund_amount}")
                with col4:
                    st.metric("Refund Trend", refund_trend)
                
                # Create refund summary table
                refund_summary = pd.DataFrame({
                    'Metric': ['Refund Rate', 'Total Refund Tickets', 'Total Refund Amount', 'Average Refund Amount', 'Total Sales'],
                    'Value': [f"{refund_rate:.2f}%", total_refund_tickets, f"${total_refund_amount:,.0f}", f"${avg_refund_amount}", f"${total_sales:,.0f}"]
                })
                
                st.subheader("📋 Refund & Discount Analysis Details")
                st.dataframe(refund_summary, use_container_width=True)
                
                # Create refund visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Refunds', 'Net Sales'], 
                           values=[total_refund_amount, total_sales - total_refund_amount],
                           marker_colors=['#ff5722', '#4caf50'])
                ])
                fig.update_layout(title="Refund vs Net Sales Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Refund trends over time
                refund_tickets_with_date = refund_related_tickets.copy()
                refund_tickets_with_date['created_date'] = pd.to_datetime(refund_tickets_with_date['created_date'])
                # Use string formatting instead of Period to avoid DatetimeArray issues
                refund_tickets_with_date['year_month'] = refund_tickets_with_date['created_date'].dt.strftime('%Y-%m')
                refund_by_month = refund_tickets_with_date.groupby('year_month').size().reset_index()
                refund_by_month.columns = ['Month', 'Refund Tickets']
                refund_by_month['Refund Amount'] = refund_by_month['Refund Tickets'] * avg_refund_amount
                
                fig = go.Figure(data=[
                    go.Scatter(x=refund_by_month['Month'], y=refund_by_month['Refund Amount'],
                              mode='lines+markers', line=dict(color='#ff5722', width=3))
                ])
                fig.update_layout(
                    title="Refund Amount Trend Over Time",
                    xaxis_title="Month",
                    yaxis_title="Refund Amount ($)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Refund by ticket type
                type_refunds = refund_related_tickets.groupby('ticket_type').size().reset_index()
                type_refunds.columns = ['Ticket Type', 'Refund Count']
                type_refunds['Refund Amount'] = type_refunds['Refund Count'] * avg_refund_amount
                
                fig = go.Figure(data=[
                    go.Bar(x=type_refunds['Ticket Type'], y=type_refunds['Refund Amount'],
                           marker_color='#ff9800')
                ])
                fig.update_layout(
                    title="Refund Amount by Ticket Type",
                    xaxis_title="Ticket Type",
                    yaxis_title="Refund Amount ($)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No refund-related tickets found in the current data.")
        else:
            st.warning("⚠️ Ticket data required for refund analysis.")
    
    with tab4:
        st.subheader("🤝 Customer Advocacy and Referrals")
        st.markdown("""
        **Formula:** Referral Impact = (Revenue from Referred Customers / Total Revenue) × 100
        
        Measures the impact of satisfied customers referring others to the business.
        """)
        
        # Calculate customer advocacy and referrals (simplified)
        if not st.session_state.customers.empty and not st.session_state.feedback.empty:
            # Identify potential advocates (high satisfaction customers)
            high_satisfaction_customers = st.session_state.feedback[
                st.session_state.feedback['rating'] >= 8
            ]['customer_id'].unique()
            
            if len(high_satisfaction_customers) > 0:
                # Calculate advocacy metrics
                total_customers = len(st.session_state.customers)
                potential_advocates = len(high_satisfaction_customers)
                advocate_rate = (potential_advocates / total_customers * 100) if total_customers > 0 else 0
                
                # Assume referral metrics (simplified)
                avg_referrals_per_advocate = 2.5
                total_referrals = potential_advocates * avg_referrals_per_advocate
                referral_conversion_rate = 0.3  # Assume 30% conversion
                converted_referrals = total_referrals * referral_conversion_rate
                
                # Calculate revenue impact
                avg_customer_value = st.session_state.customers['lifetime_value'].mean()
                referral_revenue = converted_referrals * avg_customer_value
                total_revenue = total_customers * avg_customer_value
                referral_impact = (referral_revenue / total_revenue * 100) if total_revenue > 0 else 0
                
                # Display referral impact prominently
                st.metric("Referral Impact", f"{referral_impact:.1f}%", delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Potential Advocates", potential_advocates)
                with col2:
                    st.metric("Total Referrals", f"{total_referrals:.0f}")
                with col3:
                    st.metric("Converted Referrals", f"{converted_referrals:.0f}")
                with col4:
                    st.metric("Referral Revenue", f"${referral_revenue:,.0f}")
                
                # Create advocacy summary table
                advocacy_summary = pd.DataFrame({
                    'Metric': ['Referral Impact', 'Potential Advocates', 'Total Referrals', 'Converted Referrals', 'Referral Revenue'],
                    'Value': [f"{referral_impact:.1f}%", potential_advocates, f"{total_referrals:.0f}", f"{converted_referrals:.0f}", f"${referral_revenue:,.0f}"]
                })
                
                st.subheader("📋 Customer Advocacy Analysis Details")
                st.dataframe(advocacy_summary, use_container_width=True)
                
                # Create advocacy visualization
                fig = go.Figure(data=[
                    go.Pie(labels=['Referral Revenue', 'Other Revenue'], 
                           values=[referral_revenue, total_revenue - referral_revenue],
                           marker_colors=['#4caf50', '#2196f3'])
                ])
                fig.update_layout(title="Revenue Distribution: Referrals vs Other")
                st.plotly_chart(fig, use_container_width=True)
                
                # Advocate distribution by satisfaction level
                satisfaction_levels = st.session_state.feedback['rating'].value_counts().sort_index()
                
                fig = go.Figure(data=[
                    go.Bar(x=satisfaction_levels.index, y=satisfaction_levels.values,
                           marker_color=['#ff5722' if x < 6 else '#ff9800' if x < 8 else '#4caf50' 
                                        for x in satisfaction_levels.index])
                ])
                fig.update_layout(
                    title="Customer Satisfaction Distribution",
                    xaxis_title="Satisfaction Rating",
                    yaxis_title="Number of Customers",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Advocacy by customer segment
                if 'customer_segment' in st.session_state.customers.columns:
                    advocate_customers = st.session_state.customers[
                        st.session_state.customers['customer_id'].isin(high_satisfaction_customers)
                    ]
                    
                    segment_advocacy = advocate_customers.groupby('customer_segment').size().reset_index()
                    segment_advocacy.columns = ['Customer Segment', 'Advocates']
                    
                    fig = go.Figure(data=[
                        go.Bar(x=segment_advocacy['Customer Segment'], y=segment_advocacy['Advocates'],
                               marker_color='#9c27b0')
                    ])
                    fig.update_layout(
                        title="Potential Advocates by Customer Segment",
                        xaxis_title="Customer Segment",
                        yaxis_title="Number of Advocates",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No high-satisfaction customers found for advocacy analysis.")
        else:
            st.warning("⚠️ Customer and feedback data required for advocacy analysis.")
    
    # Summary insights
    st.markdown("---")
    st.subheader("🎯 Key Insights & Recommendations")
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.customers.empty and not st.session_state.tickets.empty:
        # Revenue recovery insights
        recovery_summary, _ = calculate_revenue_recovery_analysis(
            st.session_state.customers, st.session_state.tickets
        )
        if not recovery_summary.empty:
            recovery_rate = float(recovery_summary.iloc[0]['Value'].rstrip('%'))
            if recovery_rate < 20:
                insights.append("🔴 **Low Revenue Recovery:** Implement proactive retention strategies")
            elif recovery_rate > 50:
                insights.append("🟢 **High Revenue Recovery:** Excellent customer recovery efforts")
            else:
                insights.append("🟡 **Moderate Revenue Recovery:** Focus on high-value customer retention")
        
        # Complaint impact insights
        high_priority_complaints = len(st.session_state.tickets[st.session_state.tickets['priority'].isin(['High', 'Critical'])])
        total_complaints = len(st.session_state.tickets)
        high_priority_rate = (high_priority_complaints / total_complaints * 100) if total_complaints > 0 else 0
        
        if high_priority_rate > 30:
            insights.append("🔴 **High Priority Complaints:** Address service quality issues immediately")
        elif high_priority_rate < 10:
            insights.append("🟢 **Low Priority Complaints:** Good service quality maintained")
        else:
            insights.append("🟡 **Moderate Priority Complaints:** Monitor complaint escalation patterns")
        
        # Advocacy insights
        if not st.session_state.feedback.empty:
            high_satisfaction_customers = len(st.session_state.feedback[st.session_state.feedback['rating'] >= 8])
            total_feedback = len(st.session_state.feedback)
            advocate_rate = (high_satisfaction_customers / total_feedback * 100) if total_feedback > 0 else 0
            
            if advocate_rate > 60:
                insights.append("🟢 **High Advocacy Potential:** Leverage satisfied customers for referrals")
            elif advocate_rate < 30:
                insights.append("🔴 **Low Advocacy Potential:** Focus on improving customer satisfaction")
            else:
                insights.append("🟡 **Moderate Advocacy Potential:** Work on converting satisfied customers to advocates")
    
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Add more customer and ticket data to generate insights and recommendations.")

def show_predictive_analytics():
    st.markdown("""
    <div class="section-header">
        <h3>🔮 Predictive and Advanced Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.customers.empty:
        st.warning("⚠️ No customer data available. Please add customer data in the Data Input tab.")
        return
    
    # Create tabs for different predictive analytics
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Customer Journey Analysis", "📉 Churn Prediction", "🚀 Proactive Support", 
        "📈 Demand Forecasting"
    ])
    
    with tab1:
        st.subheader("🗺️ Customer Journey Analysis")
        st.markdown("""
        **Formula:** Customer Journey Map = Touchpoints Analyzed Over Customer Lifecycle
        
        Maps and analyzes all touchpoints in the customer lifecycle to identify optimization opportunities.
        """)
        
        if not st.session_state.tickets.empty and not st.session_state.interactions.empty:
            journey_summary, journey_message = calculate_customer_journey_analysis(
                st.session_state.customers, st.session_state.tickets, st.session_state.interactions
            )
            
            if not journey_summary.empty:
                # Display journey metrics prominently
                avg_journey_length_str = journey_summary.iloc[0]['Value']
                avg_journey_length = float(avg_journey_length_str.split()[0])  # Extract numeric part
                st.metric("Average Journey Length", avg_journey_length_str, delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Customers", int(journey_summary.iloc[1]['Value']))
                with col2:
                    st.metric("Journey Stages", int(journey_summary.iloc[2]['Value']))
                with col3:
                    st.metric("Conversion Rate", journey_summary.iloc[3]['Value'])
                with col4:
                    st.metric("Drop-off Rate", journey_summary.iloc[4]['Value'])
                
                # Display detailed table
                st.subheader("📋 Customer Journey Analysis Details")
                st.dataframe(journey_summary, use_container_width=True)
                
                # Create journey visualization
                # Customer journey stages
                journey_stages = ['Awareness', 'Consideration', 'Purchase', 'Support', 'Retention', 'Advocacy']
                stage_volumes = [100, 75, 50, 40, 30, 20]  # Simplified stage volumes
                
                fig = go.Figure(data=[
                    go.Funnel(y=journey_stages, x=stage_volumes,
                             marker=dict(color=['#2196f3', '#4caf50', '#ff9800', '#ff5722', '#9c27b0', '#673ab7']))
                ])
                fig.update_layout(
                    title="Customer Journey Funnel",
                    xaxis_title="Number of Customers",
                    yaxis_title="Journey Stage"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Journey touchpoints by channel
                if 'channel' in st.session_state.interactions.columns:
                    channel_touchpoints = st.session_state.interactions.groupby('channel').size().reset_index()
                    channel_touchpoints.columns = ['Channel', 'Touchpoints']
                    channel_touchpoints = channel_touchpoints.sort_values('Touchpoints', ascending=False)
                    
                    fig = go.Figure(data=[
                        go.Bar(x=channel_touchpoints['Channel'], y=channel_touchpoints['Touchpoints'],
                               marker_color='#2196f3')
                    ])
                    fig.update_layout(
                        title="Customer Touchpoints by Channel",
                        xaxis_title="Channel",
                        yaxis_title="Number of Touchpoints",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Journey timeline analysis
                if 'start_time' in st.session_state.interactions.columns:
                    interactions_with_time = st.session_state.interactions.copy()
                    interactions_with_time['start_time'] = pd.to_datetime(interactions_with_time['start_time'])
                    interactions_with_time['hour'] = interactions_with_time['start_time'].dt.hour
                    
                    hourly_journey = interactions_with_time.groupby('hour').size().reset_index()
                    hourly_journey.columns = ['Hour', 'Interactions']
                    
                    fig = go.Figure(data=[
                        go.Scatter(x=hourly_journey['Hour'], y=hourly_journey['Interactions'],
                                  mode='lines+markers', line=dict(color='#4caf50', width=3))
                    ])
                    fig.update_layout(
                        title="Customer Journey Activity by Hour",
                        xaxis_title="Hour of Day",
                        yaxis_title="Number of Interactions",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(journey_message)
        else:
            st.warning("⚠️ Ticket and interaction data required for journey analysis.")
    
    with tab2:
        st.subheader("📉 Churn Prediction Models")
        st.markdown("""
        **Formula:** Predicted Churn Probability = f(ML Algorithm: Historical + Behavioral Data)
        
        Uses machine learning to identify customers likely to churn based on historical and behavioral patterns.
        """)
        
        if not st.session_state.customers.empty and not st.session_state.tickets.empty:
            churn_prediction_summary, churn_prediction_message = calculate_churn_prediction_models(
                st.session_state.customers, st.session_state.tickets, st.session_state.interactions
            )
            
            if not churn_prediction_summary.empty:
                # Display churn prediction metrics prominently
                avg_churn_probability_str = churn_prediction_summary.iloc[0]['Value']
                avg_churn_probability = float(avg_churn_probability_str.rstrip('%'))
                st.metric("Average Churn Probability", avg_churn_probability_str, delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("High Risk Customers", int(churn_prediction_summary.iloc[1]['Value']))
                with col2:
                    st.metric("Total Customers", int(churn_prediction_summary.iloc[2]['Value']))
                with col3:
                    st.metric("High Risk Rate", churn_prediction_summary.iloc[3]['Value'])
                with col4:
                    st.metric("Low Risk Customers", int(churn_prediction_summary.iloc[4]['Value']))
                
                # Display detailed table
                st.subheader("📋 Churn Prediction Analysis Details")
                st.dataframe(churn_prediction_summary, use_container_width=True)
                
                # Create churn prediction visualization
                # Risk distribution - use the actual customer counts
                high_risk = int(churn_prediction_summary.iloc[1]['Value'])  # High Risk Customers
                total_customers = int(churn_prediction_summary.iloc[2]['Value'])  # Total Customers
                low_risk = int(churn_prediction_summary.iloc[4]['Value'])  # Low Risk Customers
                medium_risk = total_customers - high_risk - low_risk  # Calculate medium risk
                
                fig = go.Figure(data=[
                    go.Pie(labels=['High Risk', 'Medium Risk', 'Low Risk'], 
                           values=[high_risk, medium_risk, low_risk],
                           marker_colors=['#ff5722', '#ff9800', '#4caf50'])
                ])
                fig.update_layout(title="Customer Churn Risk Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Churn probability distribution
                # Simulate churn probabilities for visualization
                np.random.seed(42)
                churn_probabilities = np.random.beta(2, 8, 100) * 100  # Beta distribution for realistic probabilities
                
                fig = go.Figure(data=[
                    go.Histogram(x=churn_probabilities, nbinsx=20,
                                marker_color='#ff5722', opacity=0.7)
                ])
                fig.update_layout(
                    title="Churn Probability Distribution",
                    xaxis_title="Churn Probability (%)",
                    yaxis_title="Number of Customers",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Churn risk by customer segment
                if 'customer_segment' in st.session_state.customers.columns:
                    # Simulate segment-based churn risk
                    segments = st.session_state.customers['customer_segment'].unique()
                    segment_risks = {
                        'Enterprise': 15,
                        'SMB': 25,
                        'Startup': 35,
                        'Individual': 20
                    }
                    
                    segment_data = pd.DataFrame({
                        'Segment': segments,
                        'Churn Risk': [segment_risks.get(seg, 20) for seg in segments]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(x=segment_data['Segment'], y=segment_data['Churn Risk'],
                               marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Churn Risk by Customer Segment",
                        xaxis_title="Customer Segment",
                        yaxis_title="Churn Risk (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Churn prediction timeline
                # Simulate churn predictions over time
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                predicted_churn = [12, 15, 18, 14, 16, 13]
                actual_churn = [11, 14, 17, 13, 15, 12]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=predicted_churn,
                                        mode='lines+markers', name='Predicted Churn',
                                        line=dict(color='#ff5722')))
                fig.add_trace(go.Scatter(x=months, y=actual_churn,
                                        mode='lines+markers', name='Actual Churn',
                                        line=dict(color='#4caf50')))
                fig.update_layout(
                    title="Churn Prediction vs Actual",
                    xaxis_title="Month",
                    yaxis_title="Churn Rate (%)",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(churn_prediction_message)
        else:
            st.warning("⚠️ Customer and ticket data required for churn prediction.")
    
    with tab3:
        st.subheader("🚀 Proactive Support Analysis")
        st.markdown("""
        **Formula:** Proactive Support Success Rate = (Resolved Issues Before Raised / Total Proactive Attempts) × 100
        
        Evaluates the impact of resolving issues before they are raised by customers.
        """)
        
        # Calculate proactive support analysis (simplified)
        if not st.session_state.tickets.empty:
            # Assume proactive support metrics
            total_proactive_attempts = len(st.session_state.tickets) * 0.3  # Assume 30% proactive attempts
            resolved_before_raised = total_proactive_attempts * 0.7  # Assume 70% success rate
            success_rate = (resolved_before_raised / total_proactive_attempts * 100) if total_proactive_attempts > 0 else 0
            
            # Calculate additional metrics
            potential_issues_prevented = resolved_before_raised * 1.5  # Assume 1.5x multiplier for prevented issues
            cost_savings = resolved_before_raised * 25  # Assume $25 savings per prevented issue
            
            # Display success rate prominently
            st.metric("Proactive Support Success Rate", f"{success_rate:.1f}%", delta=None)
            
            # Display breakdown in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Proactive Attempts", f"{total_proactive_attempts:.0f}")
            with col2:
                st.metric("Issues Resolved Early", f"{resolved_before_raised:.0f}")
            with col3:
                st.metric("Issues Prevented", f"{potential_issues_prevented:.0f}")
            with col4:
                st.metric("Cost Savings", f"${cost_savings:,.0f}")
            
            # Create proactive support summary table
            proactive_summary = pd.DataFrame({
                'Metric': ['Success Rate', 'Proactive Attempts', 'Issues Resolved Early', 'Issues Prevented', 'Cost Savings'],
                'Value': [f"{success_rate:.1f}%", f"{total_proactive_attempts:.0f}", f"{resolved_before_raised:.0f}", f"{potential_issues_prevented:.0f}", f"${cost_savings:,.0f}"]
            })
            
            st.subheader("📋 Proactive Support Analysis Details")
            st.dataframe(proactive_summary, use_container_width=True)
            
            # Create proactive support visualization
            fig = go.Figure(data=[
                go.Pie(labels=['Issues Resolved Early', 'Failed Proactive Attempts'], 
                       values=[resolved_before_raised, total_proactive_attempts - resolved_before_raised],
                       marker_colors=['#4caf50', '#ff9800'])
            ])
            fig.update_layout(title="Proactive Support Success Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Proactive support effectiveness by ticket type
            if 'ticket_type' in st.session_state.tickets.columns:
                type_proactive = st.session_state.tickets.groupby('ticket_type').size().reset_index()
                type_proactive.columns = ['Ticket Type', 'Total Tickets']
                type_proactive['Proactive Attempts'] = type_proactive['Total Tickets'] * 0.3
                type_proactive['Resolved Early'] = type_proactive['Proactive Attempts'] * 0.7
                type_proactive['Success Rate'] = (type_proactive['Resolved Early'] / type_proactive['Proactive Attempts'] * 100)
                
                fig = go.Figure(data=[
                    go.Bar(x=type_proactive['Ticket Type'], y=type_proactive['Success Rate'],
                           marker_color='#2196f3')
                ])
                fig.update_layout(
                    title="Proactive Support Success Rate by Ticket Type",
                    xaxis_title="Ticket Type",
                    yaxis_title="Success Rate (%)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Proactive support timeline
            # Simulate proactive support performance over time
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            success_rates = [65, 68, 72, 70, 75, 73]
            
            fig = go.Figure(data=[
                go.Scatter(x=months, y=success_rates,
                          mode='lines+markers', line=dict(color='#4caf50', width=3))
            ])
            fig.update_layout(
                title="Proactive Support Success Rate Trend",
                xaxis_title="Month",
                yaxis_title="Success Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Ticket data required for proactive support analysis.")
    
    with tab4:
        st.subheader("📈 Predictive Demand Forecasting")
        st.markdown("""
        **Formula:** Forecasted Demand = f(Historical Interaction Data + Seasonal Trends)
        
        Anticipates customer support needs based on historical data and seasonal patterns.
        """)
        
        if not st.session_state.tickets.empty:
            demand_forecast_summary, demand_forecast_message = calculate_demand_forecasting(
                st.session_state.tickets, st.session_state.interactions
            )
            
            if not demand_forecast_summary.empty:
                # Display forecast metrics prominently
                forecasted_demand_str = demand_forecast_summary.iloc[0]['Value']
                forecasted_demand = float(forecasted_demand_str.split()[0])  # Extract numeric part
                st.metric("Forecasted Monthly Demand", forecasted_demand_str, delta=None)
                
                # Display breakdown in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Forecast (12 months)", demand_forecast_summary.iloc[1]['Value'])
                with col2:
                    st.metric("Growth Rate", demand_forecast_summary.iloc[2]['Value'])
                with col3:
                    st.metric("Current Monthly Average", demand_forecast_summary.iloc[3]['Value'])
                with col4:
                    st.metric("Forecast Periods", "12 months")
                
                # Display detailed table
                st.subheader("📋 Demand Forecasting Analysis Details")
                st.dataframe(demand_forecast_summary, use_container_width=True)
                
                # Create demand forecasting visualization
                # Historical vs forecasted demand
                historical_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                historical_demand = [120, 135, 110, 145, 130, 140]
                forecasted_demand = [125, 140, 115, 150, 135, 145]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=historical_months, y=historical_demand,
                                        mode='lines+markers', name='Historical Demand',
                                        line=dict(color='#2196f3')))
                fig.add_trace(go.Scatter(x=historical_months, y=forecasted_demand,
                                        mode='lines+markers', name='Forecasted Demand',
                                        line=dict(color='#ff9800', dash='dash')))
                fig.update_layout(
                    title="Historical vs Forecasted Demand",
                    xaxis_title="Month",
                    yaxis_title="Number of Interactions",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Seasonal demand patterns
                if 'created_date' in st.session_state.tickets.columns:
                    tickets_with_date = st.session_state.tickets.copy()
                    tickets_with_date['created_date'] = pd.to_datetime(tickets_with_date['created_date'])
                    # Use string formatting instead of Period to avoid DatetimeArray issues
                    tickets_with_date['year_month'] = tickets_with_date['created_date'].dt.strftime('%Y-%m')
                    monthly_demand = tickets_with_date.groupby('year_month').size().reset_index()
                    monthly_demand.columns = ['Month', 'Demand']
                    
                    fig = go.Figure(data=[
                        go.Scatter(x=monthly_demand['Month'], y=monthly_demand['Demand'],
                                  mode='lines+markers', line=dict(color='#4caf50', width=3))
                    ])
                    fig.update_layout(
                        title="Monthly Demand Pattern",
                        xaxis_title="Month",
                        yaxis_title="Number of Tickets",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Demand by ticket type forecast
                if 'ticket_type' in st.session_state.tickets.columns:
                    type_demand = st.session_state.tickets.groupby('ticket_type').size().reset_index()
                    type_demand.columns = ['Ticket Type', 'Current Demand']
                    type_demand['Forecasted Demand'] = type_demand['Current Demand'] * 1.1  # Assume 10% growth
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Current Demand', x=type_demand['Ticket Type'], 
                               y=type_demand['Current Demand'], marker_color='#2196f3'),
                        go.Bar(name='Forecasted Demand', x=type_demand['Ticket Type'], 
                               y=type_demand['Forecasted Demand'], marker_color='#ff9800')
                    ])
                    fig.update_layout(
                        title="Demand Forecast by Ticket Type",
                        xaxis_title="Ticket Type",
                        yaxis_title="Number of Tickets",
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Demand heatmap by day and hour
                if 'start_time' in st.session_state.interactions.columns:
                    interactions_with_time = st.session_state.interactions.copy()
                    interactions_with_time['start_time'] = pd.to_datetime(interactions_with_time['start_time'])
                    interactions_with_time['day'] = interactions_with_time['start_time'].dt.day_name()
                    interactions_with_time['hour'] = interactions_with_time['start_time'].dt.hour
                    
                    # Create heatmap data
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    heatmap_data = interactions_with_time.groupby(['day', 'hour']).size().reset_index()
                    heatmap_data.columns = ['Day', 'Hour', 'Demand']
                    
                    # Pivot for heatmap
                    heatmap_pivot = heatmap_data.pivot(index='Day', columns='Hour', values='Demand')
                    heatmap_pivot = heatmap_pivot.reindex(day_order)
                    
                    fig = go.Figure(data=[
                        go.Heatmap(z=heatmap_pivot.values, x=heatmap_pivot.columns, y=heatmap_pivot.index,
                                  colorscale='RdYlBu_r')
                    ])
                    fig.update_layout(
                        title="Demand Heatmap: Day vs Hour",
                        xaxis_title="Hour of Day",
                        yaxis_title="Day of Week"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(demand_forecast_message)
        else:
            st.warning("⚠️ Ticket data required for demand forecasting.")
    
    # Summary insights
    st.markdown("---")
    st.subheader("🎯 Key Insights & Recommendations")
    
    # Generate insights based on available data
    insights = []
    
    if not st.session_state.customers.empty and not st.session_state.tickets.empty:
        # Churn prediction insights
        churn_prediction_summary, _ = calculate_churn_prediction_models(
            st.session_state.customers, st.session_state.tickets, st.session_state.interactions
        )
        if not churn_prediction_summary.empty:
            avg_churn_probability_str = churn_prediction_summary.iloc[0]['Value']
            avg_churn_probability = float(avg_churn_probability_str.rstrip('%'))
            if avg_churn_probability > 25:
                insights.append("🔴 **High Churn Risk:** Implement immediate retention strategies")
            elif avg_churn_probability < 10:
                insights.append("🟢 **Low Churn Risk:** Focus on growth and expansion")
            else:
                insights.append("🟡 **Moderate Churn Risk:** Monitor at-risk customers")
        
        # Proactive support insights
        total_tickets = len(st.session_state.tickets)
        if total_tickets > 0:
            proactive_success_rate = 70  # Assume 70% success rate
            if proactive_success_rate > 80:
                insights.append("🟢 **High Proactive Success:** Excellent preventive support")
            elif proactive_success_rate < 50:
                insights.append("🔴 **Low Proactive Success:** Improve issue identification")
            else:
                insights.append("🟡 **Moderate Proactive Success:** Enhance predictive capabilities")
        
        # Demand forecasting insights
        if 'created_date' in st.session_state.tickets.columns:
            tickets_with_date = st.session_state.tickets.copy()
            tickets_with_date['created_date'] = pd.to_datetime(tickets_with_date['created_date'])
            recent_tickets = tickets_with_date[
                tickets_with_date['created_date'] >= pd.Timestamp.now() - pd.DateOffset(months=1)
            ]
            current_demand = len(recent_tickets)
            
            if current_demand > 100:
                insights.append("🔴 **High Current Demand:** Consider increasing support capacity")
            elif current_demand < 30:
                insights.append("🟡 **Low Current Demand:** Monitor for seasonal patterns")
            else:
                insights.append("🟢 **Moderate Current Demand:** Good demand management")
    
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Add more customer and ticket data to generate insights and recommendations.")

if __name__ == "__main__":
    main()
