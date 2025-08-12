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

# Plotly imports for charts
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Machine Learning imports
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import time

# Import Finance metric calculation functions
try:
    from finance_metrics_calculator import *
except ImportError as e:
    st.error(f"Error importing finance_metrics_calculator: {e}")
    # Define fallback functions
    def calculate_financial_performance_metrics(income_statement_data, balance_sheet_data):
        return pd.DataFrame(), "Error: Could not import metrics calculator"
    def calculate_liquidity_solvency_metrics(balance_sheet_data, cash_flow_data):
        return pd.DataFrame(), "Error: Could not import metrics calculator"

# Import auto insights functionality
try:
    from finance_auto_insights import (
        FinanceInsights, display_insights_section, display_executive_summary, 
        generate_financial_performance_ai_recommendations, 
        generate_liquidity_solvency_ai_recommendations, 
        generate_liquidity_analysis_ai_recommendations, 
        generate_solvency_metrics_ai_recommendations, 
        generate_cash_flow_analysis_ai_recommendations,
        generate_roa_roe_analysis_ai_recommendations,
        generate_asset_turnover_ai_recommendations,
        generate_expense_efficiency_ai_recommendations,
        generate_productivity_trends_ai_recommendations,
        generate_budget_variance_analysis_ai_recommendations,
        generate_forecast_accuracy_ai_recommendations,
        generate_scenario_analysis_ai_recommendations,
        generate_variance_reporting_ai_recommendations,
        generate_operating_cash_flow_ai_recommendations,
        generate_free_cash_flow_ai_recommendations,
        generate_working_capital_ai_recommendations,
        generate_cash_flow_trends_ai_recommendations,
        generate_debt_analysis_ai_recommendations,
        generate_wacc_calculation_ai_recommendations,
        generate_interest_coverage_ai_recommendations,
        generate_capital_optimization_ai_recommendations,
        generate_npv_analysis_ai_recommendations,
        generate_payback_period_ai_recommendations,
        generate_eva_calculation_ai_recommendations,
        generate_investment_insights_ai_recommendations,
        generate_customer_profitability_ai_recommendations,
        generate_product_profitability_ai_recommendations,
        generate_value_chain_analysis_ai_recommendations,
        generate_strategic_insights_ai_recommendations
    )
except ImportError as e:
    st.error(f"Error importing finance_auto_insights: {e}")
    FinanceInsights = None
    display_insights_section = None
    display_executive_summary = None
    generate_financial_performance_ai_recommendations = None
    generate_liquidity_solvency_ai_recommendations = None
    generate_liquidity_analysis_ai_recommendations = None
    generate_solvency_metrics_ai_recommendations = None
    generate_cash_flow_analysis_ai_recommendations = None
    generate_roa_roe_analysis_ai_recommendations = None
    generate_asset_turnover_ai_recommendations = None
    generate_expense_efficiency_ai_recommendations = None
    generate_productivity_trends_ai_recommendations = None
    generate_budget_variance_analysis_ai_recommendations = None
    generate_forecast_accuracy_ai_recommendations = None
    generate_scenario_analysis_ai_recommendations = None
    generate_variance_reporting_ai_recommendations = None
    generate_operating_cash_flow_ai_recommendations = None
    generate_free_cash_flow_ai_recommendations = None
    generate_working_capital_ai_recommendations = None
    generate_cash_flow_trends_ai_recommendations = None
    generate_debt_analysis_ai_recommendations = None
    generate_wacc_calculation_ai_recommendations = None
    generate_interest_coverage_ai_recommendations = None
    generate_capital_optimization_ai_recommendations = None
    generate_npv_analysis_ai_recommendations = None
    generate_payback_period_ai_recommendations = None
    generate_eva_calculation_ai_recommendations = None
    generate_investment_insights_ai_recommendations = None

# Import risk analyzer functionality
try:
    from finance_risk_analyzer import FinanceRiskAnalyzer, display_risk_dashboard
except ImportError as e:
    st.error(f"Error importing finance_risk_analyzer: {e}")
    FinanceRiskAnalyzer = None
    display_risk_dashboard = None

# Import predictive analytics functionality
try:
    from finance_predictive_analytics import display_finance_predictive_analytics_dashboard, FinancePredictiveAnalytics
except ImportError as e:
    st.error(f"Error importing finance_predictive_analytics: {e}")
    display_finance_predictive_analytics_dashboard = None
    FinancePredictiveAnalytics = None

def format_ai_recommendations(recommendations_text):
    """
    Format AI recommendations text to display properly in Streamlit with each bullet point on a separate line.
    Remove double asterisks and emoji characters from headings.
    """
    if not recommendations_text:
        return ""
    
    # Split the text into lines
    lines = recommendations_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue
            
        # If it's already a bullet point, keep it as is
        if line.startswith("   •"):
            formatted_lines.append(line)
        # If it's a heading with emoji and double asterisks, clean it up
        elif (line.startswith("🤖") or line.startswith("🎯") or line.startswith("💰") or 
              line.startswith("💸") or line.startswith("⚠️") or line.startswith("👥") or 
              line.startswith("📦") or line.startswith("🔍") or line.startswith("🟢") or 
              line.startswith("🟡") or line.startswith("🟠") or line.startswith("🔴") or 
              line.startswith("📈") or line.startswith("📉")):
            # Remove double asterisks and emoji, keep only the text
            cleaned_line = line
            # Remove emoji characters
            emoji_patterns = ["🤖", "🎯", "💰", "💸", "⚠️", "👥", "📦", "🔍", "🟢", "🟡", "🟠", "🔴", "📈", "📉"]
            for emoji in emoji_patterns:
                cleaned_line = cleaned_line.replace(emoji, "")
            # Remove double asterisks
            cleaned_line = cleaned_line.replace("**", "")
            # Clean up extra spaces
            cleaned_line = cleaned_line.strip()
            formatted_lines.append(cleaned_line)
        # If it contains bullet points on the same line, split them
        elif "•" in line:
            # Split by bullet points
            parts = line.split("•")
            for i, part in enumerate(parts):
                part = part.strip()
                if part:
                    if i == 0:  # First part (before first bullet)
                        formatted_lines.append(part)
                    else:  # Bullet point parts
                        formatted_lines.append(f"   • {part}")
        else:
            # Regular line, keep as is
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)

def display_formatted_recommendations(recommendations_text):
    """
    Display AI recommendations with proper formatting using HTML to ensure bullet points are on separate lines.
    """
    if not recommendations_text:
        return
    
    # Convert the text to HTML format for better display
    html_content = recommendations_text.replace('\n', '<br>')
    
    # Replace bullet points with proper HTML list items
    lines = recommendations_text.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            html_lines.append("<br>")
        elif line.startswith("   •"):
            # Convert bullet point to HTML list item
            content = line.replace("   •", "").strip()
            html_lines.append(f"<li>{content}</li>")
        elif line and not line.startswith("   •") and not "•" in line:
            # This is a heading (already cleaned of emoji and asterisks), add it as a header
            html_lines.append(f"<h4>{line}</h4>")
        elif "•" in line:
            # Split by bullet points and create list items
            parts = line.split("•")
            for i, part in enumerate(parts):
                part = part.strip()
                if part:
                    if i == 0:  # First part (before first bullet)
                        html_lines.append(f"<h4>{part}</h4>")
                    else:  # Bullet point parts
                        html_lines.append(f"<li>{part}</li>")
        else:
            # Regular line
            html_lines.append(f"<p>{line}</p>")
    
    # Combine into HTML with proper list structure
    html_content = ""
    in_list = False
    
    for line in html_lines:
        if line.startswith("<li>"):
            if not in_list:
                html_content += "<ul>"
                in_list = True
            html_content += line
        elif line.startswith("<h4>"):
            if in_list:
                html_content += "</ul>"
                in_list = False
            html_content += line
        elif line.startswith("<p>"):
            if in_list:
                html_content += "</ul>"
                in_list = False
            html_content += line
        elif line == "<br>":
            if in_list:
                html_content += "</ul>"
                in_list = False
            html_content += line
    
    # Close any open list
    if in_list:
        html_content += "</ul>"
    
    # Display using HTML
    st.markdown(html_content, unsafe_allow_html=True)

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
    """Return a list of numeric columns, excluding 'supplier'."""
    return [col for col in df.select_dtypes(include=['number']).columns if col != 'supplier']

def get_categorical_columns(df):
    """Return a list of categorical/object columns, excluding 'supplier'."""
    return [col for col in df.select_dtypes(include=['object']).columns if col != 'supplier']

# --- Utility Functions ---
def get_variable_list(df):
    """Get list of variables for analysis."""
    return [col for col in df.columns if col not in ['supplier', 'period', 'date']]

def normalize_column(col, minimize=False):
    """Normalize a column to 0-1 scale."""
    if minimize:
        return (col.max() - col) / (col.max() - col.min())
    else:
        return (col - col.min()) / (col.max() - col.min())

def get_weights(variables, scenario):
    """Get weights for different scenarios."""
    if scenario == "balanced":
        return {var: 1/len(variables) for var in variables}
    elif scenario == "cost_focused":
        return {var: 0.6 if 'cost' in var.lower() or 'price' in var.lower() else 0.4/(len(variables)-1) for var in variables}
    elif scenario == "quality_focused":
        return {var: 0.6 if 'quality' in var.lower() or 'score' in var.lower() else 0.4/(len(variables)-1) for var in variables}
    else:
        return {var: 1/len(variables) for var in variables}

def apply_common_layout(fig):
    """Apply common layout settings to plots."""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

def truncate_col(text, max_len=20):
    """Truncate text for table columns"""
    text = str(text)
    return text[:max_len] + '...' if len(text) > max_len else text

def get_column_name(merged_data, column_name):
    """Helper function to get the correct column name after merge operations."""
    if column_name in merged_data.columns:
        return column_name
    
    # Check for common suffixes that pandas adds during merges
    possible_names = [
        column_name,
        f"{column_name}_x",
        f"{column_name}_y",
        f"{column_name}_1",
        f"{column_name}_2"
    ]
    
    # For specific columns, add additional possible names
    if column_name == 'unit_price':
        possible_names.extend(['price', 'unit_cost'])
    elif column_name == 'supplier_id':
        possible_names.extend(['supplier', 'vendor_id'])
    elif column_name == 'item_name':
        possible_names.extend(['name', 'product_name'])
    
    return next((name for name in possible_names if name in merged_data.columns), None)

def get_unit_price_column(merged_data):
    """Helper function to get the correct unit price column name after merge operations."""
    return get_column_name(merged_data, 'unit_price')

def check_data_quality(po_df, items_data, suppliers):
    """Check data quality and provide recommendations."""
    issues = []
    recommendations = []
    
    # Check for missing data
    if po_df.empty:
        issues.append("No purchase order data found")
        recommendations.append("Upload purchase order data")
    
    if items_data.empty:
        issues.append("No items data found")
        recommendations.append("Upload items data")
    
    if suppliers.empty:
        issues.append("No suppliers data found")
        recommendations.append("Upload suppliers data")
    
    # Check for required columns
    required_po_cols = ['supplier_id', 'item_id', 'quantity', 'unit_price']
    missing_po_cols = [col for col in required_po_cols if col not in po_df.columns]
    if missing_po_cols:
        issues.append(f"Missing required columns in purchase orders: {', '.join(missing_po_cols)}")
        recommendations.append("Ensure all required columns are present in purchase order data")
    
    # Check for data consistency
    if not po_df.empty and not items_data.empty:
        po_items = set(po_df['item_id'].unique())
        available_items = set(items_data['item_id'].unique())
        missing_items = po_items - available_items
        if missing_items:
            issues.append(f"Purchase orders reference {len(missing_items)} items not found in items data")
            recommendations.append("Ensure all items in purchase orders exist in items data")
    
    return issues, recommendations

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

