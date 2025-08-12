import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import io
import base64
import random

# Import IT metric calculation functions
from it_metrics_calculator import *

# Chart creation functions - Sales App Style
def create_chart(chart_type, data, **kwargs):
    """Create charts with sales app styling"""
    
    if chart_type == "bar":
        fig = px.bar(data, **kwargs)
        fig.update_layout(xaxis_tickangle=-45)
    elif chart_type == "pie":
        fig = px.pie(data, **kwargs)
    elif chart_type == "line":
        fig = px.line(data, **kwargs, markers=True)
    elif chart_type == "scatter":
        fig = px.scatter(data, **kwargs)
    else:
        fig = px.bar(data, **kwargs)
        fig.update_layout(xaxis_tickangle=-45)
    
    return fig

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

def display_dataframe_with_index_1(df, **kwargs):
    """Display dataframe with index starting from 1"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        # Set a reasonable height to avoid inner scrollbars
        height = min(400, len(df_display) * 35 + 50)
        return st.dataframe(df_display, height=height, use_container_width=True, **kwargs)
    else:
        return st.dataframe(df, **kwargs)

def create_template_for_download():
    """Create an Excel template with all required IT data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct IT schema
    servers_template = pd.DataFrame(columns=[
        'server_id', 'server_name', 'server_type', 'location', 'ip_address', 
        'os_version', 'cpu_cores', 'ram_gb', 'storage_tb', 'status', 'last_maintenance'
    ])
    
    network_devices_template = pd.DataFrame(columns=[
        'device_id', 'device_name', 'device_type', 'location', 'ip_address', 
        'model', 'firmware_version', 'status', 'last_backup'
    ])
    
    applications_template = pd.DataFrame(columns=[
        'app_id', 'app_name', 'app_type', 'version', 'server_id', 'department', 
        'critical_level', 'status', 'last_update'
    ])
    
    incidents_template = pd.DataFrame(columns=[
        'incident_id', 'title', 'description', 'priority', 'category', 'reported_by', 
        'reported_date', 'assigned_to', 'status', 'resolution_date', 'resolution_time_minutes'
    ])
    
    tickets_template = pd.DataFrame(columns=[
        'ticket_id', 'title', 'description', 'priority', 'category', 'submitted_by', 
        'submitted_date', 'assigned_to', 'status', 'resolution_date', 'satisfaction_score'
    ])
    
    assets_template = pd.DataFrame(columns=[
        'asset_id', 'asset_name', 'asset_type', 'model', 'serial_number', 'purchase_date', 
        'warranty_expiry', 'location', 'assigned_to', 'status', 'purchase_cost'
    ])
    
    security_events_template = pd.DataFrame(columns=[
        'event_id', 'event_type', 'severity', 'source_ip', 'target_ip', 'timestamp', 
        'description', 'status', 'investigation_required'
    ])
    
    backups_template = pd.DataFrame(columns=[
        'backup_id', 'system_name', 'backup_type', 'start_time', 'end_time', 
        'size_gb', 'status', 'retention_days', 'location'
    ])
    
    projects_template = pd.DataFrame(columns=[
        'project_id', 'project_name', 'description', 'start_date', 'end_date', 
        'budget', 'actual_cost', 'status', 'manager', 'team_size'
    ])
    
    users_template = pd.DataFrame(columns=[
        'user_id', 'username', 'full_name', 'email', 'department', 'role', 
        'access_level', 'last_login', 'status', 'created_date'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        servers_template.to_excel(writer, sheet_name='Servers', index=False)
        network_devices_template.to_excel(writer, sheet_name='Network_Devices', index=False)
        applications_template.to_excel(writer, sheet_name='Applications', index=False)
        incidents_template.to_excel(writer, sheet_name='Incidents', index=False)
        tickets_template.to_excel(writer, sheet_name='Tickets', index=False)
        assets_template.to_excel(writer, sheet_name='Assets', index=False)
        security_events_template.to_excel(writer, sheet_name='Security_Events', index=False)
        backups_template.to_excel(writer, sheet_name='Backups', index=False)
        projects_template.to_excel(writer, sheet_name='Projects', index=False)
        users_template.to_excel(writer, sheet_name='Users', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Servers', 'Network_Devices', 'Applications', 'Incidents', 'Tickets', 'Assets', 'Security_Events', 'Backups', 'Projects', 'Users'],
            'Required Fields': [
                'server_id, server_name, server_type, location, ip_address, os_version, cpu_cores, ram_gb, storage_tb, status, last_maintenance',
                'device_id, device_name, device_type, location, ip_address, model, firmware_version, status, last_backup',
                'app_id, app_name, app_type, version, server_id, department, critical_level, status, last_update',
                'incident_id, title, description, priority, category, reported_by, reported_date, assigned_to, status, resolution_date, resolution_time_minutes',
                'ticket_id, title, description, priority, category, submitted_by, submitted_date, assigned_to, status, resolution_date, satisfaction_score',
                'asset_id, asset_name, asset_type, model, serial_number, purchase_date, warranty_expiry, location, assigned_to, status, purchase_cost',
                'event_id, event_type, severity, source_ip, target_ip, timestamp, description, status, investigation_required',
                'backup_id, system_name, backup_type, start_time, end_time, size_gb, status, retention_days, location',
                'project_id, project_name, description, start_date, end_date, budget, actual_cost, status, manager, team_size',
                'user_id, username, full_name, email, department, role, access_level, last_login, status, created_date'
            ],
            'Data Types': [
                'Text, Text, Text, Text, Text, Text, Number, Number, Number, Text, Date',
                'Text, Text, Text, Text, Text, Text, Text, Text, Date',
                'Text, Text, Text, Text, Text, Text, Text, Text, Date',
                'Text, Text, Text, Text, Text, Text, Date, Text, Text, Date, Number',
                'Text, Text, Text, Text, Text, Text, Date, Text, Text, Date, Number',
                'Text, Text, Text, Text, Text, Date, Date, Text, Text, Text, Number',
                'Text, Text, Text, Text, Text, Date, Text, Text, Boolean',
                'Text, Text, Text, Date, Date, Number, Text, Number, Text',
                'Text, Text, Text, Date, Date, Number, Number, Text, Text, Number',
                'Text, Text, Text, Text, Text, Text, Text, Date, Text, Date'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Format the instructions sheet
        worksheet = writer.sheets['Instructions']
        for i, col in enumerate(instructions_df.columns):
            worksheet.set_column(i, i, len(col) + 5)
    
    output.seek(0)
    return output

def export_data_to_excel():
    """Export current data to Excel file"""
    if 'servers_data' not in st.session_state or st.session_state.servers_data.empty:
        st.error("No data available to export. Please upload data first.")
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each dataset to a separate sheet
        st.session_state.servers_data.to_excel(writer, sheet_name='Servers', index=False)
        st.session_state.network_devices_data.to_excel(writer, sheet_name='Network_Devices', index=False)
        st.session_state.applications_data.to_excel(writer, sheet_name='Applications', index=False)
        st.session_state.incidents_data.to_excel(writer, sheet_name='Incidents', index=False)
        st.session_state.tickets_data.to_excel(writer, sheet_name='Tickets', index=False)
        st.session_state.assets_data.to_excel(writer, sheet_name='Assets', index=False)
        st.session_state.security_events_data.to_excel(writer, sheet_name='Security_Events', index=False)
        st.session_state.backups_data.to_excel(writer, sheet_name='Backups', index=False)
        st.session_state.projects_data.to_excel(writer, sheet_name='Projects', index=False)
        st.session_state.users_data.to_excel(writer, sheet_name='Users', index=False)
    
    output.seek(0)
    return output

def create_basic_sample_data():
    """Create basic sample data for IT analytics testing"""
    # Sample servers data
    servers_data = pd.DataFrame({
        'server_id': [f'SVR{i:03d}' for i in range(1, 16)],
        'server_name': [f'Server-{i}' for i in range(1, 16)],
        'server_type': ['Production', 'Development', 'Testing', 'Production', 'Development'] * 3,
        'location': ['Data Center A', 'Data Center B', 'Office A', 'Data Center A', 'Office B'] * 3,
        'ip_address': [f'192.168.1.{i}' for i in range(10, 25)],
        'os_version': ['Windows Server 2019', 'Ubuntu 20.04', 'CentOS 8', 'Windows Server 2022', 'Ubuntu 22.04'] * 3,
        'cpu_cores': [8, 16, 4, 32, 8, 16, 4, 32, 8, 16, 4, 32, 8, 16, 4],
        'ram_gb': [32, 64, 16, 128, 32, 64, 16, 128, 32, 64, 16, 128, 32, 64, 16],
        'storage_tb': [2, 4, 1, 8, 2, 4, 1, 8, 2, 4, 1, 8, 2, 4, 1],
        'status': ['Online', 'Online', 'Offline', 'Online', 'Online', 'Online', 'Offline', 'Online', 'Online', 'Online', 'Offline', 'Online', 'Online', 'Online', 'Offline'],
        'last_maintenance': pd.date_range(start='2024-01-01', periods=15, freq='D'),
        'uptime_percentage': np.random.uniform(95.0, 99.9, 15),
        'cpu_utilization': np.random.uniform(10.0, 90.0, 15),
        'memory_utilization': np.random.uniform(20.0, 85.0, 15),
        'next_maintenance': pd.date_range(start='2024-06-01', periods=15, freq='D')
    })
    
    # Sample network devices data
    network_devices_data = pd.DataFrame({
        'device_id': [f'NET{i:03d}' for i in range(1, 21)],
        'device_name': [f'Switch-{i}' for i in range(1, 21)],
        'device_type': ['Switch', 'Router', 'Firewall', 'Switch', 'Router'] * 4,
        'location': ['Data Center A', 'Data Center B', 'Office A', 'Office B', 'Remote Site'] * 4,
        'ip_address': [f'10.0.{i}.{j}' for i in range(1, 5) for j in range(1, 6)],
        'model': ['Cisco Catalyst', 'Juniper Router', 'Fortinet Firewall', 'HP Switch', 'Mikrotik Router'] * 4,
        'firmware_version': ['15.2', '20.4', '6.4', '16.2', '6.48'] * 4,
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 4,
        'last_backup': pd.date_range(start='2024-01-01', periods=20, freq='D'),
        'latency_ms': np.random.uniform(1.0, 50.0, 20),
        'packet_loss_percentage': np.random.uniform(0.0, 2.0, 20),
        'uptime_percentage': np.random.uniform(98.0, 99.9, 20)
    })
    
    # Sample applications data
    applications_data = pd.DataFrame({
        'app_id': [f'APP{i:03d}' for i in range(1, 26)],
        'app_name': [f'Application-{i}' for i in range(1, 26)],
        'app_type': ['Web App', 'Database', 'API', 'Web App', 'Database'] * 5,
        'version': ['2.1.0', '1.5.2', '3.0.1', '2.1.0', '1.5.2'] * 5,
        'server_id': [f'SVR{i:03d}' for i in range(1, 26)],
        'department': ['IT', 'Finance', 'HR', 'Sales', 'Marketing'] * 5,
        'critical_level': ['High', 'Medium', 'Low', 'High', 'Medium'] * 5,
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 5,
        'last_update': pd.date_range(start='2024-01-01', periods=25, freq='D')
    })
    
    # Sample incidents data
    incidents_data = pd.DataFrame({
        'incident_id': [f'INC{i:03d}' for i in range(1, 51)],
        'title': [f'Incident {i}' for i in range(1, 51)],
        'description': [f'Description for incident {i}' for i in range(1, 51)],
        'priority': ['High', 'Medium', 'Low', 'High', 'Medium'] * 10,
        'category': ['Hardware', 'Software', 'Network', 'Security', 'User Error'] * 10,
        'reported_by': [f'User{i}' for i in range(1, 51)],
        'reported_date': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'assigned_to': [f'Tech{i}' for i in range(1, 51)],
        'status': ['Resolved', 'In Progress', 'Open', 'Resolved', 'In Progress'] * 10,
        'resolution_date': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'resolution_time_minutes': np.random.randint(30, 480, 50)
    })
    
    # Sample tickets data
    tickets_data = pd.DataFrame({
        'ticket_id': [f'TKT{i:03d}' for i in range(1, 101)],
        'title': [f'Support Ticket {i}' for i in range(1, 101)],
        'description': [f'Description for ticket {i}' for i in range(1, 101)],
        'priority': ['High', 'Medium', 'Low', 'High', 'Medium'] * 20,
        'category': ['Hardware', 'Software', 'Network', 'Access', 'Training'] * 20,
        'submitted_by': [f'User{i}' for i in range(1, 101)],
        'submitted_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'assigned_to': [f'Tech{i}' for i in range(1, 101)],
        'status': ['Resolved', 'In Progress', 'Open', 'Resolved', 'In Progress'] * 20,
        'resolution_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'satisfaction_score': np.random.randint(1, 6, 100)
    })
    
    # Sample assets data
    assets_data = pd.DataFrame({
        'asset_id': [f'AST{i:03d}' for i in range(1, 31)],
        'asset_name': [f'Asset-{i}' for i in range(1, 31)],
        'asset_type': ['Laptop', 'Desktop', 'Monitor', 'Laptop', 'Desktop'] * 6,
        'model': [f'Model-{i}' for i in range(1, 31)],
        'serial_number': [f'SN{i:06d}' for i in range(1, 31)],
        'purchase_date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'warranty_expiry': pd.date_range(start='2025-01-01', periods=30, freq='D'),
        'location': ['Office A', 'Office B', 'Office A', 'Office B', 'Office A'] * 6,
        'assigned_to': [f'User{i}' for i in range(1, 31)],
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 6,
        'purchase_cost': np.random.randint(500, 5000, 30)
    })
    
    # Sample security events data
    security_events_data = pd.DataFrame({
        'event_id': [f'SEC{i:03d}' for i in range(1, 41)],
        'event_type': ['Login Attempt', 'File Access', 'Network Scan', 'Login Attempt', 'File Access'] * 8,
        'severity': ['Low', 'Medium', 'High', 'Low', 'Medium'] * 8,
        'source_ip': [f'192.168.{i}.{j}' for i in range(1, 5) for j in range(1, 11)],
        'target_ip': [f'10.0.{i}.{j}' for i in range(1, 5) for j in range(1, 11)],
        'timestamp': pd.date_range(start='2024-01-01', periods=40, freq='H'),
        'description': [f'Security event {i} description' for i in range(1, 41)],
        'status': ['Investigated', 'Open', 'Closed', 'Investigated', 'Open'] * 8,
        'investigation_required': [True, False, True, False, True] * 8
    })
    
    # Sample backups data
    backups_data = pd.DataFrame({
        'backup_id': [f'BAK{i:03d}' for i in range(1, 21)],
        'system_name': [f'System-{i}' for i in range(1, 21)],
        'backup_type': ['Full', 'Incremental', 'Full', 'Incremental', 'Full'] * 4,
        'start_time': pd.date_range(start='2024-01-01', periods=20, freq='D'),
        'end_time': pd.date_range(start='2024-01-01', periods=20, freq='D') + pd.Timedelta(hours=2),
        'size_gb': np.random.randint(10, 500, 20),
        'status': ['Success', 'Success', 'Success', 'Success', 'Success'] * 4,
        'retention_days': [30, 7, 30, 7, 30] * 4,
        'location': ['Local', 'Cloud', 'Local', 'Cloud', 'Local'] * 4
    })
    
    # Sample projects data
    projects_data = pd.DataFrame({
        'project_id': [f'PRJ{i:03d}' for i in range(1, 16)],
        'project_name': [f'Project-{i}' for i in range(1, 16)],
        'description': [f'Description for project {i}' for i in range(1, 16)],
        'start_date': pd.date_range(start='2024-01-01', periods=15, freq='D'),
        'end_date': pd.date_range(start='2024-06-01', periods=15, freq='D'),
        'budget': np.random.randint(10000, 100000, 15),
        'actual_cost': np.random.randint(8000, 120000, 15),
        'status': ['In Progress', 'Completed', 'Planning', 'In Progress', 'Completed'] * 3,
        'manager': [f'Manager{i}' for i in range(1, 16)],
        'team_size': np.random.randint(3, 15, 15)
    })
    
    # Sample users data
    users_data = pd.DataFrame({
        'user_id': [f'USR{i:03d}' for i in range(1, 51)],
        'username': [f'user{i}' for i in range(1, 51)],
        'full_name': [f'User {i}' for i in range(1, 51)],
        'email': [f'user{i}@company.com' for i in range(1, 51)],
        'department': ['IT', 'Finance', 'HR', 'Sales', 'Marketing'] * 10,
        'role': ['Developer', 'Analyst', 'Manager', 'Developer', 'Analyst'] * 10,
        'access_level': ['Admin', 'User', 'Manager', 'Admin', 'User'] * 10,
        'last_login': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 10,
        'created_date': pd.date_range(start='2023-01-01', periods=50, freq='D')
    })
    
    return {
        'Servers': servers_data,
        'Network_Devices': network_devices_data,
        'Applications': applications_data,
        'Incidents': incidents_data,
        'Tickets': tickets_data,
        'Assets': assets_data,
        'Security_Events': security_events_data,
        'Backups': backups_data,
        'Projects': projects_data,
        'Users': users_data
    }

def create_security_sample_data():
    """Create security-focused sample data for IT analytics testing"""
    # Enhanced security events with more realistic data
    security_events_data = pd.DataFrame({
        'event_id': [f'SEC{i:03d}' for i in range(1, 51)],
        'event_type': ['Failed Login', 'Suspicious Activity', 'Data Access', 'Network Intrusion', 'Malware Detection'] * 10,
        'severity': ['High', 'Medium', 'Low', 'High', 'Medium'] * 10,
        'source_ip': [f'192.168.{i}.{j}' for i in range(1, 6) for j in range(1, 11)],
        'target_ip': [f'10.0.{i}.{j}' for i in range(1, 6) for j in range(1, 11)],
        'timestamp': pd.date_range(start='2024-01-01', periods=50, freq='H'),
        'description': [f'Enhanced security event {i} with detailed threat analysis' for i in range(1, 51)],
        'status': ['Investigated', 'Open', 'Closed', 'Escalated', 'Resolved'] * 10,
        'investigation_required': [True, True, False, True, True] * 10
    })
    
    # Enhanced incidents with security focus
    incidents_data = pd.DataFrame({
        'incident_id': [f'INC{i:03d}' for i in range(1, 61)],
        'title': [f'Security Incident {i}' for i in range(1, 61)],
        'description': [f'Detailed security incident description {i} with threat indicators' for i in range(1, 61)],
        'priority': ['Critical', 'High', 'Medium', 'Critical', 'High'] * 12,
        'category': ['Security Breach', 'Data Leak', 'Malware', 'Unauthorized Access', 'Network Attack'] * 12,
        'reported_by': [f'Security{i}' for i in range(1, 61)],
        'reported_date': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'assigned_to': [f'SecTech{i}' for i in range(1, 61)],
        'status': ['Resolved', 'In Progress', 'Open', 'Escalated', 'Resolved'] * 12,
        'resolution_date': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'resolution_time_minutes': np.random.randint(60, 1440, 60)
    })
    
    # Enhanced backups with security considerations
    backups_data = pd.DataFrame({
        'backup_id': [f'BAK{i:03d}' for i in range(1, 31)],
        'system_name': [f'Secure-System-{i}' for i in range(1, 31)],
        'backup_type': ['Encrypted Full', 'Incremental', 'Encrypted Full', 'Incremental', 'Encrypted Full'] * 6,
        'start_time': pd.date_range(start='2024-01-01', periods=30, freq='D'),
        'end_time': pd.date_range(start='2024-01-01', periods=30, freq='D') + pd.Timedelta(hours=3),
        'size_gb': np.random.randint(50, 1000, 30),
        'status': ['Success', 'Success', 'Success', 'Success', 'Success'] * 6,
        'retention_days': [90, 30, 90, 30, 90] * 6,
        'location': ['Secure Local', 'Encrypted Cloud', 'Secure Local', 'Encrypted Cloud', 'Secure Local'] * 6
    })
    
    # Enhanced users with security roles
    users_data = pd.DataFrame({
        'user_id': [f'USR{i:03d}' for i in range(1, 61)],
        'username': [f'secuser{i}' for i in range(1, 61)],
        'full_name': [f'Security User {i}' for i in range(1, 61)],
        'email': [f'secuser{i}@company.com' for i in range(1, 61)],
        'department': ['Security', 'IT', 'Security', 'IT', 'Security'] * 12,
        'role': ['Security Analyst', 'Security Engineer', 'Security Manager', 'Security Analyst', 'Security Engineer'] * 12,
        'access_level': ['Admin', 'User', 'Manager', 'Admin', 'User'] * 12,
        'last_login': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 12,
        'created_date': pd.date_range(start='2023-01-01', periods=60, freq='D')
    })
    
    return {
        'Security_Events': security_events_data,
        'Incidents': incidents_data,
        'Backups': backups_data,
        'Users': users_data
    }

def create_performance_sample_data():
    """Create performance-focused sample data for IT analytics testing"""
    # Enhanced servers with performance metrics
    servers_data = pd.DataFrame({
        'server_id': [f'SVR{i:03d}' for i in range(1, 21)],
        'server_name': [f'Perf-Server-{i}' for i in range(1, 21)],
        'server_type': ['High-Performance', 'Production', 'Development', 'High-Performance', 'Production'] * 4,
        'location': ['Data Center A', 'Data Center B', 'Office A', 'Data Center A', 'Office B'] * 4,
        'ip_address': [f'192.168.2.{i}' for i in range(10, 30)],
        'os_version': ['Windows Server 2022', 'Ubuntu 22.04', 'CentOS 9', 'Windows Server 2022', 'Ubuntu 22.04'] * 4,
        'cpu_cores': [32, 64, 16, 128, 32, 64, 16, 128, 32, 64, 16, 128, 32, 64, 16, 128, 32, 64, 16, 128],
        'ram_gb': [128, 256, 64, 512, 128, 256, 64, 512, 128, 256, 64, 512, 128, 256, 64, 512, 128, 256, 64, 512],
        'storage_tb': [8, 16, 4, 32, 8, 16, 4, 32, 8, 16, 4, 32, 8, 16, 4, 32, 8, 16, 4, 32],
        'status': ['Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online', 'Online'],
        'last_maintenance': pd.date_range(start='2024-01-01', periods=20, freq='D')
    })
    
    # Enhanced applications with performance metrics
    applications_data = pd.DataFrame({
        'app_id': [f'APP{i:03d}' for i in range(1, 31)],
        'app_name': [f'Perf-App-{i}' for i in range(1, 31)],
        'app_type': ['High-Performance Web', 'Database', 'API', 'High-Performance Web', 'Database'] * 6,
        'version': ['3.1.0', '2.5.2', '4.0.1', '3.1.0', '2.5.2'] * 6,
        'server_id': [f'SVR{i:03d}' for i in range(1, 31)],
        'department': ['IT', 'Finance', 'HR', 'Sales', 'Marketing'] * 6,
        'critical_level': ['Critical', 'High', 'Medium', 'Critical', 'High'] * 6,
        'status': ['Active', 'Active', 'Active', 'Active', 'Active'] * 6,
        'last_update': pd.date_range(start='2024-01-01', periods=30, freq='D')
    })
    
    # Enhanced tickets with performance metrics
    tickets_data = pd.DataFrame({
        'ticket_id': [f'TKT{i:03d}' for i in range(1, 121)],
        'title': [f'Performance Ticket {i}' for i in range(1, 121)],
        'description': [f'Performance optimization request {i} with detailed requirements' for i in range(1, 121)],
        'priority': ['Critical', 'High', 'Medium', 'Critical', 'High'] * 24,
        'category': ['Performance', 'Optimization', 'Scalability', 'Performance', 'Optimization'] * 24,
        'submitted_by': [f'PerfUser{i}' for i in range(1, 121)],
        'submitted_date': pd.date_range(start='2024-01-01', periods=120, freq='D'),
        'assigned_to': [f'PerfTech{i}' for i in range(1, 121)],
        'status': ['Resolved', 'In Progress', 'Open', 'Resolved', 'In Progress'] * 24,
        'resolution_date': pd.date_range(start='2024-01-01', periods=120, freq='D'),
        'satisfaction_score': np.random.randint(4, 6, 120)
    })
    
    # Enhanced projects with performance focus
    projects_data = pd.DataFrame({
        'project_id': [f'PRJ{i:03d}' for i in range(1, 21)],
        'project_name': [f'Performance Project {i}' for i in range(1, 21)],
        'description': [f'Performance optimization project {i} with scalability goals' for i in range(1, 21)],
        'start_date': pd.date_range(start='2024-01-01', periods=20, freq='D'),
        'end_date': pd.date_range(start='2024-06-01', periods=20, freq='D'),
        'budget': np.random.randint(50000, 200000, 20),
        'actual_cost': np.random.randint(40000, 250000, 20),
        'status': ['In Progress', 'Completed', 'Planning', 'In Progress', 'Completed'] * 4,
        'manager': [f'PerfManager{i}' for i in range(1, 21)],
        'team_size': np.random.randint(5, 20, 20)
    })
    
    return {
        'Servers': servers_data,
        'Applications': applications_data,
        'Tickets': tickets_data,
        'Projects': projects_data
    }

def create_comprehensive_sample_data():
    """Create comprehensive sample data for IT analytics testing with enhanced datasets"""
    
    def cycle(values, desired_length):
        """Repeat values to exactly desired_length elements."""
        base = list(values)
        return [base[i % len(base)] for i in range(desired_length)]

    # Enhanced servers with more realistic metrics
    servers_data = pd.DataFrame({
        'server_id': [f'SVR{i:03d}' for i in range(1, 51)],
        'server_name': [f'Server-{i}' for i in range(1, 51)],
        'server_type': ['Production', 'Development', 'Testing', 'Staging', 'Backup'] * 10,
        'location': ['Data Center A', 'Data Center B', 'Office A', 'Office B', 'Cloud AWS'] * 10,
        'ip_address': [f'192.168.{i//10}.{i%10+1}' for i in range(1, 51)],
        'os_version': ['Windows Server 2022', 'Ubuntu 22.04', 'CentOS 9', 'Windows Server 2019', 'Ubuntu 20.04'] * 10,
        'cpu_cores': np.random.randint(4, 128, 50),
        'ram_gb': np.random.randint(8, 512, 50),
        'storage_tb': np.random.randint(1, 32, 50),
        'status': ['Online', 'Online', 'Online', 'Maintenance', 'Offline'] * 10,
        'uptime_percentage': np.random.uniform(95.0, 99.9, 50),
        'cpu_utilization': np.random.uniform(10.0, 90.0, 50),
        'memory_utilization': np.random.uniform(20.0, 85.0, 50),
        'disk_utilization': np.random.uniform(15.0, 80.0, 50),
        'last_maintenance': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'next_maintenance': pd.date_range(start='2024-06-01', periods=50, freq='D'),
        'power_consumption_watts': np.random.randint(200, 800, 50),
        'temperature_celsius': np.random.uniform(18.0, 35.0, 50),
        'network_bandwidth_mbps': np.random.randint(100, 10000, 50)
    })
    
    # Enhanced network devices with performance metrics
    network_devices_data = pd.DataFrame({
        'device_id': [f'NET{i:03d}' for i in range(1, 41)],
        'device_name': [f'Device-{i}' for i in range(1, 41)],
        'device_type': ['Switch', 'Router', 'Firewall', 'Load Balancer', 'Wireless AP'] * 8,
        'location': ['Data Center A', 'Data Center B', 'Office A', 'Office B', 'Remote Site'] * 8,
        'ip_address': [f'10.0.{i//10}.{i%10+1}' for i in range(1, 41)],
        'model': ['Cisco Catalyst', 'Juniper Router', 'Fortinet Firewall', 'F5 BIG-IP', 'Aruba AP'] * 8,
        'firmware_version': [f'{random.randint(15, 20)}.{random.randint(0, 9)}.{random.randint(0, 9)}' for _ in range(40)],
        'status': ['Active', 'Active', 'Active', 'Backup', 'Maintenance'] * 8,
        'last_backup': pd.date_range(start='2024-01-01', periods=40, freq='D'),
        'latency_ms': np.random.uniform(1.0, 50.0, 40),
        'packet_loss_percentage': np.random.uniform(0.0, 2.0, 40),
        'throughput_mbps': np.random.randint(100, 10000, 40),
        'error_rate_percentage': np.random.uniform(0.0, 1.0, 40),
        'uptime_percentage': np.random.uniform(98.0, 99.9, 40),
        'temperature_celsius': np.random.uniform(20.0, 40.0, 40),
        'fan_speed_rpm': np.random.randint(2000, 8000, 40)
    })
    
    # Enhanced applications with detailed metrics
    applications_data = pd.DataFrame({
        'app_id': [f'APP{i:03d}' for i in range(1, 61)],
        'app_name': [f'Application-{i}' for i in range(1, 61)],
        'app_type': ['Web App', 'Database', 'API', 'Mobile App', 'Desktop App'] * 12,
        'version': [f'{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}' for _ in range(60)],
        'server_id': [f'SVR{random.randint(1, 50):03d}' for _ in range(60)],
        'department': ['IT', 'Finance', 'HR', 'Sales', 'Marketing', 'Operations'] * 10,
        'critical_level': ['Critical', 'High', 'Medium', 'Low'] * 15,
        'status': ['Active', 'Active', 'Active', 'Development', 'Testing'] * 12,
        'last_update': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'response_time_ms': np.random.uniform(50.0, 2000.0, 60),
        'availability_percentage': np.random.uniform(95.0, 99.9, 60),
        'user_count': np.random.randint(10, 1000, 60),
        'data_size_gb': np.random.uniform(0.1, 100.0, 60),
        'last_backup': pd.date_range(start='2024-01-01', periods=60, freq='D'),
        'security_score': np.random.randint(70, 100, 60),
        'performance_score': np.random.randint(60, 100, 60),
        'compliance_status': ['Compliant', 'Compliant', 'Compliant', 'Under Review', 'Non-Compliant'] * 12
    })
    
    # Enhanced incidents with detailed tracking
    incidents_data = pd.DataFrame({
        'incident_id': [f'INC{i:03d}' for i in range(1, 101)],
        'title': [f'Incident {i}' for i in range(1, 101)],
        'description': [f'Detailed description for incident {i} with technical details' for i in range(1, 101)],
        'priority': cycle(['Critical', 'High', 'Medium', 'Low'], 100),
        'category': cycle(['Hardware', 'Software', 'Network', 'Security', 'Performance', 'User Error'], 100),
        'reported_by': [f'User{i}' for i in range(1, 101)],
        'reported_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'assigned_to': [f'Tech{i}' for i in range(1, 101)],
        'status': cycle(['Resolved', 'In Progress', 'Open', 'Escalated', 'Closed'], 100),
        'resolution_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'resolution_time_minutes': np.random.randint(30, 1440, 100),
        'impact_level': cycle(['High', 'Medium', 'Low'], 100),
        'affected_users': np.random.randint(1, 500, 100),
        'business_impact': cycle(['Revenue Loss', 'Productivity Loss', 'Data Loss', 'Reputation Damage', 'Compliance Risk'], 100),
        'root_cause': cycle(['Hardware Failure', 'Software Bug', 'Network Issue', 'Human Error', 'External Attack'], 100),
        'prevention_measures': cycle(['Hardware Upgrade', 'Software Patch', 'Network Redundancy', 'Training', 'Security Enhancement'], 100)
    })
    
    # Enhanced tickets with SLA tracking
    tickets_data = pd.DataFrame({
        'ticket_id': [f'TKT{i:03d}' for i in range(1, 201)],
        'title': [f'Support Ticket {i}' for i in range(1, 201)],
        'description': [f'Detailed description for ticket {i} with user requirements' for i in range(1, 201)],
        'priority': cycle(['Critical', 'High', 'Medium', 'Low'], 200),
        'category': cycle(['Hardware', 'Software', 'Network', 'Access', 'Training', 'Account Management'], 200),
        'submitted_by': [f'User{i}' for i in range(1, 201)],
        'submitted_date': pd.date_range(start='2024-01-01', periods=200, freq='D'),
        'assigned_to': [f'Tech{i}' for i in range(1, 201)],
        'status': cycle(['Resolved', 'In Progress', 'Open', 'Escalated', 'Closed'], 200),
        'resolution_date': pd.date_range(start='2024-01-01', periods=200, freq='D'),
        'satisfaction_score': np.random.randint(1, 6, 200),
        'sla_target_hours': np.random.randint(2, 48, 200),
        'actual_resolution_hours': np.random.randint(1, 72, 200),
        'sla_met': np.random.choice([True, False], 200, p=[0.85, 0.15]),
        'escalation_count': np.random.randint(0, 3, 200),
        'customer_priority': cycle(['VIP', 'Regular', 'VIP', 'Regular', 'VIP'], 200),
        'resolution_quality': np.random.randint(1, 6, 200),
        'knowledge_article_created': np.random.choice([True, False], 200, p=[0.3, 0.7])
    })
    
    # Enhanced assets with lifecycle tracking
    assets_data = pd.DataFrame({
        'asset_id': [f'AST{i:03d}' for i in range(1, 101)],
        'asset_name': [f'Asset-{i}' for i in range(1, 101)],
        'asset_type': cycle(['Laptop', 'Desktop', 'Monitor', 'Printer', 'Tablet', 'Phone', 'Server', 'Network Device'], 100),
        'model': [f'Model-{i}' for i in range(1, 101)],
        'serial_number': [f'SN{i:06d}' for i in range(1, 101)],
        'purchase_date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'warranty_expiry': pd.date_range(start='2025-01-01', periods=100, freq='D'),
        'location': ['Office A', 'Office B', 'Home Office', 'Data Center', 'Remote Site'] * 20,
        'assigned_to': [f'User{i}' for i in range(1, 101)],
        'status': cycle(['Active', 'Active', 'Active', 'Maintenance', 'Retired', 'Lost'], 100),
        'purchase_cost': np.random.randint(500, 10000, 100),
        'current_value': np.random.randint(200, 8000, 100),
        'depreciation_rate': np.random.uniform(0.1, 0.3, 100),
        'last_maintenance': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'next_maintenance': pd.date_range(start='2024-06-01', periods=100, freq='D'),
        'lifecycle_stage': ['Deployment', 'Active', 'Maintenance', 'End of Life', 'Replacement'] * 20,
        'vendor': cycle(['Dell', 'HP', 'Lenovo', 'Cisco', 'Apple', 'Samsung'], 100),
        'support_contract': cycle(['Active', 'Active', 'Expired', 'Active', 'Active', 'Expired'], 100)
    })
    
    # Enhanced security events with threat intelligence
    security_events_data = pd.DataFrame({
        'event_id': [f'SEC{i:03d}' for i in range(1, 101)],
        'event_type': cycle(['Failed Login', 'Suspicious Activity', 'Data Access', 'Network Intrusion', 'Malware Detection', 'Privilege Escalation'], 100),
        'severity': ['Critical', 'High', 'Medium', 'Low'] * 25,
        'source_ip': [f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}' for _ in range(100)],
        'target_ip': [f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}' for _ in range(100)],
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
        'description': [f'Detailed security event {i} with threat indicators and analysis' for i in range(1, 101)],
        'status': cycle(['Investigated', 'Open', 'Closed', 'Escalated', 'Resolved'], 100),
        'investigation_required': np.random.choice([True, False], 100, p=[0.7, 0.3]),
        'threat_level': ['Low', 'Medium', 'High', 'Critical'] * 25,
        'affected_systems': np.random.randint(1, 20, 100),
        'data_compromised': np.random.choice([True, False], 100, p=[0.2, 0.8]),
        'response_time_minutes': np.random.randint(5, 120, 100),
        'mitigation_applied': ['Firewall Rule', 'Access Revoked', 'System Isolated', 'Patch Applied', 'User Notified'] * 20,
        'false_positive': np.random.choice([True, False], 100, p=[0.1, 0.9]),
        'compliance_impact': cycle(['GDPR', 'HIPAA', 'SOX', 'PCI-DSS', 'None'], 100)
    })
    
    # Enhanced backups with detailed metrics
    backups_data = pd.DataFrame({
        'backup_id': [f'BAK{i:03d}' for i in range(1, 51)],
        'system_name': [f'System-{i}' for i in range(1, 51)],
        'backup_type': ['Full', 'Incremental', 'Differential', 'Snapshot', 'Archive'] * 10,
        'start_time': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'end_time': pd.date_range(start='2024-01-01', periods=50, freq='D') + pd.Timedelta(hours=2),
        'size_gb': np.random.randint(10, 1000, 50),
        'status': cycle(['Success', 'Success', 'Success', 'Partial Success', 'Failed'], 50),
        'retention_days': cycle([30, 7, 30, 7, 90, 365], 50),
        'location': cycle(['Local', 'Cloud', 'Offsite', 'Hybrid'], 50),
        'compression_ratio': np.random.uniform(1.5, 4.0, 50),
        'encryption_enabled': np.random.choice([True, False], 50, p=[0.9, 0.1]),
        'verification_status': cycle(['Verified', 'Verified', 'Verified', 'Failed', 'Pending'], 50),
        'recovery_time_minutes': np.random.randint(5, 120, 50),
        'backup_window_hours': np.random.randint(1, 8, 50),
        'data_integrity_score': np.random.randint(90, 100, 50),
        'cost_per_gb': np.random.uniform(0.01, 0.10, 50)
    })
    
    # Enhanced projects with detailed tracking
    projects_data = pd.DataFrame({
        'project_id': [f'PRJ{i:03d}' for i in range(1, 31)],
        'project_name': [f'Project-{i}' for i in range(1, 31)],
        'description': [f'Detailed description for project {i} with objectives and deliverables' for i in range(1, 31)],
        'start_date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
        'end_date': pd.date_range(start='2024-06-01', periods=30, freq='D'),
        'budget': np.random.randint(10000, 500000, 30),
        'actual_cost': np.random.randint(8000, 600000, 30),
        'status': ['In Progress', 'Completed', 'Planning', 'On Hold', 'Cancelled'] * 6,
        'manager': [f'Manager{i}' for i in range(1, 31)],
        'team_size': np.random.randint(3, 25, 30),
        'progress_percentage': np.random.randint(0, 100, 30),
        'risk_level': ['Low', 'Medium', 'High'] * 10,
        'priority': ['High', 'Medium', 'Low'] * 10,
        'stakeholders': np.random.randint(3, 15, 30),
        'milestones_completed': np.random.randint(0, 10, 30),
        'total_milestones': np.random.randint(5, 15, 30),
        'quality_score': np.random.randint(60, 100, 30),
        'customer_satisfaction': np.random.randint(1, 6, 30),
        'lessons_learned_documented': np.random.choice([True, False], 30, p=[0.8, 0.2])
    })
    
    # Enhanced users with detailed profiles
    users_data = pd.DataFrame({
        'user_id': [f'USR{i:03d}' for i in range(1, 101)],
        'username': [f'user{i}' for i in range(1, 101)],
        'full_name': [f'User {i}' for i in range(1, 101)],
        'email': [f'user{i}@company.com' for i in range(1, 101)],
        'department': cycle(['IT', 'Finance', 'HR', 'Sales', 'Marketing', 'Operations', 'Engineering', 'Support'], 100),
        'role': cycle(['Developer', 'Analyst', 'Manager', 'Director', 'Specialist', 'Coordinator'], 100),
        'access_level': cycle(['Admin', 'User', 'Manager', 'Power User', 'Read Only'], 100),
        'last_login': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'status': cycle(['Active', 'Active', 'Active', 'Inactive', 'Suspended'], 100),
        'created_date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'last_password_change': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'failed_login_attempts': np.random.randint(0, 5, 100),
        'account_locked': np.random.choice([True, False], 100, p=[0.05, 0.95]),
        'mfa_enabled': np.random.choice([True, False], 100, p=[0.8, 0.2]),
        'session_timeout_minutes': np.random.randint(30, 480, 100),
        'data_access_level': cycle(['Public', 'Internal', 'Confidential', 'Restricted'], 100),
        'training_completed': np.random.choice([True, False], 100, p=[0.9, 0.1]),
        'compliance_status': cycle(['Compliant', 'Compliant', 'Compliant', 'Under Review', 'Non-Compliant'], 100)
    })
    
    # Enhanced cost data
    cost_data = pd.DataFrame({
        'cost_id': [f'COST{i:03d}' for i in range(1, 51)],
        'category': cycle(['Hardware', 'Software', 'Cloud Services', 'Maintenance', 'Personnel', 'Training', 'Licensing', 'Infrastructure'], 50),
        'subcategory': cycle(['Servers', 'Network Equipment', 'Security Tools', 'Backup Services', 'Support Contracts'], 50),
        'amount': np.random.randint(1000, 100000, 50),
        'date': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'department': cycle(['IT', 'IT', 'IT', 'IT', 'IT'], 50),
        'vendor': cycle(['Dell', 'Microsoft', 'AWS', 'Cisco', 'Oracle'], 50),
        'payment_terms': cycle(['Net 30', 'Net 30', 'Net 30', 'Net 30', 'Net 30'], 50),
        'recurring': np.random.choice([True, False], 50, p=[0.6, 0.4]),
        'budgeted': np.random.choice([True, False], 50, p=[0.8, 0.2]),
        'approval_status': cycle(['Approved', 'Approved', 'Approved', 'Pending', 'Rejected'], 50)
    })
    
    # Enhanced performance metrics
    performance_data = pd.DataFrame({
        'metric_id': [f'PERF{i:03d}' for i in range(1, 51)],
        'metric_name': ['CPU Utilization', 'Memory Usage', 'Disk I/O', 'Network Throughput', 'Response Time'] * 10,
        'system_id': [f'SYS{random.randint(1, 50):03d}' for _ in range(50)],
        'value': np.random.uniform(10.0, 95.0, 50),
        'unit': ['%', '%', 'MB/s', 'Mbps', 'ms'] * 10,
        'timestamp': pd.date_range(start='2024-01-01', periods=50, freq='H'),
        'threshold': np.random.uniform(70.0, 90.0, 50),
        'status': ['Normal', 'Normal', 'Warning', 'Critical', 'Normal'] * 10,
        'trend': ['Stable', 'Increasing', 'Decreasing', 'Stable', 'Stable'] * 10,
        'alert_sent': np.random.choice([True, False], 50, p=[0.2, 0.8])
    })
    
    return {
        'Servers': servers_data,
        'Network_Devices': network_devices_data,
        'Applications': applications_data,
        'Incidents': incidents_data,
        'Tickets': tickets_data,
        'Assets': assets_data,
        'Security_Events': security_events_data,
        'Backups': backups_data,
        'Projects': projects_data,
        'Users': users_data,
        'Cost_Data': cost_data,
        'Performance_Metrics': performance_data
    }

def create_disaster_recovery_sample_data():
    """Create disaster recovery and business continuity focused sample data"""
    
    # Disaster recovery scenarios
    dr_scenarios_data = pd.DataFrame({
        'scenario_id': [f'DR{i:03d}' for i in range(1, 21)],
        'scenario_name': [f'DR Scenario {i}' for i in range(1, 21)],
        'scenario_type': ['Natural Disaster', 'Cyber Attack', 'Hardware Failure', 'Human Error', 'Power Outage'] * 4,
        'severity': ['Critical', 'High', 'Medium', 'Low'] * 5,
        'affected_systems': np.random.randint(5, 50, 20),
        'estimated_downtime_hours': np.random.randint(1, 72, 20),
        'rto_target_hours': np.random.randint(1, 24, 20),
        'rpo_target_hours': np.random.randint(0, 4, 20),
        'last_tested': pd.date_range(start='2023-01-01', periods=20, freq='D'),
        'next_test_date': pd.date_range(start='2024-06-01', periods=20, freq='D'),
        'test_status': ['Passed', 'Passed', 'Passed', 'Failed', 'Not Tested'] * 4,
        'recovery_procedures_documented': np.random.choice([True, False], 20, p=[0.9, 0.1]),
        'team_trained': np.random.choice([True, False], 20, p=[0.8, 0.2])
    })
    
    # Business impact analysis
    business_impact_data = pd.DataFrame({
        'impact_id': [f'IMP{i:03d}' for i in range(1, 31)],
        'system_id': [f'SYS{random.randint(1, 50):03d}' for _ in range(30)],
        'system_name': [f'System-{i}' for i in range(1, 31)],
        'business_criticality': (['Critical', 'High', 'Medium', 'Low'] * 8)[:30],
        'revenue_impact_per_hour': np.random.randint(1000, 100000, 30),
        'productivity_impact_per_hour': np.random.randint(100, 10000, 30),
        'customer_impact': (['High', 'Medium', 'Low'] * 10)[:30],
        'compliance_impact': (['GDPR', 'HIPAA', 'SOX', 'PCI-DSS', 'None'] * 6)[:30],
        'recovery_priority': (['P0', 'P1', 'P2', 'P3'] * 8)[:30],
        'dependencies': np.random.randint(1, 10, 30),
        'last_assessment': pd.date_range(start='2024-01-01', periods=30, freq='D')
    })
    
    # Recovery procedures
    recovery_procedures_data = pd.DataFrame({
        'procedure_id': [f'PROC{i:03d}' for i in range(1, 26)],
        'procedure_name': [f'Recovery Procedure {i}' for i in range(1, 26)],
        'system_id': [f'SYS{random.randint(1, 50):03d}' for _ in range(25)],
        'procedure_type': (['Automated', 'Manual', 'Semi-Automated'] * 9)[:25],
        'estimated_duration_minutes': np.random.randint(5, 120, 25),
        'required_skills': ['System Admin', 'Network Admin', 'Database Admin', 'Security Admin', 'General IT'] * 5,
        'prerequisites': np.random.randint(0, 5, 25),
        'success_rate': np.random.uniform(85.0, 99.9, 25),
        'last_updated': pd.date_range(start='2024-01-01', periods=25, freq='D'),
        'version': [f'{random.randint(1, 5)}.{random.randint(0, 9)}' for _ in range(25)],
        'approved_by': [f'Manager{random.randint(1, 10)}' for _ in range(25)]
    })
    
    # Recovery team
    recovery_team_data = pd.DataFrame({
        'member_id': [f'TEAM{i:03d}' for i in range(1, 21)],
        'member_name': [f'Team Member {i}' for i in range(1, 21)],
        'role': ['Incident Commander', 'Technical Lead', 'Communications Lead', 'Business Liaison', 'Technical Specialist'] * 4,
        'department': ['IT', 'IT', 'IT', 'Business', 'IT'] * 4,
        'contact_number': [f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}' for _ in range(20)],
        'availability': ['24/7', 'Business Hours', '24/7', 'Business Hours', 'On-Call'] * 4,
        'skills': ['Incident Management', 'Technical Recovery', 'Communication', 'Business Analysis', 'System Administration'] * 4,
        'training_completed': np.random.choice([True, False], 20, p=[0.9, 0.1]),
        'last_training': pd.date_range(start='2023-01-01', periods=20, freq='D'),
        'certification': ['ITIL', 'CISSP', 'PMP', 'ITIL', 'CISSP'] * 4
    })
    
    # Recovery testing
    recovery_testing_data = pd.DataFrame({
        'test_id': [f'TEST{i:03d}' for i in range(1, 16)],
        'test_name': [f'Recovery Test {i}' for i in range(1, 16)],
        'test_type': ['Tabletop Exercise', 'Walkthrough', 'Simulation', 'Full Recovery', 'Partial Recovery'] * 3,
        'test_date': pd.date_range(start='2024-01-01', periods=15, freq='D'),
        'duration_hours': np.random.randint(2, 8, 15),
        'participants': np.random.randint(5, 20, 15),
        'scenarios_tested': np.random.randint(1, 5, 15),
        'success_rate': np.random.uniform(70.0, 100.0, 15),
        'issues_found': np.random.randint(0, 10, 15),
        'lessons_learned': np.random.randint(1, 8, 15),
        'next_test_recommendation': pd.date_range(start='2024-06-01', periods=15, freq='D'),
        'test_coordinator': [f'Coordinator{i}' for i in range(1, 16)]
    })
    
    return {
        'DR_Scenarios': dr_scenarios_data,
        'Business_Impact': business_impact_data,
        'Recovery_Procedures': recovery_procedures_data,
        'Recovery_Team': recovery_team_data,
        'Recovery_Testing': recovery_testing_data
    }

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="IT Analytics Dashboard",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🖥️ IT Analytics Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'servers_data' not in st.session_state:
        st.session_state.servers_data = pd.DataFrame()
    if 'network_devices_data' not in st.session_state:
        st.session_state.network_devices_data = pd.DataFrame()
    if 'applications_data' not in st.session_state:
        st.session_state.applications_data = pd.DataFrame()
    if 'incidents_data' not in st.session_state:
        st.session_state.incidents_data = pd.DataFrame()
    if 'tickets_data' not in st.session_state:
        st.session_state.tickets_data = pd.DataFrame()
    if 'assets_data' not in st.session_state:
        st.session_state.assets_data = pd.DataFrame()
    if 'security_events_data' not in st.session_state:
        st.session_state.security_events_data = pd.DataFrame()
    if 'backups_data' not in st.session_state:
        st.session_state.backups_data = pd.DataFrame()
    if 'projects_data' not in st.session_state:
        st.session_state.projects_data = pd.DataFrame()
    if 'users_data' not in st.session_state:
        st.session_state.users_data = pd.DataFrame()
    
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
        
        if st.button("📊 Data Input", key="nav_data_input", use_container_width=True):
            st.session_state.current_page = "📊 Data Input"
        
        if st.button("🖥️ Infrastructure & Systems", key="nav_infrastructure", use_container_width=True):
            st.session_state.current_page = "🖥️ Infrastructure & Systems"
        
        if st.button("🔒 Security & Risk", key="nav_security", use_container_width=True):
            st.session_state.current_page = "🔒 Security & Risk"
        
        if st.button("🛠️ IT Support", key="nav_support", use_container_width=True):
            st.session_state.current_page = "🛠️ IT Support"
        
        if st.button("💻 Asset Management", key="nav_assets", use_container_width=True):
            st.session_state.current_page = "💻 Asset Management"
        
        if st.button("📈 Data Management", key="nav_data_mgmt", use_container_width=True):
            st.session_state.current_page = "📈 Data Management"
        
        if st.button("📋 Project Management", key="nav_projects", use_container_width=True):
            st.session_state.current_page = "📋 Project Management"
        
        if st.button("👥 User Experience", key="nav_ux", use_container_width=True):
            st.session_state.current_page = "👥 User Experience"
        
        if st.button("💰 Cost Optimization", key="nav_cost", use_container_width=True):
            st.session_state.current_page = "💰 Cost Optimization"
        
        if st.button("🚀 Strategy & Innovation", key="nav_strategy", use_container_width=True):
            st.session_state.current_page = "🚀 Strategy & Innovation"
        
        if st.button("🎓 Training & Development", key="nav_training", use_container_width=True):
            st.session_state.current_page = "🎓 Training & Development"
        
        if st.button("🔄 Disaster Recovery", key="nav_disaster", use_container_width=True):
            st.session_state.current_page = "🔄 Disaster Recovery"
        
        if st.button("🔗 Integration", key="nav_integration", use_container_width=True):
            st.session_state.current_page = "🔗 Integration"
        
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
    
    elif page == "📊 Data Input":
        show_data_input()
    
    elif page == "🖥️ Infrastructure & Systems":
        show_infrastructure_systems()
    
    elif page == "🔒 Security & Risk":
        show_security_risk()
    
    elif page == "🛠️ IT Support":
        show_it_support()
    
    elif page == "💻 Asset Management":
        show_asset_management()
    
    elif page == "📈 Data Management":
        show_data_management()
    
    elif page == "📋 Project Management":
        show_project_management()
    
    elif page == "👥 User Experience":
        show_user_experience()
    
    elif page == "💰 Cost Optimization":
        show_cost_optimization()
    
    elif page == "🚀 Strategy & Innovation":
        show_strategy_innovation()
    
    elif page == "🎓 Training & Development":
        show_training_development()
    
    elif page == "🔄 Disaster Recovery":
        show_disaster_recovery()
    
    elif page == "🔗 Integration":
        show_integration()

def show_home():
    # Welcome section with modern styling
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #1e3c72; margin-bottom: 20px; text-align: center;">🎯 Welcome to the IT Analytics Dashboard</h2>
        <p style="color: #4a5568; font-size: 1.1rem; line-height: 1.6; text-align: center;">
            This comprehensive tool helps you calculate and analyze key IT metrics across multiple categories, 
            providing insights to optimize your IT operations and drive strategic decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card-blue">
            <h3 style="margin: 0; font-size: 1.2rem;">🖥️ Infrastructure</h3>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">System Performance & Uptime</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card-purple">
            <h3 style="margin: 0; font-size: 1.2rem;">🔒 Security</h3>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Risk Management & Compliance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card-green">
            <h3 style="margin: 0; font-size: 1.2rem;">🛠️ Support</h3>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Help Desk & User Experience</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card-orange">
            <h3 style="margin: 0; font-size: 1.2rem;">📊 Analytics</h3>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Data Insights & Reporting</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Available metrics categories
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📊 Available Metrics Categories</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a grid layout for categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🖥️ Infrastructure & Systems Performance</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Server Uptime Analysis</li>
                <li>Network Latency and Speed Analysis</li>
                <li>System Load Analysis</li>
                <li>Application Performance Monitoring (APM)</li>
                <li>Incident Response Time Analysis</li>
                <li>System Availability Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🔒 Security & Risk Management</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Vulnerability Analysis</li>
                <li>Firewall Performance Analysis</li>
                <li>Data Breach Incident Analysis</li>
                <li>Access Control Analysis</li>
                <li>Phishing Attack Metrics</li>
                <li>Encryption Effectiveness</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🛠️ IT Support & Help Desk</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Ticket Resolution Rate</li>
                <li>First Call Resolution (FCR)</li>
                <li>Average Ticket Resolution Time</li>
                <li>Ticket Volume Analysis</li>
                <li>User Satisfaction Metrics</li>
                <li>Recurring Issue Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">💻 Asset Management</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>IT Asset Utilization</li>
                <li>Hardware Lifecycle Analysis</li>
                <li>Software Licensing Compliance</li>
                <li>Cloud Resource Utilization</li>
                <li>IT Inventory Turnover</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">📈 Data Management & Analytics</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Data Quality Analysis</li>
                <li>Database Performance Metrics</li>
                <li>Backup Success Rate</li>
                <li>Data Loss Metrics</li>
                <li>Storage Usage Trends</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">📋 Project Management & Development</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Project Delivery Metrics</li>
                <li>Development Cycle Time</li>
                <li>Code Quality Analysis</li>
                <li>Release Management Metrics</li>
                <li>Agile Metrics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">👥 User Experience & Accessibility</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Application Usability Metrics</li>
                <li>Website Performance Analysis</li>
                <li>Accessibility Compliance Analysis</li>
                <li>User Feedback Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">💰 Cost & Resource Optimization</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>IT Budget Utilization</li>
                <li>Cost Per User or Device</li>
                <li>Cloud Cost Analysis</li>
                <li>Energy Efficiency Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🚀 IT Strategy & Innovation</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Technology Adoption Metrics</li>
                <li>ROI on IT Investments</li>
                <li>Emerging Technology Feasibility</li>
                <li>IT Alignment with Business Goals</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🎓 Training & Development</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Employee Training Effectiveness</li>
                <li>IT Certification Metrics</li>
                <li>End-User Training Participation</li>
                <li>Skill Gap Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🔄 Disaster Recovery & Business Continuity</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>Disaster Recovery Readiness</li>
                <li>Recovery Time Objective (RTO) Metrics</li>
                <li>Disaster Recovery Testing Success</li>
                <li>Business Continuity Downtime Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1e3c72; margin: 0 0 15px 0;">🔗 Integration & Interoperability</h4>
            <ul style="color: #4a5568; margin: 0; padding-left: 20px;">
                <li>System Integration Metrics</li>
                <li>Data Flow Efficiency</li>
                <li>API Performance Metrics</li>
                <li>Interoperability Compliance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting started section
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">🚀 Getting Started</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;">
                <h4 style="color: #1e3c72; margin: 0 0 10px 0;">1. 📤 Upload Data</h4>
                <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">Use the Data Input section to upload your IT data</p>
            </div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #2196f3;">
                <h4 style="color: #1e3c72; margin: 0 0 10px 0;">2. 📥 Download Template</h4>
                <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">Get the Excel template with the correct data schema</p>
            </div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #ff9800;">
                <h4 style="color: #1e3c72; margin: 0 0 10px 0;">3. 📊 Analyze Metrics</h4>
                <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">Navigate through the sections to explore different analytics</p>
            </div>
            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #9c27b0;">
                <h4 style="color: #1e3c72; margin: 0 0 10px 0;">4. 📤 Export Results</h4>
                <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">Download your analysis results and reports</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data requirements section
    st.markdown("""
    <div class="welcome-section">
        <h3 style="color: #1e3c72; margin-bottom: 20px;">📋 Data Requirements</h3>
        <p style="color: #4a5568; font-size: 1rem; line-height: 1.6; margin-bottom: 20px;">
            The application requires data in the following categories. Each category has specific required fields 
            that are detailed in the Data Input section.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #1565c0; margin: 0 0 8px 0;">🖥️ Servers</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Infrastructure and server information</p>
            </div>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #2e7d32; margin: 0 0 8px 0;">🌐 Network Devices</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Network equipment and performance data</p>
            </div>
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #ef6c00; margin: 0 0 8px 0;">📱 Applications</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Software applications and their status</p>
            </div>
            <div style="background: #fce4ec; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #c2185b; margin: 0 0 8px 0;">🚨 Incidents</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">IT incidents and resolution times</p>
            </div>
            <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #7b1fa2; margin: 0 0 8px 0;">🎫 Tickets</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Support tickets and user requests</p>
            </div>
            <div style="background: #e0f2f1; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #00695c; margin: 0 0 8px 0;">💻 Assets</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">IT assets and their lifecycle information</p>
            </div>
            <div style="background: #fff8e1; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #f57f17; margin: 0 0 8px 0;">🔒 Security Events</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Security incidents and threat data</p>
            </div>
            <div style="background: #e8eaf6; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #3f51b5; margin: 0 0 8px 0;">💾 Backups</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">Backup operations and success rates</p>
            </div>
            <div style="background: #f1f8e9; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #558b2f; margin: 0 0 8px 0;">📋 Projects</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">IT projects and development metrics</p>
            </div>
            <div style="background: #fafafa; padding: 15px; border-radius: 8px; text-align: center;">
                <h5 style="color: #424242; margin: 0 0 8px 0;">👤 Users</h5>
                <p style="color: #4a5568; margin: 0; font-size: 0.85rem;">User information and access data</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_data_input():
    """Show data input forms and file upload options"""
    
    # Main header for the page
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #1e3c72; margin-bottom: 20px; text-align: center;">📊 Data Input & Management</h2>
        <p style="color: #4a5568; font-size: 1.1rem; line-height: 1.6; text-align: center;">
            Upload your IT data using our template or add data manually through the forms below.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different data input methods
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Template", "📤 Upload Data", "📝 Manual Entry", "📁 Sample Data Sets"
    ])
    
    # Tab 1: Template Download
    with tab1:
        st.markdown("### 📥 Download Data Template")
        
        st.markdown("Download the Excel template with all required data schema, fill it with your data, and upload it back.")
        
        # Create template for download
        if st.button("📥 Download Data Template", use_container_width=True):
            template = create_template_for_download()
            st.download_button(
                label="📥 Download Template",
                data=template.getvalue(),
                file_name="IT_Analytics_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ Template downloaded successfully! Fill it with your data and upload it in the 'Upload Data' tab.")
        
        # Add some spacing for visual balance
        st.markdown("")
        st.markdown("**Template includes:**")
        st.markdown("• 10 data tables in separate sheets")
        st.markdown("• Instructions sheet with field descriptions")
        st.markdown("• Proper column headers and data types")
        
        # Quick stats display
        if any([not st.session_state.servers_data.empty, not st.session_state.network_devices_data.empty, 
                not st.session_state.applications_data.empty, not st.session_state.incidents_data.empty,
                not st.session_state.tickets_data.empty, not st.session_state.assets_data.empty,
                not st.session_state.security_events_data.empty, not st.session_state.backups_data.empty,
                not st.session_state.projects_data.empty, not st.session_state.users_data.empty]):
            
            st.markdown("---")
            st.markdown("### 📊 Current Data Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if not st.session_state.servers_data.empty:
                    st.metric("🖥️ Servers", len(st.session_state.servers_data))
                if not st.session_state.network_devices_data.empty:
                    st.metric("🌐 Network Devices", len(st.session_state.network_devices_data))
            
            with col2:
                if not st.session_state.applications_data.empty:
                    st.metric("📱 Applications", len(st.session_state.applications_data))
                if not st.session_state.incidents_data.empty:
                    st.metric("🚨 Incidents", len(st.session_state.incidents_data))
            
            with col3:
                if not st.session_state.tickets_data.empty:
                    st.metric("🎫 Tickets", len(st.session_state.tickets_data))
                if not st.session_state.assets_data.empty:
                    st.metric("💻 Assets", len(st.session_state.assets_data))
            
            with col4:
                if not st.session_state.security_events_data.empty:
                    st.metric("🔒 Security Events", len(st.session_state.security_events_data))
                if not st.session_state.backups_data.empty:
                    st.metric("💾 Backups", len(st.session_state.backups_data))
    
    # Tab 2: Upload Data
    with tab2:
        st.markdown("### 📤 Upload Your Data")
        st.markdown("Upload your filled Excel template:")
        
        # File upload for Excel template
        uploaded_file = st.file_uploader(
            "Upload Excel file with all tables", 
            type=['xlsx', 'xls'],
            help="Upload the filled Excel template with all 10 tables in separate sheets"
        )
        
        # Add helpful information
        st.markdown("")
        st.markdown("**Upload features:**")
        st.markdown("• Automatic validation of all sheets")
        st.markdown("• Import all 10 tables at once")
        st.markdown("• Error checking and feedback")
        
        required_sheets = [
            "Servers", "Network_Devices", "Applications", "Incidents", "Tickets",
            "Assets", "Security_Events", "Backups", "Projects", "Users"
        ]
    
        if uploaded_file is not None:
            try:
                # Read all sheets from the Excel file
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                
                # Check if all required sheets are present
                available_sheets = list(excel_data.keys())
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
                
                if missing_sheets:
                    st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                    st.info("Please ensure your Excel file contains all 10 required sheets.")
                else:
                    # Load data into session state
                    st.session_state.servers_data = excel_data['Servers']
                    st.session_state.network_devices_data = excel_data['Network_Devices']
                    st.session_state.applications_data = excel_data['Applications']
                    st.session_state.incidents_data = excel_data['Incidents']
                    st.session_state.tickets_data = excel_data['Tickets']
                    st.session_state.assets_data = excel_data['Assets']
                    st.session_state.security_events_data = excel_data['Security_Events']
                    st.session_state.backups_data = excel_data['Backups']
                    st.session_state.projects_data = excel_data['Projects']
                    st.session_state.users_data = excel_data['Users']
                    
                    st.success("✅ All data loaded successfully from Excel file!")
                    st.info(f"📊 Loaded {len(st.session_state.servers_data)} servers, {len(st.session_state.applications_data)} applications, {len(st.session_state.tickets_data)} tickets, and more...")
                    
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.info("Please ensure the file is a valid Excel file with the correct format.")
    
    # Tab 3: Manual Data Entry
    with tab3:
        st.markdown("### 📝 Manual Data Entry")
        st.markdown("Add data manually using the forms below:")
        
        # Create sub-tabs for all the individual data entry forms
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6, sub_tab7, sub_tab8, sub_tab9, sub_tab10 = st.tabs([
            "🖥️ Servers", "🌐 Network Devices", "📱 Applications", "🚨 Incidents", "🎫 Tickets", 
            "💻 Assets", "🔒 Security Events", "💾 Backups", "📋 Projects", "👤 Users"
        ])
        
        # Sub-tab 1: Servers
        with sub_tab1:
            st.markdown("### 🖥️ Servers")
            st.markdown("Add and manage server infrastructure data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                server_id = st.text_input("Server ID", key="server_id_input")
                server_name = st.text_input("Server Name", key="server_name_input")
                server_type = st.selectbox("Server Type", ["Web Server", "Database Server", "Application Server", "File Server", "Mail Server"], key="server_type_input")
                location = st.selectbox("Location", ["Data Center A", "Data Center B", "Cloud AWS", "Cloud Azure", "Office HQ"], key="location_input")
                ip_address = st.text_input("IP Address", key="ip_address_input")
            
            with col2:
                os_version = st.selectbox("OS Version", ["Windows Server 2019", "Windows Server 2022", "Ubuntu 20.04", "Ubuntu 22.04", "CentOS 7", "CentOS 8"], key="os_version_input")
                cpu_cores = st.number_input("CPU Cores", min_value=1, value=4, key="cpu_cores_input")
                ram_gb = st.number_input("RAM (GB)", min_value=1, value=8, key="ram_gb_input")
                storage_tb = st.number_input("Storage (TB)", min_value=1, value=1, key="storage_tb_input")
                status = st.selectbox("Status", ["Active", "Maintenance", "Retired"], key="status_input")
            
            if st.button("Add Server"):
                new_server = pd.DataFrame([{
                    'server_id': server_id,
                    'server_name': server_name,
                    'server_type': server_type,
                    'location': location,
                    'ip_address': ip_address,
                    'os_version': os_version,
                    'cpu_cores': cpu_cores,
                    'ram_gb': ram_gb,
                    'storage_tb': storage_tb,
                    'status': status,
                    'last_maintenance': datetime.now()
                }])
                st.session_state.servers_data = pd.concat([st.session_state.servers_data, new_server], ignore_index=True)
                st.success("Server added successfully!")
            
            # Display existing data
            if not st.session_state.servers_data.empty:
                st.markdown("#### Existing Servers")
                display_dataframe_with_index_1(st.session_state.servers_data)
        
        # Sub-tab 2: Network Devices
        with sub_tab2:
            st.markdown("### 🌐 Network Devices")
            st.markdown("Add and manage network infrastructure data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                device_id = st.text_input("Device ID", key="device_id_input")
                device_name = st.text_input("Device Name", key="device_name_input")
                device_type = st.selectbox("Device Type", ["Router", "Switch", "Firewall", "Load Balancer", "Wireless AP"], key="device_type_input")
                location = st.selectbox("Location", ["Data Center A", "Data Center B", "Cloud AWS", "Cloud Azure", "Office HQ"], key="device_location_input")
                ip_address = st.text_input("IP Address", key="device_ip_input")
            
            with col2:
                model = st.selectbox("Model", ["Cisco 2960", "Cisco 3850", "Fortinet FG-60F", "F5 BIG-IP", "Aruba AP-515"], key="model_input")
                firmware_version = st.text_input("Firmware Version", value="v1.0.0", key="firmware_input")
                status = st.selectbox("Status", ["Active", "Backup", "Maintenance"], key="device_status_input")
            
            if st.button("Add Network Device"):
                new_device = pd.DataFrame([{
                    'device_id': device_id,
                    'device_name': device_name,
                    'device_type': device_type,
                    'location': location,
                    'ip_address': ip_address,
                    'model': model,
                    'firmware_version': firmware_version,
                    'status': status,
                    'last_backup': datetime.now()
                }])
                st.session_state.network_devices_data = pd.concat([st.session_state.network_devices_data, new_device], ignore_index=True)
                st.success("Network Device added successfully!")
            
            # Display existing data
            if not st.session_state.network_devices_data.empty:
                st.markdown("#### Existing Network Devices")
                display_dataframe_with_index_1(st.session_state.network_devices_data)
        
        # Sub-tab 3: Applications
        with sub_tab3:
            st.markdown("### 📱 Applications")
            st.markdown("Add and manage application data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                app_id = st.text_input("Application ID", key="app_id_input")
                app_name = st.text_input("Application Name", key="app_name_input")
                app_type = st.selectbox("Application Type", ["Web Application", "Database", "Email System", "CRM", "ERP", "BI Tool", "Security Tool"], key="app_type_input")
                version = st.text_input("Version", value="1.0.0", key="version_input")
                server_id = st.text_input("Server ID", key="app_server_id_input")
            
            with col2:
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Sales", "Marketing", "Operations"], key="app_dept_input")
                status = st.selectbox("Status", ["Active", "Development", "Maintenance", "Retired"], key="app_status_input")
                last_updated = st.date_input("Last Updated", key="app_updated_input")
                criticality = st.selectbox("Criticality", ["Low", "Medium", "High", "Critical"], key="app_criticality_input")
            
            if st.button("Add Application"):
                new_app = pd.DataFrame([{
                    'app_id': app_id,
                    'app_name': app_name,
                    'app_type': app_type,
                    'version': version,
                    'server_id': server_id,
                    'department': department,
                    'status': status,
                    'last_updated': last_updated,
                    'criticality': criticality
                }])
                st.session_state.applications_data = pd.concat([st.session_state.applications_data, new_app], ignore_index=True)
                st.success("Application added successfully!")
            
            # Display existing data
            if not st.session_state.applications_data.empty:
                st.markdown("#### Existing Applications")
                display_dataframe_with_index_1(st.session_state.applications_data)
        
        # Sub-tab 4: Incidents
        with sub_tab4:
            st.markdown("### 🚨 Incidents")
            st.markdown("Add and manage incident data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                incident_id = st.text_input("Incident ID", key="incident_id_input")
                title = st.text_input("Title", key="incident_title_input")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="incident_priority_input")
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], key="incident_status_input")
                category = st.selectbox("Category", ["Hardware", "Software", "Network", "Security", "User Error"], key="incident_category_input")
            
            with col2:
                reported_by = st.text_input("Reported By", key="incident_reporter_input")
                assigned_to = st.text_input("Assigned To", key="incident_assignee_input")
                created_date = st.date_input("Created Date", key="incident_created_input")
                resolved_date = st.date_input("Resolved Date", key="incident_resolved_input")
            
            if st.button("Add Incident"):
                new_incident = pd.DataFrame([{
                    'incident_id': incident_id,
                    'title': title,
                    'priority': priority,
                    'status': status,
                    'category': category,
                    'reported_by': reported_by,
                    'assigned_to': assigned_to,
                    'created_date': created_date,
                    'resolved_date': resolved_date
                }])
                st.session_state.incidents_data = pd.concat([st.session_state.incidents_data, new_incident], ignore_index=True)
                st.success("Incident added successfully!")
            
            # Display existing data
            if not st.session_state.incidents_data.empty:
                st.markdown("#### Existing Incidents")
                display_dataframe_with_index_1(st.session_state.incidents_data)
        
        # Sub-tab 5: Tickets
        with sub_tab5:
            st.markdown("### 🎫 Tickets")
            st.markdown("Add and manage support ticket data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                ticket_id = st.text_input("Ticket ID", key="ticket_id_input")
                title = st.text_input("Title", key="ticket_title_input")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="ticket_priority_input")
                status = st.selectbox("Status", ["Open", "In Progress", "Waiting", "Resolved", "Closed"], key="ticket_status_input")
                category = st.selectbox("Category", ["Technical", "Access", "Software", "Hardware", "Network"], key="ticket_category_input")
            
            with col2:
                requester = st.text_input("Requester", key="ticket_requester_input")
                assignee = st.text_input("Assignee", key="ticket_assignee_input")
                created_date = st.date_input("Created Date", key="ticket_created_input")
                due_date = st.date_input("Due Date", key="ticket_due_input")
            
            if st.button("Add Ticket"):
                new_ticket = pd.DataFrame([{
                    'ticket_id': ticket_id,
                    'title': title,
                    'priority': priority,
                    'status': status,
                    'category': category,
                    'requester': requester,
                    'assignee': assignee,
                    'created_date': created_date,
                    'due_date': due_date
                }])
                st.session_state.tickets_data = pd.concat([st.session_state.tickets_data, new_ticket], ignore_index=True)
                st.success("Ticket added successfully!")
            
            # Display existing data
            if not st.session_state.tickets_data.empty:
                st.markdown("#### Existing Tickets")
                display_dataframe_with_index_1(st.session_state.tickets_data)
        
        # Sub-tab 6: Assets
        with sub_tab6:
            st.markdown("### 💻 Assets")
            st.markdown("Add and manage asset data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                asset_id = st.text_input("Asset ID", key="asset_id_input")
                asset_name = st.text_input("Asset Name", key="asset_name_input")
                asset_type = st.selectbox("Asset Type", ["Laptop", "Desktop", "Monitor", "Printer", "Mobile Device"], key="asset_type_input")
                location = st.selectbox("Location", ["Office HQ", "Branch Office", "Home Office", "Warehouse"], key="asset_location_input")
                assigned_to = st.text_input("Assigned To", key="asset_assignee_input")
            
            with col2:
                model = st.text_input("Model", key="asset_model_input")
                vendor = st.text_input("Vendor", key="asset_vendor_input")
                purchase_date = st.date_input("Purchase Date", key="asset_purchase_input")
                warranty_expiry = st.date_input("Warranty Expiry", key="asset_warranty_input")
                status = st.selectbox("Status", ["Active", "Maintenance", "Retired", "Lost"], key="asset_status_input")
            
            if st.button("Add Asset"):
                new_asset = pd.DataFrame([{
                    'asset_id': asset_id,
                    'asset_name': asset_name,
                    'asset_type': asset_type,
                    'location': location,
                    'assigned_to': assigned_to,
                    'model': model,
                    'vendor': vendor,
                    'purchase_date': purchase_date,
                    'warranty_expiry': warranty_expiry,
                    'status': status
                }])
                st.session_state.assets_data = pd.concat([st.session_state.assets_data, new_asset], ignore_index=True)
                st.success("Asset added successfully!")
            
            # Display existing data
            if not st.session_state.assets_data.empty:
                st.markdown("#### Existing Assets")
                display_dataframe_with_index_1(st.session_state.assets_data)
        
        # Sub-tab 7: Security Events
        with sub_tab7:
            st.markdown("### 🔒 Security Events")
            st.markdown("Add and manage security event data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                event_id = st.text_input("Event ID", key="security_event_id_input")
                event_type = st.selectbox("Event Type", ["Login Attempt", "Data Access", "System Change", "Network Activity", "Malware Alert"], key="security_event_type_input")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], key="security_severity_input")
                status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "False Positive"], key="security_status_input")
                source_ip = st.text_input("Source IP", key="security_source_ip_input")
            
            with col2:
                target_system = st.text_input("Target System", key="security_target_input")
                user_involved = st.text_input("User Involved", key="security_user_input")
                timestamp_date = st.date_input("Timestamp Date", key="security_timestamp_date_input")
                timestamp_time = st.time_input("Timestamp Time", key="security_timestamp_time_input")
                description = st.text_area("Description", key="security_description_input")
            
            if st.button("Add Security Event"):
                # Combine date and time into datetime
                from datetime import datetime, time
                timestamp = datetime.combine(timestamp_date, timestamp_time)
                
                new_security_event = pd.DataFrame([{
                    'event_id': event_id,
                    'event_type': event_type,
                    'severity': severity,
                    'status': status,
                    'source_ip': source_ip,
                    'target_system': target_system,
                    'user_involved': user_involved,
                    'timestamp': timestamp,
                    'description': description
                }])
                st.session_state.security_events_data = pd.concat([st.session_state.security_events_data, new_security_event], ignore_index=True)
                st.success("Security event added successfully!")
            
            # Display existing data
            if not st.session_state.security_events_data.empty:
                st.markdown("#### Existing Security Events")
                display_dataframe_with_index_1(st.session_state.security_events_data)
        
        # Sub-tab 8: Backups
        with sub_tab8:
            st.markdown("### 💾 Backups")
            st.markdown("Add and manage backup data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                backup_id = st.text_input("Backup ID", key="backup_id_input")
                system_name = st.text_input("System Name", key="backup_system_input")
                backup_type = st.selectbox("Backup Type", ["Full", "Incremental", "Differential"], key="backup_type_input")
                status = st.selectbox("Status", ["Successful", "Failed", "In Progress", "Scheduled"], key="backup_status_input")
                size_gb = st.number_input("Size (GB)", min_value=0.1, value=10.0, key="backup_size_input")
            
            with col2:
                start_date = st.date_input("Start Date", key="backup_start_date_input")
                start_time = st.time_input("Start Time", key="backup_start_time_input")
                end_date = st.date_input("End Date", key="backup_end_date_input")
                end_time = st.time_input("End Time", key="backup_end_time_input")
                retention_days = st.number_input("Retention (Days)", min_value=1, value=30, key="backup_retention_input")
                location = st.selectbox("Location", ["Local", "Cloud", "Offsite"], key="backup_location_input")
            
            if st.button("Add Backup"):
                # Combine date and time into datetime
                from datetime import datetime, time
                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)
                
                new_backup = pd.DataFrame([{
                    'backup_id': backup_id,
                    'system_name': system_name,
                    'backup_type': backup_type,
                    'status': status,
                    'size_gb': size_gb,
                    'start_time': start_datetime,
                    'end_time': end_datetime,
                    'retention_days': retention_days,
                    'location': location
                }])
                st.session_state.backups_data = pd.concat([st.session_state.backups_data, new_backup], ignore_index=True)
                st.success("Backup added successfully!")
            
            # Display existing data
            if not st.session_state.backups_data.empty:
                st.markdown("#### Existing Backups")
                display_dataframe_with_index_1(st.session_state.backups_data)
        
        # Sub-tab 9: Projects
        with sub_tab9:
            st.markdown("### 📋 Projects")
            st.markdown("Add and manage project data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_id = st.text_input("Project ID", key="project_id_input")
                project_name = st.text_input("Project Name", key="project_name_input")
                project_type = st.selectbox("Project Type", ["Infrastructure", "Application", "Security", "Migration", "Upgrade"], key="project_type_input")
                status = st.selectbox("Status", ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"], key="project_status_input")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="project_priority_input")
            
            with col2:
                manager = st.text_input("Project Manager", key="project_manager_input")
                start_date = st.date_input("Start Date", key="project_start_input")
                end_date = st.date_input("End Date", key="project_end_input")
                budget = st.number_input("Budget ($)", min_value=0, value=10000, key="project_budget_input")
            
            if st.button("Add Project"):
                new_project = pd.DataFrame([{
                    'project_id': project_id,
                    'project_name': project_name,
                    'project_type': project_type,
                    'status': status,
                    'priority': priority,
                    'manager': manager,
                    'start_date': start_date,
                    'end_date': end_date,
                    'budget': budget
                }])
                st.session_state.projects_data = pd.concat([st.session_state.projects_data, new_project], ignore_index=True)
                st.success("Project added successfully!")
            
            # Display existing data
            if not st.session_state.projects_data.empty:
                st.markdown("#### Existing Projects")
                display_dataframe_with_index_1(st.session_state.projects_data)
        
        # Sub-tab 10: Users
        with sub_tab10:
            st.markdown("### 👤 Users")
            st.markdown("Add and manage user data.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_id = st.text_input("User ID", key="user_id_input")
                username = st.text_input("Username", key="user_username_input")
                full_name = st.text_input("Full Name", key="user_fullname_input")
                email = st.text_input("Email", key="user_email_input")
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Sales", "Marketing", "Operations"], key="user_dept_input")
            
            with col2:
                role = st.selectbox("Role", ["User", "Admin", "Manager", "Supervisor"], key="user_role_input")
                status = st.selectbox("Status", ["Active", "Inactive", "Suspended"], key="user_status_input")
                created_date = st.date_input("Created Date", key="user_created_input")
                last_login_date = st.date_input("Last Login Date", key="user_lastlogin_date_input")
                last_login_time = st.time_input("Last Login Time", key="user_lastlogin_time_input")
            
            if st.button("Add User"):
                # Combine date and time into datetime
                from datetime import datetime, time
                last_login = datetime.combine(last_login_date, last_login_time)
                
                new_user = pd.DataFrame([{
                    'user_id': user_id,
                    'username': username,
                    'full_name': full_name,
                    'email': email,
                    'department': department,
                    'role': role,
                    'status': status,
                    'created_date': created_date,
                    'last_login': last_login
                }])
                st.session_state.users_data = pd.concat([st.session_state.users_data, new_user], ignore_index=True)
                st.success("User added successfully!")
            
            # Display existing data
            if not st.session_state.users_data.empty:
                st.markdown("#### Existing Users")
                display_dataframe_with_index_1(st.session_state.users_data)
    # Tab 4: Sample Data Sets
    with tab4:
        show_sample_data_sets()

    

    

    

    

    

    

    

    

    


def show_sample_data_sets():
    """Display sample data sets for testing the program"""
    st.title("📁 Sample Data Sets for Testing")
    
    st.markdown("""
    <div class="welcome-section">
        <h2>🚀 Ready-to-Use Sample Data</h2>
        <p>Download these pre-populated Excel files to test all features of the IT Analytics Dashboard without manual data entry.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple buttons to load sample data directly into the system
    st.markdown("### 🚀 Load Sample Data Sets")
    st.markdown("Click any button below to automatically load sample data into the system:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Load Basic Sample Data", key="load_basic_btn", use_container_width=True):
            with st.spinner("Loading basic sample data..."):
                basic_sample_data = create_basic_sample_data()
                
                # Load data directly into session state
                st.session_state.servers_data = basic_sample_data.get('Servers', pd.DataFrame())
                st.session_state.network_devices_data = basic_sample_data.get('Network_Devices', pd.DataFrame())
                st.session_state.applications_data = basic_sample_data.get('Applications', pd.DataFrame())
                st.session_state.incidents_data = basic_sample_data.get('Incidents', pd.DataFrame())
                st.session_state.tickets_data = basic_sample_data.get('Tickets', pd.DataFrame())
                st.session_state.assets_data = basic_sample_data.get('Assets', pd.DataFrame())
                st.session_state.security_events_data = basic_sample_data.get('Security_Events', pd.DataFrame())
                st.session_state.backups_data = basic_sample_data.get('Backups', pd.DataFrame())
                st.session_state.projects_data = basic_sample_data.get('Projects', pd.DataFrame())
                st.session_state.users_data = basic_sample_data.get('Users', pd.DataFrame())
                
                st.success("✅ Basic sample data loaded successfully!")
                st.info(f"📊 Loaded: {len(st.session_state.servers_data)} servers, {len(st.session_state.applications_data)} applications, {len(st.session_state.tickets_data)} tickets, and more...")
    
    with col2:
        if st.button("🔒 Load Security Sample Data", key="load_security_btn", use_container_width=True):
            with st.spinner("Loading security sample data..."):
                security_sample_data = create_security_sample_data()
                
                # Load security-focused data
                st.session_state.security_events_data = security_sample_data.get('Security_Events', pd.DataFrame())
                st.session_state.incidents_data = security_sample_data.get('Incidents', pd.DataFrame())
                st.session_state.backups_data = security_sample_data.get('Backups', pd.DataFrame())
                st.session_state.users_data = security_sample_data.get('Users', pd.DataFrame())
                
                st.success("✅ Security sample data loaded successfully!")
                st.info(f"🔒 Loaded: {len(st.session_state.security_events_data)} security events, {len(st.session_state.incidents_data)} incidents, and more...")
    
    with col3:
        if st.button("🚀 Load Comprehensive Sample Data", key="load_comprehensive_btn", use_container_width=True):
            with st.spinner("Loading comprehensive sample data..."):
                comprehensive_sample_data = create_comprehensive_sample_data()
                
                # Load all comprehensive data
                st.session_state.servers_data = comprehensive_sample_data.get('Servers', pd.DataFrame())
                st.session_state.network_devices_data = comprehensive_sample_data.get('Network_Devices', pd.DataFrame())
                st.session_state.applications_data = comprehensive_sample_data.get('Applications', pd.DataFrame())
                st.session_state.incidents_data = comprehensive_sample_data.get('Incidents', pd.DataFrame())
                st.session_state.tickets_data = comprehensive_sample_data.get('Tickets', pd.DataFrame())
                st.session_state.assets_data = comprehensive_sample_data.get('Assets', pd.DataFrame())
                st.session_state.security_events_data = comprehensive_sample_data.get('Security_Events', pd.DataFrame())
                st.session_state.backups_data = comprehensive_sample_data.get('Backups', pd.DataFrame())
                st.session_state.projects_data = comprehensive_sample_data.get('Projects', pd.DataFrame())
                st.session_state.users_data = comprehensive_sample_data.get('Users', pd.DataFrame())
                
                st.success("✅ Comprehensive sample data loaded successfully!")
                st.info(f"🚀 Loaded: {len(st.session_state.servers_data)} servers, {len(st.session_state.applications_data)} applications, {len(st.session_state.tickets_data)} tickets, and more...")
    
    st.markdown("---")
    
    # Sample data preview section
    st.subheader("📋 Sample Data Preview")
    
    # Show preview button for basic sample data
    st.markdown("### 🖥️ Sample Servers Data Preview")
    if st.button("👁️ Preview Basic Sample Data", key="preview_basic_btn"):
        with st.spinner("Loading preview..."):
            basic_sample_data = create_basic_sample_data()
            servers_preview = basic_sample_data.get('Servers', pd.DataFrame())
            if not servers_preview.empty:
                st.dataframe(servers_preview.head(), use_container_width=True)
                st.caption("💡 This is just a preview. Click the generate buttons above to download full samples.")
            else:
                st.warning("No sample data available.")
    
    st.markdown("---")
    
    # Instructions for using sample data
    st.subheader("📚 How to Use Sample Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📥 Step 1: Load Sample Data</h4>
            <ul>
                <li>Choose the sample dataset that fits your testing needs</li>
                <li>Click the load button to automatically populate the system</li>
                <li>Data is immediately available for all dashboard features</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🚀 Step 2: Start Testing</h4>
            <ul>
                <li>Navigate to any dashboard section</li>
                <li>All analytics and visualizations will work immediately</li>
                <li>No need to upload files - data is already loaded</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data structure information
    st.subheader("📊 Sample Data Structure")
    
    st.markdown("""
    <div class="info-card">
        <h4>📋 What's Included in Each Sample:</h4>
        <ul>
            <li><strong>Basic Sample:</strong> 10 data tables with essential IT metrics including servers, network devices, applications, incidents, tickets, assets, security events, backups, projects, and users</li>
            <li><strong>Security Sample:</strong> 4 focused tables for security and risk analysis including security events, incidents, backups, and users</li>
            <li><strong>Comprehensive Sample:</strong> 12 enhanced tables with enterprise-level data including 50+ servers, 40+ network devices, 60+ applications, 100+ incidents, 200+ tickets, 100+ assets, 100+ security events, 50+ backups, 30+ projects, 100+ users, cost data, and performance metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def show_infrastructure_systems():
    """Display infrastructure and systems performance analysis"""
    st.title("🖥️ Infrastructure & Systems Performance")
    
    if st.session_state.servers_data.empty:
        st.warning("⚠️ No server data available. Please upload data first.")
        return
    
    # Server Uptime Analysis
    st.subheader("🖥️ Server Uptime Analysis")
    uptime_df, uptime_msg = calculate_server_uptime(st.session_state.servers_data, st.session_state.incidents_data)
    
    if not uptime_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Uptime chart
            fig = create_chart("bar", uptime_df, x='server_name', y='uptime_percentage', 
                        title='Server Uptime Percentage',
                        color='uptime_percentage',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Server", yaxis_title="Uptime %")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Average Uptime", f"{uptime_df['uptime_percentage'].mean():.2f}%")
            st.metric("Lowest Uptime", f"{uptime_df['uptime_percentage'].min():.2f}%")
            st.metric("Highest Uptime", f"{uptime_df['uptime_percentage'].max():.2f}%")
        
        st.info(f"📊 {uptime_msg}")
        display_dataframe_with_index_1(uptime_df)
    
    st.markdown("---")
    
    # Network Latency Analysis
    st.subheader("🌐 Network Latency Analysis")
    if not st.session_state.network_devices_data.empty:
        latency_df, latency_msg = calculate_network_latency(st.session_state.network_devices_data, st.session_state.incidents_data)
        
        if not latency_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_chart("scatter", latency_df, x='device_name', y='avg_latency_ms', 
                               title='Network Device Latency',
                               color='device_type',
                               size='avg_latency_ms')
                fig.update_layout(xaxis_title="Device", yaxis_title="Latency (ms)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Average Latency", f"{latency_df['avg_latency_ms'].mean():.1f} ms")
                st.metric("Min Latency", f"{latency_df['avg_latency_ms'].min():.1f} ms")
                st.metric("Max Latency", f"{latency_df['avg_latency_ms'].max():.1f} ms")
            
            st.info(f"📊 {latency_msg}")
            display_dataframe_with_index_1(latency_df)
    
    st.markdown("---")
    
    # System Load Analysis
    st.subheader("⚡ System Load Analysis")
    if not st.session_state.applications_data.empty:
        load_df, load_msg = calculate_system_load(st.session_state.servers_data, st.session_state.applications_data)
        
        if not load_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_chart("bar", load_df, x='server_name', y='load_percentage', 
                           title='System Load by Server',
                           color='app_count',
                           color_continuous_scale='plasma')
                fig.update_layout(xaxis_title="Server", yaxis_title="Load %")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Average Load", f"{load_df['load_percentage'].mean():.1f}%")
                st.metric("Peak Load", f"{load_df['load_percentage'].max():.1f}%")
                st.metric("Total Apps", f"{load_df['app_count'].sum()}")
            
            st.info(f"📊 {load_msg}")
            display_dataframe_with_index_1(load_df)
    
    st.markdown("---")
    
    # Application Performance Monitoring
    st.subheader("📱 Application Performance Monitoring")
    if not st.session_state.applications_data.empty:
        perf_df, perf_msg = calculate_application_performance(st.session_state.applications_data, st.session_state.incidents_data)
        
        if not perf_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_chart("scatter", perf_df, x='response_time_ms', y='error_rate_percent', 
                               title='Application Performance',
                               color='critical_level',
                               size='health_score',
                               hover_data=['app_name'])
                fig.update_layout(xaxis_title="Response Time (ms)", yaxis_title="Error Rate (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(perf_df, x='app_name', y='health_score', 
                           title='Application Health Score',
                           color='health_score',
                           color_continuous_scale='RdYlGn')
                fig.update_layout(xaxis_title="Application", yaxis_title="Health Score")
                st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"📊 {perf_msg}")
            display_dataframe_with_index_1(perf_df)
    
    st.markdown("---")
    
    # Incident Response Time Analysis
    st.subheader("🚨 Incident Response Time Analysis")
    if not st.session_state.incidents_data.empty:
        response_df, response_msg = calculate_incident_response_time(st.session_state.incidents_data)
        
        if not response_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(response_df, x='priority', y='mean', 
                           title='Average Resolution Time by Priority',
                           color='count',
                           color_continuous_scale='Reds')
                fig.update_layout(xaxis_title="Priority", yaxis_title="Resolution Time (minutes)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Avg Resolution Time", f"{response_df['mean'].mean():.1f} min")
                st.metric("Total Incidents", f"{response_df['count'].sum()}")
                st.metric("High Priority Avg", f"{response_df[response_df['priority'] == 'High']['mean'].iloc[0] if not response_df[response_df['priority'] == 'High'].empty else 0:.1f} min")
            
            st.info(f"📊 {response_msg}")
            display_dataframe_with_index_1(response_df)
    
    st.markdown("---")
    
    # System Availability Analysis
    st.subheader("✅ System Availability Analysis")
    if not st.session_state.applications_data.empty:
        availability_df, availability_msg = calculate_system_availability(st.session_state.servers_data, st.session_state.applications_data, st.session_state.incidents_data)
        
        if not availability_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(availability_df, x='server_name', y='availability_percentage', 
                           title='System Availability by Server',
                           color='app_count',
                           color_continuous_scale='Greens')
                fig.update_layout(xaxis_title="Server", yaxis_title="Availability %")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Average Availability", f"{availability_df['availability_percentage'].mean():.2f}%")
                st.metric("Lowest Availability", f"{availability_df['availability_percentage'].min():.2f}%")
                st.metric("Total Critical Apps", f"{availability_df['critical_apps'].sum()}")
            
            st.info(f"📊 {availability_msg}")
            display_dataframe_with_index_1(availability_df)

def show_security_risk():
    """Display security and risk management analysis"""
    st.title("🔒 Security & Risk Management")
    
    if st.session_state.security_events_data.empty:
        st.warning("⚠️ No security event data available. Please upload data first.")
        return
    
    # Vulnerability Analysis
    st.subheader("🔍 Vulnerability Analysis")
    vuln_df, vuln_msg = calculate_vulnerability_analysis(st.session_state.security_events_data, st.session_state.servers_data, st.session_state.applications_data)
    
    if not vuln_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the pie chart
            vuln_data = pd.DataFrame({
                'Type': ['Total Vulnerabilities', 'Server Vulnerabilities', 'Application Vulnerabilities'],
                'Count': [vuln_df['total_vulnerabilities'].iloc[0], vuln_df['server_vulnerabilities'].iloc[0], vuln_df['application_vulnerabilities'].iloc[0]]
            })
            
            fig = create_chart("pie", vuln_data, values='Count', 
                        names='Type',
                        title='Vulnerability Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Vulnerability Rate", f"{vuln_df['vulnerability_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total Systems", vuln_df['total_systems'].iloc[0])
            st.metric("Total Vulnerabilities", vuln_df['total_vulnerabilities'].iloc[0])
        
        st.info(f"📊 {vuln_msg}")
        display_dataframe_with_index_1(vuln_df)
    
    st.markdown("---")
    
    # Firewall Performance Analysis
    st.subheader("🛡️ Firewall Performance Analysis")
    firewall_df, firewall_msg = calculate_firewall_performance(st.session_state.security_events_data)
    
    if not firewall_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the chart
            firewall_data = pd.DataFrame({
                'Status': ['Blocked', 'Successful'],
                'Count': [firewall_df['blocked_attempts'].iloc[0], firewall_df['successful_attempts'].iloc[0]]
            })
            
            fig = create_chart("bar", firewall_data, x='Status', y='Count',
                        title='Firewall Effectiveness',
                        color='Status',
                        color_discrete_map={'Blocked': 'red', 'Successful': 'green'})
            fig.update_layout(xaxis_title="Access Attempts", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Firewall Effectiveness", f"{firewall_df['firewall_effectiveness_percent'].iloc[0]:.1f}%")
            st.metric("Total Attempts", firewall_df['total_access_attempts'].iloc[0])
            st.metric("Blocked Attempts", firewall_df['blocked_attempts'].iloc[0])
        
        st.info(f"📊 {firewall_msg}")
        display_dataframe_with_index_1(firewall_df)
    
    st.markdown("---")
    
    # Data Breach Analysis
    st.subheader("🚨 Data Breach Analysis")
    breach_df, breach_msg = calculate_data_breach_analysis(st.session_state.security_events_data, st.session_state.incidents_data)
    
    if not breach_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the chart
            breach_data = pd.DataFrame({
                'Type': ['Data Breaches', 'Security Events', 'Incident Breaches'],
                'Count': [breach_df['data_breaches_detected'].iloc[0], breach_df['security_events'].iloc[0], breach_df['incident_breaches'].iloc[0]]
            })
            
            fig = create_chart("bar", breach_data, x='Type', y='Count',
                        title='Data Breach Incidents',
                        color='Type',
                        color_discrete_sequence=['red', 'orange', 'yellow'])
            fig.update_layout(xaxis_title="Breach Type", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Data Breach Rate", f"{breach_df['data_breach_rate_percent'].iloc[0]:.3f}%")
            st.metric("Total Data Stored", breach_df['total_data_stored'].iloc[0])
            st.metric("Breaches Detected", breach_df['data_breaches_detected'].iloc[0])
        
        st.info(f"📊 {breach_msg}")
        display_dataframe_with_index_1(breach_df)
    
    st.markdown("---")
    
    # Access Control Analysis
    st.subheader("🔐 Access Control Analysis")
    if not st.session_state.users_data.empty:
        access_df, access_msg = calculate_access_control_analysis(st.session_state.users_data, st.session_state.security_events_data)
        
        if not access_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create data for the pie chart
                access_data = pd.DataFrame({
                    'Status': ['Active Users', 'Inactive Users'],
                    'Count': [access_df['active_users'].iloc[0], access_df['inactive_users'].iloc[0]]
                })
                
                fig = create_chart("pie", access_data, values='Count',
                           names='Status',
                           title='User Access Status')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Access Control Compliance", f"{access_df['access_control_compliance_percent'].iloc[0]:.1f}%")
                st.metric("Total Users", access_df['total_users'].iloc[0])
                st.metric("Unauthorized Attempts", access_df['unauthorized_access_attempts'].iloc[0])
            
            st.info(f"📊 {access_msg}")
            display_dataframe_with_index_1(access_df)
    
    st.markdown("---")
    
    # Phishing Metrics
    st.subheader("🎣 Phishing Attack Metrics")
    phishing_df, phishing_msg = calculate_phishing_metrics(st.session_state.security_events_data, st.session_state.incidents_data)
    
    if not phishing_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(x=['Phishing Attempts', 'Successful Attacks'], 
                        y=[phishing_df['phishing_attempts'].iloc[0], phishing_df['successful_phishing_attacks'].iloc[0]],
                        title='Phishing Attack Analysis',
                        color=['Attempts', 'Successful'],
                        color_discrete_map={'Attempts': 'orange', 'Successful': 'red'})
            fig.update_layout(xaxis_title="Attack Type", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Phishing Attempt Rate", f"{phishing_df['phishing_attempt_rate_percent'].iloc[0]:.2f}%")
            st.metric("Phishing Success Rate", f"{phishing_df['phishing_success_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total User Interactions", phishing_df['total_user_interactions'].iloc[0])
        
        st.info(f"📊 {phishing_msg}")
        display_dataframe_with_index_1(phishing_df)
    
    st.markdown("---")
    
    # Encryption Effectiveness
    st.subheader("🔐 Encryption Effectiveness")
    if not st.session_state.assets_data.empty:
        encryption_df, encryption_msg = calculate_encryption_effectiveness(st.session_state.security_events_data, st.session_state.assets_data)
        
        if not encryption_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.pie(values=[encryption_df['encrypted_assets'].iloc[0], encryption_df['unencrypted_assets'].iloc[0]], 
                           names=['Encrypted', 'Unencrypted'],
                           title='Asset Encryption Status')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Encryption Effectiveness", f"{encryption_df['encryption_effectiveness_percent'].iloc[0]:.1f}%")
                st.metric("Sensitive Assets", encryption_df['total_sensitive_assets'].iloc[0])
                st.metric("Encrypted Assets", encryption_df['encrypted_assets'].iloc[0])
            
            st.info(f"📊 {encryption_msg}")
            display_dataframe_with_index_1(encryption_df)

def show_it_support():
    """Display IT support and help desk analysis"""
    st.title("🛠️ IT Support & Help Desk")
    
    if st.session_state.tickets_data.empty:
        st.warning("⚠️ No ticket data available. Please upload data first.")
        return
    
    # Ticket Resolution Rate
    st.subheader("📊 Ticket Resolution Rate")
    resolution_df, resolution_msg = calculate_ticket_resolution_rate(st.session_state.tickets_data)
    
    if not resolution_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the pie chart
            sla_data = pd.DataFrame({
                'Status': ['SLA Compliant', 'SLA Violation'],
                'Count': [resolution_df['sla_compliant_tickets'].iloc[0], resolution_df['resolved_tickets'].iloc[0] - resolution_df['sla_compliant_tickets'].iloc[0]]
            })
            fig = create_chart("pie", sla_data, values='Count', 
                        names='Status',
                        title='Ticket Resolution SLA Compliance')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Resolution Rate", f"{resolution_df['resolution_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total Tickets", resolution_df['total_tickets'].iloc[0])
            st.metric("Pending Tickets", resolution_df['pending_tickets'].iloc[0])
        
        st.info(f"📊 {resolution_msg}")
        display_dataframe_with_index_1(resolution_df)
    
    st.markdown("---")
    
    # First Call Resolution
    st.subheader("📞 First Call Resolution")
    fcr_df, fcr_msg = calculate_first_call_resolution(st.session_state.tickets_data)
    
    if not fcr_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the bar chart
            fcr_data = pd.DataFrame({
                'Issue Type': ['FCR Issues', 'Escalated Issues'],
                'Count': [fcr_df['issues_resolved_first_call'].iloc[0], fcr_df['escalated_issues'].iloc[0]]
            })
            fig = create_chart("bar", fcr_data, x='Issue Type', y='Count',
                        title='First Call Resolution vs Escalation',
                        color='Issue Type',
                        color_discrete_map={'FCR Issues': 'green', 'Escalated Issues': 'orange'})
            fig.update_layout(xaxis_title="Issue Type", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("FCR Rate", f"{fcr_df['fcr_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total Issues", fcr_df['total_issues_reported'].iloc[0])
            st.metric("FCR Issues", fcr_df['issues_resolved_first_call'].iloc[0])
        
        st.info(f"📊 {fcr_msg}")
        display_dataframe_with_index_1(fcr_df)
    
    st.markdown("---")
    
    # Average Resolution Time
    st.subheader("⏱️ Average Resolution Time")
    time_df, time_msg = calculate_average_resolution_time(st.session_state.tickets_data)
    
    if not time_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = create_chart("bar", time_df, x='priority', y='mean', 
                        title='Average Resolution Time by Priority',
                        color='count',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Priority", yaxis_title="Resolution Time (minutes)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Avg Resolution Time", f"{time_df['mean'].mean():.1f} min")
            st.metric("Total Resolved", time_df['count'].sum())
            st.metric("Fastest Resolution", f"{time_df['mean'].min():.1f} min")
        
        st.info(f"📊 {time_msg}")
        display_dataframe_with_index_1(time_df)
    
    st.markdown("---")
    
    # Ticket Volume Analysis
    st.subheader("📈 Ticket Volume Analysis")
    volume_df, volume_msg = calculate_ticket_volume_analysis(st.session_state.tickets_data)
    
    if not volume_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get category volume data for the chart
            category_volume = st.session_state.tickets_data.groupby('category').size().reset_index(name='ticket_count')
            category_volume = category_volume.sort_values('ticket_count', ascending=False)
            
            fig = create_chart("bar", category_volume, x='category', y='ticket_count', 
                        title='Ticket Volume by Category',
                        color='ticket_count',
                        color_continuous_scale='plasma')
            fig.update_layout(xaxis_title="Category", yaxis_title="Ticket Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Daily Volume Rate", f"{volume_df['daily_volume_rate'].iloc[0]:.1f}")
            st.metric("Total Tickets", volume_df['total_tickets'].iloc[0])
            st.metric("Peak Day Estimate", volume_df['peak_day_tickets'].iloc[0])
        
        st.info(f"📊 {volume_msg}")
        display_dataframe_with_index_1(volume_df)
    
    st.markdown("---")
    
    # User Satisfaction Metrics
    st.subheader("😊 User Satisfaction Metrics")
    satisfaction_df, satisfaction_msg = calculate_user_satisfaction_metrics(st.session_state.tickets_data)
    
    if not satisfaction_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create data for the pie chart
            satisfaction_data = pd.DataFrame({
                'Status': ['Satisfied', 'Dissatisfied'],
                'Count': [satisfaction_df['satisfied_users'].iloc[0], satisfaction_df['dissatisfied_users'].iloc[0]]
            })
            fig = create_chart("pie", satisfaction_data, values='Count', 
                        names='Status',
                        title='User Satisfaction Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Satisfaction Rate", f"{satisfaction_df['satisfaction_rate_percent'].iloc[0]:.1f}%")
            st.metric("Avg Satisfaction Score", f"{satisfaction_df['avg_satisfaction_score'].iloc[0]:.1f}")
            st.metric("Users Surveyed", satisfaction_df['total_users_surveyed'].iloc[0])
        
        st.info(f"📊 {satisfaction_msg}")
        display_dataframe_with_index_1(satisfaction_df)
    
    st.markdown("---")
    
    # Recurring Issue Analysis
    st.subheader("🔄 Recurring Issue Analysis")
    recurring_issues, recurring_msg = calculate_recurring_issue_analysis(st.session_state.tickets_data)
    
    # Get all issue counts for display (not just recurring ones)
    if not st.session_state.tickets_data.empty:
        all_issue_counts = st.session_state.tickets_data.groupby('title').size().reset_index(name='occurrence_count')
        all_issue_counts = all_issue_counts.sort_values('occurrence_count', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = create_chart("bar", all_issue_counts.head(10), x='title', y='occurrence_count', 
                        title='Top Issues by Occurrence',
                        color='occurrence_count',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Issue Title", yaxis_title="Occurrence Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate summary metrics
            total_tickets = len(st.session_state.tickets_data)
            total_recurring = recurring_issues['occurrence_count'].sum() if not recurring_issues.empty else 0
            recurring_rate = (total_recurring / total_tickets) * 100 if total_tickets > 0 else 0
            unique_issues = len(all_issue_counts)
            recurring_issue_types = len(recurring_issues)
            
            st.metric("Recurring Issue Rate", f"{recurring_rate:.1f}%")
            st.metric("Total Tickets", total_tickets)
            st.metric("Unique Issue Types", unique_issues)
            st.metric("Recurring Issue Types", recurring_issue_types)
        
        st.info(f"📊 {recurring_msg}")
        display_dataframe_with_index_1(all_issue_counts.head(10))

def show_asset_management():
    """Display asset management analysis"""
    st.title("💻 Asset Management")
    
    if st.session_state.assets_data.empty:
        st.warning("⚠️ No asset data available. Please upload data first.")
        return
    
    # Asset Utilization
    st.subheader("📊 Asset Utilization")
    utilization_df, utilization_msg = calculate_asset_utilization(st.session_state.assets_data)
    
    if not utilization_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.pie(values=[utilization_df['utilized_assets'].iloc[0], utilization_df['inactive_assets'].iloc[0], utilization_df['maintenance_assets'].iloc[0]], 
                        names=['Active', 'Inactive', 'Maintenance'],
                        title='Asset Utilization Status')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Asset Utilization", f"{utilization_df['asset_utilization_percent'].iloc[0]:.1f}%")
            st.metric("Total Assets", utilization_df['total_it_assets'].iloc[0])
            st.metric("Active Assets", utilization_df['utilized_assets'].iloc[0])
        
        st.info(f"📊 {utilization_msg}")
        display_dataframe_with_index_1(utilization_df)
    
    st.markdown("---")
    
    # Hardware Lifecycle Analysis
    st.subheader("🔄 Hardware Lifecycle Analysis")
    lifecycle_df, lifecycle_msg = calculate_hardware_lifecycle_analysis(st.session_state.assets_data)
    
    if not lifecycle_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.scatter(lifecycle_df, x='age_years', y='depreciation_rate_percent', 
                           title='Asset Age vs Depreciation',
                           color='asset_type',
                           size='original_value',
                           hover_data=['asset_name'])
            fig.update_layout(xaxis_title="Age (Years)", yaxis_title="Depreciation Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Avg Depreciation", f"{lifecycle_df['depreciation_rate_percent'].mean():.1f}%")
            st.metric("Avg Asset Age", f"{lifecycle_df['age_years'].mean():.1f} years")
            st.metric("Total Asset Value", f"${lifecycle_df['original_value'].sum():,.0f}")
        
        st.info(f"📊 {lifecycle_msg}")
        display_dataframe_with_index_1(lifecycle_df.head(10))
    
    st.markdown("---")
    
    # Software Licensing Compliance
    st.subheader("📋 Software Licensing Compliance")
    if not st.session_state.applications_data.empty:
        compliance_df, compliance_msg = calculate_software_licensing_compliance(st.session_state.assets_data, st.session_state.applications_data)
        
        if not compliance_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.pie(values=[compliance_df['compliant_licenses'].iloc[0], compliance_df['non_compliant_licenses'].iloc[0]], 
                           names=['Compliant', 'Non-Compliant'],
                           title='Software Licensing Compliance')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Compliance Rate", f"{compliance_df['licensing_compliance_rate_percent'].iloc[0]:.1f}%")
                st.metric("Total Licenses", compliance_df['total_software_licenses'].iloc[0])
                st.metric("Compliant Licenses", compliance_df['compliant_licenses'].iloc[0])
            
            st.info(f"📊 {compliance_msg}")
            display_dataframe_with_index_1(compliance_df)
    
    st.markdown("---")
    
    # Cloud Resource Utilization
    st.subheader("☁️ Cloud Resource Utilization")
    if not st.session_state.servers_data.empty:
        cloud_df, cloud_msg = calculate_cloud_resource_utilization(st.session_state.assets_data, st.session_state.servers_data)
        
        if not cloud_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(x=['Cloud Utilization', 'Storage Utilization'], 
                           y=[cloud_df['cloud_utilization_percent'].iloc[0], cloud_df['storage_utilization_percent'].iloc[0]],
                           title='Cloud and Storage Utilization',
                           color=['Cloud', 'Storage'],
                           color_discrete_map={'Cloud': 'blue', 'Storage': 'green'})
                fig.update_layout(xaxis_title="Utilization Type", yaxis_title="Percentage (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Cloud Utilization", f"{cloud_df['cloud_utilization_percent'].iloc[0]:.1f}%")
                st.metric("Storage Utilization", f"{cloud_df['storage_utilization_percent'].iloc[0]:.1f}%")
                st.metric("Total Storage (TB)", f"{cloud_df['total_storage_tb'].iloc[0]:.1f}")
            
            st.info(f"📊 {cloud_msg}")
            display_dataframe_with_index_1(cloud_df)
    
    st.markdown("---")
    
    # Inventory Turnover
    st.subheader("📦 Inventory Turnover")
    turnover_df, turnover_msg = calculate_inventory_turnover(st.session_state.assets_data)
    
    if not turnover_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(x=['Purchases', 'Inventory Value'], 
                        y=[turnover_df['total_purchase_value'].iloc[0], turnover_df['average_inventory_value'].iloc[0]],
                        title='Asset Purchases vs Inventory Value',
                        color=['Purchases', 'Inventory'],
                        color_discrete_map={'Purchases': 'orange', 'Inventory': 'purple'})
            fig.update_layout(xaxis_title="Category", yaxis_title="Value ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Turnover Rate", f"{turnover_df['inventory_turnover_rate'].iloc[0]:.2f}")
            st.metric("Total Purchases", f"${turnover_df['total_purchase_value'].iloc[0]:,.0f}")
            st.metric("Avg Inventory Value", f"${turnover_df['average_inventory_value'].iloc[0]:,.0f}")
        
        st.info(f"📊 {turnover_msg}")
        display_dataframe_with_index_1(turnover_df)

def show_data_management():
    """Display data management and analytics"""
    st.title("📈 Data Management & Analytics")
    
    if st.session_state.applications_data.empty:
        st.warning("⚠️ No application data available. Please upload data first.")
        return
    
    # Data Quality Analysis
    st.subheader("🔍 Data Quality Analysis")
    if not st.session_state.backups_data.empty:
        quality_df, quality_msg = calculate_data_quality_analysis(st.session_state.applications_data, st.session_state.backups_data)
        
        if not quality_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.pie(values=[quality_df['valid_data_points'].iloc[0], quality_df['total_data_points'].iloc[0] - quality_df['valid_data_points'].iloc[0]], 
                           names=['Valid', 'Invalid'],
                           title='Data Quality Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Data Quality Rate", f"{quality_df['data_quality_rate_percent'].iloc[0]:.1f}%")
                st.metric("Valid Data Points", quality_df['valid_data_points'].iloc[0])
                st.metric("Total Data Points", quality_df['total_data_points'].iloc[0])
            
            st.info(f"📊 {quality_msg}")
            display_dataframe_with_index_1(quality_df)
    
    st.markdown("---")
    
    # Database Performance Metrics
    st.subheader("🗄️ Database Performance Metrics")
    if not st.session_state.servers_data.empty:
        perf_df, perf_msg = calculate_database_performance_metrics(st.session_state.servers_data, st.session_state.applications_data)
        
        if not perf_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(x=['Query Time', 'Index Efficiency'], 
                           y=[perf_df['avg_query_execution_time_ms'].iloc[0], perf_df['index_efficiency_percent'].iloc[0]],
                           title='Database Performance Metrics',
                           color=['Query', 'Index'],
                           color_discrete_map={'Query': 'blue', 'Index': 'green'})
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Avg Query Time", f"{perf_df['avg_query_execution_time_ms'].iloc[0]:.1f} ms")
                st.metric("Index Efficiency", f"{perf_df['index_efficiency_percent'].iloc[0]:.1f}%")
                st.metric("Total Databases", perf_df['total_databases'].iloc[0])
            
            st.info(f"📊 {perf_msg}")
            display_dataframe_with_index_1(perf_df)
    
    st.markdown("---")
    
    # Backup Success Rate
    st.subheader("💾 Backup Success Rate")
    if not st.session_state.backups_data.empty:
        backup_df, backup_msg = calculate_backup_success_rate(st.session_state.backups_data)
        
        if not backup_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.pie(values=[backup_df['successful_backups'].iloc[0], backup_df['failed_backups'].iloc[0]], 
                           names=['Successful', 'Failed'],
                           title='Backup Success Rate')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Backup Success Rate", f"{backup_df['backup_success_rate_percent'].iloc[0]:.1f}%")
                st.metric("Total Backups", backup_df['total_backups_attempted'].iloc[0])
                st.metric("Successful Backups", backup_df['successful_backups'].iloc[0])
            
            st.info(f"📊 {backup_msg}")
            display_dataframe_with_index_1(backup_df)
    
    st.markdown("---")
    
    # Data Loss Metrics
    st.subheader("📉 Data Loss Metrics")
    if not st.session_state.incidents_data.empty:
        loss_df, loss_msg = calculate_data_loss_metrics(st.session_state.incidents_data, st.session_state.backups_data)
        
        if not loss_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(x=['Data Loss Incidents', 'Backup Failures'], 
                           y=[loss_df['incident_data_loss'].iloc[0], loss_df['backup_failures'].iloc[0]],
                           title='Data Loss Analysis',
                           color=['Incidents', 'Backups'],
                           color_discrete_map={'Incidents': 'red', 'Backups': 'orange'})
                fig.update_layout(xaxis_title="Loss Type", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Data Loss Rate", f"{loss_df['data_loss_rate_percent'].iloc[0]:.3f}%")
                st.metric("Total Data Stored", loss_df['total_data_stored'].iloc[0])
                st.metric("Loss Incidents", loss_df['data_loss_incidents'].iloc[0])
            
            st.info(f"📊 {loss_msg}")
            display_dataframe_with_index_1(loss_df)
    
    st.markdown("---")
    
    # Storage Usage Trends
    st.subheader("📊 Storage Usage Trends")
    if not st.session_state.servers_data.empty:
        storage_df, storage_msg = calculate_storage_usage_trends(st.session_state.servers_data, st.session_state.backups_data)
        
        if not storage_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(x=['Current Usage', 'Backup Storage', 'Forecasted Need'], 
                           y=[storage_df['current_storage_used_tb'].iloc[0], storage_df['backup_storage_tb'].iloc[0], storage_df['forecasted_storage_requirement_tb'].iloc[0]],
                           title='Storage Usage Analysis',
                           color=['Current', 'Backup', 'Forecast'],
                           color_discrete_map={'Current': 'blue', 'Backup': 'green', 'Forecast': 'orange'})
                fig.update_layout(xaxis_title="Storage Type", yaxis_title="Storage (TB)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Storage Usage", f"{storage_df['storage_usage_trend_percent'].iloc[0]:.1f}%")
                st.metric("Current Usage (TB)", f"{storage_df['current_storage_used_tb'].iloc[0]:.1f}")
                st.metric("Forecasted Need (TB)", f"{storage_df['forecasted_storage_requirement_tb'].iloc[0]:.1f}")
            
            st.info(f"📊 {storage_msg}")
            display_dataframe_with_index_1(storage_df)

# Add placeholder functions for remaining pages
def show_project_management():
    """Display project management and development analysis"""
    st.title("📋 Project Management & Development")
    
    if st.session_state.projects_data.empty:
        st.warning("⚠️ No project data available. Please upload data first.")
        return
    
    # Project Delivery Metrics
    st.subheader("📊 Project Delivery Metrics")
    delivery_df, delivery_msg = calculate_project_delivery_metrics(st.session_state.projects_data)
    
    if not delivery_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create project status distribution from the actual data
            status_counts = st.session_state.projects_data['status'].value_counts()
            # Create data for the chart
            status_data = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values
            })
            
            fig = create_chart("bar", status_data, x='Status', y='Count', 
                        title='Project Status Distribution',
                        color='Status',
                        color_discrete_map={'Completed': 'green', 'In Progress': 'blue', 'Planning': 'orange', 'On Hold': 'red'})
            fig.update_layout(xaxis_title="Project Status", yaxis_title="Number of Projects")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Total Projects", delivery_df['total_projects'].iloc[0])
            st.metric("Completed Projects", delivery_df['completed_projects'].iloc[0])
            st.metric("On-Time Delivery", f"{delivery_df['on_time_delivery_percent'].iloc[0]:.1f}%")
            st.metric("Budget Adherence", f"{delivery_df['budget_adherence_percent'].iloc[0]:.1f}%")
        
        st.info(f"📊 {delivery_msg}")
        display_dataframe_with_index_1(delivery_df)
    
    st.markdown("---")
    
    # Development Cycle Time
    st.subheader("⏱️ Development Cycle Time")
    cycle_df, cycle_msg = calculate_development_cycle_time(st.session_state.projects_data)
    
    if not cycle_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create scatter plot from actual project data
            completed_projects = st.session_state.projects_data[st.session_state.projects_data['status'] == 'Completed']
            if not completed_projects.empty:
                fig = create_chart("scatter", completed_projects, x='budget', y='actual_cost', 
                               title='Budget vs Actual Cost',
                               color='status',
                               size='team_size',
                               hover_data=['project_name'])
                fig.update_layout(xaxis_title="Budget ($)", yaxis_title="Actual Cost ($)")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Avg Cycle Time", f"{cycle_df['avg_development_cycle_time_days'].iloc[0]:.1f} days")
            st.metric("Fastest Cycle", f"{cycle_df['fastest_cycle_days'].iloc[0]:.1f} days")
            st.metric("Slowest Cycle", f"{cycle_df['slowest_cycle_days'].iloc[0]:.1f} days")
        
        st.info(f"📊 {cycle_msg}")
        display_dataframe_with_index_1(cycle_df)
    
    st.markdown("---")
    
    # Code Quality Analysis
    st.subheader("🔍 Code Quality Analysis")
    quality_df, quality_msg = calculate_code_quality_analysis(st.session_state.projects_data)
    
    if not quality_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create quality metrics visualization from the actual data
            quality_metrics = {
                'Bug Density': quality_df['bugs_per_loc'].iloc[0],
                'Code Compliance': quality_df['coding_standard_compliance_percent'].iloc[0],
                'Total Bugs': quality_df['total_bugs'].iloc[0],
                'Lines of Code': quality_df['total_lines_of_code'].iloc[0]
            }
            
            # Create data for the chart
            quality_data = pd.DataFrame({
                'Metric': list(quality_metrics.keys()),
                'Value': list(quality_metrics.values())
            })
            
            fig = create_chart("bar", quality_data, x='Metric', y='Value', 
                        title='Code Quality Metrics',
                        color='Value',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Quality Metric", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Total Bugs", quality_df['total_bugs'].iloc[0])
            st.metric("Bugs per LOC", f"{quality_df['bugs_per_loc'].iloc[0]:.4f}")
            st.metric("Code Compliance", f"{quality_df['coding_standard_compliance_percent'].iloc[0]:.1f}%")
            st.metric("Total Lines of Code", f"{quality_df['total_lines_of_code'].iloc[0]:,.0f}")
        
        st.info(f"📊 {quality_msg}")
        display_dataframe_with_index_1(quality_df)
    
    st.markdown("---")
    
    # Release Management Metrics
    st.subheader("🚀 Release Management Metrics")
    release_df, release_msg = calculate_release_management_metrics(st.session_state.projects_data)
    
    if not release_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create release metrics visualization
            release_metrics = {
                'Deployment Success Rate': release_df['deployment_success_rate_percent'].iloc[0],
                'Rollback Rate': release_df['rollback_rate_percent'].iloc[0],
                'Total Deployments': release_df['total_deployments'].iloc[0]
            }
            
            # Create data for the chart
            release_data = pd.DataFrame({
                'Metric': list(release_metrics.keys()),
                'Value': list(release_metrics.values())
            })
            
            fig = create_chart("bar", release_data, x='Metric', y='Value',
                        title='Release Management Metrics',
                        color='Value',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Deployment Success Rate", f"{release_df['deployment_success_rate_percent'].iloc[0]:.1f}%")
            st.metric("Rollback Rate", f"{release_df['rollback_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total Deployments", release_df['total_deployments'].iloc[0])
        
        st.info(f"📊 {release_msg}")
        display_dataframe_with_index_1(release_df)
    
    st.markdown("---")
    
    # Agile Metrics
    st.subheader("🔄 Agile Metrics")
    agile_df, agile_msg = calculate_agile_metrics(st.session_state.projects_data)
    
    if not agile_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create agile metrics visualization
            agile_metrics = {
                'Sprint Velocity': agile_df['sprint_velocity'].iloc[0],
                'Burndown Rate': agile_df['burndown_rate_percent'].iloc[0],
                'Total Story Points': agile_df['total_story_points'].iloc[0]
            }
            
            # Create data for the chart
            agile_data = pd.DataFrame({
                'Metric': list(agile_metrics.keys()),
                'Value': list(agile_metrics.values())
            })
            
            fig = create_chart("bar", agile_data, x='Metric', y='Value',
                        title='Agile Metrics Overview',
                        color='Value',
                        color_continuous_scale='plasma')
            fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Sprint Velocity", f"{agile_df['sprint_velocity'].iloc[0]:.1f}")
            st.metric("Burndown Rate", f"{agile_df['burndown_rate_percent'].iloc[0]:.1f}%")
            st.metric("Total Story Points", agile_df['total_story_points'].iloc[0])
        
        st.info(f"📊 {agile_msg}")
        display_dataframe_with_index_1(agile_df)

def show_user_experience():
    """Display user experience and accessibility analysis"""
    st.title("👥 User Experience & Accessibility")
    
    if st.session_state.applications_data.empty or st.session_state.tickets_data.empty:
        st.warning("⚠️ No application or ticket data available. Please upload data first.")
        return
    
    # Application Usability Metrics
    st.subheader("📱 Application Usability Metrics")
    usability_df, usability_msg = calculate_application_usability_metrics(st.session_state.applications_data, st.session_state.tickets_data)
    
    if not usability_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create usability metrics visualization
            usability_metrics = {
                'Usability Score': usability_df['usability_score_percent'].iloc[0],
                'Avg Satisfaction': usability_df['avg_satisfaction_score'].iloc[0],
                'Satisfied Users': usability_df['satisfied_users'].iloc[0]
            }
            
            # Create data for the chart
            usability_data = pd.DataFrame({
                'Metric': list(usability_metrics.keys()),
                'Value': list(usability_metrics.values())
            })
            
            fig = create_chart("bar", usability_data, x='Metric', y='Value', 
                        title='Application Usability Metrics',
                        color='Value',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Usability Score", f"{usability_df['usability_score_percent'].iloc[0]:.1f}%")
            st.metric("Avg Satisfaction", f"{usability_df['avg_satisfaction_score'].iloc[0]:.1f}/5")
            st.metric("Satisfied Users", f"{usability_df['satisfied_users'].iloc[0]}/{usability_df['total_users_surveyed'].iloc[0]}")
        
        st.info(f"📊 {usability_msg}")
        display_dataframe_with_index_1(usability_df)
    
    st.markdown("---")
    
    # Website Performance Analysis
    st.subheader("🌐 Website Performance Analysis")
    if not st.session_state.applications_data.empty:
        web_df, web_msg = calculate_website_performance_analysis(st.session_state.applications_data, st.session_state.incidents_data)
        
        if not web_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create website performance visualization
                performance_metrics = {
                    'Avg Page Load Time': web_df['avg_page_load_time_seconds'].iloc[0],
                    'Mobile Traffic %': web_df['mobile_traffic_percentage'].iloc[0],
                    'Desktop Traffic %': web_df['desktop_traffic_percentage'].iloc[0]
                }
                
                # Create data for the chart
                performance_data = pd.DataFrame({
                    'Metric': list(performance_metrics.keys()),
                    'Value': list(performance_metrics.values())
                })
                
                fig = create_chart("bar", performance_data, x='Metric', y='Value', 
                            title='Website Performance Metrics',
                            color='Value',
                            color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Avg Page Load Time", f"{web_df['avg_page_load_time_seconds'].iloc[0]:.1f}s")
                st.metric("Mobile Traffic", f"{web_df['mobile_traffic_percentage'].iloc[0]:.1f}%")
                st.metric("Web Incidents", web_df['web_incidents'].iloc[0])
            
            st.info(f"📊 {web_msg}")
            display_dataframe_with_index_1(web_df)
    
    st.markdown("---")
    
    # Accessibility Compliance Analysis
    st.subheader("♿ Accessibility Compliance Analysis")
    if not st.session_state.applications_data.empty:
        accessibility_df, accessibility_msg = calculate_accessibility_compliance_analysis(st.session_state.applications_data)
        
        if not accessibility_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create data for the pie chart
                accessibility_data = pd.DataFrame({
                    'Status': ['Compliant Features', 'Non-Compliant Features'],
                    'Count': [accessibility_df['compliant_features'].iloc[0], accessibility_df['non_compliant_features'].iloc[0]]
                })
                
                fig = create_chart("pie", accessibility_data, values='Count', 
                           names='Status',
                           title='Accessibility Compliance Distribution',
                           color_discrete_map={'Compliant Features': 'green', 'Non-Compliant Features': 'red'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Compliance Rate", f"{accessibility_df['accessibility_compliance_rate_percent'].iloc[0]:.1f}%")
                st.metric("Compliant Features", accessibility_df['compliant_features'].iloc[0])
                st.metric("Non-Compliant Features", accessibility_df['non_compliant_features'].iloc[0])
            
            st.info(f"📊 {accessibility_msg}")
            display_dataframe_with_index_1(accessibility_df)
    
    st.markdown("---")
    
    # User Feedback Analysis
    st.subheader("💬 User Feedback Analysis")
    if not st.session_state.tickets_data.empty:
        feedback_df, feedback_msg = calculate_user_feedback_analysis(st.session_state.tickets_data)
        
        if not feedback_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create user feedback visualization
                feedback_metrics = {
                    'User Feedback Score': feedback_df['user_feedback_score_percent'].iloc[0],
                    'Avg Feedback Score': feedback_df['avg_feedback_score'].iloc[0],
                    'Positive Feedback': feedback_df['positive_feedback'].iloc[0]
                }
                
                # Create data for the chart
                feedback_data = pd.DataFrame({
                    'Metric': list(feedback_metrics.keys()),
                    'Value': list(feedback_metrics.values())
                })
                
                fig = create_chart("bar", feedback_data, x='Metric', y='Value', 
                            title='User Feedback Metrics',
                            color='Value',
                            color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("User Feedback Score", f"{feedback_df['user_feedback_score_percent'].iloc[0]:.1f}%")
                st.metric("Avg Feedback Score", f"{feedback_df['avg_feedback_score'].iloc[0]:.1f}/5")
                st.metric("Positive Feedback", f"{feedback_df['positive_feedback'].iloc[0]}/{feedback_df['total_feedback'].iloc[0]}")
            
            st.info(f"📊 {feedback_msg}")
            display_dataframe_with_index_1(feedback_df)

def show_cost_optimization():
    """Display cost and resource optimization analysis"""
    st.title("💰 Cost & Resource Optimization")
    
    if st.session_state.projects_data.empty and st.session_state.assets_data.empty:
        st.warning("⚠️ No project or asset data available. Please upload data first.")
        return
    
    # IT Budget Utilization
    st.subheader("💼 IT Budget Utilization")
    budget_df, budget_msg = calculate_it_budget_utilization(st.session_state.projects_data, st.session_state.assets_data)
    
    if not budget_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create budget utilization visualization
            budget_metrics = {
                'Budget Utilization': budget_df['budget_utilization_percent'].iloc[0],
                'Project Costs': budget_df['project_costs'].iloc[0],
                'Asset Costs': budget_df['asset_costs'].iloc[0]
            }
            
            # Create data for the chart
            budget_data = pd.DataFrame({
                'Category': list(budget_metrics.keys()),
                'Amount': list(budget_metrics.values())
            })
            
            fig = create_chart("bar", budget_data, x='Category', y='Amount', 
                        title='IT Budget Breakdown',
                        color='Amount',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Cost Category", yaxis_title="Amount ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Budget Utilization", f"{budget_df['budget_utilization_percent'].iloc[0]:.1f}%")
            st.metric("Actual Spending", f"${budget_df['actual_spending'].iloc[0]:,.0f}")
            st.metric("Budgeted Amount", f"${budget_df['budgeted_amount'].iloc[0]:,.0f}")
        
        st.info(f"📊 {budget_msg}")
        display_dataframe_with_index_1(budget_df)
    
    st.markdown("---")
    
    # Cost per User/Device Analysis
    st.subheader("👥 Cost per User/Device Analysis")
    if not st.session_state.assets_data.empty or not st.session_state.users_data.empty:
        cost_df, cost_msg = calculate_cost_per_user_device(st.session_state.assets_data, st.session_state.users_data)
        
        if not cost_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create cost per user/device visualization
                cost_metrics = {
                    'Cost per User': cost_df['cost_per_user'].iloc[0],
                    'Cost per Device': cost_df['cost_per_device'].iloc[0],
                    'Total IT Costs': cost_df['total_it_costs'].iloc[0]
                }
                
                # Create data for the chart
                cost_data = pd.DataFrame({
                    'Metric': list(cost_metrics.keys()),
                    'Amount': list(cost_metrics.values())
                })
                
                fig = create_chart("bar", cost_data, x='Metric', y='Amount', 
                            title='Cost Distribution Analysis',
                            color='Amount',
                            color_continuous_scale='plasma')
                fig.update_layout(xaxis_title="Cost Metric", yaxis_title="Amount ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Cost per User", f"${cost_df['cost_per_user'].iloc[0]:,.0f}")
                st.metric("Cost per Device", f"${cost_df['cost_per_device'].iloc[0]:,.0f}")
                st.metric("Total Users", cost_df['number_of_users'].iloc[0])
            
            st.info(f"📊 {cost_msg}")
            display_dataframe_with_index_1(cost_df)
    
    st.markdown("---")
    
    # Cloud Cost Analysis
    st.subheader("☁️ Cloud Cost Analysis")
    if not st.session_state.assets_data.empty or not st.session_state.servers_data.empty:
        cloud_df, cloud_msg = calculate_cloud_cost_analysis(st.session_state.assets_data, st.session_state.servers_data)
        
        if not cloud_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create cloud cost visualization
                cloud_metrics = {
                    'Cloud Cost Rate': cloud_df['cloud_cost_rate_percent'].iloc[0],
                    'Cloud Resources Cost': cloud_df['cloud_resources_cost'].iloc[0],
                    'Potential Savings': cloud_df['potential_savings'].iloc[0]
                }
                
                # Create data for the pie chart
                cloud_data = pd.DataFrame({
                    'Type': ['Cloud Costs', 'On-Premise Costs'],
                    'Amount': [cloud_df['cloud_resources_cost'].iloc[0], 
                              cloud_df['total_it_spending'].iloc[0] - cloud_df['cloud_resources_cost'].iloc[0]]
                })
                
                fig = create_chart("pie", cloud_data, values='Amount', 
                           names='Type',
                           title='Cloud vs On-Premise Cost Distribution',
                           color_discrete_map={'Cloud Costs': 'blue', 'On-Premise Costs': 'green'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Cloud Cost Rate", f"{cloud_df['cloud_cost_rate_percent'].iloc[0]:.1f}%")
                st.metric("Cloud Resources Cost", f"${cloud_df['cloud_resources_cost'].iloc[0]:,.0f}")
                st.metric("Potential Savings", f"${cloud_df['potential_savings'].iloc[0]:,.0f}")
            
            st.info(f"📊 {cloud_msg}")
            display_dataframe_with_index_1(cloud_df)
    
    st.markdown("---")
    
    # Energy Efficiency Analysis
    st.subheader("⚡ Energy Efficiency Analysis")
    if not st.session_state.servers_data.empty or not st.session_state.assets_data.empty:
        energy_df, energy_msg = calculate_energy_efficiency_analysis(st.session_state.servers_data, st.session_state.assets_data)
        
        if not energy_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create energy efficiency visualization
                energy_metrics = {
                    'Energy Efficiency': energy_df['energy_efficiency'].iloc[0],
                    'Total Energy Used': energy_df['total_energy_used'].iloc[0],
                    'Avg Energy per Operation': energy_df['avg_energy_per_operation'].iloc[0]
                }
                
                # Create data for the chart
                energy_data = pd.DataFrame({
                    'Metric': list(energy_metrics.keys()),
                    'Value': list(energy_metrics.values())
                })
                
                fig = create_chart("bar", energy_data, x='Metric', y='Value', 
                            title='Energy Efficiency Metrics',
                            color='Value',
                            color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Energy Efficiency", f"{energy_df['energy_efficiency'].iloc[0]:.1f}")
                st.metric("Total Energy Used", f"{energy_df['total_energy_used'].iloc[0]:.0f}")
                st.metric("Total IT Operations", energy_df['total_it_operations'].iloc[0])
            
            st.info(f"📊 {energy_msg}")
            display_dataframe_with_index_1(energy_df)

def show_strategy_innovation():
    """Display IT strategy and innovation analysis"""
    st.title("🚀 IT Strategy & Innovation")
    
    if st.session_state.applications_data.empty and st.session_state.users_data.empty:
        st.warning("⚠️ No application or user data available. Please upload data first.")
        return
    
    # Technology Adoption Metrics
    st.subheader("📱 Technology Adoption Metrics")
    adoption_df, adoption_msg = calculate_technology_adoption_metrics(st.session_state.applications_data, st.session_state.users_data)
    
    if not adoption_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create adoption metrics visualization
            adoption_metrics = {
                'Adoption Rate': adoption_df['adoption_rate_percent'].iloc[0],
                'Users Using New Tools': adoption_df['users_using_new_tools'].iloc[0],
                'New Applications': adoption_df['new_applications'].iloc[0]
            }
            
            adoption_data = pd.DataFrame({
                'Metric': list(adoption_metrics.keys()),
                'Value': list(adoption_metrics.values())
            })
            
            fig = create_chart("bar", adoption_data, x='Metric', y='Value',
                        title='Technology Adoption Overview',
                        color='Value',
                        color_continuous_scale='viridis')
            fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Adoption Rate", f"{adoption_df['adoption_rate_percent'].iloc[0]:.1f}%")
            st.metric("Users Using New Tools", f"{adoption_df['users_using_new_tools'].iloc[0]}/{adoption_df['total_users'].iloc[0]}")
            st.metric("New Applications", adoption_df['new_applications'].iloc[0])
        
        st.info(f"📊 {adoption_msg}")
        display_dataframe_with_index_1(adoption_df)
    
    st.markdown("---")
    
    # ROI on IT Investments
    st.subheader("💰 ROI on IT Investments")
    if not st.session_state.projects_data.empty or not st.session_state.assets_data.empty:
        roi_df, roi_msg = calculate_roi_on_it_investments(st.session_state.projects_data, st.session_state.assets_data)
        
        if not roi_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create ROI visualization
                roi_metrics = {
                    'ROI Percentage': roi_df['roi_percent'].iloc[0],
                    'Total Investment': roi_df['cost_of_it_investment'].iloc[0],
                    'Total Returns': roi_df['benefits_from_it_investment'].iloc[0]
                }
                
                roi_data = pd.DataFrame({
                    'Metric': list(roi_metrics.keys()),
                    'Value': list(roi_metrics.values())
                })
                
                fig = create_chart("bar", roi_data, x='Metric', y='Value',
                            title='IT Investment ROI Analysis',
                            color='Value',
                            color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("ROI Percentage", f"{roi_df['roi_percent'].iloc[0]:.1f}%")
                st.metric("Total Investment", f"${roi_df['cost_of_it_investment'].iloc[0]:,.0f}")
                st.metric("Total Returns", f"${roi_df['benefits_from_it_investment'].iloc[0]:,.0f}")
            
            st.info(f"📊 {roi_msg}")
            display_dataframe_with_index_1(roi_df)
    
    st.markdown("---")
    
    # Emerging Technology Feasibility
    st.subheader("🔮 Emerging Technology Feasibility")
    if not st.session_state.projects_data.empty:
        feasibility_df, feasibility_msg = calculate_emerging_technology_feasibility(st.session_state.projects_data)
        
        if not feasibility_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create feasibility visualization
                feasibility_metrics = {
                    'Feasibility Score': feasibility_df['feasibility_score_percent'].iloc[0],
                    'Technologies Assessed': feasibility_df['total_technologies_assessed'].iloc[0],
                    'Positive Impact': feasibility_df['technologies_with_positive_impact'].iloc[0]
                }
                
                feasibility_data = pd.DataFrame({
                    'Metric': list(feasibility_metrics.keys()),
                    'Value': list(feasibility_metrics.values())
                })
                
                fig = create_chart("bar", feasibility_data, x='Metric', y='Value',
                            title='Emerging Technology Assessment',
                            color='Value',
                            color_continuous_scale='plasma')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Feasibility Score", f"{feasibility_df['feasibility_score_percent'].iloc[0]:.1f}%")
                st.metric("Technologies Assessed", feasibility_df['total_technologies_assessed'].iloc[0])
                st.metric("Positive Impact", feasibility_df['technologies_with_positive_impact'].iloc[0])
            
            st.info(f"📊 {feasibility_msg}")
            display_dataframe_with_index_1(feasibility_df)
    
    st.markdown("---")
    
    # IT Alignment with Business Goals
    st.subheader("🎯 IT Alignment with Business Goals")
    if not st.session_state.projects_data.empty:
        alignment_df, alignment_msg = calculate_it_alignment_with_business_goals(st.session_state.projects_data)
        
        if not alignment_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create alignment visualization
                alignment_metrics = {
                    'Alignment Score': alignment_df['alignment_score_percent'].iloc[0],
                    'Aligned Initiatives': alignment_df['it_initiatives_aligned_with_business_goals'].iloc[0],
                    'Total Initiatives': alignment_df['total_it_initiatives'].iloc[0]
                }
                
                alignment_data = pd.DataFrame({
                    'Metric': list(alignment_metrics.keys()),
                    'Value': list(alignment_metrics.values())
                })
                
                fig = create_chart("bar", alignment_data, x='Metric', y='Value',
                            title='IT-Business Alignment Metrics',
                            color='Value',
                            color_continuous_scale='viridis')
                fig.update_layout(xaxis_title="Metric", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Alignment Score", f"{alignment_df['alignment_score_percent'].iloc[0]:.1f}%")
                st.metric("Aligned Initiatives", alignment_df['it_initiatives_aligned_with_business_goals'].iloc[0])
                st.metric("Total Initiatives", alignment_df['total_it_initiatives'].iloc[0])
            
            st.info(f"📊 {alignment_msg}")
            display_dataframe_with_index_1(alignment_df)

def show_training_development():
    """Display training and development analysis"""
    st.title("🎓 Training & Development")
    st.info("🚧 This section is under development. Training and development analytics will be available soon.")

def show_disaster_recovery():
    """Display disaster recovery and business continuity analysis"""
    st.title("🔄 Disaster Recovery & Business Continuity")
    st.info("🚧 This section is under development. Disaster recovery analytics will be available soon.")

def show_integration():
    """Display integration and interoperability analysis"""
    st.title("🔗 Integration & Interoperability")
    st.info("🚧 This section is under development. Integration analytics will be available soon.")

if __name__ == "__main__":
    main()
