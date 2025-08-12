import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime
import warnings
import importlib.util
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="AzIntelligence - Enterprise Analytics Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add department paths to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([
    os.path.join(current_dir, 'pro'),
    os.path.join(current_dir, 'cs'),
    os.path.join(current_dir, 'fin'),
    os.path.join(current_dir, 'hr'),
    os.path.join(current_dir, 'IT'),
    os.path.join(current_dir, 'marketing'),
    os.path.join(current_dir, 'RD'),
    os.path.join(current_dir, 'sale')
])

# Custom CSS for modern dashboard styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Modern Enterprise Dashboard Styling */
    .main .block-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        max-width: 100%;
    }
    
    /* Department card styling */
    .dept-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .dept-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        background: rgba(255, 255, 255, 1);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Navigation buttons */
    .nav-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px;
        display: inline-block;
        text-decoration: none;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Department icons */
    .dept-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        display: block;
    }
    
    /* Responsive grid */
    .dept-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background-color: #48bb78; }
    .status-warning { background-color: #ed8936; }
    .status-error { background-color: #f56565; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# Department information and navigation
DEPARTMENTS = {
    'procurement': {
        'name': 'Procurement & Supply Chain',
        'icon': '📦',
        'description': 'Supplier management, cost optimization, risk assessment',
        'color': '#667eea',
        'file': 'pro/pro.py',
        'module_name': 'pro'
    },
    'customer_support': {
        'name': 'Customer Support',
        'icon': '🎧',
        'description': 'Ticket management, customer satisfaction, agent performance',
        'color': '#764ba2',
        'file': 'cs/cs.py',
        'module_name': 'cs'
    },
    'finance': {
        'name': 'Finance & Accounting',
        'icon': '💰',
        'description': 'Financial analysis, budgeting, forecasting, risk management',
        'color': '#f093fb',
        'file': 'fin/fin.py',
        'module_name': 'fin'
    },
    'hr': {
        'name': 'Human Resources',
        'icon': '👥',
        'description': 'Employee analytics, performance management, workforce planning',
        'color': '#4facfe',
        'file': 'hr/hr.py',
        'module_name': 'hr'
    },
    'it': {
        'name': 'Information Technology',
        'icon': '💻',
        'description': 'IT infrastructure, system performance, cybersecurity',
        'color': '#43e97b',
        'file': 'IT/it.py',
        'module_name': 'it'
    },
    'marketing': {
        'name': 'Marketing & Analytics',
        'icon': '📊',
        'description': 'Campaign performance, customer acquisition, ROI analysis',
        'color': '#fa709a',
        'file': 'marketing/mark.py',
        'module_name': 'marketing'
    },
    'rd': {
        'name': 'Research & Development',
        'icon': '🔬',
        'description': 'Innovation metrics, project tracking, patent analysis',
        'color': '#ffecd2',
        'file': 'RD/rd.py',
        'module_name': 'rd'
    },
    'sales': {
        'name': 'Sales & Revenue',
        'icon': '📈',
        'description': 'Sales performance, pipeline analysis, forecasting',
        'color': '#a8edea',
        'file': 'sale/sale.py',
        'module_name': 'sale'
    }
}

def load_department_module(dept_key):
    """Load a department module dynamically"""
    try:
        dept_info = DEPARTMENTS.get(dept_key)
        if not dept_info:
            st.error(f"Department '{dept_key}' not found")
            return None
        
        module_path = os.path.join(current_dir, dept_info['file'])
        if not os.path.exists(module_path):
            st.error(f"Department file not found: {module_path}")
            return None
        
        # Load the module
        spec = importlib.util.spec_from_file_location(
            dept_info['module_name'], 
            module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
        
    except Exception as e:
        st.error(f"Error loading department module: {str(e)}")
        return None

def run_department_app(dept_key):
    """Run a specific department application"""
    try:
        module = load_department_module(dept_key)
        if not module:
            return False
        
        dept_info = DEPARTMENTS[dept_key]
        
        # Check if the module has a main function
        if hasattr(module, 'main') and callable(module.main):
            # Set session state to indicate which department is active
            st.session_state.active_department = dept_key
            st.session_state.department_name = dept_info['name']
            
            # Run the department's main function
            module.main()
            return True
        else:
            st.error(f"Main function not found in {dept_info['module_name']}")
            return False
            
    except Exception as e:
        st.error(f"Error running department application: {str(e)}")
        return False

def create_department_card(dept_key, dept_info):
    """Create a department card with a button"""
    st.markdown(f"""
    <div class="dept-card">
        <div class="dept-icon">{dept_info['icon']}</div>
        <h3 style="color: {dept_info['color']}; margin-bottom: 10px;">{dept_info['name']}</h3>
        <p style="color: #666; font-size: 14px;">{dept_info['description']}</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-active"></span>
            <span style="font-size: 12px; color: #48bb78;">Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a button below the card
    if st.button(f"🚀 Launch {dept_info['name']}", key=f"launch_{dept_key}", 
                 help=f"Click to open {dept_info['name']} application"):
        st.session_state.selected_department = dept_key
        st.rerun()

def display_overview_metrics():
    """Display overview metrics from all departments"""
    st.subheader("📊 Enterprise Overview")
    
    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>Total Departments</h4>
            <h2 style="color: #667eea;">8</h2>
            <p style="font-size: 12px; color: #666;">Active Systems</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>Data Sources</h4>
            <h2 style="color: #764ba2;">24+</h2>
            <p style="font-size: 12px; color: #666;">Excel Templates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>Analytics Tools</h4>
            <h2 style="color: #f093fb;">50+</h2>
            <p style="font-size: 12px; color: #666;">Metrics & KPIs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>AI Insights</h4>
            <h2 style="color: #4facfe;">100+</h2>
            <p style="font-size: 12px; color: #666;">Recommendations</p>
        </div>
        """, unsafe_allow_html=True)

def display_department_grid():
    """Display the grid of department cards"""
    st.subheader("🏢 Department Applications")
    
    # Create department grid
    st.markdown('<div class="dept-grid">', unsafe_allow_html=True)
    
    # Display departments in a grid layout
    cols = st.columns(2)
    for i, (dept_key, dept_info) in enumerate(DEPARTMENTS.items()):
        with cols[i % 2]:
            create_department_card(dept_key, dept_info)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_quick_actions():
    """Display quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View All Metrics", key="view_metrics"):
            st.session_state.show_metrics = True
    
    with col2:
        if st.button("📁 Upload Data", key="upload_data"):
            st.session_state.show_upload = True
    
    with col3:
        if st.button("🔍 Search Analytics", key="search_analytics"):
            st.session_state.show_search = True

def display_recent_activity():
    """Display recent activity across departments"""
    st.subheader("🕒 Recent Activity")
    
    # Sample recent activity data
    recent_activities = [
        {"department": "Sales", "action": "Data uploaded", "time": "2 minutes ago", "status": "success"},
        {"department": "Finance", "action": "Report generated", "time": "5 minutes ago", "status": "success"},
        {"department": "HR", "action": "Analytics updated", "time": "10 minutes ago", "status": "success"},
        {"department": "Procurement", "action": "Risk assessment", "time": "15 minutes ago", "status": "warning"},
        {"department": "Marketing", "action": "Campaign analysis", "time": "20 minutes ago", "status": "success"}
    ]
    
    for activity in recent_activities:
        status_color = "#48bb78" if activity["status"] == "success" else "#ed8936"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {status_color};">
            <strong>{activity['department']}</strong> - {activity['action']}
            <br><small style="color: #666;">{activity['time']}</small>
        </div>
        """, unsafe_allow_html=True)

def display_data_management_view():
    """Placeholder for Data Management view"""
    # Add back button
    if st.button("← Back to Main Dashboard", key="back_from_data_mgmt"):
        st.session_state.show_data_management = False
        st.rerun()
    
    st.subheader("📁 Data Management")
    st.info("This section is under construction. Please check back later for data management features.")
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">📂</div>
        <h3 style="color: #667eea; margin-bottom: 10px;">Data Upload</h3>
        <p style="color: #666; font-size: 14px;">Upload Excel files for analysis.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-active"></span>
            <span style="font-size: 12px; color: #48bb78;">Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">🔄</div>
        <h3 style="color: #764ba2; margin-bottom: 10px;">Data Integration</h3>
        <p style="color: #666; font-size: 14px;">Connect with various data sources.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-warning"></span>
            <span style="font-size: 12px; color: #ed8936;">Pending</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">💾</div>
        <h3 style="color: #f093fb; margin-bottom: 10px;">Data Storage</h3>
        <p style="color: #666; font-size: 14px;">Securely store and manage your data.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-active"></span>
            <span style="font-size: 12px; color: #48bb78;">Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">🔗</div>
        <h3 style="color: #4facfe; margin-bottom: 10px;">Data Pipelines</h3>
        <p style="color: #666; font-size: 14px;">Automate data ingestion and transformation.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-warning"></span>
            <span style="font-size: 12px; color: #ed8936;">Pending</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_settings_view():
    """Placeholder for Settings view"""
    # Add back button
    if st.button("← Back to Main Dashboard", key="back_from_settings"):
        st.session_state.show_settings = False
        st.rerun()
    
    st.subheader("⚙️ Settings")
    st.info("This section is under construction. Please check back later for settings features.")
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">⚙️</div>
        <h3 style="color: #4facfe; margin-bottom: 10px;">General Settings</h3>
        <p style="color: #666; font-size: 14px;">Configure application-wide settings.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-warning"></span>
            <span style="font-size: 12px; color: #ed8936;">Pending</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">🔑</div>
        <h3 style="color: #764ba2; margin-bottom: 10px;">User Authentication</h3>
        <p style="color: #666; font-size: 14px;">Manage user accounts and permissions.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-warning"></span>
            <span style="font-size: 12px; color: #ed8936;">Pending</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="dept-card">
        <div class="dept-icon">🔄</div>
        <h3 style="color: #667eea; margin-bottom: 10px;">Data Refresh</h3>
        <p style="color: #666; font-size: 14px;">Schedule data refresh for all departments.</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-warning"></span>
            <span style="font-size: 12px; color: #ed8936;">Pending</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    load_custom_css()
    
    # Check if a department is selected
    if 'selected_department' in st.session_state and st.session_state.selected_department:
        dept_key = st.session_state.selected_department
        dept_info = DEPARTMENTS[dept_key]
        
        # Show department header with back button
        st.markdown(f"""
        <div class="main-header">
            <h1>{dept_info['icon']} {dept_info['name']}</h1>
            <p>{dept_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add back button
        if st.button("← Back to Main Dashboard", key="back_to_main"):
            st.session_state.selected_department = None
            st.rerun()
        
        # Run the department application
        run_department_app(dept_key)
        
    else:
        # Show main dashboard
        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🏢 AzIntelligence</h1>
            <p>Enterprise Analytics Dashboard</p>
            <p style="font-size: 14px; opacity: 0.8;">Click on any department to access its full analytics suite</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for special views
        if st.session_state.get('show_data_management', False):
            display_data_management_view()
        elif st.session_state.get('show_settings', False):
            display_settings_view()
        else:
            # Show normal dashboard content
            # Overview metrics
            display_overview_metrics()
            
            # Department grid
            display_department_grid()
            
            # Quick actions
            display_quick_actions()
            
            # Recent activity
            display_recent_activity()
        
        # Footer
        st.markdown("""
        <div class="footer">
            <p>AzIntelligence | Enterprise Analytics Platform | Built with Streamlit</p>
            <p style="font-size: 12px; margin-top: 10px;">Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        with st.sidebar:
            st.title("🧭 Navigation")
            st.markdown("---")
            
            st.subheader("Departments")
            for dept_key, dept_info in DEPARTMENTS.items():
                if st.button(f"{dept_info['icon']} {dept_info['name']}", key=f"sidebar_{dept_key}", use_container_width=True):
                    st.session_state.selected_department = dept_key
                    st.rerun()
            
            st.markdown("---")
            
            # Developer credits in sidebar
            st.markdown("""
            <div style="text-align: center; padding: 20px 0; border-top: 1px solid rgba(255,255,255,0.2);">
                <p style="font-size: 14px; margin-bottom: 10px; color: #000000; font-weight: 500;">Developed by <strong style="color: #667eea;">Aryan Zabihi</strong></p>
                <div style="display: flex; justify-content: center; gap: 15px;">
                    <a href="https://github.com/aryanzabihi" target="_blank" style="color: #000000; text-decoration: none; display: flex; align-items: center; gap: 3px; font-size: 12px; padding: 5px 10px; background: rgba(255,255,255,0.15); border-radius: 5px; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.2);">
                        <span style="font-size: 14px;">🐙</span> GitHub
                    </a>
                    <a href="https://linkedin.com/in/aryanzabihi" target="_blank" style="color: #000000; text-decoration: none; display: flex; align-items: center; gap: 3px; font-size: 12px; padding: 5px 10px; background: rgba(255,255,255,0.15); border-radius: 5px; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.2);">
                        <span style="font-size: 14px;">💼</span> LinkedIn
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
