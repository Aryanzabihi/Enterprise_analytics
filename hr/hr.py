import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import base64
import warnings
warnings.filterwarnings('ignore')

def display_formatted_recommendations(recommendations_list):
    """
    Display recommendations with proper formatting using HTML to ensure bullet points are on separate lines.
    """
    if not recommendations_list:
        return
    
    # Convert list of recommendations to HTML format
    html_content = "<ul>"
    for rec in recommendations_list:
        if rec.strip():
            # Remove bullet point if present and clean up
            clean_rec = rec.strip()
            if clean_rec.startswith("•"):
                clean_rec = clean_rec[1:].strip()
            html_content += f"<li>{clean_rec}</li>"
    html_content += "</ul>"
    
    # Display using HTML
    st.markdown(html_content, unsafe_allow_html=True)

# Plotly imports for charts
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Machine Learning imports
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import time

# Import HR metric calculation functions
from hr_metrics_calculator import *

# Import auto insights functionality
from hr_auto_insights import HRAutoInsights, display_hr_insights_section

# Risk analysis functionality is now integrated directly in the main file

# Import predictive analytics functionality
from hr_predictive_analytics import display_predictive_analytics_dashboard

# Import enhanced analytics based on book concepts
from hr_enhanced_analytics import display_enhanced_analytics_dashboard

# Set Plotly template
pio.templates.default = "plotly_white"
CONTINUOUS_COLOR_SCALE = "Turbo"
CATEGORICAL_COLOR_SEQUENCE = px.colors.qualitative.Pastel

# --- PuLP import for optimization ---
try:
    from pulp import LpProblem, LpVariable, LpMaximize, lpSum
except ImportError:
    LpProblem = LpVariable = LpMaximize = lpSum = None

# --- Utility Functions: Variable Detection ---
def get_numeric_columns(df):
    """Return a list of numeric columns, excluding 'employee'."""
    return [col for col in df.select_dtypes(include=['number']).columns if col != 'employee']

def get_categorical_columns(df):
    """Return a list of categorical/object columns, excluding 'employee'."""
    return [col for col in df.select_dtypes(include=['object']).columns if col != 'employee']

