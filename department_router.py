import streamlit as st
import os
import sys
import importlib.util
from typing import Dict, Any, Optional
import pandas as pd

class DepartmentRouter:
    """Handles routing and integration between different department applications"""
    
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.departments = {
            'procurement': {
                'name': 'Procurement & Supply Chain',
                'icon': '📦',
                'description': 'Supplier management, cost optimization, risk assessment',
                'color': '#667eea',
                'file': 'pro/pro.py',
                'module_name': 'pro',
                'main_function': 'main'
            },
            'customer_support': {
                'name': 'Customer Support',
                'icon': '🎧',
                'description': 'Ticket management, customer satisfaction, agent performance',
                'color': '#764ba2',
                'file': 'cs/cs.py',
                'module_name': 'cs',
                'main_function': 'main'
            },
            'finance': {
                'name': 'Finance & Accounting',
                'icon': '💰',
                'description': 'Financial analysis, budgeting, forecasting, risk management',
                'color': '#f093fb',
                'file': 'fin/fin.py',
                'module_name': 'fin',
                'main_function': 'main'
            },
            'hr': {
                'name': 'Human Resources',
                'icon': '👥',
                'description': 'Employee analytics, performance management, workforce planning',
                'color': '#4facfe',
                'file': 'hr/hr.py',
                'module_name': 'hr',
                'main_function': 'main'
            },
            'it': {
                'name': 'Information Technology',
                'icon': '💻',
                'description': 'IT infrastructure, system performance, cybersecurity',
                'color': '#43e97b',
                'file': 'IT/it.py',
                'module_name': 'it',
                'main_function': 'main'
            },
            'marketing': {
                'name': 'Marketing & Analytics',
                'icon': '📊',
                'description': 'Campaign performance, customer acquisition, ROI analysis',
                'color': '#fa709a',
                'file': 'marketing/mark.py',
                'module_name': 'marketing',
                'main_function': 'main'
            },
            'rd': {
                'name': 'Research & Development',
                'icon': '🔬',
                'description': 'Innovation metrics, project tracking, patent analysis',
                'color': '#ffecd2',
                'file': 'RD/rd.py',
                'module_name': 'rd',
                'main_function': 'main'
            },
            'sales': {
                'name': 'Sales & Revenue',
                'icon': '📈',
                'description': 'Sales performance, pipeline analysis, forecasting',
                'color': '#a8edea',
                'file': 'sale/sale.py',
                'module_name': 'sale',
                'main_function': 'main'
            }
        }
        
        # Add department paths to system path
        for dept_info in self.departments.values():
            dept_path = os.path.join(self.current_dir, dept_info['module_name'])
            if dept_path not in sys.path:
                sys.path.append(dept_path)
    
    def get_department_info(self, dept_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific department"""
        return self.departments.get(dept_key)
    
    def get_all_departments(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all departments"""
        return self.departments
    
    def load_department_module(self, dept_key: str) -> Optional[Any]:
        """Load a department module dynamically"""
        try:
            dept_info = self.departments.get(dept_key)
            if not dept_info:
                st.error(f"Department '{dept_key}' not found")
                return None
            
            module_path = os.path.join(self.current_dir, dept_info['file'])
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
    
    def run_department_app(self, dept_key: str) -> bool:
        """Run a specific department application"""
        try:
            module = self.load_department_module(dept_key)
            if not module:
                return False
            
            dept_info = self.departments[dept_key]
            main_function = getattr(module, dept_info['main_function'], None)
            
            if main_function and callable(main_function):
                # Set session state to indicate which department is active
                st.session_state.active_department = dept_key
                st.session_state.department_name = dept_info['name']
                
                # Run the department's main function
                main_function()
                return True
            else:
                st.error(f"Main function '{dept_info['main_function']}' not found in {dept_info['module_name']}")
                return False
                
        except Exception as e:
            st.error(f"Error running department application: {str(e)}")
            return False
    
    def create_department_navigation(self):
        """Create navigation buttons for all departments"""
        st.sidebar.title("🏢 Department Navigation")
        st.sidebar.markdown("---")
        
        # Add main dashboard button
        if st.sidebar.button("🏠 Main Dashboard", key="nav_main"):
            st.session_state.active_department = None
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Add department buttons
        for dept_key, dept_info in self.departments.items():
            if st.sidebar.button(
                f"{dept_info['icon']} {dept_info['name']}", 
                key=f"nav_{dept_key}"
            ):
                st.session_state.active_department = dept_key
                st.rerun()
        
        st.sidebar.markdown("---")
        
        # Add quick actions
        st.sidebar.subheader("⚡ Quick Actions")
        if st.sidebar.button("📊 Cross-Department View"):
            st.session_state.show_cross_dept = True
        
        if st.sidebar.button("📁 Data Management"):
            st.session_state.show_data_mgmt = True
        
        if st.sidebar.button("⚙️ Settings"):
            st.session_state.show_settings = True
    
    def get_department_status(self, dept_key: str) -> str:
        """Get the status of a department (active, inactive, error)"""
        try:
            dept_info = self.departments[dept_key]
            module_path = os.path.join(self.current_dir, dept_info['file'])
            
            if not os.path.exists(module_path):
                return "error"
            
            # Try to load the module to check if it's working
            module = self.load_department_module(dept_key)
            if module:
                return "active"
            else:
                return "warning"
                
        except Exception:
            return "error"
    
    def create_department_overview(self):
        """Create an overview of all departments with their status"""
        st.subheader("🏢 Department Status Overview")
        
        # Create status grid
        cols = st.columns(2)
        for i, (dept_key, dept_info) in enumerate(self.departments.items()):
            with cols[i % 2]:
                status = self.get_department_status(dept_key)
                
                # Status color mapping
                status_colors = {
                    'active': '#48bb78',
                    'warning': '#ed8936',
                    'error': '#f56565'
                }
                
                status_text = {
                    'active': '🟢 Active',
                    'warning': '🟡 Warning',
                    'error': '🔴 Error'
                }
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {status_colors[status]};">
                    <h4 style="margin: 0 0 10px 0;">{dept_info['icon']} {dept_info['name']}</h4>
                    <p style="font-size: 12px; color: #666; margin: 0 0 10px 0;">{dept_info['description']}</p>
                    <span style="color: {status_colors[status]}; font-weight: 600;">{status_text[status]}</span>
                </div>
                """, unsafe_allow_html=True)
    
    def create_cross_department_view(self):
        """Create a view that shows data from multiple departments"""
        st.subheader("🔗 Cross-Department Analytics")
        
        # This would integrate data from multiple departments
        # For now, show a placeholder
        st.info("Cross-department analytics view will be implemented here")
        
        # Example: Show which departments have data loaded
        if 'department_data' in st.session_state:
            st.write("Data loaded from departments:")
            for dept, data in st.session_state.department_data.items():
                if data is not None and not data.empty:
                    st.write(f"- {dept}: {data.shape[0]} rows")
    
    def create_data_management_view(self):
        """Create a unified data management view"""
        st.subheader("📁 Unified Data Management")
        
        # File upload for any department
        uploaded_file = st.file_uploader(
            "Upload data file",
            type=['xlsx', 'csv'],
            help="Upload data for any department"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                
                st.success(f"File uploaded successfully: {uploaded_file.name}")
                st.info(f"Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
                
                # Store in session state
                if 'uploaded_data' not in st.session_state:
                    st.session_state.uploaded_data = {}
                
                st.session_state.uploaded_data[uploaded_file.name] = df
                
                # Show data preview
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    def create_settings_view(self):
        """Create a settings view for the integrated dashboard"""
        st.subheader("⚙️ Dashboard Settings")
        
        # Theme selection
        theme = st.selectbox(
            "Select Theme",
            ["Default", "Dark", "Light", "Corporate"],
            index=0
        )
        
        # Layout options
        layout = st.selectbox(
            "Select Layout",
            ["Wide", "Centered", "Compact"],
            index=0
        )
        
        # Auto-refresh settings
        auto_refresh = st.checkbox("Enable Auto-refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh Interval (seconds)", 30, 300, 60)
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.session_state.dashboard_theme = theme
            st.session_state.dashboard_layout = layout
            st.session_state.auto_refresh = auto_refresh
            if auto_refresh:
                st.session_state.refresh_interval = refresh_interval
            
            st.success("Settings saved successfully!")
    
    def handle_navigation(self):
        """Main navigation handler"""
        # Check if a department is selected
        if 'active_department' in st.session_state and st.session_state.active_department:
            dept_key = st.session_state.active_department
            dept_info = self.departments[dept_key]
            
            # Show department header
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {dept_info['color']} 0%, #2d3748 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                <h1>{dept_info['icon']} {dept_info['name']}</h1>
                <p>{dept_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add back button
            if st.button("← Back to Main Dashboard"):
                st.session_state.active_department = None
                st.rerun()
            
            # Run the department application
            self.run_department_app(dept_key)
            
        else:
            # Show main dashboard
            self.create_department_overview()
            
            # Check for other views
            if st.session_state.get('show_cross_dept', False):
                self.create_cross_department_view()
                st.session_state.show_cross_dept = False
            
            if st.session_state.get('show_data_mgmt', False):
                self.create_data_management_view()
                st.session_state.show_data_mgmt = False
            
            if st.session_state.get('show_settings', False):
                self.create_settings_view()
                st.session_state.show_settings = False

# Global router instance
router = DepartmentRouter()

def main():
    """Main function for the integrated dashboard"""
    st.set_page_config(
        page_title="Enterprise Analytics Dashboard",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'active_department' not in st.session_state:
        st.session_state.active_department = None
    
    # Create navigation
    router.create_department_navigation()
    
    # Handle navigation
    router.handle_navigation()

if __name__ == "__main__":
    main()