def display_dataframe_with_index_1(df, **kwargs):
    """Display dataframe with index starting from 1"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        return st.dataframe(df_display, **kwargs)
    else:
        return st.dataframe(df, **kwargs)

def safe_calculate_variance(actual, budget, metric_name="metric"):
    """Safely calculate variance with error handling"""
    try:
        if budget > 0:
            return ((actual - budget) / budget * 100)
        else:
            return 0
    except (TypeError, ValueError, ZeroDivisionError):
        st.warning(f"⚠️ Unable to calculate {metric_name} variance due to data issues")
        return 0

def create_template_for_download():
    """Create an Excel template with all required Finance data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct Finance schema
    income_statement_template = pd.DataFrame(columns=[
        'period', 'revenue', 'cost_of_goods_sold', 'gross_profit', 'operating_expenses',
        'operating_income', 'interest_expense', 'income_tax_expense', 'net_income'
    ])
    
    balance_sheet_template = pd.DataFrame(columns=[
        'period', 'cash_and_equivalents', 'accounts_receivable', 'inventory', 'current_assets',
        'total_assets', 'accounts_payable', 'current_liabilities', 'total_liabilities',
        'shareholder_equity', 'shares_outstanding'
    ])
    
    cash_flow_template = pd.DataFrame(columns=[
        'period', 'net_income', 'depreciation', 'working_capital_change', 'operating_cash_flow',
        'capital_expenditures', 'free_cash_flow', 'initial_investment', 'cash_flow', 'nopat'
    ])
    
    budget_template = pd.DataFrame(columns=[
        'period', 'revenue', 'expenses', 'profit', 'category'
    ])
    
    forecast_template = pd.DataFrame(columns=[
        'period', 'revenue', 'expenses', 'profit', 'confidence_level'
    ])
    
    market_template = pd.DataFrame(columns=[
        'period', 'market_price', 'dividends_per_share', 'volume', 'market_cap'
    ])
    
    customer_template = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'revenue', 'profit_margin', 'profitability', 
        'costs_to_serve', 'segment', 'region', 'lifetime_value'
    ])
    
    product_template = pd.DataFrame(columns=[
        'product_id', 'product_name', 'revenue', 'cost', 'total_costs', 'direct_costs', 
        'allocated_costs', 'margin', 'category', 'lifecycle_stage'
    ])
    
    value_chain_template = pd.DataFrame(columns=[
        'function', 'cost', 'percentage', 'period'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        income_statement_template.to_excel(writer, sheet_name='Income_Statement', index=False)
        balance_sheet_template.to_excel(writer, sheet_name='Balance_Sheet', index=False)
        cash_flow_template.to_excel(writer, sheet_name='Cash_Flow', index=False)
        budget_template.to_excel(writer, sheet_name='Budget', index=False)
        forecast_template.to_excel(writer, sheet_name='Forecast', index=False)
        market_template.to_excel(writer, sheet_name='Market_Data', index=False)
        customer_template.to_excel(writer, sheet_name='Customer_Data', index=False)
        product_template.to_excel(writer, sheet_name='Product_Data', index=False)
        value_chain_template.to_excel(writer, sheet_name='Value_Chain', index=False)
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Income_Statement', 'Balance_Sheet', 'Cash_Flow', 'Budget', 'Forecast', 'Market_Data', 'Customer_Data', 'Product_Data', 'Value_Chain'],
            'Required Fields': [
                'period, revenue, cost_of_goods_sold, gross_profit, operating_expenses, operating_income, interest_expense, income_tax_expense, net_income',
                'period, cash_and_equivalents, accounts_receivable, inventory, current_assets, total_assets, accounts_payable, current_liabilities, total_liabilities, shareholder_equity, shares_outstanding',
                'period, net_income, depreciation, working_capital_change, operating_cash_flow, capital_expenditures, free_cash_flow, initial_investment, cash_flow, nopat',
                'period, revenue, expenses, profit, category',
                'period, revenue, expenses, profit, confidence_level',
                'period, market_price, dividends_per_share, volume, market_cap',
                'customer_id, customer_name, revenue, profit_margin, profitability, costs_to_serve, segment, region, lifetime_value',
                'product_id, product_name, revenue, cost, total_costs, direct_costs, allocated_costs, margin, category, lifecycle_stage',
                'function, cost, percentage, period'
            ],
            'Data Types': [
                'Date, Number, Number, Number, Number, Number, Number, Number, Number',
                'Date, Number, Number, Number, Number, Number, Number, Number, Number, Number, Number',
                'Date, Number, Number, Number, Number, Number, Number, Number, Number, Number, Number',
                'Date, Number, Number, Number, Text',
                'Date, Number, Number, Number, Number',
                'Date, Number, Number, Number, Number',
                'Text, Text, Number, Number, Number, Number, Text, Text, Number',
                'Text, Text, Number, Number, Number, Number, Number, Number, Text, Text',
                'Text, Number, Number, Date'
            ],
            'Description': [
                'Income statement with revenue, costs, and profitability metrics',
                'Balance sheet with assets, liabilities, and equity',
                'Cash flow statement with operating, investing, and financing activities',
                'Budget data for variance analysis',
                'Forecast data for accuracy measurement',
                'Market data including stock prices and dividends',
                'Customer profitability analysis',
                'Product/service profitability analysis',
                'Value chain cost analysis by function'
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
    """Export all Finance data to Excel file"""
    if (st.session_state.income_statement.empty and st.session_state.balance_sheet.empty and 
        st.session_state.cash_flow.empty and st.session_state.budget.empty and
        st.session_state.forecast.empty and st.session_state.market_data.empty and
        st.session_state.customer_data.empty and st.session_state.product_data.empty and
        st.session_state.value_chain.empty):
        st.warning("No data to export. Please add data first.")
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each DataFrame to a separate sheet
        st.session_state.income_statement.to_excel(writer, sheet_name='Income_Statement', index=False)
        st.session_state.balance_sheet.to_excel(writer, sheet_name='Balance_Sheet', index=False)
        st.session_state.cash_flow.to_excel(writer, sheet_name='Cash_Flow', index=False)
        st.session_state.budget.to_excel(writer, sheet_name='Budget', index=False)
        st.session_state.forecast.to_excel(writer, sheet_name='Forecast', index=False)
        st.session_state.market_data.to_excel(writer, sheet_name='Market_Data', index=False)
        st.session_state.customer_data.to_excel(writer, sheet_name='Customer_Data', index=False)
        st.session_state.product_data.to_excel(writer, sheet_name='Product_Data', index=False)
        st.session_state.value_chain.to_excel(writer, sheet_name='Value_Chain', index=False)
    
    output.seek(0)
    return output

# Page configuration
st.set_page_config(
    page_title="Finance Analytics Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
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
    .section-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .section-header h3 {
        color: white;
        margin: 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for Finance data storage
if 'income_statement' not in st.session_state:
    st.session_state.income_statement = pd.DataFrame(columns=[
        'period', 'revenue', 'cost_of_goods_sold', 'gross_profit', 'operating_expenses',
        'operating_income', 'interest_expense', 'income_tax_expense', 'net_income'
    ])

if 'balance_sheet' not in st.session_state:
    st.session_state.balance_sheet = pd.DataFrame(columns=[
        'period', 'cash_and_equivalents', 'accounts_receivable', 'inventory', 'current_assets',
        'total_assets', 'accounts_payable', 'current_liabilities', 'total_liabilities',
        'shareholder_equity', 'shares_outstanding'
    ])

if 'cash_flow' not in st.session_state:
    st.session_state.cash_flow = pd.DataFrame(columns=[
        'period', 'net_income', 'depreciation', 'working_capital_change', 'operating_cash_flow',
        'capital_expenditures', 'free_cash_flow', 'initial_investment', 'cash_flow', 'nopat'
    ])

if 'budget' not in st.session_state:
    st.session_state.budget = pd.DataFrame(columns=[
        'period', 'revenue', 'expenses', 'profit', 'category'
    ])

if 'forecast' not in st.session_state:
    st.session_state.forecast = pd.DataFrame(columns=[
        'period', 'revenue', 'expenses', 'profit', 'confidence_level'
    ])

if 'market_data' not in st.session_state:
    st.session_state.market_data = pd.DataFrame(columns=[
        'period', 'market_price', 'dividends_per_share', 'volume', 'market_cap'
    ])

if 'customer_data' not in st.session_state:
    st.session_state.customer_data = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'revenue', 'costs_to_serve', 'profitability'
    ])

if 'product_data' not in st.session_state:
    st.session_state.product_data = pd.DataFrame(columns=[
        'product_id', 'product_name', 'revenue', 'direct_costs', 'allocated_costs', 'total_costs'
    ])

if 'value_chain' not in st.session_state:
    st.session_state.value_chain = pd.DataFrame(columns=[
        'function', 'cost', 'percentage', 'period'
    ])

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="Finance Analytics",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">💰 Finance Analytics</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'income_statement' not in st.session_state:
        st.session_state.income_statement = pd.DataFrame()
    if 'balance_sheet' not in st.session_state:
        st.session_state.balance_sheet = pd.DataFrame()
    if 'cash_flow' not in st.session_state:
        st.session_state.cash_flow = pd.DataFrame()
    if 'budget' not in st.session_state:
        st.session_state.budget = pd.DataFrame()
    if 'forecast' not in st.session_state:
        st.session_state.forecast = pd.DataFrame()
    if 'market_data' not in st.session_state:
        st.session_state.market_data = pd.DataFrame()
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = pd.DataFrame()
    if 'product_data' not in st.session_state:
        st.session_state.product_data = pd.DataFrame()
    if 'value_chain' not in st.session_state:
        st.session_state.value_chain = pd.DataFrame()
    
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
        
        if st.button("🎯 Auto Insights", key="nav_auto_insights", use_container_width=True):
            st.session_state.current_page = "🤖 Auto Insights"
        
        if st.button("🔮 Predictive Analytics", key="nav_predictive", use_container_width=True):
            st.session_state.current_page = "🔮 Predictive Analytics"
        
        if st.button("📈 Financial Performance", key="nav_financial_performance", use_container_width=True):
            st.session_state.current_page = "📊 Financial Performance"
        
        if st.button("💧 Liquidity & Solvency", key="nav_liquidity_solvency", use_container_width=True):
            st.session_state.current_page = "💧 Liquidity & Solvency"
        
        if st.button("⚡ Efficiency & Productivity", key="nav_efficiency_productivity", use_container_width=True):
            st.session_state.current_page = "⚡ Efficiency & Productivity"
        
        if st.button("📋 Budget & Forecasting", key="nav_budget_forecasting", use_container_width=True):
            st.session_state.current_page = "📋 Budget & Forecasting"
        
        if st.button("💸 Cash Flow", key="nav_cash_flow", use_container_width=True):
            st.session_state.current_page = "💸 Cash Flow"
        
        if st.button("🏗️ Capital Structure", key="nav_capital_structure", use_container_width=True):
            st.session_state.current_page = "🏗️ Capital Structure"
        
        if st.button("📈 Investment & Valuation", key="nav_investment_valuation", use_container_width=True):
            st.session_state.current_page = "📈 Investment & Valuation"
        
        if st.button("🛡️ Risk & Compliance", key="nav_risk_compliance", use_container_width=True):
            st.session_state.current_page = "⚠️ Risk & Compliance"
        
        if st.button("📊 Strategic KPIs", key="nav_strategic_kpis", use_container_width=True):
            st.session_state.current_page = "📊 Strategic KPIs"
        
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
    
    elif page == "🤖 Auto Insights":
        show_auto_insights()
    
    elif page == "🔮 Predictive Analytics":
        show_predictive_analytics()
    
    elif page == "📊 Financial Performance":
        show_financial_performance()
    
    elif page == "💧 Liquidity & Solvency":
        show_liquidity_solvency()
    
    elif page == "⚡ Efficiency & Productivity":
        show_efficiency_productivity()
    
    elif page == "📋 Budget & Forecasting":
        show_budget_forecasting()
    
    elif page == "💸 Cash Flow":
        show_cash_flow()
    
    elif page == "🏗️ Capital Structure":
        show_capital_structure()
    
    elif page == "📈 Investment & Valuation":
        show_investment_valuation()
    
    elif page == "⚠️ Risk & Compliance":
        show_risk_compliance()
    
    elif page == "📊 Strategic KPIs":
        show_strategic_kpis()

def show_home():
    st.markdown("""
    <div class="section-header">
        <h3>🏠 Welcome to Finance Analytics Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 💰 Comprehensive Finance Analytics Platform
    
    This dashboard provides comprehensive analytics for Finance departments, 
    covering all aspects from financial performance to strategic financial analysis.
    
    #### 📊 **Key Analytics Categories:**
    
    **📊 Financial Performance Analysis**
    - Revenue Growth Rate Analysis
    - Gross Margin Optimization
    - Operating Margin Tracking
    - Net Margin Analysis
    - Earnings per Share (EPS) Calculation
    
    **💧 Liquidity and Solvency**
    - Current Ratio Analysis
    - Quick Ratio Assessment
    - Cash Conversion Cycle (CCC)
    - Debt Service Coverage Ratio (DSCR)
    
    **⚡ Efficiency and Productivity**
    - Return on Assets (ROA)
    - Return on Equity (ROE)
    - Asset Turnover Ratio
    - Operating Expense Ratio
    
    **📋 Budgeting, Forecasting & Variance**
    - Budget Variance Analysis
    - Forecast Accuracy (MAPE)
    - Scenario Analysis
    - Variance Reporting
    
    **💸 Cash Flow & Working Capital**
    - Operating Cash Flow Analysis
    - Free Cash Flow (FCF) Calculation
    - Working Capital Turnover
    - Cash Flow Optimization
    
    **🏗️ Capital Structure & Financing**
    - Debt-to-Equity Ratio
    - Weighted Average Cost of Capital (WACC)
    - Interest Coverage Ratio
    - Capital Structure Optimization
    
    **📈 Investment & Valuation**
    - Net Present Value (NPV)
    - Internal Rate of Return (IRR)
    - Payback Period Analysis
    - Economic Value Added (EVA)
    
    **⚠️ Risk & Compliance**
    - Value at Risk (VaR)
    - Liquidity Risk Metrics
    - Capital Adequacy Ratio (CAR)
    - Risk Management Analysis
    
    **📊 Strategic Financial KPIs**
    - Customer Profitability Analysis
    - Product/Service Profitability
    - Value Chain Cost Analysis
    - Strategic Financial Insights
    
    ---
    
    ### 📈 **Getting Started:**
    
    1. **📝 Data Input**: Upload your financial data or use the template provided
    2. **📊 Analytics**: Explore comprehensive metrics across all categories
    3. **📋 Reports**: Generate detailed reports and insights
    4. **📤 Export**: Download your analytics and data
    
    ### 🎯 **Data Requirements:**
    
    The dashboard requires data across 9 key areas:
    - **Income Statement**: Revenue, costs, and profitability data
    - **Balance Sheet**: Assets, liabilities, and equity information
    - **Cash Flow**: Operating, investing, and financing activities
    - **Budget**: Budgeted vs actual performance
    - **Forecast**: Forecasted vs actual performance
    - **Market Data**: Stock prices, dividends, market cap
    - **Customer Data**: Customer profitability analysis
    - **Product Data**: Product/service profitability
    - **Value Chain**: Cost analysis by function
    
    Start by uploading your data in the **Data Input** tab! 💰
    """)

def generate_sample_finance_data():
    """Generate comprehensive sample finance data for testing"""
    np.random.seed(42)
    
    # Generate periods with proper datetime format for forecasting
    periods = []
    for year in range(2020, 2024):
        for quarter in range(1, 5):
            # Create proper datetime for each quarter
            month = (quarter - 1) * 3 + 1  # Q1=Jan, Q2=Apr, Q3=Jul, Q4=Oct
            periods.append(f"{year}-{month:02d}-01")
    
    # Ensure we have at least 8 periods for forecasting
    if len(periods) < 8:
        # Add more periods if needed
        for year in range(2024, 2026):
            for quarter in range(1, 5):
                month = (quarter - 1) * 3 + 1
                periods.append(f"{year}-{month:02d}-01")
    
    # Income Statement Data - Ensure we have enough periods for forecasting
    # Generate more periods if needed for forecasting
    if len(periods) < 12:  # Ensure at least 12 periods for robust forecasting
        additional_periods = []
        for year in range(2024, 2027):  # Add more years
            for quarter in range(1, 5):
                month = (quarter - 1) * 3 + 1
                additional_periods.append(f"{year}-{month:02d}-01")
        periods.extend(additional_periods)
    
    # Create realistic revenue trends with some seasonality
    base_revenue = 2000000
    revenue_trend = []
    for i, period in enumerate(periods):
        # Add trend and seasonality
        trend = base_revenue * (1 + 0.05 * i)  # 5% growth per period
        seasonality = 1 + 0.1 * np.sin(2 * np.pi * i / 4)  # Quarterly seasonality
        noise = np.random.uniform(0.9, 1.1)  # Random noise
        revenue_trend.append(trend * seasonality * noise)
    
    income_statement = pd.DataFrame({
        'period': periods,
        'revenue': revenue_trend,
        'cost_of_goods_sold': [rev * np.random.uniform(0.5, 0.7) for rev in revenue_trend],
        'gross_profit': [rev * np.random.uniform(0.3, 0.5) for rev in revenue_trend],
        'operating_expenses': [rev * np.random.uniform(0.15, 0.25) for rev in revenue_trend],
        'operating_income': [rev * np.random.uniform(0.1, 0.2) for rev in revenue_trend],
        'interest_expense': [rev * np.random.uniform(0.02, 0.05) for rev in revenue_trend],
        'income_tax_expense': [rev * np.random.uniform(0.02, 0.04) for rev in revenue_trend],
        'net_income': [rev * np.random.uniform(0.08, 0.15) for rev in revenue_trend]
    })
    
    # Balance Sheet Data
    balance_sheet = pd.DataFrame({
        'period': periods,
        'total_assets': [rev * np.random.uniform(2.5, 4.0) for rev in revenue_trend],
        'current_assets': [rev * np.random.uniform(1.0, 2.0) for rev in revenue_trend],
        'cash_and_equivalents': [rev * np.random.uniform(0.2, 0.5) for rev in revenue_trend],
        'accounts_receivable': [rev * np.random.uniform(0.15, 0.3) for rev in revenue_trend],
        'inventory': [rev * np.random.uniform(0.1, 0.4) for rev in revenue_trend],
        'accounts_payable': [rev * np.random.uniform(0.1, 0.3) for rev in revenue_trend],
        'current_liabilities': [rev * np.random.uniform(0.4, 1.0) for rev in revenue_trend],
        'total_liabilities': [rev * np.random.uniform(1.0, 2.5) for rev in revenue_trend],
        'shareholder_equity': [rev * np.random.uniform(1.5, 3.0) for rev in revenue_trend],
        'shares_outstanding': [1000000] * len(periods)
    })
    
    # Cash Flow Data
    cash_flow = pd.DataFrame({
        'period': periods,
        'net_income': [rev * np.random.uniform(0.08, 0.15) for rev in revenue_trend],
        'depreciation': [rev * np.random.uniform(0.02, 0.05) for rev in revenue_trend],
        'working_capital_change': [rev * np.random.uniform(-0.1, 0.1) for rev in revenue_trend],
        'operating_cash_flow': [rev * np.random.uniform(0.08, 0.15) for rev in revenue_trend],
        'capital_expenditures': [rev * np.random.uniform(-0.3, -0.1) for rev in revenue_trend],
        'free_cash_flow': [rev * np.random.uniform(0.05, 0.12) for rev in revenue_trend],
        'initial_investment': [1000000 if i == 0 else 0 for i in range(len(periods))],
        'cash_flow': [rev * np.random.uniform(-0.1, 0.2) for rev in revenue_trend],
        'nopat': [rev * np.random.uniform(0.06, 0.12) for rev in revenue_trend]
    })
    
    # Budget Data
    budget = pd.DataFrame({
        'period': periods,
        'revenue': [rev * np.random.uniform(0.9, 1.1) for rev in revenue_trend],
        'expenses': [rev * np.random.uniform(0.6, 0.8) for rev in revenue_trend],
        'profit': [rev * np.random.uniform(0.1, 0.2) for rev in revenue_trend],
        'category': np.random.choice(['Budget', 'Forecast'], len(periods))
    })
    
    # Forecast Data - Use overlapping periods with income statement for testing
    # Use the last 8 periods from income statement to create forecast data
    forecast_periods = periods[-8:]  # Last 8 periods from income statement
    
    forecast = pd.DataFrame({
        'period': forecast_periods,
        'revenue': np.random.uniform(1200000, 6000000, len(forecast_periods)),
        'expenses': np.random.uniform(800000, 4000000, len(forecast_periods)),
        'profit': np.random.uniform(200000, 1800000, len(forecast_periods)),
        'confidence_level': np.random.uniform(0.6, 0.95, len(forecast_periods))
    })
    
    # Market Data
    market_data = pd.DataFrame({
        'period': periods,
        'market_price': np.random.uniform(50, 200, len(periods)),
        'dividends_per_share': np.random.uniform(1, 5, len(periods)),
        'volume': np.random.uniform(1000000, 5000000, len(periods)),
        'market_cap': np.random.uniform(10000000, 50000000, len(periods))
    })
    
    # Customer Data
    customer_data = pd.DataFrame({
        'customer_id': [f'CUST{i:03d}' for i in range(1, 51)],
        'customer_name': [f'Customer {i}' for i in range(1, 51)],
        'revenue': np.random.uniform(50000, 500000, 50),
        'profit_margin': np.random.uniform(10, 40, 50),
        'profitability': np.random.uniform(5000, 200000, 50),  # Add profitability column
        'costs_to_serve': np.random.uniform(10000, 100000, 50),  # Add costs to serve
        'segment': np.random.choice(['Enterprise', 'Mid-Market', 'SMB'], 50),
        'region': np.random.choice(['North America', 'Europe', 'Asia', 'Latin America'], 50),
        'lifetime_value': np.random.uniform(100000, 2000000, 50)
    })
    
    # Product Data
    product_data = pd.DataFrame({
        'product_id': [f'PROD{i:03d}' for i in range(1, 31)],
        'product_name': [f'Product {i}' for i in range(1, 31)],
        'revenue': np.random.uniform(100000, 1000000, 30),
        'cost': np.random.uniform(50000, 500000, 30),
        'total_costs': np.random.uniform(60000, 600000, 30),  # Add total_costs column
        'direct_costs': np.random.uniform(40000, 400000, 30),  # Add direct_costs column
        'allocated_costs': np.random.uniform(20000, 200000, 30),  # Add allocated_costs column
        'margin': np.random.uniform(20, 60, 30),
        'category': np.random.choice(['Software', 'Hardware', 'Services', 'Consulting'], 30),
        'lifecycle_stage': np.random.choice(['Introduction', 'Growth', 'Maturity', 'Decline'], 30)
    })
    
    # Value Chain Data
    value_chain = pd.DataFrame({
        'function': ['R&D', 'Design', 'Manufacturing', 'Marketing', 'Sales', 'Distribution', 'Customer Service'],
        'cost': np.random.uniform(100000, 800000, 7),
        'percentage': np.random.uniform(5, 25, 7),
        'period': np.random.choice(periods, 7)
    })
    
    return {
        'income_statement': income_statement,
        'balance_sheet': balance_sheet,
        'cash_flow': cash_flow,
        'budget': budget,
        'forecast': forecast,
        'market_data': market_data,
        'customer_data': customer_data,
        'product_data': product_data,
        'value_chain': value_chain
    }

def show_data_input():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">📝 Data Management</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Upload your finance data files to unlock powerful analytics and insights. 
            Support for Excel (.xlsx) and CSV formats with automatic data validation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 Upload Data Files")
    
    # Create tabs for different upload methods
    upload_tab1, upload_tab2, upload_tab3, upload_tab4 = st.tabs(["📤 Upload Files", "📥 Download Template", "✏️ Manual Data Entry", "🎯 Load Sample Data"])
    
    with upload_tab1:
        # Complete Dataset Upload Section
        st.markdown("### 📊 Complete Dataset")
        
        uploaded_complete_dataset = st.file_uploader(
            "📊 Upload Complete Dataset (Excel file with multiple sheets)", 
            type=['xlsx'], 
            key="complete_dataset_upload",
            help="Upload an Excel file with sheets named: Income_Statement, Balance_Sheet, Cash_Flow, Budget, Forecast, Market_Data, Customer_Data, Product_Data, Value_Chain"
        )
        
        if uploaded_complete_dataset is not None:
            try:
                # Read all sheets from the Excel file
                excel_file = pd.ExcelFile(uploaded_complete_dataset)
                
                # Dictionary to store loaded data
                loaded_data = {}
                
                # Expected sheet names
                expected_sheets = {
                    'income_statement': 'income_statement',
                    'balance_sheet': 'balance_sheet', 
                    'cash_flow': 'cash_flow',
                    'budget': 'budget',
                    'forecast': 'forecast',
                    'market_data': 'market_data',
                    'customer_data': 'customer_data',
                    'product_data': 'product_data',
                    'value_chain': 'value_chain'
                }
                
                # Load each sheet if it exists
                for sheet_name, session_key in expected_sheets.items():
                    if sheet_name in excel_file.sheet_names:
                        loaded_data[session_key] = pd.read_excel(uploaded_complete_dataset, sheet_name=sheet_name)
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                            ✅ {sheet_name} loaded: {len(loaded_data[session_key])} records
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                            ⚠️ Sheet '{sheet_name}' not found in the uploaded file
                        </div>
                        """, unsafe_allow_html=True)
                
                # Update session state with loaded data
                for session_key, data in loaded_data.items():
                    setattr(st.session_state, session_key, data)
                
                # Show summary
                total_records = sum(len(data) for data in loaded_data.values())
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 10px; margin: 15px 0;">
                    <h4 style="margin: 0 0 10px 0;">🎉 Complete Dataset Loaded Successfully!</h4>
                    <p style="margin: 0;">Total records loaded: <strong>{total_records:,}</strong> across <strong>{len(loaded_data)}</strong> data tables</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading complete dataset: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        # Separator
        st.markdown("---")
        
        # Individual File Upload Section
        st.markdown("### 📁 Individual Files")
        
        # File uploaders in a modern grid layout
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_income_statement = st.file_uploader("📈 Income Statement", type=['xlsx', 'csv'], key="income_statement_upload")
            uploaded_balance_sheet = st.file_uploader("💰 Balance Sheet", type=['xlsx', 'csv'], key="balance_sheet_upload")
            uploaded_cash_flow = st.file_uploader("💸 Cash Flow", type=['xlsx', 'csv'], key="cash_flow_upload")
            uploaded_budget = st.file_uploader("📋 Budget", type=['xlsx', 'csv'], key="budget_upload")
        
        with col2:
            uploaded_forecast = st.file_uploader("🔮 Forecast", type=['xlsx', 'csv'], key="forecast_upload")
            uploaded_market_data = st.file_uploader("📊 Market Data", type=['xlsx', 'csv'], key="market_data_upload")
            uploaded_customer_data = st.file_uploader("👥 Customer Data", type=['xlsx', 'csv'], key="customer_data_upload")
            uploaded_product_data = st.file_uploader("📦 Product Data", type=['xlsx', 'csv'], key="product_data_upload")
        
        # Process uploaded files with modern success/error styling
        if uploaded_income_statement is not None:
            try:
                if uploaded_income_statement.name.endswith('.csv'):
                    st.session_state.income_statement = pd.read_csv(uploaded_income_statement)
                else:
                    st.session_state.income_statement = pd.read_excel(uploaded_income_statement)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Income statement data loaded: {len(st.session_state.income_statement)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading income statement data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_balance_sheet is not None:
            try:
                if uploaded_balance_sheet.name.endswith('.csv'):
                    st.session_state.balance_sheet = pd.read_csv(uploaded_balance_sheet)
                else:
                    st.session_state.balance_sheet = pd.read_excel(uploaded_balance_sheet)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Balance sheet data loaded: {len(st.session_state.balance_sheet)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading balance sheet data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_cash_flow is not None:
            try:
                if uploaded_cash_flow.name.endswith('.csv'):
                    st.session_state.cash_flow = pd.read_csv(uploaded_cash_flow)
                else:
                    st.session_state.cash_flow = pd.read_excel(uploaded_cash_flow)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Cash flow data loaded: {len(st.session_state.cash_flow)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading cash flow data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_budget is not None:
            try:
                if uploaded_budget.name.endswith('.csv'):
                    st.session_state.budget = pd.read_csv(uploaded_budget)
                else:
                    st.session_state.budget = pd.read_excel(uploaded_budget)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Budget data loaded: {len(st.session_state.budget)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading budget data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_forecast is not None:
            try:
                if uploaded_forecast.name.endswith('.csv'):
                    st.session_state.forecast = pd.read_csv(uploaded_forecast)
                else:
                    st.session_state.forecast = pd.read_excel(uploaded_forecast)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Forecast data loaded: {len(st.session_state.forecast)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading forecast data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_market_data is not None:
            try:
                if uploaded_market_data.name.endswith('.csv'):
                    st.session_state.market_data = pd.read_csv(uploaded_market_data)
                else:
                    st.session_state.market_data = pd.read_excel(uploaded_market_data)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Market data loaded: {len(st.session_state.market_data)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading market data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_customer_data is not None:
            try:
                if uploaded_customer_data.name.endswith('.csv'):
                    st.session_state.customer_data = pd.read_csv(uploaded_customer_data)
                else:
                    st.session_state.customer_data = pd.read_excel(uploaded_customer_data)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Customer data loaded: {len(st.session_state.customer_data)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading customer data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_product_data is not None:
            try:
                if uploaded_product_data.name.endswith('.csv'):
                    st.session_state.product_data = pd.read_csv(uploaded_product_data)
                else:
                    st.session_state.product_data = pd.read_excel(uploaded_product_data)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Product data loaded: {len(st.session_state.product_data)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading product data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    with upload_tab2:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">📥 Download Excel Template</h4>
            <p style="color: #34495e; margin-bottom: 20px;">Download our comprehensive Excel template with all required data fields, formatting, and detailed instructions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create template for download
        template_output = create_template_for_download()
        
        st.download_button(
            label="📥 Download Template",
            data=template_output.getvalue(),
            file_name="finance_analytics_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">Template includes:</h5>
            <ul style="color: #34495e; line-height: 1.6;">
                <li>📈 <strong>Income Statement:</strong> Revenue, expenses, and profitability data</li>
                <li>💰 <strong>Balance Sheet:</strong> Assets, liabilities, and equity data</li>
                <li>💸 <strong>Cash Flow:</strong> Operating, investing, and financing cash flows</li>
                <li>📋 <strong>Budget:</strong> Budgeted revenue, expenses, and targets</li>
                <li>🔮 <strong>Forecast:</strong> Forecasted financial performance</li>
                <li>📊 <strong>Market Data:</strong> Market prices, volumes, and trends</li>
                <li>👥 <strong>Customer Data:</strong> Customer revenue and profitability</li>
                <li>📦 <strong>Product Data:</strong> Product revenue and costs</li>
                <li>🏗️ <strong>Value Chain:</strong> Value chain functions and costs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with upload_tab3:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">✏️ Manual Data Entry</h4>
            <p style="color: #34495e; margin-bottom: 20px;">Add data manually using the forms below. This is useful for small datasets or quick data entry.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for different data types
        manual_tab1, manual_tab2, manual_tab3, manual_tab4, manual_tab5, manual_tab6, manual_tab7, manual_tab8, manual_tab9 = st.tabs([
            "Income Statement", "Balance Sheet", "Cash Flow", "Budget", 
            "Forecast", "Market Data", "Customer Data", "Product Data", "Value Chain"
        ])
        
        with manual_tab1:
            st.subheader("Income Statement")
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.text_input("Period", key="period_income")
                revenue = st.number_input("Revenue", min_value=0.0, key="revenue_input")
                cost_of_goods_sold = st.number_input("Cost of Goods Sold", min_value=0.0, key="cogs_input")
                gross_profit = st.number_input("Gross Profit", min_value=0.0, key="gross_profit_input")
                operating_expenses = st.number_input("Operating Expenses", min_value=0.0, key="opex_input")
            
            with col2:
                operating_income = st.number_input("Operating Income", min_value=0.0, key="op_income_input")
                net_income = st.number_input("Net Income", min_value=0.0, key="net_income_input")
                ebitda = st.number_input("EBITDA", min_value=0.0, key="ebitda_input")
                ebit = st.number_input("EBIT", min_value=0.0, key="ebit_input")
            
            if st.button("Add Income Statement"):
                new_income = pd.DataFrame([{
                    'period': period,
                    'revenue': revenue,
                    'cost_of_goods_sold': cost_of_goods_sold,
                    'gross_profit': gross_profit,
                    'operating_expenses': operating_expenses,
                    'operating_income': operating_income,
                    'net_income': net_income,
                    'ebitda': ebitda,
                    'ebit': ebit
                }])
                st.session_state.income_statement = pd.concat([st.session_state.income_statement, new_income], ignore_index=True)
                st.success("Income Statement added successfully!")
            
            # Display existing data
            if not st.session_state.income_statement.empty:
                st.subheader("Existing Income Statements")
                display_dataframe_with_index_1(st.session_state.income_statement)
        
        with manual_tab2:
            st.subheader("Balance Sheet")
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.text_input("Period", key="period_balance")
                total_assets = st.number_input("Total Assets", min_value=0.0, key="total_assets_input")
                current_assets = st.number_input("Current Assets", min_value=0.0, key="current_assets_input")
                cash_and_equivalents = st.number_input("Cash & Equivalents", min_value=0.0, key="cash_input")
                accounts_receivable = st.number_input("Accounts Receivable", min_value=0.0, key="ar_input")
            
            with col2:
                total_liabilities = st.number_input("Total Liabilities", min_value=0.0, key="total_liabilities_input")
                current_liabilities = st.number_input("Current Liabilities", min_value=0.0, key="current_liabilities_input")
                total_equity = st.number_input("Total Equity", min_value=0.0, key="total_equity_input")
                working_capital = st.number_input("Working Capital", min_value=0.0, key="working_capital_input")
            
            if st.button("Add Balance Sheet"):
                new_balance = pd.DataFrame([{
                    'period': period,
                    'total_assets': total_assets,
                    'current_assets': current_assets,
                    'cash_and_equivalents': cash_and_equivalents,
                    'accounts_receivable': accounts_receivable,
                    'total_liabilities': total_liabilities,
                    'current_liabilities': current_liabilities,
                    'total_equity': total_equity,
                    'working_capital': working_capital
                }])
                st.session_state.balance_sheet = pd.concat([st.session_state.balance_sheet, new_balance], ignore_index=True)
                st.success("Balance Sheet added successfully!")
            
            # Display existing data
            if not st.session_state.balance_sheet.empty:
                st.subheader("Existing Balance Sheets")
                display_dataframe_with_index_1(st.session_state.balance_sheet)
        
        with manual_tab3:
            st.subheader("Cash Flow")
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.text_input("Period", key="period_cash")
                operating_cash_flow = st.number_input("Operating Cash Flow", min_value=0.0, key="ocf_input")
                investing_cash_flow = st.number_input("Investing Cash Flow", min_value=0.0, key="icf_input")
                financing_cash_flow = st.number_input("Financing Cash Flow", min_value=0.0, key="fcf_input")
            
            with col2:
                net_cash_flow = st.number_input("Net Cash Flow", min_value=0.0, key="net_cf_input")
                free_cash_flow = st.number_input("Free Cash Flow", min_value=0.0, key="fcf_input2")
                capex = st.number_input("Capital Expenditure", min_value=0.0, key="capex_input")
            
            if st.button("Add Cash Flow"):
                new_cash_flow = pd.DataFrame([{
                    'period': period,
                    'operating_cash_flow': operating_cash_flow,
                    'investing_cash_flow': investing_cash_flow,
                    'financing_cash_flow': financing_cash_flow,
                    'net_cash_flow': net_cash_flow,
                    'free_cash_flow': free_cash_flow,
                    'capex': capex
                }])
                st.session_state.cash_flow = pd.concat([st.session_state.cash_flow, new_cash_flow], ignore_index=True)
                st.success("Cash Flow added successfully!")
            
            # Display existing data
            if not st.session_state.cash_flow.empty:
                st.subheader("Existing Cash Flows")
                display_dataframe_with_index_1(st.session_state.cash_flow)
        
        with manual_tab4:
            st.subheader("Budget")
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.text_input("Period", key="period_budget")
                budgeted_revenue = st.number_input("Budgeted Revenue", min_value=0.0, key="budget_revenue_input")
                budgeted_expenses = st.number_input("Budgeted Expenses", min_value=0.0, key="budget_expenses_input")
                budgeted_profit = st.number_input("Budgeted Profit", min_value=0.0, key="budget_profit_input")
            
            with col2:
                department = st.text_input("Department", key="department_budget_input")
                category = st.text_input("Category", key="category_budget_input")
                variance = st.number_input("Variance", key="variance_input")
            
            if st.button("Add Budget"):
                new_budget = pd.DataFrame([{
                    'period': period,
                    'budgeted_revenue': budgeted_revenue,
                    'budgeted_expenses': budgeted_expenses,
                    'budgeted_profit': budgeted_profit,
                    'department': department,
                    'category': category,
                    'variance': variance
                }])
                st.session_state.budget = pd.concat([st.session_state.budget, new_budget], ignore_index=True)
                st.success("Budget added successfully!")
            
            # Display existing data
            if not st.session_state.budget.empty:
                st.subheader("Existing Budgets")
                display_dataframe_with_index_1(st.session_state.budget)
        
        with manual_tab5:
            st.subheader("Forecast")
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.text_input("Period", key="period_forecast")
                forecasted_revenue = st.number_input("Forecasted Revenue", min_value=0.0, key="forecast_revenue_input")
                forecasted_expenses = st.number_input("Forecasted Expenses", min_value=0.0, key="forecast_expenses_input")
                forecasted_profit = st.number_input("Forecasted Profit", min_value=0.0, key="forecast_profit_input")
            
            with col2:
                confidence_level = st.selectbox("Confidence Level", ["High", "Medium", "Low"], key="confidence_input")
                scenario = st.selectbox("Scenario", ["Base", "Optimistic", "Pessimistic"], key="scenario_input")
            
            if st.button("Add Forecast"):
                new_forecast = pd.DataFrame([{
                    'period': period,
                    'forecasted_revenue': forecasted_revenue,
                    'forecasted_expenses': forecasted_expenses,
                    'forecasted_profit': forecasted_profit,
                    'confidence_level': confidence_level,
                    'scenario': scenario
                }])
                st.session_state.forecast = pd.concat([st.session_state.forecast, new_forecast], ignore_index=True)
                st.success("Forecast added successfully!")
            
            # Display existing data
            if not st.session_state.forecast.empty:
                st.subheader("Existing Forecasts")
                display_dataframe_with_index_1(st.session_state.forecast)
        
        with manual_tab6:
            st.subheader("Market Data")
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", key="date_market_input")
                market_price = st.number_input("Market Price", min_value=0.0, key="market_price_input")
                volume = st.number_input("Volume", min_value=0, key="volume_input")
                market_cap = st.number_input("Market Cap", min_value=0.0, key="market_cap_input")
            
            with col2:
                pe_ratio = st.number_input("P/E Ratio", min_value=0.0, key="pe_ratio_input")
                beta = st.number_input("Beta", min_value=0.0, key="beta_input")
                sector = st.text_input("Sector", key="sector_input")
            
            if st.button("Add Market Data"):
                new_market = pd.DataFrame([{
                    'date': date,
                    'market_price': market_price,
                    'volume': volume,
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'beta': beta,
                    'sector': sector
                }])
                st.session_state.market_data = pd.concat([st.session_state.market_data, new_market], ignore_index=True)
                st.success("Market Data added successfully!")
            
            # Display existing data
            if not st.session_state.market_data.empty:
                st.subheader("Existing Market Data")
                display_dataframe_with_index_1(st.session_state.market_data)
        
        with manual_tab7:
            st.subheader("Customer Data")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                customer_id = st.text_input("Customer ID", key="customer_id_input")
                customer_name = st.text_input("Customer Name", key="customer_name_input")
                revenue = st.number_input("Revenue", min_value=0.0, key="customer_revenue_input")
                profit_margin = st.number_input("Profit Margin %", min_value=0.0, max_value=100.0, key="profit_margin_input")
            
            with col2:
                profitability = st.number_input("Profitability", min_value=0.0, key="profitability_input")
                costs_to_serve = st.number_input("Costs to Serve", min_value=0.0, key="costs_to_serve_input")
                segment = st.selectbox("Segment", ["Enterprise", "Mid-Market", "SMB"], key="segment_input")
                region = st.selectbox("Region", ["North America", "Europe", "Asia", "Latin America"], key="region_input")
            
            with col3:
                lifetime_value = st.number_input("Lifetime Value", min_value=0.0, key="ltv_input")
            
            if st.button("Add Customer Data"):
                new_customer = pd.DataFrame([{
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'revenue': revenue,
                    'profit_margin': profit_margin,
                    'profitability': profitability,
                    'costs_to_serve': costs_to_serve,
                    'segment': segment,
                    'region': region,
                    'lifetime_value': lifetime_value
                }])
                st.session_state.customer_data = pd.concat([st.session_state.customer_data, new_customer], ignore_index=True)
                st.success("Customer Data added successfully!")
            
            # Display existing data
            if not st.session_state.customer_data.empty:
                st.subheader("Existing Customer Data")
                display_dataframe_with_index_1(st.session_state.customer_data)
        
        with manual_tab8:
            st.subheader("Product Data")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                product_id = st.text_input("Product ID", key="product_id_input")
                product_name = st.text_input("Product Name", key="product_name_input")
                revenue = st.number_input("Revenue", min_value=0.0, key="product_revenue_input")
                cost = st.number_input("Cost", min_value=0.0, key="product_cost_input")
            
            with col2:
                total_costs = st.number_input("Total Costs", min_value=0.0, key="total_costs_input")
                direct_costs = st.number_input("Direct Costs", min_value=0.0, key="direct_costs_input")
                allocated_costs = st.number_input("Allocated Costs", min_value=0.0, key="allocated_costs_input")
                margin = st.number_input("Margin", min_value=0.0, key="product_margin_input")
            
            with col3:
                category = st.selectbox("Category", ["Software", "Hardware", "Services", "Consulting"], key="product_category_input")
                lifecycle_stage = st.selectbox("Lifecycle Stage", ["Introduction", "Growth", "Maturity", "Decline"], key="lifecycle_input")
            
            if st.button("Add Product Data"):
                new_product = pd.DataFrame([{
                    'product_id': product_id,
                    'product_name': product_name,
                    'revenue': revenue,
                    'cost': cost,
                    'total_costs': total_costs,
                    'direct_costs': direct_costs,
                    'allocated_costs': allocated_costs,
                    'margin': margin,
                    'category': category,
                    'lifecycle_stage': lifecycle_stage
                }])
                st.session_state.product_data = pd.concat([st.session_state.product_data, new_product], ignore_index=True)
                st.success("Product Data added successfully!")
            
            # Display existing data
            if not st.session_state.product_data.empty:
                st.subheader("Existing Product Data")
                display_dataframe_with_index_1(st.session_state.product_data)
        
        with manual_tab9:
            st.subheader("Value Chain")
            col1, col2 = st.columns(2)
            
            with col1:
                function = st.text_input("Function", key="function_input")
                cost = st.number_input("Cost", min_value=0.0, key="vc_cost_input")
                efficiency_score = st.number_input("Efficiency Score", min_value=0.0, max_value=100.0, key="efficiency_input")
            
            with col2:
                value_added = st.number_input("Value Added", min_value=0.0, key="value_added_input")
                process_time = st.number_input("Process Time (days)", min_value=0, key="process_time_input")
            
            if st.button("Add Value Chain Data"):
                new_vc = pd.DataFrame([{
                    'function': function,
                    'cost': cost,
                    'efficiency_score': efficiency_score,
                    'value_added': value_added,
                    'process_time': process_time
                }])
                st.session_state.value_chain = pd.concat([st.session_state.value_chain, new_vc], ignore_index=True)
                st.success("Value Chain Data added successfully!")
            
            # Display existing data
            if not st.session_state.value_chain.empty:
                st.subheader("Existing Value Chain Data")
                display_dataframe_with_index_1(st.session_state.value_chain)
    
    with upload_tab4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; margin: 20px 0; color: white;">
            <h3 style="color: white; margin: 0 0 15px 0;">🎯 Sample Data for Testing</h3>
            <p style="margin: 0; opacity: 0.9;">
                Load comprehensive sample data to test all analytics features. This includes 100+ records across all data types.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data loading section
        st.markdown("### 📊 Load Sample Dataset")
        
        if st.button("🚀 Load Sample Data", type="primary", use_container_width=True):
            try:
                # Generate sample finance data
                sample_data = generate_sample_finance_data()
                
                # Update session state
                st.session_state.income_statement = sample_data['income_statement']
                st.session_state.balance_sheet = sample_data['balance_sheet']
                st.session_state.cash_flow = sample_data['cash_flow']
                st.session_state.budget = sample_data['budget']
                st.session_state.forecast = sample_data['forecast']
                st.session_state.market_data = sample_data['market_data']
                st.session_state.customer_data = sample_data['customer_data']
                st.session_state.product_data = sample_data['product_data']
                st.session_state.value_chain = sample_data['value_chain']
                
                # Show success message
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                            padding: 20px; border-radius: 12px; margin: 20px 0; color: white;">
                    <h4 style="color: white; margin: 0 0 10px 0;">✅ Sample Data Loaded Successfully!</h4>
                    <p style="margin: 0; opacity: 0.9;">
                        📈 Income Statements: {len(sample_data['income_statement'])} records<br>
                        💰 Balance Sheets: {len(sample_data['balance_sheet'])} records<br>
                        💸 Cash Flows: {len(sample_data['cash_flow'])} records<br>
                        📋 Budgets: {len(sample_data['budget'])} records<br>
                        🔮 Forecasts: {len(sample_data['forecast'])} records<br>
                        📊 Market Data: {len(sample_data['market_data'])} records<br>
                        👥 Customers: {len(sample_data['customer_data'])} records<br>
                        📦 Products: {len(sample_data['product_data'])} records<br>
                        🏗️ Value Chain: {len(sample_data['value_chain'])} records
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.success("🎉 You can now explore all analytics features with the sample data!")
                
            except Exception as e:
                st.error(f"❌ Error loading sample data: {str(e)}")
                st.info("💡 Sample data generation function will be created.")
        
        # Data preview section
        st.markdown("### 👀 Sample Data Preview")
        
        if not st.session_state.income_statement.empty:
            st.markdown("**📈 Income Statement Preview:**")
            st.dataframe(st.session_state.income_statement.head(), use_container_width=True)
        else:
            st.info("💡 Click 'Load Sample Data' to see a preview of the sample data.")
    
    # Data summary section with modern cards
    st.markdown("### 📊 Data Summary")
    
    # Create summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Income Statements</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.income_statement):,}</h2>
                </div>
                <div style="font-size: 2rem;">📈</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-purple">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Balance Sheets</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.balance_sheet):,}</h2>
                </div>
                <div style="font-size: 2rem;">💰</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-orange">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Cash Flows</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.cash_flow):,}</h2>
                </div>
                <div style="font-size: 2rem;">💸</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-teal">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Customers</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.customer_data):,}</h2>
                </div>
                <div style="font-size: 2rem;">👥</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Export data section
    st.markdown("### 📤 Export Data")
    
    if (not st.session_state.income_statement.empty or not st.session_state.balance_sheet.empty or 
        not st.session_state.cash_flow.empty or not st.session_state.budget.empty or 
        not st.session_state.forecast.empty or not st.session_state.market_data.empty or 
        not st.session_state.customer_data.empty or not st.session_state.product_data.empty or 
        not st.session_state.value_chain.empty):
        
        export_output = export_data_to_excel()
        
        st.download_button(
            label="📤 Export All Data",
            data=export_output.getvalue(),
            file_name=f"finance_analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("""
        <div class="chart-container">
            <p style="color: #34495e; margin: 0;"><strong>Export includes:</strong> All loaded datasets with summary sheet and data quality metrics</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chart-container">
            <p style="color: #f97316; margin: 0;">📝 No data to export. Please upload data files first.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data tables section
    st.markdown("### 📋 Data Tables")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">📈 Income Statement</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.income_statement.empty:
            display_dataframe_with_index_1(st.session_state.income_statement, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No income statement data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">💰 Balance Sheet</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.balance_sheet.empty:
            display_dataframe_with_index_1(st.session_state.balance_sheet, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No balance sheet data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">💸 Cash Flow</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.cash_flow.empty:
            display_dataframe_with_index_1(st.session_state.cash_flow, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No cash flow data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">👥 Customers</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.customer_data.empty:
            display_dataframe_with_index_1(st.session_state.customer_data, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No customer data available</p>
            </div>
            """, unsafe_allow_html=True)

def show_auto_insights():
    """Display auto insights dashboard"""
    st.markdown("""
    <div class="section-header">
        <h3>💡 Auto Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if FinanceInsights is None:
        st.error("Auto insights module not available. Please check the installation.")
        return
    
    # Check if data is available
    if (st.session_state.income_statement.empty and st.session_state.balance_sheet.empty and 
        st.session_state.cash_flow.empty and st.session_state.budget.empty and 
        st.session_state.forecast.empty and st.session_state.customer_data.empty and 
        st.session_state.product_data.empty):
        st.warning("⚠️ No data available for insights. Please load data in the Data Input section first.")
        return
    
    # Initialize insights
    insights = FinanceInsights(
        st.session_state.income_statement,
        st.session_state.balance_sheet,
        st.session_state.cash_flow,
        st.session_state.budget,
        st.session_state.forecast,
        st.session_state.market_data,
        st.session_state.customer_data,
        st.session_state.product_data,
        st.session_state.value_chain
    )
    
    # Create tabs for different insight types
    insight_tab1, insight_tab2, insight_tab3, insight_tab4, insight_tab5, insight_tab6 = st.tabs([
        "📊 Financial Performance", "💰 Liquidity & Solvency", "💸 Cash Flow", 
        "📋 Budget & Forecasting", "👥 Customer & Product", "🎯 Executive Summary"
    ])
    
    with insight_tab1:
        st.markdown("### 📊 Financial Performance Insights")
        performance_insights = insights.generate_profitability_insights()
        display_insights_section(performance_insights, "Financial Performance Insights", "📊")
        
        # Add AI recommendations for financial performance
        if generate_financial_performance_ai_recommendations:
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            try:
                ai_recommendations = generate_financial_performance_ai_recommendations(
                    st.session_state.income_statement,
                    st.session_state.balance_sheet,
                    st.session_state.cash_flow
                )
                display_formatted_recommendations(ai_recommendations)
            except Exception as e:
                st.error(f"Error generating AI recommendations: {e}")
                st.info("Please check if you have loaded financial data in the Data Input section.")
        else:
            st.error("AI recommendations function not available. Please check the import.")
    
    with insight_tab2:
        st.markdown("### 💰 Liquidity & Solvency Insights")
        liquidity_insights = insights.generate_liquidity_solvency_insights()
        display_insights_section(liquidity_insights, "Liquidity & Solvency Insights", "💰")
    
    with insight_tab3:
        st.markdown("### 💸 Cash Flow Insights")
        cash_flow_insights = insights.generate_cash_flow_insights()
        display_insights_section(cash_flow_insights, "Cash Flow Insights", "💸")
    
    with insight_tab4:
        st.markdown("### 📋 Budget & Forecasting Insights")
        budget_insights = insights.generate_budget_forecasting_insights()
        display_insights_section(budget_insights, "Budget & Forecasting Insights", "📋")
    
    with insight_tab5:
        st.markdown("### 👥 Customer & Product Insights")
        customer_insights = insights.generate_customer_productivity_insights()
        display_insights_section(customer_insights, "Customer & Product Insights", "👥")
    
    with insight_tab6:
        st.markdown("### 🎯 Executive Summary")
        executive_summary = insights.generate_executive_summary()
        display_executive_summary(executive_summary, "Executive Financial Summary", "🎯")

def show_predictive_analytics():
    """Display predictive analytics dashboard"""
    st.markdown("""
    <div class="section-header">
        <h3>🔮 Predictive Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if display_finance_predictive_analytics_dashboard is None:
        st.error("Predictive analytics module not available. Please check the installation.")
        return
    
    # Check if data is available
    if (st.session_state.income_statement.empty and st.session_state.balance_sheet.empty and 
        st.session_state.cash_flow.empty and st.session_state.budget.empty and 
        st.session_state.forecast.empty and st.session_state.customer_data.empty and 
        st.session_state.product_data.empty):
        st.warning("⚠️ No data available for predictive analytics. Please load data in the Data Input section first.")
        return
    
    # Display predictive analytics dashboard
    display_finance_predictive_analytics_dashboard(
        st.session_state.income_statement,
        st.session_state.balance_sheet,
        st.session_state.cash_flow,
        st.session_state.budget,
        st.session_state.forecast,
        st.session_state.market_data,
        st.session_state.customer_data,
        st.session_state.product_data,
        st.session_state.value_chain
    )

# Analytics functions for the main sections
def show_financial_performance():
    st.markdown("""
    <div class="section-header">
        <h3>📊 Financial Performance Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.income_statement.empty and st.session_state.balance_sheet.empty:
        st.info("📊 Please upload income statement and balance sheet data to view financial performance analytics.")
        return
    
    # Calculate financial performance metrics
    performance_summary, performance_message = calculate_financial_performance_metrics(
        st.session_state.income_statement, st.session_state.balance_sheet
    )
    
    # Display summary metrics
    st.subheader("📈 Financial Performance Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if not performance_summary.empty:
            revenue_growth = performance_summary.iloc[0]['Value']
            st.metric("Revenue Growth Rate", revenue_growth)
    
    with col2:
        if not performance_summary.empty and len(performance_summary) > 1:
            gross_margin = performance_summary.iloc[1]['Value']
            st.metric("Gross Margin", gross_margin)
    
    with col3:
        if not performance_summary.empty and len(performance_summary) > 2:
            operating_margin = performance_summary.iloc[2]['Value']
            st.metric("Operating Margin", operating_margin)
    
    with col4:
        if not performance_summary.empty and len(performance_summary) > 3:
            net_margin = performance_summary.iloc[3]['Value']
            st.metric("Net Margin", net_margin)
    
    with col5:
        if not performance_summary.empty and len(performance_summary) > 4:
            eps = performance_summary.iloc[4]['Value']
            st.metric("EPS", eps)
    
    st.info(performance_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Revenue Analysis", "💰 Margin Analysis", "📊 Profitability Trends", "📋 Performance Insights"
    ])
    
    with tab1:
        st.subheader("📈 Revenue Analysis")
        
        if not st.session_state.income_statement.empty:
            # Revenue trend analysis
            revenue_trend = st.session_state.income_statement.groupby('period').agg({
                'revenue': 'sum'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Scatter(x=revenue_trend['period'], y=revenue_trend['revenue'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Revenue')
            ])
            fig.update_layout(
                title="Revenue Trend Over Time",
                xaxis_title="Period",
                yaxis_title="Revenue ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_1")
            
            # Add AI recommendations for Revenue Analysis
            if generate_financial_performance_ai_recommendations:
                st.markdown("---")
                try:
                    ai_recommendations = generate_financial_performance_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
            

    
    with tab2:
        st.subheader("💰 Margin Analysis")
        
        if not st.session_state.income_statement.empty:
            # Margin analysis
            margin_analysis = st.session_state.income_statement.copy()
            margin_analysis['gross_margin_pct'] = ((margin_analysis['revenue'] - margin_analysis['cost_of_goods_sold']) / margin_analysis['revenue'] * 100).round(1)
            margin_analysis['operating_margin_pct'] = (margin_analysis['operating_income'] / margin_analysis['revenue'] * 100).round(1)
            margin_analysis['net_margin_pct'] = (margin_analysis['net_income'] / margin_analysis['revenue'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=margin_analysis['period'], y=margin_analysis['gross_margin_pct'],
                           marker_color='#2ca02c', name='Gross Margin',
                           text=margin_analysis['gross_margin_pct'],
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Gross Margin by Period",
                    xaxis_title="Period",
                    yaxis_title="Gross Margin (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_2")
            
            with col2:
                fig = go.Figure(data=[
                    go.Bar(x=margin_analysis['period'], y=margin_analysis['net_margin_pct'],
                           marker_color='#ff7f0e', name='Net Margin',
                           text=margin_analysis['net_margin_pct'],
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Net Margin by Period",
                    xaxis_title="Period",
                    yaxis_title="Net Margin (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_3")
            
            # Add AI recommendations for Margin Analysis
            if generate_financial_performance_ai_recommendations:
                st.markdown("---")
                try:
                    ai_recommendations = generate_financial_performance_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
            

    
    with tab3:
        st.subheader("📊 Profitability Trends")
        
        if not st.session_state.income_statement.empty:
            # Profitability trends
            profitability_trends = st.session_state.income_statement.groupby('period').agg({
                'revenue': 'sum',
                'net_income': 'sum'
            }).reset_index()
            profitability_trends['profitability_ratio'] = (profitability_trends['net_income'] / profitability_trends['revenue'] * 100).round(1)
            
            fig = go.Figure(data=[
                go.Scatter(x=profitability_trends['period'], y=profitability_trends['profitability_ratio'],
                          mode='lines+markers', line=dict(color='#9467bd', width=3),
                          marker=dict(size=8), name='Profitability Ratio')
            ])
            fig.update_layout(
                title="Profitability Ratio Trend",
                xaxis_title="Period",
                yaxis_title="Profitability Ratio (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_4")
            
            # Add AI recommendations for Profitability Trends
            if generate_financial_performance_ai_recommendations:
                st.markdown("---")
                try:
                    ai_recommendations = generate_financial_performance_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
            

    
    with tab4:
        st.subheader("📋 Performance Insights")
        
        if not st.session_state.income_statement.empty:
            # Performance insights
            st.write("**Financial Performance Summary:**")
            
            total_revenue = st.session_state.income_statement['revenue'].sum()
            total_net_income = st.session_state.income_statement['net_income'].sum()
            avg_gross_margin = ((total_revenue - st.session_state.income_statement['cost_of_goods_sold'].sum()) / total_revenue * 100) if total_revenue > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${total_revenue:,.0f}")
            with col2:
                st.metric("Total Net Income", f"${total_net_income:,.0f}")
            with col3:
                st.metric("Avg Gross Margin", f"{avg_gross_margin:.1f}%")
            
            # Performance recommendations
            st.write("**Key Performance Indicators:**")
            if avg_gross_margin > 50:
                st.success(f"✅ Strong gross margin: {avg_gross_margin:.1f}%")
            elif avg_gross_margin > 30:
                st.info(f"ℹ️ Moderate gross margin: {avg_gross_margin:.1f}%")
            else:
                st.warning(f"⚠️ Low gross margin: {avg_gross_margin:.1f}% - consider cost optimization")
            
            net_margin = (total_net_income / total_revenue * 100) if total_revenue > 0 else 0
            if net_margin > 15:
                st.success(f"✅ Excellent net margin: {net_margin:.1f}%")
            elif net_margin > 10:
                st.info(f"ℹ️ Good net margin: {net_margin:.1f}%")
            else:
                st.warning(f"⚠️ Low net margin: {net_margin:.1f}% - review cost structure")
            
            # Add AI recommendations for Performance Insights
            if generate_financial_performance_ai_recommendations:
                st.markdown("---")
                try:
                    ai_recommendations = generate_financial_performance_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")


# Placeholder functions for other sections
def show_liquidity_solvency():
    st.markdown("""
    <div class="section-header">
        <h3>💧 Liquidity and Solvency</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.balance_sheet.empty and st.session_state.cash_flow.empty:
        st.info("💧 Please upload balance sheet and cash flow data to view liquidity and solvency analytics.")
        return
    
    # Calculate liquidity and solvency metrics
    liquidity_summary, liquidity_message = calculate_liquidity_solvency_metrics(
        st.session_state.balance_sheet, st.session_state.cash_flow
    )
    
    # Display summary metrics
    st.subheader("💧 Liquidity and Solvency Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not liquidity_summary.empty:
            current_ratio = liquidity_summary.iloc[0]['Value']
            st.metric("Current Ratio", current_ratio)
    
    with col2:
        if not liquidity_summary.empty and len(liquidity_summary) > 1:
            quick_ratio = liquidity_summary.iloc[1]['Value']
            st.metric("Quick Ratio", quick_ratio)
    
    with col3:
        if not liquidity_summary.empty and len(liquidity_summary) > 2:
            ccc = liquidity_summary.iloc[2]['Value']
            st.metric("Cash Conversion Cycle", ccc)
    
    with col4:
        if not liquidity_summary.empty and len(liquidity_summary) > 3:
            dscr = liquidity_summary.iloc[3]['Value']
            st.metric("Debt Service Coverage", dscr)
    
    st.info(liquidity_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💧 Liquidity Analysis", "📊 Solvency Metrics", "💰 Cash Flow Analysis", "📋 Risk Assessment"
    ])
    
    with tab1:
        st.subheader("💧 Liquidity Analysis")
        
        if not st.session_state.balance_sheet.empty:
            # Current ratio trend
            current_ratio_trend = st.session_state.balance_sheet.copy()
            current_ratio_trend['current_ratio'] = (current_ratio_trend['current_assets'] / current_ratio_trend['current_liabilities']).round(2)
            
            fig = go.Figure(data=[
                go.Scatter(x=current_ratio_trend['period'], y=current_ratio_trend['current_ratio'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Current Ratio')
            ])
            fig.update_layout(
                title="Current Ratio Trend Over Time",
                xaxis_title="Period",
                yaxis_title="Current Ratio",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=2.0, line_dash="dash", line_color="green", annotation_text="Good (2.0)")
            fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Poor (1.0)")
            st.plotly_chart(fig, use_container_width=True, key="chart_5")
            
            # Quick ratio analysis
            quick_ratio_data = st.session_state.balance_sheet.copy()
            quick_ratio_data['quick_ratio'] = ((quick_ratio_data['cash_and_equivalents'] + quick_ratio_data['accounts_receivable']) / 
                                              quick_ratio_data['current_liabilities']).round(2)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=quick_ratio_data['period'], y=quick_ratio_data['quick_ratio'],
                           marker_color='#2ca02c', name='Quick Ratio',
                           text=quick_ratio_data['quick_ratio'],
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Quick Ratio by Period",
                    xaxis_title="Period",
                    yaxis_title="Quick Ratio",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_6")
            
            with col2:
                # Working capital analysis
                working_capital_data = st.session_state.balance_sheet.copy()
                working_capital_data['working_capital'] = working_capital_data['current_assets'] - working_capital_data['current_liabilities']
                
                fig = go.Figure(data=[
                    go.Scatter(x=working_capital_data['period'], y=working_capital_data['working_capital'],
                              mode='lines+markers', line=dict(color='#ff7f0e', width=3),
                              marker=dict(size=8), name='Working Capital')
                ])
                fig.update_layout(
                    title="Working Capital Trend",
                    xaxis_title="Period",
                    yaxis_title="Working Capital ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_7")
            
            # AI Strategic Recommendations for Liquidity Analysis
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            
            if generate_liquidity_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_liquidity_analysis_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("📊 Solvency Metrics")
        
        if not st.session_state.balance_sheet.empty:
            # Debt-to-equity ratio
            debt_equity_data = st.session_state.balance_sheet.copy()
            
            # Check if required columns exist
            required_cols = ['total_liabilities', 'shareholder_equity']
            if all(col in debt_equity_data.columns for col in required_cols):
                debt_equity_data['debt_to_equity'] = (debt_equity_data['total_liabilities'] / debt_equity_data['shareholder_equity']).round(2)
            else:
                st.warning("⚠️ Required columns for debt-to-equity calculation not found. Please ensure your balance sheet data includes 'total_liabilities' and 'shareholder_equity' columns.")
                return
            
            fig = go.Figure(data=[
                go.Scatter(x=debt_equity_data['period'], y=debt_equity_data['debt_to_equity'],
                          mode='lines+markers', line=dict(color='#9467bd', width=3),
                          marker=dict(size=8), name='Debt-to-Equity Ratio')
            ])
            fig.update_layout(
                title="Debt-to-Equity Ratio Trend",
                xaxis_title="Period",
                yaxis_title="Debt-to-Equity Ratio",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=0.5, line_dash="dash", line_color="green", annotation_text="Conservative (0.5)")
            fig.add_hline(y=1.0, line_dash="dash", line_color="orange", annotation_text="Moderate (1.0)")
            fig.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="High Risk (2.0)")
            st.plotly_chart(fig, use_container_width=True, key="chart_8")
            
            # Asset composition analysis
            latest_balance = st.session_state.balance_sheet.iloc[-1]
            
            # Check if required columns exist for asset composition
            asset_cols = ['cash_and_equivalents', 'accounts_receivable', 'inventory', 'current_assets', 'total_assets']
            if all(col in latest_balance.index for col in asset_cols):
                asset_composition = {
                    'Cash & Equivalents': latest_balance['cash_and_equivalents'],
                    'Accounts Receivable': latest_balance['accounts_receivable'],
                    'Inventory': latest_balance['inventory'],
                    'Other Current Assets': latest_balance['current_assets'] - latest_balance['cash_and_equivalents'] - latest_balance['accounts_receivable'] - latest_balance['inventory'],
                    'Non-Current Assets': latest_balance['total_assets'] - latest_balance['current_assets']
                }
            else:
                st.warning("⚠️ Required columns for asset composition analysis not found. Please ensure your balance sheet data includes all required asset columns.")
                return
            
            fig = px.pie(values=list(asset_composition.values()), names=list(asset_composition.keys()),
                        title="Asset Composition")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, key="chart_9")
            
            # AI Strategic Recommendations for Solvency Metrics
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            
            if generate_solvency_metrics_ai_recommendations:
                try:
                    ai_recommendations = generate_solvency_metrics_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("💰 Cash Flow Analysis")
        
        if not st.session_state.cash_flow.empty:
            # Operating cash flow trend
            fig = go.Figure(data=[
                go.Scatter(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['operating_cash_flow'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Operating Cash Flow')
            ])
            fig.update_layout(
                title="Operating Cash Flow Trend",
                xaxis_title="Period",
                yaxis_title="Operating Cash Flow ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="operating_cf_trend")
            
            # Operating cash flow components
            col1, col2 = st.columns(2)
            with col1:
                latest_cf = st.session_state.cash_flow.iloc[-1]
                
                # Check if required columns exist for cash flow components
                cf_cols = ['net_income', 'depreciation', 'working_capital_change', 'capital_expenditures']
                if all(col in latest_cf.index for col in cf_cols):
                    cf_components = {
                        'Net Income': latest_cf['net_income'],
                        'Depreciation': latest_cf['depreciation'],
                        'Working Capital Change': -latest_cf['working_capital_change'],
                        'Capital Expenditures': -latest_cf['capital_expenditures']
                    }
                else:
                    st.warning("⚠️ Required columns for cash flow components not found. Please ensure your cash flow data includes all required columns.")
                    return
                
                fig = px.bar(x=list(cf_components.keys()), y=list(cf_components.values()),
                            title="Operating Cash Flow Components",
                            color=list(cf_components.values()),
                            color_continuous_scale='RdYlGn')
                fig.update_layout(
                    xaxis_title="Component",
                    yaxis_title="Amount ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="cf_components")
            
            with col2:
                # Cash flow quality analysis
                cf_quality_data = st.session_state.cash_flow.copy()
                cf_quality_data['cf_quality'] = (cf_quality_data['operating_cash_flow'] / cf_quality_data['net_income']).round(2)
                
                fig = go.Figure(data=[
                    go.Scatter(x=cf_quality_data['period'], y=cf_quality_data['cf_quality'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='Cash Flow Quality')
                ])
                fig.update_layout(
                    title="Cash Flow Quality (OCF/Net Income)",
                    xaxis_title="Period",
                    yaxis_title="Quality Ratio",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Good Quality (≥1.0)")
                fig.add_hline(y=0.8, line_dash="dash", line_color="orange", annotation_text="Acceptable (≥0.8)")
                st.plotly_chart(fig, use_container_width=True, key="cf_quality")
            
            # AI Strategic Recommendations for Cash Flow Analysis
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            
            if generate_cash_flow_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_cash_flow_analysis_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("📋 Risk Assessment")
        
        if not st.session_state.balance_sheet.empty:
            # Risk metrics summary
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            # Check if required columns exist for risk metrics
            risk_cols = ['current_assets', 'current_liabilities', 'total_liabilities', 'shareholder_equity']
            if all(col in latest_bs.index for col in risk_cols):
                current_ratio = latest_bs['current_assets'] / latest_bs['current_liabilities']
                debt_to_equity = latest_bs['total_liabilities'] / latest_bs['shareholder_equity']
                working_capital = latest_bs['current_assets'] - latest_bs['current_liabilities']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if current_ratio >= 2.0:
                        st.success(f"✅ Current Ratio: {current_ratio:.2f} (Excellent)")
                    elif current_ratio >= 1.5:
                        st.info(f"ℹ️ Current Ratio: {current_ratio:.2f} (Good)")
                    else:
                        st.warning(f"⚠️ Current Ratio: {current_ratio:.2f} (Poor)")
                
                with col2:
                    if debt_to_equity <= 0.5:
                        st.success(f"✅ Debt-to-Equity: {debt_to_equity:.2f} (Conservative)")
                    elif debt_to_equity <= 1.0:
                        st.info(f"ℹ️ Debt-to-Equity: {debt_to_equity:.2f} (Moderate)")
                    else:
                        st.warning(f"⚠️ Debt-to-Equity: {debt_to_equity:.2f} (High Risk)")
                
                with col3:
                    if working_capital > 0:
                        st.success(f"✅ Working Capital: ${working_capital:,.0f} (Positive)")
                    else:
                        st.error(f"❌ Working Capital: ${working_capital:,.0f} (Negative)")
                
                # Risk recommendations
                st.write("**Risk Assessment Summary:**")
                if current_ratio < 1.5:
                    st.warning("⚠️ **Liquidity Risk**: Current ratio below recommended level. Consider improving working capital management.")
                
                if debt_to_equity > 1.0:
                    st.warning("⚠️ **Solvency Risk**: High debt levels detected. Review capital structure and debt management.")
                
                if working_capital < 0:
                    st.error("❌ **Working Capital Risk**: Negative working capital indicates potential liquidity issues.")
                
                if current_ratio >= 2.0 and debt_to_equity <= 0.5:
                    st.success("✅ **Low Risk Profile**: Strong liquidity and conservative capital structure.")
            else:
                st.warning("⚠️ Required columns for risk assessment not found. Please ensure your balance sheet data includes all required columns.")
        
        # AI Strategic Recommendations - Always show regardless of column requirements
        st.markdown("---")
        st.markdown("### 🤖 AI Strategic Recommendations")
        
        if generate_liquidity_solvency_ai_recommendations:
            try:
                ai_recommendations = generate_liquidity_solvency_ai_recommendations(
                    st.session_state.balance_sheet,
                    st.session_state.cash_flow
                )
                display_formatted_recommendations(ai_recommendations)
            except Exception as e:
                st.error(f"Error generating AI recommendations: {e}")
                st.info("Please check if you have loaded balance sheet data in the Data Input section.")
        else:
            st.error("AI recommendations function not available. Please check the import.")

def show_efficiency_productivity():
    st.markdown("""
    <div class="section-header">
        <h3>⚡ Efficiency and Productivity</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.income_statement.empty and st.session_state.balance_sheet.empty:
        st.info("⚡ Please upload income statement and balance sheet data to view efficiency and productivity analytics.")
        return
    
    # Calculate efficiency metrics
    efficiency_summary, efficiency_message = calculate_efficiency_metrics(
        st.session_state.income_statement, st.session_state.balance_sheet
    )
    
    # Display summary metrics
    st.subheader("⚡ Efficiency and Productivity Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not efficiency_summary.empty:
            roa = efficiency_summary.iloc[0]['Value']
            st.metric("Return on Assets (ROA)", roa)
    
    with col2:
        if not efficiency_summary.empty and len(efficiency_summary) > 1:
            roe = efficiency_summary.iloc[1]['Value']
            st.metric("Return on Equity (ROE)", roe)
    
    with col3:
        if not efficiency_summary.empty and len(efficiency_summary) > 2:
            asset_turnover = efficiency_summary.iloc[2]['Value']
            st.metric("Asset Turnover Ratio", asset_turnover)
    
    with col4:
        if not efficiency_summary.empty and len(efficiency_summary) > 3:
            op_exp_ratio = efficiency_summary.iloc[3]['Value']
            st.metric("Operating Expense Ratio", op_exp_ratio)
    
    st.info(efficiency_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 ROA & ROE Analysis", "🔄 Asset Turnover", "💰 Expense Efficiency", "📈 Productivity Trends"
    ])
    
    # Calculate efficiency metrics for all tabs
    efficiency_data = None
    if not st.session_state.income_statement.empty and not st.session_state.balance_sheet.empty:
        try:
            efficiency_data = st.session_state.income_statement.merge(
                st.session_state.balance_sheet[['period', 'total_assets', 'shareholder_equity']], 
                on='period', how='inner'
            )
            efficiency_data['roa'] = (efficiency_data['net_income'] / efficiency_data['total_assets'] * 100).round(2)
            efficiency_data['roe'] = (efficiency_data['net_income'] / efficiency_data['shareholder_equity'] * 100).round(2)
            efficiency_data['asset_turnover'] = (efficiency_data['revenue'] / efficiency_data['total_assets']).round(2)
            
            # Debug: Show efficiency data structure
            if st.checkbox("Show efficiency data debug"):
                st.write("Efficiency data columns:", list(efficiency_data.columns))
                st.write("Efficiency data shape:", efficiency_data.shape)
                st.write("Sample efficiency data:", efficiency_data.head())
        except Exception as e:
            st.error(f"❌ Error creating efficiency data: {str(e)}")
            efficiency_data = None
    
    with tab1:
        st.subheader("📊 ROA & ROE Analysis")
        
        if efficiency_data is not None:
            
            # ROA trend
            fig = go.Figure(data=[
                go.Scatter(x=efficiency_data['period'], y=efficiency_data['roa'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='ROA (%)')
            ])
            fig.update_layout(
                title="Return on Assets (ROA) Trend",
                xaxis_title="Period",
                yaxis_title="ROA (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=10, line_dash="dash", line_color="green", annotation_text="Good (10%)")
            fig.add_hline(y=5, line_dash="dash", line_color="orange", annotation_text="Average (5%)")
            st.plotly_chart(fig, use_container_width=True, key="chart_13")
            
            # ROE trend
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Scatter(x=efficiency_data['period'], y=efficiency_data['roe'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='ROE (%)')
                ])
                fig.update_layout(
                    title="Return on Equity (ROE) Trend",
                    xaxis_title="Period",
                    yaxis_title="ROE (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=15, line_dash="dash", line_color="green", annotation_text="Good (15%)")
                fig.add_hline(y=10, line_dash="dash", line_color="orange", annotation_text="Average (10%)")
                st.plotly_chart(fig, use_container_width=True, key="chart_14")
            
            with col2:
                # ROA vs ROE comparison
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=efficiency_data['period'], y=efficiency_data['roa'],
                                        mode='lines+markers', name='ROA', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=efficiency_data['period'], y=efficiency_data['roe'],
                                        mode='lines+markers', name='ROE', line=dict(color='#2ca02c')))
                fig.update_layout(
                    title="ROA vs ROE Comparison",
                    xaxis_title="Period",
                    yaxis_title="Return (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_15")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_roa_roe_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_roa_roe_analysis_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("🔄 Asset Turnover")
        
        if efficiency_data is not None:
            # Asset turnover analysis
            asset_turnover_data = efficiency_data.copy()
            
            fig = go.Figure(data=[
                go.Scatter(x=asset_turnover_data['period'], y=asset_turnover_data['asset_turnover'],
                          mode='lines+markers', line=dict(color='#ff7f0e', width=3),
                          marker=dict(size=8), name='Asset Turnover')
            ])
            fig.update_layout(
                title="Asset Turnover Ratio Trend",
                xaxis_title="Period",
                yaxis_title="Asset Turnover Ratio",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_16")
            
            # Asset utilization analysis
            latest_data = asset_turnover_data.iloc[-1]
            asset_utilization = {
                'Revenue': latest_data['revenue'],
                'Total Assets': latest_data['total_assets'],
                'Asset Turnover': latest_data['asset_turnover']
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Revenue", f"${latest_data['revenue']:,.0f}")
                st.metric("Total Assets", f"${latest_data['total_assets']:,.0f}")
            
            with col2:
                st.metric("Asset Turnover", f"{latest_data['asset_turnover']:.2f}")
                efficiency_score = (latest_data['asset_turnover'] / 1.0) * 100  # Benchmark of 1.0
                st.metric("Efficiency Score", f"{efficiency_score:.1f}%")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_asset_turnover_ai_recommendations:
                try:
                    ai_recommendations = generate_asset_turnover_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("💰 Expense Efficiency")
        
        if not st.session_state.income_statement.empty:
            # Operating expense ratio analysis
            expense_data = st.session_state.income_statement.copy()
            expense_data['op_exp_ratio'] = (expense_data['operating_expenses'] / expense_data['revenue'] * 100).round(2)
            expense_data['cogs_ratio'] = (expense_data['cost_of_goods_sold'] / expense_data['revenue'] * 100).round(2)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=expense_data['period'], y=expense_data['op_exp_ratio'],
                                    mode='lines+markers', name='Operating Expense Ratio', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=expense_data['period'], y=expense_data['cogs_ratio'],
                                    mode='lines+markers', name='COGS Ratio', line=dict(color='#2ca02c')))
            fig.update_layout(
                title="Expense Ratios Over Time",
                xaxis_title="Period",
                yaxis_title="Ratio (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_17")
            
            # Expense breakdown
            latest_expense = expense_data.iloc[-1]
            expense_breakdown = {}
            
            # Add available expense categories
            if 'cost_of_goods_sold' in latest_expense.index:
                expense_breakdown['Cost of Goods Sold'] = latest_expense['cost_of_goods_sold']
            if 'operating_expenses' in latest_expense.index:
                expense_breakdown['Operating Expenses'] = latest_expense['operating_expenses']
            if 'interest_expense' in latest_expense.index:
                expense_breakdown['Interest Expense'] = latest_expense['interest_expense']
            if 'income_tax_expense' in latest_expense.index:
                expense_breakdown['Income Tax'] = latest_expense['income_tax_expense']
            
            # If no expense categories found, show a message
            if not expense_breakdown:
                st.warning("⚠️ No expense data available for breakdown analysis.")
                return
            
            fig = px.pie(values=list(expense_breakdown.values()), names=list(expense_breakdown.keys()),
                        title="Expense Breakdown")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, key="chart_18")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_expense_efficiency_ai_recommendations:
                try:
                    ai_recommendations = generate_expense_efficiency_ai_recommendations(
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("📈 Productivity Trends")
        
        if efficiency_data is not None and not efficiency_data.empty:
            try:
                # Productivity metrics
                productivity_data = efficiency_data.copy()
                productivity_data['revenue_per_asset'] = (productivity_data['revenue'] / productivity_data['total_assets']).round(2)
                productivity_data['profit_per_asset'] = (productivity_data['net_income'] / productivity_data['total_assets']).round(2)
            except Exception as e:
                st.error(f"❌ Error creating productivity data: {str(e)}")
                return
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=productivity_data['period'], y=productivity_data['revenue_per_asset'],
                                    mode='lines+markers', name='Revenue per Asset', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=productivity_data['period'], y=productivity_data['profit_per_asset'],
                                    mode='lines+markers', name='Profit per Asset', line=dict(color='#2ca02c')))
            fig.update_layout(
                title="Productivity Metrics",
                xaxis_title="Period",
                yaxis_title="Amount per Asset ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_19")
            
            # Efficiency insights
            try:
                latest_prod = productivity_data.iloc[-1]
            except Exception as e:
                st.error(f"❌ Error accessing productivity data: {str(e)}")
                return
            
            # Show debug information if needed
            if st.checkbox("Show productivity debug info"):
                st.write("Productivity data columns:", list(productivity_data.columns))
                st.write("Latest prod keys:", list(latest_prod.index))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if latest_prod['roa'] >= 10:
                    st.success(f"✅ ROA: {latest_prod['roa']:.1f}% (Excellent)")
                elif latest_prod['roa'] >= 5:
                    st.info(f"ℹ️ ROA: {latest_prod['roa']:.1f}% (Good)")
                else:
                    st.warning(f"⚠️ ROA: {latest_prod['roa']:.1f}% (Needs Improvement)")
            
            with col2:
                if latest_prod['roe'] >= 15:
                    st.success(f"✅ ROE: {latest_prod['roe']:.1f}% (Excellent)")
                elif latest_prod['roe'] >= 10:
                    st.info(f"ℹ️ ROE: {latest_prod['roe']:.1f}% (Good)")
                else:
                    st.warning(f"⚠️ ROE: {latest_prod['roe']:.1f}% (Needs Improvement)")
            
            with col3:
                try:
                    if latest_prod['asset_turnover'] >= 1.0:
                        st.success(f"✅ Asset Turnover: {latest_prod['asset_turnover']:.2f} (Good)")
                    else:
                        st.warning(f"⚠️ Asset Turnover: {latest_prod['asset_turnover']:.2f} (Low)")
                except KeyError:
                    st.error("❌ Asset Turnover data not available")
            
            # Recommendations
            st.write("**Efficiency Recommendations:**")
            if latest_prod['roa'] < 5:
                st.warning("⚠️ **Low ROA**: Consider improving asset utilization or reducing costs.")
            
            if latest_prod['roe'] < 10:
                st.warning("⚠️ **Low ROE**: Review capital structure and profitability drivers.")
            
            try:
                if latest_prod['asset_turnover'] < 1.0:
                    st.warning("⚠️ **Low Asset Turnover**: Consider divesting underutilized assets or improving sales.")
            except KeyError:
                pass
            
            if latest_prod['roa'] >= 10 and latest_prod['roe'] >= 15:
                st.success("✅ **Excellent Efficiency**: Strong asset utilization and profitability metrics.")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_productivity_trends_ai_recommendations:
                try:
                    ai_recommendations = generate_productivity_trends_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

def show_budget_forecasting():
    st.markdown("""
    <div class="section-header">
        <h3>📋 Budgeting, Forecasting & Variance</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.budget.empty and st.session_state.forecast.empty:
        st.info("📋 Please upload budget and forecast data to view budgeting and forecasting analytics.")
        return
    
    # Calculate budget variance metrics
    variance_summary, variance_message = calculate_budget_variance_metrics(
        st.session_state.income_statement, st.session_state.budget, st.session_state.forecast
    )
    
    # Display summary metrics
    st.subheader("📋 Budget and Forecasting Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not variance_summary.empty:
            budget_variance = variance_summary.iloc[0]['Value']
            st.metric("Budget Variance", budget_variance)
    
    with col2:
        if not variance_summary.empty and len(variance_summary) > 1:
            forecast_accuracy = variance_summary.iloc[1]['Value']
            st.metric("Forecast Accuracy (MAPE)", forecast_accuracy)
    
    with col3:
        if not variance_summary.empty and len(variance_summary) > 2:
            scenario_analysis = variance_summary.iloc[2]['Value']
            st.metric("Scenario Analysis", scenario_analysis)
    
    st.info(variance_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Budget Variance Analysis", "🔮 Forecast Accuracy", "📈 Scenario Analysis", "📋 Variance Reporting"
    ])
    
    with tab1:
        st.subheader("📊 Budget Variance Analysis")
        
        if not st.session_state.budget.empty and not st.session_state.income_statement.empty:
            try:
                # Always use manual column renaming approach for consistent results
                budget_copy = st.session_state.budget.copy()
                income_copy = st.session_state.income_statement[['period', 'revenue', 'cost_of_goods_sold', 'operating_expenses']].copy()
                
                # Rename budget columns
                budget_copy = budget_copy.rename(columns={
                    'revenue': 'revenue_budget',
                    'expenses': 'expenses_budget'
                })
                
                # Rename income statement columns
                income_copy = income_copy.rename(columns={
                    'revenue': 'revenue_actual',
                    'cost_of_goods_sold': 'cost_of_goods_sold_actual',
                    'operating_expenses': 'operating_expenses_actual'
                })
                
                # Merge with renamed columns
                budget_actual = budget_copy.merge(income_copy, on='period', how='inner')
                
                # Add calculated actual expenses column
                try:
                    # Check if we have the individual expense columns
                    if 'cost_of_goods_sold_actual' in budget_actual.columns and 'operating_expenses_actual' in budget_actual.columns:
                        budget_actual['expenses_actual'] = budget_actual['cost_of_goods_sold_actual'] + budget_actual['operating_expenses_actual']
                    elif 'expenses_actual' not in budget_actual.columns:
                        # If we don't have the individual columns, try to calculate from available data
                        st.warning("⚠️ Individual expense columns not found, using available data")
                        if 'cost_of_goods_sold' in budget_actual.columns and 'operating_expenses' in budget_actual.columns:
                            budget_actual['expenses_actual'] = budget_actual['cost_of_goods_sold'] + budget_actual['operating_expenses']
                        else:
                            st.error("❌ Cannot calculate expenses_actual - missing required columns")
                            st.write("Available columns:", list(budget_actual.columns))
                            return
                except KeyError as e:
                    st.error(f"❌ Error calculating expenses_actual: {str(e)}")
                    return
                
            except Exception as e:
                st.error(f"❌ Error merging budget and actual data: {str(e)}")
                return
            
            # Debug information removed for cleaner interface
            
            # Calculate variances with proper error handling
            try:
                # Check if required columns exist
                required_columns = ['revenue_budget', 'revenue_actual', 'expenses_budget', 'expenses_actual']
                missing_columns = [col for col in required_columns if col not in budget_actual.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing columns: {missing_columns}")
                    return
                
                budget_actual['revenue_variance'] = ((budget_actual['revenue_actual'] - budget_actual['revenue_budget']) / budget_actual['revenue_budget'] * 100).round(2)
                budget_actual['expense_variance'] = ((budget_actual['expenses_budget'] - budget_actual['expenses_actual']) / budget_actual['expenses_budget'] * 100).round(2)
            except KeyError as e:
                st.error(f"❌ Error calculating variances: {str(e)}. Please check your budget data structure.")
                st.write("Available columns:", list(budget_actual.columns))
                return
            
            # Revenue variance analysis
            fig = go.Figure(data=[
                go.Scatter(x=budget_actual['period'], y=budget_actual['revenue_variance'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Revenue Variance (%)')
            ])
            fig.update_layout(
                title="Revenue Budget Variance Over Time",
                xaxis_title="Period",
                yaxis_title="Variance (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="On Budget")
            fig.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="Favorable (+5%)")
            fig.add_hline(y=-5, line_dash="dash", line_color="red", annotation_text="Unfavorable (-5%)")
            st.plotly_chart(fig, use_container_width=True, key="chart_20")
            
            # Budget vs Actual comparison
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=budget_actual['period'], y=budget_actual['revenue_budget'],
                                    name='Budgeted Revenue', marker_color='#1f77b4'))
                fig.add_trace(go.Bar(x=budget_actual['period'], y=budget_actual['revenue_actual'],
                                    name='Actual Revenue', marker_color='#2ca02c'))
                fig.update_layout(
                    title="Budget vs Actual Revenue",
                    xaxis_title="Period",
                    yaxis_title="Revenue ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_21")
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=budget_actual['period'], y=budget_actual['expenses_budget'],
                                    name='Budgeted Expenses', marker_color='#ff7f0e'))
                fig.add_trace(go.Bar(x=budget_actual['period'], y=budget_actual['expenses_actual'],
                                    name='Actual Expenses', marker_color='#d62728'))
                fig.update_layout(
                    title="Budget vs Actual Expenses",
                    xaxis_title="Period",
                    yaxis_title="Expenses ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_22")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_budget_variance_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_budget_variance_analysis_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.budget
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and budget data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("🔮 Forecast Accuracy")
        
        if not st.session_state.forecast.empty and not st.session_state.income_statement.empty:
            try:
                # Always use manual column renaming approach for consistent results
                forecast_copy = st.session_state.forecast.copy()
                income_copy = st.session_state.income_statement[['period', 'revenue', 'cost_of_goods_sold', 'operating_expenses']].copy()
                
                # Rename forecast columns
                forecast_copy = forecast_copy.rename(columns={
                    'revenue': 'revenue_forecast',
                    'expenses': 'expenses_forecast'
                })
                
                # Rename income statement columns
                income_copy = income_copy.rename(columns={
                    'revenue': 'revenue_actual',
                    'cost_of_goods_sold': 'cost_of_goods_sold_actual',
                    'operating_expenses': 'operating_expenses_actual'
                })
                
                # Merge with renamed columns
                forecast_actual = forecast_copy.merge(income_copy, on='period', how='inner')
                
                # Check if we have any overlapping data
                if forecast_actual.empty:
                    st.warning("⚠️ No overlapping periods found between forecast and actual data.")
                    st.info("Forecast periods: " + ", ".join(forecast_copy['period'].astype(str).tolist()[:5]) + "...")
                    st.info("Income statement periods: " + ", ".join(income_copy['period'].astype(str).tolist()[:5]) + "...")
                    st.info("Please ensure your forecast data covers periods that exist in your income statement data.")
                    return
                
                # Add calculated actual expenses column
                try:
                    # Check if we have the individual expense columns
                    if 'cost_of_goods_sold_actual' in forecast_actual.columns and 'operating_expenses_actual' in forecast_actual.columns:
                        forecast_actual['expenses_actual'] = forecast_actual['cost_of_goods_sold_actual'] + forecast_actual['operating_expenses_actual']
                    elif 'expenses_actual' not in forecast_actual.columns:
                        # If we don't have the individual columns, try to calculate from available data
                        st.warning("⚠️ Individual forecast expense columns not found, using available data")
                        if 'cost_of_goods_sold' in forecast_actual.columns and 'operating_expenses' in forecast_actual.columns:
                            forecast_actual['expenses_actual'] = forecast_actual['cost_of_goods_sold'] + forecast_actual['operating_expenses']
                        else:
                            st.error("❌ Cannot calculate forecast expenses_actual - missing required columns")
                            st.write("Available forecast columns:", list(forecast_actual.columns))
                            return
                except KeyError as e:
                    st.error(f"❌ Error calculating forecast expenses_actual: {str(e)}")
                    return
                
            except Exception as e:
                st.error(f"❌ Error merging forecast and actual data: {str(e)}")
                return
            
            # Calculate forecast accuracy with error handling
            try:
                required_forecast_columns = ['revenue_forecast', 'revenue_actual', 'expenses_forecast', 'expenses_actual']
                missing_forecast_columns = [col for col in required_forecast_columns if col not in forecast_actual.columns]
                
                if missing_forecast_columns:
                    st.error(f"❌ Missing forecast columns: {missing_forecast_columns}")
                    return
                
                forecast_actual['revenue_accuracy'] = (abs(forecast_actual['revenue_forecast'] - forecast_actual['revenue_actual']) / forecast_actual['revenue_actual'] * 100).round(2)
                forecast_actual['expense_accuracy'] = (abs(forecast_actual['expenses_forecast'] - forecast_actual['expenses_actual']) / forecast_actual['expenses_actual'] * 100).round(2)
            except KeyError as e:
                st.error(f"❌ Error calculating forecast accuracy: {str(e)}")
                return
            
            # Forecast accuracy trend
            fig = go.Figure(data=[
                go.Scatter(x=forecast_actual['period'], y=forecast_actual['revenue_accuracy'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Revenue Forecast Error (%)')
            ])
            fig.update_layout(
                title="Forecast Accuracy Over Time",
                xaxis_title="Period",
                yaxis_title="Forecast Error (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="Excellent (≤5%)")
            fig.add_hline(y=10, line_dash="dash", line_color="orange", annotation_text="Good (≤10%)")
            fig.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="Poor (>20%)")
            st.plotly_chart(fig, use_container_width=True, key="chart_23")
            
            # Confidence level analysis
            col1, col2 = st.columns(2)
            with col1:
                if 'confidence_level' in forecast_actual.columns:
                    fig = go.Figure(data=[
                        go.Scatter(x=forecast_actual['period'], y=forecast_actual['confidence_level'],
                                  mode='lines+markers', line=dict(color='#2ca02c', width=3),
                                  marker=dict(size=8), name='Confidence Level')
                    ])
                    fig.update_layout(
                        title="Forecast Confidence Level",
                        xaxis_title="Period",
                        yaxis_title="Confidence Level",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True, key="chart_24")
                else:
                    st.info("Confidence level data not available in merged dataset.")
            
            with col2:
                # Forecast vs Actual comparison
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=forecast_actual['period'], y=forecast_actual['revenue_forecast'],
                                        mode='lines+markers', name='Forecasted Revenue', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=forecast_actual['period'], y=forecast_actual['revenue_actual'],
                                        mode='lines+markers', name='Actual Revenue', line=dict(color='#2ca02c')))
                fig.update_layout(
                    title="Forecast vs Actual Revenue",
                    xaxis_title="Period",
                    yaxis_title="Revenue ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_25")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_forecast_accuracy_ai_recommendations:
                try:
                    ai_recommendations = generate_forecast_accuracy_ai_recommendations(
                        st.session_state.forecast,
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded forecast and income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("📈 Scenario Analysis")
        
        if not st.session_state.income_statement.empty:
            # Scenario analysis simulation
            latest_revenue = st.session_state.income_statement['revenue'].iloc[-1]
            latest_expenses = st.session_state.income_statement['cost_of_goods_sold'].iloc[-1] + st.session_state.income_statement['operating_expenses'].iloc[-1]
            
            # Define scenarios
            scenarios = {
                'Optimistic': {'revenue_change': 0.20, 'expense_change': 0.05},
                'Base Case': {'revenue_change': 0.00, 'expense_change': 0.00},
                'Conservative': {'revenue_change': -0.10, 'expense_change': 0.10},
                'Pessimistic': {'revenue_change': -0.20, 'expense_change': 0.15}
            }
            
            scenario_results = []
            for scenario, changes in scenarios.items():
                new_revenue = latest_revenue * (1 + changes['revenue_change'])
                new_expenses = latest_expenses * (1 + changes['expense_change'])
                new_profit = new_revenue - new_expenses
                profit_margin = (new_profit / new_revenue * 100) if new_revenue > 0 else 0
                
                scenario_results.append({
                    'Scenario': scenario,
                    'Revenue': new_revenue,
                    'Expenses': new_expenses,
                    'Profit': new_profit,
                    'Profit Margin': profit_margin
                })
            
            scenario_df = pd.DataFrame(scenario_results)
            
            # Scenario comparison chart
            fig = go.Figure(data=[
                go.Bar(x=scenario_df['Scenario'], y=scenario_df['Profit'],
                       marker_color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'],
                       text=scenario_df['Profit'].round(0),
                       textposition='auto')
            ])
            fig.update_layout(
                title="Profit Projections by Scenario",
                xaxis_title="Scenario",
                yaxis_title="Projected Profit ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_26")
            
            # Scenario details table
            st.subheader("Scenario Details")
            display_dataframe_with_index_1(scenario_df.round(2))
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_scenario_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_scenario_analysis_ai_recommendations(
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("📋 Variance Reporting")
        
        if not st.session_state.budget.empty and not st.session_state.income_statement.empty:
            # Variance summary
            latest_budget = st.session_state.budget.iloc[-1]
            latest_actual = st.session_state.income_statement.iloc[-1]
            
            try:
                revenue_variance = ((latest_actual['revenue'] - latest_budget['revenue']) / latest_budget['revenue'] * 100) if latest_budget['revenue'] > 0 else 0
                expense_variance = ((latest_budget['expenses'] - (latest_actual['cost_of_goods_sold'] + latest_actual['operating_expenses'])) / latest_budget['expenses'] * 100) if latest_budget['expenses'] > 0 else 0
            except KeyError:
                st.warning("⚠️ Budget data structure doesn't match expected format. Please check your data.")
                revenue_variance = 0
                expense_variance = 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if revenue_variance >= 0:
                    st.success(f"✅ Revenue Variance: {revenue_variance:.1f}% (Favorable)")
                else:
                    st.error(f"❌ Revenue Variance: {revenue_variance:.1f}% (Unfavorable)")
            
            with col2:
                if expense_variance >= 0:
                    st.success(f"✅ Expense Variance: {expense_variance:.1f}% (Favorable)")
                else:
                    st.error(f"❌ Expense Variance: {expense_variance:.1f}% (Unfavorable)")
            
            with col3:
                total_variance = revenue_variance - expense_variance
                if total_variance >= 0:
                    st.success(f"✅ Net Variance: {total_variance:.1f}% (Favorable)")
                else:
                    st.error(f"❌ Net Variance: {total_variance:.1f}% (Unfavorable)")
            
            # Variance recommendations
            st.write("**Variance Analysis Recommendations:**")
            if abs(revenue_variance) > 10:
                st.warning(f"⚠️ **High Revenue Variance**: {abs(revenue_variance):.1f}% variance detected. Review revenue forecasting models.")
            
            if abs(expense_variance) > 10:
                st.warning(f"⚠️ **High Expense Variance**: {abs(expense_variance):.1f}% variance detected. Review cost control measures.")
            
            if revenue_variance < -5 and expense_variance > 5:
                st.error("❌ **Critical Variance**: Both revenue and expenses are significantly off target.")
            
            if abs(revenue_variance) <= 5 and abs(expense_variance) <= 5:
                st.success("✅ **Excellent Budget Performance**: All variances within acceptable ranges.")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_variance_reporting_ai_recommendations:
                try:
                    ai_recommendations = generate_variance_reporting_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.budget
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and budget data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

def show_cash_flow():
    st.markdown("""
    <div class="section-header">
        <h3>💸 Cash Flow & Working Capital</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.cash_flow.empty and st.session_state.balance_sheet.empty:
        st.info("💸 Please upload cash flow and balance sheet data to view cash flow analytics.")
        return
    
    # Calculate cash flow metrics
    cash_flow_summary, cash_flow_message = calculate_cash_flow_metrics(
        st.session_state.cash_flow, st.session_state.balance_sheet
    )
    
    # Display summary metrics
    st.subheader("💸 Cash Flow & Working Capital Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not cash_flow_summary.empty:
            operating_cf = cash_flow_summary.iloc[0]['Value']
            st.metric("Operating Cash Flow", operating_cf)
    
    with col2:
        if not cash_flow_summary.empty and len(cash_flow_summary) > 1:
            free_cf = cash_flow_summary.iloc[1]['Value']
            st.metric("Free Cash Flow", free_cf)
    
    with col3:
        if not cash_flow_summary.empty and len(cash_flow_summary) > 2:
            working_capital_turnover = cash_flow_summary.iloc[2]['Value']
            st.metric("Working Capital Turnover", working_capital_turnover)
    
    st.info(cash_flow_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Operating Cash Flow", "🔄 Free Cash Flow", "📊 Working Capital", "📈 Cash Flow Trends"
    ])
    
    with tab1:
        st.subheader("💰 Operating Cash Flow")
        
        if not st.session_state.cash_flow.empty:
            # Operating cash flow trend
            fig = go.Figure(data=[
                go.Scatter(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['operating_cash_flow'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Operating Cash Flow')
            ])
            fig.update_layout(
                title="Operating Cash Flow Trend",
                xaxis_title="Period",
                yaxis_title="Operating Cash Flow ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="operating_cf_trend")
            
            # Operating cash flow components
            col1, col2 = st.columns(2)
            with col1:
                latest_cf = st.session_state.cash_flow.iloc[-1]
                cf_components = {
                    'Net Income': latest_cf['net_income'],
                    'Depreciation': latest_cf['depreciation'],
                    'Working Capital Change': -latest_cf['working_capital_change']
                }
                
                fig = px.bar(x=list(cf_components.keys()), y=list(cf_components.values()),
                            title="Operating Cash Flow Components",
                            color=list(cf_components.values()),
                            color_continuous_scale='RdYlGn')
                fig.update_layout(
                    xaxis_title="Component",
                    yaxis_title="Amount ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="cf_components")
            
            with col2:
                # Cash flow quality analysis
                cf_quality_data = st.session_state.cash_flow.copy()
                cf_quality_data['cf_quality'] = (cf_quality_data['operating_cash_flow'] / cf_quality_data['net_income']).round(2)
                
                fig = go.Figure(data=[
                    go.Scatter(x=cf_quality_data['period'], y=cf_quality_data['cf_quality'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='Cash Flow Quality')
                ])
                fig.update_layout(
                    title="Cash Flow Quality (OCF/Net Income)",
                    xaxis_title="Period",
                    yaxis_title="Quality Ratio",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Good Quality (≥1.0)")
                fig.add_hline(y=0.8, line_dash="dash", line_color="orange", annotation_text="Acceptable (≥0.8)")
                st.plotly_chart(fig, use_container_width=True, key="cf_quality")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_operating_cash_flow_ai_recommendations:
                try:
                    ai_recommendations = generate_operating_cash_flow_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("🔄 Free Cash Flow")
        
        if not st.session_state.cash_flow.empty:
            # Free cash flow trend
            fig = go.Figure(data=[
                go.Scatter(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['free_cash_flow'],
                          mode='lines+markers', line=dict(color='#2ca02c', width=3),
                          marker=dict(size=8), name='Free Cash Flow')
            ])
            fig.update_layout(
                title="Free Cash Flow Trend",
                xaxis_title="Period",
                yaxis_title="Free Cash Flow ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="fcf_trend")
            
            # FCF vs OCF comparison
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['operating_cash_flow'],
                                        mode='lines+markers', name='Operating CF', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['free_cash_flow'],
                                        mode='lines+markers', name='Free CF', line=dict(color='#2ca02c')))
                fig.update_layout(
                    title="Operating vs Free Cash Flow",
                    xaxis_title="Period",
                    yaxis_title="Cash Flow ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="fcf_vs_ocf")
            
            with col2:
                # Capital expenditures analysis
                fig = go.Figure(data=[
                    go.Bar(x=st.session_state.cash_flow['period'], y=st.session_state.cash_flow['capital_expenditures'],
                           marker_color='#ff7f0e', name='Capital Expenditures',
                           text=st.session_state.cash_flow['capital_expenditures'].round(0),
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Capital Expenditures",
                    xaxis_title="Period",
                    yaxis_title="Capital Expenditures ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="capex_analysis")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_free_cash_flow_ai_recommendations:
                try:
                    ai_recommendations = generate_free_cash_flow_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("📊 Working Capital")
        
        if not st.session_state.balance_sheet.empty:
            # Working capital calculation
            working_capital_data = st.session_state.balance_sheet.copy()
            working_capital_data['working_capital'] = working_capital_data['current_assets'] - working_capital_data['current_liabilities']
            working_capital_data['working_capital_ratio'] = (working_capital_data['current_assets'] / working_capital_data['current_liabilities']).round(2)
            
            # Working capital trend
            fig = go.Figure(data=[
                go.Scatter(x=working_capital_data['period'], y=working_capital_data['working_capital'],
                          mode='lines+markers', line=dict(color='#9467bd', width=3),
                          marker=dict(size=8), name='Working Capital')
            ])
            fig.update_layout(
                title="Working Capital Trend",
                xaxis_title="Period",
                yaxis_title="Working Capital ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="wc_trend")
            
            # Working capital components
            col1, col2 = st.columns(2)
            with col1:
                latest_wc = working_capital_data.iloc[-1]
                wc_components = {
                    'Cash & Equivalents': latest_wc['cash_and_equivalents'],
                    'Accounts Receivable': latest_wc['accounts_receivable'],
                    'Inventory': latest_wc['inventory'],
                    'Other Current Assets': latest_wc['current_assets'] - latest_wc['cash_and_equivalents'] - latest_wc['accounts_receivable'] - latest_wc['inventory']
                }
                
                fig = px.pie(values=list(wc_components.values()), names=list(wc_components.keys()),
                            title="Working Capital Components")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="wc_components")
            
            with col2:
                # Working capital ratio
                fig = go.Figure(data=[
                    go.Scatter(x=working_capital_data['period'], y=working_capital_data['working_capital_ratio'],
                              mode='lines+markers', line=dict(color='#ff7f0e', width=3),
                              marker=dict(size=8), name='Working Capital Ratio')
                ])
                fig.update_layout(
                    title="Working Capital Ratio",
                    xaxis_title="Period",
                    yaxis_title="Ratio",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=2.0, line_dash="dash", line_color="green", annotation_text="Good (≥2.0)")
                fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Poor (<1.0)")
                st.plotly_chart(fig, use_container_width=True, key="wc_ratio")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_working_capital_ai_recommendations:
                try:
                    ai_recommendations = generate_working_capital_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.cash_flow
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet and cash flow data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("📈 Cash Flow Trends")
        
        if not st.session_state.cash_flow.empty:
            # Cash flow trend analysis
            cf_trends = st.session_state.cash_flow.copy()
            cf_trends['cf_growth'] = cf_trends['operating_cash_flow'].pct_change() * 100
            
            fig = go.Figure(data=[
                go.Scatter(x=cf_trends['period'], y=cf_trends['cf_growth'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Cash Flow Growth (%)')
            ])
            fig.update_layout(
                title="Cash Flow Growth Rate",
                xaxis_title="Period",
                yaxis_title="Growth Rate (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="No Growth")
            st.plotly_chart(fig, use_container_width=True, key="cf_growth")
            
            # Cash flow insights
            latest_cf_trend = cf_trends.iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if latest_cf_trend['operating_cash_flow'] > 0:
                    st.success(f"✅ Operating CF: ${latest_cf_trend['operating_cash_flow']:,.0f} (Positive)")
                else:
                    st.error(f"❌ Operating CF: ${latest_cf_trend['operating_cash_flow']:,.0f} (Negative)")
            
            with col2:
                if latest_cf_trend['free_cash_flow'] > 0:
                    st.success(f"✅ Free CF: ${latest_cf_trend['free_cash_flow']:,.0f} (Positive)")
                else:
                    st.error(f"❌ Free CF: ${latest_cf_trend['free_cash_flow']:,.0f} (Negative)")
            
            with col3:
                if not pd.isna(latest_cf_trend['cf_growth']) and latest_cf_trend['cf_growth'] > 0:
                    st.success(f"✅ CF Growth: {latest_cf_trend['cf_growth']:.1f}% (Growing)")
                elif not pd.isna(latest_cf_trend['cf_growth']):
                    st.warning(f"⚠️ CF Growth: {latest_cf_trend['cf_growth']:.1f}% (Declining)")
                else:
                    st.info("ℹ️ CF Growth: No data")
            
            # Cash flow recommendations
            st.write("**Cash Flow Analysis Recommendations:**")
            if latest_cf_trend['operating_cash_flow'] < 0:
                st.error("❌ **Negative Operating Cash Flow**: Critical issue. Review operations and cost structure.")
            
            if latest_cf_trend['free_cash_flow'] < 0:
                st.warning("⚠️ **Negative Free Cash Flow**: May indicate over-investment or operational issues.")
            
            if latest_cf_trend['operating_cash_flow'] > 0 and latest_cf_trend['free_cash_flow'] > 0:
                st.success("✅ **Strong Cash Flow**: Positive operating and free cash flow indicate healthy operations.")
            
            # Working capital recommendations
            if not st.session_state.balance_sheet.empty:
                latest_wc = st.session_state.balance_sheet.iloc[-1]
                working_capital = latest_wc['current_assets'] - latest_wc['current_liabilities']
                
                if working_capital < 0:
                    st.error("❌ **Negative Working Capital**: Immediate attention required for liquidity management.")
                elif working_capital < latest_wc['current_assets'] * 0.1:
                    st.warning("⚠️ **Low Working Capital**: Consider improving working capital management.")
                else:
                    st.success("✅ **Adequate Working Capital**: Sufficient liquidity for operations.")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_cash_flow_trends_ai_recommendations:
                try:
                    ai_recommendations = generate_cash_flow_trends_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

def show_capital_structure():
    st.markdown("""
    <div class="section-header">
        <h3>🏗️ Capital Structure & Financing</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.balance_sheet.empty and st.session_state.income_statement.empty:
        st.info("🏗️ Please upload balance sheet and income statement data to view capital structure analytics.")
        return
    
    # Calculate capital structure metrics
    capital_summary, capital_message = calculate_capital_structure_metrics(
        st.session_state.balance_sheet, st.session_state.income_statement
    )
    
    # Display summary metrics
    st.subheader("🏗️ Capital Structure Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not capital_summary.empty:
            debt_equity = capital_summary.iloc[0]['Value']
            st.metric("Debt-to-Equity Ratio", debt_equity)
    
    with col2:
        if not capital_summary.empty and len(capital_summary) > 1:
            wacc = capital_summary.iloc[1]['Value']
            st.metric("WACC", wacc)
    
    with col3:
        if not capital_summary.empty and len(capital_summary) > 2:
            interest_coverage = capital_summary.iloc[2]['Value']
            st.metric("Interest Coverage Ratio", interest_coverage)
    
    st.info(capital_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Debt Analysis", "💰 WACC Calculation", "🏦 Interest Coverage", "📈 Capital Optimization"
    ])
    
    with tab1:
        st.subheader("📊 Debt Analysis")
        
        if not st.session_state.balance_sheet.empty:
            # Debt-to-equity trend
            debt_analysis = st.session_state.balance_sheet.copy()
            debt_analysis['debt_to_equity'] = (debt_analysis['total_liabilities'] / debt_analysis['shareholder_equity']).round(2)
            debt_analysis['debt_ratio'] = (debt_analysis['total_liabilities'] / debt_analysis['total_assets'] * 100).round(2)
            
            fig = go.Figure(data=[
                go.Scatter(x=debt_analysis['period'], y=debt_analysis['debt_to_equity'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='Debt-to-Equity Ratio')
            ])
            fig.update_layout(
                title="Debt-to-Equity Ratio Trend",
                xaxis_title="Period",
                yaxis_title="Debt-to-Equity Ratio",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=0.5, line_dash="dash", line_color="green", annotation_text="Conservative (0.5)")
            fig.add_hline(y=1.0, line_dash="dash", line_color="orange", annotation_text="Moderate (1.0)")
            fig.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="High Risk (2.0)")
            st.plotly_chart(fig, use_container_width=True, key="chart_27")
            
            # Capital structure composition
            col1, col2 = st.columns(2)
            with col1:
                latest_debt = debt_analysis.iloc[-1]
                capital_composition = {
                    'Total Liabilities': latest_debt['total_liabilities'],
                    'Shareholder Equity': latest_debt['shareholder_equity']
                }
                
                fig = px.pie(values=list(capital_composition.values()), names=list(capital_composition.keys()),
                            title="Capital Structure Composition")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="chart_28")
            
            with col2:
                # Debt ratio trend
                fig = go.Figure(data=[
                    go.Scatter(x=debt_analysis['period'], y=debt_analysis['debt_ratio'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='Debt Ratio (%)')
                ])
                fig.update_layout(
                    title="Debt Ratio Trend",
                    xaxis_title="Period",
                    yaxis_title="Debt Ratio (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Conservative (30%)")
                fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Moderate (50%)")
                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk (70%)")
                st.plotly_chart(fig, use_container_width=True, key="chart_29")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_debt_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_debt_analysis_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet and income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("💰 WACC Calculation")
        
        if not st.session_state.balance_sheet.empty:
            # WACC calculation details
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            equity_value = latest_bs['shareholder_equity']
            debt_value = latest_bs['total_liabilities']
            total_value = equity_value + debt_value
            
            # Assumed costs (in real scenario, these would come from market data)
            cost_of_equity = 0.12  # 12%
            cost_of_debt = 0.06    # 6%
            tax_rate = 0.25        # 25%
            
            equity_weight = equity_value / total_value if total_value > 0 else 0
            debt_weight = debt_value / total_value if total_value > 0 else 0
            
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
            
            # WACC breakdown
            wacc_breakdown = {
                'Equity Component': equity_weight * cost_of_equity * 100,
                'Debt Component': debt_weight * cost_of_debt * (1 - tax_rate) * 100
            }
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=list(wacc_breakdown.values()), names=list(wacc_breakdown.keys()),
                            title="WACC Components")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="chart_30")
            
            with col2:
                # WACC metrics
                st.metric("Total Value", f"${total_value:,.0f}")
                st.metric("Equity Weight", f"{equity_weight:.1%}")
                st.metric("Debt Weight", f"{debt_weight:.1%}")
                st.metric("WACC", f"{wacc:.1%}")
            
            # WACC sensitivity analysis
            st.subheader("WACC Sensitivity Analysis")
            
            # Create sensitivity matrix
            equity_costs = [0.10, 0.12, 0.14, 0.16]
            debt_costs = [0.04, 0.06, 0.08, 0.10]
            
            sensitivity_data = []
            for ec in equity_costs:
                for dc in debt_costs:
                    wacc_sens = (equity_weight * ec) + (debt_weight * dc * (1 - tax_rate))
                    sensitivity_data.append({
                        'Cost of Equity': f"{ec:.1%}",
                        'Cost of Debt': f"{dc:.1%}",
                        'WACC': f"{wacc_sens:.1%}"
                    })
            
            sensitivity_df = pd.DataFrame(sensitivity_data)
            display_dataframe_with_index_1(sensitivity_df)
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_wacc_calculation_ai_recommendations:
                try:
                    ai_recommendations = generate_wacc_calculation_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet and income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("🏦 Interest Coverage")
        
        if not st.session_state.income_statement.empty and not st.session_state.balance_sheet.empty:
            # Check if required columns exist
            if 'interest_expense' not in st.session_state.income_statement.columns:
                st.warning("⚠️ Interest expense data not available. Skipping interest coverage analysis.")
                return
            if 'operating_income' not in st.session_state.income_statement.columns:
                st.warning("⚠️ Operating income data not available. Skipping interest coverage analysis.")
                return
            
            try:
                # Interest coverage analysis
                coverage_data = st.session_state.income_statement.copy()
                coverage_data['interest_coverage'] = (coverage_data['operating_income'] / coverage_data['interest_expense']).round(2)
            except Exception as e:
                st.error(f"❌ Error in interest coverage analysis: {str(e)}")
                return
            
            fig = go.Figure(data=[
                go.Scatter(x=coverage_data['period'], y=coverage_data['interest_coverage'],
                          mode='lines+markers', line=dict(color='#ff7f0e', width=3),
                          marker=dict(size=8), name='Interest Coverage Ratio')
            ])
            fig.update_layout(
                title="Interest Coverage Ratio Trend",
                xaxis_title="Period",
                yaxis_title="Interest Coverage Ratio",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=3.0, line_dash="dash", line_color="green", annotation_text="Strong (≥3.0)")
            fig.add_hline(y=1.5, line_dash="dash", line_color="orange", annotation_text="Adequate (≥1.5)")
            fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Risky (<1.0)")
            st.plotly_chart(fig, use_container_width=True, key="interest_coverage_trend")
            
            # Interest expense analysis
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=coverage_data['period'], y=coverage_data['interest_expense'],
                           marker_color='#d62728', name='Interest Expense',
                           text=coverage_data['interest_expense'].round(0),
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Interest Expense Trend",
                    xaxis_title="Period",
                    yaxis_title="Interest Expense ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="interest_expense_trend")
            
            with col2:
                # Operating income vs interest expense
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=coverage_data['period'], y=coverage_data['operating_income'],
                                        mode='lines+markers', name='Operating Income', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=coverage_data['period'], y=coverage_data['interest_expense'],
                                        mode='lines+markers', name='Interest Expense', line=dict(color='#d62728')))
                fig.update_layout(
                    title="Operating Income vs Interest Expense",
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="operating_vs_interest")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_interest_coverage_ai_recommendations:
                try:
                    ai_recommendations = generate_interest_coverage_ai_recommendations(
                        st.session_state.income_statement,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded income statement and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("📈 Capital Optimization")
        
        if not st.session_state.balance_sheet.empty and not st.session_state.income_statement.empty:
            # Capital optimization analysis
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            latest_is = st.session_state.income_statement.iloc[-1]
            
            debt_to_equity = latest_bs['total_liabilities'] / latest_bs['shareholder_equity']
            debt_ratio = latest_bs['total_liabilities'] / latest_bs['total_assets']
            
            # Calculate interest coverage if data is available
            if 'interest_expense' in latest_is.index and 'operating_income' in latest_is.index:
                interest_coverage = latest_is['operating_income'] / latest_is['interest_expense'] if latest_is['interest_expense'] > 0 else float('inf')
            else:
                interest_coverage = float('inf')  # No interest expense means excellent coverage
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if debt_to_equity <= 0.5:
                    st.success(f"✅ Debt-to-Equity: {debt_to_equity:.2f} (Conservative)")
                elif debt_to_equity <= 1.0:
                    st.info(f"ℹ️ Debt-to-Equity: {debt_to_equity:.2f} (Moderate)")
                else:
                    st.warning(f"⚠️ Debt-to-Equity: {debt_to_equity:.2f} (High Risk)")
            
            with col2:
                if debt_ratio <= 0.3:
                    st.success(f"✅ Debt Ratio: {debt_ratio:.1%} (Conservative)")
                elif debt_ratio <= 0.5:
                    st.info(f"ℹ️ Debt Ratio: {debt_ratio:.1%} (Moderate)")
                else:
                    st.warning(f"⚠️ Debt Ratio: {debt_ratio:.1%} (High Risk)")
            
            with col3:
                if interest_coverage >= 3.0:
                    st.success(f"✅ Interest Coverage: {interest_coverage:.1f} (Strong)")
                elif interest_coverage >= 1.5:
                    st.info(f"ℹ️ Interest Coverage: {interest_coverage:.1f} (Adequate)")
                else:
                    st.error(f"❌ Interest Coverage: {interest_coverage:.1f} (Risky)")
            
            # Capital optimization recommendations
            st.write("**Capital Structure Recommendations:**")
            
            if debt_to_equity > 1.0:
                st.warning("⚠️ **High Debt Levels**: Consider reducing debt or increasing equity to improve financial stability.")
            
            if interest_coverage < 1.5:
                st.error("❌ **Low Interest Coverage**: Critical issue. Consider debt restructuring or operational improvements.")
            
            if debt_ratio > 0.5:
                st.warning("⚠️ **High Debt Ratio**: Review capital structure to reduce financial risk.")
            
            if debt_to_equity <= 0.5 and interest_coverage >= 3.0:
                st.success("✅ **Optimal Capital Structure**: Conservative debt levels with strong interest coverage.")
            
            # Optimal capital structure simulation
            st.subheader("Optimal Capital Structure Simulation")
            
            # Simulate different debt levels
            equity_base = latest_bs['shareholder_equity']
            debt_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
            
            simulation_results = []
            for debt_level in debt_levels:
                new_debt = equity_base * debt_level
                new_equity = equity_base - new_debt
                new_total = new_equity + new_debt
                
                # Simplified WACC calculation
                new_wacc = (new_equity/new_total * 0.12) + (new_debt/new_total * 0.06 * 0.75)
                
                simulation_results.append({
                    'Debt Level': f"{debt_level:.0%}",
                    'Debt Amount': new_debt,
                    'Equity Amount': new_equity,
                    'WACC': f"{new_wacc:.1%}"
                })
            
            simulation_df = pd.DataFrame(simulation_results)
            display_dataframe_with_index_1(simulation_df)
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_capital_optimization_ai_recommendations:
                try:
                    ai_recommendations = generate_capital_optimization_ai_recommendations(
                        st.session_state.balance_sheet,
                        st.session_state.income_statement
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded balance sheet and income statement data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

def show_investment_valuation():
    st.markdown("""
    <div class="section-header">
        <h3>📈 Investment & Valuation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.cash_flow.empty and st.session_state.balance_sheet.empty:
        st.info("📈 Please upload cash flow and balance sheet data to view investment and valuation analytics.")
        return
    
    # Calculate investment valuation metrics
    investment_summary, investment_message = calculate_investment_valuation_metrics(
        st.session_state.cash_flow, st.session_state.balance_sheet
    )
    
    # Display summary metrics
    st.subheader("📈 Investment & Valuation Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not investment_summary.empty:
            npv = investment_summary.iloc[0]['Value']
            st.metric("Net Present Value (NPV)", npv)
    
    with col2:
        if not investment_summary.empty and len(investment_summary) > 1:
            payback_period = investment_summary.iloc[1]['Value']
            st.metric("Payback Period", payback_period)
    
    with col3:
        if not investment_summary.empty and len(investment_summary) > 2:
            eva = investment_summary.iloc[2]['Value']
            st.metric("Economic Value Added (EVA)", eva)
    
    st.info(investment_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 NPV Analysis", "⏱️ Payback Period", "📊 EVA Calculation", "🎯 Investment Insights"
    ])
    
    with tab1:
        st.subheader("💰 NPV Analysis")
        
        if not st.session_state.cash_flow.empty:
            # NPV calculation with different discount rates
            cash_flows = st.session_state.cash_flow['cash_flow'].values
            initial_investment = st.session_state.cash_flow['initial_investment'].iloc[0]
            
            discount_rates = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]
            npv_results = []
            
            for rate in discount_rates:
                npv = -initial_investment
                for i, cf in enumerate(cash_flows):
                    npv += cf / ((1 + rate) ** (i + 1))
                npv_results.append({
                    'Discount Rate': f"{rate:.1%}",
                    'NPV': npv,
                    'Decision': 'Accept' if npv > 0 else 'Reject'
                })
            
            npv_df = pd.DataFrame(npv_results)
            
            # NPV vs Discount Rate chart
            fig = go.Figure(data=[
                go.Scatter(x=[float(x.strip('%'))/100 for x in npv_df['Discount Rate']], 
                          y=npv_df['NPV'],
                          mode='lines+markers', line=dict(color='#1f77b4', width=3),
                          marker=dict(size=8), name='NPV')
            ])
            fig.update_layout(
                title="NPV vs Discount Rate",
                xaxis_title="Discount Rate",
                yaxis_title="Net Present Value ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Break-even")
            st.plotly_chart(fig, use_container_width=True, key="chart_31")
            
            # NPV results table
            st.subheader("NPV Analysis Results")
            display_dataframe_with_index_1(npv_df.round(2))
            
            # IRR estimation (simplified)
            st.subheader("Internal Rate of Return (IRR) Estimation")
            
            # Find IRR using interpolation
            positive_npv = npv_df[npv_df['NPV'] > 0]
            negative_npv = npv_df[npv_df['NPV'] < 0]
            
            if not positive_npv.empty and not negative_npv.empty:
                # Simple interpolation to estimate IRR
                pos_rate = float(positive_npv.iloc[-1]['Discount Rate'].strip('%')) / 100
                neg_rate = float(negative_npv.iloc[0]['Discount Rate'].strip('%')) / 100
                pos_npv = positive_npv.iloc[-1]['NPV']
                neg_npv = negative_npv.iloc[0]['NPV']
                
                irr = pos_rate + (pos_npv / (pos_npv - neg_npv)) * (neg_rate - pos_rate)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated IRR", f"{irr:.1%}")
                with col2:
                    if irr > 0.15:
                        st.success("✅ High IRR (Excellent)")
                    elif irr > 0.10:
                        st.info("ℹ️ Good IRR (Acceptable)")
                    else:
                        st.warning("⚠️ Low IRR (Marginal)")
            else:
                st.info("IRR calculation requires both positive and negative NPV values")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_npv_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_npv_analysis_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("⏱️ Payback Period")
        
        if not st.session_state.cash_flow.empty:
            # Payback period calculation
            cash_flows = st.session_state.cash_flow['cash_flow'].values
            initial_investment = st.session_state.cash_flow['initial_investment'].iloc[0]
            
            cumulative_cf = 0
            payback_period = 0
            payback_data = []
            
            for i, cf in enumerate(cash_flows):
                cumulative_cf += cf
                payback_data.append({
                    'Period': i + 1,
                    'Cash Flow': cf,
                    'Cumulative CF': cumulative_cf,
                    'Remaining Investment': initial_investment - cumulative_cf
                })
                
                if cumulative_cf >= initial_investment and payback_period == 0:
                    payback_period = i + 1
            
            payback_df = pd.DataFrame(payback_data)
            
            # Payback period visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=payback_df['Period'], y=payback_df['Cumulative CF'],
                                    mode='lines+markers', name='Cumulative Cash Flow', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=payback_df['Period'], y=[initial_investment] * len(payback_df),
                                    mode='lines', name='Initial Investment', line=dict(color='red', dash='dash')))
            fig.update_layout(
                title="Payback Period Analysis",
                xaxis_title="Period",
                yaxis_title="Cumulative Cash Flow ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_32")
            
            # Payback period results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Investment", f"${initial_investment:,.0f}")
            with col2:
                st.metric("Payback Period", f"{payback_period} years")
            with col3:
                if payback_period <= 3:
                    st.success("✅ Quick Payback (≤3 years)")
                elif payback_period <= 5:
                    st.info("ℹ️ Moderate Payback (≤5 years)")
                else:
                    st.warning("⚠️ Long Payback (>5 years)")
            
            # Payback period table
            st.subheader("Payback Period Details")
            display_dataframe_with_index_1(payback_df.round(2))
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_payback_period_ai_recommendations:
                try:
                    ai_recommendations = generate_payback_period_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("📊 EVA Calculation")
        
        if not st.session_state.cash_flow.empty and not st.session_state.balance_sheet.empty:
            # EVA calculation
            latest_cf = st.session_state.cash_flow.iloc[-1]
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            nopat = latest_cf['nopat']
            capital_employed = latest_bs['total_assets']
            wacc = 0.092  # From previous calculation
            
            eva = nopat - (wacc * capital_employed)
            
            # EVA components
            eva_components = {
                'NOPAT': nopat,
                'Capital Charge': wacc * capital_employed,
                'EVA': eva
            }
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=list(eva_components.keys()), y=list(eva_components.values()),
                            title="EVA Components",
                            color=list(eva_components.values()),
                            color_continuous_scale='RdYlGn')
                fig.update_layout(
                    xaxis_title="Component",
                    yaxis_title="Amount ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_33")
            
            with col2:
                st.metric("NOPAT", f"${nopat:,.0f}")
                st.metric("Capital Employed", f"${capital_employed:,.0f}")
                st.metric("WACC", f"{wacc:.1%}")
                st.metric("EVA", f"${eva:,.0f}")
            
            # EVA trend analysis
            if len(st.session_state.cash_flow) > 1:
                eva_trend = st.session_state.cash_flow.copy()
                eva_trend['eva'] = eva_trend['nopat'] - (wacc * capital_employed)
                
                fig = go.Figure(data=[
                    go.Scatter(x=eva_trend['period'], y=eva_trend['eva'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='EVA')
                ])
                fig.update_layout(
                    title="EVA Trend Over Time",
                    xaxis_title="Period",
                    yaxis_title="Economic Value Added ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Break-even")
                st.plotly_chart(fig, use_container_width=True, key="chart_34")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_eva_calculation_ai_recommendations:
                try:
                    ai_recommendations = generate_eva_calculation_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("🎯 Investment Insights")
        
        if not st.session_state.cash_flow.empty:
            # Investment decision framework
            latest_npv = float(investment_summary.iloc[0]['Value'].replace('$', '').replace(',', '')) if not investment_summary.empty else 0
            latest_payback = int(investment_summary.iloc[1]['Value'].split()[0]) if not investment_summary.empty and len(investment_summary) > 1 else 0
            latest_eva = float(investment_summary.iloc[2]['Value'].replace('$', '').replace(',', '')) if not investment_summary.empty and len(investment_summary) > 2 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if latest_npv > 0:
                    st.success(f"✅ NPV: ${latest_npv:,.0f} (Positive)")
                else:
                    st.error(f"❌ NPV: ${latest_npv:,.0f} (Negative)")
            
            with col2:
                if latest_payback <= 3:
                    st.success(f"✅ Payback: {latest_payback} years (Quick)")
                elif latest_payback <= 5:
                    st.info(f"ℹ️ Payback: {latest_payback} years (Moderate)")
                else:
                    st.warning(f"⚠️ Payback: {latest_payback} years (Long)")
            
            with col3:
                if latest_eva > 0:
                    st.success(f"✅ EVA: ${latest_eva:,.0f} (Value Creating)")
                else:
                    st.error(f"❌ EVA: ${latest_eva:,.0f} (Value Destroying)")
            
            # Investment recommendations
            st.write("**Investment Analysis Recommendations:**")
            
            if latest_npv > 0 and latest_payback <= 3 and latest_eva > 0:
                st.success("✅ **Excellent Investment**: Strong NPV, quick payback, and positive EVA.")
            
            elif latest_npv > 0 and latest_payback <= 5:
                st.info("ℹ️ **Good Investment**: Positive NPV with acceptable payback period.")
            
            elif latest_npv < 0:
                st.error("❌ **Poor Investment**: Negative NPV indicates value destruction.")
            
            elif latest_payback > 5:
                st.warning("⚠️ **Long Payback Risk**: Consider shorter-term alternatives.")
            
            # Risk assessment
            st.subheader("Investment Risk Assessment")
            
            risk_factors = []
            if latest_npv < 0:
                risk_factors.append("Negative NPV")
            if latest_payback > 5:
                risk_factors.append("Long payback period")
            if latest_eva < 0:
                risk_factors.append("Negative EVA")
            
            if risk_factors:
                st.warning(f"⚠️ **Risk Factors Identified**: {', '.join(risk_factors)}")
            else:
                st.success("✅ **Low Risk Profile**: All metrics indicate favorable investment conditions.")
            
            # Sensitivity analysis
            st.subheader("Sensitivity Analysis")
            
            # Cash flow sensitivity
            base_cf = st.session_state.cash_flow['cash_flow'].mean()
            sensitivity_scenarios = [-20, -10, 0, 10, 20]  # Percentage changes
            
            sensitivity_results = []
            for change in sensitivity_scenarios:
                new_cf = base_cf * (1 + change/100)
                new_npv = -initial_investment + sum([new_cf / ((1 + 0.10) ** (i + 1)) for i in range(len(cash_flows))])
                
                sensitivity_results.append({
                    'Cash Flow Change': f"{change:+.0f}%",
                    'New NPV': new_npv,
                    'Decision': 'Accept' if new_npv > 0 else 'Reject'
                })
            
            sensitivity_df = pd.DataFrame(sensitivity_results)
            display_dataframe_with_index_1(sensitivity_df.round(2))
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_investment_insights_ai_recommendations:
                try:
                    ai_recommendations = generate_investment_insights_ai_recommendations(
                        st.session_state.cash_flow,
                        st.session_state.balance_sheet
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded cash flow and balance sheet data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

def show_risk_compliance():
    st.markdown("""
    <div class="section-header">
        <h3>⚠️ Risk & Compliance</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if (st.session_state.balance_sheet.empty and st.session_state.income_statement.empty and 
        st.session_state.cash_flow.empty and st.session_state.market_data.empty):
        st.info("⚠️ Please upload financial data to view risk and compliance analytics.")
        return
    
    # Use new risk analyzer if available
    if FinanceRiskAnalyzer is not None:
        # Initialize risk analyzer
        risk_analyzer = FinanceRiskAnalyzer(
            st.session_state.income_statement,
            st.session_state.balance_sheet,
            st.session_state.cash_flow,
            st.session_state.budget,
            st.session_state.forecast,
            st.session_state.market_data,
            st.session_state.customer_data,
            st.session_state.product_data,
            st.session_state.value_chain
        )
        
        # Generate comprehensive risk report
        risk_report = risk_analyzer.generate_comprehensive_risk_report()
        
        # Display risk dashboard
        display_risk_dashboard(risk_report)
        
        # Add traditional risk metrics as well
        if not st.session_state.balance_sheet.empty and not st.session_state.market_data.empty:
            risk_summary, risk_message = calculate_risk_compliance_metrics(
                st.session_state.balance_sheet, st.session_state.market_data
            )
            
            st.markdown("### 📊 Traditional Risk Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if not risk_summary.empty:
                    var = risk_summary.iloc[0]['Value']
                    st.metric("Value at Risk (VaR)", var)
            
            with col2:
                if not risk_summary.empty and len(risk_summary) > 1:
                    lcr = risk_summary.iloc[1]['Value']
                    st.metric("Liquidity Coverage Ratio", lcr)
            
            with col3:
                if not risk_summary.empty and len(risk_summary) > 2:
                    car = risk_summary.iloc[2]['Value']
                    st.metric("Capital Adequacy Ratio", car)
            
            st.info(risk_message)
    else:
        # Fallback to original risk analysis
        if st.session_state.balance_sheet.empty and st.session_state.market_data.empty:
            st.info("⚠️ Please upload balance sheet and market data to view risk and compliance analytics.")
            return
        
        # Calculate risk compliance metrics
        risk_summary, risk_message = calculate_risk_compliance_metrics(
            st.session_state.balance_sheet, st.session_state.market_data
        )
    
    # Display summary metrics
    st.subheader("⚠️ Risk & Compliance Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not risk_summary.empty:
            var = risk_summary.iloc[0]['Value']
            st.metric("Value at Risk (VaR)", var)
    
    with col2:
        if not risk_summary.empty and len(risk_summary) > 1:
            lcr = risk_summary.iloc[1]['Value']
            st.metric("Liquidity Coverage Ratio", lcr)
    
    with col3:
        if not risk_summary.empty and len(risk_summary) > 2:
            car = risk_summary.iloc[2]['Value']
            st.metric("Capital Adequacy Ratio", car)
    
    st.info(risk_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 VaR Analysis", "💧 Liquidity Risk", "🏦 Capital Adequacy", "📈 Risk Monitoring"
    ])
    
    with tab1:
        st.subheader("📊 VaR Analysis")
        
        if not st.session_state.balance_sheet.empty:
            # VaR calculation simulation
            portfolio_value = st.session_state.balance_sheet['total_assets'].iloc[-1]
            volatility = 0.15  # Assumed 15% volatility
            confidence_levels = [0.90, 0.95, 0.99]
            time_horizons = [1, 30, 90]  # days
            
            var_results = []
            for conf in confidence_levels:
                for horizon in time_horizons:
                    # Z-score for confidence level
                    z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
                    z_score = z_scores[conf]
                    
                    var = portfolio_value * volatility * np.sqrt(horizon/365) * z_score
                    var_results.append({
                        'Confidence Level': f"{conf:.0%}",
                        'Time Horizon': f"{horizon} days",
                        'VaR': var,
                        'VaR %': (var / portfolio_value * 100)
                    })
            
            var_df = pd.DataFrame(var_results)
            
            # VaR heatmap
            var_pivot = var_df.pivot(index='Time Horizon', columns='Confidence Level', values='VaR %')
            
            fig = go.Figure(data=go.Heatmap(
                z=var_pivot.values,
                x=var_pivot.columns,
                y=var_pivot.index,
                colorscale='RdYlGn_r',
                text=var_pivot.values.round(2),
                texttemplate="%{text}%",
                textfont={"size": 12}
            ))
            fig.update_layout(
                title="VaR by Confidence Level and Time Horizon",
                xaxis_title="Confidence Level",
                yaxis_title="Time Horizon",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_35")
            
            # VaR trend analysis
            if len(st.session_state.balance_sheet) > 1:
                var_trend = st.session_state.balance_sheet.copy()
                var_trend['var_95'] = var_trend['total_assets'] * volatility * np.sqrt(30/365) * 1.645
                
                fig = go.Figure(data=[
                    go.Scatter(x=var_trend['period'], y=var_trend['var_95'],
                              mode='lines+markers', line=dict(color='#d62728', width=3),
                              marker=dict(size=8), name='95% VaR (30 days)')
                ])
                fig.update_layout(
                    title="VaR Trend Over Time",
                    xaxis_title="Period",
                    yaxis_title="Value at Risk ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_36")
            
            # VaR results table
            st.subheader("VaR Analysis Results")
            display_dataframe_with_index_1(var_df.round(2))
    
    with tab2:
        st.subheader("💧 Liquidity Risk")
        
        if not st.session_state.balance_sheet.empty:
            # Liquidity coverage ratio calculation
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            # High-quality liquid assets (simplified)
            hqla = latest_bs['cash_and_equivalents']
            
            # Net cash outflows (simplified - 30% of current liabilities)
            net_cash_outflows = latest_bs['current_liabilities'] * 0.3
            
            lcr = hqla / net_cash_outflows if net_cash_outflows > 0 else 0
            
            # Liquidity metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High-Quality Liquid Assets", f"${hqla:,.0f}")
            with col2:
                st.metric("Net Cash Outflows (30 days)", f"${net_cash_outflows:,.0f}")
            with col3:
                st.metric("Liquidity Coverage Ratio", f"{lcr:.1%}")
            
            # LCR compliance
            if lcr >= 1.0:
                st.success("✅ **LCR Compliant**: Ratio ≥ 100% (Regulatory requirement met)")
            else:
                st.error(f"❌ **LCR Non-Compliant**: Ratio {lcr:.1%} < 100% (Regulatory requirement not met)")
            
            # Liquidity stress testing
            st.subheader("Liquidity Stress Testing")
            
            stress_scenarios = {
                'Baseline': 1.0,
                'Mild Stress': 0.8,
                'Moderate Stress': 0.6,
                'Severe Stress': 0.4
            }
            
            stress_results = []
            for scenario, factor in stress_scenarios.items():
                stressed_hqla = hqla * factor
                stressed_lcr = stressed_hqla / net_cash_outflows if net_cash_outflows > 0 else 0
                
                stress_results.append({
                    'Scenario': scenario,
                    'HQLA Factor': f"{factor:.1f}",
                    'Stressed HQLA': stressed_hqla,
                    'Stressed LCR': stressed_lcr,
                    'Compliant': 'Yes' if stressed_lcr >= 1.0 else 'No'
                })
            
            stress_df = pd.DataFrame(stress_results)
            display_dataframe_with_index_1(stress_df.round(2))
            
            # Liquidity composition
            liquidity_composition = {
                'Cash & Equivalents': latest_bs['cash_and_equivalents'],
                'Accounts Receivable': latest_bs['accounts_receivable'],
                'Other Liquid Assets': latest_bs['current_assets'] - latest_bs['cash_and_equivalents'] - latest_bs['accounts_receivable']
            }
            
            fig = px.pie(values=list(liquidity_composition.values()), names=list(liquidity_composition.keys()),
                        title="Liquidity Asset Composition")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, key="chart_37")
    
    with tab3:
        st.subheader("🏦 Capital Adequacy")
        
        if not st.session_state.balance_sheet.empty:
            # Capital adequacy ratio calculation
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            # Tier 1 capital (simplified - shareholder equity)
            tier1_capital = latest_bs['shareholder_equity']
            
            # Risk-weighted assets (simplified - 80% of total assets)
            risk_weighted_assets = latest_bs['total_assets'] * 0.8
            
            car = (tier1_capital / risk_weighted_assets * 100) if risk_weighted_assets > 0 else 0
            
            # Capital metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tier 1 Capital", f"${tier1_capital:,.0f}")
            with col2:
                st.metric("Risk-Weighted Assets", f"${risk_weighted_assets:,.0f}")
            with col3:
                st.metric("Capital Adequacy Ratio", f"{car:.1f}%")
            
            # CAR compliance
            if car >= 8.0:
                st.success("✅ **CAR Compliant**: Ratio ≥ 8% (Basel III requirement met)")
            else:
                st.error(f"❌ **CAR Non-Compliant**: Ratio {car:.1f}% < 8% (Basel III requirement not met)")
            
            # Capital structure analysis
            st.subheader("Capital Structure Analysis")
            
            capital_components = {
                'Tier 1 Capital': tier1_capital,
                'Total Liabilities': latest_bs['total_liabilities'],
                'Risk Buffer': tier1_capital - (risk_weighted_assets * 0.08)
            }
            
            fig = px.bar(x=list(capital_components.keys()), y=list(capital_components.values()),
                        title="Capital Components",
                        color=list(capital_components.values()),
                        color_continuous_scale='RdYlGn')
            fig.update_layout(
                xaxis_title="Component",
                yaxis_title="Amount ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_38")
            
            # Capital adequacy trend
            if len(st.session_state.balance_sheet) > 1:
                car_trend = st.session_state.balance_sheet.copy()
                car_trend['car'] = (car_trend['shareholder_equity'] / (car_trend['total_assets'] * 0.8) * 100).round(2)
                
                fig = go.Figure(data=[
                    go.Scatter(x=car_trend['period'], y=car_trend['car'],
                              mode='lines+markers', line=dict(color='#2ca02c', width=3),
                              marker=dict(size=8), name='Capital Adequacy Ratio (%)')
                ])
                fig.update_layout(
                    title="Capital Adequacy Ratio Trend",
                    xaxis_title="Period",
                    yaxis_title="CAR (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                fig.add_hline(y=8.0, line_dash="dash", line_color="green", annotation_text="Basel III (8%)")
                fig.add_hline(y=10.5, line_dash="dash", line_color="orange", annotation_text="Conservation Buffer (10.5%)")
                st.plotly_chart(fig, use_container_width=True, key="chart_39")
    
    with tab4:
        st.subheader("📈 Risk Monitoring")
        
        if not st.session_state.balance_sheet.empty:
            # Risk dashboard
            latest_bs = st.session_state.balance_sheet.iloc[-1]
            
            # Calculate various risk metrics
            current_ratio = latest_bs['current_assets'] / latest_bs['current_liabilities']
            debt_to_equity = latest_bs['total_liabilities'] / latest_bs['shareholder_equity']
            working_capital = latest_bs['current_assets'] - latest_bs['current_liabilities']
            
            # Risk assessment
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if current_ratio >= 2.0:
                    st.success(f"✅ Current Ratio: {current_ratio:.2f}")
                elif current_ratio >= 1.5:
                    st.info(f"ℹ️ Current Ratio: {current_ratio:.2f}")
                else:
                    st.error(f"❌ Current Ratio: {current_ratio:.2f}")
            
            with col2:
                if debt_to_equity <= 0.5:
                    st.success(f"✅ Debt-to-Equity: {debt_to_equity:.2f}")
                elif debt_to_equity <= 1.0:
                    st.info(f"ℹ️ Debt-to-Equity: {debt_to_equity:.2f}")
                else:
                    st.warning(f"⚠️ Debt-to-Equity: {debt_to_equity:.2f}")
            
            with col3:
                if working_capital > 0:
                    st.success(f"✅ Working Capital: ${working_capital:,.0f}")
                else:
                    st.error(f"❌ Working Capital: ${working_capital:,.0f}")
            
            with col4:
                if lcr >= 1.0:
                    st.success(f"✅ LCR: {lcr:.1%}")
                else:
                    st.error(f"❌ LCR: {lcr:.1%}")
            
            # Risk heatmap
            st.subheader("Risk Heatmap")
            
            risk_metrics = {
                'Liquidity Risk': current_ratio,
                'Solvency Risk': debt_to_equity,
                'Capital Risk': car/100,  # Normalize to 0-1
                'Working Capital Risk': 1 if working_capital > 0 else 0
            }
            
            # Create risk matrix
            risk_matrix = pd.DataFrame({
                'Risk Metric': list(risk_metrics.keys()),
                'Risk Score': list(risk_metrics.values()),
                'Risk Level': ['Low' if v > 0.5 else 'Medium' if v > 0.2 else 'High' for v in risk_metrics.values()]
            })
            
            fig = px.bar(risk_matrix, x='Risk Metric', y='Risk Score',
                        color='Risk Level',
                        color_discrete_map={'Low': '#2ca02c', 'Medium': '#ff7f0e', 'High': '#d62728'},
                        title="Risk Assessment Dashboard")
            fig.update_layout(
                xaxis_title="Risk Metric",
                yaxis_title="Risk Score",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_40")
            
            # Risk recommendations
            st.write("**Risk Management Recommendations:**")
            
            risk_issues = []
            if current_ratio < 1.5:
                risk_issues.append("Improve liquidity management")
            if debt_to_equity > 1.0:
                risk_issues.append("Reduce debt levels")
            if working_capital < 0:
                risk_issues.append("Address negative working capital")
            if lcr < 1.0:
                risk_issues.append("Increase liquid assets")
            if car < 8.0:
                risk_issues.append("Strengthen capital position")
            
            if risk_issues:
                st.warning(f"⚠️ **Risk Issues Identified**: {', '.join(risk_issues)}")
            else:
                st.success("✅ **Low Risk Profile**: All risk metrics within acceptable ranges.")
            
            # Early warning indicators
            st.subheader("Early Warning Indicators")
            
            warning_indicators = []
            if current_ratio < 1.0:
                warning_indicators.append("Critical liquidity risk")
            if debt_to_equity > 2.0:
                warning_indicators.append("Excessive leverage")
            if working_capital < -latest_bs['current_assets'] * 0.1:
                warning_indicators.append("Severe working capital deficit")
            if lcr < 0.5:
                warning_indicators.append("Inadequate liquidity coverage")
            
            if warning_indicators:
                st.error(f"🚨 **Critical Risk Alerts**: {', '.join(warning_indicators)}")
            else:
                st.success("✅ **No Critical Risk Alerts**: All indicators within safe ranges.")

def show_strategic_kpis():
    st.markdown("""
    <div class="section-header">
        <h3>📊 Strategic Financial KPIs</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have data
    if st.session_state.customer_data.empty and st.session_state.product_data.empty and st.session_state.value_chain.empty:
        st.info("📊 Please upload customer, product, and value chain data to view strategic KPIs analytics.")
        return
    
    # Calculate strategic KPIs
    strategic_summary, strategic_message = calculate_strategic_kpis(
        st.session_state.customer_data, st.session_state.product_data, st.session_state.value_chain
    )
    
    # Display summary metrics
    st.subheader("📊 Strategic Financial KPIs Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not strategic_summary.empty:
            customer_profitability = strategic_summary.iloc[0]['Value']
            st.metric("Customer Profitability", customer_profitability)
    
    with col2:
        if not strategic_summary.empty and len(strategic_summary) > 1:
            product_profitability = strategic_summary.iloc[1]['Value']
            st.metric("Product Profitability", product_profitability)
    
    with col3:
        if not strategic_summary.empty and len(strategic_summary) > 2:
            value_chain_cost = strategic_summary.iloc[2]['Value']
            st.metric("Value Chain Cost", value_chain_cost)
    
    st.info(strategic_message)
    
    # Detailed analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Customer Profitability", "📦 Product Profitability", "🔗 Value Chain Analysis", "🎯 Strategic Insights"
    ])
    
    with tab1:
        st.subheader("👥 Customer Profitability")
        
        if not st.session_state.customer_data.empty:
            # Customer profitability analysis
            customer_analysis = st.session_state.customer_data.copy()
            customer_analysis['profit'] = customer_analysis['revenue'] - customer_analysis['costs_to_serve']
            customer_analysis['profit_margin'] = (customer_analysis['profit'] / customer_analysis['revenue'] * 100).round(2)
            
            # Top customers by profitability
            top_customers = customer_analysis.nlargest(5, 'profit')
            
            fig = go.Figure(data=[
                go.Bar(x=top_customers['customer_name'], y=top_customers['profit'],
                       marker_color='#2ca02c', name='Profit',
                       text=top_customers['profit'].round(0),
                       textposition='auto')
            ])
            fig.update_layout(
                title="Top 5 Customers by Profit",
                xaxis_title="Customer",
                yaxis_title="Profit ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_41")
            
            # Customer profitability distribution
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(customer_analysis, x='profitability',
                                  title="Customer Profitability Distribution",
                                  nbins=10)
                fig.update_layout(
                    xaxis_title="Profitability (%)",
                    yaxis_title="Number of Customers",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_42")
            
            with col2:
                # Customer profitability vs revenue
                fig = px.scatter(customer_analysis, x='revenue', y='profitability',
                                title="Customer Profitability vs Revenue",
                                hover_data=['customer_name'])
                fig.update_layout(
                    xaxis_title="Revenue ($)",
                    yaxis_title="Profitability (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_43")
            
            # Customer segmentation
            st.subheader("Customer Segmentation")
            
            # Segment customers by profitability
            customer_analysis['segment'] = pd.cut(customer_analysis['profitability'], 
                                                bins=[-float('inf'), 0, 20, 40, float('inf')],
                                                labels=['Loss Making', 'Low Profit', 'Medium Profit', 'High Profit'])
            
            segment_summary = customer_analysis.groupby('segment').agg({
                'customer_id': 'count',
                'revenue': 'sum',
                'profit': 'sum',
                'profitability': 'mean'
            }).round(2)
            
            segment_summary.columns = ['Customer Count', 'Total Revenue', 'Total Profit', 'Avg Profitability']
            display_dataframe_with_index_1(segment_summary)
            
            # Customer profitability insights
            avg_profitability = customer_analysis['profitability'].mean()
            loss_making_customers = len(customer_analysis[customer_analysis['profitability'] < 0])
            total_customers = len(customer_analysis)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Profitability", f"{avg_profitability:.1f}%")
            with col2:
                st.metric("Loss-Making Customers", f"{loss_making_customers}/{total_customers}")
            with col3:
                loss_percentage = (loss_making_customers / total_customers * 100) if total_customers > 0 else 0
                st.metric("Loss-Making %", f"{loss_percentage:.1f}%")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_customer_profitability_ai_recommendations:
                try:
                    ai_recommendations = generate_customer_profitability_ai_recommendations(
                        st.session_state.customer_data
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded customer data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab2:
        st.subheader("📦 Product Profitability")
        
        if not st.session_state.product_data.empty:
            # Product profitability analysis
            product_analysis = st.session_state.product_data.copy()
            product_analysis['profit'] = product_analysis['revenue'] - product_analysis['total_costs']
            product_analysis['profit_margin'] = (product_analysis['profit'] / product_analysis['revenue'] * 100).round(2)
            
            # Product profitability ranking
            fig = go.Figure(data=[
                go.Bar(x=product_analysis['product_name'], y=product_analysis['profit_margin'],
                       marker_color='#1f77b4', name='Profit Margin (%)',
                       text=product_analysis['profit_margin'],
                       textposition='auto')
            ])
            fig.update_layout(
                title="Product Profitability Margins",
                xaxis_title="Product",
                yaxis_title="Profit Margin (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_44")
            
            # Product cost structure analysis
            col1, col2 = st.columns(2)
            with col1:
                cost_structure = {
                    'Direct Costs': product_analysis['direct_costs'].sum(),
                    'Allocated Costs': product_analysis['allocated_costs'].sum(),
                    'Total Revenue': product_analysis['revenue'].sum()
                }
                
                fig = px.pie(values=list(cost_structure.values()), names=list(cost_structure.keys()),
                            title="Product Cost Structure")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="chart_45")
            
            with col2:
                # Product revenue vs profit
                # Use absolute profit margin for size to handle negative values
                product_analysis_copy = product_analysis.copy()
                product_analysis_copy['abs_profit_margin'] = product_analysis_copy['profit_margin'].abs()
                
                fig = px.scatter(product_analysis_copy, x='revenue', y='profit',
                                title="Product Revenue vs Profit",
                                hover_data=['product_name'],
                                size='abs_profit_margin')
                fig.update_layout(
                    xaxis_title="Revenue ($)",
                    yaxis_title="Profit ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_46")
            
            # Product performance summary
            st.subheader("Product Performance Summary")
            
            product_summary = product_analysis.agg({
                'revenue': 'sum',
                'total_costs': 'sum',
                'profit': 'sum',
                'profit_margin': 'mean'
            }).round(2)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue", f"${product_summary['revenue']:,.0f}")
            with col2:
                st.metric("Total Costs", f"${product_summary['total_costs']:,.0f}")
            with col3:
                st.metric("Total Profit", f"${product_summary['profit']:,.0f}")
            with col4:
                st.metric("Avg Profit Margin", f"{product_summary['profit_margin']:.1f}%")
            
            # Product recommendations
            st.write("**Product Performance Recommendations:**")
            
            low_profit_products = product_analysis[product_analysis['profit_margin'] < 10]
            high_profit_products = product_analysis[product_analysis['profit_margin'] > 30]
            
            if not low_profit_products.empty:
                st.warning(f"⚠️ **Low Profit Products**: {len(low_profit_products)} products with <10% margin. Consider cost optimization or pricing review.")
            
            if not high_profit_products.empty:
                st.success(f"✅ **High Profit Products**: {len(high_profit_products)} products with >30% margin. Consider expansion opportunities.")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_product_profitability_ai_recommendations:
                try:
                    ai_recommendations = generate_product_profitability_ai_recommendations(
                        st.session_state.product_data
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded product data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab3:
        st.subheader("🔗 Value Chain Analysis")
        
        if not st.session_state.value_chain.empty:
            # Value chain cost analysis
            value_chain_analysis = st.session_state.value_chain.copy()
            
            # Value chain cost breakdown
            fig = go.Figure(data=[
                go.Bar(x=value_chain_analysis['function'], y=value_chain_analysis['cost'],
                       marker_color='#ff7f0e', name='Cost',
                       text=value_chain_analysis['cost'].round(0),
                       textposition='auto')
            ])
            fig.update_layout(
                title="Value Chain Cost by Function",
                xaxis_title="Function",
                yaxis_title="Cost ($)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_47")
            
            # Value chain cost distribution
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(value_chain_analysis, values='cost', names='function',
                            title="Value Chain Cost Distribution")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="chart_48")
            
            with col2:
                # Cost percentage by function
                fig = go.Figure(data=[
                    go.Bar(x=value_chain_analysis['function'], y=value_chain_analysis['percentage'],
                           marker_color='#9467bd', name='Cost %',
                           text=value_chain_analysis['percentage'].round(1),
                           textposition='auto')
                ])
                fig.update_layout(
                    title="Cost Percentage by Function",
                    xaxis_title="Function",
                    yaxis_title="Cost Percentage (%)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_49")
            
            # Value chain optimization
            st.subheader("Value Chain Optimization")
            
            total_cost = value_chain_analysis['cost'].sum()
            highest_cost_function = value_chain_analysis.loc[value_chain_analysis['cost'].idxmax()]
            lowest_cost_function = value_chain_analysis.loc[value_chain_analysis['cost'].idxmin()]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Value Chain Cost", f"${total_cost:,.0f}")
            with col2:
                st.metric("Highest Cost Function", f"{highest_cost_function['function']}")
            with col3:
                st.metric("Lowest Cost Function", f"{lowest_cost_function['function']}")
            
            # Value chain recommendations
            st.write("**Value Chain Optimization Recommendations:**")
            
            high_cost_functions = value_chain_analysis[value_chain_analysis['percentage'] > 20]
            if not high_cost_functions.empty:
                st.warning(f"⚠️ **High Cost Functions**: {', '.join(high_cost_functions['function'])} represent >20% of total cost. Consider optimization strategies.")
            
            # Cost reduction potential
            st.subheader("Cost Reduction Potential")
            
            # Simulate cost reduction scenarios
            reduction_scenarios = [0.05, 0.10, 0.15, 0.20]  # 5%, 10%, 15%, 20% reduction
            
            reduction_results = []
            for reduction in reduction_scenarios:
                new_total_cost = total_cost * (1 - reduction)
                savings = total_cost - new_total_cost
                
                reduction_results.append({
                    'Reduction Target': f"{reduction:.0%}",
                    'New Total Cost': new_total_cost,
                    'Cost Savings': savings,
                    'Savings %': reduction * 100
                })
            
            reduction_df = pd.DataFrame(reduction_results)
            display_dataframe_with_index_1(reduction_df.round(2))
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_value_chain_analysis_ai_recommendations:
                try:
                    ai_recommendations = generate_value_chain_analysis_ai_recommendations(
                        st.session_state.value_chain
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded value chain data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")
    
    with tab4:
        st.subheader("🎯 Strategic Insights")
        
        # Strategic insights dashboard
        if not st.session_state.customer_data.empty and not st.session_state.product_data.empty:
            # Key strategic metrics
            customer_avg_profitability = st.session_state.customer_data['profitability'].mean()
            product_avg_margin = (st.session_state.product_data['revenue'].sum() - st.session_state.product_data['total_costs'].sum()) / st.session_state.product_data['revenue'].sum() * 100
            value_chain_efficiency = 100 - st.session_state.value_chain['percentage'].sum() if not st.session_state.value_chain.empty else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if customer_avg_profitability > 25:
                    st.success(f"✅ Customer Profitability: {customer_avg_profitability:.1f}% (Excellent)")
                elif customer_avg_profitability > 15:
                    st.info(f"ℹ️ Customer Profitability: {customer_avg_profitability:.1f}% (Good)")
                else:
                    st.warning(f"⚠️ Customer Profitability: {customer_avg_profitability:.1f}% (Needs Improvement)")
            
            with col2:
                if product_avg_margin > 30:
                    st.success(f"✅ Product Margin: {product_avg_margin:.1f}% (Excellent)")
                elif product_avg_margin > 20:
                    st.info(f"ℹ️ Product Margin: {product_avg_margin:.1f}% (Good)")
                else:
                    st.warning(f"⚠️ Product Margin: {product_avg_margin:.1f}% (Needs Improvement)")
            
            with col3:
                if value_chain_efficiency > 80:
                    st.success(f"✅ Value Chain Efficiency: {value_chain_efficiency:.1f}% (Excellent)")
                elif value_chain_efficiency > 60:
                    st.info(f"ℹ️ Value Chain Efficiency: {value_chain_efficiency:.1f}% (Good)")
                else:
                    st.warning(f"⚠️ Value Chain Efficiency: {value_chain_efficiency:.1f}% (Needs Improvement)")
            
            # Strategic recommendations
            st.write("**Strategic Recommendations:**")
            
            recommendations = []
            
            if customer_avg_profitability < 15:
                recommendations.append("Focus on customer profitability improvement through pricing optimization and cost-to-serve reduction")
            
            if product_avg_margin < 20:
                recommendations.append("Review product pricing strategy and cost structure to improve margins")
            
            if value_chain_efficiency < 60:
                recommendations.append("Optimize value chain operations to reduce costs and improve efficiency")
            
            # Customer concentration risk
            if not st.session_state.customer_data.empty:
                top_customer_revenue = st.session_state.customer_data['revenue'].nlargest(1).iloc[0]
                total_revenue = st.session_state.customer_data['revenue'].sum()
                concentration = (top_customer_revenue / total_revenue * 100) if total_revenue > 0 else 0
                
                if concentration > 20:
                    recommendations.append(f"High customer concentration risk ({concentration:.1f}% from top customer). Diversify customer base.")
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
            else:
                st.success("✅ **Excellent Strategic Position**: All key metrics are performing well.")
            
            # Competitive positioning
            st.subheader("Competitive Positioning")
            
            # Benchmark analysis (simplified)
            benchmarks = {
                'Customer Profitability': {'Industry Avg': 18, 'Your Company': customer_avg_profitability},
                'Product Margin': {'Industry Avg': 25, 'Your Company': product_avg_margin},
                'Value Chain Efficiency': {'Industry Avg': 70, 'Your Company': value_chain_efficiency}
            }
            
            benchmark_df = pd.DataFrame(benchmarks)
            display_dataframe_with_index_1(benchmark_df.round(1))
            
            # Performance vs benchmarks
            st.write("**Performance vs Industry Benchmarks:**")
            
            for metric, values in benchmarks.items():
                your_value = values['Your Company']
                benchmark_value = values['Industry Avg']
                
                if your_value > benchmark_value * 1.1:
                    st.success(f"✅ {metric}: {your_value:.1f}% vs {benchmark_value}% (Above Benchmark)")
                elif your_value < benchmark_value * 0.9:
                    st.warning(f"⚠️ {metric}: {your_value:.1f}% vs {benchmark_value}% (Below Benchmark)")
                else:
                    st.info(f"ℹ️ {metric}: {your_value:.1f}% vs {benchmark_value}% (At Benchmark)")
            
            # Strategic priorities
            st.subheader("Strategic Priorities")
            
            priorities = []
            if customer_avg_profitability < 15:
                priorities.append("1. **Customer Profitability Optimization**")
            if product_avg_margin < 20:
                priorities.append("2. **Product Margin Enhancement**")
            if value_chain_efficiency < 60:
                priorities.append("3. **Value Chain Optimization**")
            if concentration > 20:
                priorities.append("4. **Customer Base Diversification**")
            
            if priorities:
                st.write("**Recommended Strategic Priorities:**")
                for priority in priorities:
                    st.write(priority)
            else:
                st.success("✅ **Strong Strategic Position**: Focus on growth and market expansion opportunities.")
            
            # AI Strategic Recommendations
            st.markdown("---")
            st.markdown("### 🤖 AI Strategic Recommendations")
            if generate_strategic_insights_ai_recommendations:
                try:
                    ai_recommendations = generate_strategic_insights_ai_recommendations(
                        st.session_state.customer_data,
                        st.session_state.product_data,
                        st.session_state.value_chain
                    )
                    display_formatted_recommendations(ai_recommendations)
                except Exception as e:
                    st.error(f"Error generating AI recommendations: {e}")
                    st.info("Please check if you have loaded customer, product, and value chain data in the Data Input section.")
            else:
                st.error("AI recommendations function not available. Please check the import.")

if __name__ == "__main__":
    main() 

    