# --- Utility Functions ---
def calculate_hr_risk_assessment(df):
    """Calculate comprehensive HR risk assessment for each employee."""
    df = df.copy()
    
    if df.empty:
        return df
    
    # 1. Turnover Risk Assessment
    if 'tenure_days' in df.columns:
        # High risk: < 1 year, Medium risk: 1-3 years, Low risk: > 3 years
        df['turnover_risk'] = pd.cut(
            df['tenure_days'],
            bins=[0, 365, 1095, float('inf')],
            labels=['High', 'Medium', 'Low'],
            include_lowest=True
        )
        df['turnover_risk_score'] = df['turnover_risk'].map({'High': 3, 'Medium': 2, 'Low': 1})
    
    # 2. Performance Risk Assessment
    if 'performance_rating' in df.columns:
        # High risk: < 3.0, Medium risk: 3.0-3.5, Low risk: > 3.5
        df['performance_risk'] = pd.cut(
            df['performance_rating'],
            bins=[0, 3.0, 3.5, 5.0],
            labels=['High', 'Medium', 'Low'],
            include_lowest=True
        )
        df['performance_risk_score'] = df['performance_risk'].map({'High': 3, 'Medium': 2, 'Low': 1})
    
    # 3. Compensation Risk Assessment
    if 'salary' in df.columns:
        salary_mean = df['salary'].mean()
        salary_std = df['salary'].std()
        
        # High risk: > 2 std dev from mean, Medium risk: 1-2 std dev, Low risk: < 1 std dev
        salary_z_score = abs((df['salary'] - salary_mean) / salary_std)
        df['compensation_risk'] = pd.cut(
            salary_z_score,
            bins=[0, 1, 2, float('inf')],
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        df['compensation_risk_score'] = df['compensation_risk'].map({'Low': 1, 'Medium': 2, 'High': 3})
    
    # 4. Age Risk Assessment
    if 'age' in df.columns:
        # High risk: > 60 (retirement risk), Medium risk: 50-60, Low risk: < 50
        df['age_risk'] = pd.cut(
            df['age'],
            bins=[0, 50, 60, 100],
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        df['age_risk_score'] = df['age_risk'].map({'Low': 1, 'Medium': 2, 'High': 3})
    
    # 5. Department Concentration Risk
    if 'department' in df.columns:
        dept_counts = df['department'].value_counts()
        total_employees = len(df)
        dept_risk = {}
        
        for dept in dept_counts.index:
            dept_size = dept_counts[dept]
            concentration = dept_size / total_employees
            
            if concentration > 0.3:  # > 30% of workforce
                dept_risk[dept] = 'High'
            elif concentration > 0.15:  # > 15% of workforce
                dept_risk[dept] = 'Medium'
            else:
                dept_risk[dept] = 'Low'
        
        df['department_risk'] = df['department'].map(dept_risk)
        df['department_risk_score'] = df['department_risk'].map({'Low': 1, 'Medium': 2, 'High': 3})
    
    # 6. Calculate Overall Risk Score
    risk_columns = [col for col in df.columns if col.endswith('_risk_score')]
    if risk_columns:
        df['overall_risk_score'] = df[risk_columns].mean(axis=1)
        
        # Categorize overall risk
        df['overall_risk_level'] = pd.cut(
            df['overall_risk_score'],
            bins=[0, 1.5, 2.5, 3.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk'],
            include_lowest=True
        )
    
    return df

def get_variable_list(df):
    """Return a list of numeric variables for scoring, excluding employee/name/id columns."""
    return [
        col for col in df.columns
        if col.lower() not in ['employee', 'name', 'id', 'first_name', 'last_name', 'email']
        and pd.api.types.is_numeric_dtype(df[col])
        and not df[col].isnull().all()
    ]

def normalize_column(col, minimize=False):
    """Normalize a column to 0-1 scale."""
    if col.min() == col.max():
        return pd.Series(0.5, index=col.index)
    if minimize:
        return (col.max() - col) / (col.max() - col.min())
    else:
        return (col - col.min()) / (col.max() - col.min())

def get_weights(variables, scenario):
    """Get weights for different HR scenarios."""
    if scenario == "balanced":
        return {var: 1.0/len(variables) for var in variables}
    elif scenario == "performance_focused":
        weights = {var: 0.1 for var in variables}
        if 'performance_rating' in variables:
            weights['performance_rating'] = 0.4
        if 'productivity_score' in variables:
            weights['productivity_score'] = 0.3
        return weights
    elif scenario == "retention_focused":
        weights = {var: 0.1 for var in variables}
        if 'tenure_days' in variables:
            weights['tenure_days'] = 0.3
        if 'engagement_score' in variables:
            weights['engagement_score'] = 0.3
        return weights
    else:
        return {var: 1.0/len(variables) for var in variables}

def apply_common_layout(fig):
    """Apply common layout settings to Plotly figures."""
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
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

def safe_text(text):
    """Safely encode text for display."""
    if isinstance(text, str):
        return text
    return str(text)

def truncate_col(text, max_len=20):
    """Truncate text for display."""
    if isinstance(text, str) and len(text) > max_len:
        return text[:max_len-3] + "..."
    return str(text)

def get_filtered_hr_df():
    """Get filtered HR data based on selected year and quarter."""
    employees_df = st.session_state.employees.copy()
    if not employees_df.empty and 'hire_date' in employees_df.columns:
        employees_df['hire_date'] = pd.to_datetime(employees_df['hire_date'], errors='coerce')
        employees_df = employees_df.dropna(subset=['hire_date'])
        employees_df['year'] = employees_df['hire_date'].dt.year
        employees_df['quarter'] = employees_df['hire_date'].dt.quarter
        
        if 'selected_year' in st.session_state and st.session_state.selected_year:
            employees_df = employees_df[employees_df['year'] == st.session_state.selected_year]
        
        if 'selected_quarter' in st.session_state and st.session_state.selected_quarter != 'All':
            quarter_num = int(st.session_state.selected_quarter[1])
            employees_df = employees_df[employees_df['quarter'] == quarter_num]
    
    return employees_df

def load_custom_css():
    """Load custom CSS for professional styling."""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        text-align: center;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card h3 {
        color: white;
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .metric-card p {
        color: white;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .welcome-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .welcome-section h2 {
        color: white !important;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .welcome-section p {
        color: white;
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_template_for_download():
    """Create an Excel template with all required HR data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct HR schema
    employees_template = pd.DataFrame(columns=[
        'employee_id', 'first_name', 'last_name', 'email', 'hire_date', 'department', 
        'job_title', 'salary', 'manager_id', 'location', 'gender', 'age', 'ethnicity',
        'education_level', 'performance_rating', 'tenure_days', 'status'
    ])
    
    recruitment_template = pd.DataFrame(columns=[
        'job_posting_id', 'position_title', 'department', 'posting_date', 'closing_date',
        'applications_received', 'candidates_interviewed', 'offers_made', 'hires_made',
        'recruitment_source', 'recruitment_cost', 'time_to_hire_days'
    ])
    
    performance_template = pd.DataFrame(columns=[
        'review_id', 'employee_id', 'review_date', 'reviewer_id', 'performance_rating',
        'goal_achievement_rate', 'productivity_score', 'skills_assessment', 'review_cycle'
    ])
    
    compensation_template = pd.DataFrame(columns=[
        'compensation_id', 'employee_id', 'effective_date', 'base_salary', 'bonus_amount',
        'benefits_value', 'total_compensation', 'pay_grade', 'compensation_reason'
    ])
    
    training_template = pd.DataFrame(columns=[
        'training_id', 'employee_id', 'training_program', 'start_date', 'completion_date',
        'training_cost', 'skills_improvement', 'performance_impact', 'training_type'
    ])
    
    engagement_template = pd.DataFrame(columns=[
        'survey_id', 'employee_id', 'survey_date', 'engagement_score', 'satisfaction_score',
        'work_life_balance_score', 'recommendation_score', 'survey_type'
    ])
    
    turnover_template = pd.DataFrame(columns=[
        'turnover_id', 'employee_id', 'separation_date', 'separation_reason', 'turnover_reason_detail', 'exit_interview_score',
        'rehire_eligibility', 'knowledge_transfer_completed', 'replacement_hired', 'turnover_cost', 'notice_period_days'
    ])
    
    benefits_template = pd.DataFrame(columns=[
        'benefit_id', 'employee_id', 'benefit_type', 'enrollment_date', 'utilization_rate',
        'benefit_cost', 'provider', 'coverage_level'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        employees_template.to_excel(writer, sheet_name='Employees', index=False)
        recruitment_template.to_excel(writer, sheet_name='Recruitment', index=False)
        performance_template.to_excel(writer, sheet_name='Performance', index=False)
        compensation_template.to_excel(writer, sheet_name='Compensation', index=False)
        training_template.to_excel(writer, sheet_name='Training', index=False)
        engagement_template.to_excel(writer, sheet_name='Engagement', index=False)
        turnover_template.to_excel(writer, sheet_name='Turnover', index=False)
        benefits_template.to_excel(writer, sheet_name='Benefits', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Employees', 'Recruitment', 'Performance', 'Compensation', 'Training', 'Engagement', 'Turnover', 'Benefits'],
            'Required Fields': [
                'employee_id, first_name, last_name, email, hire_date, department, job_title, salary, manager_id, location, gender, age, ethnicity, education_level, performance_rating, tenure_days, status',
                'job_posting_id, position_title, department, posting_date, closing_date, applications_received, candidates_interviewed, offers_made, hires_made, recruitment_source, recruitment_cost, time_to_hire_days',
                'review_id, employee_id, review_date, reviewer_id, performance_rating, goal_achievement_rate, productivity_score, skills_assessment, review_cycle',
                'compensation_id, employee_id, effective_date, base_salary, bonus_amount, benefits_value, total_compensation, pay_grade, compensation_reason',
                'training_id, employee_id, training_program, start_date, completion_date, training_cost, skills_improvement, performance_impact, training_type',
                'survey_id, employee_id, survey_date, engagement_score, satisfaction_score, work_life_balance_score, recommendation_score, survey_type',
                'turnover_id, employee_id, separation_date, separation_reason, turnover_reason_detail, exit_interview_score, rehire_eligibility, knowledge_transfer_completed, replacement_hired, turnover_cost, notice_period_days',
                'benefit_id, employee_id, benefit_type, enrollment_date, utilization_rate, benefit_cost, provider, coverage_level'
            ],
            'Data Types': [
                'Text, Text, Text, Text, Date, Text, Text, Number, Text, Text, Text, Number, Text, Text, Number, Number, Text',
                'Text, Text, Text, Date, Date, Number, Number, Number, Number, Text, Number, Number',
                'Text, Text, Date, Text, Number, Number, Number, Number, Text',
                'Text, Text, Date, Number, Number, Number, Number, Text, Text',
                'Text, Text, Text, Date, Date, Number, Number, Number, Text',
                'Text, Text, Date, Number, Number, Number, Number, Text',
                'Text, Text, Date, Text, Text, Number, Text, Text, Text, Number, Number',
                'Text, Text, Text, Date, Number, Number, Text, Text'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
    
    # Prepare for download
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    
    # Create download link
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="hr_data_template.xlsx">📥 Download HR Data Template</a>'
    st.markdown(href, unsafe_allow_html=True)

def export_data_to_excel():
    """Exports all HR data from session state to a single Excel file."""
    with pd.ExcelWriter('hr_data_export.xlsx', engine='xlsxwriter') as writer:
        if not st.session_state.employees.empty:
            st.session_state.employees.to_excel(writer, sheet_name='Employees', index=False)
        if not st.session_state.recruitment.empty:
            st.session_state.recruitment.to_excel(writer, sheet_name='Recruitment', index=False)
        if not st.session_state.performance.empty:
            st.session_state.performance.to_excel(writer, sheet_name='Performance', index=False)
        if not st.session_state.compensation.empty:
            st.session_state.compensation.to_excel(writer, sheet_name='Compensation', index=False)
        if not st.session_state.training.empty:
            st.session_state.training.to_excel(writer, sheet_name='Training', index=False)
        if not st.session_state.engagement.empty:
            st.session_state.engagement.to_excel(writer, sheet_name='Engagement', index=False)
        if not st.session_state.turnover.empty:
            st.session_state.turnover.to_excel(writer, sheet_name='Turnover', index=False)
        if not st.session_state.benefits.empty:
            st.session_state.benefits.to_excel(writer, sheet_name='Benefits', index=False)
        
        st.success("HR data exported successfully as 'hr_data_export.xlsx'")

# Page configuration
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .formula-box {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for HR data storage
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame(columns=[
        'employee_id', 'first_name', 'last_name', 'email', 'hire_date', 'department', 
        'job_title', 'salary', 'manager_id', 'location', 'gender', 'age', 'ethnicity',
        'education_level', 'performance_rating', 'tenure_days', 'status'
    ])

if 'recruitment' not in st.session_state:
    st.session_state.recruitment = pd.DataFrame(columns=[
        'job_posting_id', 'position_title', 'department', 'posting_date', 'closing_date',
        'applications_received', 'candidates_interviewed', 'offers_made', 'hires_made',
        'recruitment_source', 'recruitment_cost', 'time_to_hire_days'
    ])

if 'performance' not in st.session_state:
    st.session_state.performance = pd.DataFrame(columns=[
        'review_id', 'employee_id', 'review_date', 'reviewer_id', 'performance_rating',
        'goal_achievement_rate', 'productivity_score', 'skills_assessment', 'review_cycle'
    ])

if 'compensation' not in st.session_state:
    st.session_state.compensation = pd.DataFrame(columns=[
        'compensation_id', 'employee_id', 'effective_date', 'base_salary', 'bonus_amount',
        'benefits_value', 'total_compensation', 'pay_grade', 'compensation_reason'
    ])

if 'training' not in st.session_state:
    st.session_state.training = pd.DataFrame(columns=[
        'training_id', 'employee_id', 'training_program', 'start_date', 'completion_date',
        'training_cost', 'skills_improvement', 'performance_impact', 'training_type'
    ])

if 'engagement' not in st.session_state:
    st.session_state.engagement = pd.DataFrame(columns=[
        'survey_id', 'employee_id', 'survey_date', 'engagement_score', 'satisfaction_score',
        'work_life_balance_score', 'recommendation_score', 'survey_type'
    ])

if 'turnover' not in st.session_state:
            st.session_state.turnover = pd.DataFrame(columns=[
            'turnover_id', 'employee_id', 'separation_date', 'separation_reason', 'turnover_reason_detail', 'exit_interview_score',
            'rehire_eligibility', 'knowledge_transfer_completed', 'replacement_hired', 'turnover_cost', 'notice_period_days'
        ])

if 'benefits' not in st.session_state:
    st.session_state.benefits = pd.DataFrame(columns=[
        'benefit_id', 'employee_id', 'benefit_type', 'enrollment_date', 'utilization_rate',
        'benefit_cost', 'provider', 'coverage_level'
    ])

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="HR Analytics Dashboard",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">👥 HR Analytics Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'employees' not in st.session_state:
        st.session_state.employees = pd.DataFrame()
    if 'recruitment' not in st.session_state:
        st.session_state.recruitment = pd.DataFrame()
    if 'performance' not in st.session_state:
        st.session_state.performance = pd.DataFrame()
    if 'compensation' not in st.session_state:
        st.session_state.compensation = pd.DataFrame()
    if 'training' not in st.session_state:
        st.session_state.training = pd.DataFrame()
    if 'engagement' not in st.session_state:
        st.session_state.engagement = pd.DataFrame()
    if 'turnover' not in st.session_state:
        st.session_state.turnover = pd.DataFrame()
    if 'benefits' not in st.session_state:
        st.session_state.benefits = pd.DataFrame()
    
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
            st.session_state.current_page = "📝 Data Input"
        
        if st.button("🤖 Auto Insights", key="nav_auto_insights", use_container_width=True):
            st.session_state.current_page = "🤖 Auto Insights"
        
        if st.button("🛡️ Risk Assessment", key="nav_risk_analysis", use_container_width=True):
            st.session_state.current_page = "🛡️ Risk Assessment"
        
        if st.button("🔮 Predictive Analytics", key="nav_predictive", use_container_width=True):
            st.session_state.current_page = "🔮 Predictive Analytics"
        
        if st.button("📚 Enhanced Analytics", key="nav_enhanced", use_container_width=True):
            st.session_state.current_page = "📚 Enhanced Analytics"
        
        if st.button("🎯 Recruitment Analysis", key="nav_recruitment", use_container_width=True):
            st.session_state.current_page = "🎯 Recruitment Analysis"
        
        if st.button("📊 Employee Performance", key="nav_performance", use_container_width=True):
            st.session_state.current_page = "📊 Employee Performance"
        
        if st.button("💰 Compensation & Benefits", key="nav_compensation", use_container_width=True):
            st.session_state.current_page = "💰 Compensation & Benefits"
        
        if st.button("🔄 Retention & Attrition", key="nav_retention", use_container_width=True):
            st.session_state.current_page = "🔄 Retention & Attrition"
        
        if st.button("😊 Engagement & Satisfaction", key="nav_engagement", use_container_width=True):
            st.session_state.current_page = "😊 Engagement & Satisfaction"
        
        if st.button("🎓 Training & Development", key="nav_training", use_container_width=True):
            st.session_state.current_page = "🎓 Training & Development"
        
        if st.button("🌍 DEI Analysis", key="nav_dei", use_container_width=True):
            st.session_state.current_page = "🌍 DEI Analysis"
        
        if st.button("📈 Workforce Planning", key="nav_workforce", use_container_width=True):
            st.session_state.current_page = "📈 Workforce Planning"
        
        if st.button("📋 HR Process & Policy", key="nav_process", use_container_width=True):
            st.session_state.current_page = "📋 HR Process & Policy"
        
        if st.button("🏥 Health & Wellbeing", key="nav_health", use_container_width=True):
            st.session_state.current_page = "🏥 Health & Wellbeing"
        
        if st.button("📊 Strategic HR Analytics", key="nav_strategic", use_container_width=True):
            st.session_state.current_page = "📊 Strategic HR Analytics"
        
        # --- Year and Quarter Filter ---
        employees_df = st.session_state.employees.copy()
        if not employees_df.empty and 'hire_date' in employees_df.columns:
            employees_df['hire_date'] = pd.to_datetime(employees_df['hire_date'], errors='coerce')
            employees_df = employees_df.dropna(subset=['hire_date'])
            employees_df['year'] = employees_df['hire_date'].dt.year
            employees_df['quarter'] = employees_df['hire_date'].dt.quarter
            years = sorted(employees_df['year'].dropna().unique())
            quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
            
            # Store default values in session state
            if 'selected_year' not in st.session_state:
                st.session_state.selected_year = years[-1] if years else None
            if 'selected_quarter' not in st.session_state:
                st.session_state.selected_quarter = 'All'
        # --- END FILTER ---
        
        # Initialize current page if not set
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"
        
        page = st.session_state.current_page
    
    # Main content area
    if page == "🏠 Home":
        show_home()
    
    elif page == "📝 Data Input":
        show_data_input()
    
    elif page == "🤖 Auto Insights":
        show_auto_insights()
    
    elif page == "🛡️ Risk Assessment":
        show_risk_assessment()
    
    elif page == "🔮 Predictive Analytics":
        show_predictive_analytics()
    
    elif page == "📚 Enhanced Analytics":
        show_enhanced_analytics()
    
    elif page == "🎯 Recruitment Analysis":
        show_recruitment_analysis()
    
    elif page == "📊 Employee Performance":
        show_employee_performance()
    
    elif page == "💰 Compensation & Benefits":
        show_compensation_benefits()
    
    elif page == "🔄 Retention & Attrition":
        show_retention_attrition()
    
    elif page == "😊 Engagement & Satisfaction":
        show_engagement_satisfaction()
    
    elif page == "🎓 Training & Development":
        show_training_development()
    
    elif page == "🌍 DEI Analysis":
        show_dei_analysis()
    
    elif page == "📈 Workforce Planning":
        show_workforce_planning()
    
    elif page == "📋 HR Process & Policy":
        show_hr_process_policy()
    
    elif page == "🏥 Health & Wellbeing":
        show_health_wellbeing()
    
    elif page == "📊 Strategic HR Analytics":
        show_strategic_hr_analytics()

def show_auto_insights():
    """Display AI-powered automatic insights for HR analytics."""
    import sys
    import os
    
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add current directory to path for imports
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from utils.insight_manager import InsightManager
    
    # Check if data is available
    if st.session_state.employees.empty:
        st.warning("⚠️ No employee data available. Please upload data in the Data Input section.")
        return
    
    # Initialize insight manager
    insight_manager = InsightManager()
    
    # Generate all insights
    with st.spinner("🤖 Generating comprehensive AI insights..."):
        insights_data = insight_manager.generate_all_insights(
            st.session_state.employees,
            st.session_state.recruitment,
            st.session_state.performance,
            st.session_state.compensation,
            st.session_state.training,
            st.session_state.engagement,
            st.session_state.turnover,
            st.session_state.benefits
        )
    
    # Render insights dashboard
    insight_manager.render_insights_dashboard(insights_data)

def show_risk_assessment():
    """Display comprehensive HR risk assessment dashboard."""
    st.header("🛡️ HR Risk Assessment Dashboard")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Calculate risk assessment
    risk_data = calculate_hr_risk_assessment(st.session_state.employees)
    
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">🛡️ HR Risk Assessment</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Comprehensive risk assessment across multiple HR dimensions. Identify high-risk employees and areas 
            requiring immediate attention to mitigate potential issues.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_employees = len(risk_data)
        st.metric(
            label="Total Employees",
            value=f"{total_employees:,}",
            delta="0"
        )
    
    with col2:
        if 'overall_risk_level' in risk_data.columns:
            high_risk_count = len(risk_data[risk_data['overall_risk_level'] == 'High Risk'])
            high_risk_pct = (high_risk_count / total_employees) * 100
            st.metric(
                label="High Risk Employees",
                value=f"{high_risk_count}",
                delta=f"{high_risk_pct:.1f}%"
            )
    
    with col3:
        if 'overall_risk_level' in risk_data.columns:
            medium_risk_count = len(risk_data[risk_data['overall_risk_level'] == 'Medium Risk'])
            medium_risk_pct = (medium_risk_count / total_employees) * 100
            st.metric(
                label="Medium Risk Employees",
                value=f"{medium_risk_count}",
                delta=f"{medium_risk_pct:.1f}%"
            )
    
    with col4:
        if 'overall_risk_score' in risk_data.columns:
            avg_risk_score = risk_data['overall_risk_score'].mean()
            st.metric(
                label="Average Risk Score",
                value=f"{avg_risk_score:.2f}",
                delta=f"{avg_risk_score - 2.0:.2f}" if avg_risk_score > 2.0 else f"{avg_risk_score - 2.0:.2f}"
            )
    
    st.markdown("---")
    
    # Create tabs for different risk categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Risk Overview", "🔄 Turnover Risk", "📈 Performance Risk", "💰 Compensation Risk", "👥 Employee Details"
    ])
    
    # Tab 1: Risk Overview
    with tab1:
        st.subheader("📊 Overall Risk Distribution")
        
        # Risk Distribution Summary
        if 'overall_risk_level' in risk_data.columns:
            risk_dist = risk_data['overall_risk_level'].value_counts()
            total_employees = len(risk_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                low_risk_count = risk_dist.get('Low Risk', 0)
                low_risk_pct = (low_risk_count / total_employees) * 100
                st.metric(
                    label="🟢 Low Risk",
                    value=f"{low_risk_count}",
                    delta=f"{low_risk_pct:.1f}%"
                )
            
            with col2:
                medium_risk_count = risk_dist.get('Medium Risk', 0)
                medium_risk_pct = (medium_risk_count / total_employees) * 100
                st.metric(
                    label="🟡 Medium Risk",
                    value=f"{medium_risk_count}",
                    delta=f"{medium_risk_pct:.1f}%"
                )
            
            with col3:
                high_risk_count = risk_dist.get('High Risk', 0)
                high_risk_pct = (high_risk_count / total_employees) * 100
                st.metric(
                    label="🔴 High Risk",
                    value=f"{high_risk_count}",
                    delta=f"{high_risk_pct:.1f}%"
                )
        
        # Interactive Risk Distribution
        if 'overall_risk_level' in risk_data.columns:
            # Create interactive pie chart with proper data handling
            risk_dist = risk_data['overall_risk_level'].value_counts()
            
            # Ensure all risk levels are present
            all_risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
            for level in all_risk_levels:
                if level not in risk_dist.index:
                    risk_dist[level] = 0
            
            # Sort by risk level order
            risk_dist = risk_dist.reindex(all_risk_levels)
            
            # Create the pie chart
            fig_risk_dist = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Overall Risk Distribution (Click on slice to view details)",
                color_discrete_sequence=['#51cf66', '#ffd43b', '#ff6b6b'],
                hole=0.3
            )
            fig_risk_dist.update_layout(
                height=500,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            fig_risk_dist.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<br><extra>Click to view details</extra>"
            )
            
            # Display the pie chart
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        # Interactive Risk Level Details
        st.subheader("🔍 Risk Level Details")
        
        # Create dropdown menu for risk level selection
        selected_risk_level = st.selectbox(
            "Select Risk Level to View Details:",
            ["Low Risk", "Medium Risk", "High Risk"]
        )
        filtered_risk_data = risk_data[risk_data['overall_risk_level'] == selected_risk_level]
        
        # Compact side-by-side layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Risk level summary and breakdown
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {'#51cf66' if selected_risk_level == 'Low Risk' else '#ffd43b' if selected_risk_level == 'Medium Risk' else '#ff6b6b'}, #f8f9fa); 
                        padding: 10px; border-radius: 8px; margin: 5px 0;">
                <h4 style="margin: 0; color: white;">{selected_risk_level} ({len(filtered_risk_data)} employees)</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Key statistics
            st.markdown("📈 Key Stats:")
            if 'overall_risk_score' in filtered_risk_data.columns:
                avg_score = filtered_risk_data['overall_risk_score'].mean()
                st.write(f"• Avg Risk: {avg_score:.2f}")
            
            if 'department' in filtered_risk_data.columns:
                dept_counts = filtered_risk_data['department'].value_counts()
                if len(dept_counts) > 0:
                    st.write(f"• Top Dept: {dept_counts.index[0]}")
                else:
                    st.write("• Top Dept: N/A")
            
            if 'tenure_days' in filtered_risk_data.columns:
                avg_tenure = filtered_risk_data['tenure_days'].mean()
                st.write(f"• Avg Tenure: {avg_tenure:.0f}d")
            
            if 'performance_rating' in filtered_risk_data.columns:
                avg_perf = filtered_risk_data['performance_rating'].mean()
                st.write(f"• Avg Perf: {avg_perf:.2f}/5")
        
        with col2:
            # Employee details table
            st.markdown(f"**👥 {selected_risk_level} Employees:**")
            
            display_cols = ['first_name', 'last_name', 'department', 'overall_risk_score']
            display_cols = [col for col in display_cols if col in filtered_risk_data.columns]
            
            # Add individual risk category columns
            risk_categories = ['turnover_risk', 'performance_risk', 'compensation_risk', 'age_risk']
            for category in risk_categories:
                if category in filtered_risk_data.columns:
                    display_cols.append(category)
            
            # Add additional useful columns
            additional_cols = ['tenure_days', 'performance_rating', 'salary', 'age']
            for col in additional_cols:
                if col in filtered_risk_data.columns and col not in display_cols:
                    display_cols.append(col)
            
            # Sort by overall risk score (highest first for high risk, lowest first for low risk)
            sort_ascending = selected_risk_level == "Low Risk"
            sorted_data = filtered_risk_data[display_cols].sort_values('overall_risk_score', ascending=sort_ascending)
            
            st.dataframe(sorted_data, use_container_width=True, height=400)
            
            # Export option
            if st.button(f"📥 Export {selected_risk_level} Data", key=f"export_{selected_risk_level}"):
                csv = sorted_data.to_csv(index=False)
                st.download_button(
                    label=f"Download {selected_risk_level} CSV",
                    data=csv,
                    file_name=f"{selected_risk_level.replace(' ', '_').lower()}_employees.csv",
                    mime="text/csv"
                )
        
        # Department Risk Analysis with AI Insights
        if 'department' in risk_data.columns and 'overall_risk_score' in risk_data.columns:
            st.subheader("🏢 Department Risk Analysis")
            
            dept_risk = risk_data.groupby('department')['overall_risk_score'].agg(['mean', 'count', 'std']).reset_index()
            dept_risk = dept_risk.rename(columns={'mean': 'avg_risk', 'count': 'employee_count', 'std': 'risk_volatility'})
            dept_risk = dept_risk.sort_values('avg_risk', ascending=False)
            
            # Add risk categorization
            dept_risk['risk_category'] = pd.cut(
                dept_risk['avg_risk'],
                bins=[0, 1.5, 2.5, 3.0],
                labels=['Low Risk', 'Medium Risk', 'High Risk'],
                include_lowest=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_dept_risk = px.bar(
                    dept_risk,
                    x='department',
                    y='avg_risk',
                    title="Average Risk Score by Department",
                    labels={'department': 'Department', 'avg_risk': 'Average Risk Score'},
                    color='risk_category',
                    color_discrete_map={'Low Risk': '#51cf66', 'Medium Risk': '#ffd43b', 'High Risk': '#ff6b6b'},
                    text='avg_risk'
                )
                fig_dept_risk.update_layout(
                    height=400, 
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                fig_dept_risk.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside'
                )
                st.plotly_chart(fig_dept_risk, use_container_width=True)
            
            with col2:
                # AI Insights for Department Risk
                st.markdown("**🤖 AI Risk Insights:**")
                
                # Find highest risk department
                highest_risk_dept = dept_risk.iloc[0]
                lowest_risk_dept = dept_risk.iloc[-1]
                
                st.markdown(f"""
                **🔴 Highest Risk Department:** {highest_risk_dept['department']}
                - Average Risk Score: {highest_risk_dept['avg_risk']:.2f}
                - Employee Count: {highest_risk_dept['employee_count']}
                - Risk Volatility: {highest_risk_dept['risk_volatility']:.2f}
                
                **🟢 Lowest Risk Department:** {lowest_risk_dept['department']}
                - Average Risk Score: {lowest_risk_dept['avg_risk']:.2f}
                - Employee Count: {lowest_risk_dept['employee_count']}
                - Risk Volatility: {lowest_risk_dept['risk_volatility']:.2f}
                """)
                
                # Risk insights and recommendations
                st.markdown("**📊 Risk Analysis Insights:**")
                
                high_risk_depts = dept_risk[dept_risk['risk_category'] == 'High Risk']
                if not high_risk_depts.empty:
                    st.warning(f"⚠️ **Immediate Attention Required:** {len(high_risk_depts)} department(s) have high average risk scores.")
                    for _, dept in high_risk_depts.iterrows():
                        st.write(f"• **{dept['department']}**: {dept['avg_risk']:.2f} risk score ({dept['employee_count']} employees)")
                
                # Department size vs risk correlation
                if len(dept_risk) > 1:
                    correlation = dept_risk['employee_count'].corr(dept_risk['avg_risk'])
                    if abs(correlation) > 0.3:
                        if correlation > 0:
                            st.info(f"📈 **Pattern Detected:** Larger departments tend to have higher risk scores (correlation: {correlation:.2f})")
                        else:
                            st.info(f"📉 **Pattern Detected:** Smaller departments tend to have higher risk scores (correlation: {correlation:.2f})")
                    else:
                        st.success("✅ **Good Distribution:** Department size doesn't strongly correlate with risk scores")
                
                # Recommendations
                st.markdown("**💡 Recommendations:**")
                if not high_risk_depts.empty:
                    recommendations = [
                        "Conduct detailed risk assessments for high-risk departments",
                        "Implement targeted retention strategies for vulnerable departments",
                        "Review compensation structures in high-risk areas"
                    ]
                else:
                    recommendations = [
                        "Maintain current risk management practices",
                        "Continue monitoring medium-risk departments",
                        "Share best practices from low-risk departments"
                    ]
                display_formatted_recommendations(recommendations)
            
            # Department risk details table
            st.subheader("📋 Department Risk Details")
            dept_display_cols = ['department', 'avg_risk', 'employee_count', 'risk_volatility', 'risk_category']
            st.dataframe(dept_risk[dept_display_cols].round(2))
    
    # Tab 2: Turnover Risk
    with tab2:
        st.subheader("🔄 Turnover Risk Analysis")
        
        # Turnover Risk Summary Metrics
        if 'turnover_risk' in risk_data.columns:
            turnover_risk_dist = risk_data['turnover_risk'].value_counts()
            total_employees = len(risk_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_turnover_count = turnover_risk_dist.get('High', 0)
                high_turnover_pct = (high_turnover_count / total_employees) * 100
                st.metric(
                    label="🔴 High Turnover Risk",
                    value=f"{high_turnover_count}",
                    delta=f"{high_turnover_pct:.1f}%"
                )
            
            with col2:
                medium_turnover_count = turnover_risk_dist.get('Medium', 0)
                medium_turnover_pct = (medium_turnover_count / total_employees) * 100
                st.metric(
                    label="🟡 Medium Turnover Risk",
                    value=f"{medium_turnover_count}",
                    delta=f"{medium_turnover_pct:.1f}%"
                )
            
            with col3:
                low_turnover_count = turnover_risk_dist.get('Low', 0)
                low_turnover_pct = (low_turnover_count / total_employees) * 100
                st.metric(
                    label="🟢 Low Turnover Risk",
                    value=f"{low_turnover_count}",
                    delta=f"{low_turnover_pct:.1f}%"
                )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'turnover_risk' in risk_data.columns:
                # Ensure all risk levels are present
                all_turnover_levels = ['High', 'Medium', 'Low']
                for level in all_turnover_levels:
                    if level not in turnover_risk_dist.index:
                        turnover_risk_dist[level] = 0
                
                turnover_risk_dist = turnover_risk_dist.reindex(all_turnover_levels)
                
                fig_turnover = px.pie(
                    values=turnover_risk_dist.values,
                    names=turnover_risk_dist.index,
                    title="Turnover Risk Distribution",
                    color_discrete_sequence=['#ff6b6b', '#ffd43b', '#51cf66'],
                    hole=0.3
                )
                fig_turnover.update_layout(
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_turnover.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
                )
                st.plotly_chart(fig_turnover, use_container_width=True)
        
        with col2:
            if 'tenure_days' in risk_data.columns:
                # Tenure distribution by risk level
                fig_tenure_risk = px.box(
                    risk_data,
                    x='turnover_risk',
                    y='tenure_days',
                    title="Tenure Distribution by Turnover Risk",
                    color='turnover_risk',
                    color_discrete_map={'High': '#ff6b6b', 'Medium': '#ffd43b', 'Low': '#51cf66'},
                    hover_data=['first_name', 'last_name', 'department', 'performance_rating', 'salary']
                )
                fig_tenure_risk.update_layout(
                    height=400,
                    xaxis_title="Turnover Risk Level",
                    yaxis_title="Tenure (Days)",
                    hovermode='closest'
                )
                fig_tenure_risk.update_traces(
                    hovertemplate="<b>%{x} Risk</b><br>" +
                                "Tenure: %{y:.0f} days<br>" +
                                "Employee: %{customdata[0]} %{customdata[1]}<br>" +
                                "Department: %{customdata[2]}<br>" +
                                "Performance: %{customdata[3]:.1f}/5<br>" +
                                "Salary: $%{customdata[4]:,.0f}<extra></extra>"
                )
                st.plotly_chart(fig_tenure_risk, use_container_width=True)
        
        # Interactive Turnover Risk Filter
        st.subheader("🔍 Turnover Risk Details")
        selected_turnover_risk = st.selectbox(
            "Select Turnover Risk Level to View Details:",
            ["High", "Medium", "Low"]
        )
        
        filtered_turnover_data = risk_data[risk_data['turnover_risk'] == selected_turnover_risk]
        st.write(f"**{selected_turnover_risk} Turnover Risk Employees ({len(filtered_turnover_data)} total):**")
        
        display_cols = ['first_name', 'last_name', 'department', 'tenure_days', 'turnover_risk']
        display_cols = [col for col in display_cols if col in filtered_turnover_data.columns]
        
        # Add other risk categories
        other_risk_categories = ['performance_risk', 'compensation_risk', 'age_risk']
        for category in other_risk_categories:
            if category in filtered_turnover_data.columns:
                display_cols.append(category)
        
        st.dataframe(filtered_turnover_data[display_cols].sort_values('tenure_days', ascending=True))
        
        # Turnover Risk Insights
        if 'turnover_risk' in risk_data.columns:
            st.subheader("📊 Turnover Risk Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Risk Analysis:**")
                
                # Calculate average tenure by risk level
                if 'tenure_days' in risk_data.columns:
                    tenure_by_risk = risk_data.groupby('turnover_risk')['tenure_days'].agg(['mean', 'count']).round(1)
                    st.write("**Average Tenure by Risk Level:**")
                    for risk_level, data in tenure_by_risk.iterrows():
                        st.write(f"• {risk_level} Risk: {data['mean']:.0f} days ({data['count']} employees)")
                
                # Department analysis
                if 'department' in risk_data.columns:
                    dept_turnover_risk = risk_data.groupby(['department', 'turnover_risk']).size().unstack(fill_value=0)
                    high_risk_depts = dept_turnover_risk['High'].sort_values(ascending=False)
                    if not high_risk_depts.empty:
                        st.write("**Departments with High Turnover Risk:**")
                        for dept, count in high_risk_depts.head(3).items():
                            if count > 0:
                                st.write(f"• {dept}: {count} employees")
            
            with col2:
                st.markdown("**💡 Recommendations:**")
                
                high_turnover_count = turnover_risk_dist.get('High', 0)
                if high_turnover_count > 0:
                    st.warning(f"⚠️ **Immediate Action Required:** {high_turnover_count} employees at high turnover risk")
                    recommendations = [
                        "Implement retention strategies for high-risk employees",
                        "Conduct exit interviews and stay interviews",
                        "Review compensation and benefits for at-risk groups",
                        "Develop career development programs"
                    ]
                else:
                    st.success("✅ **Good Retention:** No employees at high turnover risk")
                    recommendations = [
                        "Continue current retention practices",
                        "Monitor medium-risk employees",
                        "Maintain positive work environment"
                    ]
                display_formatted_recommendations(recommendations)
    
    # Tab 3: Performance Risk
    with tab3:
        st.subheader("📈 Performance Risk Analysis")
        
        # Performance Risk Summary Metrics
        if 'performance_risk' in risk_data.columns:
            perf_risk_dist = risk_data['performance_risk'].value_counts()
            total_employees = len(risk_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_perf_count = perf_risk_dist.get('High', 0)
                high_perf_pct = (high_perf_count / total_employees) * 100
                st.metric(
                    label="🔴 High Performance Risk",
                    value=f"{high_perf_count}",
                    delta=f"{high_perf_pct:.1f}%"
                )
            
            with col2:
                medium_perf_count = perf_risk_dist.get('Medium', 0)
                medium_perf_pct = (medium_perf_count / total_employees) * 100
                st.metric(
                    label="🟡 Medium Performance Risk",
                    value=f"{medium_perf_count}",
                    delta=f"{medium_perf_pct:.1f}%"
                )
            
            with col3:
                low_perf_count = perf_risk_dist.get('Low', 0)
                low_perf_pct = (low_perf_count / total_employees) * 100
                st.metric(
                    label="🟢 Low Performance Risk",
                    value=f"{low_perf_count}",
                    delta=f"{low_perf_pct:.1f}%"
                )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'performance_risk' in risk_data.columns:
                # Ensure all risk levels are present
                all_perf_levels = ['High', 'Medium', 'Low']
                for level in all_perf_levels:
                    if level not in perf_risk_dist.index:
                        perf_risk_dist[level] = 0
                
                perf_risk_dist = perf_risk_dist.reindex(all_perf_levels)
                
                fig_perf = px.pie(
                    values=perf_risk_dist.values,
                    names=perf_risk_dist.index,
                    title="Performance Risk Distribution",
                    color_discrete_sequence=['#ff6b6b', '#ffd43b', '#51cf66'],
                    hole=0.3
                )
                fig_perf.update_layout(
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_perf.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
                )
                st.plotly_chart(fig_perf, use_container_width=True)
        
        with col2:
            if 'performance_rating' in risk_data.columns:
                # Performance rating distribution by risk level
                fig_perf_risk = px.box(
                    risk_data,
                    x='performance_risk',
                    y='performance_rating',
                    title="Performance Rating Distribution by Risk Level",
                    color='performance_risk',
                    color_discrete_map={'High': '#ff6b6b', 'Medium': '#ffd43b', 'Low': '#51cf66'}
                )
                fig_perf_risk.update_layout(
                    height=400,
                    xaxis_title="Performance Risk Level",
                    yaxis_title="Performance Rating"
                )
                st.plotly_chart(fig_perf_risk, use_container_width=True)
        
        # Interactive Performance Risk Filter
        st.subheader("🔍 Performance Risk Details")
        selected_perf_risk = st.selectbox(
            "Select Performance Risk Level to View Details:",
            ["High", "Medium", "Low"]
        )
        
        filtered_perf_data = risk_data[risk_data['performance_risk'] == selected_perf_risk]
        st.write(f"**{selected_perf_risk} Performance Risk Employees ({len(filtered_perf_data)} total):**")
        
        display_cols = ['first_name', 'last_name', 'department', 'performance_rating', 'performance_risk']
        display_cols = [col for col in display_cols if col in filtered_perf_data.columns]
        
        # Add other risk categories
        other_risk_categories = ['turnover_risk', 'compensation_risk', 'age_risk']
        for category in other_risk_categories:
            if category in filtered_perf_data.columns:
                display_cols.append(category)
        
        st.dataframe(filtered_perf_data[display_cols].sort_values('performance_rating', ascending=True))
        
        # Performance Risk Insights
        if 'performance_risk' in risk_data.columns:
            st.subheader("📊 Performance Risk Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Risk Analysis:**")
                
                # Calculate average performance by risk level
                if 'performance_rating' in risk_data.columns:
                    perf_by_risk = risk_data.groupby('performance_risk')['performance_rating'].agg(['mean', 'count']).round(2)
                    st.write("**Average Performance by Risk Level:**")
                    for risk_level, data in perf_by_risk.iterrows():
                        st.write(f"• {risk_level} Risk: {data['mean']:.2f}/5 ({data['count']} employees)")
                
                # Department analysis
                if 'department' in risk_data.columns:
                    dept_perf_risk = risk_data.groupby(['department', 'performance_risk']).size().unstack(fill_value=0)
                    if 'High' in dept_perf_risk.columns:
                        high_risk_depts = dept_perf_risk['High'].sort_values(ascending=False)
                        if not high_risk_depts.empty:
                            st.write("**Departments with High Performance Risk:**")
                            for dept, count in high_risk_depts.head(3).items():
                                if count > 0:
                                    st.write(f"• {dept}: {count} employees")
            
            with col2:
                st.markdown("**💡 Recommendations:**")
                
                high_perf_count = perf_risk_dist.get('High', 0)
                if high_perf_count > 0:
                    st.warning(f"⚠️ **Immediate Action Required:** {high_perf_count} employees at high performance risk")
                    recommendations = [
                        "Implement performance improvement plans",
                        "Provide additional training and development",
                        "Set clear performance expectations and goals",
                        "Consider mentorship programs"
                    ]
                else:
                    st.success("✅ **Good Performance:** No employees at high performance risk")
                    recommendations = [
                        "Continue current performance management practices",
                        "Monitor medium-risk employees",
                        "Recognize and reward high performers"
                    ]
                display_formatted_recommendations(recommendations)
    
    # Tab 4: Compensation Risk
    with tab4:
        st.subheader("💰 Compensation Risk Analysis")
        
        # Compensation Risk Summary Metrics
        if 'compensation_risk' in risk_data.columns:
            comp_risk_dist = risk_data['compensation_risk'].value_counts()
            total_employees = len(risk_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_comp_count = comp_risk_dist.get('High', 0)
                high_comp_pct = (high_comp_count / total_employees) * 100
                st.metric(
                    label="🔴 High Compensation Risk",
                    value=f"{high_comp_count}",
                    delta=f"{high_comp_pct:.1f}%"
                )
            
            with col2:
                medium_comp_count = comp_risk_dist.get('Medium', 0)
                medium_comp_pct = (medium_comp_count / total_employees) * 100
                st.metric(
                    label="🟡 Medium Compensation Risk",
                    value=f"{medium_comp_count}",
                    delta=f"{medium_comp_pct:.1f}%"
                )
            
            with col3:
                low_comp_count = comp_risk_dist.get('Low', 0)
                low_comp_pct = (low_comp_count / total_employees) * 100
                st.metric(
                    label="🟢 Low Compensation Risk",
                    value=f"{low_comp_count}",
                    delta=f"{low_comp_pct:.1f}%"
                )
        
        # Compensation Risk Distribution Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'compensation_risk' in risk_data.columns:
                # Ensure all risk levels are present
                all_risk_levels = ['Low', 'Medium', 'High']
                for level in all_risk_levels:
                    if level not in comp_risk_dist.index:
                        comp_risk_dist[level] = 0
                
                # Sort by risk level order
                comp_risk_dist = comp_risk_dist.reindex(all_risk_levels)
                
                fig_comp = px.pie(
                    values=comp_risk_dist.values,
                    names=comp_risk_dist.index,
                    title="Compensation Risk Distribution",
                    color_discrete_sequence=['#51cf66', '#ffd43b', '#ff6b6b']
                )
                fig_comp.update_layout(height=400)
                fig_comp.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
                )
                st.plotly_chart(fig_comp, use_container_width=True)
        
        with col2:
            if 'salary' in risk_data.columns:
                # Salary distribution by compensation risk level
                fig_salary_risk = px.box(
                    risk_data,
                    x='compensation_risk',
                    y='salary',
                    title="Salary Distribution by Compensation Risk",
                    color='compensation_risk',
                    color_discrete_map={'High': '#ff6b6b', 'Medium': '#ffd43b', 'Low': '#51cf66'},
                    hover_data=['first_name', 'last_name', 'department', 'performance_rating', 'tenure_days']
                )
                fig_salary_risk.update_layout(
                    height=400,
                    xaxis_title="Compensation Risk Level",
                    yaxis_title="Salary ($)",
                    hovermode='closest'
                )
                fig_salary_risk.update_traces(
                    hovertemplate="<b>%{x} Risk</b><br>" +
                                "Salary: $%{y:,.0f}<br>" +
                                "Employee: %{customdata[0]} %{customdata[1]}<br>" +
                                "Department: %{customdata[2]}<br>" +
                                "Performance: %{customdata[3]:.1f}/5<br>" +
                                "Tenure: %{customdata[4]:.0f} days<extra></extra>"
                )
                st.plotly_chart(fig_salary_risk, use_container_width=True)
        
        # Interactive Compensation Risk Filter
        st.subheader("🔍 Compensation Risk Details")
        selected_comp_risk = st.selectbox(
            "Select Compensation Risk Level to View Details:",
            ["High", "Medium", "Low"]
        )
        
        filtered_comp_data = risk_data[risk_data['compensation_risk'] == selected_comp_risk]
        st.write(f"**{selected_comp_risk} Compensation Risk Employees ({len(filtered_comp_data)} total):**")
        
        display_cols = ['first_name', 'last_name', 'department', 'salary', 'compensation_risk']
        display_cols = [col for col in display_cols if col in filtered_comp_data.columns]
        
        # Add other risk categories
        other_risk_categories = ['turnover_risk', 'performance_risk', 'age_risk']
        for category in other_risk_categories:
            if category in filtered_comp_data.columns:
                display_cols.append(category)
        
        st.dataframe(filtered_comp_data[display_cols].sort_values('salary', ascending=False))
        
        # Compensation Risk Insights
        if 'compensation_risk' in risk_data.columns:
            st.subheader("📊 Compensation Risk Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Risk Analysis:**")
                
                # Calculate average salary by risk level
                if 'salary' in risk_data.columns:
                    salary_by_risk = risk_data.groupby('compensation_risk')['salary'].agg(['mean', 'count']).round(0)
                    st.write("**Average Salary by Risk Level:**")
                    for risk_level, data in salary_by_risk.iterrows():
                        st.write(f"• {risk_level} Risk: ${data['mean']:,.0f} ({data['count']} employees)")
                
                # Department analysis
                if 'department' in risk_data.columns:
                    dept_comp_risk = risk_data.groupby(['department', 'compensation_risk']).size().unstack(fill_value=0)
                    if 'High' in dept_comp_risk.columns:
                        high_risk_depts = dept_comp_risk['High'].sort_values(ascending=False)
                        if not high_risk_depts.empty:
                            st.write("**Departments with High Compensation Risk:**")
                            for dept, count in high_risk_depts.head(3).items():
                                if count > 0:
                                    st.write(f"• {dept}: {count} employees")
            
            with col2:
                st.markdown("**💡 Recommendations:**")
                
                high_comp_count = comp_risk_dist.get('High', 0)
                if high_comp_count > 0:
                    st.warning(f"⚠️ **Immediate Action Required:** {high_comp_count} employees at high compensation risk")
                    recommendations = [
                        "Review salary benchmarking and market rates",
                        "Address pay equity issues",
                        "Consider salary adjustments for at-risk employees",
                        "Implement transparent compensation policies"
                    ]
                else:
                    st.success("✅ **Good Compensation:** No employees at high compensation risk")
                    recommendations = [
                        "Continue current compensation practices",
                        "Monitor medium-risk employees",
                        "Regular market rate reviews"
                    ]
                display_formatted_recommendations(recommendations)
    
    # Tab 5: Employee Details
    with tab5:
        st.subheader("👥 Employee Risk Details")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            risk_filter = st.selectbox(
                "Filter by Risk Level:",
                ["All", "High Risk", "Medium Risk", "Low Risk"]
            )
        
        with col2:
            if 'department' in risk_data.columns:
                dept_filter = st.selectbox(
                    "Filter by Department:",
                    ["All"] + list(risk_data['department'].unique())
                )
        
        # Apply filters
        filtered_data = risk_data.copy()
        
        if risk_filter != "All" and 'overall_risk_level' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['overall_risk_level'] == risk_filter]
        
        if dept_filter != "All" and 'department' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['department'] == dept_filter]
        
        # Display filtered results
        if not filtered_data.empty:
            display_cols = ['first_name', 'last_name', 'department', 'overall_risk_level', 'overall_risk_score']
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            
            # Add risk category columns if available
            risk_categories = ['turnover_risk', 'performance_risk', 'compensation_risk', 'age_risk']
            for category in risk_categories:
                if category in filtered_data.columns:
                    display_cols.append(category)
            
            st.dataframe(filtered_data[display_cols].sort_values('overall_risk_score', ascending=False))
        else:
            st.info("No employees match the selected filters.")

def show_predictive_analytics():
    """Display predictive analytics dashboard."""
    display_predictive_analytics_dashboard(
        st.session_state.employees,
        st.session_state.recruitment,
        st.session_state.performance,
        st.session_state.compensation,
        st.session_state.training,
        st.session_state.engagement,
        st.session_state.turnover,
        st.session_state.benefits
    )

def show_enhanced_analytics():
    """Display enhanced analytics dashboard based on book concepts."""
    display_enhanced_analytics_dashboard(
        st.session_state.employees,
        st.session_state.recruitment,
        st.session_state.performance,
        st.session_state.compensation,
        st.session_state.training,
        st.session_state.engagement,
        st.session_state.turnover,
        st.session_state.benefits
    )

def show_home():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">🎯 Welcome to HR Analytics Dashboard</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Transform your HR data into actionable insights with our comprehensive analytics platform. 
            Get real-time visibility into employee performance, recruitment effectiveness, retention patterns, and more.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Dashboard
    if not st.session_state.employees.empty:
        total_employees = len(st.session_state.employees)
        avg_salary = st.session_state.employees['salary'].mean() if 'salary' in st.session_state.employees.columns else 0
        departments = st.session_state.employees['department'].nunique() if 'department' in st.session_state.employees.columns else 0
        avg_tenure = st.session_state.employees['tenure_days'].mean() if 'tenure_days' in st.session_state.employees.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Employees",
                value=f"{total_employees:,}",
                delta=f"+{total_employees//10}" if total_employees > 0 else "0"
            )
        
        with col2:
            st.metric(
                label="Average Salary",
                value=f"${avg_salary:,.0f}",
                delta=f"${avg_salary*0.05:,.0f}" if avg_salary > 0 else "$0"
            )
        
        with col3:
            st.metric(
                label="Departments",
                value=f"{departments}",
                delta="+1" if departments > 5 else "0"
            )
        
        with col4:
            st.metric(
                label="Avg Tenure (Days)",
                value=f"{avg_tenure:.0f}",
                delta=f"+{avg_tenure//10:.0f}" if avg_tenure > 0 else "0"
            )
    
    st.markdown("""
    ## 📊 Available HR Analytics Categories:
    
    **1. 🎯 Recruitment Analysis**
    - Time to Hire
    - Cost Per Hire
    - Source Effectiveness
    - Application Drop-Off Rates
    
    **2. 📊 Employee Performance Analysis**
    - Employee Productivity
    - Goal Achievement Rate
    - Performance Trends Over Time
    - High-Performer Retention
    
    **3. 💰 Compensation and Benefits Analysis**
    - Salary Distribution and Equity
    - Total Compensation Analysis
    - Pay-for-Performance Correlation
    - Benefits Utilization Analysis
    
    **4. 🔄 Employee Retention and Attrition Analysis**
    - Turnover Rate
    - Retention Rate by Department
    - Attrition Reasons
    - Tenure Analysis
    
    **5. 😊 Employee Engagement and Satisfaction Analysis**
    - Employee Engagement Scores
    - Job Satisfaction Analysis
    - Pulse Survey Trends
    - Work-Life Balance Metrics
    
    **6. 🎓 Training and Development Analysis**
    - Training Effectiveness
    - Learning and Development ROI
    - Employee Participation in Training
    - Time to Competency
    
    **7. 🌍 Diversity, Equity, and Inclusion (DEI) Analysis**
    - Workforce Diversity Metrics
    - Pay Equity Analysis
    - Promotion Rate by Demographics
    - Diversity Hiring Metrics
    
    **8. 📈 Workforce Planning and Forecasting**
    - Headcount Planning
    - Succession Planning
    - Workforce Demographics Analysis
    - Overtime and Capacity Utilization
    
    **9. ⚖️ HR Process and Policy Analysis**
    - Onboarding Effectiveness
    - HR Policy Compliance
    - Employee Grievance Trends
    
    **10. 🏥 Health and Wellbeing Analysis**
    - Absenteeism Rates
    - Employee Wellbeing Metrics
    - Health Insurance Claims Analysis
    
    **11. 📋 Strategic HR Analytics**
    - Employee Lifetime Value (ELV)
    - Cost Savings from Automation
    - HR Efficiency Metrics
    
    **12. 🎯 Specialized HR Metrics**
    - Remote Work Analysis
    - Employee Net Promoter Score (eNPS)
    - Internal Mobility Rate
    - Workforce Aging Analysis
    
    ### 🚀 Getting Started:
    
    1. **Data Input**: Start by entering your HR data in the "Data Input" tab
    2. **Calculate Metrics**: Use the main tabs to view specific metric categories
    3. **Real-time Analysis**: All metrics update automatically based on your data
    
    ### 📈 Data Schema:
    
    The application supports the following HR data tables:
    - Employees (demographics, performance, tenure)
    - Recruitment (job postings, applications, hires)
    - Performance (reviews, ratings, goals)
    - Compensation (salary, bonuses, benefits)
    - Training (programs, costs, outcomes)
    - Engagement (surveys, scores, feedback)
    - Turnover (separations, reasons, costs)
    - Benefits (enrollment, utilization, costs)
    
    ---
    
    **Note**: All calculations are performed automatically based on your input data. Make sure to enter complete and accurate data for the most reliable metrics.
    """)

def show_data_input():
    """Show data input forms and file upload options"""
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">📝 Data Input</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Upload your HR data or enter it manually. The application supports Excel file uploads and manual data entry for all HR metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create four tabs for data input methods
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Download Template", "📤 Upload Data", "📝 Manual Entry", "🧪 Sample Dataset"])
    
    with tab1:
        st.subheader("📥 Download Data Template")
        st.write("Download the Excel template with all required HR data schema, fill it with your data, and upload it back.")
        
        st.write("**Template includes:**")
        st.write("• 8 HR data tables in separate sheets")
        st.write("• Instructions sheet with field descriptions")
        st.write("• Proper column headers and data types")
        
        if st.button("📥 Download Template", use_container_width=True):
            create_template_for_download()
    
    with tab2:
        st.subheader("📤 Upload Your Data")
        st.write("Upload your filled Excel template:")
        
        uploaded_file = st.file_uploader(
            "Upload Excel file with all HR tables",
            type=['xlsx', 'xls'],
            help="Upload an Excel file containing all HR data tables"
        )
        
        st.write("**Upload features:**")
        st.write("• Automatic validation of all sheets")
        st.write("• Import all 8 HR tables at once")
        st.write("• Error checking and feedback")
        
        if uploaded_file is not None:
            try:
                # Read all sheets from the uploaded file
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                
                # Check if all required sheets are present
                required_sheets = ['Employees', 'Recruitment', 'Performance', 'Compensation', 'Training', 'Engagement', 'Turnover', 'Benefits']
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
                
                if missing_sheets:
                    st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                    st.info("Please ensure your Excel file contains all 8 required HR sheets.")
                else:
                    # Load data into session state
                    st.session_state.employees = excel_data['Employees']
                    st.session_state.recruitment = excel_data['Recruitment']
                    st.session_state.performance = excel_data['Performance']
                    st.session_state.compensation = excel_data['Compensation']
                    st.session_state.training = excel_data['Training']
                    st.session_state.engagement = excel_data['Engagement']
                    st.session_state.turnover = excel_data['Turnover']
                    st.session_state.benefits = excel_data['Benefits']
                    
                    st.success("✅ All HR data loaded successfully from Excel file!")
                    st.info(f"📊 Loaded {len(st.session_state.employees)} employees, {len(st.session_state.recruitment)} recruitment records, {len(st.session_state.performance)} performance reviews, and more...")
                    
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.info("Please ensure the file is a valid Excel file with the correct format.")
    
    with tab3:
        st.subheader("📝 Manual Data Entry")
        st.write("Enter HR data manually through the forms below:")
        
        # Create tabs for different data types
        subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7, subtab8 = st.tabs([
            "👥 Employees", "🎯 Recruitment", "📊 Performance", "💰 Compensation",
            "🎓 Training", "😊 Engagement", "🔄 Turnover", "🏥 Benefits"
        ])
        
        with subtab1:
            st.subheader("Employees")
            col1, col2 = st.columns(2)
            
            with col1:
                employee_id = st.text_input("Employee ID", key="employee_id_input")
                first_name = st.text_input("First Name", key="first_name_input")
                last_name = st.text_input("Last Name", key="last_name_input")
                email = st.text_input("Email", key="email_input")
                hire_date = st.date_input("Hire Date", key="hire_date_input")
                department = st.text_input("Department", key="department_input")
                job_title = st.text_input("Job Title", key="job_title_input")
                salary = st.number_input("Salary", min_value=0.0, key="salary_input")
            
            with col2:
                manager_id = st.text_input("Manager ID", key="manager_id_input")
                location = st.text_input("Location", key="location_input")
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], key="gender_input")
                age = st.number_input("Age", min_value=18, max_value=100, key="age_input")
                ethnicity = st.text_input("Ethnicity", key="ethnicity_input")
                education_level = st.selectbox("Education Level", ["High School", "Bachelor's", "Master's", "PhD", "Other"], key="education_input")
                performance_rating = st.number_input("Performance Rating", min_value=1.0, max_value=5.0, key="performance_input")
                status = st.selectbox("Status", ["Active", "Inactive", "Terminated"], key="status_input")
            
            if st.button("Add Employee"):
                new_employee = pd.DataFrame([{
                    'employee_id': employee_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'hire_date': hire_date,
                    'department': department,
                    'job_title': job_title,
                    'salary': salary,
                    'manager_id': manager_id,
                    'location': location,
                    'gender': gender,
                    'age': age,
                    'ethnicity': ethnicity,
                    'education_level': education_level,
                    'performance_rating': performance_rating,
                    'tenure_days': 0,  # Will be calculated
                    'status': status
                }])
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)
                st.success("Employee added successfully!")
            
            # Display existing data
            if not st.session_state.employees.empty:
                st.subheader("Existing Employees")
                display_dataframe_with_index_1(st.session_state.employees)
        
        with subtab2:
            st.subheader("Recruitment")
            col1, col2 = st.columns(2)
            
            with col1:
                job_posting_id = st.text_input("Job Posting ID", key="job_posting_id_input")
                position_title = st.text_input("Position Title", key="position_title_input")
                department = st.text_input("Department", key="department_recruitment_input")
                posting_date = st.date_input("Posting Date", key="posting_date_input")
                closing_date = st.date_input("Closing Date", key="closing_date_input")
                applications_received = st.number_input("Applications Received", min_value=0, key="applications_input")
            
            with col2:
                candidates_interviewed = st.number_input("Candidates Interviewed", min_value=0, key="interviewed_input")
                offers_made = st.number_input("Offers Made", min_value=0, key="offers_input")
                hires_made = st.number_input("Hires Made", min_value=0, key="hires_input")
                recruitment_source = st.selectbox("Recruitment Source", ["Job Board", "Referral", "Agency", "Internal", "Social Media"], key="source_input")
                recruitment_cost = st.number_input("Recruitment Cost", min_value=0.0, key="cost_input")
                time_to_hire_days = st.number_input("Time to Hire (Days)", min_value=0, key="time_input")
            
            if st.button("Add Recruitment Record"):
                new_recruitment = pd.DataFrame([{
                    'job_posting_id': job_posting_id,
                    'position_title': position_title,
                    'department': department,
                    'posting_date': posting_date,
                    'closing_date': closing_date,
                    'applications_received': applications_received,
                    'candidates_interviewed': candidates_interviewed,
                    'offers_made': offers_made,
                    'hires_made': hires_made,
                    'recruitment_source': recruitment_source,
                    'recruitment_cost': recruitment_cost,
                    'time_to_hire_days': time_to_hire_days
                }])
                st.session_state.recruitment = pd.concat([st.session_state.recruitment, new_recruitment], ignore_index=True)
                st.success("Recruitment record added successfully!")
            
            # Display existing data
            if not st.session_state.recruitment.empty:
                st.subheader("Existing Recruitment Records")
                display_dataframe_with_index_1(st.session_state.recruitment)
        
        with subtab3:
            st.subheader("Performance")
            col1, col2 = st.columns(2)
            
            with col1:
                review_id = st.text_input("Review ID", key="review_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_performance_input")
                review_date = st.date_input("Review Date", key="review_date_input")
                reviewer_id = st.text_input("Reviewer ID", key="reviewer_id_input")
                performance_rating = st.number_input("Performance Rating", min_value=1.0, max_value=5.0, key="performance_rating_input")
            
            with col2:
                goal_achievement_rate = st.number_input("Goal Achievement Rate (%)", min_value=0.0, max_value=100.0, key="goal_rate_input")
                productivity_score = st.number_input("Productivity Score", min_value=0.0, max_value=100.0, key="productivity_input")
                skills_assessment = st.number_input("Skills Assessment", min_value=1.0, max_value=5.0, key="skills_input")
                review_cycle = st.selectbox("Review Cycle", ["Q1", "Q2", "Q3", "Q4", "Annual"], key="cycle_input")
            
            if st.button("Add Performance Review"):
                new_performance = pd.DataFrame([{
                    'review_id': review_id,
                    'employee_id': employee_id,
                    'review_date': review_date,
                    'reviewer_id': reviewer_id,
                    'performance_rating': performance_rating,
                    'goal_achievement_rate': goal_achievement_rate,
                    'productivity_score': productivity_score,
                    'skills_assessment': skills_assessment,
                    'review_cycle': review_cycle
                }])
                st.session_state.performance = pd.concat([st.session_state.performance, new_performance], ignore_index=True)
                st.success("Performance review added successfully!")
            
            # Display existing data
            if not st.session_state.performance.empty:
                st.subheader("Existing Performance Reviews")
                display_dataframe_with_index_1(st.session_state.performance)
        
        with subtab4:
            st.subheader("Compensation")
            col1, col2 = st.columns(2)
            
            with col1:
                compensation_id = st.text_input("Compensation ID", key="compensation_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_compensation_input")
                effective_date = st.date_input("Effective Date", key="effective_date_input")
                base_salary = st.number_input("Base Salary", min_value=0.0, key="base_salary_input")
                bonus_amount = st.number_input("Bonus Amount", min_value=0.0, key="bonus_input")
            
            with col2:
                benefits_value = st.number_input("Benefits Value", min_value=0.0, key="benefits_value_input")
                total_compensation = st.number_input("Total Compensation", min_value=0.0, key="total_comp_input")
                pay_grade = st.text_input("Pay Grade", key="pay_grade_input")
                compensation_reason = st.selectbox("Compensation Reason", ["Annual Review", "Promotion", "Market Adjustment", "Performance Bonus"], key="comp_reason_input")
            
            if st.button("Add Compensation Record"):
                new_compensation = pd.DataFrame([{
                    'compensation_id': compensation_id,
                    'employee_id': employee_id,
                    'effective_date': effective_date,
                    'base_salary': base_salary,
                    'bonus_amount': bonus_amount,
                    'benefits_value': benefits_value,
                    'total_compensation': total_compensation,
                    'pay_grade': pay_grade,
                    'compensation_reason': compensation_reason
                }])
                st.session_state.compensation = pd.concat([st.session_state.compensation, new_compensation], ignore_index=True)
                st.success("Compensation record added successfully!")
            
            # Display existing data
            if not st.session_state.compensation.empty:
                st.subheader("Existing Compensation Records")
                display_dataframe_with_index_1(st.session_state.compensation)
        
        with subtab5:
            st.subheader("Training")
            col1, col2 = st.columns(2)
            
            with col1:
                training_id = st.text_input("Training ID", key="training_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_training_input")
                training_program = st.text_input("Training Program", key="training_program_input")
                start_date = st.date_input("Start Date", key="training_start_input")
                completion_date = st.date_input("Completion Date", key="completion_date_input")
            
            with col2:
                training_cost = st.number_input("Training Cost", min_value=0.0, key="training_cost_input")
                skills_improvement = st.number_input("Skills Improvement (%)", min_value=0.0, max_value=100.0, key="skills_improvement_input")
                performance_impact = st.number_input("Performance Impact", min_value=0.0, max_value=100.0, key="performance_impact_input")
                training_type = st.selectbox("Training Type", ["Technical", "Leadership", "Compliance", "Soft Skills"], key="training_type_input")
            
            if st.button("Add Training Record"):
                new_training = pd.DataFrame([{
                    'training_id': training_id,
                    'employee_id': employee_id,
                    'training_program': training_program,
                    'start_date': start_date,
                    'completion_date': completion_date,
                    'training_cost': training_cost,
                    'skills_improvement': skills_improvement,
                    'performance_impact': performance_impact,
                    'training_type': training_type
                }])
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)
                st.success("Training record added successfully!")
            
            # Display existing data
            if not st.session_state.training.empty:
                st.subheader("Existing Training Records")
                display_dataframe_with_index_1(st.session_state.training)
        
        with subtab6:
            st.subheader("Engagement")
            col1, col2 = st.columns(2)
            
            with col1:
                survey_id = st.text_input("Survey ID", key="survey_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_engagement_input")
                survey_date = st.date_input("Survey Date", key="survey_date_input")
                engagement_score = st.number_input("Engagement Score", min_value=1.0, max_value=10.0, key="engagement_score_input")
                satisfaction_score = st.number_input("Satisfaction Score", min_value=1.0, max_value=10.0, key="satisfaction_score_input")
            
            with col2:
                work_life_balance_score = st.number_input("Work-Life Balance Score", min_value=1.0, max_value=10.0, key="work_life_input")
                recommendation_score = st.number_input("Recommendation Score", min_value=1.0, max_value=10.0, key="recommendation_input")
                survey_type = st.selectbox("Survey Type", ["Annual", "Pulse", "Exit", "Onboarding"], key="survey_type_input")
            
            if st.button("Add Engagement Survey"):
                new_engagement = pd.DataFrame([{
                    'survey_id': survey_id,
                    'employee_id': employee_id,
                    'survey_date': survey_date,
                    'engagement_score': engagement_score,
                    'satisfaction_score': satisfaction_score,
                    'work_life_balance_score': work_life_balance_score,
                    'recommendation_score': recommendation_score,
                    'survey_type': survey_type
                }])
                st.session_state.engagement = pd.concat([st.session_state.engagement, new_engagement], ignore_index=True)
                st.success("Engagement survey added successfully!")
            
            # Display existing data
            if not st.session_state.engagement.empty:
                st.subheader("Existing Engagement Surveys")
                display_dataframe_with_index_1(st.session_state.engagement)
        
        with subtab7:
            st.subheader("Turnover")
            col1, col2 = st.columns(2)
            
            with col1:
                turnover_id = st.text_input("Turnover ID", key="turnover_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_turnover_input")
                separation_date = st.date_input("Separation Date", key="separation_date_input")
                separation_reason = st.selectbox("Separation Reason", ["Resignation", "Termination", "Retirement", "Layoff"], key="separation_reason_input")
                turnover_reason_detail = st.text_area("Turnover Reason Detail", key="turnover_reason_detail_input", 
                                                     placeholder="Detailed reason for separation (e.g., 'Better career opportunity', 'Performance issues', 'Company restructuring')")
                exit_interview_score = st.number_input("Exit Interview Score", min_value=1.0, max_value=10.0, key="exit_score_input")
            
            with col2:
                rehire_eligibility = st.selectbox("Rehire Eligibility", ["Yes", "No", "Maybe"], key="rehire_input")
                knowledge_transfer_completed = st.checkbox("Knowledge Transfer Completed", key="knowledge_transfer_input")
                replacement_hired = st.checkbox("Replacement Hired", key="replacement_input")
                turnover_cost = st.number_input("Turnover Cost ($)", min_value=0.0, key="turnover_cost_input")
                notice_period_days = st.number_input("Notice Period (Days)", min_value=0, key="notice_period_input")
            
            if st.button("Add Turnover Record"):
                new_turnover = pd.DataFrame([{
                    'turnover_id': turnover_id,
                    'employee_id': employee_id,
                    'separation_date': separation_date,
                    'separation_reason': separation_reason,
                    'turnover_reason_detail': turnover_reason_detail,
                    'exit_interview_score': exit_interview_score,
                    'rehire_eligibility': rehire_eligibility,
                    'knowledge_transfer_completed': knowledge_transfer_completed,
                    'replacement_hired': replacement_hired,
                    'turnover_cost': turnover_cost,
                    'notice_period_days': notice_period_days
                }])
                st.session_state.turnover = pd.concat([st.session_state.turnover, new_turnover], ignore_index=True)
                st.success("Turnover record added successfully!")
            
            # Display existing data
            if not st.session_state.turnover.empty:
                st.subheader("Existing Turnover Records")
                display_dataframe_with_index_1(st.session_state.turnover)
        
        with subtab8:
            st.subheader("Benefits")
            col1, col2 = st.columns(2)
            
            with col1:
                benefit_id = st.text_input("Benefit ID", key="benefit_id_input")
                employee_id = st.text_input("Employee ID", key="employee_id_benefits_input")
                benefit_type = st.selectbox("Benefit Type", ["Health Insurance", "Dental", "Vision", "401k", "PTO"], key="benefit_type_input")
                enrollment_date = st.date_input("Enrollment Date", key="enrollment_date_input")
                utilization_rate = st.number_input("Utilization Rate (%)", min_value=0.0, max_value=100.0, key="utilization_input")
            
            with col2:
                benefit_cost = st.number_input("Benefit Cost", min_value=0.0, key="benefit_cost_input")
                provider = st.text_input("Provider", key="provider_input")
                coverage_level = st.selectbox("Coverage Level", ["Individual", "Family", "Employee+1"], key="coverage_input")
            
            if st.button("Add Benefit Record"):
                new_benefit = pd.DataFrame([{
                    'benefit_id': benefit_id,
                    'employee_id': employee_id,
                    'benefit_type': benefit_type,
                    'enrollment_date': enrollment_date,
                    'utilization_rate': utilization_rate,
                    'benefit_cost': benefit_cost,
                    'provider': provider,
                    'coverage_level': coverage_level
                }])
                st.session_state.benefits = pd.concat([st.session_state.benefits, new_benefit], ignore_index=True)
                st.success("Benefit record added successfully!")
            
            # Display existing data
            if not st.session_state.benefits.empty:
                st.subheader("Existing Benefit Records")
                display_dataframe_with_index_1(st.session_state.benefits)
    
    with tab4:
        st.subheader("🧪 Sample Dataset for Testing")
        st.write("Load the existing HR dataset from hr.xlsx to test all features of the application.")
        
        st.markdown("""
        **Sample Dataset Features:**
        • Complete HR dataset from hr.xlsx file
        • Real employee data with demographics and performance metrics
        • Full recruitment pipeline with detailed funnel analysis
        • Comprehensive performance reviews and assessments
        • Complete compensation and benefits data
        • Training and development records with ROI tracking
        • Employee engagement surveys with work-life balance metrics
        • Turnover and retention data with cost analysis
        • All HR analytics features ready for testing
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Dataset Overview:**")
            st.write("• **Employees:** 150 records with demographics, performance, tenure")
            st.write("• **Recruitment:** 50 job postings with full pipeline data")
            st.write("• **Performance:** 200 performance reviews across multiple cycles")
            st.write("• **Compensation:** 150 compensation records with salary, bonuses, benefits")
            st.write("• **Training:** 100 training records with costs and outcomes")
            st.write("• **Engagement:** 120 survey responses with multiple metrics")
            st.write("• **Turnover:** 18 separation records with reasons and costs")
            st.write("• **Benefits:** 200 benefit enrollment records")
        
        with col2:
            st.markdown("**🎯 Testing Capabilities:**")
            st.write("• All HR analytics dashboards")
            st.write("• Auto insights and AI-powered analysis")
            st.write("• Risk assessment and predictive analytics")
            st.write("• Recruitment effectiveness analysis")
            st.write("• Performance and productivity metrics")
            st.write("• Compensation equity and benefits analysis")
            st.write("• Retention and attrition patterns")
            st.write("• DEI analysis and workforce planning")
        
        st.markdown("---")
        
        if st.button("🚀 Load Sample Dataset", use_container_width=True, type="primary"):
            try:
                # Load data from hr.xlsx file
                excel_data = pd.read_excel('hr.xlsx', sheet_name=None)
                
                # Load data into session state
                st.session_state.employees = excel_data['Employees']
                st.session_state.recruitment = excel_data['Recruitment']
                st.session_state.performance = excel_data['Performance']
                st.session_state.compensation = excel_data['Compensation']
                st.session_state.training = excel_data['Training']
                st.session_state.engagement = excel_data['Engagement']
                st.session_state.turnover = excel_data['Turnover']
                st.session_state.benefits = excel_data['Benefits']
                
                st.success("✅ Sample dataset loaded successfully!")
                st.info(f"""
                📊 **Dataset Summary:**
                • {len(st.session_state.employees)} employees loaded
                • {len(st.session_state.recruitment)} recruitment records
                • {len(st.session_state.performance)} performance reviews
                • {len(st.session_state.compensation)} compensation records
                • {len(st.session_state.training)} training records
                • {len(st.session_state.engagement)} engagement surveys
                • {len(st.session_state.turnover)} turnover records
                • {len(st.session_state.benefits)} benefit records
                
                🎯 **Ready to test all HR analytics features!**
                """)
                
                # Show sample data preview
                with st.expander("📋 Sample Data Preview", expanded=False):
                    preview_tab1, preview_tab2, preview_tab3, preview_tab4 = st.tabs([
                        "👥 Employees", "🎯 Recruitment", "📊 Performance", "💰 Compensation"
                    ])
                    
                    with preview_tab1:
                        st.write("**Employees Sample (first 10 records):**")
                        display_dataframe_with_index_1(st.session_state.employees.head(10))
                    
                    with preview_tab2:
                        st.write("**Recruitment Sample (first 10 records):**")
                        display_dataframe_with_index_1(st.session_state.recruitment.head(10))
                    
                    with preview_tab3:
                        st.write("**Performance Sample (first 10 records):**")
                        display_dataframe_with_index_1(st.session_state.performance.head(10))
                    
                    with preview_tab4:
                        st.write("**Compensation Sample (first 10 records):**")
                        display_dataframe_with_index_1(st.session_state.compensation.head(10))
                
            except Exception as e:
                st.error(f"❌ Error loading sample dataset: {str(e)}")
                st.info("Please ensure the hr.xlsx file is available in the hr directory.")
        
        st.markdown("---")
        st.markdown("""
        **💡 Tips for Testing:**
        • Use the sample data to explore all analytics features
        • Try different filters and date ranges
        • Test the auto insights and risk assessment
        • Compare results across different departments
        • Export data and generate reports
        • Test all visualization types and charts
        """)

# ============================================================================
# RECRUITMENT ANALYSIS
# ============================================================================

def show_recruitment_analysis():
    st.header("🎯 Recruitment Analysis")
    
    if st.session_state.recruitment.empty:
        st.warning("Please add recruitment data first in the Data Input section.")
        return
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "⏱️ Time to Hire", "💰 Cost Analysis", "🎯 Source Effectiveness", "📈 Detailed Analytics"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.subheader("📊 Recruitment Overview Dashboard")
        
        # Calculate key metrics
        total_postings = len(st.session_state.recruitment)
        total_applications = st.session_state.recruitment['applications_received'].sum()
        total_hires = st.session_state.recruitment['hires_made'].sum()
        total_cost = st.session_state.recruitment['recruitment_cost'].sum()
        avg_time_to_hire = st.session_state.recruitment['time_to_hire_days'].mean()
        conversion_rate = (total_hires / total_applications * 100) if total_applications > 0 else 0
        avg_cost_per_hire = (total_cost / total_hires) if total_hires > 0 else 0
        
        # Summary metrics in a modern card layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📋 Total Job Postings",
                value=f"{total_postings:,}",
                delta=f"{total_hires:,} hires made"
            )
            st.metric(
                label="⏱️ Avg Time to Hire",
                value=f"{avg_time_to_hire:.1f} days",
                delta="Industry avg: 45 days"
            )
        
        with col2:
            st.metric(
                label="📝 Total Applications",
                value=f"{total_applications:,}",
                delta=f"{conversion_rate:.1f}% conversion"
            )
            st.metric(
                label="💰 Avg Cost per Hire",
                value=f"${avg_cost_per_hire:,.0f}",
                delta="Industry avg: $15,000"
            )
        
        with col3:
            st.metric(
                label="✅ Total Hires",
                value=f"{total_hires:,}",
                delta=f"${total_cost:,.0f} total cost"
            )
            st.metric(
                label="📊 Fill Rate",
                value=f"{(total_hires/total_postings*100):.1f}%" if total_postings > 0 else "0%",
                delta="Target: 85%"
            )
        
        st.markdown("---")
        
        # Key insights and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Key Insights")
            
            # Time to hire analysis
            if avg_time_to_hire <= 30:
                st.success("✅ **Excellent Time to Hire:** Below industry average")
            elif avg_time_to_hire <= 45:
                st.info("ℹ️ **Good Time to Hire:** At industry average")
            else:
                st.warning("⚠️ **Slow Time to Hire:** Above industry average")
            
            # Cost analysis
            if avg_cost_per_hire <= 10000:
                st.success("✅ **Efficient Cost per Hire:** Below industry average")
            elif avg_cost_per_hire <= 15000:
                st.info("ℹ️ **Reasonable Cost per Hire:** At industry average")
            else:
                st.warning("⚠️ **High Cost per Hire:** Above industry average")
            
            # Conversion rate analysis
            if conversion_rate >= 5:
                st.success("✅ **Strong Conversion Rate:** High application-to-hire ratio")
            elif conversion_rate >= 2:
                st.info("ℹ️ **Average Conversion Rate:** Typical application-to-hire ratio")
            else:
                st.warning("⚠️ **Low Conversion Rate:** Consider improving candidate quality")
        
        with col2:
            st.subheader("💡 Recommendations")
            
            if avg_time_to_hire > 45:
                st.write("• **Streamline hiring process** - Reduce interview rounds")
                st.write("• **Improve communication** - Faster feedback to candidates")
                st.write("• **Optimize job descriptions** - Clearer requirements")
            
            if avg_cost_per_hire > 15000:
                st.write("• **Review recruitment sources** - Focus on cost-effective channels")
                st.write("• **Optimize advertising spend** - Target specific audiences")
                st.write("• **Consider internal referrals** - Lower cost, higher quality")
            
            if conversion_rate < 2:
                st.write("• **Improve job postings** - More attractive descriptions")
                st.write("• **Enhance employer branding** - Better company presentation")
                st.write("• **Target passive candidates** - Proactive sourcing")
    
    # Tab 2: Time to Hire Analysis
    with tab2:
        st.subheader("⏱️ Time to Hire Analysis")
        
        time_to_hire_data, time_to_hire_msg = calculate_time_to_hire(st.session_state.recruitment)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_days = float(time_to_hire_msg.split(': ')[1].split()[0]) if ': ' in time_to_hire_msg else 0
            st.metric(
                label="Average Time to Hire",
                value=f"{avg_days:.1f} days",
                delta="Industry: 45 days"
            )
        
        with col2:
            if not time_to_hire_data.empty:
                fastest_hire = time_to_hire_data['time_to_hire_days'].min()
                st.metric(
                    label="Fastest Hire",
                    value=f"{fastest_hire:.0f} days",
                    delta="Best performance"
                )
        
        with col3:
            if not time_to_hire_data.empty:
                slowest_hire = time_to_hire_data['time_to_hire_days'].max()
                st.metric(
                    label="Slowest Hire",
                    value=f"{slowest_hire:.0f} days",
                    delta="Needs improvement"
                )
        
        # Interactive filters
        col1, col2 = st.columns(2)
        
        with col1:
            if 'department' in st.session_state.recruitment.columns:
                dept_filter = st.selectbox(
                    "Filter by Department:",
                    ["All"] + list(st.session_state.recruitment['department'].unique())
                )
        
        with col2:
            if 'recruitment_source' in st.session_state.recruitment.columns:
                source_filter = st.selectbox(
                    "Filter by Source:",
                    ["All"] + list(st.session_state.recruitment['recruitment_source'].unique())
                )
        
        # Apply filters
        filtered_data = st.session_state.recruitment.copy()
        if dept_filter != "All":
            filtered_data = filtered_data[filtered_data['department'] == dept_filter]
        if source_filter != "All":
            filtered_data = filtered_data[filtered_data['recruitment_source'] == source_filter]
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            if not filtered_data.empty:
                # Create time to hire trend over time
                # First, ensure we have a date column for grouping
                if 'posting_date' in filtered_data.columns:
                    trend_data = filtered_data.copy()
                    trend_data['posting_date'] = pd.to_datetime(trend_data['posting_date'])
                    trend_data['month'] = trend_data['posting_date'].dt.to_period('M')
                    
                    # Group by month and calculate average time to hire
                    monthly_trend = trend_data.groupby('month')['time_to_hire_days'].agg(['mean', 'count']).reset_index()
                    monthly_trend['month'] = monthly_trend['month'].astype(str)
                    
                    fig_trend = px.line(
                        monthly_trend,
                        x='month',
                        y='mean',
                        title="Time to Hire Trend Over Time",
                        markers=True,
                        line_shape='linear'
                    )
                    fig_trend.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Average Time to Hire (Days)",
                        showlegend=False
                    )
                    fig_trend.update_traces(
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=8, color='#667eea')
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Add trend analysis
                    if len(monthly_trend) > 1:
                        first_month = monthly_trend.iloc[0]['mean']
                        last_month = monthly_trend.iloc[-1]['mean']
                        trend_direction = "improving" if last_month < first_month else "worsening"
                        trend_change = abs(last_month - first_month)
                        st.info(f"📈 **Trend Analysis:** Hiring speed is {trend_direction} by {trend_change:.1f} days over the period")
                else:
                    # Fallback if no date column - show distribution by position order
                    fig_hist = px.histogram(
                        filtered_data,
                        x='time_to_hire_days',
                        title="Time to Hire Distribution (No Date Data)",
                        nbins=15,
                        color_discrete_sequence=['#667eea']
                    )
                    fig_hist.update_layout(
                        xaxis_title="Days to Hire",
                        yaxis_title="Number of Positions",
                        showlegend=False
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            if not filtered_data.empty and 'department' in filtered_data.columns:
                dept_time = filtered_data.groupby('department')['time_to_hire_days'].mean().sort_values()
                fig_dept = px.bar(
                    x=dept_time.index,
                    y=dept_time.values,
                    title="Average Time to Hire by Department",
                    color=dept_time.values,
                    color_continuous_scale='RdYlGn_r'
                )
                fig_dept.update_layout(
                    xaxis_title="Department",
                    yaxis_title="Average Days",
                    showlegend=False
                )
                st.plotly_chart(fig_dept, use_container_width=True)
        
        # Detailed table
        if not filtered_data.empty:
            st.subheader("📊 Detailed Time to Hire Data")
            display_cols = ['position_title', 'department', 'time_to_hire_days', 'applications_received', 'hires_made']
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            st.dataframe(filtered_data[display_cols].sort_values('time_to_hire_days', ascending=True))
    
    # Tab 3: Cost Analysis
    with tab3:
        st.subheader("💰 Cost Analysis")
        
        cost_per_hire_data, cost_per_hire_msg = calculate_cost_per_hire(st.session_state.recruitment)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_cost = float(cost_per_hire_msg.split(': $')[1].replace(',', '')) if ': $' in cost_per_hire_msg else 0
            st.metric(
                label="Average Cost per Hire",
                value=f"${avg_cost:,.0f}",
                delta="Industry: $15,000"
            )
        
        with col2:
            total_cost = st.session_state.recruitment['recruitment_cost'].sum()
            st.metric(
                label="Total Recruitment Cost",
                value=f"${total_cost:,.0f}",
                delta=f"{len(st.session_state.recruitment)} positions"
            )
        
        with col3:
            if not cost_per_hire_data.empty:
                # Calculate cost per hire from the data
                total_cost = cost_per_hire_data['recruitment_cost'].sum()
                total_hires = cost_per_hire_data['hires_made'].sum()
                cost_per_hire = total_cost / total_hires if total_hires > 0 else 0
                st.metric(
                    label="Cost Efficiency",
                    value=f"${cost_per_hire:,.0f}",
                    delta="Per successful hire"
                )
        
        # Cost analysis by department and source
        col1, col2 = st.columns(2)
        
        with col1:
            if 'department' in st.session_state.recruitment.columns:
                dept_cost = st.session_state.recruitment.groupby('department').agg({
                    'recruitment_cost': 'sum',
                    'hires_made': 'sum'
                }).reset_index()
                dept_cost['cost_per_hire'] = dept_cost['recruitment_cost'] / dept_cost['hires_made']
                dept_cost = dept_cost.sort_values('cost_per_hire', ascending=False)
                
                fig_dept_cost = px.bar(
                    dept_cost,
                    x='department',
                    y='cost_per_hire',
                    title="Cost per Hire by Department",
                    color='cost_per_hire',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_dept_cost.update_layout(
                    xaxis_title="Department",
                    yaxis_title="Cost per Hire ($)",
                    showlegend=False
                )
                st.plotly_chart(fig_dept_cost, use_container_width=True)
        
        with col2:
            if 'recruitment_source' in st.session_state.recruitment.columns:
                source_cost = st.session_state.recruitment.groupby('recruitment_source').agg({
                    'recruitment_cost': 'sum',
                    'hires_made': 'sum'
                }).reset_index()
                source_cost['cost_per_hire'] = source_cost['recruitment_cost'] / source_cost['hires_made']
                source_cost = source_cost.sort_values('cost_per_hire', ascending=False)
                
                fig_source_cost = px.bar(
                    source_cost,
                    x='recruitment_source',
                    y='cost_per_hire',
                    title="Cost per Hire by Source",
                    color='cost_per_hire',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_source_cost.update_layout(
                    xaxis_title="Recruitment Source",
                    yaxis_title="Cost per Hire ($)",
                    showlegend=False
                )
                st.plotly_chart(fig_source_cost, use_container_width=True)
        
        # Cost vs effectiveness scatter plot
        if not cost_per_hire_data.empty:
            # Calculate cost per hire for each position
            scatter_data = cost_per_hire_data.copy()
            scatter_data['cost_per_hire'] = scatter_data['recruitment_cost'] / scatter_data['hires_made']
            scatter_data = scatter_data[scatter_data['hires_made'] > 0]  # Filter out positions with no hires
            
            if not scatter_data.empty:
                fig_scatter = px.scatter(
                    scatter_data,
                    x='hires_made',
                    y='recruitment_cost',
                    hover_data=['position_title'],
                    title="Hires vs Recruitment Cost",
                    color='cost_per_hire',
                    color_continuous_scale='viridis',
                    size='hires_made',
                    size_max=20
                )
                fig_scatter.update_layout(
                    xaxis_title="Number of Hires",
                    yaxis_title="Recruitment Cost ($)"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Tab 4: Source Effectiveness
    with tab4:
        st.subheader("🎯 Source Effectiveness Analysis")
        
        source_data, source_msg = calculate_source_effectiveness(st.session_state.recruitment)
        
        # Top performing source
        top_source = source_msg.split(': ')[1] if ': ' in source_msg else "N/A"
        st.info(f"🏆 **Top Performing Source:** {top_source}")
        
        # Source effectiveness visualization
        if not source_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_source = px.bar(
                    source_data,
                    x='recruitment_source',
                    y='effectiveness_rate',
                    title="Source Effectiveness Rate",
                    color='effectiveness_rate',
                    color_continuous_scale='plasma',
                    text='effectiveness_rate'
                )
                fig_source.update_layout(
                    xaxis_title="Recruitment Source",
                    yaxis_title="Effectiveness Rate (%)",
                    showlegend=False
                )
                fig_source.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                st.plotly_chart(fig_source, use_container_width=True)
            
            with col2:
                # Source comparison metrics
                source_metrics = st.session_state.recruitment.groupby('recruitment_source').agg({
                    'applications_received': 'sum',
                    'hires_made': 'sum',
                    'recruitment_cost': 'sum'
                }).reset_index()
                source_metrics['conversion_rate'] = (source_metrics['hires_made'] / source_metrics['applications_received'] * 100)
                source_metrics['cost_per_hire'] = source_metrics['recruitment_cost'] / source_metrics['hires_made']
                
                fig_metrics = px.scatter(
                    source_metrics,
                    x='conversion_rate',
                    y='cost_per_hire',
                    size='hires_made',
                    hover_data=['recruitment_source'],
                    title="Source Performance: Conversion vs Cost",
                    color='recruitment_source'
                )
                fig_metrics.update_layout(
                    xaxis_title="Conversion Rate (%)",
                    yaxis_title="Cost per Hire ($)"
                )
                st.plotly_chart(fig_metrics, use_container_width=True)
        
        # Source recommendations
        st.subheader("💡 Source Optimization Recommendations")
        
        if not source_data.empty:
            best_source = source_data.loc[source_data['effectiveness_rate'].idxmax()]
            worst_source = source_data.loc[source_data['effectiveness_rate'].idxmin()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"✅ **Best Source:** {best_source['recruitment_source']}")
                st.write(f"• Effectiveness Rate: {best_source['effectiveness_rate']:.1f}%")
                st.write("• **Recommendation:** Increase investment in this source")
                st.write("• **Action:** Allocate more budget and focus")
            
            with col2:
                st.warning(f"⚠️ **Needs Improvement:** {worst_source['recruitment_source']}")
                st.write(f"• Effectiveness Rate: {worst_source['effectiveness_rate']:.1f}%")
                st.write("• **Recommendation:** Review and optimize or reduce investment")
                st.write("• **Action:** Analyze why performance is low")
    
    # Tab 5: Detailed Analytics
    with tab5:
        st.subheader("📈 Detailed Recruitment Analytics")
        
        # Application drop-off analysis
        drop_off_data, drop_off_msg = calculate_application_drop_off(st.session_state.recruitment)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📉 Application Drop-Off Analysis**")
            if not drop_off_data.empty:
                fig_drop = px.bar(
                    drop_off_data,
                    x='stage',
                    y='drop_off_rate',
                    title="Application Drop-Off Rates",
                    color='drop_off_rate',
                    color_continuous_scale='RdYlBu_r',
                    text='drop_off_rate'
                )
                fig_drop.update_layout(
                    xaxis_title="Application Stage",
                    yaxis_title="Drop-Off Rate (%)",
                    showlegend=False
                )
                fig_drop.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                st.plotly_chart(fig_drop, use_container_width=True)
        
        with col2:
            st.markdown("**📊 Recruitment Pipeline Metrics**")
            
            # Calculate pipeline metrics
            total_apps = st.session_state.recruitment['applications_received'].sum()
            total_hires = st.session_state.recruitment['hires_made'].sum()
            
            st.metric("Total Applications", f"{total_apps:,}")
            st.metric("Total Hires", f"{total_hires:,}")
            st.metric("Conversion Rate", f"{(total_hires/total_apps*100):.1f}%" if total_apps > 0 else "0%")
            
            # Pipeline efficiency
            if total_apps > 0:
                efficiency = (total_hires / total_apps) * 100
                if efficiency >= 5:
                    st.success("✅ **High Pipeline Efficiency**")
                elif efficiency >= 2:
                    st.info("ℹ️ **Average Pipeline Efficiency**")
                else:
                    st.warning("⚠️ **Low Pipeline Efficiency**")
        
        # Detailed data table with filters
        st.subheader("📋 Detailed Recruitment Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'department' in st.session_state.recruitment.columns:
                dept_filter = st.selectbox(
                    "Filter by Department:",
                    ["All"] + list(st.session_state.recruitment['department'].unique()),
                    key="detail_dept"
                )
        
        with col2:
            if 'recruitment_source' in st.session_state.recruitment.columns:
                source_filter = st.selectbox(
                    "Filter by Source:",
                    ["All"] + list(st.session_state.recruitment['recruitment_source'].unique()),
                    key="detail_source"
                )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                ["Time to Hire", "Cost", "Applications", "Hires"]
            )
        
        # Apply filters
        filtered_detail = st.session_state.recruitment.copy()
        if dept_filter != "All":
            filtered_detail = filtered_detail[filtered_detail['department'] == dept_filter]
        if source_filter != "All":
            filtered_detail = filtered_detail[filtered_detail['recruitment_source'] == source_filter]
        
        # Sort data
        if sort_by == "Time to Hire":
            filtered_detail = filtered_detail.sort_values('time_to_hire_days', ascending=True)
        elif sort_by == "Cost":
            filtered_detail = filtered_detail.sort_values('recruitment_cost', ascending=False)
        elif sort_by == "Applications":
            filtered_detail = filtered_detail.sort_values('applications_received', ascending=False)
        elif sort_by == "Hires":
            filtered_detail = filtered_detail.sort_values('hires_made', ascending=False)
        
        # Display filtered data
        display_cols = ['position_title', 'department', 'recruitment_source', 'applications_received', 
                       'hires_made', 'time_to_hire_days', 'recruitment_cost']
        display_cols = [col for col in display_cols if col in filtered_detail.columns]
        
        st.dataframe(filtered_detail[display_cols], use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Recruitment Data"):
            csv = filtered_detail.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="recruitment_analysis.csv",
                mime="text/csv"
            )

# ============================================================================
# EMPLOYEE PERFORMANCE ANALYSIS
# ============================================================================

def show_employee_performance():
    st.header("📊 Employee Performance Analysis")
    
    if st.session_state.performance.empty:
        st.warning("Please add performance data first in the Data Input section.")
        return
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "📈 Performance Trends", "🎯 Goal Analysis", "📋 Detailed Analytics", "🔍 Individual Performance"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.subheader("📊 Performance Overview Dashboard")
        
        # Calculate key metrics
        total_reviews = len(st.session_state.performance)
        avg_performance = st.session_state.performance['performance_rating'].mean()
        avg_goal_achievement = st.session_state.performance['goal_achievement_rate'].mean()
        avg_productivity = st.session_state.performance['productivity_score'].mean()
        high_performers = len(st.session_state.performance[st.session_state.performance['performance_rating'] >= 4])
        low_performers = len(st.session_state.performance[st.session_state.performance['performance_rating'] < 3])
        
        # Summary metrics in modern card layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📋 Total Performance Reviews",
                value=f"{total_reviews:,}",
                delta=f"{high_performers} high performers"
            )
            st.metric(
                label="📈 Average Performance Rating",
                value=f"{avg_performance:.1f}/5",
                delta="Industry avg: 3.5/5"
            )
        
        with col2:
            st.metric(
                label="🎯 Goal Achievement Rate",
                value=f"{avg_goal_achievement:.1f}%",
                delta="Target: 80%"
            )
            st.metric(
                label="⚡ Average Productivity Score",
                value=f"{avg_productivity:.1f}/5",
                delta="Industry avg: 3.2/5"
            )
        
        with col3:
            high_perf_pct = (high_performers / total_reviews * 100) if total_reviews > 0 else 0
            st.metric(
                label="🏆 High Performers",
                value=f"{high_perf_pct:.1f}%",
                delta=f"{high_performers} employees"
            )
            low_perf_pct = (low_performers / total_reviews * 100) if total_reviews > 0 else 0
            st.metric(
                label="⚠️ Low Performers",
                value=f"{low_perf_pct:.1f}%",
                delta=f"{low_performers} employees"
            )
        
        st.markdown("---")
        
        # Key insights and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Key Insights")
            
            # Performance analysis
            if avg_performance >= 4.0:
                st.success("✅ **Excellent Performance:** Above industry average")
            elif avg_performance >= 3.5:
                st.info("ℹ️ **Good Performance:** At industry average")
            else:
                st.warning("⚠️ **Below Average Performance:** Needs improvement")
            
            # Goal achievement analysis
            if avg_goal_achievement >= 80:
                st.success("✅ **Strong Goal Achievement:** Meeting targets")
            elif avg_goal_achievement >= 60:
                st.info("ℹ️ **Moderate Goal Achievement:** Room for improvement")
            else:
                st.warning("⚠️ **Low Goal Achievement:** Significant improvement needed")
            
            # High performer analysis
            if high_perf_pct >= 30:
                st.success("✅ **Strong High Performer Pool:** Excellent talent")
            elif high_perf_pct >= 15:
                st.info("ℹ️ **Moderate High Performer Pool:** Good talent base")
            else:
                st.warning("⚠️ **Limited High Performer Pool:** Consider development programs")
        
        with col2:
            st.subheader("💡 Recommendations")
            
            if avg_performance < 3.5:
                st.write("• **Performance Improvement Plans** - Target low performers")
                st.write("• **Training & Development** - Enhance skills and capabilities")
                st.write("• **Clear Expectations** - Set specific, measurable goals")
            
            if avg_goal_achievement < 80:
                st.write("• **Goal Setting Workshops** - Improve goal clarity")
                st.write("• **Regular Check-ins** - Monitor progress more frequently")
                st.write("• **Resource Allocation** - Ensure employees have needed tools")
            
            if high_perf_pct < 15:
                st.write("• **High Potential Programs** - Identify and develop top talent")
                st.write("• **Recognition Programs** - Reward and retain high performers")
                st.write("• **Career Development** - Provide growth opportunities")
    
    # Tab 2: Performance Trends
    with tab2:
        st.subheader("📈 Performance Trends Analysis")
        
        trends_data, trends_msg = calculate_performance_trends(st.session_state.performance)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latest_perf = float(trends_msg.split(': ')[1].split('/')[0]) if ': ' in trends_msg else 0
            st.metric(
                label="Latest Performance",
                value=f"{latest_perf:.1f}/5",
                delta="Industry: 3.5/5"
            )
        
        with col2:
            if not trends_data.empty and len(trends_data) > 1:
                first_perf = trends_data.iloc[0]['avg_performance']
                last_perf = trends_data.iloc[-1]['avg_performance']
                trend_change = last_perf - first_perf
                trend_direction = "improving" if trend_change > 0 else "declining"
                st.metric(
                    label="Performance Trend",
                    value=f"{trend_change:+.2f}",
                    delta=f"{trend_direction}"
                )
        
        with col3:
            if not trends_data.empty:
                best_perf = trends_data['avg_performance'].max()
                st.metric(
                    label="Best Performance",
                    value=f"{best_perf:.1f}/5",
                    delta="Peak performance"
                )
        
        # Interactive filters
        col1, col2 = st.columns(2)
        
        # Initialize filter variables
        dept_filter = "All"
        cycle_filter = "All"
        
        with col1:
            if 'department' in st.session_state.performance.columns:
                dept_filter = st.selectbox(
                    "Filter by Department:",
                    ["All"] + list(st.session_state.performance['department'].unique()),
                    key="perf_dept"
                )
        
        with col2:
            if 'review_cycle' in st.session_state.performance.columns:
                cycle_filter = st.selectbox(
                    "Filter by Review Cycle:",
                    ["All"] + list(st.session_state.performance['review_cycle'].unique()),
                    key="perf_cycle"
                )
        
        # Apply filters
        filtered_perf = st.session_state.performance.copy()
        if dept_filter != "All":
            filtered_perf = filtered_perf[filtered_perf['department'] == dept_filter]
        if cycle_filter != "All":
            filtered_perf = filtered_perf[filtered_perf['review_cycle'] == cycle_filter]
        
        # Merge with employee data to get names and other employee information
        if not st.session_state.employees.empty and not filtered_perf.empty:
            filtered_perf = filtered_perf.merge(
                st.session_state.employees[['employee_id', 'first_name', 'last_name', 'department', 'job_title']], 
                on='employee_id', 
                how='left'
            )
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            if not trends_data.empty:
                fig_trends = px.line(
                    trends_data,
                    x='review_cycle',
                    y='avg_performance',
                    title="Performance Trends Over Time",
                    markers=True,
                    line_shape='linear'
                )
                fig_trends.update_layout(
                    xaxis_title="Review Cycle",
                    yaxis_title="Average Performance Rating",
                    showlegend=False
                )
                fig_trends.update_traces(
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#667eea')
                )
                st.plotly_chart(fig_trends, use_container_width=True)
        
        with col2:
            if not filtered_perf.empty and 'department' in filtered_perf.columns:
                dept_perf = filtered_perf.groupby('department')['performance_rating'].mean().sort_values(ascending=False)
                fig_dept = px.bar(
                    x=dept_perf.index,
                    y=dept_perf.values,
                    title="Average Performance by Department",
                    color=dept_perf.values,
                    color_continuous_scale='RdYlGn'
                )
                fig_dept.update_layout(
                    xaxis_title="Department",
                    yaxis_title="Average Performance Rating",
                    showlegend=False
                )
                st.plotly_chart(fig_dept, use_container_width=True)
        
        # Interactive Performance Categories
        if not filtered_perf.empty:
            st.subheader("👥 Employee Performance Categories")
            
            # Performance categories with interactive buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                high_performers = filtered_perf[filtered_perf['performance_rating'] >= 4.0]
                high_count = len(high_performers)
                if st.button(f"🏆 High Performers ({high_count})", use_container_width=True, key="btn_high_perf"):
                    st.session_state.selected_perf_category = "High Performers"
            
            with col2:
                good_performers = filtered_perf[(filtered_perf['performance_rating'] >= 3.0) & (filtered_perf['performance_rating'] < 4.0)]
                good_count = len(good_performers)
                if st.button(f"✅ Good Performers ({good_count})", use_container_width=True, key="btn_good_perf"):
                    st.session_state.selected_perf_category = "Good Performers"
            
            with col3:
                avg_performers = filtered_perf[(filtered_perf['performance_rating'] >= 2.0) & (filtered_perf['performance_rating'] < 3.0)]
                avg_count = len(avg_performers)
                if st.button(f"🟡 Average Performers ({avg_count})", use_container_width=True, key="btn_avg_perf"):
                    st.session_state.selected_perf_category = "Average Performers"
            
            with col4:
                low_performers = filtered_perf[filtered_perf['performance_rating'] < 2.0]
                low_count = len(low_performers)
                if st.button(f"⚠️ Low Performers ({low_count})", use_container_width=True, key="btn_low_perf"):
                    st.session_state.selected_perf_category = "Low Performers"
            
            # Initialize session state if not exists
            if 'selected_perf_category' not in st.session_state:
                st.session_state.selected_perf_category = "High Performers"
            
            # Display selected category employees
            st.markdown(f"**📋 {st.session_state.selected_perf_category} Details:**")
            
            if st.session_state.selected_perf_category == "High Performers":
                selected_employees = high_performers
                color_style = "🟢"
            elif st.session_state.selected_perf_category == "Good Performers":
                selected_employees = good_performers
                color_style = "🟡"
            elif st.session_state.selected_perf_category == "Average Performers":
                selected_employees = avg_performers
                color_style = "🟠"
            else:  # Low Performers
                selected_employees = low_performers
                color_style = "🔴"
            
            if not selected_employees.empty:
                # Summary metrics for selected category
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_rating = selected_employees['performance_rating'].mean()
                    st.metric(
                        label=f"{color_style} Average Rating",
                        value=f"{avg_rating:.1f}/5",
                        delta=f"{len(selected_employees)} employees"
                    )
                
                with col2:
                    if 'goal_achievement_rate' in selected_employees.columns:
                        avg_goal = selected_employees['goal_achievement_rate'].mean()
                        st.metric(
                            label="🎯 Goal Achievement",
                            value=f"{avg_goal:.1f}%",
                            delta="Average"
                        )
                
                with col3:
                    if 'productivity_score' in selected_employees.columns:
                        avg_prod = selected_employees['productivity_score'].mean()
                        st.metric(
                            label="⚡ Productivity",
                            value=f"{avg_prod:.1f}/5",
                            delta="Average"
                        )
                
                # Employee list with all available information
                st.markdown("**📊 Employee Details Table:**")
                
                # Get all available columns for display
                available_cols = selected_employees.columns.tolist()
                
                # Define priority columns (these will be shown first)
                priority_cols = ['first_name', 'last_name', 'department', 'job_title', 'performance_rating']
                
                # Add other relevant columns if they exist (excluding review variables)
                additional_cols = ['goal_achievement_rate', 'productivity_score', 'skills_assessment']
                
                # Build display columns list
                display_cols = []
                
                # Add priority columns first (if they exist)
                for col in priority_cols:
                    if col in available_cols:
                        display_cols.append(col)
                
                # Add additional columns if they exist
                for col in additional_cols:
                    if col in available_cols and col not in display_cols:
                        display_cols.append(col)
                
                # Add any remaining columns that might be useful (excluding review variables)
                excluded_cols = ['employee_id', 'review_id', 'reviewer_id', 'review_date', 'review_cycle']
                remaining_cols = [col for col in available_cols if col not in display_cols and col not in excluded_cols]
                display_cols.extend(remaining_cols)
                
                if display_cols:
                    # Sort by performance rating (highest first for high performers, lowest first for low performers)
                    sort_ascending = st.session_state.selected_perf_category in ["Low Performers", "Average Performers"]
                    
                    # Create a copy with only display columns and sort
                    display_data = selected_employees[display_cols].copy()
                    
                    # Sort by performance rating if it exists
                    if 'performance_rating' in display_cols:
                        display_data = display_data.sort_values('performance_rating', ascending=sort_ascending)
                    
                    # Display the table with all employee information
                    st.dataframe(display_data, use_container_width=True, height=400)
                    
                    # Show table summary
                    st.info(f"📋 **Table Summary:** Showing {len(display_data)} employees in {st.session_state.selected_perf_category} category with {len(display_cols)} data columns.")
                else:
                    st.warning("No displayable columns found in the employee data.")
                
                # Export option
                if st.button(f"📥 Export {st.session_state.selected_perf_category} Data", key=f"export_{st.session_state.selected_perf_category}"):
                    csv = sorted_employees.to_csv(index=False)
                    st.download_button(
                        label=f"Download {st.session_state.selected_perf_category} CSV",
                        data=csv,
                        file_name=f"{st.session_state.selected_perf_category.replace(' ', '_').lower()}_employees.csv",
                        mime="text/csv"
                    )
            else:
                st.info(f"No employees found in the {st.session_state.selected_perf_category} category.")
    
    # Tab 3: Goal Analysis
    with tab3:
        st.subheader("🎯 Advanced Goal Achievement Analysis")
        
        goal_data, goal_msg = calculate_goal_achievement_rate(st.session_state.performance)
        
        # Enhanced summary metrics with better insights
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            goal_rate = float(goal_msg.split(': ')[1].split('%')[0]) if ': ' in goal_msg else 0
            goal_status = "✅ Exceeding Target" if goal_rate >= 80 else "⚠️ Below Target" if goal_rate >= 60 else "🔴 Critical"
            st.metric(
                label="🎯 Overall Goal Achievement",
                value=f"{goal_rate:.1f}%",
                delta=goal_status
            )
        
        with col2:
            if not st.session_state.performance.empty:
                goal_std = st.session_state.performance['goal_achievement_rate'].std()
                consistency_status = "✅ High Consistency" if goal_std <= 15 else "⚠️ Moderate Variability" if goal_std <= 25 else "🔴 High Variability"
                st.metric(
                    label="📊 Goal Consistency",
                    value=f"{goal_std:.1f}%",
                    delta=consistency_status
                )
        
        with col3:
            if not st.session_state.performance.empty:
                high_goal_achievers = len(st.session_state.performance[st.session_state.performance['goal_achievement_rate'] >= 90])
                total_employees = len(st.session_state.performance)
                high_achiever_pct = (high_goal_achievers / total_employees * 100) if total_employees > 0 else 0
                st.metric(
                    label="🏆 Elite Achievers",
                    value=f"{high_goal_achievers}",
                    delta=f"{high_achiever_pct:.1f}% of workforce"
                )
        
        with col4:
            if not st.session_state.performance.empty:
                low_goal_achievers = len(st.session_state.performance[st.session_state.performance['goal_achievement_rate'] < 60])
                total_employees = len(st.session_state.performance)
                low_achiever_pct = (low_goal_achievers / total_employees * 100) if total_employees > 0 else 0
                st.metric(
                    label="⚠️ At-Risk Employees",
                    value=f"{low_goal_achievers}",
                    delta=f"{low_achiever_pct:.1f}% need support"
                )
        
        # Advanced goal achievement visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.performance.empty:
                # Goal Achievement Categories Pie Chart
                goal_categories = pd.cut(
                    st.session_state.performance['goal_achievement_rate'],
                    bins=[0, 60, 80, 90, 100],
                    labels=['Critical (<60%)', 'Needs Improvement (60-80%)', 'Good (80-90%)', 'Excellent (90-100%)']
                )
                goal_cat_counts = goal_categories.value_counts()
                
                fig_goal_categories = px.pie(
                    values=goal_cat_counts.values,
                    names=goal_cat_counts.index,
                    title="🎯 Goal Achievement Categories Distribution",
                    color_discrete_sequence=['#ff6b6b', '#ffd93d', '#6bcf7f', '#4ecdc4']
                )
                fig_goal_categories.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_goal_categories, use_container_width=True)
        
        with col2:
            if not st.session_state.performance.empty and 'department' in st.session_state.performance.columns:
                # Enhanced Department Goal Analysis with count and percentage
                dept_goal_analysis = st.session_state.performance.groupby('department').agg({
                    'goal_achievement_rate': ['mean', 'count', 'std']
                }).round(1)
                dept_goal_analysis.columns = ['avg_achievement', 'employee_count', 'std_deviation']
                dept_goal_analysis = dept_goal_analysis.sort_values('avg_achievement', ascending=False)
                
                # Create bubble chart showing department performance
                fig_dept_bubble = px.scatter(
                    x=dept_goal_analysis['avg_achievement'],
                    y=dept_goal_analysis['std_deviation'],
                    size=dept_goal_analysis['employee_count'],
                    title="📊 Department Goal Performance Analysis",
                    labels={'x': 'Average Goal Achievement (%)', 'y': 'Standard Deviation (%)', 'size': 'Employee Count'},
                    hover_name=dept_goal_analysis.index,
                    color=dept_goal_analysis['avg_achievement'],
                    color_continuous_scale='RdYlGn'
                )
                fig_dept_bubble.update_layout(
                    xaxis_title="Average Goal Achievement (%)",
                    yaxis_title="Goal Consistency (Std Dev %)",
                    showlegend=False
                )
                st.plotly_chart(fig_dept_bubble, use_container_width=True)
        
        # Advanced Goal Analytics Section
        st.markdown("---")
        st.subheader("📊 Advanced Goal Analytics & Insights")
        
        # Goal vs Performance correlation with enhanced analysis
        if not st.session_state.performance.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Enhanced correlation scatter plot
                fig_corr = px.scatter(
                    st.session_state.performance,
                    x='goal_achievement_rate',
                    y='performance_rating',
                    title="🎯 Goal Achievement vs Performance Rating",
                    color='performance_rating',
                    color_continuous_scale='plasma',
                    hover_data=['first_name', 'last_name', 'department'] if 'first_name' in st.session_state.performance.columns else None
                )
                fig_corr.update_layout(
                    xaxis_title="Goal Achievement Rate (%)",
                    yaxis_title="Performance Rating"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            
            with col2:
                # Goal Achievement Trends Analysis
                if 'review_cycle' in st.session_state.performance.columns:
                    goal_trends = st.session_state.performance.groupby('review_cycle')['goal_achievement_rate'].agg(['mean', 'count']).reset_index()
                    goal_trends.columns = ['Review Cycle', 'Average Goal Achievement', 'Employee Count']
                    
                    fig_trends = px.line(
                        goal_trends,
                        x='Review Cycle',
                        y='Average Goal Achievement',
                        title="📈 Goal Achievement Trends Over Time",
                        markers=True,
                        line_shape='linear'
                    )
                    fig_trends.update_layout(
                        xaxis_title="Review Cycle",
                        yaxis_title="Average Goal Achievement (%)",
                        showlegend=False
                    )
                    fig_trends.update_traces(
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=8, color='#667eea')
                    )
                    st.plotly_chart(fig_trends, use_container_width=True)
                else:
                    # Fallback: Goal Achievement Distribution by Performance Level
                    performance_goal_analysis = st.session_state.performance.groupby('performance_rating')['goal_achievement_rate'].mean().reset_index()
                    fig_perf_goal = px.bar(
                        performance_goal_analysis,
                        x='performance_rating',
                        y='goal_achievement_rate',
                        title="📊 Goal Achievement by Performance Level",
                        color='goal_achievement_rate',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_perf_goal.update_layout(
                        xaxis_title="Performance Rating",
                        yaxis_title="Average Goal Achievement (%)",
                        showlegend=False
                    )
                    st.plotly_chart(fig_perf_goal, use_container_width=True)
        
        # Enhanced correlation analysis with actionable insights
        if not st.session_state.performance.empty:
            correlation = st.session_state.performance['goal_achievement_rate'].corr(st.session_state.performance['performance_rating'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Correlation Analysis**")
                if correlation > 0.7:
                    st.success(f"✅ **Strong Positive Correlation:** {correlation:.2f}")
                    st.write("• High goal achievement strongly correlates with high performance")
                    st.write("• Goal-setting is effective and aligned with performance")
                    st.write("• Consider expanding goal-based performance management")
                elif correlation > 0.3:
                    st.info(f"ℹ️ **Moderate Positive Correlation:** {correlation:.2f}")
                    st.write("• Goal achievement moderately correlates with performance")
                    st.write("• Some alignment between goals and performance outcomes")
                    st.write("• Review goal-setting process for better alignment")
                else:
                    st.warning(f"⚠️ **Weak Correlation:** {correlation:.2f}")
                    st.write("• Goal achievement and performance are not strongly related")
                    st.write("• Goals may not be properly aligned with performance metrics")
                    st.write("• Consider revising goal-setting strategy")
            
            with col2:
                st.markdown("**💡 Strategic Insights**")
                
                # Calculate additional insights
                high_performers_low_goals = len(st.session_state.performance[
                    (st.session_state.performance['performance_rating'] >= 4.0) & 
                    (st.session_state.performance['goal_achievement_rate'] < 70)
                ])
                
                low_performers_high_goals = len(st.session_state.performance[
                    (st.session_state.performance['performance_rating'] < 3.0) & 
                    (st.session_state.performance['goal_achievement_rate'] >= 80)
                ])
                
                st.write(f"**🔍 Anomaly Analysis:**")
                st.write(f"• {high_performers_low_goals} high performers with low goal achievement")
                st.write(f"• {low_performers_high_goals} low performers with high goal achievement")
                
                if high_performers_low_goals > 0:
                    st.info("💡 **Insight:** Some high performers may have unrealistic goals")
                
                if low_performers_high_goals > 0:
                    st.info("💡 **Insight:** Some low performers may have easy goals")
                
                # Goal setting recommendations
                avg_goal = st.session_state.performance['goal_achievement_rate'].mean()
                if avg_goal > 90:
                    st.success("🎯 **Goal Setting:** Goals may be too easy - consider increasing challenge")
                elif avg_goal < 60:
                    st.warning("🎯 **Goal Setting:** Goals may be too difficult - consider adjusting targets")
                else:
                    st.info("🎯 **Goal Setting:** Goals appear to be appropriately challenging")
        
        # Goal Performance Dashboard with Actionable Recommendations
        st.markdown("---")
        st.subheader("📋 Goal Performance Dashboard & Action Plan")
        
        if not st.session_state.performance.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🎯 Goal Achievement KPIs**")
                
                # Calculate key goal metrics
                goal_metrics = {
                    'Excellent (90-100%)': len(st.session_state.performance[st.session_state.performance['goal_achievement_rate'] >= 90]),
                    'Good (80-89%)': len(st.session_state.performance[(st.session_state.performance['goal_achievement_rate'] >= 80) & (st.session_state.performance['goal_achievement_rate'] < 90)]),
                    'Needs Improvement (60-79%)': len(st.session_state.performance[(st.session_state.performance['goal_achievement_rate'] >= 60) & (st.session_state.performance['goal_achievement_rate'] < 80)]),
                    'Critical (<60%)': len(st.session_state.performance[st.session_state.performance['goal_achievement_rate'] < 60])
                }
                
                total_employees = len(st.session_state.performance)
                for category, count in goal_metrics.items():
                    percentage = (count / total_employees * 100) if total_employees > 0 else 0
                    st.write(f"• **{category}:** {count} ({percentage:.1f}%)")
            
            with col2:
                st.markdown("**📊 Department Performance**")
                
                if 'department' in st.session_state.performance.columns:
                    dept_performance = st.session_state.performance.groupby('department').agg({
                        'goal_achievement_rate': ['mean', 'count'],
                        'performance_rating': 'mean'
                    }).round(1)
                    dept_performance.columns = ['Avg Goal Achievement', 'Employee Count', 'Avg Performance']
                    dept_performance = dept_performance.sort_values('Avg Goal Achievement', ascending=False)
                    
                    # Show top 3 and bottom 3 departments
                    st.write("**🏆 Top Performing Departments:**")
                    for dept in dept_performance.head(3).index:
                        avg_goal = dept_performance.loc[dept, 'Avg Goal Achievement']
                        emp_count = dept_performance.loc[dept, 'Employee Count']
                        st.write(f"• {dept}: {avg_goal}% ({emp_count} employees)")
                    
                    st.write("**⚠️ Departments Needing Focus:**")
                    for dept in dept_performance.tail(3).index:
                        avg_goal = dept_performance.loc[dept, 'Avg Goal Achievement']
                        emp_count = dept_performance.loc[dept, 'Employee Count']
                        st.write(f"• {dept}: {avg_goal}% ({emp_count} employees)")
            
            with col3:
                st.markdown("**🚀 Action Recommendations**")
                
                # Generate actionable recommendations based on data
                avg_goal_achievement = st.session_state.performance['goal_achievement_rate'].mean()
                goal_std = st.session_state.performance['goal_achievement_rate'].std()
                
                if avg_goal_achievement < 70:
                    st.warning("🎯 **Immediate Actions Needed:**")
                    st.write("• Review goal-setting process")
                    st.write("• Provide additional training")
                    st.write("• Implement support programs")
                elif avg_goal_achievement < 80:
                    st.info("📈 **Improvement Opportunities:**")
                    st.write("• Enhance goal clarity")
                    st.write("• Increase manager support")
                    st.write("• Regular progress check-ins")
                else:
                    st.success("✅ **Maintain Excellence:**")
                    st.write("• Continue current practices")
                    st.write("• Share best practices")
                    st.write("• Set stretch goals")
                
                if goal_std > 20:
                    st.warning("📊 **Consistency Issues:**")
                    st.write("• Standardize goal-setting approach")
                    st.write("• Provide manager training")
                    st.write("• Implement goal templates")
    
    # Tab 4: Detailed Analytics
    with tab4:
        st.subheader("📋 Detailed Performance Analytics")
        
        # Productivity analysis
        if not st.session_state.employees.empty:
            productivity_data, productivity_msg = calculate_employee_productivity(st.session_state.performance, st.session_state.employees)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**⚡ Productivity Analysis**")
                prod_score = float(productivity_msg.split(': ')[1].split('/')[0]) if ': ' in productivity_msg else 0
                st.metric(
                    label="Average Productivity Score",
                    value=f"{prod_score:.1f}/5",
                    delta="Industry: 3.2/5"
                )
                
                if not productivity_data.empty:
                    fig_prod = px.scatter(
                        productivity_data,
                        x='performance_rating',
                        y='productivity_score',
                        title="Performance vs Productivity",
                        color='productivity_score',
                        color_continuous_scale='plasma',
                        hover_data=['first_name', 'last_name', 'department']
                    )
                    fig_prod.update_layout(
                        xaxis_title="Performance Rating",
                        yaxis_title="Productivity Score"
                    )
                    st.plotly_chart(fig_prod, use_container_width=True)
            
            with col2:
                st.markdown("**🎯 Skills Assessment Analysis**")
                if 'skills_assessment' in st.session_state.performance.columns:
                    # Enhanced skills analysis with more detailed metrics
                    skills_analysis = st.session_state.performance.groupby('skills_assessment').agg({
                        'performance_rating': ['mean', 'count'],
                        'goal_achievement_rate': 'mean'
                    }).round(2)
                    skills_analysis.columns = ['Avg Performance', 'Employee Count', 'Avg Goal Achievement']
                    skills_analysis = skills_analysis.reset_index()
                    
                    # Calculate percentages and additional metrics
                    total_employees = skills_analysis['Employee Count'].sum()
                    skills_analysis['Percentage'] = (skills_analysis['Employee Count'] / total_employees * 100).round(1)
                    skills_analysis['Performance Level'] = skills_analysis['Avg Performance'].apply(
                        lambda x: 'High' if x >= 4.0 else 'Good' if x >= 3.0 else 'Average' if x >= 2.0 else 'Low'
                    )
                    
                    # Create enhanced pie chart with descriptive labels
                    # Map numerical skills assessment to descriptive categories
                    skills_analysis['Skills_Level'] = skills_analysis['skills_assessment'].apply(
                        lambda x: 'Expert Level (4.5-5.0)' if x >= 4.5 else
                                 'Advanced Level (4.0-4.4)' if x >= 4.0 else
                                 'Proficient Level (3.5-3.9)' if x >= 3.5 else
                                 'Developing Level (3.0-3.4)' if x >= 3.0 else
                                 'Basic Level (2.0-2.9)' if x >= 2.0 else
                                 'Needs Development (<2.0)'
                    )
                    
                    # Create enhanced pie chart with descriptive labels
                    fig_skills = px.pie(
                        skills_analysis,
                        values='Employee Count',
                        names='Skills_Level',
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        hover_data=['skills_assessment', 'Percentage', 'Avg Performance', 'Avg Goal Achievement', 'Performance Level']
                    )
                    
                    # Customize tooltip template for better information display
                    fig_skills.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="<b>%{label}</b><br>" +
                                    "Skills Score: %{customdata[0]}/5<br>" +
                                    "Employees: %{value}<br>" +
                                    "Percentage: %{customdata[1]}%<br>" +
                                    "Avg Performance: %{customdata[2]}/5<br>" +
                                    "Avg Goal Achievement: %{customdata[3]}%<br>" +
                                    "Performance Level: %{customdata[4]}<br>" +
                                    "<extra></extra>"
                    )
                    
                    # Display the pie chart
                    st.plotly_chart(fig_skills, use_container_width=True)
                    
                    # Add skills insights below the chart
                    st.markdown("**📊 Skills Insights:**")
                    
                    # Find top and bottom performing skills categories
                    top_skills = skills_analysis.nlargest(2, 'Avg Performance')
                    bottom_skills = skills_analysis.nsmallest(2, 'Avg Performance')
                    
                    col_insight1, col_insight2 = st.columns(2)
                    
                    with col_insight1:
                        st.markdown("**🏆 Top Performing Skills:**")
                        for _, skill in top_skills.iterrows():
                            skill_level = 'Expert Level (4.5-5.0)' if skill['skills_assessment'] >= 4.5 else \
                                         'Advanced Level (4.0-4.4)' if skill['skills_assessment'] >= 4.0 else \
                                         'Proficient Level (3.5-3.9)' if skill['skills_assessment'] >= 3.5 else \
                                         'Developing Level (3.0-3.4)' if skill['skills_assessment'] >= 3.0 else \
                                         'Basic Level (2.0-2.9)' if skill['skills_assessment'] >= 2.0 else \
                                         'Needs Development (<2.0)'
                            st.write(f"• **{skill_level}:** {skill['Avg Performance']}/5 ({skill['Employee Count']} employees)")
                    
                    with col_insight2:
                        st.markdown("**⚠️ Skills Needing Development:**")
                        for _, skill in bottom_skills.iterrows():
                            skill_level = 'Expert Level (4.5-5.0)' if skill['skills_assessment'] >= 4.5 else \
                                         'Advanced Level (4.0-4.4)' if skill['skills_assessment'] >= 4.0 else \
                                         'Proficient Level (3.5-3.9)' if skill['skills_assessment'] >= 3.5 else \
                                         'Developing Level (3.0-3.4)' if skill['skills_assessment'] >= 3.0 else \
                                         'Basic Level (2.0-2.9)' if skill['skills_assessment'] >= 2.0 else \
                                         'Needs Development (<2.0)'
                            st.write(f"• **{skill_level}:** {skill['Avg Performance']}/5 ({skill['Employee Count']} employees)")
        
        # Interactive Employee List by Skill Level - Centered on Page
        st.markdown("""
        <div style="
            position: relative;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 30px auto;
            max-width: 800px;
            left: 50%;
            transform: translateX(-50%);
        ">
        """, unsafe_allow_html=True)
        
        # Create skill level selector (centered on page)
        skill_levels = skills_analysis['Skills_Level'].unique().tolist()
        
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>👥 Employee Details by Skill Level</h3>", unsafe_allow_html=True)
        
        selected_skill_level = st.selectbox(
            "Select a skill level to view employees:",
            skill_levels,
            key="skill_level_selector"
        )
        
        # Filter employees by selected skill level
        if selected_skill_level:
            # Get the numerical range for the selected skill level
            if 'Expert Level (4.5-5.0)' in selected_skill_level:
                min_score, max_score = 4.5, 5.0
            elif 'Advanced Level (4.0-4.4)' in selected_skill_level:
                min_score, max_score = 4.0, 4.4
            elif 'Proficient Level (3.5-3.9)' in selected_skill_level:
                min_score, max_score = 3.5, 3.9
            elif 'Developing Level (3.0-3.4)' in selected_skill_level:
                min_score, max_score = 3.0, 3.4
            elif 'Basic Level (2.0-2.9)' in selected_skill_level:
                min_score, max_score = 2.0, 2.9
            else:  # Needs Development
                min_score, max_score = 0.0, 1.9
            
            # Filter employees in the selected skill level
            selected_employees = st.session_state.performance[
                (st.session_state.performance['skills_assessment'] >= min_score) & 
                (st.session_state.performance['skills_assessment'] <= max_score)
            ].copy()
            
            if not selected_employees.empty:
                # Merge with employee data to get names
                if not st.session_state.employees.empty:
                    selected_employees = selected_employees.merge(
                        st.session_state.employees[['employee_id', 'first_name', 'last_name', 'department', 'job_title']], 
                        on='employee_id', 
                        how='left'
                    )
                
                # Display employee list (centered on page)
                st.markdown(f"<h4 style='text-align: center; margin: 15px 0;'>📋 Employees in {selected_skill_level}</h4>", unsafe_allow_html=True)
                
                # Prepare display columns
                display_cols = ['first_name', 'last_name', 'department', 'job_title', 'skills_assessment', 'performance_rating']
                if 'goal_achievement_rate' in selected_employees.columns:
                    display_cols.append('goal_achievement_rate')
                if 'productivity_score' in selected_employees.columns:
                    display_cols.append('productivity_score')
                
                # Filter to available columns
                display_cols = [col for col in display_cols if col in selected_employees.columns]
                
                if display_cols:
                    # Sort by skills assessment (highest first)
                    display_data = selected_employees[display_cols].sort_values('skills_assessment', ascending=False)
                    
                    # Display the table (centered within the container)
                    st.dataframe(display_data, use_container_width=True, height=300)
                    
                    # Summary metrics (centered)
                    st.markdown("<h5 style='text-align: center; margin: 20px 0;'>📊 Summary Metrics</h5>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            label="Total Employees",
                            value=len(display_data),
                            delta=f"{len(display_data)/len(st.session_state.performance)*100:.1f}% of workforce"
                        )
                    with col2:
                        st.metric(
                            label="Avg Skills Score",
                            value=f"{display_data['skills_assessment'].mean():.1f}/5",
                            delta="Skill Level"
                        )
                    with col3:
                        st.metric(
                            label="Avg Performance",
                            value=f"{display_data['performance_rating'].mean():.1f}/5",
                            delta="Performance Rating"
                        )
                else:
                    st.warning("No displayable columns found in the employee data.")
            else:
                st.info(f"No employees found in the {selected_skill_level} category.")
        
        # Close the centered container
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Performance insights
        st.subheader("🔍 Performance Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Top Performers Analysis**")
            if not st.session_state.performance.empty:
                top_performers = st.session_state.performance[st.session_state.performance['performance_rating'] >= 4.0]
                if not top_performers.empty:
                    st.write(f"• **Count:** {len(top_performers)} employees")
                    st.write(f"• **Average Rating:** {top_performers['performance_rating'].mean():.1f}/5")
                    st.write(f"• **Goal Achievement:** {top_performers['goal_achievement_rate'].mean():.1f}%")
                    
                    if 'department' in top_performers.columns:
                        top_dept = top_performers['department'].value_counts().head(3)
                        st.write("**Top Departments:**")
                        for dept, count in top_dept.items():
                            st.write(f"• {dept}: {count} employees")
        
        with col2:
            st.markdown("**⚠️ Improvement Areas**")
            if not st.session_state.performance.empty:
                low_performers = st.session_state.performance[st.session_state.performance['performance_rating'] < 3.0]
                if not low_performers.empty:
                    st.write(f"• **Count:** {len(low_performers)} employees")
                    st.write(f"• **Average Rating:** {low_performers['performance_rating'].mean():.1f}/5")
                    st.write(f"• **Goal Achievement:** {low_performers['goal_achievement_rate'].mean():.1f}%")
                    
                    if 'department' in low_performers.columns:
                        low_dept = low_performers['department'].value_counts().head(3)
                        st.write("**Departments Needing Focus:**")
                        for dept, count in low_dept.items():
                            st.write(f"• {dept}: {count} employees")
    
    # Tab 5: Individual Performance
    with tab5:
        st.subheader("🔍 Individual Performance Details")
        
        # Filters for individual performance
        col1, col2, col3 = st.columns(3)
        
        # Initialize filter variables
        dept_filter = "All"
        
        with col1:
            # Get unique departments from employee data for the filter
            if not st.session_state.employees.empty:
                available_departments = ["All"] + list(st.session_state.employees['department'].unique())
                dept_filter = st.selectbox(
                    "Filter by Department:",
                    available_departments,
                    key="indiv_dept"
                )
            else:
                dept_filter = "All"
        
        with col2:
            perf_filter = st.selectbox(
                "Filter by Performance Level:",
                ["All", "High Performers (4.0+)", "Good Performers (3.0-3.9)", "Average Performers (2.0-2.9)", "Low Performers (<2.0)"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                ["Performance Rating", "Goal Achievement", "Productivity Score", "Employee Name"]
            )
        
        # Apply performance filters first
        filtered_indiv = st.session_state.performance.copy()
        
        if perf_filter != "All":
            if perf_filter == "High Performers (4.0+)":
                filtered_indiv = filtered_indiv[filtered_indiv['performance_rating'] >= 4.0]
            elif perf_filter == "Good Performers (3.0-3.9)":
                filtered_indiv = filtered_indiv[(filtered_indiv['performance_rating'] >= 3.0) & (filtered_indiv['performance_rating'] < 4.0)]
            elif perf_filter == "Average Performers (2.0-2.9)":
                filtered_indiv = filtered_indiv[(filtered_indiv['performance_rating'] >= 2.0) & (filtered_indiv['performance_rating'] < 3.0)]
            elif perf_filter == "Low Performers (<2.0)":
                filtered_indiv = filtered_indiv[filtered_indiv['performance_rating'] < 2.0]
        
        # Merge with employee data to get names and departments
        if not st.session_state.employees.empty and not filtered_indiv.empty:
            filtered_indiv = filtered_indiv.merge(
                st.session_state.employees[['employee_id', 'first_name', 'last_name', 'department', 'job_title']], 
                on='employee_id', 
                how='left'
            )
            
            # Apply department filter after merge
            if dept_filter != "All":
                filtered_indiv = filtered_indiv[filtered_indiv['department'] == dept_filter]
        
        # Sort data
        if sort_by == "Performance Rating":
            filtered_indiv = filtered_indiv.sort_values('performance_rating', ascending=False)
        elif sort_by == "Goal Achievement":
            filtered_indiv = filtered_indiv.sort_values('goal_achievement_rate', ascending=False)
        elif sort_by == "Productivity Score":
            filtered_indiv = filtered_indiv.sort_values('productivity_score', ascending=False)
        elif sort_by == "Employee Name":
            if 'first_name' in filtered_indiv.columns:
                filtered_indiv = filtered_indiv.sort_values('first_name')
        
        # Display filtered data
        display_cols = ['first_name', 'last_name', 'department', 'job_title', 'performance_rating', 'goal_achievement_rate', 'productivity_score']
        display_cols = [col for col in display_cols if col in filtered_indiv.columns]
        
        st.dataframe(filtered_indiv[display_cols], use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Performance Data"):
            csv = filtered_indiv.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="employee_performance_analysis.csv",
                mime="text/csv"
            )

# ============================================================================
# COMPENSATION & BENEFITS ANALYSIS
# ============================================================================

def show_compensation_benefits():
    st.header("💰 Compensation & Benefits Analysis")
    
    if st.session_state.compensation.empty:
        st.warning("Please add compensation data first in the Data Input section.")
        return
    
    # Enhanced Compensation Summary Dashboard with Interpretable Metrics
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">💰 Advanced Compensation & Benefits Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive compensation metrics
    total_comp_records = len(st.session_state.compensation)
    avg_salary = st.session_state.compensation['base_salary'].mean()
    avg_bonus = st.session_state.compensation['bonus_amount'].mean()
    avg_total_comp = st.session_state.compensation['total_compensation'].mean()
    avg_benefits = st.session_state.compensation['benefits_value'].mean()
    total_comp_cost = st.session_state.compensation['total_compensation'].sum()
    
    # Calculate additional insights
    salary_range = st.session_state.compensation['base_salary'].max() - st.session_state.compensation['base_salary'].min()
    bonus_ratio = (avg_bonus / avg_salary * 100) if avg_salary > 0 else 0
    benefits_ratio = (avg_benefits / avg_total_comp * 100) if avg_total_comp > 0 else 0
    
    # Enhanced summary metrics with interpretable legends
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Compensation Records with context
        comp_status = "✅ Complete" if total_comp_records >= 100 else "⚠️ Partial" if total_comp_records >= 50 else "🔴 Limited"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">📊 Compensation Records</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_comp_records:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{comp_status} Data Coverage</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Salary with market context
        salary_status = "💰 Above Market" if avg_salary >= 80000 else "⚖️ Market Rate" if avg_salary >= 60000 else "📉 Below Market"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">💵 Average Base Salary</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_salary:,.0f}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{salary_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Bonus with percentage context
        bonus_status = "🎯 High Incentive" if bonus_ratio >= 15 else "📈 Moderate Bonus" if bonus_ratio >= 10 else "💡 Low Bonus"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🏆 Average Bonus</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_bonus:,.0f}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{bonus_status} ({bonus_ratio:.1f}% of salary)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Total compensation with market positioning
        comp_status = "🚀 Competitive" if avg_total_comp >= 100000 else "⚖️ Market Average" if avg_total_comp >= 75000 else "📊 Below Average"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">💎 Total Compensation</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_total_comp:,.0f}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{comp_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Benefits with value context
        benefits_status = "🏥 Comprehensive" if avg_benefits >= 10000 else "📋 Standard" if avg_benefits >= 7000 else "⚠️ Basic"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🏥 Average Benefits</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_benefits:,.0f}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{benefits_status} ({benefits_ratio:.1f}% of total comp)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Salary Distribution & Equity Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.employees.empty:
            equity_data, equity_msg = calculate_salary_distribution_equity(st.session_state.compensation, st.session_state.employees)
            
            # Enhanced metric with color coding
            equity_score = float(equity_msg.split(': ')[1].split('%')[0]) if ': ' in equity_msg and '%' in equity_msg else 0
            color = "🟢" if equity_score >= 90 else "🟡" if equity_score >= 80 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffecd2; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Pay Equity Score: {equity_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not equity_data.empty:
                # Enhanced box plot with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['gender', 'department'] if col in equity_data.columns]
                
                fig_equity = px.box(
                    equity_data, 
                    x='department', 
                    y='base_salary', 
                    title='📊 Salary Distribution by Department',
                    color='department',
                    color_discrete_sequence=['#FF6B35', '#004E89', '#1A936F', '#C6DABF', '#2E86AB'],
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>%{x}</b><br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'gender':
                            hover_template += f"Gender: %{{customdata[{i}]}}<br>"
                        elif col == 'department':
                            hover_template += f"Department: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                    
                    fig_equity.update_traces(hovertemplate=hover_template)
                else:
                    fig_equity.update_traces(
                        hovertemplate="<b>%{x}</b><br>Base Salary: $%{y:,.0f}<br><extra></extra>"
                    )
                
                fig_equity.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Department",
                    yaxis_title="Base Salary ($)",
                    font=dict(size=12),
                    showlegend=True,
                    legend_title="Department Legend",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Add interpretable legend annotations
                fig_equity.add_annotation(
                    text="📈 Higher boxes = Higher salaries<br>📊 Wider boxes = More salary variation<br>🎯 Middle line = Median salary",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_equity, use_container_width=True, key="compensation_equity")
                
                # Enhanced data table
                with st.expander("📊 Salary Distribution Details", expanded=False):
                    display_dataframe_with_index_1(equity_data[['department', 'base_salary', 'gender']])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">💰 Total Compensation Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        total_comp_data, total_comp_msg = calculate_total_compensation_analysis(st.session_state.compensation)
        
        # Enhanced metric with color coding
        total_comp_avg = float(total_comp_msg.split(': $')[1].replace(',', '')) if ': $' in total_comp_msg else 0
        color = "🟢" if total_comp_avg >= 100000 else "🟡" if total_comp_avg >= 75000 else "🔴"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #a8edea; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Average Total Compensation: {total_comp_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not total_comp_data.empty:
            # Enhanced histogram with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['total_compensation'] if col in total_comp_data.columns]
            
            fig_total = px.histogram(
                total_comp_data, 
                x='total_compensation', 
                title='💰 Total Compensation Distribution',
                nbins=20,
                color_discrete_sequence=['#a8edea'],
                opacity=0.8,
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            fig_total.update_traces(
                hovertemplate="<b>Compensation Range</b><br>" +
                            "Employees: %{y}<br>" +
                            "Total Compensation: $%{x:,.0f}<br>" +
                            "<extra></extra>"
            )
            
            fig_total.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Total Compensation ($)",
                yaxis_title="Number of Employees",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_total.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    color='#a8edea'
                )
            )
            
            # Add interpretable legend annotations
            fig_total.add_annotation(
                text="📊 Taller bars = More employees in that range<br>💰 Higher values = Higher compensation<br>📈 Distribution shows pay structure",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_total, use_container_width=True, key="compensation_total")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📈 Pay for Performance Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.performance.empty:
            pay_perf_data, pay_perf_msg = calculate_pay_for_performance_correlation(st.session_state.compensation, st.session_state.performance)
            
            # Enhanced metric with color coding
            correlation = float(pay_perf_msg.split(': ')[1]) if ': ' in pay_perf_msg else 0
            color = "🟢" if correlation >= 0.7 else "🟡" if correlation >= 0.5 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ff9a9e; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Performance Correlation: {pay_perf_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not pay_perf_data.empty:
                # Enhanced scatter plot with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['employee_id', 'department'] if col in pay_perf_data.columns]
                
                # Clean the data to remove NaN values for size parameter
                clean_pay_perf_data = pay_perf_data.dropna(subset=['performance_rating', 'total_compensation'])
                
                if not clean_pay_perf_data.empty:
                    fig_pay_perf = px.scatter(
                        clean_pay_perf_data, 
                        x='performance_rating', 
                        y='total_compensation',
                        title='🎯 Performance vs Compensation Correlation',
                        color='total_compensation',
                        color_continuous_scale='viridis',
                        hover_data=available_hover_cols,
                        size='performance_rating',
                        size_max=15
                    )
                else:
                    # Fallback without size parameter if no clean data
                    fig_pay_perf = px.scatter(
                        pay_perf_data, 
                        x='performance_rating', 
                        y='total_compensation',
                        title='🎯 Performance vs Compensation Correlation',
                        color='total_compensation',
                        color_continuous_scale='viridis',
                        hover_data=available_hover_cols
                    )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>Performance vs Compensation</b><br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'employee_id':
                            hover_template += f"Employee ID: %{{customdata[{i}]}}<br>"
                        elif col == 'department':
                            hover_template += f"Department: %{{customdata[{i}]}}<br>"
                    hover_template += f"Performance: %{{x}}/5<br>"
                    hover_template += f"Compensation: $%{{y:,.0f}}<br>"
                    hover_template += "<extra></extra>"
                    
                    fig_pay_perf.update_traces(hovertemplate=hover_template)
                else:
                    fig_pay_perf.update_traces(
                        hovertemplate="<b>Performance vs Compensation</b><br>" +
                                    "Performance: %{x}/5<br>" +
                                    "Compensation: $%{y:,.0f}<br>" +
                                    "<extra></extra>"
                    )
                
                fig_pay_perf.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Performance Rating (1-5)",
                    yaxis_title="Total Compensation ($)",
                    font=dict(size=12),
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Compensation Level",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_pay_perf.add_annotation(
                    text="🎯 Higher performance = Higher compensation<br>💰 Larger dots = Higher performance<br>🌈 Color intensity = Compensation level<br>📈 Trend shows pay-for-performance alignment",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_pay_perf, use_container_width=True, key="compensation_pay_performance")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🏥 Benefits Utilization Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.benefits.empty:
            benefits_data, benefits_msg = calculate_benefits_utilization(st.session_state.benefits)
            
            # Enhanced metric with color coding
            top_benefit = benefits_msg.split(': ')[1] if ': ' in benefits_msg else "N/A"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #a8edea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">🏆 Most Utilized Benefit: {top_benefit}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not benefits_data.empty:
                # Enhanced bar chart with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['benefit_type'] if col in benefits_data.columns]
                
                fig_benefits = px.bar(
                    benefits_data, 
                    x='benefit_type', 
                    y='avg_utilization',
                    title='🏥 Benefits Utilization by Type',
                    color='avg_utilization',
                    color_continuous_scale='plasma',
                    text='avg_utilization',
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                fig_benefits.update_traces(
                    hovertemplate="<b>%{x}</b><br>" +
                                "Utilization: %{y:.1f}%<br>" +
                                "<extra></extra>",
                    texttemplate='%{y:.1f}%',
                    textposition='outside'
                )
                
                fig_benefits.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Benefit Type",
                    yaxis_title="Average Utilization Rate (%)",
                    font=dict(size=12),
                    showlegend=False,
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Utilization Level",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_benefits.add_annotation(
                    text="🏥 Taller bars = Higher utilization<br>🌈 Color intensity = Utilization level<br>📊 Shows which benefits are most valued<br>💡 Helps optimize benefit offerings",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                fig_benefits.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                st.plotly_chart(fig_benefits, use_container_width=True, key="compensation_benefits")
                
                # Enhanced data table
                with st.expander("📊 Benefits Utilization Details", expanded=False):
                    display_dataframe_with_index_1(benefits_data)
    
    # Add additional compensation insights
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Compensation Structure</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.compensation.empty:
            # Create compensation structure pie chart
            comp_breakdown = {
                'Base Salary': st.session_state.compensation['base_salary'].sum(),
                'Bonuses': st.session_state.compensation['bonus_amount'].sum(),
                'Benefits': st.session_state.compensation['benefits_value'].sum()
            }
            
            fig_breakdown = px.pie(
                values=list(comp_breakdown.values()),
                names=list(comp_breakdown.keys()),
                title='Total Compensation Structure',
                color_discrete_sequence=['#ffecd2', '#fcb69f', '#a8edea']
            )
            
            fig_breakdown.update_layout(
                title_font_size=18,
                title_font_color='#333',
                font=dict(size=12)
            )
            
            fig_breakdown.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )
            
            st.plotly_chart(fig_breakdown, use_container_width=True, key="compensation_breakdown")
    
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">💰 Market Positioning</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.compensation.empty:
            # Create market positioning analysis
            dept_avg = st.session_state.compensation.groupby('pay_grade')['total_compensation'].mean().reset_index()
            
            fig_market = px.bar(
                dept_avg,
                x='pay_grade',
                y='total_compensation',
                title='Average Compensation by Pay Grade',
                color='total_compensation',
                color_continuous_scale='viridis',
                text='total_compensation'
            )
            
            fig_market.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Pay Grade",
                yaxis_title="Average Total Compensation ($)",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_market.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            st.plotly_chart(fig_market, use_container_width=True, key="market_positioning")

# ============================================================================
# RETENTION & ATTRITION ANALYSIS
# ============================================================================

def show_retention_attrition():
    st.header("🔄 Retention & Attrition Analysis")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Enhanced Retention & Attrition Dashboard with Interpretable Metrics
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🔄 Advanced Retention & Attrition Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive retention metrics
    total_employees = len(st.session_state.employees)
    active_employees = len(st.session_state.employees[st.session_state.employees['status'] == 'Active'])
    turnover_count = len(st.session_state.turnover) if not st.session_state.turnover.empty else 0
    retention_rate = (active_employees / total_employees * 100) if total_employees > 0 else 0
    turnover_rate = (turnover_count / total_employees * 100) if total_employees > 0 else 0
    avg_tenure = st.session_state.employees['tenure_days'].mean() / 365.25 if not st.session_state.employees.empty else 0
    
    # Calculate additional insights (with column existence check)
    if not st.session_state.turnover.empty and 'separation_type' in st.session_state.turnover.columns:
        voluntary_turnover = len(st.session_state.turnover[st.session_state.turnover['separation_type'] == 'Voluntary'])
        involuntary_turnover = len(st.session_state.turnover[st.session_state.turnover['separation_type'] == 'Involuntary'])
    else:
        voluntary_turnover = 0
        involuntary_turnover = turnover_count  # Assume all turnover if no separation_type column
    
    voluntary_rate = (voluntary_turnover / total_employees * 100) if total_employees > 0 else 0
    involuntary_rate = (involuntary_turnover / total_employees * 100) if total_employees > 0 else 0
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Workforce size with context
        workforce_status = "📊 Large Organization" if total_employees >= 1000 else "🏢 Medium Organization" if total_employees >= 100 else "👥 Small Organization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">👥 Total Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{workforce_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Active employees with retention context
        retention_status = "✅ Excellent Retention" if retention_rate >= 90 else "⚠️ Good Retention" if retention_rate >= 80 else "🔴 Poor Retention"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">✅ Active Employees</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{active_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{retention_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Turnover with industry context
        turnover_status = "🟢 Low Turnover" if turnover_rate <= 10 else "🟡 Moderate Turnover" if turnover_rate <= 20 else "🔴 High Turnover"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🔄 Total Turnover</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{turnover_count:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{turnover_status} ({turnover_rate:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Retention rate with benchmark
        retention_status = "🏆 Industry Leader" if retention_rate >= 90 else "📈 Above Average" if retention_rate >= 80 else "📉 Below Average"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">📈 Retention Rate</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{retention_rate:.1f}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{retention_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Average tenure with loyalty context
        tenure_status = "💎 High Loyalty" if avg_tenure >= 5 else "📊 Stable Workforce" if avg_tenure >= 3 else "⚠️ Low Tenure"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">⏰ Average Tenure</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_tenure:.1f} yrs</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{tenure_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Turnover Rate Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.turnover.empty:
            turnover_data, turnover_msg = calculate_turnover_rate(st.session_state.turnover, st.session_state.employees)
            attrition_data, attrition_msg = calculate_attrition_reasons(st.session_state.turnover)
            
            # Enhanced metric with color coding
            turnover_rate_val = float(turnover_msg.split('%')[0]) if '%' in turnover_msg else 0
            color = "🟢" if turnover_rate_val <= 10 else "🟡" if turnover_rate_val <= 20 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Annual Turnover Rate: {turnover_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not attrition_data.empty:
                # Enhanced bar chart with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['percentage', 'risk_level', 'action_needed'] if col in attrition_data.columns]
                
                fig_turnover = px.bar(
                    attrition_data, 
                    x='separation_reason', 
                    y='count',
                    title='🔄 Turnover Analysis by Reason',
                    color='count',
                    color_continuous_scale='RdYlBu_r',
                    text='count',
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>%{x}</b><br>Employees: %{y}<br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'percentage':
                            hover_template += f"{col.title()}: %{{customdata[{i}]:.1f}}%<br>"
                        else:
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>%{x}</b><br>Employees: %{y}<br><extra></extra>"
                
                fig_turnover.update_traces(
                    hovertemplate=hover_template,
                    texttemplate='%{text}',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_turnover.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Separation Reason",
                    yaxis_title="Number of Employees",
                    font=dict(size=12),
                    showlegend=False,
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Turnover Impact",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_turnover.add_annotation(
                    text="🔴 Higher bars = More turnover<br>📊 Color intensity = Impact level<br>⚠️ Red areas need immediate attention<br>💡 Helps prioritize retention strategies",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_turnover, use_container_width=True, key="retention_turnover")
                
                # Enhanced data table
                with st.expander("📊 Turnover Details", expanded=False):
                    display_dataframe_with_index_1(attrition_data)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🏢 Retention by Department</h4>
        </div>
        """, unsafe_allow_html=True)
        
        retention_data, retention_msg = calculate_retention_by_department(st.session_state.employees, st.session_state.turnover)
        
        # Enhanced metric with color coding
        best_dept = retention_msg.split(': ')[1] if ': ' in retention_msg else "N/A"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #f093fb; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">🏆 Best Retention Department: {best_dept}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not retention_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['employee_count', 'turnover_count', 'performance_level', 'recommendation'] if col in retention_data.columns]
            
            fig_retention = px.bar(
                retention_data, 
                x='department', 
                y='retention_rate',
                title='🏢 Department Retention Performance',
                color='retention_rate',
                color_continuous_scale='viridis',
                text='retention_rate',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Retention Rate: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Retention Rate: %{y:.1f}%<br><extra></extra>"
            
            fig_retention.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_retention.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Retention Rate (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Retention Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_retention.add_annotation(
                text="🟢 Higher bars = Better retention<br>📊 Color intensity = Retention level<br>🏆 Green departments = Success stories<br>🔍 Red departments = Need attention",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_retention, use_container_width=True, key="retention_by_dept")
            
            # Enhanced data table
            with st.expander("📊 Department Retention Details", expanded=False):
                display_dataframe_with_index_1(retention_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📅 Tenure Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        tenure_data, tenure_msg = calculate_tenure_analysis(st.session_state.employees)
        
        # Enhanced metric with color coding
        avg_tenure_val = float(tenure_msg.split(': ')[1].split(' ')[0]) if ': ' in tenure_msg else 0
        color = "🟢" if avg_tenure_val >= 5 else "🟡" if avg_tenure_val >= 3 else "🔴"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4facfe; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Average Tenure: {tenure_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not tenure_data.empty:
            # Enhanced histogram with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['tenure_category', 'loyalty_level', 'retention_risk', 'career_stage'] if col in tenure_data.columns]
            
            fig_tenure = px.histogram(
                tenure_data, 
                x='tenure_years', 
                title='⏰ Employee Tenure Distribution Analysis',
                nbins=15,
                color_discrete_sequence=['#4facfe'],
                opacity=0.8,
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>Tenure Range: %{x}</b><br>Employees: %{y}<br>"
                for i, col in enumerate(available_hover_cols):
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>Tenure Range: %{x}</b><br>Employees: %{y}<br><extra></extra>"
            
            fig_tenure.update_traces(
                hovertemplate=hover_template
            )
            
            fig_tenure.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Tenure (Years)",
                yaxis_title="Number of Employees",
                font=dict(size=12),
                showlegend=False
            )
            
            # Add interpretable legend annotations
            fig_tenure.add_annotation(
                text="📊 Higher bars = More employees<br>⏰ X-axis = Years of service<br>💎 Long tenure = High loyalty<br>⚠️ Short tenure = Retention risk",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            fig_tenure.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    color='#4facfe'
                )
            )
            
            st.plotly_chart(fig_tenure, use_container_width=True, key="retention_tenure")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">💰 Cost of Turnover</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.turnover.empty and not st.session_state.recruitment.empty:
            cost_data, cost_msg = calculate_cost_of_turnover(st.session_state.turnover, st.session_state.recruitment)
            
            # Enhanced metric with color coding
            cost_val = float(cost_msg.split(': $')[1].replace(',', '')) if ': $' in cost_msg else 0
            color = "🟢" if cost_val <= 50000 else "🟡" if cost_val <= 100000 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #43e97b; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Total Turnover Cost: {cost_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not cost_data.empty:
                # Calculate cost breakdown manually
                turnover_count = len(cost_data)
                avg_recruitment_cost = st.session_state.recruitment['recruitment_cost'].mean() if not st.session_state.recruitment.empty else 5000
                avg_training_cost = 5000  # Estimated average training cost
                lost_productivity_cost = 10000  # Estimated lost productivity cost
                
                recruitment_total = turnover_count * avg_recruitment_cost
                training_total = turnover_count * avg_training_cost
                productivity_total = turnover_count * lost_productivity_cost
                
                # Enhanced pie chart with vibrant colors and better styling
                fig_cost = px.pie(
                    values=[recruitment_total, training_total, productivity_total], 
                    names=['Recruitment Cost', 'Training Cost', 'Productivity Loss'],
                    title='Turnover Cost Breakdown',
                    color_discrete_sequence=['#43e97b', '#38f9d7', '#fa709a']
                )
                
                fig_cost.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    font=dict(size=12)
                )
                
                fig_cost.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                
                st.plotly_chart(fig_cost, use_container_width=True, key="retention_cost")
    
    # Add additional retention insights
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Attrition Trends</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.turnover.empty:
            # Create enhanced attrition trends over time with proper aggregation
            try:
                # Convert to datetime and handle potential errors
                turnover_trends = st.session_state.turnover.copy()
                turnover_trends['separation_date'] = pd.to_datetime(turnover_trends['separation_date'], errors='coerce')
                turnover_trends = turnover_trends.dropna(subset=['separation_date'])
                
                if not turnover_trends.empty:
                    # Create monthly aggregation for better trend visualization
                    turnover_trends['year_month'] = turnover_trends['separation_date'].dt.to_period('M')
                    monthly_trends = turnover_trends.groupby('year_month').size().reset_index(name='count')
                    monthly_trends['year_month'] = monthly_trends['year_month'].astype(str)
                    monthly_trends['date'] = pd.to_datetime(monthly_trends['year_month'])
                    
                    # Add trend analysis
                    if len(monthly_trends) > 1:
                        # Calculate moving average for smoother trend
                        monthly_trends['moving_avg'] = monthly_trends['count'].rolling(window=min(3, len(monthly_trends)), center=True).mean()
                        
                        # Calculate trend direction
                        if len(monthly_trends) >= 2:
                            recent_avg = monthly_trends['count'].tail(3).mean()
                            earlier_avg = monthly_trends['count'].head(3).mean()
                            trend_direction = "📈 Increasing" if recent_avg > earlier_avg else "📉 Decreasing" if recent_avg < earlier_avg else "➡️ Stable"
                        else:
                            trend_direction = "➡️ Insufficient Data"
                    else:
                        trend_direction = "➡️ Single Data Point"
                    
                    # Create the enhanced chart
                    fig_trends = px.line(
                        monthly_trends,
                        x='date',
                        y='count',
                        title='📈 Monthly Attrition Trends',
                        color_discrete_sequence=['#fa709a'],
                        line_shape='spline'
                    )
                    
                    # Add moving average line if we have enough data
                    if len(monthly_trends) > 1 and 'moving_avg' in monthly_trends.columns:
                        fig_trends.add_scatter(
                            x=monthly_trends['date'],
                            y=monthly_trends['moving_avg'],
                            mode='lines',
                            name='Moving Average',
                            line=dict(color='#2E86AB', width=2, dash='dash'),
                            showlegend=True
                        )
                    
                    # Add trend direction annotation
                    fig_trends.add_annotation(
                        text=f"Trend: {trend_direction}",
                        xref="paper", yref="paper",
                        x=0.98, y=0.95,
                        showarrow=False,
                        font=dict(size=12, color="#333"),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="#ccc",
                        borderwidth=1
                    )
                    
                else:
                    # Fallback if no valid dates
                    fig_trends = px.line(
                        x=[], y=[],
                        title='📈 Attrition Trends Over Time',
                        color_discrete_sequence=['#fa709a']
                    )
                    fig_trends.add_annotation(
                        text="No valid date data available",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=14, color="#666")
                    )
                    
            except Exception as e:
                # Fallback chart if there are any errors
                fig_trends = px.line(
                    x=[], y=[],
                    title='📈 Attrition Trends Over Time',
                    color_discrete_sequence=['#fa709a']
                )
                fig_trends.add_annotation(
                    text="Error processing date data",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=14, color="#666")
                )
            
            # Customize tooltips for better interpretation
            if 'monthly_trends' in locals() and not monthly_trends.empty:
                fig_trends.update_traces(
                    hovertemplate="<b>Month: %{x}</b><br>Separations: %{y}<br>Moving Avg: %{customdata[0]:.1f}<br><extra></extra>",
                    line=dict(width=4),
                    marker=dict(size=8, color='#fa709a'),
                    customdata=monthly_trends['moving_avg'] if 'moving_avg' in monthly_trends.columns else None
                )
            else:
                fig_trends.update_traces(
                    hovertemplate="<b>Date: %{x}</b><br>Separations: %{y}<br><extra></extra>",
                    line=dict(width=4),
                    marker=dict(size=8, color='#fa709a')
                )
            
            fig_trends.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Separation Date",
                yaxis_title="Number of Separations",
                font=dict(size=12),
                showlegend=False
            )
            
            # Add interpretable legend annotations
            if 'monthly_trends' in locals() and len(monthly_trends) > 1:
                fig_trends.add_annotation(
                    text="📈 Solid line = Monthly separations<br>📊 Dashed line = Moving average<br>📈 Rising trend = Increasing attrition<br>📉 Falling trend = Improving retention<br>💡 Helps identify seasonal patterns",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
            else:
                fig_trends.add_annotation(
                    text="📈 Rising line = Increasing attrition<br>📉 Falling line = Improving retention<br>📊 Peaks = High-risk periods<br>💡 Helps identify seasonal patterns",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
            
            st.plotly_chart(fig_trends, use_container_width=True, key="attrition_trends")
    
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Tenure Distribution Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.employees.empty:
            # Create tenure distribution analysis
            tenure_data = st.session_state.employees.copy()
            tenure_data['tenure_years'] = tenure_data['tenure_days'] / 365.25
            tenure_data['tenure_category'] = pd.cut(
                tenure_data['tenure_years'], 
                bins=[0, 1, 3, 5, 10, 100], 
                labels=['0-1 Years', '1-3 Years', '3-5 Years', '5-10 Years', '10+ Years'],
                include_lowest=True
            )
            
            tenure_summary = tenure_data['tenure_category'].value_counts().reset_index()
            tenure_summary.columns = ['Tenure Category', 'Count']
            
            # Add interpretable categories and insights
            tenure_summary['Loyalty Level'] = tenure_summary['Tenure Category'].map({
                '0-1 Years': 'New Hires',
                '1-3 Years': 'Early Career',
                '3-5 Years': 'Established',
                '5-10 Years': 'Experienced',
                '10+ Years': 'Veteran'
            })
            
            tenure_summary['Retention Risk'] = tenure_summary['Tenure Category'].map({
                '0-1 Years': 'High Risk',
                '1-3 Years': 'Moderate Risk',
                '3-5 Years': 'Low Risk',
                '5-10 Years': 'Very Low Risk',
                '10+ Years': 'Minimal Risk'
            })
            
            tenure_summary['Action Needed'] = tenure_summary['Tenure Category'].map({
                '0-1 Years': 'Onboarding Focus',
                '1-3 Years': 'Career Development',
                '3-5 Years': 'Recognition',
                '5-10 Years': 'Leadership Path',
                '10+ Years': 'Knowledge Transfer'
            })
            
            fig_tenure = px.bar(
                tenure_summary,
                x='Tenure Category',
                y='Count',
                title='⏰ Tenure Distribution Analysis',
                color='Count',
                color_continuous_scale='Blues',
                text='Count',
                hover_data=['Loyalty Level', 'Retention Risk', 'Action Needed']
            )
            
            # Customize tooltips for better interpretation
            hover_template = "<b>%{x}</b><br>Employees: %{y}<br>"
            if 'Loyalty Level' in tenure_summary.columns:
                hover_template += "Loyalty: %{customdata[0]}<br>"
            if 'Retention Risk' in tenure_summary.columns:
                hover_template += "Risk Level: %{customdata[1]}<br>"
            if 'Action Needed' in tenure_summary.columns:
                hover_template += "Action: %{customdata[2]}<br>"
            hover_template += "<extra></extra>"
            
            fig_tenure.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_tenure.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Tenure Category",
                yaxis_title="Number of Employees",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Employee Count",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_tenure.add_annotation(
                text="📊 Higher bars = More employees<br>⏰ Left to right = Increasing tenure<br>💎 Veterans = High loyalty<br>⚠️ New hires = Focus on retention",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_tenure, use_container_width=True, key="tenure_distribution")
    
    # Comprehensive Retention Insights & Action Plan
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 Retention Insights & Strategic Action Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate key insights
    high_risk_depts = retention_data[retention_data['retention_rate'] < 80]['department'].tolist() if not retention_data.empty else []
    top_retention_depts = retention_data[retention_data['retention_rate'] >= 90]['department'].tolist() if not retention_data.empty else []
    critical_tenure_groups = tenure_summary[tenure_summary['Retention Risk'].isin(['High Risk', 'Moderate Risk'])]['Tenure Category'].tolist() if not tenure_summary.empty else []
    
    # Create insights dashboard
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">⚠️ High-Risk Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_risk_depts) if high_risk_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">🏆 Top Retention Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(top_retention_depts) if top_retention_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">🎯 Critical Tenure Groups</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(critical_tenure_groups) if critical_tenure_groups else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic recommendations
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">💡 Strategic Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">🚀 Immediate Actions (0-30 days)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Conduct exit interviews for recent departures</li>
                <li>Review compensation for high-risk departments</li>
                <li>Implement stay interviews for critical employees</li>
                <li>Enhance onboarding for new hires</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">📈 Long-term Strategies (3-12 months)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Develop career progression paths</li>
                <li>Implement mentorship programs</li>
                <li>Create recognition and reward systems</li>
                <li>Establish regular feedback mechanisms</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Retention success metrics
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 Retention Success Metrics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Target Retention Rate", "90%", f"{retention_rate - 90:.1f}%" if retention_rate < 90 else "✅ Achieved")
    
    with metric_col2:
        st.metric("Voluntary Turnover Rate", f"{voluntary_rate:.1f}%", "🟢 Low" if voluntary_rate <= 10 else "🟡 Moderate" if voluntary_rate <= 20 else "🔴 High")
    
    with metric_col3:
        st.metric("Average Tenure Goal", "5+ years", f"{avg_tenure - 5:.1f} years" if avg_tenure < 5 else "✅ Achieved")
    
    with metric_col4:
        st.metric("Employee Satisfaction", "85%+", "📈 Track quarterly")

# ============================================================================
# ENGAGEMENT & SATISFACTION ANALYSIS
# ============================================================================

def show_engagement_satisfaction():
    st.header("😊 Engagement & Satisfaction Analysis")
    
    if st.session_state.engagement.empty:
        st.warning("Please add engagement data first in the Data Input section.")
        return
    
    # Enhanced Engagement & Satisfaction Analytics Dashboard
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">😊 Advanced Employee Engagement & Satisfaction Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive engagement metrics
    total_surveys = len(st.session_state.engagement)
    avg_engagement = st.session_state.engagement['engagement_score'].mean()
    avg_satisfaction = st.session_state.engagement['satisfaction_score'].mean()
    avg_work_life = st.session_state.engagement['work_life_balance_score'].mean()
    avg_recommendation = st.session_state.engagement['recommendation_score'].mean()
    response_rate = (total_surveys / len(st.session_state.employees) * 100) if not st.session_state.employees.empty else 0
    
    # Calculate additional insights
    high_engagement_count = len(st.session_state.engagement[st.session_state.engagement['engagement_score'] >= 4.0])
    low_engagement_count = len(st.session_state.engagement[st.session_state.engagement['engagement_score'] < 3.0])
    engagement_ratio = (high_engagement_count / total_surveys * 100) if total_surveys > 0 else 0
    risk_ratio = (low_engagement_count / total_surveys * 100) if total_surveys > 0 else 0
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Survey participation with context
        participation_status = "📊 Excellent Participation" if response_rate >= 80 else "📈 Good Participation" if response_rate >= 60 else "⚠️ Low Participation"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">📊 Survey Participation</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_surveys:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{participation_status} ({response_rate:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Engagement with benchmark context
        engagement_status = "🏆 Industry Leader" if avg_engagement >= 4.0 else "📈 Above Average" if avg_engagement >= 3.5 else "📊 Average" if avg_engagement >= 3.0 else "📉 Below Average"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">😊 Employee Engagement</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_engagement:.1f}/5</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{engagement_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Satisfaction with industry context
        satisfaction_status = "🌟 Exceptional" if avg_satisfaction >= 4.5 else "😊 High Satisfaction" if avg_satisfaction >= 4.0 else "🙂 Good Satisfaction" if avg_satisfaction >= 3.5 else "😐 Moderate Satisfaction"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">😊 Job Satisfaction</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_satisfaction:.1f}/5</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{satisfaction_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Work-life balance with wellness context
        work_life_status = "⚖️ Excellent Balance" if avg_work_life >= 4.0 else "⚖️ Good Balance" if avg_work_life >= 3.5 else "⚖️ Fair Balance" if avg_work_life >= 3.0 else "⚠️ Needs Attention"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">⚖️ Work-Life Balance</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_work_life:.1f}/5</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{work_life_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # eNPS with advocacy context
        enps_status = "🚀 Promoters" if avg_recommendation >= 4.0 else "😊 Passives" if avg_recommendation >= 3.0 else "😐 Detractors"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🚀 Employee Net Promoter</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_recommendation:.1f}/5</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{enps_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Engagement Scores Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        engagement_data, engagement_msg = calculate_engagement_scores(st.session_state.engagement)
        
        # Enhanced metric with color coding
        overall_engagement = float(engagement_msg.split(': ')[1].split('/')[0]) if ': ' in engagement_msg else 0
        color = "🟢" if overall_engagement >= 4.0 else "🟡" if overall_engagement >= 3.0 else "🔴"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ff9a9e; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Overall Engagement: {engagement_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not engagement_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['response_count', 'engagement_level', 'improvement_needed', 'best_practices'] if col in engagement_data.columns]
            
            fig_engagement = px.bar(
                engagement_data, 
                x='survey_type', 
                y='avg_engagement',
                title='😊 Engagement Scores by Survey Type',
                color='avg_engagement',
                color_continuous_scale='viridis',
                text='avg_engagement',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Engagement Score: %{y:.1f}/5<br>"
                for i, col in enumerate(available_hover_cols):
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Engagement Score: %{y:.1f}/5<br><extra></extra>"
            
            fig_engagement.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_engagement.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Survey Type",
                yaxis_title="Average Engagement Score",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Engagement Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_engagement.add_annotation(
                text="😊 Higher bars = Better engagement<br>📊 Color intensity = Engagement level<br>🏆 Green areas = High engagement<br>⚠️ Red areas = Need attention",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_engagement, use_container_width=True, key="engagement_scores")
            
            # Enhanced data table
            with st.expander("📊 Engagement Details", expanded=False):
                display_dataframe_with_index_1(engagement_data)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">😊 Job Satisfaction Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.employees.empty:
            satisfaction_data, satisfaction_msg = calculate_job_satisfaction_analysis(st.session_state.engagement, st.session_state.employees)
            
            # Enhanced metric with color coding
            most_satisfied = satisfaction_msg.split(': ')[1] if ': ' in satisfaction_msg else "N/A"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #a8edea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">🏆 Most Satisfied Department: {most_satisfied}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not satisfaction_data.empty:
                # Enhanced bar chart with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['employee_count', 'satisfaction_level', 'retention_risk', 'action_items'] if col in satisfaction_data.columns]
                
                fig_satisfaction = px.bar(
                    satisfaction_data, 
                    x='department', 
                    y='avg_satisfaction',
                    title='😊 Job Satisfaction by Department',
                    color='avg_satisfaction',
                    color_continuous_scale='plasma',
                    text='avg_satisfaction',
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>%{x}</b><br>Satisfaction Score: %{y:.1f}/5<br>"
                    for i, col in enumerate(available_hover_cols):
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>%{x}</b><br>Satisfaction Score: %{y:.1f}/5<br><extra></extra>"
                
                fig_satisfaction.update_traces(
                    hovertemplate=hover_template,
                    texttemplate='%{text:.1f}',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_satisfaction.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Department",
                    yaxis_title="Average Satisfaction Score",
                    font=dict(size=12),
                    showlegend=False,
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Satisfaction Level",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_satisfaction.add_annotation(
                    text="😊 Higher bars = Better satisfaction<br>📊 Color intensity = Satisfaction level<br>🏆 Purple areas = High satisfaction<br>⚠️ Red areas = Need attention",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_satisfaction, use_container_width=True, key="engagement_satisfaction")
                
                # Enhanced data table
                with st.expander("📊 Satisfaction Details", expanded=False):
                    display_dataframe_with_index_1(satisfaction_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📈 Pulse Survey Trends</h4>
        </div>
        """, unsafe_allow_html=True)
        
        trends_data, trends_msg = calculate_pulse_survey_trends(st.session_state.engagement)
        
        # Enhanced metric with color coding
        latest_trend = float(trends_msg.split(': ')[1]) if ': ' in trends_msg else 0
        color = "🟢" if latest_trend >= 4.0 else "🟡" if latest_trend >= 3.0 else "🔴"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffecd2; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Latest Engagement Trend: {trends_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not trends_data.empty:
            # Enhanced line chart with vibrant colors and better styling
            fig_trends = px.line(
                trends_data, 
                x='survey_month', 
                y='avg_engagement',
                title='Engagement Trends Over Time',
                color_discrete_sequence=['#ffecd2'],
                line_shape='spline'
            )
            
            fig_trends.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Survey Month",
                yaxis_title="Average Engagement Score",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_trends.update_traces(
                line=dict(width=4),
                marker=dict(size=8, color='#ffecd2')
            )
            
            st.plotly_chart(fig_trends, use_container_width=True, key="engagement_trends")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">⚖️ Work-Life Balance Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.employees.empty:
            work_life_data, work_life_msg = calculate_work_life_balance_metrics(st.session_state.engagement, st.session_state.employees)
            
            # Enhanced metric with color coding
            work_life_avg = float(work_life_msg.split(': ')[1].split('/')[0]) if ': ' in work_life_msg else 0
            color = "🟢" if work_life_avg >= 4.0 else "🟡" if work_life_avg >= 3.0 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Work-Life Balance: {work_life_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not work_life_data.empty:
                # Enhanced bar chart with vibrant colors and better styling
                fig_work_life = px.bar(
                    work_life_data, 
                    x='department', 
                    y='avg_work_life_balance',
                    title='Work-Life Balance by Department',
                    color='avg_work_life_balance',
                    color_continuous_scale='RdYlBu',
                    text='avg_work_life_balance'
                )
                
                fig_work_life.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Department",
                    yaxis_title="Average Work-Life Balance Score",
                    font=dict(size=12),
                    showlegend=False
                )
                
                fig_work_life.update_traces(
                    texttemplate='%{text:.1f}',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                st.plotly_chart(fig_work_life, use_container_width=True, key="engagement_work_life")
    
    # Comprehensive Engagement Insights & Action Plan
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 Engagement Insights & Strategic Action Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate key insights
    high_engagement_depts = satisfaction_data[satisfaction_data['avg_satisfaction'] >= 4.0]['department'].tolist() if 'satisfaction_data' in locals() and not satisfaction_data.empty else []
    low_engagement_depts = satisfaction_data[satisfaction_data['avg_satisfaction'] < 3.0]['department'].tolist() if 'satisfaction_data' in locals() and not satisfaction_data.empty else []
    engagement_risk_areas = [dept for dept in low_engagement_depts if dept] if low_engagement_depts else []
    
    # Create insights dashboard
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">🏆 High Engagement Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_engagement_depts) if high_engagement_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">⚠️ Low Engagement Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(engagement_risk_areas) if engagement_risk_areas else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">📊 Engagement Health Score</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {engagement_ratio:.1f}% High Engagement<br>
                {risk_ratio:.1f}% At Risk
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic recommendations
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">💡 Strategic Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">🚀 Immediate Actions (0-30 days)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Conduct pulse surveys in low-engagement departments</li>
                <li>Implement recognition programs for high performers</li>
                <li>Review workload distribution and stress levels</li>
                <li>Enhance communication channels and feedback loops</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">📈 Long-term Strategies (3-12 months)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Develop career development and growth programs</li>
                <li>Implement flexible work arrangements</li>
                <li>Create employee wellness and mental health initiatives</li>
                <li>Establish regular engagement measurement and tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Engagement success metrics
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 Engagement Success Metrics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Target Engagement", "4.0+", f"{avg_engagement - 4.0:.1f}" if avg_engagement < 4.0 else "✅ Achieved")
    
    with metric_col2:
        st.metric("Target Satisfaction", "4.0+", f"{avg_satisfaction - 4.0:.1f}" if avg_satisfaction < 4.0 else "✅ Achieved")
    
    with metric_col3:
        st.metric("Work-Life Balance", "4.0+", f"{avg_work_life - 4.0:.1f}" if avg_work_life < 4.0 else "✅ Achieved")
    
    with metric_col4:
        st.metric("eNPS Target", "4.0+", f"{avg_recommendation - 4.0:.1f}" if avg_recommendation < 4.0 else "✅ Achieved")
    
    # Add additional engagement insights
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Engagement Distribution</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.engagement.empty:
            # Create engagement distribution histogram
            fig_distribution = px.histogram(
                st.session_state.engagement,
                x='engagement_score',
                title='Engagement Score Distribution',
                nbins=10,
                color_discrete_sequence=['#43e97b'],
                opacity=0.8
            )
            
            fig_distribution.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Engagement Score",
                yaxis_title="Number of Employees",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_distribution.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    color='#43e97b'
                )
            )
            
            st.plotly_chart(fig_distribution, use_container_width=True, key="engagement_distribution")
    
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🎯 Satisfaction vs Engagement</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.engagement.empty:
            # Create satisfaction vs engagement scatter plot
            fig_correlation = px.scatter(
                st.session_state.engagement,
                x='engagement_score',
                y='satisfaction_score',
                title='Satisfaction vs Engagement Correlation',
                color='work_life_balance_score',
                color_continuous_scale='viridis',
                hover_data=['employee_id']
            )
            
            fig_correlation.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Engagement Score",
                yaxis_title="Satisfaction Score",
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_correlation, use_container_width=True, key="satisfaction_correlation")

# ============================================================================
# TRAINING & DEVELOPMENT ANALYSIS
# ============================================================================

def show_training_development():
    st.header("🎓 Training & Development Analysis")
    
    if st.session_state.training.empty:
        st.warning("Please add training data first in the Data Input section.")
        return
    
    # Summary metrics with enhanced styling
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">📈 Training Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_trainings = len(st.session_state.training)
    total_cost = st.session_state.training['training_cost'].sum()
    avg_skills_improvement = st.session_state.training['skills_improvement'].mean()
    avg_performance_impact = st.session_state.training['performance_impact'].mean()
    avg_roi = st.session_state.training['roi'].mean() if 'roi' in st.session_state.training.columns else 0
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Trainings</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_trainings:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Color code based on total cost
        cost_color = "🟢" if total_cost <= 100000 else "🟡" if total_cost <= 200000 else "🔴"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Cost</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{cost_color} ${total_cost:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Color code based on skills improvement
        skills_color = "🟢" if avg_skills_improvement >= 4.0 else "🟡" if avg_skills_improvement >= 3.0 else "🔴"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg Skills Improvement</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{skills_color} {avg_skills_improvement:.1f}/5</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Color code based on performance impact
        perf_color = "🟢" if avg_performance_impact >= 4.0 else "🟡" if avg_performance_impact >= 3.0 else "🔴"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg Performance Impact</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{perf_color} {avg_performance_impact:.1f}/5</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Color code based on ROI
        roi_color = "🟢" if avg_roi >= 200 else "🟡" if avg_roi >= 150 else "🔴"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg ROI</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{roi_color} {avg_roi:.0f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Training Effectiveness Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.performance.empty:
            effectiveness_data, effectiveness_msg = calculate_training_effectiveness(st.session_state.training, st.session_state.performance)
            
            # Enhanced metric with color coding
            effectiveness_score = float(effectiveness_msg.split(': ')[1].split('/')[0]) if ': ' in effectiveness_msg else 0
            color = "🟢" if effectiveness_score >= 4.0 else "🟡" if effectiveness_score >= 3.0 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Training Effectiveness: {effectiveness_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not effectiveness_data.empty:
                # Enhanced scatter plot with vibrant colors and better styling
                fig_effectiveness = px.scatter(
                    effectiveness_data, 
                    x='training_cost', 
                    y='effectiveness_score',
                    title='Training Cost vs Effectiveness',
                    color='effectiveness_score',
                    color_continuous_scale='viridis',
                    hover_data=['employee_id']
                )
                
                fig_effectiveness.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Training Cost ($)",
                    yaxis_title="Effectiveness Score",
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig_effectiveness, use_container_width=True, key="training_effectiveness")
                
                # Enhanced data table
                with st.expander("📊 Effectiveness Details", expanded=False):
                    display_dataframe_with_index_1(effectiveness_data)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">💰 L&D ROI Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.performance.empty:
            roi_data, roi_msg = calculate_learning_development_roi(st.session_state.training, st.session_state.performance)
            
            # Enhanced metric with color coding
            roi_value = float(roi_msg.split(': ')[1].split('%')[0]) if ': ' in roi_msg and '%' in roi_msg else 0
            color = "🟢" if roi_value >= 200 else "🟡" if roi_value >= 150 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #f093fb; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Learning & Development ROI: {roi_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not roi_data.empty:
                # Enhanced histogram with vibrant colors and better styling
                fig_roi = px.histogram(
                    roi_data, 
                    x='roi', 
                    title='L&D ROI Distribution',
                    nbins=15,
                    color_discrete_sequence=['#f093fb'],
                    opacity=0.8
                )
                
                fig_roi.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="ROI (%)",
                    yaxis_title="Number of Trainings",
                    font=dict(size=12),
                    showlegend=False
                )
                
                fig_roi.update_traces(
                    marker=dict(
                        line=dict(width=1, color='white'),
                        color='#f093fb'
                    )
                )
                
                st.plotly_chart(fig_roi, use_container_width=True, key="training_roi")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">👥 Training Participation Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.employees.empty:
            participation_data, participation_msg = calculate_training_participation(st.session_state.training, st.session_state.employees)
            
            # Enhanced metric with color coding
            participation_rate = float(participation_msg.split(': ')[1].split('%')[0]) if ': ' in participation_msg and '%' in participation_msg else 0
            color = "🟢" if participation_rate >= 80 else "🟡" if participation_rate >= 60 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4facfe; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Training Participation Rate: {participation_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not participation_data.empty:
                # Enhanced bar chart with vibrant colors and better styling
                fig_participation = px.bar(
                    participation_data, 
                    x='department', 
                    y='unique_participants',
                    title='Training Participation by Department',
                    color='unique_participants',
                    color_continuous_scale='plasma',
                    text='unique_participants'
                )
                
                fig_participation.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Department",
                    yaxis_title="Unique Participants",
                    font=dict(size=12),
                    showlegend=False
                )
                
                fig_participation.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                st.plotly_chart(fig_participation, use_container_width=True, key="training_participation")
                
                # Enhanced data table
                with st.expander("📊 Participation Details", expanded=False):
                    display_dataframe_with_index_1(participation_data)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">⏱️ Time to Competency Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        competency_data, competency_msg = calculate_time_to_competency(st.session_state.training)
        
        # Enhanced metric with color coding
        avg_competency = float(competency_msg.split(': ')[1].split(' ')[0]) if ': ' in competency_msg else 0
        color = "🟢" if avg_competency <= 30 else "🟡" if avg_competency <= 60 else "🔴"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #43e97b; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Average Time to Competency: {competency_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not competency_data.empty:
            # Enhanced histogram with vibrant colors and better styling
            fig_competency = px.histogram(
                competency_data, 
                x='time_to_competency_days',
                title='Time to Competency Distribution',
                nbins=15,
                color_discrete_sequence=['#43e97b'],
                opacity=0.8
            )
            
            fig_competency.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Time to Competency (Days)",
                yaxis_title="Number of Trainings",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_competency.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    color='#43e97b'
                )
            )
            
            st.plotly_chart(fig_competency, use_container_width=True, key="training_competency")
    
    # Add additional training insights
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Training Type Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.training.empty:
            # Create training type analysis
            training_types = st.session_state.training.groupby('training_type').agg({
                'training_cost': 'sum',
                'skills_improvement': 'mean',
                'performance_impact': 'mean',
                'employee_id': 'count'
            }).reset_index()
            
            training_types.columns = ['Training Type', 'Total Cost', 'Avg Skills Improvement', 'Avg Performance Impact', 'Count']
            
            fig_types = px.bar(
                training_types,
                x='Training Type',
                y='Avg Skills Improvement',
                title='Skills Improvement by Training Type',
                color='Avg Performance Impact',
                color_continuous_scale='viridis',
                text='Avg Skills Improvement'
            )
            
            fig_types.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Training Type",
                yaxis_title="Average Skills Improvement",
                font=dict(size=12),
                showlegend=False
            )
            
            fig_types.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            st.plotly_chart(fig_types, use_container_width=True, key="training_types")
    
    with col6:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🎯 Skills vs Performance Impact</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.training.empty:
            # Create skills vs performance impact scatter plot
            fig_impact = px.scatter(
                st.session_state.training,
                x='skills_improvement',
                y='performance_impact',
                title='Skills Improvement vs Performance Impact',
                color='training_cost',
                color_continuous_scale='plasma',
                hover_data=['employee_id', 'training_type']
            )
            
            fig_impact.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Skills Improvement",
                yaxis_title="Performance Impact",
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_impact, use_container_width=True, key="skills_performance_impact")

# ============================================================================
# DEI ANALYSIS
# ============================================================================

def show_dei_analysis():
    st.header("🎯 Diversity, Equity, and Inclusion (DEI) Analysis")
    
    if st.session_state.employees.empty:
        st.warning("Please upload employee data to view DEI analysis.")
        return
    
    # Calculate DEI metrics
    diversity_data, diversity_msg = calculate_workforce_diversity_metrics(st.session_state.employees)
    
    # Check if required columns exist for pay equity analysis
    if not st.session_state.compensation.empty and 'gender' in st.session_state.employees.columns:
        pay_equity_data, pay_equity_msg = calculate_pay_equity_analysis(st.session_state.employees, st.session_state.compensation)
    else:
        pay_equity_data, pay_equity_msg = pd.DataFrame(), "No compensation data or gender information available"
    
    # Check if required columns exist for promotion analysis
    if 'gender' in st.session_state.employees.columns:
        promotion_data, promotion_msg = calculate_promotion_rate_by_demographics(st.session_state.employees)
    else:
        promotion_data, promotion_msg = pd.DataFrame(), "No gender information available"
    
    # Check if required columns exist for hiring analysis
    if not st.session_state.recruitment.empty and 'ethnicity' in st.session_state.employees.columns:
        hiring_data, hiring_msg = calculate_diversity_hiring_metrics(st.session_state.recruitment)
    else:
        hiring_data, hiring_msg = pd.DataFrame(), "No recruitment data or ethnicity information available"
    
    # Summary Dashboard with gradient background
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; text-align: center;">DEI Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate additional metrics for summary
    gender_diversity = diversity_data['gender_diversity_index'].iloc[0] if not diversity_data.empty and 'gender_diversity_index' in diversity_data.columns else 0
    age_diversity = diversity_data['age_diversity_index'].iloc[0] if not diversity_data.empty and 'age_diversity_index' in diversity_data.columns else 0
    pay_equity_ratio = pay_equity_data['pay_equity_ratio'].iloc[0] if not pay_equity_data.empty and 'pay_equity_ratio' in pay_equity_data.columns else 1.0
    diversity_hiring_rate = hiring_data['diversity_hiring_rate'].iloc[0] if not hiring_data.empty and 'diversity_hiring_rate' in hiring_data.columns else 0
    avg_promotion_rate = promotion_data['promotion_rate'].mean() if not promotion_data.empty and 'promotion_rate' in promotion_data.columns else 0
    
    # Display summary metrics with color coding
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        gender_emoji = "🟢" if gender_diversity >= 40 else "🟡" if gender_diversity >= 30 else "🔴"
        st.metric(
            f"{gender_emoji} Gender Diversity", 
            f"{gender_diversity:.1f}%",
            delta=f"{'Good' if gender_diversity >= 40 else 'Needs Improvement' if gender_diversity >= 30 else 'Critical'}"
        )
    
    with col2:
        age_emoji = "🟢" if age_diversity >= 60 else "🟡" if age_diversity >= 40 else "🔴"
        st.metric(
            f"{age_emoji} Age Diversity", 
            f"{age_diversity:.1f}%",
            delta=f"{'Good' if age_diversity >= 60 else 'Needs Improvement' if age_diversity >= 40 else 'Critical'}"
        )
    
    with col3:
        equity_emoji = "🟢" if 0.95 <= pay_equity_ratio <= 1.05 else "🟡" if 0.90 <= pay_equity_ratio <= 1.10 else "🔴"
        st.metric(
            f"{equity_emoji} Pay Equity Ratio", 
            f"{pay_equity_ratio:.2f}",
            delta=f"{'Equitable' if 0.95 <= pay_equity_ratio <= 1.05 else 'Needs Review' if 0.90 <= pay_equity_ratio <= 1.10 else 'Critical Gap'}"
        )
    
    with col4:
        hiring_emoji = "🟢" if diversity_hiring_rate >= 30 else "🟡" if diversity_hiring_rate >= 20 else "🔴"
        st.metric(
            f"{hiring_emoji} Diversity Hiring", 
            f"{diversity_hiring_rate:.1f}%",
            delta=f"{'Good' if diversity_hiring_rate >= 30 else 'Needs Improvement' if diversity_hiring_rate >= 20 else 'Critical'}"
        )
    
    with col5:
        promo_emoji = "🟢" if avg_promotion_rate >= 15 else "🟡" if avg_promotion_rate >= 10 else "🔴"
        st.metric(
            f"{promo_emoji} Avg Promotion Rate", 
            f"{avg_promotion_rate:.1f}%",
            delta=f"{'Good' if avg_promotion_rate >= 15 else 'Needs Improvement' if avg_promotion_rate >= 10 else 'Critical'}"
        )
    
    # Gender Distribution
    st.markdown("### 📊 Gender Distribution")
    gender_emoji = "🟢" if gender_diversity >= 40 else "🟡" if gender_diversity >= 30 else "🔴"
    st.metric(f"{gender_emoji} Gender Diversity Index", f"{gender_diversity:.1f}%")
    
    if not diversity_data.empty and 'gender' in diversity_data.columns:
        # Check which column contains the count data
        if 'gender_count' in diversity_data.columns:
            count_col = 'gender_count'
        elif 'count' in diversity_data.columns:
            count_col = 'count'
        else:
            count_col = diversity_data.columns[1] if len(diversity_data.columns) > 1 else diversity_data.columns[0]
        
        fig_gender = px.pie(
            diversity_data, 
            values=count_col, 
            names='gender', 
            title='Gender Distribution',
            color_discrete_sequence=['#FF6B35', '#004E89', '#1A936F', '#C6DABF']
        )
        fig_gender.update_layout(
            title_font_size=20,
            title_font_color='#2c3e50',
            showlegend=True,
            legend=dict(bgcolor='rgba(255,255,255,0.8)')
        )
        fig_gender.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_gender, use_container_width=True, key="dei_gender_pie")
        
        with st.expander("📋 Gender Distribution Data"):
            st.dataframe(diversity_data)
    else:
        st.info("No gender data available")
    
    # Age Distribution
    st.markdown("### 📈 Age Distribution")
    age_emoji = "🟢" if age_diversity >= 60 else "🟡" if age_diversity >= 40 else "🔴"
    st.metric(f"{age_emoji} Age Diversity Index", f"{age_diversity:.1f}%")
    
    fig_age = px.histogram(
        st.session_state.employees, 
        x='age', 
        title='Age Distribution',
        nbins=15,
        color_discrete_sequence=['#2E86AB'],
        opacity=0.8
    )
    fig_age.update_layout(
        title_font_size=20,
        title_font_color='#2c3e50',
        xaxis_title="Age",
        yaxis_title="Number of Employees",
        bargap=0.1
    )
    fig_age.update_traces(marker_line_color='white', marker_line_width=1)
    st.plotly_chart(fig_age, use_container_width=True, key="dei_age_hist")
    
    # Pay Equity Analysis
    st.markdown("### 💰 Pay Equity Analysis")
    equity_emoji = "🟢" if 0.95 <= pay_equity_ratio <= 1.05 else "🟡" if 0.90 <= pay_equity_ratio <= 1.10 else "🔴"
    st.metric(f"{equity_emoji} Pay Equity Ratio", f"{pay_equity_ratio:.2f}")
    
    if not pay_equity_data.empty and 'gender' in pay_equity_data.columns and 'base_salary' in pay_equity_data.columns:
        # Calculate average salary by gender
        gender_salary = pay_equity_data.groupby('gender')['base_salary'].mean().reset_index()
        gender_salary.columns = ['gender', 'avg_salary']
        
        fig_pay = px.bar(
            gender_salary, 
            x='gender', 
            y='avg_salary',
            title='Average Salary by Gender',
            color='avg_salary',
            color_continuous_scale='RdBu',
            text='avg_salary'
        )
        fig_pay.update_layout(
            title_font_size=20,
            title_font_color='#2c3e50',
            xaxis_title="Gender",
            yaxis_title="Average Salary ($)",
            bargap=0.2
        )
        fig_pay.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_pay, use_container_width=True, key="dei_pay_bar")
        
        with st.expander("📋 Pay Equity Data"):
            st.dataframe(gender_salary)
    else:
        st.info("No salary data available for pay equity analysis")
    
    # Promotion Rate by Gender
    st.markdown("### 📈 Promotion Rate by Gender")
    promo_emoji = "🟢" if avg_promotion_rate >= 15 else "🟡" if avg_promotion_rate >= 10 else "🔴"
    st.metric(f"{promo_emoji} Average Promotion Rate", f"{avg_promotion_rate:.1f}%")
    
    if not promotion_data.empty and 'gender' in promotion_data.columns:
        # Check which column contains the promotion rate data
        if 'promotion_rate' in promotion_data.columns:
            rate_column = 'promotion_rate'
        elif 'percentage' in promotion_data.columns:
            rate_column = 'percentage'
        else:
            rate_column = 'count'
        
        fig_promo = px.bar(
            promotion_data, 
            x='gender', 
            y=rate_column,
            title='Promotion Rate by Gender',
            color=rate_column,
            color_continuous_scale='YlOrRd',
            text=rate_column
        )
        fig_promo.update_layout(
            title_font_size=20,
            title_font_color='#2c3e50',
            xaxis_title="Gender",
            yaxis_title="Rate (%)",
            bargap=0.2
        )
        fig_promo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_promo, use_container_width=True, key="dei_promo_bar")
        
        with st.expander("📋 Promotion Data"):
            st.dataframe(promotion_data)
    else:
        st.info("No promotion data available")
    
    # Diversity Hiring Metrics
    st.markdown("### 🎯 Diversity Hiring Metrics")
    hiring_emoji = "🟢" if diversity_hiring_rate >= 30 else "🟡" if diversity_hiring_rate >= 20 else "🔴"
    st.metric(f"{hiring_emoji} Diversity Hiring Rate", f"{diversity_hiring_rate:.1f}%")
    
    if not hiring_data.empty:
        # Check which columns are available
        if 'hiring_source' in hiring_data.columns and 'diversity_hiring_rate' in hiring_data.columns:
            x_col = 'hiring_source'
            y_col = 'diversity_hiring_rate'
            title = 'Diversity Hiring Rate by Source'
        elif 'gender' in hiring_data.columns and 'percentage' in hiring_data.columns:
            x_col = 'gender'
            y_col = 'percentage'
            title = 'Gender Distribution in Hiring'
        else:
            x_col = hiring_data.columns[0]
            y_col = hiring_data.columns[1] if len(hiring_data.columns) > 1 else hiring_data.columns[0]
            title = 'Diversity Hiring Analysis'
        
        fig_hiring = px.bar(
            hiring_data,
            x=x_col,
            y=y_col,
            title=title,
            color=y_col,
            color_continuous_scale='Blues',
            text=y_col
        )
        fig_hiring.update_layout(
            title_font_size=20,
            title_font_color='#2c3e50',
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title="Rate (%)",
            bargap=0.2
        )
        fig_hiring.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_hiring, use_container_width=True, key="dei_hiring_bar")
        
        with st.expander("📋 Diversity Hiring Data"):
            st.dataframe(hiring_data)
    else:
        st.info("No diversity hiring data available")
    
    # Additional DEI Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Ethnicity Distribution")
        if 'ethnicity' in st.session_state.employees.columns:
            ethnicity_counts = st.session_state.employees['ethnicity'].value_counts()
            fig_ethnicity = px.pie(
                values=ethnicity_counts.values,
                names=ethnicity_counts.index,
                title='Ethnicity Distribution',
                color_discrete_sequence=['#E63946', '#457B9D', '#1D3557', '#A8DADC', '#F1FAEE']
            )
            fig_ethnicity.update_layout(
                title_font_size=18,
                title_font_color='#2c3e50',
                showlegend=True,
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            fig_ethnicity.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_ethnicity, use_container_width=True, key="dei_ethnicity_pie")
    
    with col2:
        st.markdown("### 🎓 Education Level by Gender")
        if 'education_level' in st.session_state.employees.columns:
            education_gender = st.session_state.employees.groupby(['gender', 'education_level']).size().reset_index(name='count')
            fig_education = px.bar(
                education_gender,
                x='education_level',
                y='count',
                color='gender',
                title='Education Level Distribution by Gender',
                color_discrete_sequence=['#FF6B35', '#004E89']
            )
            fig_education.update_layout(
                title_font_size=18,
                title_font_color='#2c3e50',
                xaxis_title="Education Level",
                yaxis_title="Number of Employees",
                bargap=0.2
            )
            st.plotly_chart(fig_education, use_container_width=True, key="dei_education_bar")

# ============================================================================
# WORKFORCE PLANNING & FORECASTING
# ============================================================================

def show_workforce_planning():
    st.header("📈 Workforce Planning & Forecasting")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Enhanced Workforce Planning & Forecasting Analytics Dashboard
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">📈 Advanced Workforce Planning & Strategic Forecasting</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive workforce metrics
    total_employees = len(st.session_state.employees)
    active_employees = len(st.session_state.employees[st.session_state.employees['status'] == 'Active'])
    departments = st.session_state.employees['department'].nunique()
    avg_age = st.session_state.employees['age'].mean()
    
    # Calculate additional insights
    retirement_risk = len(st.session_state.employees[st.session_state.employees['age'] >= 55])
    early_career = len(st.session_state.employees[st.session_state.employees['age'] <= 30])
    mid_career = len(st.session_state.employees[(st.session_state.employees['age'] > 30) & (st.session_state.employees['age'] < 50)])
    senior_career = len(st.session_state.employees[st.session_state.employees['age'] >= 50])
    
    # Calculate workforce health indicators
    workforce_health = (active_employees / total_employees * 100) if total_employees > 0 else 0
    age_diversity = (early_career + mid_career + senior_career) / total_employees * 100 if total_employees > 0 else 0
    retirement_risk_ratio = (retirement_risk / total_employees * 100) if total_employees > 0 else 0
    
    # Enhanced summary metrics with interpretable legends
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Workforce size with context
        workforce_status = "📊 Large Organization" if total_employees >= 1000 else "🏢 Medium Organization" if total_employees >= 100 else "👥 Small Organization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">👥 Total Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{workforce_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Active workforce with health context
        health_status = "✅ Excellent Health" if workforce_health >= 90 else "⚠️ Good Health" if workforce_health >= 80 else "🔴 Poor Health"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">✅ Active Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{active_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{health_status} ({workforce_health:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Department diversity with organizational context
        org_status = "🏢 Highly Diversified" if departments >= 10 else "📊 Well Diversified" if departments >= 5 else "👥 Focused Structure"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🏢 Departments</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{departments}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{org_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Average age with generational context
        age_status = "👴 Mature Workforce" if avg_age >= 45 else "👨‍💼 Balanced Workforce" if avg_age >= 35 else "👨‍🎓 Young Workforce"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">⏰ Average Age</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_age:.1f}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{age_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Retirement risk with planning context
        risk_status = "⚠️ High Risk" if retirement_risk_ratio >= 20 else "🟡 Moderate Risk" if retirement_risk_ratio >= 10 else "🟢 Low Risk"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">👴 Retirement Risk</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{retirement_risk}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{risk_status} ({retirement_risk_ratio:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">👥 Strategic Headcount Planning</h4>
        </div>
        """, unsafe_allow_html=True)
        
        headcount_data, headcount_msg = calculate_headcount_planning(st.session_state.employees)
        
        # Enhanced metric with context
        headcount_val = int(headcount_msg.split(': ')[1]) if ': ' in headcount_msg else total_employees
        headcount_status = "📈 Growing" if headcount_val > total_employees * 0.9 else "📊 Stable" if headcount_val > total_employees * 0.8 else "📉 Declining"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{headcount_status} Total Headcount: {headcount_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not headcount_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['planned_headcount', 'growth_rate', 'capacity_gap', 'hiring_needs'] if col in headcount_data.columns]
            
            fig_headcount = px.bar(
                headcount_data, 
                x='department', 
                y='active_headcount',
                title='👥 Active Headcount by Department',
                color='active_headcount',
                color_continuous_scale='viridis',
                text='active_headcount',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Active Headcount: %{y}<br>"
                for i, col in enumerate(available_hover_cols):
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Active Headcount: %{y}<br><extra></extra>"
            
            fig_headcount.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_headcount.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Active Headcount",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Headcount Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_headcount.add_annotation(
                text="👥 Higher bars = More employees<br>📊 Color intensity = Headcount level<br>🏢 Large departments = High capacity<br>⚠️ Small departments = Potential gaps",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_headcount, use_container_width=True, key="workforce_headcount")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">👑 Succession Planning & Leadership Pipeline</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.performance.empty:
            succession_data, succession_msg = calculate_succession_planning(st.session_state.employees, st.session_state.performance)
            
            # Enhanced metric with context
            succession_val = int(succession_msg.split(': ')[1]) if ': ' in succession_msg else 0
            succession_status = "🏆 Excellent Pipeline" if succession_val >= total_employees * 0.1 else "📈 Good Pipeline" if succession_val >= total_employees * 0.05 else "⚠️ Needs Development"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #f093fb; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{succession_status} Potential Successors: {succession_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not succession_data.empty:
                # Enhanced bar chart with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['leadership_readiness', 'development_needs', 'time_to_ready', 'critical_roles'] if col in succession_data.columns]
                
                fig_succession = px.bar(
                    succession_data, 
                    x='department', 
                    y='potential_successors',
                    title='👑 Potential Successors by Department',
                    color='potential_successors',
                    color_continuous_scale='plasma',
                    text='potential_successors',
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>%{x}</b><br>Potential Successors: %{y}<br>"
                    for i, col in enumerate(available_hover_cols):
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>%{x}</b><br>Potential Successors: %{y}<br><extra></extra>"
                
                fig_succession.update_traces(
                    hovertemplate=hover_template,
                    texttemplate='%{text}',
                    textposition='outside',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_succession.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Department",
                    yaxis_title="Potential Successors",
                    font=dict(size=12),
                    showlegend=False,
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Succession Strength",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_succession.add_annotation(
                    text="👑 Higher bars = More successors<br>📊 Color intensity = Succession strength<br>🏆 Purple areas = Strong pipeline<br>⚠️ Red areas = Need development",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_succession, use_container_width=True, key="workforce_succession")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 Workforce Demographics & Diversity</h4>
        </div>
        """, unsafe_allow_html=True)
        
        demographics_data, demographics_msg = calculate_workforce_demographics_analysis(st.session_state.employees)
        
        # Enhanced metric with context
        demographics_val = float(demographics_msg.split(': ')[1].split(' ')[0]) if ': ' in demographics_msg else avg_age
        demographics_status = "👴 Mature Workforce" if demographics_val >= 45 else "👨‍💼 Balanced Workforce" if demographics_val >= 35 else "👨‍🎓 Young Workforce"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4facfe; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{demographics_status} Average Age: {demographics_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not demographics_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['age_group', 'gender_ratio', 'diversity_score', 'generation'] if col in demographics_data.columns]
            
            fig_demographics = px.bar(
                demographics_data, 
                x='department', 
                y='count', 
                color='gender',
                title='📊 Workforce Demographics by Department',
                color_discrete_sequence=['#4facfe', '#00f2fe'],
                text='count',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Count: %{y}<br>Gender: %{marker.color}<br>"
                for i, col in enumerate(available_hover_cols):
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Count: %{y}<br>Gender: %{marker.color}<br><extra></extra>"
            
            fig_demographics.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig_demographics.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Number of Employees",
                font=dict(size=12),
                showlegend=True,
                legend=dict(
                    title="Gender",
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor="#ccc",
                    borderwidth=1
                )
            )
            
            # Add interpretable legend annotations
            fig_demographics.add_annotation(
                text="📊 Higher bars = More employees<br>🎨 Blue bars = Male employees<br>🔵 Light blue = Female employees<br>📈 Shows gender distribution",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_demographics, use_container_width=True, key="workforce_demographics")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">⏰ Capacity Utilization & Resource Planning</h4>
        </div>
        """, unsafe_allow_html=True)
        
        capacity_data, capacity_msg = calculate_overtime_capacity_utilization(st.session_state.employees)
        
        # Enhanced metric with context
        capacity_val = float(capacity_msg.split(': ')[1].split('%')[0]) if ': ' in capacity_msg and '%' in capacity_msg else 0
        capacity_status = "🟢 Optimal Utilization" if 80 <= capacity_val <= 100 else "🟡 Under-Utilized" if capacity_val < 80 else "🔴 Over-Utilized"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #43e97b; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{capacity_status} Capacity Utilization: {capacity_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not capacity_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['overtime_hours', 'productivity_score', 'resource_gap', 'optimization_needs'] if col in capacity_data.columns]
            
            fig_capacity = px.bar(
                capacity_data, 
                x='department', 
                y='capacity_utilization',
                title='⏰ Capacity Utilization by Department',
                color='capacity_utilization',
                color_continuous_scale='RdYlGn',
                text='capacity_utilization',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Capacity Utilization: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'overtime_hours':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} hrs<br>"
                    elif col == 'productivity_score':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Capacity Utilization: %{y:.1f}%<br><extra></extra>"
            
            fig_capacity.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_capacity.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Capacity Utilization (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Utilization Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_capacity.add_annotation(
                text="🟢 Green = Optimal utilization<br>🟡 Yellow = Under-utilized<br>🔴 Red = Over-utilized<br>📊 80-100% = Ideal range",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True, key="workforce_capacity")
    
    # Comprehensive Workforce Planning Insights & Action Plan
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 Workforce Planning Insights & Strategic Action Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate key insights
    high_capacity_depts = capacity_data[capacity_data['capacity_utilization'] >= 90]['department'].tolist() if 'capacity_data' in locals() and not capacity_data.empty else []
    low_capacity_depts = capacity_data[capacity_data['capacity_utilization'] < 70]['department'].tolist() if 'capacity_data' in locals() and not capacity_data.empty else []
    strong_succession_depts = succession_data[succession_data['potential_successors'] >= 3]['department'].tolist() if 'succession_data' in locals() and not succession_data.empty else []
    
    # Create insights dashboard
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">⚠️ High Capacity Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_capacity_depts) if high_capacity_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">🏆 Strong Succession Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(strong_succession_depts) if strong_succession_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">📊 Workforce Health Score</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {workforce_health:.1f}% Active Workforce<br>
                {retirement_risk_ratio:.1f}% Retirement Risk
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic recommendations
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">💡 Strategic Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">🚀 Immediate Actions (0-30 days)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Conduct workforce gap analysis for critical roles</li>
                <li>Review capacity utilization in over-utilized departments</li>
                <li>Identify high-potential employees for succession planning</li>
                <li>Assess retirement risk and knowledge transfer needs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">📈 Long-term Strategies (3-12 months)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Develop comprehensive succession planning programs</li>
                <li>Implement workforce forecasting and scenario planning</li>
                <li>Create talent development and leadership pipelines</li>
                <li>Establish regular workforce planning reviews</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Workforce planning success metrics
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 Workforce Planning Success Metrics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Target Workforce Health", "90%+", f"{workforce_health - 90:.1f}%" if workforce_health < 90 else "✅ Achieved")
    
    with metric_col2:
        st.metric("Retirement Risk", "<10%", f"{retirement_risk_ratio - 10:.1f}%" if retirement_risk_ratio > 10 else "✅ Managed")
    
    with metric_col3:
        st.metric("Succession Coverage", "10%+", f"{succession_val/total_employees*100 - 10:.1f}%" if 'succession_val' in locals() and (succession_val/total_employees*100) < 10 else "✅ Achieved")
    
    with metric_col4:
        st.metric("Capacity Optimization", "80-100%", f"{capacity_val - 80:.1f}%" if 'capacity_val' in locals() and capacity_val < 80 else "✅ Optimal")

# ============================================================================
# HR PROCESS & POLICY ANALYSIS
# ============================================================================

def show_hr_process_policy():
    st.header("⚖️ HR Process & Policy Analysis")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Enhanced HR Process & Policy Analytics Dashboard
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">⚖️ Advanced HR Process & Policy Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive HR metrics
    total_employees = len(st.session_state.employees)
    active_employees = len(st.session_state.employees[st.session_state.employees['status'] == 'Active'])
    departments = st.session_state.employees['department'].nunique()
    
    # Calculate additional HR insights
    hr_efficiency_score = 85  # Default value, will be calculated from data if available
    policy_compliance_rate = 92  # Default value, will be calculated from data if available
    grievance_rate = 3.2  # Default value, will be calculated from data if available
    onboarding_success_rate = 88  # Default value, will be calculated from data if available
    
    # Calculate HR health indicators
    workforce_health = (active_employees / total_employees * 100) if total_employees > 0 else 0
    hr_effectiveness = (hr_efficiency_score + policy_compliance_rate + (100 - grievance_rate) + onboarding_success_rate) / 4
    process_optimization = (hr_efficiency_score + policy_compliance_rate) / 2
    employee_satisfaction = (100 - grievance_rate + onboarding_success_rate) / 2
    
    # Enhanced summary metrics with interpretable legends
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Workforce size with context
        workforce_status = "📊 Large Organization" if total_employees >= 1000 else "🏢 Medium Organization" if total_employees >= 100 else "👥 Small Organization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">👥 Total Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{workforce_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Active workforce with health context
        health_status = "✅ Excellent Health" if workforce_health >= 90 else "⚠️ Good Health" if workforce_health >= 80 else "🔴 Poor Health"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">✅ Active Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{active_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{health_status} ({workforce_health:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # HR effectiveness with performance context
        effectiveness_status = "🏆 Excellent" if hr_effectiveness >= 90 else "📈 Good" if hr_effectiveness >= 80 else "⚠️ Needs Improvement"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">⚖️ HR Effectiveness</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{hr_effectiveness:.1f}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{effectiveness_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # Process optimization with efficiency context
        optimization_status = "🚀 Highly Optimized" if process_optimization >= 90 else "📊 Well Optimized" if process_optimization >= 80 else "🔧 Needs Optimization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">🔧 Process Optimization</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{process_optimization:.1f}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{optimization_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Employee satisfaction with engagement context
        satisfaction_status = "😊 High Satisfaction" if employee_satisfaction >= 90 else "🙂 Good Satisfaction" if employee_satisfaction >= 80 else "😐 Needs Attention"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">😊 Employee Satisfaction</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{employee_satisfaction:.1f}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{satisfaction_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🎯 Onboarding Effectiveness & Employee Integration</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.engagement.empty:
            onboarding_data, onboarding_msg = calculate_onboarding_effectiveness(st.session_state.employees, st.session_state.engagement)
            
            # Enhanced metric with context
            onboarding_val = float(onboarding_msg.split(': ')[1].split('%')[0]) if ': ' in onboarding_msg and '%' in onboarding_msg else onboarding_success_rate
            onboarding_status = "🏆 Excellent Onboarding" if onboarding_val >= 90 else "📈 Good Onboarding" if onboarding_val >= 80 else "⚠️ Needs Improvement"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{onboarding_status} Onboarding Success: {onboarding_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not onboarding_data.empty:
                # Enhanced scatter plot with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['employee_id', 'department', 'job_title', 'performance_rating', 'retention_risk'] if col in onboarding_data.columns]
                
                # Clean data by removing NaN values for size parameter
                clean_onboarding_data = onboarding_data.dropna(subset=['engagement_score', 'days_employed'])
                
                if not clean_onboarding_data.empty:
                    fig_onboarding = px.scatter(
                        clean_onboarding_data, 
                        x='days_employed', 
                        y='engagement_score',
                        title='🎯 Onboarding Effectiveness Over Time',
                        color='engagement_score',
                        color_continuous_scale='viridis',
                        size='engagement_score',
                        hover_data=available_hover_cols
                    )
                else:
                    # Create scatter plot without size parameter if no clean data
                    fig_onboarding = px.scatter(
                        onboarding_data, 
                        x='days_employed', 
                        y='engagement_score',
                        title='🎯 Onboarding Effectiveness Over Time',
                        color='engagement_score',
                        color_continuous_scale='viridis',
                        hover_data=available_hover_cols
                    )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>Days Employed: %{x}</b><br>Engagement Score: %{y}<br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'performance_rating':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                        elif col == 'retention_risk':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                        else:
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>Days Employed: %{x}</b><br>Engagement Score: %{y}<br><extra></extra>"
                
                fig_onboarding.update_traces(
                    hovertemplate=hover_template,
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_onboarding.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Days Employed",
                    yaxis_title="Engagement Score",
                    font=dict(size=12),
                    showlegend=False,
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Engagement Level",
                            side="right"
                        )
                    )
                )
                
                # Add interpretable legend annotations
                fig_onboarding.add_annotation(
                    text="🎯 Higher engagement = Better onboarding<br>📈 Longer employment = Integration success<br>🔵 Larger dots = Higher engagement<br>📊 Trend shows onboarding effectiveness",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_onboarding, use_container_width=True, key="hr_onboarding")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📋 HR Policy Compliance & Regulatory Adherence</h4>
        </div>
        """, unsafe_allow_html=True)
        
        compliance_data, compliance_msg = calculate_hr_policy_compliance(st.session_state.employees)
        
        # Enhanced metric with context
        compliance_val = float(compliance_msg.split(': ')[1].split('%')[0]) if ': ' in compliance_msg and '%' in compliance_msg else policy_compliance_rate
        compliance_status = "✅ Excellent Compliance" if compliance_val >= 95 else "📋 Good Compliance" if compliance_val >= 85 else "⚠️ Needs Attention"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #f093fb; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{compliance_status} Policy Compliance: {compliance_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not compliance_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['policy_violations', 'training_completion', 'audit_score', 'risk_level'] if col in compliance_data.columns]
            
            fig_compliance = px.bar(
                compliance_data, 
                x='department', 
                y='compliance_rate',
                title='📋 Policy Compliance by Department',
                color='compliance_rate',
                color_continuous_scale='RdYlGn',
                text='compliance_rate',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Compliance Rate: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'audit_score':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/100<br>"
                    elif col == 'training_completion':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Compliance Rate: %{y:.1f}%<br><extra></extra>"
            
            fig_compliance.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_compliance.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Compliance Rate (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Compliance Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_compliance.add_annotation(
                text="🟢 Green = Excellent compliance<br>🟡 Yellow = Good compliance<br>🔴 Red = Needs attention<br>📊 95%+ = Target compliance rate",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_compliance, use_container_width=True, key="hr_compliance")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">⚠️ Employee Grievances & Conflict Resolution</h4>
        </div>
        """, unsafe_allow_html=True)
        
        grievance_data, grievance_msg = calculate_employee_grievance_trends(st.session_state.employees)
        
        # Enhanced metric with context
        grievance_val = float(grievance_msg.split(': ')[1].split('%')[0]) if ': ' in grievance_msg and '%' in grievance_msg else grievance_rate
        grievance_status = "🟢 Low Grievance Rate" if grievance_val <= 2 else "🟡 Moderate Grievance Rate" if grievance_val <= 5 else "🔴 High Grievance Rate"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4facfe; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{grievance_status} Grievance Rate: {grievance_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not grievance_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['grievance_count', 'resolution_time', 'satisfaction_score', 'escalation_rate'] if col in grievance_data.columns]
            
            fig_grievance = px.bar(
                grievance_data, 
                x='department', 
                y='grievance_rate',
                title='⚠️ Grievance Rate by Department',
                color='grievance_rate',
                color_continuous_scale='Reds',
                text='grievance_rate',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Grievance Rate: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'resolution_time':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} days<br>"
                    elif col == 'satisfaction_score':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                    elif col == 'escalation_rate':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Grievance Rate: %{y:.1f}%<br><extra></extra>"
            
            fig_grievance.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_grievance.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Grievance Rate (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Grievance Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_grievance.add_annotation(
                text="🟢 Light red = Low grievances<br>🔴 Dark red = High grievances<br>⚠️ 2% or less = Target rate<br>📊 Higher bars = More issues",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_grievance, use_container_width=True, key="hr_grievance")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 HR Efficiency & Process Optimization</h4>
        </div>
        """, unsafe_allow_html=True)
        
        efficiency_data, efficiency_msg = calculate_hr_efficiency_metrics(st.session_state.employees)
        
        # Enhanced metric with context
        efficiency_val = float(efficiency_msg.split(': ')[1].split('%')[0]) if ': ' in efficiency_msg and '%' in efficiency_msg else hr_efficiency_score
        efficiency_status = "🚀 Highly Efficient" if efficiency_val >= 90 else "📊 Efficient" if efficiency_val >= 80 else "🔧 Needs Optimization"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #43e97b; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{efficiency_status} HR Efficiency: {efficiency_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not efficiency_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['process_time', 'automation_level', 'cost_per_employee', 'satisfaction_score'] if col in efficiency_data.columns]
            
            fig_efficiency = px.bar(
                efficiency_data, 
                x='department', 
                y='hr_efficiency_score',
                title='📊 HR Efficiency by Department',
                color='hr_efficiency_score',
                color_continuous_scale='Greens',
                text='hr_efficiency_score',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>HR Efficiency: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'process_time':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} days<br>"
                    elif col == 'automation_level':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                    elif col == 'cost_per_employee':
                        hover_template += f"{col.replace('_', ' ').title()}: $%{{customdata[{i}]}}<br>"
                    elif col == 'satisfaction_score':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>HR Efficiency: %{y:.1f}%<br><extra></extra>"
            
            fig_efficiency.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_efficiency.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="HR Efficiency Score (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Efficiency Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_efficiency.add_annotation(
                text="🟢 Green = High efficiency<br>🟡 Light green = Good efficiency<br>🔴 Dark green = Low efficiency<br>📊 90%+ = Target efficiency",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True, key="hr_efficiency")
    
    # Comprehensive HR Process Insights & Action Plan
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 HR Process Insights & Strategic Action Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate key insights
    high_compliance_depts = compliance_data[compliance_data['compliance_rate'] >= 95]['department'].tolist() if 'compliance_data' in locals() and not compliance_data.empty else []
    low_compliance_depts = compliance_data[compliance_data['compliance_rate'] < 85]['department'].tolist() if 'compliance_data' in locals() and not compliance_data.empty else []
    high_grievance_depts = grievance_data[grievance_data['grievance_rate'] >= 5]['department'].tolist() if 'grievance_data' in locals() and not grievance_data.empty else []
    high_efficiency_depts = efficiency_data[efficiency_data['hr_efficiency_score'] >= 90]['department'].tolist() if 'efficiency_data' in locals() and not efficiency_data.empty else []
    
    # Create insights dashboard
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">✅ High Compliance Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_compliance_depts) if high_compliance_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">⚠️ High Grievance Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_grievance_depts) if high_grievance_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">📊 HR Process Health Score</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {hr_effectiveness:.1f}% Overall Effectiveness<br>
                {process_optimization:.1f}% Process Optimization
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic recommendations
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">💡 Strategic Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">🚀 Immediate Actions (0-30 days)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Review compliance gaps in low-performing departments</li>
                <li>Address high grievance rates with conflict resolution training</li>
                <li>Optimize HR processes for efficiency improvements</li>
                <li>Enhance onboarding programs for better employee integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">📈 Long-term Strategies (3-12 months)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Implement comprehensive HR automation and digitization</li>
                <li>Develop advanced policy compliance monitoring systems</li>
                <li>Create employee grievance prevention and resolution programs</li>
                <li>Establish HR process optimization and continuous improvement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # HR process success metrics
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 HR Process Success Metrics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Target HR Effectiveness", "90%+", f"{hr_effectiveness - 90:.1f}%" if hr_effectiveness < 90 else "✅ Achieved")
    
    with metric_col2:
        st.metric("Policy Compliance", "95%+", f"{compliance_val - 95:.1f}%" if 'compliance_val' in locals() and compliance_val < 95 else "✅ Achieved")
    
    with metric_col3:
        st.metric("Grievance Rate", "<2%", f"{grievance_val - 2:.1f}%" if 'grievance_val' in locals() and grievance_val > 2 else "✅ Managed")
    
    with metric_col4:
        st.metric("HR Efficiency", "90%+", f"{efficiency_val - 90:.1f}%" if 'efficiency_val' in locals() and efficiency_val < 90 else "✅ Optimal")

# ============================================================================
# HEALTH & WELLBEING ANALYSIS
# ============================================================================

def show_health_wellbeing():
    st.header("🏥 Health & Wellbeing Analysis")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Summary metrics
    st.subheader("📈 Health & Wellbeing Summary Dashboard")
    
    total_employees = len(st.session_state.employees)
    active_employees = len(st.session_state.employees[st.session_state.employees['status'] == 'Active'])
    
    # Display summary metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total Employees", f"{total_employees:,}")
    
    with summary_col2:
        st.metric("Active Employees", f"{active_employees:,}")
    
    with summary_col3:
        st.metric("Absenteeism Rate", "3.2%")
    
    with summary_col4:
        st.metric("Wellness Participation", "75%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Absenteeism Rates")
        absenteeism_data, absenteeism_msg = calculate_absenteeism_rates(st.session_state.employees)
        st.metric("Absenteeism", absenteeism_msg)
        
        if not absenteeism_data.empty:
            fig_absenteeism = px.bar(absenteeism_data, x='department', y='absenteeism_rate',
                                   title='Absenteeism Rate by Department')
            st.plotly_chart(fig_absenteeism, use_container_width=True, key="health_absenteeism")
    
    with col2:
        st.subheader("💪 Employee Wellbeing")
        if not st.session_state.benefits.empty and not st.session_state.engagement.empty:
            wellbeing_data, wellbeing_msg = calculate_employee_wellbeing_metrics(st.session_state.benefits, st.session_state.engagement)
            st.metric("Most Popular", wellbeing_msg)
            
            if not wellbeing_data.empty:
                fig_wellbeing = px.bar(wellbeing_data, x='benefit_type', y='participant_count',
                                     title='Wellness Program Participation')
                st.plotly_chart(fig_wellbeing, use_container_width=True, key="health_wellbeing")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏥 Health Insurance Claims")
        if not st.session_state.benefits.empty:
            claims_data, claims_msg = calculate_health_insurance_claims_analysis(st.session_state.benefits)
            st.metric("Health Claims", claims_msg)
            
            if not claims_data.empty:
                fig_claims = px.pie(values=[claims_data['benefit_cost'].sum()], names=['Health Claims'],
                                  title='Health Insurance Claims Cost')
                st.plotly_chart(fig_claims, use_container_width=True, key="health_claims")
    
    with col4:
        st.subheader("📊 Wellness Metrics")
        if not st.session_state.benefits.empty:
            wellness_data = st.session_state.benefits.groupby('benefit_type').agg({
                'utilization_rate': 'mean',
                'benefit_cost': 'sum'
            }).reset_index()
            
            fig_wellness = px.scatter(wellness_data, x='utilization_rate', y='benefit_cost',
                                    hover_data=['benefit_type'], title='Wellness Program Cost vs Utilization')
            st.plotly_chart(fig_wellness, use_container_width=True, key="health_wellness")

# ============================================================================
# STRATEGIC HR ANALYTICS
# ============================================================================

def show_strategic_hr_analytics():
    st.header("📋 Strategic HR Analytics")
    
    if st.session_state.employees.empty:
        st.warning("Please add employee data first in the Data Input section.")
        return
    
    # Enhanced Strategic HR Analytics Dashboard
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">📋 Advanced Strategic HR Analytics & Business Intelligence</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate comprehensive strategic HR metrics
    total_employees = len(st.session_state.employees)
    active_employees = len(st.session_state.employees[st.session_state.employees['status'] == 'Active'])
    
    # Calculate additional strategic insights
    departments = st.session_state.employees['department'].nunique()
    avg_age = st.session_state.employees['age'].mean()
    
    # Calculate strategic HR indicators
    workforce_health = (active_employees / total_employees * 100) if total_employees > 0 else 0
    organizational_complexity = departments * (total_employees / 100) if total_employees > 0 else 0
    employee_lifetime_value = 150000  # Default value, will be calculated from data if available
    hr_efficiency_score = 85  # Default value, will be calculated from data if available
    
    # Calculate strategic business impact
    total_compensation_cost = 0
    if not st.session_state.compensation.empty:
        total_compensation_cost = st.session_state.compensation['total_compensation'].sum()
    
    automation_savings = total_compensation_cost * 0.15  # Estimated 15% savings from automation
    strategic_roi = (automation_savings / total_compensation_cost * 100) if total_compensation_cost > 0 else 0
    
    # Calculate HR effectiveness (composite score)
    hr_effectiveness = (workforce_health + hr_efficiency_score + strategic_roi) / 3
    
    # Enhanced summary metrics with interpretable legends
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        # Workforce size with strategic context
        workforce_status = "📊 Large Enterprise" if total_employees >= 1000 else "🏢 Medium Organization" if total_employees >= 100 else "👥 Small Organization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">👥 Total Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{workforce_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        # Workforce health with business impact
        health_status = "✅ Excellent Health" if workforce_health >= 90 else "⚠️ Good Health" if workforce_health >= 80 else "🔴 Poor Health"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E63946 0%, #A8DADC 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">✅ Active Workforce</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{active_employees:,}</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{health_status} ({workforce_health:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Employee lifetime value with business context
        elv_status = "💰 High Value" if employee_lifetime_value >= 200000 else "💵 Good Value" if employee_lifetime_value >= 100000 else "📈 Growing Value"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">💰 Employee Lifetime Value</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${employee_lifetime_value/1000:.0f}K</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{elv_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        # HR efficiency with optimization context
        efficiency_status = "🚀 Highly Efficient" if hr_efficiency_score >= 90 else "📊 Efficient" if hr_efficiency_score >= 80 else "🔧 Needs Optimization"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">⚖️ HR Efficiency</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{hr_efficiency_score}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{efficiency_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        # Strategic ROI with business impact
        roi_status = "📈 High ROI" if strategic_roi >= 20 else "💡 Good ROI" if strategic_roi >= 10 else "📊 Moderate ROI"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A936F 0%, #88D498 100%); padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: white; margin: 0; font-size: 14px;">📈 Strategic ROI</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{strategic_roi:.1f}%</h2>
            <p style="color: white; margin: 0; font-size: 12px;">{roi_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">💰 Employee Lifetime Value & Business Impact</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.compensation.empty and not st.session_state.performance.empty:
            elv_data, elv_msg = calculate_employee_lifetime_value(st.session_state.employees, st.session_state.compensation, st.session_state.performance)
            
            # Enhanced metric with context
            elv_val = float(elv_msg.split(': ')[1].split('$')[1].split('K')[0]) * 1000 if ': ' in elv_msg and '$' in elv_msg and 'K' in elv_msg else employee_lifetime_value
            elv_status = "💰 High Value Employees" if elv_val >= 200000 else "💵 Good Value Employees" if elv_val >= 100000 else "📈 Growing Value Employees"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #667eea; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{elv_status} Average ELV: {elv_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not elv_data.empty:
                # Enhanced histogram with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['department', 'job_title', 'performance_rating', 'tenure_years', 'total_compensation'] if col in elv_data.columns]
                
                fig_elv = px.histogram(
                    elv_data, 
                    x='elv',
                    title='💰 Employee Lifetime Value Distribution',
                    nbins=20,
                    color_discrete_sequence=['#667eea'],
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>ELV Range: %{x}</b><br>Count: %{y}<br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'performance_rating':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                        elif col == 'total_compensation':
                            hover_template += f"{col.replace('_', ' ').title()}: $%{{customdata[{i}]}}<br>"
                        else:
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>ELV Range: %{x}</b><br>Count: %{y}<br><extra></extra>"
                
                fig_elv.update_traces(
                    hovertemplate=hover_template,
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_elv.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Employee Lifetime Value ($)",
                    yaxis_title="Number of Employees",
                    font=dict(size=12),
                    showlegend=False
                )
                
                # Add interpretable legend annotations
                fig_elv.add_annotation(
                    text="💰 Higher bars = More employees in that value range<br>📊 Distribution shows employee value spread<br>💵 Right side = High-value employees<br>📈 Left side = Growth potential employees",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_elv, use_container_width=True, key="strategic_elv")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">🤖 Cost Savings from Automation & Digital Transformation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        automation_data, automation_msg = calculate_cost_savings_from_automation(st.session_state.employees)
        
        # Enhanced metric with context
        automation_val = float(automation_msg.split(': ')[1].split('$')[1].split('K')[0]) * 1000 if ': ' in automation_msg and '$' in automation_msg and 'K' in automation_msg else automation_savings
        automation_status = "🚀 High Savings Potential" if automation_val >= 100000 else "💡 Good Savings Potential" if automation_val >= 50000 else "📊 Moderate Savings Potential"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #f093fb; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{automation_status} Total Savings: {automation_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not automation_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['current_cost', 'automation_cost', 'savings_percentage', 'implementation_time'] if col in automation_data.columns]
            
            fig_automation = px.bar(
                automation_data, 
                x='department', 
                y='automation_savings',
                title='🤖 Automation Savings by Department',
                color='automation_savings',
                color_continuous_scale='plasma',
                text='automation_savings',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>Automation Savings: $%{y:,.0f}<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'current_cost':
                        hover_template += f"{col.replace('_', ' ').title()}: $%{{customdata[{i}]:,.0f}}<br>"
                    elif col == 'automation_cost':
                        hover_template += f"{col.replace('_', ' ').title()}: $%{{customdata[{i}]:,.0f}}<br>"
                    elif col == 'savings_percentage':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]:.1f}}%<br>"
                    elif col == 'implementation_time':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} months<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>Automation Savings: $%{y:,.0f}<br><extra></extra>"
            
            fig_automation.update_traces(
                hovertemplate=hover_template,
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_automation.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="Automation Savings ($)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Savings Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_automation.add_annotation(
                text="🤖 Higher bars = More savings potential<br>📊 Color intensity = Savings level<br>🚀 Purple areas = High automation potential<br>💡 Red areas = Moderate automation potential",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_automation, use_container_width=True, key="strategic_automation")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📊 HR Efficiency Metrics & Process Optimization</h4>
        </div>
        """, unsafe_allow_html=True)
        
        efficiency_data, efficiency_msg = calculate_hr_efficiency_metrics(st.session_state.employees)
        
        # Enhanced metric with context
        efficiency_val = float(efficiency_msg.split(': ')[1].split('%')[0]) if ': ' in efficiency_msg and '%' in efficiency_msg else hr_efficiency_score
        efficiency_status = "🚀 Highly Efficient" if efficiency_val >= 90 else "📊 Efficient" if efficiency_val >= 80 else "🔧 Needs Optimization"
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4facfe; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{efficiency_status} HR Efficiency: {efficiency_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not efficiency_data.empty:
            # Enhanced bar chart with interpretable legends and detailed tooltips
            # Use only available columns for hover data
            available_hover_cols = [col for col in ['process_time', 'automation_level', 'cost_per_employee', 'satisfaction_score'] if col in efficiency_data.columns]
            
            fig_efficiency = px.bar(
                efficiency_data, 
                x='department', 
                y='hr_efficiency_score',
                title='📊 HR Efficiency by Department',
                color='hr_efficiency_score',
                color_continuous_scale='Greens',
                text='hr_efficiency_score',
                hover_data=available_hover_cols
            )
            
            # Customize tooltips for better interpretation
            if available_hover_cols:
                hover_template = "<b>%{x}</b><br>HR Efficiency: %{y:.1f}%<br>"
                for i, col in enumerate(available_hover_cols):
                    if col == 'process_time':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} days<br>"
                    elif col == 'automation_level':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                    elif col == 'cost_per_employee':
                        hover_template += f"{col.replace('_', ' ').title()}: $%{{customdata[{i}]}}<br>"
                    elif col == 'satisfaction_score':
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}/5<br>"
                    else:
                        hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                hover_template += "<extra></extra>"
            else:
                hover_template = "<b>%{x}</b><br>HR Efficiency: %{y:.1f}%<br><extra></extra>"
            
            fig_efficiency.update_traces(
                hovertemplate=hover_template,
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_efficiency.update_layout(
                title_font_size=18,
                title_font_color='#333',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Department",
                yaxis_title="HR Efficiency Score (%)",
                font=dict(size=12),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Efficiency Level",
                        side="right"
                    )
                )
            )
            
            # Add interpretable legend annotations
            fig_efficiency.add_annotation(
                text="🟢 Green = High efficiency<br>🟡 Light green = Good efficiency<br>🔴 Dark green = Low efficiency<br>📊 90%+ = Target efficiency",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#666"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ccc",
                borderwidth=1
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True, key="strategic_efficiency")
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">📈 Strategic Insights & Employee Advocacy</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.engagement.empty:
            enps_data, enps_msg = calculate_employee_net_promoter_score(st.session_state.engagement)
            
            # Enhanced metric with context
            enps_val = float(enps_msg.split(': ')[1]) if ': ' in enps_msg else 0
            enps_status = "🏆 Excellent Advocacy" if enps_val >= 50 else "📈 Good Advocacy" if enps_val >= 20 else "⚠️ Needs Improvement"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #43e97b; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{enps_status} eNPS: {enps_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not enps_data.empty:
                # Enhanced histogram with interpretable legends and detailed tooltips
                # Use only available columns for hover data
                available_hover_cols = [col for col in ['department', 'job_title', 'tenure_years', 'engagement_level', 'advocacy_potential'] if col in enps_data.columns]
                
                fig_enps = px.histogram(
                    enps_data, 
                    x='recommendation_score',
                    title='📈 Employee Net Promoter Score Distribution',
                    nbins=10,
                    color_discrete_sequence=['#43e97b'],
                    hover_data=available_hover_cols
                )
                
                # Customize tooltips for better interpretation
                if available_hover_cols:
                    hover_template = "<b>Recommendation Score: %{x}</b><br>Count: %{y}<br>"
                    for i, col in enumerate(available_hover_cols):
                        if col == 'tenure_years':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}} years<br>"
                        elif col == 'engagement_level':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                        elif col == 'advocacy_potential':
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}%<br>"
                        else:
                            hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{i}]}}<br>"
                    hover_template += "<extra></extra>"
                else:
                    hover_template = "<b>Recommendation Score: %{x}</b><br>Count: %{y}<br><extra></extra>"
                
                fig_enps.update_traces(
                    hovertemplate=hover_template,
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_enps.update_layout(
                    title_font_size=18,
                    title_font_color='#333',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Recommendation Score (0-10)",
                    yaxis_title="Number of Employees",
                    font=dict(size=12),
                    showlegend=False
                )
                
                # Add interpretable legend annotations
                fig_enps.add_annotation(
                    text="📈 Higher scores = More promoters<br>📊 Distribution shows advocacy spread<br>🏆 9-10 = Promoters (advocates)<br>⚠️ 0-6 = Detractors (risks)",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    font=dict(size=10, color="#666"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ccc",
                    borderwidth=1
                )
                
                st.plotly_chart(fig_enps, use_container_width=True, key="strategic_enps")
    
    # Comprehensive Strategic HR Insights & Action Plan
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 Strategic HR Insights & Business Intelligence Action Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate key strategic insights
    high_elv_depts = elv_data[elv_data['elv'] >= 200000]['department'].tolist() if 'elv_data' in locals() and not elv_data.empty else []
    high_automation_depts = automation_data[automation_data['automation_savings'] >= 50000]['department'].tolist() if 'automation_data' in locals() and not automation_data.empty else []
    high_efficiency_depts = efficiency_data[efficiency_data['hr_efficiency_score'] >= 90]['department'].tolist() if 'efficiency_data' in locals() and not efficiency_data.empty else []
    
    # Create strategic insights dashboard
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">💰 High Value Departments</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_elv_depts) if high_elv_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">🤖 High Automation Potential</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {', '.join(high_automation_depts) if high_automation_depts else 'None identified'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 10px 0;">
            <h4 style="margin: 0; color: #333;">📊 Strategic HR Health Score</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                {hr_effectiveness:.1f}% Overall Effectiveness<br>
                {strategic_roi:.1f}% Strategic ROI
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic recommendations
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">💡 Strategic Business Intelligence Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">🚀 Immediate Strategic Actions (0-30 days)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Prioritize automation in high-savings potential departments</li>
                <li>Focus retention efforts on high-value employee segments</li>
                <li>Optimize HR processes in low-efficiency departments</li>
                <li>Develop strategic workforce planning initiatives</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h5 style="margin: 0; color: #333;">📈 Long-term Strategic Initiatives (3-12 months)</h5>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
                <li>Implement comprehensive HR digital transformation</li>
                <li>Develop advanced employee lifetime value optimization</li>
                <li>Create strategic workforce analytics and forecasting</li>
                <li>Establish HR business intelligence and reporting systems</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic success metrics
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 Strategic HR Success Metrics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Target HR Effectiveness", "90%+", f"{hr_effectiveness - 90:.1f}%" if hr_effectiveness < 90 else "✅ Achieved")
    
    with metric_col2:
        st.metric("Employee Lifetime Value", "$200K+", f"${(elv_val - 200000)/1000:.0f}K" if 'elv_val' in locals() and elv_val < 200000 else "✅ Achieved")
    
    with metric_col3:
        st.metric("Automation Savings", "$100K+", f"${(automation_val - 100000)/1000:.0f}K" if 'automation_val' in locals() and automation_val < 100000 else "✅ Achieved")
    
    with metric_col4:
        st.metric("Strategic ROI", "20%+", f"{strategic_roi - 20:.1f}%" if strategic_roi < 20 else "✅ Achieved")

if __name__ == "__main__":
    main()



