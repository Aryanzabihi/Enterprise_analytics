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

# Import metric calculation functions
from metrics_calculator import *

# Import advanced cost metrics functions
from advanced_cost_metrics import (
    calculate_benchmark_price_efficiency, calculate_negotiation_opportunity_index,
    calculate_tail_spend_optimization, calculate_unit_cost_trend_analysis,
    calculate_savings_realization_tracking, calculate_spend_avoidance_detection,
    calculate_contract_leakage
)

# Import auto insights functionality
from auto_insights import ProcurementInsights, display_insights_section

# Import risk analyzer functionality
from risk_analyzer import ProcurementRiskAnalyzer, display_risk_dashboard

# Import predictive analytics functionality
from procurement_predictive_analytics import display_procurement_predictive_analytics_dashboard, ProcurementPredictiveAnalytics

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
def calculate_risk_scores(df):
    """Calculate various procurement risk scores for each supplier."""
    df = df.copy()
    mean_price = df['price'].mean()
    threshold = mean_price * 0.85
    df['lowball_risk'] = ((mean_price - df['price']) / mean_price).where(df['price'] < threshold, 0)
    if 'quality' in df.columns or 'technical' in df.columns:
        q_col = 'quality' if 'quality' in df.columns else 'technical'
        price_norm = (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
        quality_norm = (df[q_col] - df[q_col].min()) / (df[q_col].max() - df[q_col].min())
        df['drip_pricing_risk'] = price_norm * (1 - quality_norm)
        price_75 = df['price'].quantile(0.75)
        quality_25 = df[q_col].quantile(0.25)
        df['drip_pricing_flag'] = ((df['price'] > price_75) & (df[q_col] < quality_25)).astype(float)
    else:
        df['drip_pricing_risk'] = 0
        df['drip_pricing_flag'] = 0
    price_rank = df['price'].rank(pct=True)
    score_rank = df['score'].rank(pct=True)
    df['signaling_risk'] = ((score_rank > 0.8) & (price_rank > 0.8)).astype(float)
    high_price_threshold = df['price'].quantile(0.75)
    low_score_threshold = df['score'].median()
    df['cover_bid_risk'] = ((df['price'] > high_price_threshold) & (df[q_col] < low_score_threshold)).astype(float)
    df['price_z'] = (df['price'] - df['price'].mean()) / df['price'].std(ddof=0)
    df['score_z'] = (df['score'] - df['score'].mean()) / df['score'].std(ddof=0)
    df['decoy_bid_risk'] = ((df['price_z'].abs() > 2) | (df['score_z'].abs() > 2)).astype(float)
    df['price_rounded'] = df['price'].round(-2)
    df['score_rounded'] = df['score'].round(0)
    df['price_similarity'] = df['price_rounded'].duplicated(keep=False)
    df['score_similarity'] = df['score_rounded'].duplicated(keep=False)
    df['bid_similarity_risk'] = (df['price_similarity'] | df['score_similarity']).astype(float)
    risk_cols = [
        'lowball_risk', 'drip_pricing_risk', 'drip_pricing_flag', 'signaling_risk',
        'cover_bid_risk', 'decoy_bid_risk', 'bid_similarity_risk'
    ]
    df['total_risk'] = df[risk_cols].mean(axis=1)
    return df

def get_variable_list(df):
    """Return a list of numeric variables for scoring, excluding supplier/name/id columns."""
    return [
        col for col in df.columns
        if col.lower() not in ['supplier', 'name', 'id']
        and pd.api.types.is_numeric_dtype(df[col])
        and not df[col].isnull().all()
    ]

def normalize_column(col, minimize=False):
    """Normalize a pandas Series to [0,1], optionally minimizing."""
    if col.nunique() == 1:
        return pd.Series([1.0]*len(col), index=col.index)
    if minimize:
        return (col.max() - col) / (col.max() - col.min())
    else:
        return (col - col.min()) / (col.max() - col.min())

def get_weights(variables, scenario):
    """Return variable weights for different scoring scenarios."""
    n = len(variables)
    weights = dict.fromkeys(variables, 1/n)
    if scenario == 'price-focused' and 'price' in variables:
        weights = dict.fromkeys(variables, 0.2/(n-1) if n > 1 else 1)
        weights['price'] = 0.6
    elif scenario == 'quality-focused' and 'quality' in variables:
        weights = dict.fromkeys(variables, 0.2/(n-1) if n > 1 else 1)
        weights['quality'] = 0.6
    return weights

def apply_common_layout(fig):
    """Apply a common layout to Plotly figures for consistent style."""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial', size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

# --- Caching for Sample Data ---
@st.cache_data
def get_sample_df():
    """Return a sample DataFrame for user guidance."""
    return pd.DataFrame({
        'supplier': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E', 'Supplier F', 'Supplier G'],
        'price': [1000, 1175, 1080, 1120, 1055, 1205, 1095],
        'currency': ['USD', 'EUR', 'USD', 'EUR', 'USD', 'EUR', 'USD'],
        'discount': [50, 20, 35, 15, 25, 10, 30],
        'payment_terms': ['Net 30', 'Net 60', 'Net 45', 'Net 30', 'Net 60', 'Net 45', 'Net 30'],
        'quantity': [100, 180, 150, 170, 120, 160, 140],
        'min_order_quantity': [50, 90, 70, 85, 60, 80, 65],
        'lead_time_days': [30, 42, 29, 38, 33, 36, 40],
        'quality': [80, 86, 79, 83, 81, 82, 85],
        'technical': [90, 87, 86, 88, 85, 89, 91],
        'warranty_months': [24, 18, 20, 22, 18, 16, 24],
        'certifications': ['ISO9001,CE', 'ISO14001', 'ISO9001', 'CE', 'ISO9001,ISO14001', 'CE', 'ISO9001,CE'],
        'delivery_time_days': [35, 48, 33, 44, 39, 37, 41],
        'delivery_terms': ['FOB', 'CIF', 'FOB', 'CIF', 'FOB', 'CIF', 'FOB'],
        'shipping_cost': [100, 145, 95, 125, 110, 120, 115],
        'compliance': ['Yes', 'No', 'Yes', 'Yes', 'Yes', 'No', 'Yes'],
        'compliance_notes': ['All docs provided', 'Missing certificate', 'All docs provided', 'All docs provided', 'All docs provided', 'Missing docs', 'All docs provided'],
        'country': ['USA', 'Germany', 'USA', 'France', 'USA', 'Italy', 'Spain'],
        'supplier_type': ['Manufacturer', 'Distributor', 'Manufacturer', 'Distributor', 'Manufacturer', 'Distributor', 'Manufacturer'],
        'experience_years': [10, 6, 8, 7, 9, 5, 11],
        'score': [0.85, 0.79, 0.83, 0.81, 0.82, 0.77, 0.86],
        'remarks': ['Preferred', '', 'Reliable', '', 'Preferred', '', 'Top rated']
    })

# PDF Report Generation System - REMOVED

# PDF utility function removed as requested

# PDF utility function removed as requested

# PDF utility function removed as requested

# PDF utility function removed as requested

# PDF utility function removed as requested

def truncate_col(text, max_len=20):
    """Truncate text for table columns"""
    text = str(text)
    return text[:max_len] + '...' if len(text) > max_len else text

# PDF generation function removed as requested

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

def get_filtered_po_df():
    """Get filtered purchase order data with robust fallback logic"""
    po_df = st.session_state.purchase_orders.copy()
    
    # If no data, return empty DataFrame
    if po_df.empty:
        return po_df
    
    # Store original data for fallback
    original_po_df = po_df.copy()
    
    if 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        
        # If no valid dates, return original data
        if po_df.empty:
            return original_po_df
        
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        
        year = st.session_state.get('selected_year')
        quarter = st.session_state.get('selected_quarter')
        
        # Apply year filter with safety check
        if year is not None:
            year_filtered = po_df[po_df['year'] == year]
            if len(year_filtered) >= 5:  # Only apply if we have enough data
                po_df = year_filtered
        
        # Apply quarter filter with safety check
        if quarter and quarter != 'All':
            try:
                quarter_num = int(quarter[1])
                quarter_filtered = po_df[po_df['quarter'] == quarter_num]
                if len(quarter_filtered) >= 5:  # Only apply if we have enough data
                    po_df = quarter_filtered
            except (ValueError, IndexError):
                pass
    
    # Final safety check - if we somehow ended up with no data, return original
    if po_df.empty:
        return original_po_df
    
    return po_df

def check_data_quality(po_df, items_data, suppliers):
    """Check data quality and provide warnings if issues are found"""
    warnings = []
    
    # Check for required columns
    required_po_cols = ['item_id', 'supplier_id', 'quantity', 'unit_price', 'department']
    missing_po_cols = [col for col in required_po_cols if col not in po_df.columns]
    if missing_po_cols:
        warnings.append(f"Missing columns in purchase orders: {missing_po_cols}")
    
    if not items_data.empty:
        required_items_cols = ['item_id', 'category']
        missing_items_cols = [col for col in required_items_cols if col not in items_data.columns]
        if missing_items_cols:
            warnings.append(f"Missing columns in items data: {missing_items_cols}")
    
    if not suppliers.empty:
        required_supplier_cols = ['supplier_id', 'supplier_name']
        missing_supplier_cols = [col for col in required_supplier_cols if col not in suppliers.columns]
        if missing_supplier_cols:
            warnings.append(f"Missing columns in suppliers data: {missing_supplier_cols}")
    
    # Check for data relationships
    if not po_df.empty and not items_data.empty:
        po_items = set(po_df['item_id'].unique())
        items_items = set(items_data['item_id'].unique())
        missing_items = po_items - items_items
        if missing_items:
            warnings.append(f"Purchase orders reference {len(missing_items)} items not found in items data")
    
    if not po_df.empty and not suppliers.empty:
        po_suppliers = set(po_df['supplier_id'].unique())
        suppliers_suppliers = set(suppliers['supplier_id'].unique())
        missing_suppliers = po_suppliers - suppliers_suppliers
        if missing_suppliers:
            warnings.append(f"Purchase orders reference {len(missing_suppliers)} suppliers not found in suppliers data")
    
    # Display warnings if any
    if warnings:
        st.warning("⚠️ Data Quality Issues Found:")
        for warning in warnings:
            st.write(f"• {warning}")
        st.info("💡 Some analytics may not display correctly. Please check your data.")
    
    return len(warnings) == 0

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

def create_template_for_download():
    """Create an Excel template with all required data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct schema
    suppliers_template = pd.DataFrame(columns=[
        'supplier_id', 'supplier_name', 'country', 'region', 'registration_date', 
        'diversity_flag', 'esg_score', 'certifications', 'risk_score', 'city',
        'contact_person', 'email', 'phone', 'payment_terms', 'certification_status', 'lead_time_days'
    ])
    
    items_template = pd.DataFrame(columns=[
        'item_id', 'item_name', 'category', 'unit', 'recyclable_flag', 'carbon_score',
        'unit_price', 'subcategory', 'sustainability_rating', 'supplier_id', 'min_order_quantity', 'lead_time_days'
    ])
    
    purchase_orders_template = pd.DataFrame(columns=[
        'po_id', 'order_date', 'department', 'supplier_id', 'item_id', 'quantity', 
        'unit_price', 'delivery_date', 'currency', 'budget_code', 'total_amount',
        'status', 'priority', 'approval_status'
    ])
    
    contracts_template = pd.DataFrame(columns=[
        'contract_id', 'supplier_id', 'start_date', 'end_date', 'contract_value', 
        'volume_commitment', 'dispute_count', 'compliance_status', 'contract_type', 'renewal_date', 
        'terms_conditions', 'performance_metrics', 'penalty_clauses'
    ])
    
    deliveries_template = pd.DataFrame(columns=[
        'delivery_id', 'po_id', 'delivery_date_actual', 'delivered_quantity', 'defect_flag', 'defect_notes',
        'quantity_delivered', 'quality_score', 'delivery_date', 'on_time_flag', 'carrier',
        'tracking_number', 'delivery_status'
    ])
    
    invoices_template = pd.DataFrame(columns=[
        'invoice_id', 'po_id', 'invoice_date', 'payment_date', 'invoice_amount',
        'amount', 'tax_amount', 'discount_amount', 'payment_status', 'payment_method', 'due_date', 'late_payment_flag'
    ])
    
    budgets_template = pd.DataFrame(columns=[
        'budget_code', 'department', 'category', 'fiscal_year', 'budget_amount', 'amount', 'period', 
        'budget_id', 'allocated_amount', 'spent_amount', 'remaining_amount', 'budget_status', 'approval_date'
    ])
    
    rfqs_template = pd.DataFrame(columns=[
        'rfq_id', 'supplier_id', 'item_id', 'unit_price', 'response_date', 'issue_date',
        'due_date', 'status', 'quantity', 'awarded_supplier_id', 'evaluation_score',
        'technical_score', 'commercial_score'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet (using original sheet names)
        suppliers_template.to_excel(writer, sheet_name='suppliers', index=False)
        items_template.to_excel(writer, sheet_name='items', index=False)
        purchase_orders_template.to_excel(writer, sheet_name='purchase_orders', index=False)
        contracts_template.to_excel(writer, sheet_name='contracts', index=False)
        deliveries_template.to_excel(writer, sheet_name='deliveries', index=False)
        invoices_template.to_excel(writer, sheet_name='invoices', index=False)
        budgets_template.to_excel(writer, sheet_name='budgets', index=False)
        rfqs_template.to_excel(writer, sheet_name='rfqs', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Suppliers', 'Items', 'Purchase_Orders', 'Contracts', 'Deliveries', 'Invoices', 'Budgets', 'RFQs'],
            'Required Fields': [
                'supplier_id, supplier_name, country, region, registration_date, diversity_flag, esg_score, certifications, total_risk_score, city, contact_person, email, phone, payment_terms, certification_status, lead_time_days',
                'item_id, item_name, category, unit, recyclable_flag, carbon_score, unit_price, subcategory, sustainability_rating, supplier_id, min_order_quantity, lead_time_days',
                'po_id, order_date, department, supplier_id, item_id, quantity, unit_price, delivery_date, currency, budget_code, total_amount, status, priority, approval_status',
                'contract_id, supplier_id, start_date, end_date, contract_value, volume_commitment, dispute_count, compliance_status, contract_type, renewal_date, terms_conditions, performance_metrics, penalty_clauses',
                'delivery_id, po_id, delivery_date_actual, delivered_quantity, defect_flag, defect_notes, quantity_delivered, quality_score, delivery_date, on_time_flag, carrier, tracking_number, delivery_status',
                'invoice_id, po_id, invoice_date, payment_date, invoice_amount, amount, tax_amount, discount_amount, payment_status, payment_method, due_date, late_payment_flag',
                'budget_code, department, category, fiscal_year, budget_amount, amount, period, budget_id, allocated_amount, spent_amount, remaining_amount, budget_status, approval_date',
                'rfq_id, supplier_id, item_id, unit_price, response_date, issue_date, due_date, status, quantity, awarded_supplier_id, evaluation_score, technical_score, commercial_score'
            ],
            'Data Types': [
                'Text, Text, Text, Text, Date, Text (Yes/No), Number, Text, Number, Text, Text, Text, Text, Text, Text, Number',
                'Text, Text, Text, Text, Text (Yes/No), Number, Number, Text, Number, Text, Number, Number',
                'Text, Date, Text, Text, Text, Number, Number, Date, Text, Text, Number, Text, Text, Text',
                'Text, Text, Date, Date, Number, Number, Number, Text, Text, Date, Text, Text, Text',
                'Text, Text, Date, Number, Boolean, Text, Number, Number, Date, Boolean, Text, Text, Text',
                'Text, Text, Date, Date, Number, Number, Number, Number, Text, Text, Date, Boolean',
                'Text, Text, Text, Text, Number, Number, Text, Text, Number, Number, Number, Text, Date',
                'Text, Text, Text, Number, Date, Date, Date, Text, Number, Text, Number, Number, Number'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Format the instructions sheet
        instructions_sheet = writer.sheets['Instructions']
        instructions_sheet.set_column('A:C', 30)
        
        # Add a title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#667eea',
            'font_color': 'white',
            'align': 'center'
        })
        
        instructions_sheet.write('A1', 'Procurement Analytics Data Template', title_format)
        instructions_sheet.merge_range('A1:C1', 'Procurement Analytics Data Template', title_format)
    
    output.seek(0)
    return output

def export_data_to_excel():
    """Export all loaded data to Excel"""
    if (st.session_state.purchase_orders.empty and st.session_state.suppliers.empty and 
        st.session_state.items_data.empty and st.session_state.deliveries.empty and 
        st.session_state.invoices.empty and st.session_state.contracts.empty and 
        st.session_state.budgets.empty and st.session_state.rfqs.empty):
        st.warning("No data to export. Please load data first.")
        return None
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each dataset to a separate sheet
        if not st.session_state.suppliers.empty:
            st.session_state.suppliers.to_excel(writer, sheet_name='suppliers', index=False)
        
        if not st.session_state.items_data.empty:
            st.session_state.items_data.to_excel(writer, sheet_name='items', index=False)
        
        if not st.session_state.purchase_orders.empty:
            st.session_state.purchase_orders.to_excel(writer, sheet_name='purchase_orders', index=False)
        
        if not st.session_state.contracts.empty:
            st.session_state.contracts.to_excel(writer, sheet_name='contracts', index=False)
        
        if not st.session_state.deliveries.empty:
            st.session_state.deliveries.to_excel(writer, sheet_name='deliveries', index=False)
        
        if not st.session_state.invoices.empty:
            st.session_state.invoices.to_excel(writer, sheet_name='invoices', index=False)
        
        if not st.session_state.budgets.empty:
            st.session_state.budgets.to_excel(writer, sheet_name='budgets', index=False)
        
        if not st.session_state.rfqs.empty:
            st.session_state.rfqs.to_excel(writer, sheet_name='rfqs', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add summary sheet
        summary_data = {
            'Dataset': ['suppliers', 'items', 'purchase_orders', 'contracts', 'deliveries', 'invoices', 'budgets', 'rfqs'],
            'Records': [
                len(st.session_state.suppliers),
                len(st.session_state.items_data),
                len(st.session_state.purchase_orders),
                len(st.session_state.contracts),
                len(st.session_state.deliveries),
                len(st.session_state.invoices),
                len(st.session_state.budgets),
                len(st.session_state.rfqs)
            ],
            'Status': [
                '✅ Loaded' if not st.session_state.suppliers.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.items_data.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.purchase_orders.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.contracts.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.deliveries.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.invoices.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.budgets.empty else '❌ Empty',
                '✅ Loaded' if not st.session_state.rfqs.empty else '❌ Empty'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format the summary sheet
        summary_sheet = writer.sheets['Summary']
        summary_sheet.set_column('A:C', 20)
        
        # Add a title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#667eea',
            'font_color': 'white',
            'align': 'center'
        })
        
        summary_sheet.write('A1', 'Procurement Analytics Data Export', title_format)
        summary_sheet.merge_range('A1:C1', 'Procurement Analytics Data Export', title_format)
    
    output.seek(0)
    return output

# New PDF Report Generation System - Main Function
# PDF generation function removed as requested

# PDF section generation function removed as requested

# PDF section generation functions removed as requested

def create_comprehensive_process_efficiency(po_df):
    """Create comprehensive process efficiency section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("5. Comprehensive Process Efficiency Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("5.1 Process Efficiency Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_orders = len(po_df)
    avg_processing_time = po_df['processing_time_days'].mean() if 'processing_time_days' in po_df.columns else 0
    total_spend = po_df['total_amount'].sum()
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Purchase Orders', f"{total_orders:,}"],
        ['Average Processing Time', f"{avg_processing_time:.1f} days"],
        ['Total Spend', f"${total_spend:,.2f}"],
        ['Orders per Day', f"{total_orders/30:.1f}" if total_orders > 0 else "0"],
        ['Efficiency Score', f"{(100 - avg_processing_time):.1f}%" if avg_processing_time > 0 else "100%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_compliance_risk(po_df, suppliers_df):
    """Create comprehensive compliance & risk section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("6. Comprehensive Compliance & Risk Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("6.1 Compliance & Risk Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_suppliers = len(suppliers_df) if not suppliers_df.empty else 0
    high_risk_suppliers = len(suppliers_df[suppliers_df['total_risk_score'] > 60]) if 'total_risk_score' in suppliers_df.columns else 0
    compliance_rate = ((total_suppliers - high_risk_suppliers) / total_suppliers * 100) if total_suppliers > 0 else 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Suppliers', f"{total_suppliers:,}"],
        ['High Risk Suppliers', f"{high_risk_suppliers:,}"],
        ['Compliance Rate', f"{compliance_rate:.1f}%"],
        ['Risk Score (Avg)', f"{suppliers_df['total_risk_score'].mean():.1f}" if 'total_risk_score' in suppliers_df.columns else "N/A"],
        ['Risk Level', 'High' if high_risk_suppliers > total_suppliers * 0.2 else 'Medium' if high_risk_suppliers > total_suppliers * 0.1 else 'Low']
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_inventory_management(po_df, items_df):
    """Create comprehensive inventory management section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("7. Comprehensive Inventory Management Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("7.1 Inventory Management Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_items = len(items_df) if not items_df.empty else 0
    total_quantity = po_df['quantity'].sum() if 'quantity' in po_df.columns else 0
    avg_quantity_per_order = po_df['quantity'].mean() if 'quantity' in po_df.columns else 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Items', f"{total_items:,}"],
        ['Total Quantity Ordered', f"{total_quantity:,}"],
        ['Average Quantity per Order', f"{avg_quantity_per_order:.1f}"],
        ['Unique Categories', f"{items_df['category'].nunique()}" if not items_df.empty and 'category' in items_df.columns else "N/A"],
        ['Inventory Turnover', f"{total_quantity/total_items:.1f}" if total_items > 0 else "N/A"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_market_insights(po_df, suppliers_df):
    """Create comprehensive market insights section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("8. Comprehensive Market Insights Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("8.1 Market Insights Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_suppliers = len(suppliers_df) if not suppliers_df.empty else 0
    total_spend = po_df['total_amount'].sum()
    avg_spend_per_supplier = total_spend / total_suppliers if total_suppliers > 0 else 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Suppliers', f"{total_suppliers:,}"],
        ['Total Market Spend', f"${total_spend:,.2f}"],
        ['Average Spend per Supplier', f"${avg_spend_per_supplier:,.2f}"],
        ['Market Concentration', f"{(po_df.groupby('supplier_id')['total_amount'].sum().head(5).sum() / total_spend * 100):.1f}%" if total_spend > 0 else "N/A"],
        ['Supplier Diversity Score', f"{min(100, total_suppliers * 10):.0f}%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_contract_management(po_df, contracts_df):
    """Create comprehensive contract management section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("9. Comprehensive Contract Management Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("9.1 Contract Management Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_contracts = len(contracts_df) if not contracts_df.empty else 0
    active_contracts = len(contracts_df[contracts_df['status'] == 'Active']) if not contracts_df.empty and 'status' in contracts_df.columns else 0
    contract_value = contracts_df['contract_value'].sum() if not contracts_df.empty and 'contract_value' in contracts_df.columns else 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Contracts', f"{total_contracts:,}"],
        ['Active Contracts', f"{active_contracts:,}"],
        ['Total Contract Value', f"${contract_value:,.2f}"],
        ['Average Contract Value', f"${contract_value/total_contracts:,.2f}" if total_contracts > 0 else "$0.00"],
        ['Contract Utilization', f"{(active_contracts/total_contracts*100):.1f}%" if total_contracts > 0 else "0%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_sustainability_csr(po_df, suppliers_df, items_df):
    """Create comprehensive sustainability & CSR section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("10. Comprehensive Sustainability & CSR Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("10.1 Sustainability & CSR Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_suppliers = len(suppliers_df) if not suppliers_df.empty else 0
    sustainable_suppliers = len(suppliers_df[suppliers_df['sustainability_score'] > 7]) if not suppliers_df.empty and 'sustainability_score' in suppliers_df.columns else 0
    sustainability_rate = (sustainable_suppliers / total_suppliers * 100) if total_suppliers > 0 else 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Suppliers', f"{total_suppliers:,}"],
        ['Sustainable Suppliers', f"{sustainable_suppliers:,}"],
        ['Sustainability Rate', f"{sustainability_rate:.1f}%"],
        ['Average Sustainability Score', f"{suppliers_df['sustainability_score'].mean():.1f}" if not suppliers_df.empty and 'sustainability_score' in suppliers_df.columns else "N/A"],
        ['CSR Compliance Rate', f"{sustainability_rate:.1f}%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_process_efficiency_section(po_df):
    """Create process efficiency analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("4. Process Efficiency Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Process efficiency insights
    efficiency_text = """
    <b>Process Efficiency Overview:</b><br/>
    • Procurement cycle time analysis<br/>
    • Process automation opportunities<br/>
    • Efficiency metrics and KPIs<br/>
    • Bottleneck identification<br/>
    <br/>
    <b>Key Recommendations:</b><br/>
    • Implement e-procurement systems<br/>
    • Automate approval workflows<br/>
    • Standardize procurement processes<br/>
    • Reduce manual intervention<br/>
    • Optimize supplier onboarding
    """
    
    story.append(Paragraph(efficiency_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_compliance_risk_section(po_df, suppliers_df):
    """Create compliance and risk analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("5. Compliance & Risk Assessment", title_style))
    story.append(Spacer(1, 12))
    
    # Compliance and risk insights
    compliance_text = """
    <b>Compliance Overview:</b><br/>
    • Policy compliance assessment<br/>
    • Risk identification and scoring<br/>
    • Compliance gap analysis<br/>
    • Risk mitigation strategies<br/>
    <br/>
    <b>Risk Management:</b><br/>
    • Regulatory requirement tracking<br/>
    • Audit readiness assessment<br/>
    • Risk monitoring recommendations<br/>
    • Compliance improvement initiatives
    """
    
    story.append(Paragraph(compliance_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_inventory_management_section(po_df, items_df):
    """Create inventory management analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("6. Inventory Management Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Inventory insights
    inventory_text = """
    <b>Inventory Overview:</b><br/>
    • Inventory turnover analysis<br/>
    • Stock level optimization<br/>
    • Demand forecasting insights<br/>
    • Inventory cost analysis<br/>
    <br/>
    <b>Optimization Opportunities:</b><br/>
    • Stockout risk assessment<br/>
    • Inventory optimization recommendations<br/>
    • Supply chain visibility metrics<br/>
    • Inventory performance KPIs
    """
    
    story.append(Paragraph(inventory_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_market_insights_section(po_df, suppliers_df):
    """Create market insights analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("7. Market Insights Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Market insights
    market_text = """
    <b>Market Overview:</b><br/>
    • Market trend analysis<br/>
    • Competitive intelligence<br/>
    • Price trend monitoring<br/>
    • Supplier market analysis<br/>
    <br/>
    <b>Strategic Insights:</b><br/>
    • Market volatility assessment<br/>
    • Strategic sourcing opportunities<br/>
    • Market risk analysis<br/>
    • Competitive positioning insights
    """
    
    story.append(Paragraph(market_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_contract_management_section(po_df, contracts_df):
    """Create contract management analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("8. Contract Management Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Contract management insights
    contract_text = """
    <b>Contract Overview:</b><br/>
    • Contract performance analysis<br/>
    • Renewal opportunity identification<br/>
    • Contract compliance tracking<br/>
    • Value realization assessment<br/>
    <br/>
    <b>Management Insights:</b><br/>
    • Contract optimization recommendations<br/>
    • Performance metrics analysis<br/>
    • Risk assessment and mitigation<br/>
    • Contract lifecycle management insights
    """
    
    story.append(Paragraph(contract_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_sustainability_csr_section(po_df, suppliers_df, items_df):
    """Create sustainability and CSR analysis section"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("9. Sustainability & CSR Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Sustainability insights
    sustainability_text = """
    <b>Sustainability Overview:</b><br/>
    • ESG performance metrics<br/>
    • Sustainability initiatives tracking<br/>
    • Carbon footprint analysis<br/>
    • Supplier sustainability assessment<br/>
    <br/>
    <b>CSR Impact:</b><br/>
    • CSR program effectiveness<br/>
    • Environmental impact analysis<br/>
    • Social responsibility metrics<br/>
    • Sustainability improvement recommendations
    """
    
    story.append(Paragraph(sustainability_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_comprehensive_spend_analysis(po_df, suppliers_df, items_df):
    """Create comprehensive spend analysis section with all analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("2. Comprehensive Spend Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("2.1 Procurement Spend Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate comprehensive metrics
    total_spend = po_df['quantity'].mul(po_df['unit_price']).sum() if 'quantity' in po_df.columns and 'unit_price' in po_df.columns else po_df['total_amount'].sum()
    total_orders = len(po_df)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0
    unique_suppliers = po_df['supplier_id'].nunique() if 'supplier_id' in po_df.columns else 0
    unique_categories = po_df['item_id'].nunique() if 'item_id' in po_df.columns else 0
    
    # Summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Spend', f"${total_spend:,.2f}"],
        ['Total Orders', f"{total_orders:,}"],
        ['Average Order Value', f"${avg_order_value:,.2f}"],
        ['Unique Suppliers', f"{unique_suppliers:,}"],
        ['Categories', f"{unique_categories:,}"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    # Spend by Category Analysis
    story.append(Paragraph("2.2 Spend by Category Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not items_df.empty and 'category' in items_df.columns:
        # Merge with items to get category information
        po_with_items = po_df.merge(items_df[['item_id', 'category']], on='item_id', how='left')
        category_spend = po_with_items.groupby('category')['total_amount'].sum().sort_values(ascending=False)
        
        if not category_spend.empty:
            # Create enhanced pie chart
            try:
                fig, ax = plt.subplots(figsize=(10, 8))
                colors_list = ['#FF6B35', '#004E89', '#1A936F', '#C6DABF', '#2E86AB', '#E63946', '#457B9D']
                wedges, texts, autotexts = ax.pie(category_spend.values, labels=category_spend.index, 
                                                 autopct='%1.1f%%', colors=colors_list[:len(category_spend)])
                ax.set_title('Spend Distribution by Category', fontsize=16, fontweight='bold', color='#1e3c72')
                plt.tight_layout()
                
                # Save chart
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Category chart generation failed: {str(e)}", styles['Normal']))
            
            # Category spend table
            category_data = [[cat, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"] for cat, amount in category_spend.head(10).items()]
            category_table = Table([['Category', 'Total Spend', 'Percentage']] + category_data)
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(category_table)
            story.append(Spacer(1, 12))
    
    # Spend by Supplier Analysis
    story.append(Paragraph("2.3 Top Suppliers by Spend", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not suppliers_df.empty and 'supplier_id' in po_df.columns:
        supplier_spend = po_df.groupby('supplier_id')['total_amount'].sum().sort_values(ascending=False)
        
        if not supplier_spend.empty:
            # Create enhanced bar chart
            try:
                fig, ax = plt.subplots(figsize=(12, 8))
                top_suppliers = supplier_spend.head(10)
                
                supplier_names = []
                for supplier_id in top_suppliers.index:
                    supplier_name = suppliers_df[suppliers_df['supplier_id'] == supplier_id]['supplier_name'].iloc[0] if len(suppliers_df[suppliers_df['supplier_id'] == supplier_id]) > 0 else f"Supplier {supplier_id}"
                    supplier_names.append(supplier_name)
                
                bars = ax.bar(supplier_names, top_suppliers.values, color='#1f77b4', alpha=0.7)
                ax.set_title('Top 10 Suppliers by Spend', fontsize=16, fontweight='bold', color='#1e3c72')
                ax.set_xlabel('Suppliers', fontsize=12)
                ax.set_ylabel('Total Spend ($)', fontsize=12)
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                
                # Save chart
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Supplier chart generation failed: {str(e)}", styles['Normal']))
            
            # Supplier spend table
            supplier_data = []
            for supplier_id, amount in supplier_spend.head(10).items():
                supplier_name = suppliers_df[suppliers_df['supplier_id'] == supplier_id]['supplier_name'].iloc[0] if len(suppliers_df[suppliers_df['supplier_id'] == supplier_id]) > 0 else f"Supplier {supplier_id}"
                supplier_data.append([supplier_name, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"])
            
            supplier_table = Table([['Supplier', 'Total Spend', 'Percentage']] + supplier_data)
            supplier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(supplier_table)
            story.append(Spacer(1, 12))
    
    # Spend by Department Analysis
    story.append(Paragraph("2.4 Spend by Department", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'department' in po_df.columns:
        dept_spend = po_df.groupby('department')['total_amount'].sum().sort_values(ascending=False)
        
        if not dept_spend.empty:
            # Create department pie chart
            try:
                fig, ax = plt.subplots(figsize=(10, 8))
                colors_list = ['#2E86AB', '#A23B72', '#1A936F', '#88D498', '#FF6B35', '#F7931E']
                wedges, texts, autotexts = ax.pie(dept_spend.values, labels=dept_spend.index, 
                                                 autopct='%1.1f%%', colors=colors_list[:len(dept_spend)])
                ax.set_title('Spend Distribution by Department', fontsize=16, fontweight='bold', color='#1e3c72')
                plt.tight_layout()
                
                # Save chart
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Department chart generation failed: {str(e)}", styles['Normal']))
            
            # Department spend table
            dept_data = [[dept, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"] for dept, amount in dept_spend.items()]
            dept_table = Table([['Department', 'Total Spend', 'Percentage']] + dept_data)
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dept_table)
            story.append(Spacer(1, 12))
    
    # Budget Utilization Analysis
    story.append(Paragraph("2.5 Budget Utilization Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not st.session_state.budgets.empty:
        try:
            budget_analysis, budget_msg = calculate_budget_utilization(po_df, st.session_state.budgets)
            if not budget_analysis.empty:
                # Create budget utilization chart
                fig, ax = plt.subplots(figsize=(12, 8))
                bars = ax.bar(budget_analysis['budget_code'], budget_analysis['utilization_rate'], 
                             color=['#2ca02c' if x <= 90 else '#ff7f0e' if x <= 110 else '#d62728' for x in budget_analysis['utilization_rate']])
                ax.set_title('Budget Utilization Rate by Budget Code', fontsize=16, fontweight='bold', color='#1e3c72')
                ax.set_xlabel('Budget Code', fontsize=12)
                ax.set_ylabel('Utilization Rate (%)', fontsize=12)
                ax.tick_params(axis='x', rotation=45)
                ax.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Target')
                ax.legend()
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                
                # Save chart
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Budget utilization table
                budget_data = []
                for _, row in budget_analysis.iterrows():
                    status = "✅ Under Budget" if row['utilization_rate'] <= 90 else "⚠️ Near Budget" if row['utilization_rate'] <= 110 else "❌ Over Budget"
                    budget_data.append([row['budget_code'], f"${row['budget_amount']:,.2f}", f"${row['actual_spend']:,.2f}", 
                                      f"{row['utilization_rate']:.1f}%", status])
                
                budget_table = Table([['Budget Code', 'Budget Amount', 'Actual Spend', 'Utilization Rate', 'Status']] + budget_data)
                budget_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(budget_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Budget analysis failed: {str(e)}", styles['Normal']))
    
    # Monthly Spend Trend Analysis
    story.append(Paragraph("2.6 Monthly Spend Trend Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'order_date' in po_df.columns:
        try:
            po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
            po_df['month'] = po_df['order_date'].dt.to_period('M')
            monthly_spend = po_df.groupby('month')['total_amount'].sum()
            
            if len(monthly_spend) > 1:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.plot(range(len(monthly_spend)), monthly_spend.values, marker='o', linewidth=3, markersize=8, color='#2ca02c')
                ax.set_title('Monthly Spend Trend', fontsize=16, fontweight='bold', color='#1e3c72')
                ax.set_xlabel('Month', fontsize=12)
                ax.set_ylabel('Total Spend ($)', fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Set x-axis labels
                ax.set_xticks(range(len(monthly_spend)))
                ax.set_xticklabels([str(m) for m in monthly_spend.index], rotation=45)
                
                # Add trend line
                z = np.polyfit(range(len(monthly_spend)), monthly_spend.values, 1)
                p = np.poly1d(z)
                ax.plot(range(len(monthly_spend)), p(range(len(monthly_spend))), "r--", alpha=0.8, label='Trend Line')
                ax.legend()
                
                plt.tight_layout()
                
                # Save chart
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Monthly trend insights
                trend_text = f"""
                <b>Trend Analysis:</b><br/>
                • Average Monthly Spend: ${monthly_spend.mean():,.2f}<br/>
                • Highest Monthly Spend: ${monthly_spend.max():,.2f} ({monthly_spend.idxmax()})<br/>
                • Lowest Monthly Spend: ${monthly_spend.min():,.2f} ({monthly_spend.idxmin()})<br/>
                • Spend Volatility: {monthly_spend.std()/monthly_spend.mean()*100:.1f}%<br/>
                """
                story.append(Paragraph(trend_text, styles['Normal']))
            else:
                story.append(Paragraph("Insufficient data for trend analysis (need at least 2 months)", styles['Normal']))
        except Exception as e:
            story.append(Paragraph(f"Trend analysis failed: {str(e)}", styles['Normal']))
    
    # Tail Spend Analysis
    story.append(Paragraph("2.7 Tail Spend Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    try:
        tail_spend_analysis = calculate_tail_spend(po_df)
        if not tail_spend_analysis.empty:
            # Create Pareto chart for tail spend
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Calculate cumulative percentage
            tail_spend_analysis['cumulative_percentage'] = tail_spend_analysis['cumulative_spend'] / tail_spend_analysis['cumulative_spend'].iloc[-1] * 100
            
            # Create dual-axis plot
            ax2 = ax.twinx()
            
            # Bar chart for spend
            bars = ax.bar(range(len(tail_spend_analysis)), tail_spend_analysis['total_spend'], 
                         color='#1f77b4', alpha=0.7, label='Spend by Supplier')
            
            # Line chart for cumulative percentage
            line = ax2.plot(range(len(tail_spend_analysis)), tail_spend_analysis['cumulative_percentage'], 
                           color='red', linewidth=2, marker='o', label='Cumulative %')
            
            ax.set_title('Pareto Analysis: Tail Spend Distribution', fontsize=16, fontweight='bold', color='#1e3c72')
            ax.set_xlabel('Suppliers (Ranked by Spend)', fontsize=12)
            ax.set_ylabel('Spend ($)', fontsize=12, color='#1f77b4')
            ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12, color='red')
            
            # Add 80/20 line
            ax2.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='80% Threshold')
            
            # Combine legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.tight_layout()
            
            # Save chart
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                chart_path = tmp_file.name
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Add chart to PDF
            img = Image(chart_path, width=8*inch, height=5*inch)
            story.append(img)
            story.append(Spacer(1, 12))
            
            # Store path for cleanup
            if not hasattr(story, '_temp_files'):
                story._temp_files = []
            story._temp_files.append(chart_path)
            
            # Tail spend insights
            top_20_percent = len(tail_spend_analysis) * 0.2
            top_20_spend = tail_spend_analysis.head(int(top_20_percent))['total_spend'].sum()
            total_spend_tail = tail_spend_analysis['total_spend'].sum()
            
            tail_insights = f"""
            <b>Tail Spend Insights:</b><br/>
            • Top 20% of suppliers account for {top_20_spend/total_spend_tail*100:.1f}% of total spend<br/>
            • Bottom 80% of suppliers account for {(total_spend_tail-top_20_spend)/total_spend_tail*100:.1f}% of total spend<br/>
            • Consolidation opportunity: {len(tail_spend_analysis) - int(top_20_percent)} suppliers in tail spend<br/>
            """
            story.append(Paragraph(tail_insights, styles['Normal']))
        else:
            story.append(Paragraph("Insufficient data for tail spend analysis", styles['Normal']))
    except Exception as e:
        story.append(Paragraph(f"Tail spend analysis failed: {str(e)}", styles['Normal']))
    
    story.append(PageBreak())
    return story

def create_comprehensive_spend_analysis_with_plotly(po_df, suppliers_df, items_df):
    """Create comprehensive spend analysis with ALL analytics exactly as shown in the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("2. Comprehensive Spend Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard (exactly as in application)
    story.append(Paragraph("2.1 Procurement Spend Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_spend = po_df['quantity'].mul(po_df['unit_price']).sum() if 'quantity' in po_df.columns and 'unit_price' in po_df.columns else po_df['total_amount'].sum()
    total_orders = len(po_df)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0
    unique_suppliers = po_df['supplier_id'].nunique() if 'supplier_id' in po_df.columns else 0
    unique_categories = po_df['item_id'].nunique() if 'item_id' in po_df.columns else 0
    
    # Create summary metrics table with exact values from application
    summary_data = [
        ['Metric', 'Value'],
        ['Total Spend', f"${total_spend:,.0f}"],
        ['Total Orders', f"{total_orders:,}"],
        ['Average Order Value', f"${avg_order_value:,.0f}"],
        ['Unique Suppliers', f"{unique_suppliers:,}"],
        ['Categories', f"{unique_categories:,}"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    # 2.2 Spend by Category (exactly as in application)
    story.append(Paragraph("2.2 Spend by Category Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not items_df.empty and 'category' in items_df.columns:
        # Use the exact same calculation as in application
        po_with_items = po_df.merge(items_df[['item_id', 'category']], on='item_id', how='left')
        category_spend = po_with_items.groupby('category')['total_amount'].sum().sort_values(ascending=False)
        
        if not category_spend.empty:
            # Create Plotly chart exactly as in application
            try:
                import plotly.express as px
                import plotly.graph_objects as go
                
                # Create the exact same Plotly pie chart as in application
                fig = px.pie(
                    category_spend.reset_index(), 
                    values='total_amount', 
                    names='category', 
                    title='Spend by Category',
                    color_discrete_sequence=['#FF6B35', '#004E89', '#1A936F', '#C6DABF', '#2E86AB', '#E63946', '#457B9D']
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=800, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Category chart generation failed: {str(e)}", styles['Normal']))
            
            # Category spend table with exact data
            category_data = [[cat, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"] for cat, amount in category_spend.head(10).items()]
            category_table = Table([['Category', 'Total Spend', 'Percentage']] + category_data)
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(category_table)
            story.append(Spacer(1, 12))
    
    # 2.3 Spend by Supplier (exactly as in application)
    story.append(Paragraph("2.3 Top Suppliers by Spend", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not suppliers_df.empty and 'supplier_id' in po_df.columns:
        supplier_spend = po_df.groupby('supplier_id')['total_amount'].sum().sort_values(ascending=False)
        
        if not supplier_spend.empty:
            try:
                # Create the exact same Plotly bar chart as in application
                top_suppliers = supplier_spend.head(10)
                supplier_names = []
                for supplier_id in top_suppliers.index:
                    supplier_name = suppliers_df[suppliers_df['supplier_id'] == supplier_id]['supplier_name'].iloc[0] if len(suppliers_df[suppliers_df['supplier_id'] == supplier_id]) > 0 else f"Supplier {supplier_id}"
                    supplier_names.append(supplier_name)
                
                fig = px.bar(
                    x=supplier_names,
                    y=top_suppliers.values,
                    title='Top 10 Suppliers by Spend',
                    color=top_suppliers.values,
                    color_continuous_scale='Blues',
                    text=top_suppliers.values
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                fig.update_traces(
                    texttemplate='$%{text:,.0f}',
                    textposition='outside'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Supplier chart generation failed: {str(e)}", styles['Normal']))
            
            # Supplier spend table with exact data
            supplier_data = []
            for supplier_id, amount in supplier_spend.head(10).items():
                supplier_name = suppliers_df[suppliers_df['supplier_id'] == supplier_id]['supplier_name'].iloc[0] if len(suppliers_df[suppliers_df['supplier_id'] == supplier_id]) > 0 else f"Supplier {supplier_id}"
                supplier_data.append([supplier_name, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"])
            
            supplier_table = Table([['Supplier', 'Total Spend', 'Percentage']] + supplier_data)
            supplier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(supplier_table)
            story.append(Spacer(1, 12))
    
    # 2.4 Spend by Department (exactly as in application)
    story.append(Paragraph("2.4 Spend by Department", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'department' in po_df.columns:
        dept_spend = po_df.groupby('department')['total_amount'].sum().sort_values(ascending=False)
        
        if not dept_spend.empty:
            try:
                # Create the exact same Plotly pie chart as in application
                fig = px.pie(
                    dept_spend.reset_index(), 
                    values='total_amount', 
                    names='department', 
                    title='Spend by Department',
                    color_discrete_sequence=['#2E86AB', '#A23B72', '#1A936F', '#88D498', '#FF6B35', '#F7931E']
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=800, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
            except Exception as e:
                story.append(Paragraph(f"Department chart generation failed: {str(e)}", styles['Normal']))
            
            # Department spend table with exact data
            dept_data = [[dept, f"${amount:,.2f}", f"{(amount/total_spend)*100:.1f}%"] for dept, amount in dept_spend.items()]
            dept_table = Table([['Department', 'Total Spend', 'Percentage']] + dept_data)
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dept_table)
            story.append(Spacer(1, 12))
    
    # 2.5 Budget Utilization (exactly as in application)
    story.append(Paragraph("2.5 Budget Utilization Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not st.session_state.budgets.empty:
        try:
            budget_analysis, budget_msg = calculate_budget_utilization(po_df, st.session_state.budgets)
            if not budget_analysis.empty:
                # Create the exact same Plotly bar chart as in application
                fig = px.bar(
                    budget_analysis, 
                    x='budget_code', 
                    y='utilization_rate', 
                    title='Budget Utilization Rate',
                    color='utilization_rate',
                    color_continuous_scale='RdYlGn',
                    text='utilization_rate'
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Budget utilization table with exact data
                budget_data = []
                for _, row in budget_analysis.iterrows():
                    status = "✅ Under Budget" if row['utilization_rate'] <= 90 else "⚠️ Near Budget" if row['utilization_rate'] <= 110 else "❌ Over Budget"
                    budget_data.append([row['budget_code'], f"${row['budget_amount']:,.2f}", f"${row['actual_spend']:,.2f}", 
                                      f"{row['utilization_rate']:.1f}%", status])
                
                budget_table = Table([['Budget Code', 'Budget Amount', 'Actual Spend', 'Utilization Rate', 'Status']] + budget_data)
                budget_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(budget_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Budget analysis failed: {str(e)}", styles['Normal']))
    
    # 2.6 Monthly Spend Trend (exactly as in application)
    story.append(Paragraph("2.6 Monthly Spend Trend Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'order_date' in po_df.columns:
        try:
            po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
            po_df['month'] = po_df['order_date'].dt.to_period('M')
            monthly_spend = po_df.groupby('month')['total_amount'].sum()
            
            if len(monthly_spend) > 1:
                # Create the exact same Plotly line chart as in application
                monthly_df = monthly_spend.reset_index()
                monthly_df['month'] = monthly_df['month'].astype(str)
                
                fig = px.line(
                    monthly_df,
                    x='month',
                    y='total_amount',
                    title='Monthly Total Spend Trend',
                    markers=True,
                    line_shape='linear'
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=False
                )
                fig.update_traces(line_color='#2E86AB', line_width=3, marker_size=8)
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Monthly trend insights
                trend_text = f"""
                <b>Trend Analysis:</b><br/>
                • Average Monthly Spend: ${monthly_spend.mean():,.2f}<br/>
                • Highest Monthly Spend: ${monthly_spend.max():,.2f} ({monthly_spend.idxmax()})<br/>
                • Lowest Monthly Spend: ${monthly_spend.min():,.2f} ({monthly_spend.idxmin()})<br/>
                • Spend Volatility: {monthly_spend.std()/monthly_spend.mean()*100:.1f}%<br/>
                """
                story.append(Paragraph(trend_text, styles['Normal']))
            else:
                story.append(Paragraph("Insufficient data for trend analysis (need at least 2 months)", styles['Normal']))
        except Exception as e:
            story.append(Paragraph(f"Trend analysis failed: {str(e)}", styles['Normal']))
    
    # 2.7 Category Spend Trends (exactly as in application)
    story.append(Paragraph("2.7 Category Spend Trends Over Time", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not items_df.empty and 'order_date' in po_df.columns:
        try:
            category_trends, category_msg = calculate_category_spend_trends(po_df, items_df)
            if not category_trends.empty:
                # Create the exact same Plotly multi-line chart as in application
                fig = px.line(
                    category_trends,
                    x='month',
                    y='total_spend',
                    color='category',
                    title='Category Spend Trends Over Time',
                    markers=True
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Category trends table
                category_trend_display = category_trends.copy()
                category_trend_display.columns = ['Month', 'Category', 'Total Spend ($)']
                category_trend_display['Total Spend ($)'] = category_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                
                # Create table from the data
                trend_data = []
                for _, row in category_trend_display.head(20).iterrows():  # Show top 20 rows
                    trend_data.append([row['Month'], row['Category'], row['Total Spend ($)']])
                
                trend_table = Table([['Month', 'Category', 'Total Spend ($)']] + trend_data)
                trend_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(trend_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Category trends analysis failed: {str(e)}", styles['Normal']))
    
    # 2.8 Department Spend Trends (exactly as in application)
    story.append(Paragraph("2.8 Department Spend Trends Over Time", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'department' in po_df.columns and 'order_date' in po_df.columns:
        try:
            dept_trends, dept_msg = calculate_department_spend_trends(po_df)
            if not dept_trends.empty:
                # Create the exact same Plotly multi-line chart as in application
                fig = px.line(
                    dept_trends,
                    x='month',
                    y='total_spend',
                    color='department',
                    title='Department Spend Trends Over Time',
                    markers=True
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Department trends table
                dept_trend_display = dept_trends.copy()
                dept_trend_display.columns = ['Month', 'Department', 'Total Spend ($)']
                dept_trend_display['Total Spend ($)'] = dept_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                
                # Create table from the data
                dept_trend_data = []
                for _, row in dept_trend_display.head(20).iterrows():  # Show top 20 rows
                    dept_trend_data.append([row['Month'], row['Department'], row['Total Spend ($)']])
                
                dept_trend_table = Table([['Month', 'Department', 'Total Spend ($)']] + dept_trend_data)
                dept_trend_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(dept_trend_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Department trends analysis failed: {str(e)}", styles['Normal']))
    
    # 2.9 Top Suppliers Spend Trends (exactly as in application)
    story.append(Paragraph("2.9 Top Suppliers Spend Trends", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not suppliers_df.empty and 'order_date' in po_df.columns:
        try:
            supplier_trends, supplier_msg = calculate_supplier_spend_trends(po_df, suppliers_df)
            if not supplier_trends.empty:
                # Create the exact same Plotly multi-line chart as in application
                fig = px.line(
                    supplier_trends,
                    x='month',
                    y='total_spend',
                    color='supplier_name',
                    title='Top Suppliers Spend Trends Over Time',
                    markers=True
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Supplier trends table
                supplier_trend_display = supplier_trends.copy()
                supplier_trend_display.columns = ['Month', 'Supplier', 'Total Spend ($)']
                supplier_trend_display['Total Spend ($)'] = supplier_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                
                # Create table from the data
                supplier_trend_data = []
                for _, row in supplier_trend_display.head(20).iterrows():  # Show top 20 rows
                    supplier_trend_data.append([row['Month'], row['Supplier'], row['Total Spend ($)']])
                
                supplier_trend_table = Table([['Month', 'Supplier', 'Total Spend ($)']] + supplier_trend_data)
                supplier_trend_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(supplier_trend_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Supplier trends analysis failed: {str(e)}", styles['Normal']))
    
    # 2.10 Budget vs Actual Spend Trends (exactly as in application)
    story.append(Paragraph("2.10 Budget vs Actual Spend Trends", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not st.session_state.budgets.empty and 'order_date' in po_df.columns:
        try:
            budget_trends, budget_trend_msg = calculate_budget_spend_trends(po_df, st.session_state.budgets)
            if not budget_trends.empty:
                # Create the exact same Plotly multi-line chart as in application
                fig = px.line(
                    budget_trends,
                    x='month',
                    y='spend_amount',
                    color='budget_code',
                    title='Budget vs Actual Spend Trends Over Time',
                    markers=True
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Spend Amount ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Budget trends table
                budget_trend_display = budget_trends.copy()
                budget_trend_display.columns = ['Month', 'Budget Code', 'Spend Amount ($)']
                budget_trend_display['Spend Amount ($)'] = budget_trend_display['Spend Amount ($)'].apply(lambda x: f"${x:,.0f}")
                
                # Create table from the data
                budget_trend_data = []
                for _, row in budget_trend_display.head(20).iterrows():  # Show top 20 rows
                    budget_trend_data.append([row['Month'], row['Budget Code'], row['Spend Amount ($)']])
                
                budget_trend_table = Table([['Month', 'Budget Code', 'Spend Amount ($)']] + budget_trend_data)
                budget_trend_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(budget_trend_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Budget trends analysis failed: {str(e)}", styles['Normal']))
    
    story.append(PageBreak())
    return story

def create_comprehensive_supplier_performance(po_df, suppliers_df, deliveries_df):
    """Create comprehensive supplier performance section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("3. Comprehensive Supplier Performance & Management", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard (exactly as in application)
    story.append(Paragraph("3.1 Supplier Performance Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_suppliers = suppliers_df['supplier_id'].nunique() if not suppliers_df.empty else 0
    total_deliveries = len(deliveries_df) if not deliveries_df.empty else 0
    defect_count = len(deliveries_df[deliveries_df['defect_flag'] == True]) if not deliveries_df.empty else 0
    defect_rate = (defect_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Create summary metrics table with exact values from application
    summary_data = [
        ['Metric', 'Value'],
        ['Total Suppliers', f"{total_suppliers:,}"],
        ['Total Deliveries', f"{total_deliveries:,}"],
        ['Defect Rate', f"{defect_rate:.1f}%"],
        ['Defect Count', f"{defect_count:,}"],
        ['Quality Score', f"{(100 - defect_rate):.1f}%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    # 3.2 On-Time Delivery Rate (exactly as in application)
    story.append(Paragraph("3.2 On-Time Delivery Performance", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not deliveries_df.empty:
        try:
            delivery_analysis, delivery_msg = calculate_on_time_delivery_rate(po_df, deliveries_df)
            
            if not delivery_analysis.empty:
                # Create the exact same Plotly histogram as in application
                import plotly.express as px
                
                fig = px.histogram(
                    delivery_analysis, 
                    x='on_time', 
                    title='Delivery Performance Distribution',
                    color_discrete_sequence=['#2E86AB'],
                    opacity=0.8
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='On-Time Delivery',
                    yaxis_title='Count'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=800, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Delivery performance insights
                delivery_rate = float(delivery_msg.split('%')[0]) if '%' in delivery_msg else 0
                color = "🟢" if delivery_rate >= 90 else "🟡" if delivery_rate >= 80 else "🔴"
                
                delivery_insights = f"""
                <b>Delivery Performance Insights:</b><br/>
                • {color} On-Time Delivery Rate: {delivery_msg}<br/>
                • Total Deliveries Analyzed: {len(delivery_analysis):,}<br/>
                • Performance Status: {'Excellent' if delivery_rate >= 90 else 'Good' if delivery_rate >= 80 else 'Needs Improvement'}<br/>
                """
                story.append(Paragraph(delivery_insights, styles['Normal']))
        except Exception as e:
            story.append(Paragraph(f"Delivery analysis failed: {str(e)}", styles['Normal']))
    
    # 3.3 Supplier Risk Assessment (exactly as in application)
    story.append(Paragraph("3.3 Supplier Risk Assessment", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'risk_score' in suppliers_df.columns:
        try:
            risk_analysis = calculate_supplier_risk_assessment(
                suppliers_df, 
                st.session_state.purchase_orders if 'purchase_orders' in st.session_state else pd.DataFrame(),
                st.session_state.deliveries if 'deliveries' in st.session_state else None,
                st.session_state.invoices if 'invoices' in st.session_state else None,
                st.session_state.contracts if 'contracts' in st.session_state else None
            )
            
            if not risk_analysis.empty:
                # Create the exact same Plotly bar chart as in application
                fig = px.bar(
                    risk_analysis, 
                    x='risk_level', 
                    y='count', 
                    title='Supplier Risk Distribution',
                    color='risk_level',
                    color_discrete_map={'Low': '#2ca02c', 'Medium': '#ff7f0e', 'High': '#d62728'}
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Risk Level',
                    yaxis_title='Number of Suppliers',
                    showlegend=False
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=800, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Risk assessment table
                risk_data = []
                for _, row in risk_analysis.iterrows():
                    risk_data.append([row['risk_level'], str(row['count']), f"{(row['count']/len(suppliers_df)*100):.1f}%"])
                
                risk_table = Table([['Risk Level', 'Number of Suppliers', 'Percentage']] + risk_data)
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(risk_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Risk assessment failed: {str(e)}", styles['Normal']))
    
    # 3.4 Lead Time Analysis (exactly as in application)
    story.append(Paragraph("3.4 Lead Time Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'lead_time_days' in suppliers_df.columns:
        try:
            lead_time_analysis = calculate_lead_time_analysis(suppliers_df)
            
            if not lead_time_analysis.empty:
                # Create the exact same Plotly histogram as in application
                fig = px.histogram(
                    lead_time_analysis, 
                    x='lead_time_days', 
                    title='Supplier Lead Time Distribution',
                    nbins=20,
                    color_discrete_sequence=['#1f77b4']
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Lead Time (Days)',
                    yaxis_title='Number of Suppliers'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=800, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=7*inch, height=5.5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Lead time insights
                avg_lead_time = suppliers_df['lead_time_days'].mean()
                min_lead_time = suppliers_df['lead_time_days'].min()
                max_lead_time = suppliers_df['lead_time_days'].max()
                
                lead_time_insights = f"""
                <b>Lead Time Analysis:</b><br/>
                • Average Lead Time: {avg_lead_time:.1f} days<br/>
                • Minimum Lead Time: {min_lead_time} days<br/>
                • Maximum Lead Time: {max_lead_time} days<br/>
                • Lead Time Range: {max_lead_time - min_lead_time} days<br/>
                """
                story.append(Paragraph(lead_time_insights, styles['Normal']))
        except Exception as e:
            story.append(Paragraph(f"Lead time analysis failed: {str(e)}", styles['Normal']))
    
    # 3.5 Supplier Defect Rate Analysis (exactly as in application)
    story.append(Paragraph("3.5 Supplier Defect Rate Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not deliveries_df.empty and 'supplier_id' in deliveries_df.columns:
        try:
            defect_analysis = calculate_supplier_defect_rate(po_df, deliveries_df)
            
            if not defect_analysis.empty:
                # Create the exact same Plotly bar chart as in application
                fig = px.bar(
                    defect_analysis.head(10), 
                    x='supplier_name', 
                    y='defect_rate', 
                    title='Top 10 Suppliers by Defect Rate',
                    color='defect_rate',
                    color_continuous_scale='Reds',
                    text='defect_rate'
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Defect rate table
                defect_data = []
                for _, row in defect_analysis.head(10).iterrows():
                    status = "✅ Good" if row['defect_rate'] <= 5 else "⚠️ Moderate" if row['defect_rate'] <= 10 else "❌ Poor"
                    defect_data.append([row['supplier_name'], f"{row['defect_rate']:.1f}%", str(row['total_deliveries']), status])
                
                defect_table = Table([['Supplier', 'Defect Rate', 'Total Deliveries', 'Status']] + defect_data)
                defect_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(defect_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Defect rate analysis failed: {str(e)}", styles['Normal']))
    
    story.append(PageBreak())
    return story

def create_supplier_performance_section(po_df, suppliers_df, deliveries_df):
    """Create supplier performance section content"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("3. Supplier Performance Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # On-time Delivery Rate
    story.append(Paragraph("3.1 On-time Delivery Performance", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not deliveries_df.empty and 'delivery_status' in deliveries_df.columns:
        on_time_deliveries = len(deliveries_df[deliveries_df['delivery_status'] == 'On Time'])
        total_deliveries = len(deliveries_df)
        on_time_rate = (on_time_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
        
        # Create delivery performance chart
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = ['On Time', 'Late']
            sizes = [on_time_deliveries, total_deliveries - on_time_deliveries]
            chart_colors = ['#2ca02c', '#d62728']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=chart_colors)
            ax.set_title('Delivery Performance', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Save chart to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                chart_path = tmp_file.name
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Add chart to PDF
            img = Image(chart_path, width=6*inch, height=4.5*inch)
            story.append(img)
            story.append(Spacer(1, 12))
            
            # Store path for later cleanup
            if not hasattr(story, '_temp_files'):
                story._temp_files = []
            story._temp_files.append(chart_path)
        except Exception as e:
            story.append(Paragraph(f"Chart generation failed: {str(e)}", styles['Normal']))
        
        story.append(Paragraph(f"On-time Delivery Rate: {on_time_rate:.1f}%", styles['Normal']))
        story.append(Paragraph(f"On-time Deliveries: {on_time_deliveries} out of {total_deliveries}", styles['Normal']))
    else:
        story.append(Paragraph("Delivery data not available for analysis", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Supplier Risk Assessment
    story.append(Paragraph("3.2 Supplier Risk Assessment", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if 'total_risk_score' in suppliers_df.columns:
        avg_risk = suppliers_df['total_risk_score'].mean()
        high_risk_suppliers = len(suppliers_df[suppliers_df['total_risk_score'] > 60])
        total_suppliers = len(suppliers_df)
        
        # Create risk distribution chart
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            risk_bins = ['Low (0-30)', 'Medium (30-60)', 'High (60-100)']
            risk_counts = [
                len(suppliers_df[suppliers_df['total_risk_score'] <= 30]),
                len(suppliers_df[(suppliers_df['total_risk_score'] > 30) & (suppliers_df['total_risk_score'] <= 60)]),
                len(suppliers_df[suppliers_df['total_risk_score'] > 60])
            ]
            
            bars = ax.bar(risk_bins, risk_counts, color=['#2ca02c', '#ff7f0e', '#d62728'], alpha=0.7)
            ax.set_title('Supplier Risk Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Risk Level')
            ax.set_ylabel('Number of Suppliers')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       str(int(height)), ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Save chart to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                chart_path = tmp_file.name
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Add chart to PDF
            img = Image(chart_path, width=7*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 12))
            
            # Store path for later cleanup
            if not hasattr(story, '_temp_files'):
                story._temp_files = []
            story._temp_files.append(chart_path)
        except Exception as e:
            story.append(Paragraph(f"Chart generation failed: {str(e)}", styles['Normal']))
        
        story.append(Paragraph(f"Average Risk Score: {avg_risk:.2f}", styles['Normal']))
        story.append(Paragraph(f"High Risk Suppliers (>7): {high_risk_suppliers} out of {total_suppliers}", styles['Normal']))
        
        # Risk distribution table
        risk_data = [[bin_name, count] for bin_name, count in zip(risk_bins, risk_counts)]
        risk_table = Table([['Risk Level', 'Number of Suppliers']] + risk_data)
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
    else:
        story.append(Paragraph("Risk score data not available", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    return story

def create_comprehensive_cost_savings(po_df, rfqs_df):
    """Create comprehensive cost savings section with ALL analytics from the application"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("4. Comprehensive Cost & Savings Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Summary Dashboard
    story.append(Paragraph("4.1 Cost Savings Summary Dashboard", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    # Calculate metrics exactly as in application
    total_spend = po_df['total_amount'].sum()
    total_orders = len(po_df)
    avg_cost_per_po = total_spend / total_orders if total_orders > 0 else 0
    
    if not rfqs_df.empty and 'original_price' in rfqs_df.columns and 'final_price' in rfqs_df.columns:
        rfqs_df['savings'] = rfqs_df['original_price'] - rfqs_df['final_price']
        total_savings = rfqs_df['savings'].sum()
        avg_savings_per_rfq = rfqs_df['savings'].mean()
        savings_percentage = (total_savings / rfqs_df['original_price'].sum()) * 100
    else:
        total_savings = 0
        avg_savings_per_rfq = 0
        savings_percentage = 0
    
    # Create summary metrics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Procurement Cost', f"${total_spend:,.2f}"],
        ['Total Purchase Orders', f"{total_orders:,}"],
        ['Average Cost per PO', f"${avg_cost_per_po:,.2f}"],
        ['Total Cost Savings', f"${total_savings:,.2f}"],
        ['Average Savings per RFQ', f"${avg_savings_per_rfq:,.2f}"],
        ['Savings Percentage', f"{savings_percentage:.1f}%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    # 4.2 Cost Savings from Negotiation
    story.append(Paragraph("4.2 Cost Savings from Negotiation", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not rfqs_df.empty and 'original_price' in rfqs_df.columns and 'final_price' in rfqs_df.columns:
        try:
            savings_analysis = calculate_cost_savings_from_negotiation(po_df, rfqs_df)
            
            if not savings_analysis.empty:
                # Create Plotly chart
                import plotly.express as px
                
                fig = px.bar(
                    savings_analysis.head(10), 
                    x='rfq_id', 
                    y='savings_amount', 
                    title='Top 10 RFQs by Cost Savings',
                    color='savings_amount',
                    color_continuous_scale='Greens',
                    text='savings_amount'
                )
                fig.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='RFQ ID',
                    yaxis_title='Savings Amount ($)',
                    showlegend=False
                )
                fig.update_traces(
                    texttemplate='$%{text:,.0f}',
                    textposition='outside'
                )
                
                # Save Plotly chart as image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    chart_path = tmp_file.name
                fig.write_image(chart_path, width=1000, height=600, scale=2)
                
                # Add chart to PDF
                img = Image(chart_path, width=8*inch, height=5*inch)
                story.append(img)
                story.append(Spacer(1, 12))
                
                # Store path for cleanup
                if not hasattr(story, '_temp_files'):
                    story._temp_files = []
                story._temp_files.append(chart_path)
                
                # Savings analysis table
                savings_data = []
                for _, row in savings_analysis.head(10).iterrows():
                    savings_data.append([row['rfq_id'], f"${row['original_price']:,.2f}", f"${row['final_price']:,.2f}", f"${row['savings_amount']:,.2f}"])
                
                savings_table = Table([['RFQ ID', 'Original Price', 'Final Price', 'Savings']] + savings_data)
                savings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(savings_table)
                story.append(Spacer(1, 12))
        except Exception as e:
            story.append(Paragraph(f"Savings analysis failed: {str(e)}", styles['Normal']))
    
    story.append(PageBreak())
    return story

def create_cost_savings_section(po_df, rfqs_df):
    """Create cost savings section content"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("4. Cost Savings Analysis", title_style))
    story.append(Spacer(1, 12))
    
    # Cost Savings from Negotiation
    story.append(Paragraph("4.1 Cost Savings from Negotiation", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    if not rfqs_df.empty and 'original_price' in rfqs_df.columns and 'final_price' in rfqs_df.columns:
        rfqs_df['savings'] = rfqs_df['original_price'] - rfqs_df['final_price']
        total_savings = rfqs_df['savings'].sum()
        avg_savings_per_rfq = rfqs_df['savings'].mean()
        savings_percentage = (total_savings / rfqs_df['original_price'].sum()) * 100
        
        story.append(Paragraph(f"Total Cost Savings: ${total_savings:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Savings per RFQ: ${avg_savings_per_rfq:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Savings Percentage: {savings_percentage:.1f}%", styles['Normal']))
    else:
        story.append(Paragraph("RFQ data not available for cost savings analysis", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Procurement Cost Analysis
    story.append(Paragraph("4.2 Procurement Cost Analysis", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    total_orders = len(po_df)
    total_spend = po_df['total_amount'].sum()
    avg_cost_per_po = total_spend / total_orders if total_orders > 0 else 0
    
    story.append(Paragraph(f"Total Procurement Cost: ${total_spend:,.2f}", styles['Normal']))
    story.append(Paragraph(f"Average Cost per PO: ${avg_cost_per_po:,.2f}", styles['Normal']))
    story.append(Paragraph(f"Total Purchase Orders: {total_orders:,}", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    return story

def create_recommendations_section():
    """Create recommendations section content"""
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3c72')
    )
    story.append(Paragraph("6. Strategic Recommendations", title_style))
    story.append(Spacer(1, 12))
    
    # Key Recommendations
    story.append(Paragraph("6.1 Key Strategic Recommendations", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    recommendations = [
        "• Implement supplier consolidation strategy to reduce complexity and improve leverage",
        "• Develop category-specific sourcing strategies based on spend analysis",
        "• Establish performance-based supplier evaluation and development programs",
        "• Optimize procurement processes to reduce cycle times and costs",
        "• Enhance risk management through supplier diversification and monitoring",
        "• Leverage data analytics for predictive procurement insights",
        "• Implement sustainability criteria in supplier selection and evaluation",
        "• Develop strategic partnerships with key suppliers for mutual value creation"
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
        story.append(Spacer(1, 3))
    
    story.append(Spacer(1, 12))
    
    return story



# Report generation function removed as requested
def show_report_generation():
    """Display report generation interface - REMOVED"""
    st.info("Report generation functionality has been removed.")

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="Procurement Analytics",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🛒 Procurement Analytics</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'purchase_orders' not in st.session_state:
        st.session_state.purchase_orders = pd.DataFrame()
    if 'suppliers' not in st.session_state:
        st.session_state.suppliers = pd.DataFrame()
    if 'items_data' not in st.session_state:
        st.session_state.items_data = pd.DataFrame()
    if 'deliveries' not in st.session_state:
        st.session_state.deliveries = pd.DataFrame()
    if 'invoices' not in st.session_state:
        st.session_state.invoices = pd.DataFrame()
    if 'contracts' not in st.session_state:
        st.session_state.contracts = pd.DataFrame()
    if 'budgets' not in st.session_state:
        st.session_state.budgets = pd.DataFrame()
    if 'rfqs' not in st.session_state:
        st.session_state.rfqs = pd.DataFrame()
    

    
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
        
        if st.button("💼 Spend Analysis", key="nav_spend_analysis", use_container_width=True):
            st.session_state.current_page = "💰 Spend Analysis"
        
        if st.button("🏢 Supplier Performance", key="nav_supplier_performance", use_container_width=True):
            st.session_state.current_page = "🏭 Supplier Performance"
        
        if st.button("💰 Cost & Savings", key="nav_cost_savings", use_container_width=True):
            st.session_state.current_page = "💵 Cost & Savings"
        
        if st.button("⚡ Process Efficiency", key="nav_process_efficiency", use_container_width=True):
            st.session_state.current_page = "⚡ Process Efficiency"
        
        if st.button("🛡️ Compliance & Risk", key="nav_compliance_risk", use_container_width=True):
            st.session_state.current_page = "📋 Compliance & Risk"
        
        if st.button("📦 Inventory Management", key="nav_inventory_management", use_container_width=True):
            st.session_state.current_page = "📦 Inventory Management"
        
        if st.button("📈 Market Insights", key="nav_market_insights", use_container_width=True):
            st.session_state.current_page = "🌍 Market Insights"
        
        if st.button("📋 Contract Management", key="nav_contract_management", use_container_width=True):
            st.session_state.current_page = "📄 Contract Management"
        
        if st.button("🌿 Sustainability & CSR", key="nav_sustainability_csr", use_container_width=True):
            st.session_state.current_page = "🌱 Sustainability & CSR"
        
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
        

        
        # --- Year and Quarter Filter ---
        po_df = st.session_state.purchase_orders.copy()
        if not po_df.empty and 'order_date' in po_df.columns:
            po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
            po_df = po_df.dropna(subset=['order_date'])
            po_df['year'] = po_df['order_date'].dt.year
            po_df['quarter'] = po_df['order_date'].dt.quarter
            years = sorted(po_df['year'].dropna().unique())
            quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
            
            # Store default values in session state with validation
            if 'selected_year' not in st.session_state:
                st.session_state.selected_year = years[-1] if years else None
            elif st.session_state.selected_year not in years:
                # Reset invalid year selection
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
    
    elif page == "🔮 Predictive Analytics":
        show_predictive_analytics()
    
    elif page == "💰 Spend Analysis":
        show_spend_analysis()
    
    elif page == "🏭 Supplier Performance":
        show_supplier_performance()
    
    elif page == "💵 Cost & Savings":
        show_cost_savings()
    
    elif page == "⚡ Process Efficiency":
        show_process_efficiency()
    
    elif page == "📋 Compliance & Risk":
        show_compliance_risk()
    
    elif page == "📦 Inventory Management":
        show_inventory_management()
    
    elif page == "🌍 Market Insights":
        show_market_insights()
    
    elif page == "📄 Contract Management":
        show_contract_management()
    
    elif page == "🌱 Sustainability & CSR":
        show_sustainability_csr()

def show_home():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">🎯 Welcome to Procurement Analytics</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Transform your procurement data into actionable insights with our comprehensive analytics platform. 
            Get real-time visibility into spend patterns, supplier performance, cost savings opportunities, and more.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Dashboard
    if not st.session_state.purchase_orders.empty:
        total_spend = st.session_state.purchase_orders['quantity'].mul(st.session_state.purchase_orders['unit_price']).sum()
        total_orders = len(st.session_state.purchase_orders)
        unique_suppliers = st.session_state.purchase_orders['supplier_id'].nunique()
        avg_order_value = total_spend / total_orders if total_orders > 0 else 0
        
        st.markdown("### 📊 Quick Overview")
        
        # Modern KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card-blue">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Total Spend</h4>
                        <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">${total_spend:,.0f}</h2>
                    </div>
                    <div style="font-size: 2rem;">💰</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card-purple">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Total Orders</h4>
                        <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{total_orders:,}</h2>
                    </div>
                    <div style="font-size: 2rem;">📋</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card-orange">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Avg Order Value</h4>
                        <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">${avg_order_value:,.0f}</h2>
                    </div>
                    <div style="font-size: 2rem;">📈</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card-teal">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Active Suppliers</h4>
                        <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{unique_suppliers:,}</h2>
                    </div>
                    <div style="font-size: 2rem;">🏭</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Features Overview
    st.markdown("### 🚀 Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">📊 Analytics Modules</h4>
            <ul style="color: #34495e; line-height: 1.8;">
                <li><strong>Spend Analysis:</strong> Category, supplier, and department insights</li>
                <li><strong>Supplier Performance:</strong> Delivery rates, quality metrics</li>
                <li><strong>Cost Savings:</strong> Negotiation opportunities and TCO analysis</li>
                <li><strong>Process Efficiency:</strong> Cycle times and automation metrics</li>
                <li><strong>Compliance & Risk:</strong> Policy adherence and risk assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">🤖 AI-Powered Insights</h4>
            <ul style="color: #34495e; line-height: 1.8;">
                <li><strong>Auto Insights:</strong> Intelligent text summaries and recommendations</li>
                <li><strong>Risk Alerts:</strong> Proactive identification of issues</li>
                <li><strong>Opportunity Detection:</strong> Cost savings and optimization suggestions</li>
                <li><strong>Executive Summary:</strong> High-level overview for decision-makers</li>
                <li><strong>Actionable Recommendations:</strong> Specific steps for improvement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started Guide
    st.markdown("### 🎯 Getting Started")
    
    st.markdown("""
    <div class="chart-container">
        <h4 style="color: #2c3e50; margin-bottom: 15px;">Quick Start Guide</h4>
        <div style="display: flex; align-items: center; margin: 15px 0;">
            <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px;">1</div>
            <div style="flex: 1;">
                <strong>Upload Data:</strong> Go to the "Data Input" tab and upload your procurement data files
            </div>
        </div>
        <div style="display: flex; align-items: center; margin: 15px 0;">
            <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px;">2</div>
            <div style="flex: 1;">
                <strong>Review Insights:</strong> Check the "Auto Insights" tab for AI-generated recommendations
            </div>
        </div>
        <div style="display: flex; align-items: center; margin: 15px 0;">
            <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px;">3</div>
            <div style="flex: 1;">
                <strong>Explore Analytics:</strong> Navigate through different analysis modules for detailed insights
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some spacing for visual balance
    st.markdown("")
    st.markdown("**Template includes:**")
    st.markdown("• 8 data tables in separate sheets")
    st.markdown("• Instructions sheet with field descriptions")
    st.markdown("• Proper column headers and data types")
    
    # Add separator between template section and manual entry


def show_data_input():
    st.markdown("""
    <div class="welcome-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">📝 Data Management</h2>
        <p style="font-size: 1.1rem; color: #34495e; line-height: 1.6;">
            Upload your procurement data files to unlock powerful analytics and insights. 
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
            help="Upload an Excel file with sheets named: Suppliers, Items, Purchase_Orders, Contracts, Deliveries, Invoices, Budgets, RFQs"
        )
        
        if uploaded_complete_dataset is not None:
            try:
                # Read all sheets from the Excel file
                excel_file = pd.ExcelFile(uploaded_complete_dataset)
                
                # Dictionary to store loaded data
                loaded_data = {}
                
                # Expected sheet names
                expected_sheets = {
                    'suppliers': 'suppliers',
                    'items': 'items_data', 
                    'purchase_orders': 'purchase_orders',
                    'contracts': 'contracts',
                    'deliveries': 'deliveries',
                    'invoices': 'invoices',
                    'budgets': 'budgets',
                    'rfqs': 'rfqs'
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
            uploaded_suppliers = st.file_uploader("🏭 Suppliers Data", type=['xlsx', 'csv'], key="suppliers_upload")
            uploaded_items = st.file_uploader("📦 Items Data", type=['xlsx', 'csv'], key="items_upload")
            uploaded_purchase_orders = st.file_uploader("📄 Purchase Orders", type=['xlsx', 'csv'], key="po_upload")
            uploaded_contracts = st.file_uploader("📋 Contracts Data", type=['xlsx', 'csv'], key="contracts_upload")
        
        with col2:
            uploaded_deliveries = st.file_uploader("📦 Deliveries Data", type=['xlsx', 'csv'], key="deliveries_upload")
            uploaded_invoices = st.file_uploader("💰 Invoices Data", type=['xlsx', 'csv'], key="invoices_upload")
            uploaded_budgets = st.file_uploader("💳 Budgets Data", type=['xlsx', 'csv'], key="budgets_upload")
            uploaded_rfqs = st.file_uploader("📋 RFQs Data", type=['xlsx', 'csv'], key="rfqs_upload")
        
        # Process uploaded files with modern success/error styling
        if uploaded_suppliers is not None:
            try:
                if uploaded_suppliers.name.endswith('.csv'):
                    st.session_state.suppliers = pd.read_csv(uploaded_suppliers)
                else:
                    st.session_state.suppliers = pd.read_excel(uploaded_suppliers)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Suppliers data loaded: {len(st.session_state.suppliers)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading suppliers data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_items is not None:
            try:
                if uploaded_items.name.endswith('.csv'):
                    st.session_state.items_data = pd.read_csv(uploaded_items)
                else:
                    st.session_state.items_data = pd.read_excel(uploaded_items)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Items data loaded: {len(st.session_state.items_data)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading items data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_purchase_orders is not None:
            try:
                if uploaded_purchase_orders.name.endswith('.csv'):
                    st.session_state.purchase_orders = pd.read_csv(uploaded_purchase_orders)
                else:
                    st.session_state.purchase_orders = pd.read_excel(uploaded_purchase_orders)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Purchase orders data loaded: {len(st.session_state.purchase_orders)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading purchase orders data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_contracts is not None:
            try:
                if uploaded_contracts.name.endswith('.csv'):
                    st.session_state.contracts = pd.read_csv(uploaded_contracts)
                else:
                    st.session_state.contracts = pd.read_excel(uploaded_contracts)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Contracts data loaded: {len(st.session_state.contracts)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading contracts data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_deliveries is not None:
            try:
                if uploaded_deliveries.name.endswith('.csv'):
                    st.session_state.deliveries = pd.read_csv(uploaded_deliveries)
                else:
                    st.session_state.deliveries = pd.read_excel(uploaded_deliveries)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Deliveries data loaded: {len(st.session_state.deliveries)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading deliveries data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_invoices is not None:
            try:
                if uploaded_invoices.name.endswith('.csv'):
                    st.session_state.invoices = pd.read_csv(uploaded_invoices)
                else:
                    st.session_state.invoices = pd.read_excel(uploaded_invoices)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Invoices data loaded: {len(st.session_state.invoices)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading invoices data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_budgets is not None:
            try:
                if uploaded_budgets.name.endswith('.csv'):
                    st.session_state.budgets = pd.read_csv(uploaded_budgets)
                else:
                    st.session_state.budgets = pd.read_excel(uploaded_budgets)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ Budgets data loaded: {len(st.session_state.budgets)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading budgets data: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if uploaded_rfqs is not None:
            try:
                if uploaded_rfqs.name.endswith('.csv'):
                    st.session_state.rfqs = pd.read_csv(uploaded_rfqs)
                else:
                    st.session_state.rfqs = pd.read_excel(uploaded_rfqs)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ✅ RFQs data loaded: {len(st.session_state.rfqs)} records
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
                    ❌ Error loading RFQs data: {str(e)}
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
            file_name="procurement_analytics_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">Template includes:</h5>
            <ul style="color: #34495e; line-height: 1.6;">
                <li>🏭 <strong>Suppliers:</strong> Supplier information and ESG scores</li>
                <li>📦 <strong>Items:</strong> Product catalog with sustainability data</li>
                <li>📄 <strong>Purchase Orders:</strong> Order details and pricing</li>
                <li>📋 <strong>Contracts:</strong> Contract terms and compliance status</li>
                <li>📦 <strong>Deliveries:</strong> Delivery tracking and quality data</li>
                <li>💰 <strong>Invoices:</strong> Payment and billing information</li>
                <li>💳 <strong>Budgets:</strong> Budget allocation and tracking</li>
                <li>📋 <strong>RFQs:</strong> Request for quote responses</li>
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
        manual_tab1, manual_tab2, manual_tab3, manual_tab4, manual_tab5, manual_tab6, manual_tab7, manual_tab8 = st.tabs([
            "Purchase Orders", "Suppliers", "Items", "Contracts", 
            "Deliveries", "Invoices", "Budgets", "RFQs"
        ])
        
        with manual_tab1:
            st.subheader("Purchase Orders")
            col1, col2 = st.columns(2)
            
            with col1:
                po_id = st.text_input("PO ID", key="po_id_input")
                order_date = st.date_input("Order Date", key="order_date_input")
                department = st.text_input("Department", key="department_input")
                supplier_id = st.text_input("Supplier ID", key="supplier_id_input")
                item_id = st.text_input("Item ID", key="item_id_input")
            
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0, key="quantity_input")
                unit_price = st.number_input("Unit Price", min_value=0.0, key="unit_price_input")
                delivery_date = st.date_input("Delivery Date", key="delivery_date_input")
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CAD"], key="currency_input")
                budget_code = st.text_input("Budget Code", key="budget_code_input")
            
            if st.button("Add Purchase Order"):
                new_po = pd.DataFrame([{
                    'po_id': po_id,
                    'order_date': order_date,
                    'department': department,
                    'supplier_id': supplier_id,
                    'item_id': item_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'delivery_date': delivery_date,
                    'currency': currency,
                    'budget_code': budget_code
                }])
                st.session_state.purchase_orders = pd.concat([st.session_state.purchase_orders, new_po], ignore_index=True)
                st.success("Purchase Order added successfully!")
            
            # Display existing data
            if not st.session_state.purchase_orders.empty:
                st.subheader("Existing Purchase Orders")
                display_dataframe_with_index_1(st.session_state.purchase_orders)
        
        with manual_tab2:
            st.subheader("Suppliers")
            col1, col2 = st.columns(2)
            
            with col1:
                supplier_id = st.text_input("Supplier ID", key="supplier_id_supplier")
                supplier_name = st.text_input("Supplier Name", key="supplier_name_input")
                country = st.text_input("Country", key="country_input")
                region = st.text_input("Region", key="region_input")
            
            with col2:
                registration_date = st.date_input("Registration Date", key="registration_date_input")
                diversity_flag = st.selectbox("Diversity Flag", ["Yes", "No", "Unknown"], key="diversity_flag_input")
                esg_score = st.number_input("ESG Score", min_value=0.0, max_value=100.0, key="esg_score_input")
                certifications = st.text_input("Certifications", key="certifications_input")
            
            if st.button("Add Supplier"):
                new_supplier = pd.DataFrame([{
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'country': country,
                    'region': region,
                    'registration_date': registration_date,
                    'diversity_flag': diversity_flag,
                    'esg_score': esg_score,
                    'certifications': certifications
                }])
                st.session_state.suppliers = pd.concat([st.session_state.suppliers, new_supplier], ignore_index=True)
                st.success("Supplier added successfully!")
            
            # Display existing data
            if not st.session_state.suppliers.empty:
                st.subheader("Existing Suppliers")
                display_dataframe_with_index_1(st.session_state.suppliers)
        
        with manual_tab3:
            st.subheader("Items")
            col1, col2 = st.columns(2)
            
            with col1:
                item_id = st.text_input("Item ID", key="item_id_items")
                item_name = st.text_input("Item Name", key="item_name_input")
                category = st.text_input("Category", key="category_input")
                unit = st.text_input("Unit", key="unit_input")
            
            with col2:
                recyclable_flag = st.selectbox("Recyclable", ["Yes", "No"], key="recyclable_flag_input")
                carbon_score = st.number_input("Carbon Score", min_value=0.0, key="carbon_score_input")
            
            if st.button("Add Item"):
                new_item = pd.DataFrame([{
                    'item_id': item_id,
                    'item_name': item_name,
                    'category': category,
                    'unit': unit,
                    'recyclable_flag': recyclable_flag,
                    'carbon_score': carbon_score
                }])
                st.session_state.items_data = pd.concat([st.session_state.items_data, new_item], ignore_index=True)
                st.success("Item added successfully!")
            
            # Display existing data
            if not st.session_state.items_data.empty:
                st.subheader("Existing Items")
                display_dataframe_with_index_1(st.session_state.items_data)
        
        with manual_tab4:
            st.subheader("Contracts")
            col1, col2 = st.columns(2)
            
            with col1:
                contract_id = st.text_input("Contract ID", key="contract_id_input")
                supplier_id = st.text_input("Supplier ID", key="supplier_id_input3")
                start_date = st.date_input("Start Date", key="start_date_input")
                end_date = st.date_input("End Date", key="end_date_input")
            
            with col2:
                contract_value = st.number_input("Contract Value", min_value=0.0, key="contract_value_input")
                volume_commitment = st.number_input("Volume Commitment", min_value=0, key="volume_commitment_input")
                dispute_count = st.number_input("Dispute Count", min_value=0, key="dispute_count_input")
                compliance_status = st.selectbox("Compliance Status", ["Compliant", "Pending", "Violated"], key="compliance_status_input")
            
            if st.button("Add Contract"):
                new_contract = pd.DataFrame([{
                    'contract_id': contract_id,
                    'supplier_id': supplier_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'contract_value': contract_value,
                    'volume_commitment': volume_commitment,
                    'dispute_count': dispute_count,
                    'compliance_status': compliance_status
                }])
                st.session_state.contracts = pd.concat([st.session_state.contracts, new_contract], ignore_index=True)
                st.success("Contract added successfully!")
            
            # Display existing data
            if not st.session_state.contracts.empty:
                st.subheader("Existing Contracts")
                display_dataframe_with_index_1(st.session_state.contracts)
        
        with manual_tab5:
            st.subheader("Deliveries")
            col1, col2 = st.columns(2)
            
            with col1:
                delivery_id = st.text_input("Delivery ID", key="delivery_id_input")
                po_id = st.text_input("PO ID", key="po_id_input2")
                delivery_date = st.date_input("Delivery Date", key="delivery_date_input2")
                delivered_quantity = st.number_input("Delivered Quantity", min_value=0, key="delivered_quantity_input")
            
            with col2:
                defect_flag = st.checkbox("Defect Flag", key="defect_flag_input")
                defect_notes = st.text_input("Defect Notes", key="defect_notes_input")
            
            if st.button("Add Delivery"):
                new_delivery = pd.DataFrame([{
                    'delivery_id': delivery_id,
                    'po_id': po_id,
                    'delivery_date': delivery_date,
                    'delivered_quantity': delivered_quantity,
                    'defect_flag': defect_flag,
                    'defect_notes': defect_notes
                }])
                st.session_state.deliveries = pd.concat([st.session_state.deliveries, new_delivery], ignore_index=True)
                st.success("Delivery added successfully!")
            
            # Display existing data
            if not st.session_state.deliveries.empty:
                st.subheader("Existing Deliveries")
                display_dataframe_with_index_1(st.session_state.deliveries)
        
        with manual_tab6:
            st.subheader("Invoices")
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_id = st.text_input("Invoice ID", key="invoice_id_input")
                po_id = st.text_input("PO ID", key="po_id_input3")
                invoice_date = st.date_input("Invoice Date", key="invoice_date_input")
            
            with col2:
                payment_date = st.date_input("Payment Date", key="payment_date_input")
                invoice_amount = st.number_input("Invoice Amount", min_value=0.0, key="invoice_amount_input")
            
            if st.button("Add Invoice"):
                new_invoice = pd.DataFrame([{
                    'invoice_id': invoice_id,
                    'po_id': po_id,
                    'invoice_date': invoice_date,
                    'payment_date': payment_date,
                    'invoice_amount': invoice_amount
                }])
                st.session_state.invoices = pd.concat([st.session_state.invoices, new_invoice], ignore_index=True)
                st.success("Invoice added successfully!")
            
            # Display existing data
            if not st.session_state.invoices.empty:
                st.subheader("Existing Invoices")
                display_dataframe_with_index_1(st.session_state.invoices)
        
        with manual_tab7:
            st.subheader("Budgets")
            col1, col2 = st.columns(2)
            
            with col1:
                budget_code = st.text_input("Budget Code", key="budget_code_input2")
                department = st.text_input("Department", key="department_input2")
                category = st.text_input("Category", key="category_input2")
            
            with col2:
                fiscal_year = st.text_input("Fiscal Year", key="fiscal_year_input")
                budget_amount = st.number_input("Budget Amount", min_value=0.0, key="budget_amount_input")
            
            if st.button("Add Budget"):
                new_budget = pd.DataFrame([{
                    'budget_code': budget_code,
                    'department': department,
                    'category': category,
                    'fiscal_year': fiscal_year,
                    'budget_amount': budget_amount
                }])
                st.session_state.budgets = pd.concat([st.session_state.budgets, new_budget], ignore_index=True)
                st.success("Budget added successfully!")
            
            # Display existing data
            if not st.session_state.budgets.empty:
                st.subheader("Existing Budgets")
                display_dataframe_with_index_1(st.session_state.budgets)
        
        with manual_tab8:
            st.subheader("RFQs")
            col1, col2 = st.columns(2)
            
            with col1:
                rfq_id = st.text_input("RFQ ID", key="rfq_id_input")
                supplier_id = st.text_input("Supplier ID", key="supplier_id_input4")
                item_id = st.text_input("Item ID", key="item_id_input3")
            
            with col2:
                unit_price = st.number_input("Unit Price", min_value=0.0, key="unit_price_input2")
                response_date = st.date_input("Response Date", key="response_date_input")
            
            if st.button("Add RFQ"):
                new_rfq = pd.DataFrame([{
                    'rfq_id': rfq_id,
                    'supplier_id': supplier_id,
                    'item_id': item_id,
                    'unit_price': unit_price,
                    'response_date': response_date
                }])
                st.session_state.rfqs = pd.concat([st.session_state.rfqs, new_rfq], ignore_index=True)
                st.success("RFQ added successfully!")
            
            # Display existing data
            if not st.session_state.rfqs.empty:
                st.subheader("Existing RFQs")
                display_dataframe_with_index_1(st.session_state.rfqs)
    
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
                # Import the sample data generation function
                from generate_sample_data import generate_sample_data
                
                # Generate sample data
                sample_data = generate_sample_data()
                
                # Extract DataFrames from tuple
                purchase_orders, suppliers, items_data, deliveries, invoices, contracts, budgets, rfqs = sample_data
                
                # Update session state
                st.session_state.purchase_orders = purchase_orders
                st.session_state.suppliers = suppliers
                st.session_state.items_data = items_data
                st.session_state.deliveries = deliveries
                st.session_state.invoices = invoices
                st.session_state.contracts = contracts
                st.session_state.budgets = budgets
                st.session_state.rfqs = rfqs
                
                # Show success message
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                            padding: 20px; border-radius: 12px; margin: 20px 0; color: white;">
                    <h4 style="color: white; margin: 0 0 10px 0;">✅ Sample Data Loaded Successfully!</h4>
                    <p style="margin: 0; opacity: 0.9;">
                        📊 Purchase Orders: {len(purchase_orders)} records<br>
                        🏢 Suppliers: {len(suppliers)} records<br>
                        📦 Items: {len(items_data)} records<br>
                        🚚 Deliveries: {len(deliveries)} records<br>
                        💰 Invoices: {len(invoices)} records<br>
                        📋 Contracts: {len(contracts)} records<br>
                        💳 Budgets: {len(budgets)} records<br>
                        📝 RFQs: {len(rfqs)} records
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.success("🎉 You can now explore all analytics features with the sample data!")
                
            except Exception as e:
                st.error(f"❌ Error loading sample data: {str(e)}")
                st.info("💡 Make sure the generate_sample_data.py file is available in the same directory.")
        
        # Data preview section
        st.markdown("### 👀 Sample Data Preview")
        
        if not st.session_state.purchase_orders.empty:
            st.markdown("**📊 Purchase Orders Preview:**")
            st.dataframe(st.session_state.purchase_orders.head(), use_container_width=True)
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
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Suppliers</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.suppliers):,}</h2>
                </div>
                <div style="font-size: 2rem;">🏭</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-purple">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Items</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.items_data):,}</h2>
                </div>
                <div style="font-size: 2rem;">📦</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-orange">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Purchase Orders</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.purchase_orders):,}</h2>
                </div>
                <div style="font-size: 2rem;">📄</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-teal">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Contracts</h4>
                    <h2 style="margin: 5px 0; font-size: 1.8rem; font-weight: 700;">{len(st.session_state.contracts):,}</h2>
                </div>
                <div style="font-size: 2rem;">📋</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Export data section
    st.markdown("### 📤 Export Data")
    
    if (not st.session_state.purchase_orders.empty or not st.session_state.suppliers.empty or 
        not st.session_state.items_data.empty or not st.session_state.deliveries.empty or 
        not st.session_state.invoices.empty or not st.session_state.contracts.empty or 
        not st.session_state.budgets.empty or not st.session_state.rfqs.empty):
        
        export_output = export_data_to_excel()
        
        st.download_button(
            label="📤 Export All Data",
            data=export_output.getvalue(),
            file_name=f"procurement_analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
            <h5 style="color: #2c3e50; margin-bottom: 10px;">📄 Purchase Orders</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.purchase_orders.empty:
            display_dataframe_with_index_1(st.session_state.purchase_orders, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No purchase order data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">🏭 Suppliers</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.suppliers.empty:
            display_dataframe_with_index_1(st.session_state.suppliers, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No supplier data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">📦 Items</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.items_data.empty:
            display_dataframe_with_index_1(st.session_state.items_data, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No item data available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">💰 Budgets</h5>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.budgets.empty:
            display_dataframe_with_index_1(st.session_state.budgets, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-container">
                <p style="color: #6b7280; text-align: center; margin: 0;">No budget data available</p>
            </div>
            """, unsafe_allow_html=True)


def show_auto_insights():
    st.header("🤖 Auto Insights & AI-Powered Analysis")
    
    # Check if we have sufficient data
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section to generate insights.")
        return
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Initialize insights generator
    insights_generator = ProcurementInsights(
        purchase_orders=po_df,
        suppliers=st.session_state.suppliers,
        items_data=st.session_state.items_data,
        deliveries=st.session_state.deliveries,
        invoices=st.session_state.invoices,
        contracts=st.session_state.contracts,
        budgets=st.session_state.budgets,
        rfqs=st.session_state.rfqs
    )
    
    # Executive Summary
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 24px; border-radius: 12px; margin: 24px 0; color: white;">
        <h2 style="color: white; margin: 0 0 12px 0; font-size: 1.5rem; font-weight: 600;">📊 Executive Summary</h2>
        <p style="margin: 0; font-size: 1rem; opacity: 0.9;">AI-generated insights and recommendations for procurement optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate and display executive summary
    executive_summary = insights_generator.generate_executive_summary()
    display_insights_section(executive_summary, "Executive Summary", "📊")
    
    # Detailed Insights Sections
    st.markdown("## 📋 Detailed Analysis")
    
    # Create tabs for different insight categories
    insight_tab1, insight_tab2, insight_tab3, insight_tab4, insight_tab5, insight_tab6 = st.tabs([
        "💰 Spend Insights", "🏭 Supplier Performance", "💡 Cost Savings", 
        "⚡ Process Efficiency", "⚠️ Risk & Compliance", "🌱 Sustainability"
    ])
    
    with insight_tab1:
        spend_insights = insights_generator.generate_spend_insights()
        display_insights_section(spend_insights, "Spend Analysis Insights", "💰")
        
        # Add actionable recommendations
        st.markdown("### Actionable Recommendations")
        if "High spend concentration" in spend_insights:
            st.markdown("""
            **Immediate Actions:**
            - Review supplier contracts for high-spend categories
            - Develop category strategies for spend optimization
            - Consider supplier diversification to reduce risk
            """)
    
    with insight_tab2:
        supplier_insights = insights_generator.generate_supplier_performance_insights()
        display_insights_section(supplier_insights, "Supplier Performance Insights", "🏭")
        
        # Add performance improvement suggestions
        st.markdown("### Performance Improvement")
        if "Performance Issue" in supplier_insights:
            st.markdown("""
            **Recommended Actions:**
            - Schedule performance review meetings with underperforming suppliers
            - Implement supplier development programs
            - Establish clear performance metrics and SLAs
            """)
    
    with insight_tab3:
        cost_insights = insights_generator.generate_cost_savings_insights()
        display_insights_section(cost_insights, "Cost Savings Opportunities", "💡")
        
        # Add cost optimization strategies
        st.markdown("### Cost Optimization Strategies")
        if "Negotiation Opportunity" in cost_insights:
            st.markdown("""
            **Strategic Actions:**
            - Leverage competitive quotes for price negotiations
            - Implement volume consolidation strategies
            - Explore alternative suppliers for high-cost items
            """)
    
    with insight_tab4:
        process_insights = insights_generator.generate_process_efficiency_insights()
        display_insights_section(process_insights, "Process Efficiency Analysis", "⚡")
        
        # Add process improvement recommendations
        st.markdown("### Process Improvements")
        if "Process Inconsistency" in process_insights:
            st.markdown("""
            **Optimization Actions:**
            - Standardize procurement processes across departments
            - Implement order consolidation strategies
            - Review and optimize payment cycles
            """)
    
    with insight_tab5:
        risk_insights = insights_generator.generate_compliance_risk_insights()
        display_insights_section(risk_insights, "Risk & Compliance Assessment", "⚠️")
        
        # Add risk mitigation strategies
        st.markdown("### Risk Mitigation")
        if "Contract Compliance" in risk_insights or "Policy Violation" in risk_insights:
            st.markdown("""
            **Risk Management Actions:**
            - Review and update compliance policies
            - Implement automated compliance monitoring
            - Develop supplier risk assessment frameworks
            """)
    
    with insight_tab6:
        sustainability_insights = insights_generator.generate_sustainability_insights()
        display_insights_section(sustainability_insights, "Sustainability & CSR Analysis", "🌱")
        
        # Add sustainability improvement strategies
        st.markdown("### Sustainability Goals")
        if "Sustainability Opportunity" in sustainability_insights:
            st.markdown("""
            **Sustainability Actions:**
            - Develop supplier sustainability programs
            - Increase procurement of eco-friendly products
            - Implement diversity supplier programs
            """)
    
    # AI Recommendations Section
    st.markdown("## 🤖 AI-Powered Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### High Priority Actions")
        st.markdown("""
        - **Immediate**: Review high-spend concentration risks
        - **Short-term**: Address supplier performance issues
        - **Medium-term**: Implement cost optimization strategies
        """)

    with col2:
        st.markdown("### Strategic Opportunities")
        st.markdown("""
        - **Process**: Automate procurement workflows
        - **Savings**: Leverage volume discounts
        - **Risk**: Diversify supplier base
        """)
    
    # Data Quality Assessment
    st.markdown("## 📊 Data Quality Assessment")
    
    data_quality_score = 0
    data_issues = []
    
    if not st.session_state.purchase_orders.empty:
        data_quality_score += 25
    else:
        data_issues.append("Missing purchase order data")
    
    if not st.session_state.suppliers.empty:
        data_quality_score += 25
    else:
        data_issues.append("Missing supplier data")
    
    if not st.session_state.items_data.empty:
        data_quality_score += 25
    else:
        data_issues.append("Missing item data")
    
    if not st.session_state.deliveries.empty:
        data_quality_score += 25
    else:
        data_issues.append("Missing delivery data")
    
    # Display data quality score
    quality_color = "🟢" if data_quality_score >= 75 else "🟡" if data_quality_score >= 50 else "🔴"
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3c72; margin: 10px 0;">
        <h3 style="margin: 0; color: #333;">{quality_color} Data Quality Score: {data_quality_score}%</h3>
        <p style="margin: 5px 0 0 0; color: #666;">Higher quality data enables more accurate insights and recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    if data_issues:
        st.markdown("### Data Improvement Opportunities")
        for issue in data_issues:
            st.markdown(f"- {issue}")


def show_predictive_analytics():
    """Display the predictive analytics dashboard."""
    # Check if data is available
    if st.session_state.purchase_orders.empty:
        st.warning("⚠️ No purchase order data available. Please upload data in the Data Input section.")
        return
    
    # Display predictive analytics dashboard
    display_procurement_predictive_analytics_dashboard(
        st.session_state.purchase_orders,
        st.session_state.suppliers,
        st.session_state.items_data,
        st.session_state.deliveries,
        st.session_state.invoices,
        st.session_state.contracts,
        st.session_state.budgets,
        st.session_state.rfqs
    )


def show_spend_analysis():
    st.header("💰 Spend Analysis")
    
    # Check if data exists
    if st.session_state.purchase_orders.empty:
        st.error("❌ No purchase order data available. Please load data first.")
        st.info("💡 Go to 'Data Input' section and click 'Load Sample Data' or upload your own data.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="spend_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="spend_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Ensure we have data to work with
    if po_df.empty:
        st.error("❌ No purchase order data available. Please load data first.")
        st.info("💡 Go to 'Data Input' section to upload or load sample data.")
        return
    
    # Summary Dashboard with professional styling
    total_spend = po_df['quantity'].mul(po_df['unit_price']).sum()
    total_orders = len(po_df)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0
    unique_suppliers = po_df['supplier_id'].nunique()
    unique_categories = po_df['item_id'].nunique()
    
    st.markdown("""
    <div class="summary-dashboard">
        <h3 style="color: #1e3c72; margin: 0; text-align: center; font-weight: bold;">📈 Procurement Spend Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Spend</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${total_spend:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown(f"""
        <div class="metric-card-red">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Orders</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_orders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown(f"""
        <div class="metric-card-orange">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg Order Value</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_order_value:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown(f"""
        <div class="metric-card-teal">
            <h4 style="color: white; margin: 0; font-size: 14px;">Unique Suppliers</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{unique_suppliers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        st.markdown(f"""
        <div class="metric-card-green">
            <h4 style="color: white; margin: 0; font-size: 14px;">Categories</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{unique_categories:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Spend by Category")
        category_spend, total_spend_msg = calculate_spend_by_category(po_df, st.session_state.items_data)
        
        if not category_spend.empty:
            # Enhanced metric with color coding
            spend_value = float(total_spend_msg.replace('$', '').replace(',', '')) if '$' in total_spend_msg else 0
            color = "🟢" if spend_value >= 1000000 else "🟡" if spend_value >= 500000 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3c72; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Total Spend: {total_spend_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced pie chart with professional colors
            fig_category = px.pie(
                category_spend, 
                values='total_spend', 
                names='category', 
                title='Spend by Category',
                color_discrete_sequence=['#FF6B35', '#004E89', '#1A936F', '#C6DABF', '#2E86AB', '#E63946', '#457B9D']
            )
            fig_category.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                showlegend=True,
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            st.plotly_chart(fig_category, use_container_width=True, key="spend_category_chart")
            
            with st.expander("📊 Category Spend Data"):
                display_dataframe_with_index_1(category_spend)
        else:
            st.error(f"❌ Category Analysis Error: {total_spend_msg}")
            st.info("💡 Make sure you have items data with 'item_id' and 'category' columns")
    
    with col2:
        st.subheader("🏭 Spend by Supplier")
        supplier_spend, supplier_msg = calculate_spend_by_supplier(po_df, st.session_state.suppliers)
        if not supplier_spend.empty:
            # Enhanced metric with color coding
            supplier_spend_value = float(supplier_msg.replace('$', '').replace(',', '')) if '$' in supplier_msg else 0
            color = "🟢" if supplier_spend_value >= 1000000 else "🟡" if supplier_spend_value >= 500000 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #E63946; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Total Spend: {supplier_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced bar chart with professional colors
            fig_supplier = px.bar(
                supplier_spend.head(10), 
                x='supplier_name', 
                y='total_spend', 
                title='Top 10 Suppliers by Spend',
                color='total_spend',
                color_continuous_scale='Blues',
                text='total_spend'
            )
            fig_supplier.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_tickangle=-45,
                showlegend=False
            )
            fig_supplier.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            )
            st.plotly_chart(fig_supplier, use_container_width=True, key="spend_supplier_chart")
            
            with st.expander("📊 Supplier Spend Data"):
                display_dataframe_with_index_1(supplier_spend)
        else:
            st.error(f"❌ Supplier Analysis Error: {supplier_msg}")
            st.info("💡 Make sure you have suppliers data with 'supplier_id' and 'supplier_name' columns")
    
    # Additional metrics
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏢 Spend by Department")
        dept_spend, dept_msg = calculate_spend_by_department(po_df)
        
        if not dept_spend.empty:
            # Enhanced metric with color coding
            dept_spend_value = float(dept_msg.replace('$', '').replace(',', '')) if '$' in dept_msg else 0
            color = "🟢" if dept_spend_value >= 1000000 else "🟡" if dept_spend_value >= 500000 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #FF6B35; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Total Spend: {dept_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced pie chart with professional colors
            fig_dept = px.pie(
                dept_spend, 
                values='total_spend', 
                names='department', 
                title='Spend by Department',
                color_discrete_sequence=['#2E86AB', '#A23B72', '#1A936F', '#88D498', '#FF6B35', '#F7931E']
            )
            fig_dept.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                showlegend=True,
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            st.plotly_chart(fig_dept, use_container_width=True, key="spend_dept_chart")
            
            with st.expander("📊 Department Spend Data"):
                display_dataframe_with_index_1(dept_spend)
        else:
            st.error(f"❌ Department Analysis Error: {dept_msg}")
            st.info("💡 Make sure your purchase orders have 'department', 'quantity', and 'unit_price' columns")
    
    with col4:
        st.subheader("📈 Budget Utilization")
        if not st.session_state.budgets.empty:
            budget_analysis, budget_msg = calculate_budget_utilization(po_df, st.session_state.budgets)
            if not budget_analysis.empty:
                # Enhanced metric with color coding
                avg_utilization = budget_analysis['utilization_rate'].mean()
                color = "🟢" if avg_utilization <= 90 else "🟡" if avg_utilization <= 110 else "🔴"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2E86AB; margin: 10px 0;">
                    <h3 style="margin: 0; color: #333;">{color} Budget Utilization: {budget_msg}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced bar chart with professional colors
                fig_budget = px.bar(
                    budget_analysis, 
                    x='budget_code', 
                    y='utilization_rate', 
                    title='Budget Utilization Rate',
                    color='utilization_rate',
                    color_continuous_scale='RdYlGn',
                    text='utilization_rate'
                )
                fig_budget.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                fig_budget.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                st.plotly_chart(fig_budget, use_container_width=True, key="spend_budget_chart")
                
                with st.expander("📊 Budget Utilization Data"):
                    display_dataframe_with_index_1(budget_analysis)
        else:
            st.info("Add budget data to see utilization analysis")
    
    # Tail spend analysis
    st.subheader("🔍 Tail Spend Analysis (Pareto Chart)")
    tail_spend, tail_msg = calculate_tail_spend(po_df, st.session_state.suppliers)
    if not tail_spend.empty:
        st.metric("Tail Spend", tail_msg)
        
        # Create Pareto chart with required variables
        # Sort by total_spend in descending order
        pareto_data = tail_spend.sort_values('total_spend', ascending=False).copy()
        
        # Create required variables for Pareto chart
        pareto_data['cumulative_spend'] = pareto_data['total_spend'].cumsum()  # Cumulative sum of spend
        pareto_data['cumulative_percent'] = (pareto_data['cumulative_spend'] / pareto_data['total_spend'].sum()) * 100  # Cumulative percentage
        
        # Create Pareto chart with dual y-axis
        fig_pareto = go.Figure()
        
        # Add bar chart for individual spend
        fig_pareto.add_trace(go.Bar(
            x=pareto_data['supplier_name'],  # Use supplier names on X-axis
            y=pareto_data['total_spend'],
            name='Individual Spend',
            yaxis='y',
            marker_color='lightblue'
        ))
        
        # Add cumulative percentage line
        fig_pareto.add_trace(go.Scatter(
            x=pareto_data['supplier_name'],
            y=pareto_data['cumulative_percent'],
            name='Cumulative %',
            yaxis='y2',
            line=dict(color='#E63946', width=3),
            mode='lines+markers',
            marker=dict(size=8, color='#E63946')
        ))
        
        # Update layout for dual y-axis
        fig_pareto.update_layout(
            title='Pareto Chart: Tail Spend Analysis',
            title_font_size=18,
            title_font_color='#1e3c72',
            xaxis=dict(title='Suppliers (Ranked by Spend)', tickangle=45),
            yaxis=dict(title='Individual Spend ($)', side='left'),
            yaxis2=dict(title='Cumulative Percentage (%)', side='right', overlaying='y', range=[0, 100]),
            showlegend=True,
            legend=dict(bgcolor='rgba(255,255,255,0.8)')
        )
        
        st.plotly_chart(fig_pareto, use_container_width=True, key="spend_pareto_chart")
        
        # Add insights
        if len(pareto_data) >= 10:
            top_20_percent = int(len(pareto_data) * 0.2)
            top_20_spend = pareto_data.iloc[:top_20_percent]['total_spend'].sum()
            top_20_percentage = (top_20_spend / pareto_data['total_spend'].sum()) * 100
            
            st.info(f"💡 **Pareto Analysis**: Top {top_20_percent} suppliers (20%) account for {top_20_percentage:.1f}% of total spend")
        
        # Show Pareto chart data table
        st.subheader("📊 Pareto Chart Data")
        pareto_display = pareto_data[['supplier_name', 'total_spend', 'cumulative_spend', 'cumulative_percent']].copy()
        pareto_display.columns = ['Supplier Name', 'Individual Spend ($)', 'Cumulative Spend ($)', 'Cumulative %']
        display_dataframe_with_index_1(pareto_display)
    
    # Spend Trend Analysis Section
    st.markdown("---")
    st.subheader("📈 Spend Trend Analysis")
    
    # Check if we have date data for trend analysis
    if 'order_date' in po_df.columns:
        # Monthly Total Spend Trend
        st.markdown("### 📊 Monthly Total Spend Trend")
        monthly_trends, monthly_msg = calculate_spend_trends(po_df)
        if not monthly_trends.empty:
            # Create line chart for monthly spend trends
            fig_monthly = px.line(
                monthly_trends,
                x='month',
                y='total_spend',
                title='Monthly Total Spend Trend',
                markers=True,
                line_shape='linear'
            )
            fig_monthly.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_title='Month',
                yaxis_title='Total Spend ($)',
                showlegend=False
            )
            fig_monthly.update_traces(line_color='#2E86AB', line_width=3, marker_size=8)
            st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_spend_trend")
            
            with st.expander("📊 Monthly Spend Data"):
                monthly_display = monthly_trends.copy()
                monthly_display.columns = ['Month', 'Total Spend ($)']
                monthly_display['Total Spend ($)'] = monthly_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                display_dataframe_with_index_1(monthly_display)
        else:
            st.info("No monthly trend data available")
        
        # Category Spend Trends
        if not st.session_state.items_data.empty:
            st.markdown("### 🏷️ Category Spend Trends Over Time")
            category_trends, category_msg = calculate_category_spend_trends(po_df, st.session_state.items_data)
            if not category_trends.empty:
                # Create multi-line chart for category trends
                fig_category_trends = px.line(
                    category_trends,
                    x='month',
                    y='total_spend',
                    color='category',
                    title='Category Spend Trends Over Time',
                    markers=True
                )
                fig_category_trends.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                st.plotly_chart(fig_category_trends, use_container_width=True, key="category_spend_trends")
                
                with st.expander("📊 Category Trend Data"):
                    category_trend_display = category_trends.copy()
                    category_trend_display.columns = ['Month', 'Category', 'Total Spend ($)']
                    category_trend_display['Total Spend ($)'] = category_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                    display_dataframe_with_index_1(category_trend_display)
        
        # Department Spend Trends
        st.markdown("### 🏢 Department Spend Trends Over Time")
        dept_trends, dept_msg = calculate_department_spend_trends(po_df)
        if not dept_trends.empty:
            # Create multi-line chart for department trends
            fig_dept_trends = px.line(
                dept_trends,
                x='month',
                y='total_spend',
                color='department',
                title='Department Spend Trends Over Time',
                markers=True
            )
            fig_dept_trends.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_title='Month',
                yaxis_title='Total Spend ($)',
                showlegend=True,
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            st.plotly_chart(fig_dept_trends, use_container_width=True, key="dept_spend_trends")
            
            with st.expander("📊 Department Trend Data"):
                dept_trend_display = dept_trends.copy()
                dept_trend_display.columns = ['Month', 'Department', 'Total Spend ($)']
                dept_trend_display['Total Spend ($)'] = dept_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                display_dataframe_with_index_1(dept_trend_display)
        
        # Top Suppliers Spend Trends
        if not st.session_state.suppliers.empty:
            st.markdown("### 🏭 Top Suppliers Spend Trends")
            supplier_trends, supplier_msg = calculate_supplier_spend_trends(po_df, st.session_state.suppliers)
            if not supplier_trends.empty:
                # Get top 5 suppliers by total spend
                top_suppliers = supplier_trends.groupby('supplier_name')['total_spend'].sum().nlargest(5).index
                top_supplier_trends = supplier_trends[supplier_trends['supplier_name'].isin(top_suppliers)]
                
                # Create multi-line chart for top suppliers
                fig_supplier_trends = px.line(
                    top_supplier_trends,
                    x='month',
                    y='total_spend',
                    color='supplier_name',
                    title='Top 5 Suppliers Spend Trends Over Time',
                    markers=True
                )
                fig_supplier_trends.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis_title='Total Spend ($)',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                st.plotly_chart(fig_supplier_trends, use_container_width=True, key="supplier_spend_trends")
                
                with st.expander("📊 Supplier Trend Data"):
                    supplier_trend_display = top_supplier_trends.copy()
                    supplier_trend_display.columns = ['Month', 'Supplier Name', 'Total Spend ($)']
                    supplier_trend_display['Total Spend ($)'] = supplier_trend_display['Total Spend ($)'].apply(lambda x: f"${x:,.0f}")
                    display_dataframe_with_index_1(supplier_trend_display)
        
        # Budget vs Actual Spend Trends
        if not st.session_state.budgets.empty:
            st.markdown("### 💰 Budget vs Actual Spend Trends")
            budget_trends, budget_msg = calculate_budget_spend_trends(po_df, st.session_state.budgets)
            if not budget_trends.empty:
                # Create dual-axis chart for budget comparison
                fig_budget_trends = go.Figure()
                
                # Add actual spend bars
                fig_budget_trends.add_trace(go.Bar(
                    x=budget_trends['month'],
                    y=budget_trends['total_spend'],
                    name='Actual Spend',
                    yaxis='y',
                    marker_color='#E63946'
                ))
                
                # Add budget amount bars
                fig_budget_trends.add_trace(go.Bar(
                    x=budget_trends['month'],
                    y=budget_trends['budget_amount'],
                    name='Budget Amount',
                    yaxis='y',
                    marker_color='#2E86AB'
                ))
                
                # Add variance line
                fig_budget_trends.add_trace(go.Scatter(
                    x=budget_trends['month'],
                    y=budget_trends['variance_percent'],
                    name='Variance %',
                    yaxis='y2',
                    line=dict(color='#FF6B35', width=3),
                    mode='lines+markers'
                ))
                
                fig_budget_trends.update_layout(
                    title='Budget vs Actual Spend Trends',
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='Month',
                    yaxis=dict(title='Amount ($)', side='left'),
                    yaxis2=dict(title='Variance (%)', side='right', overlaying='y'),
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)'),
                    barmode='group'
                )
                st.plotly_chart(fig_budget_trends, use_container_width=True, key="budget_spend_trends")
                
                with st.expander("📊 Budget Trend Data"):
                    budget_trend_display = budget_trends[['month', 'budget_code', 'total_spend', 'budget_amount', 'variance', 'variance_percent']].copy()
                    budget_trend_display.columns = ['Month', 'Budget Code', 'Actual Spend ($)', 'Budget Amount ($)', 'Variance ($)', 'Variance (%)']
                    budget_trend_display['Actual Spend ($)'] = budget_trend_display['Actual Spend ($)'].apply(lambda x: f"${x:,.0f}")
                    budget_trend_display['Budget Amount ($)'] = budget_trend_display['Budget Amount ($)'].apply(lambda x: f"${x:,.0f}")
                    budget_trend_display['Variance ($)'] = budget_trend_display['Variance ($)'].apply(lambda x: f"${x:,.0f}")
                    budget_trend_display['Variance (%)'] = budget_trend_display['Variance (%)'].apply(lambda x: f"{x:.1f}%")
                    display_dataframe_with_index_1(budget_trend_display)
    else:
        st.info("📅 Order date information is required for trend analysis. Please ensure your purchase order data includes order_date column.")
    

    
    # Auto Insights Section
    st.markdown("---")
    st.markdown("## 🤖 AI-Generated Insights")
    
    # Initialize insights generator
    insights_generator = ProcurementInsights(
        purchase_orders=st.session_state.purchase_orders,
        suppliers=st.session_state.suppliers,
        items_data=st.session_state.items_data,
        deliveries=st.session_state.deliveries,
        invoices=st.session_state.invoices,
        contracts=st.session_state.contracts,
        budgets=st.session_state.budgets,
        rfqs=st.session_state.rfqs
    )
    
    # Generate spend insights
    spend_insights = insights_generator.generate_spend_insights()
    display_insights_section(spend_insights, "Spend Analysis Insights", "💰")
    
    # Add actionable recommendations based on insights
    if "High spend concentration" in spend_insights:
        st.markdown("### 🎯 Immediate Actions Required")
        st.markdown("""
        - **Risk Mitigation**: Diversify spend across categories to reduce concentration risk
        - **Strategic Sourcing**: Develop category strategies for high-spend areas
        - **Supplier Management**: Review and optimize supplier relationships
        """)
    
    if "Budget Overruns" in spend_insights:
        st.markdown("### 🚨 Budget Management Alert")
        st.markdown("""
        - **Review**: Analyze budget overruns and identify root causes
        - **Control**: Implement stricter budget controls and approval processes
        - **Forecasting**: Improve budget forecasting accuracy
        """)

def show_supplier_performance():
    st.header("🏭 Supplier Performance & Management")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="supplier_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="supplier_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary Dashboard with professional styling
    total_suppliers = st.session_state.suppliers['supplier_id'].nunique() if not st.session_state.suppliers.empty else 0
    total_deliveries = len(st.session_state.deliveries) if not st.session_state.deliveries.empty else 0
    defect_count = len(st.session_state.deliveries[st.session_state.deliveries['defect_flag'] == True]) if not st.session_state.deliveries.empty else 0
    defect_rate = (defect_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    st.markdown("""
    <div class="summary-dashboard">
        <h3 style="color: #1e3c72; margin: 0; text-align: center;">📈 Supplier Performance Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Suppliers</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_suppliers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown(f"""
        <div class="metric-card-red">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Deliveries</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_deliveries:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        # Color code based on defect rate
        defect_color = "🟢" if defect_rate <= 5 else "🟡" if defect_rate <= 10 else "🔴"
        st.markdown(f"""
        <div class="metric-card-orange">
            <h4 style="color: white; margin: 0; font-size: 14px;">Defect Rate</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{defect_color} {defect_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown(f"""
        <div class="metric-card-teal">
            <h4 style="color: white; margin: 0; font-size: 14px;">Defect Count</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{defect_count:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        st.markdown(f"""
        <div class="metric-card-green">
            <h4 style="color: white; margin: 0; font-size: 14px;">Quality Score</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{(100 - defect_rate):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.deliveries.empty:
            delivery_analysis, delivery_msg = calculate_on_time_delivery_rate(po_df, st.session_state.deliveries)
            
            # Enhanced metric with color coding
            delivery_rate = float(delivery_msg.split('%')[0]) if '%' in delivery_msg else 0
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3c72; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">⏰ On-Time Delivery: {delivery_msg}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not delivery_analysis.empty:
                # Enhanced histogram with professional colors
                fig_delivery = px.histogram(
                    delivery_analysis, 
                    x='on_time', 
                    title='Delivery Performance Distribution',
                    color_discrete_sequence=['#2E86AB'],
                    opacity=0.8
                )
                fig_delivery.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_title='On-Time Delivery',
                    yaxis_title='Count'
                )
                st.plotly_chart(fig_delivery, use_container_width=True, key="supplier_delivery_chart")
        else:
            st.info("Add delivery data to see on-time delivery analysis")
    
    with col2:
        if not st.session_state.deliveries.empty:
            defect_analysis, defect_msg = calculate_supplier_defect_rate(st.session_state.deliveries)
            
            # Enhanced metric with color coding
            defect_rate_val = float(defect_msg.split('%')[0]) if '%' in defect_msg else 0
            quality_rate = 100 - defect_rate_val
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #E63946; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">🔍 Quality Rate: {quality_rate:.1f}%</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not defect_analysis.empty:
                # Enhanced pie chart with professional colors
                fig_defect = px.pie(
                    defect_analysis, 
                    names='defect_flag', 
                    title='Defect Analysis',
                    color_discrete_sequence=['#1A936F', '#E63946']
                )
                fig_defect.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    showlegend=True,
                    legend=dict(bgcolor='rgba(255,255,255,0.8)')
                )
                st.plotly_chart(fig_defect, use_container_width=True, key="supplier_defect_chart")
        else:
            st.info("Add delivery data to see defect analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("⏱️ Average Supplier Lead Time")
        if not st.session_state.deliveries.empty and not st.session_state.suppliers.empty:
            supplier_lead_time_data, supplier_lead_time_msg = calculate_supplier_lead_time_analysis(
                st.session_state.purchase_orders, st.session_state.deliveries, st.session_state.suppliers
            )
            if not supplier_lead_time_data.empty:
                # Calculate overall average for metric display
                overall_avg = supplier_lead_time_data['avg_lead_time_days'].mean()
                st.metric("Avg Lead Time", f"{overall_avg:.1f} days")
                
                # Create bar chart for supplier lead times
                fig_supplier_lead = px.bar(
                    supplier_lead_time_data, 
                    x='supplier_name', 
                    y='avg_lead_time_days',
                    title='Average Lead Time by Supplier',
                    labels={'supplier_name': 'Supplier', 'avg_lead_time_days': 'Average Lead Time (days)'},
                    color='avg_lead_time_days',
                    color_continuous_scale='RdYlGn_r'  # Red (slow) to Green (fast)
                )
                fig_supplier_lead.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_supplier_lead, use_container_width=True, key="supplier_lead_time_chart")
                
                # Show data table with required variables
                st.subheader("📊 Lead Time Analysis Data")
                lead_time_display = supplier_lead_time_data[['supplier_name', 'avg_lead_time_days', 'order_count']].copy()
                lead_time_display.columns = ['Supplier', 'Average Lead Time (days)', 'Order Count']
                display_dataframe_with_index_1(lead_time_display)
                
                # Show detailed lead time data
                st.subheader("📋 Detailed Lead Time Data")
                detailed_lead_time, _ = calculate_lead_time_analysis(st.session_state.purchase_orders, st.session_state.deliveries)
                if not detailed_lead_time.empty:
                    detailed_display = detailed_lead_time[['supplier_id', 'order_date', 'delivery_date_actual', 'lead_time_days']].copy()
                    detailed_display.columns = ['Supplier ID', 'Order Date', 'Delivery Date', 'Lead Time (days)']
                    display_dataframe_with_index_1(detailed_display)
            else:
                st.info("No lead time data available")
        else:
            st.info("Add delivery and supplier data to see lead time analysis")
    
    with col4:
        st.subheader("⚠️ Supplier Risk Assessment")
        if not st.session_state.suppliers.empty:
            risk_data, risk_msg = calculate_supplier_risk_assessment(
                st.session_state.suppliers, 
                st.session_state.purchase_orders,
                st.session_state.deliveries if 'deliveries' in st.session_state else None,
                st.session_state.invoices if 'invoices' in st.session_state else None,
                st.session_state.contracts if 'contracts' in st.session_state else None
            )
            st.info(risk_msg)
            if not risk_data.empty:
                fig_risk = px.scatter(risk_data, x='spend_percentage', y='total_risk_score', 
                                    hover_data=['supplier_name'], title='Supplier Risk Assessment')
                st.plotly_chart(fig_risk, use_container_width=True, key="supplier_risk_chart")
                display_dataframe_with_index_1(risk_data[['supplier_name', 'spend_percentage', 'total_risk_score', 'risk_level']])
        else:
            st.info("Add supplier data to see risk assessment")
    

    
    # Auto Insights Section
    st.markdown("---")
    st.markdown("## 🤖 AI-Generated Insights")
    
    # Initialize insights generator
    insights_generator = ProcurementInsights(
        purchase_orders=st.session_state.purchase_orders,
        suppliers=st.session_state.suppliers,
        items_data=st.session_state.items_data,
        deliveries=st.session_state.deliveries,
        invoices=st.session_state.invoices,
        contracts=st.session_state.contracts,
        budgets=st.session_state.budgets,
        rfqs=st.session_state.rfqs
    )
    
    # Generate supplier performance insights
    supplier_insights = insights_generator.generate_supplier_performance_insights()
    display_insights_section(supplier_insights, "Supplier Performance Insights", "🏭")
    
    # Add actionable recommendations based on insights
    if "Performance Issue" in supplier_insights:
        st.markdown("### 🎯 Performance Improvement Actions")
        st.markdown("""
        - **Supplier Development**: Implement performance improvement programs
        - **Performance Reviews**: Schedule regular supplier performance meetings
        - **SLA Management**: Establish clear service level agreements
        """)
    
    if "Quality Issue" in supplier_insights:
        st.markdown("### 🔍 Quality Management Actions")
        st.markdown("""
        - **Quality Audits**: Conduct supplier quality assessments
        - **Process Improvement**: Work with suppliers to improve quality processes
        - **Alternative Sources**: Identify backup suppliers for critical items
        """)

def show_cost_savings():
    st.header("💵 Cost & Savings Analysis")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="cost_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="cost_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Initialize predictive analytics for cost optimization
    predictive_analytics = ProcurementPredictiveAnalytics(
        purchase_orders_df=po_df,
        suppliers_df=st.session_state.suppliers if not st.session_state.suppliers.empty else None,
        items_df=st.session_state.items_data if not st.session_state.items_data.empty else None,
        deliveries_df=st.session_state.deliveries if not st.session_state.deliveries.empty else None,
        invoices_df=st.session_state.invoices if not st.session_state.invoices.empty else None,
        contracts_df=st.session_state.contracts if not st.session_state.contracts.empty else None,
        budgets_df=st.session_state.budgets if not st.session_state.budgets.empty else None,
        rfqs_df=st.session_state.rfqs if not st.session_state.rfqs.empty else None
    )
    
    # Get item-level cost optimization opportunities
    cost_optimization_data, cost_optimization_msg = predictive_analytics.predict_cost_optimization()
    
    # Create tabs for different levels of analysis
    tab1, tab2, tab3 = st.tabs(["📊 High-Level Metrics", "🎯 Item-Level Opportunities", "📈 Detailed Analysis"])
    
    with tab1:
        # Simple, clean layout with proper spacing
        st.subheader("💰 Cost Savings from Negotiation")
        if not st.session_state.rfqs.empty:
            savings_data, savings_msg = calculate_cost_savings_from_negotiation(po_df, st.session_state.rfqs)
            
            if not savings_data.empty:
                # Summary metrics
                total_savings = savings_data['savings'].sum()
                positive_savings = savings_data[savings_data['savings'] > 0]
                avg_savings_pct = savings_data['savings_percentage'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Net Savings", f"${total_savings:,.0f}")
                with col2:
                    st.metric("Successful Negotiations", f"{len(positive_savings)}")
                with col3:
                    st.metric("Average Savings %", f"{avg_savings_pct:.1f}%")
                
                # Supplier savings chart
                supplier_savings = savings_data.groupby('supplier_id').agg({
                    'savings': 'sum',
                    'savings_percentage': 'mean'
                }).reset_index()
                
                if not st.session_state.suppliers.empty:
                    supplier_savings = supplier_savings.merge(
                        st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                        on='supplier_id', 
                        how='left'
                    )
                    x_axis_col = 'supplier_name'
                else:
                    x_axis_col = 'supplier_id'
                
                fig_savings = px.bar(
                    supplier_savings, 
                    x=x_axis_col, 
                    y='savings',
                    title='Cost Savings from Negotiation by Supplier',
                    color='savings_percentage',
                    color_continuous_scale='RdYlGn'
                )
                fig_savings.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_savings, use_container_width=True)
            else:
                st.warning("No matching RFQ-PO data found")
        else:
            st.info("📋 Add RFQ data to see negotiation savings analysis")
        
        st.markdown("---")
        
        st.subheader("📊 Benchmark-Based Price Efficiency")
        efficiency_data, efficiency_msg = calculate_benchmark_price_efficiency(po_df, st.session_state.items_data)
        
        if not efficiency_data.empty:
            overpriced_items = efficiency_data[efficiency_data['is_overpriced']]
            avg_efficiency = efficiency_data['efficiency_index'].mean()
            overpriced_spend = overpriced_items['total_spend'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Efficiency Index", f"{avg_efficiency:.2f}")
            with col2:
                st.metric("Overpriced Items", f"{len(overpriced_items)}")
            with col3:
                st.metric("Overpriced Spend", f"${overpriced_spend:,.0f}")
            

            
            # Show top overpriced items
            if len(overpriced_items) > 0:
                st.subheader("🚨 Top Overpriced Items")
                top_overpriced = overpriced_items.nlargest(10, 'deviation_pct')[['item_name', 'supplier_id', 'actual_price', 'benchmark_price', 'deviation_pct', 'total_spend']]
                top_overpriced.columns = ['Item', 'Supplier ID', 'Actual Price', 'Benchmark Price', 'Deviation %', 'Total Spend']
                display_dataframe_with_index_1(top_overpriced)
        else:
            st.info("No efficiency data available")
        
        st.markdown("---")
        
        st.subheader("🎯 Negotiation Opportunity Index")
        opportunity_data, opportunity_msg = calculate_negotiation_opportunity_index(po_df, st.session_state.items_data)
        
        if not opportunity_data.empty:
            high_opportunity = opportunity_data[opportunity_data['opportunity_level'] == 'High']
            avg_score = opportunity_data['opportunity_score'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Opportunity Score", f"{avg_score:.2f}")
            with col2:
                st.metric("High Opportunity Items", f"{len(high_opportunity)}")
            with col3:
                st.metric("Total Items Analyzed", f"{len(opportunity_data)}")
            

            
            # Show top opportunities
            if len(high_opportunity) > 0:
                st.subheader("💡 Top Negotiation Opportunities")
                top_opportunities = high_opportunity.nlargest(10, 'opportunity_score')[['item_name', 'supplier_id', 'opportunity_score', 'volume_weight', 'competition_factor', 'total_quantity']]
                top_opportunities.columns = ['Item', 'Supplier ID', 'Opportunity Score', 'Volume Weight', 'Competition Factor', 'Total Quantity']
                display_dataframe_with_index_1(top_opportunities)
        else:
            st.info("No opportunity data available")
        
        st.markdown("---")
        
        st.subheader("💰 Tail Spend Optimization")
        tail_data, tail_msg = calculate_tail_spend_optimization(po_df, st.session_state.suppliers)
        
        if not tail_data.empty:
            total_tail_spend = tail_data['total_spend'].sum()
            total_potential_savings = tail_data['potential_savings'].sum()
            high_priority_consolidation = tail_data[tail_data['consolidation_priority'] == 'High']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tail Spend", f"${total_tail_spend:,.0f}")
            with col2:
                st.metric("Potential Savings", f"${total_potential_savings:,.0f}")
            with col3:
                st.metric("High Priority Suppliers", f"{len(high_priority_consolidation)}")
            
            # Tail spend chart
            fig_tail = px.bar(
                tail_data.head(10),
                x='supplier_name',
                y='total_spend',
                color='consolidation_priority',
                title='Top 10 Tail Spend Suppliers',
                color_discrete_map={'High': '#FF6B35', 'Medium': '#FFA500'}
            )
            fig_tail.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tail, use_container_width=True)
            
            # Show consolidation opportunities
            st.subheader("🔧 Consolidation Opportunities")
            consolidation_display = tail_data[['supplier_name', 'total_spend', 'po_count', 'avg_po_value', 'potential_savings', 'consolidation_priority']].copy()
            consolidation_display.columns = ['Supplier', 'Total Spend ($)', 'PO Count', 'Avg PO Value ($)', 'Potential Savings ($)', 'Priority']
            display_dataframe_with_index_1(consolidation_display)
        else:
            st.info("No tail spend data available")
        
        st.markdown("---")
        
        st.subheader("📈 Unit Cost Trend Analysis")
        trend_analysis_data, trend_analysis_msg = calculate_unit_cost_trend_analysis(po_df, st.session_state.items_data)
        
        if not trend_analysis_data.empty:
            increasing_items = trend_analysis_data[trend_analysis_data['trend_direction'] == 'Increasing']
            avg_volatility = trend_analysis_data['price_volatility'].mean()
            total_anomalies = trend_analysis_data['anomaly_count'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Increasing Price Items", f"{len(increasing_items)}")
            with col2:
                st.metric("Avg Price Volatility", f"{avg_volatility:.2f}")
            with col3:
                st.metric("Price Anomalies", f"{total_anomalies}")
            
            # Create trend analysis for each item over time
            if not po_df.empty and not st.session_state.items_data.empty:
                # Get the correct column names
                item_name_col = get_column_name(st.session_state.items_data, 'item_name')
                
                if item_name_col is None:
                    st.error("Could not find item_name column in items data")
                    return
                
                # Merge data to get item names
                merged_trend_data = trend_analysis_data.merge(
                    st.session_state.items_data[['item_id', item_name_col]], 
                    on='item_id', 
                    how='left'
                )
                
                # Get the correct column name after merge (pandas might add suffixes)
                final_item_name_col = get_column_name(merged_trend_data, 'item_name')
                
                if final_item_name_col is None:
                    st.error("Could not find item_name column after merge")
                    return
                
                # Get items with significant trends (top 10 by trend slope)
                significant_trends = merged_trend_data.nlargest(10, 'trend_slope')[[final_item_name_col, 'trend_slope', 'trend_direction', 'avg_price']]
                significant_trends = significant_trends.sort_values('trend_slope', ascending=False)
                
                # Create bar chart showing trend slopes for top items
                fig_trend = px.bar(
                    significant_trends,
                    x=final_item_name_col,
                    y='trend_slope',
                    color='trend_direction',
                    title='Price Trend Analysis - Top 10 Items by Trend Slope',
                    color_discrete_map={'Increasing': '#FF6B35', 'Decreasing': '#87CEEB'},
                    labels={'trend_slope': 'Price Trend Slope', final_item_name_col: 'Item Name'}
                )
                fig_trend.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Show detailed trend information
                st.subheader("📊 Detailed Trend Information")
                trend_display = significant_trends.copy()
                trend_display.columns = ['Item Name', 'Trend Slope', 'Trend Direction', 'Average Price']
                trend_display['Trend Slope'] = trend_display['Trend Slope'].round(3)
                trend_display['Average Price'] = trend_display['Average Price'].round(2)
                display_dataframe_with_index_1(trend_display)
            
            # Show items with increasing prices
            if len(increasing_items) > 0:
                st.subheader("📈 Items with Increasing Prices")
                increasing_display = increasing_items.nlargest(10, 'trend_slope')[['item_name', 'category', 'trend_slope', 'price_volatility', 'anomaly_count', 'avg_price']]
                increasing_display.columns = ['Item', 'Category', 'Trend Slope', 'Price Volatility', 'Anomalies', 'Avg Price']
                display_dataframe_with_index_1(increasing_display)
        else:
            st.info("No trend analysis data available")
        
        st.markdown("---")
        
        st.subheader("🎯 Savings Realization Tracking")
        if 'rfqs' in st.session_state and not st.session_state.rfqs.empty:
            realization_data, realization_msg = calculate_savings_realization_tracking(po_df, st.session_state.rfqs)
            
            if not realization_data.empty:
                exceeded_target = realization_data[realization_data['realization_status'] == 'Exceeded Target']
                below_target = realization_data[realization_data['realization_status'] == 'Below Target']
                avg_realization = realization_data['actual_savings_pct'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Exceeded Target", f"{len(exceeded_target)}")
                with col2:
                    st.metric("Below Target", f"{len(below_target)}")
                with col3:
                    st.metric("Avg Realization %", f"{avg_realization:.1f}%")
                
                # Realization status distribution
                status_counts = realization_data['realization_status'].value_counts()
                fig_realization = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title='Savings Realization Status Distribution',
                    color_discrete_sequence=['#FF6B35', '#FFA500', '#87CEEB']
                )
                st.plotly_chart(fig_realization, use_container_width=True)
                
                # Show realization details
                st.subheader("📊 Savings Realization Details")
                realization_display = realization_data[['item_id', 'supplier_id', 'actual_savings_pct', 'target_savings_pct', 'savings_gap_pct', 'realization_status']].copy()
                realization_display.columns = ['Item ID', 'Supplier ID', 'Actual Savings %', 'Target Savings %', 'Gap %', 'Status']
                display_dataframe_with_index_1(realization_display)
            else:
                st.info("No realization data available")
        else:
            st.info("📋 Add RFQ data to see savings realization tracking")
        
        st.markdown("---")
        
        st.subheader("💡 Spend Avoidance Detection")
        avoidance_data, avoidance_msg = calculate_spend_avoidance_detection(po_df, st.session_state.items_data)
        
        if not avoidance_data.empty:
            total_avoided_cost = avoidance_data['avoided_cost'].sum()
            high_priority_opportunities = avoidance_data[avoidance_data['priority'] == 'High']
            avg_avoidance_pct = avoidance_data['avoided_cost_pct'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Avoided Cost", f"${total_avoided_cost:,.0f}")
            with col2:
                st.metric("High Priority Items", f"{len(high_priority_opportunities)}")
            with col3:
                st.metric("Avg Avoidance %", f"{avg_avoidance_pct:.1f}%")
            
            # Avoidance opportunities chart
            fig_avoidance = px.bar(
                avoidance_data.head(10),
                x='item_name',
                y='avoided_cost',
                color='avoidance_type',
                title='Top 10 Spend Avoidance Opportunities',
                color_discrete_map={'Supplier Switching': '#FF6B35', 'Price Negotiation': '#87CEEB'}
            )
            fig_avoidance.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_avoidance, use_container_width=True)
            
            # Show avoidance details
            st.subheader("💡 Avoidance Opportunities")
            avoidance_display = avoidance_data[['item_name', 'category', 'current_avg_price', 'min_price', 'avoided_cost_pct', 'avoidance_type', 'priority']].copy()
            avoidance_display.columns = ['Item', 'Category', 'Current Avg Price', 'Min Price', 'Avoidance %', 'Type', 'Priority']
            display_dataframe_with_index_1(avoidance_display)
        else:
            st.info("No avoidance opportunities found")
        
        st.markdown("---")
        
        st.subheader("📋 Contract Leakage Analysis")
        if 'contracts' in st.session_state and not st.session_state.contracts.empty:
            leakage_data, leakage_msg = calculate_contract_leakage(po_df, st.session_state.contracts, st.session_state.items_data)
            
            if isinstance(leakage_data, dict) and 'summary' in leakage_data:
                summary = leakage_data['summary']
                by_category = leakage_data['by_category']
                high_leakage_items = leakage_data['high_leakage_items']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Leakage %", f"{summary['leakage_pct']:.1f}%")
                with col2:
                    st.metric("Off-Contract Spend", f"${summary['off_contract_spend']:,.0f}")
                with col3:
                    st.metric("Contracted Spend", f"${summary['contracted_spend']:,.0f}")
                
                # Leakage by category chart
                if not by_category.empty:
                    fig_leakage = px.bar(
                        by_category,
                        x='category',
                        y='leakage_pct',
                        title='Contract Leakage by Category',
                        color='leakage_pct',
                        color_continuous_scale='Reds'
                    )
                    fig_leakage.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_leakage, use_container_width=True)
                
                # Show high leakage items
                if not high_leakage_items.empty:
                    st.subheader("🚨 High Leakage Items")
                    leakage_display = high_leakage_items.head(10)[['item_name', 'category', 'total_spend', 'po_id']].copy()
                    leakage_display.columns = ['Item', 'Category', 'Total Spend ($)', 'PO Count']
                    display_dataframe_with_index_1(leakage_display)
            else:
                st.info("No leakage data available")
        else:
            st.info("📋 Add contract data to see leakage analysis")
    
    with tab2:
        st.subheader("🎯 Item-Level Cost Optimization Opportunities")
        
        if not cost_optimization_data.empty:
            # Display summary metrics
            total_savings_potential = cost_optimization_data['savings_amount'].sum()
            avg_savings_percentage = cost_optimization_data['savings_percentage'].mean()
            high_priority_count = len(cost_optimization_data[cost_optimization_data['priority'] == 'High Priority'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Savings Potential", f"${total_savings_potential:,.0f}")
            with col2:
                st.metric("Average Savings %", f"{avg_savings_percentage:.1f}%")
            with col3:
                st.metric("High Priority Items", f"{high_priority_count}")
            
            # Filter options
            st.subheader("🔍 Filter Opportunities")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                priority_filter = st.selectbox(
                    "Priority Level",
                    options=['All', 'High Priority', 'Medium Priority', 'Low Priority'],
                    key="priority_filter"
                )
            
            with col2:
                optimization_type_filter = st.selectbox(
                    "Optimization Type",
                    options=['All'] + list(cost_optimization_data['optimization_type'].unique()),
                    key="type_filter"
                )
            
            with col3:
                min_savings = st.number_input(
                    "Min Savings ($)",
                    min_value=0,
                    max_value=int(cost_optimization_data['savings_amount'].max()),
                    value=0,
                    step=100,
                    key="min_savings_filter"
                )
            
            # Apply filters
            filtered_data = cost_optimization_data.copy()
            if priority_filter != 'All':
                filtered_data = filtered_data[filtered_data['priority'] == priority_filter]
            if optimization_type_filter != 'All':
                filtered_data = filtered_data[filtered_data['optimization_type'] == optimization_type_filter]
            filtered_data = filtered_data[filtered_data['savings_amount'] >= min_savings]
            
            # Sort by savings amount
            filtered_data = filtered_data.sort_values('savings_amount', ascending=False)
            
            # Display filtered results
            st.subheader(f"📋 Optimization Opportunities ({len(filtered_data)} items)")
            
            if not filtered_data.empty:
                # Create summary chart
                fig_summary = px.bar(
                    filtered_data.head(10),  # Top 10 by savings
                    x='item_name',
                    y='savings_amount',
                    color='priority',
                    title='Top 10 Cost Optimization Opportunities',
                    labels={'item_name': 'Item', 'savings_amount': 'Savings Potential ($)', 'priority': 'Priority'},
                    color_discrete_map={'High Priority': '#FF6B6B', 'Medium Priority': '#FFD93D', 'Low Priority': '#6BCF7F'}
                )
                fig_summary.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                st.plotly_chart(fig_summary, use_container_width=True)
                
                # Display detailed table
                st.subheader("📊 Detailed Optimization Analysis")
                
                # Prepare display data
                display_data = filtered_data[['item_name', 'optimization_type', 'current_cost', 'optimized_cost', 
                                           'savings_amount', 'savings_percentage', 'priority', 'timeframe']].copy()
                display_data.columns = ['Item Name', 'Optimization Type', 'Current Cost ($)', 'Optimized Cost ($)', 
                                      'Savings ($)', 'Savings %', 'Priority', 'Timeframe']
                display_data['Current Cost ($)'] = display_data['Current Cost ($)'].round(2)
                display_data['Optimized Cost ($)'] = display_data['Optimized Cost ($)'].round(2)
                display_data['Savings ($)'] = display_data['Savings ($)'].round(2)
                display_data['Savings %'] = display_data['Savings %'].round(1)
                
                display_dataframe_with_index_1(display_data)
                
                # Show detailed recommendations for selected item
                st.subheader("💡 Detailed Recommendations")
                
                if len(filtered_data) > 0:
                    # Item selector
                    selected_item_idx = st.selectbox(
                        "Select an item to view detailed recommendations:",
                        options=range(len(filtered_data)),
                        format_func=lambda x: f"{filtered_data.iloc[x]['item_name']} - ${filtered_data.iloc[x]['savings_amount']:,.0f} potential savings"
                    )
                    
                    selected_item = filtered_data.iloc[selected_item_idx]
                    
                    # Display detailed recommendation
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"### {selected_item['item_name']}")
                        st.markdown(f"**Optimization Type**: {selected_item['optimization_type']}")
                        st.markdown(f"**Current Cost**: ${selected_item['current_cost']:,.2f}")
                        st.markdown(f"**Optimized Cost**: ${selected_item['optimized_cost']:,.2f}")
                        st.markdown(f"**Savings Potential**: ${selected_item['savings_amount']:,.2f} ({selected_item['savings_percentage']:.1f}%)")
                        st.markdown(f"**Priority**: {selected_item['priority']}")
                        st.markdown(f"**Timeframe**: {selected_item['timeframe']}")
                        
                        st.markdown("**Recommendation**:")
                        st.info(selected_item['recommendation'])
                        
                        st.markdown("**Implementation Steps**:")
                        st.markdown(selected_item['implementation'].replace('\n', '  \n'))
                    
                    with col2:
                        # Create gauge chart for savings percentage
                        fig_gauge = px.pie(
                            values=[selected_item['savings_percentage'], 100 - selected_item['savings_percentage']],
                            names=['Savings', 'Remaining Cost'],
                            title=f"Savings Potential: {selected_item['savings_percentage']:.1f}%",
                            color_discrete_sequence=['#FF6B6B', '#E0E0E0']
                        )
                        fig_gauge.update_layout(showlegend=False)
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        
                        # Risk level indicator
                        risk_color = {'Low': '#6BCF7F', 'Medium': '#FFD93D', 'High': '#FF6B6B'}
                        st.markdown(f"""
                        <div style="background-color: {risk_color.get(selected_item['risk_level'], '#E0E0E0')}; 
                                    padding: 10px; border-radius: 5px; text-align: center; color: white;">
                            <strong>Risk Level: {selected_item['risk_level']}</strong>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No optimization opportunities match the selected filters.")
        else:
            st.info("No cost optimization data available. This may be due to insufficient data or no optimization opportunities identified.")
    
    with tab3:
        st.subheader("📈 Detailed Cost Analysis")
        
        # Item-level cost breakdown
        if not po_df.empty and not st.session_state.items_data.empty:
            # Merge purchase orders with items data
            merged_data = po_df.merge(st.session_state.items_data, on='item_id', how='left')
            
            # Get the correct unit price column name
            unit_price_col = get_unit_price_column(merged_data)
            if unit_price_col is None:
                st.error("Could not find unit price column in merged data")
                return
            
            merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
            
            # Item spend analysis
            item_name_col = get_column_name(merged_data, 'item_name')
            category_col = get_column_name(merged_data, 'category')
            
            if item_name_col is None or category_col is None:
                st.error("Could not find required columns (item_name or category) in merged data")
                return
            
            # Group by item name only to avoid duplicate items
            item_spend = merged_data.groupby(item_name_col).agg({
                'total_spend': 'sum',
                'quantity': 'sum',
                unit_price_col: 'mean',
                'po_id': 'count'
            }).reset_index()
            item_spend.columns = ['Item Name', 'Total Spend ($)', 'Total Quantity', 'Avg Unit Price ($)', 'Order Count']
            
            # Get the category for each item from the items data
            if not st.session_state.items_data.empty:
                category_col = get_column_name(st.session_state.items_data, 'category')
                if category_col is not None:
                    item_spend = item_spend.merge(
                        st.session_state.items_data[[item_name_col, category_col]], 
                        left_on='Item Name', 
                        right_on=item_name_col,
                        how='left'
                    )
                    # Use the category from items data, not from merged data
                    item_spend['Category'] = item_spend[category_col]
                    item_spend = item_spend.drop(columns=[category_col, f'{item_name_col}_y'] if f'{item_name_col}_y' in item_spend.columns else [category_col])
                else:
                    item_spend['Category'] = 'Unknown'
            else:
                item_spend['Category'] = 'Unknown'
            
            item_spend = item_spend.sort_values('Total Spend ($)', ascending=False)
            
            st.subheader("💰 Top Spending Items")
            
            # Display top 10 items by spend
            fig_top_spend = px.bar(
                item_spend.head(10),
                x='Item Name',
                y='Total Spend ($)',
                title='Top 10 Items by Total Spend',
                labels={'Item Name': 'Item', 'Total Spend ($)': 'Total Spend ($)'},
                color_discrete_sequence=['#1f77b4']  # Single blue color for all bars
            )
            fig_top_spend.update_layout(
                xaxis_tickangle=-45,
                showlegend=False
            )
            st.plotly_chart(fig_top_spend, use_container_width=True)
            
            # Display item spend table
            st.subheader("📊 Item Spend Analysis")
            display_dataframe_with_index_1(item_spend)
            
            # Price variance analysis
            st.subheader("📊 Price Variance Analysis")
            
            # Get the correct column names
            item_name_col = get_column_name(merged_data, 'item_name')
            supplier_id_col = get_column_name(merged_data, 'supplier_id')
            
            if item_name_col is None or supplier_id_col is None:
                st.error("Could not find required columns (item_name or supplier_id) in merged data")
                return
            
            price_variance = merged_data.groupby([item_name_col, supplier_id_col]).agg({
                unit_price_col: ['mean', 'std', 'count']
            }).reset_index()
            price_variance.columns = ['Item Name', 'Supplier ID', 'Avg Price', 'Price Std', 'Order Count']
            price_variance['Price Variance %'] = (price_variance['Price Std'] / price_variance['Avg Price'] * 100).round(2)
            
            # Add supplier names if available
            if not st.session_state.suppliers.empty:
                price_variance = price_variance.merge(
                    st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                    left_on='Supplier ID', 
                    right_on='supplier_id',
                    how='left'
                )
                price_variance['Supplier'] = price_variance['supplier_name'].fillna(price_variance['Supplier ID'])
            else:
                price_variance['Supplier'] = price_variance['Supplier ID']
            
            # Filter for items with multiple suppliers and significant variance
            high_variance = price_variance[
                (price_variance['Order Count'] >= 2) & 
                (price_variance['Price Variance %'] > 10)
            ].sort_values('Price Variance %', ascending=False)
            
            if not high_variance.empty:
                st.info(f"🔍 Found {len(high_variance)} item-supplier combinations with >10% price variance")
                
                fig_variance = px.scatter(
                    high_variance.head(20),
                    x='Avg Price',
                    y='Price Variance %',
                    size='Order Count',
                    color='Item Name',
                    title='Price Variance by Item and Supplier',
                    labels={'Avg Price': 'Average Price ($)', 'Price Variance %': 'Price Variance (%)', 'Order Count': 'Orders'}
                )
                st.plotly_chart(fig_variance, use_container_width=True)
                
                # Display variance table
                variance_display = high_variance[['Item Name', 'Supplier', 'Avg Price', 'Price Variance %', 'Order Count']].copy()
                variance_display.columns = ['Item Name', 'Supplier', 'Avg Price ($)', 'Price Variance (%)', 'Order Count']
                display_dataframe_with_index_1(variance_display)
            else:
                st.info("No significant price variance detected across suppliers.")
        else:
            st.info("Insufficient data for detailed cost analysis. Please ensure both purchase orders and items data are loaded.")
    
    # Auto Insights Section
    st.markdown("---")
    st.markdown("## 🤖 AI-Generated Insights")
    
    # Initialize insights generator
    insights_generator = ProcurementInsights(
        purchase_orders=st.session_state.purchase_orders,
        suppliers=st.session_state.suppliers,
        items_data=st.session_state.items_data,
        deliveries=st.session_state.deliveries,
        invoices=st.session_state.invoices,
        contracts=st.session_state.contracts,
        budgets=st.session_state.budgets,
        rfqs=st.session_state.rfqs
    )
    
    # Generate cost savings insights
    cost_insights = insights_generator.generate_cost_savings_insights()
    display_insights_section(cost_insights, "Cost Savings Opportunities", "💡")
    
    # Add actionable recommendations based on insights
    if "Negotiation Opportunity" in cost_insights:
        st.markdown("### 🎯 Negotiation Strategies")
        st.markdown("""
        - **Competitive Bidding**: Leverage multiple quotes for better pricing
        - **Volume Consolidation**: Combine orders for volume discounts
        - **Supplier Competition**: Create competitive pressure through RFQs
        """)
    
    if "High-Cost Item" in cost_insights:
        st.markdown("### 💰 Cost Optimization Actions")
        st.markdown("""
        - **Alternative Sourcing**: Identify lower-cost suppliers
        - **Value Engineering**: Work with suppliers to reduce costs
        - **Specification Review**: Optimize product specifications
        """)

def show_process_efficiency():
    st.header("⚡ Procurement Process Efficiency")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="process_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="process_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary efficiency metrics
    st.subheader("📈 Efficiency Summary Dashboard")
    
    # Calculate overall efficiency metrics
    if not po_df.empty:
        total_pos = len(po_df)
        total_spend = (po_df['quantity'] * po_df['unit_price']).sum()
        avg_order_value = total_spend / total_pos if total_pos > 0 else 0
        
        # Calculate average cycle time if available
        avg_cycle_time = "N/A"
        if not st.session_state.invoices.empty:
            cycle_data, _ = calculate_purchase_order_cycle_time(po_df, st.session_state.deliveries)
            if not cycle_data.empty:
                avg_cycle_time = f"{cycle_data['cycle_time_days'].mean():.1f} days"
        
        # Calculate average lead time if available
        avg_lead_time = "N/A"
        if not st.session_state.deliveries.empty:
            lead_time_data, _ = calculate_procurement_lead_time(po_df, st.session_state.deliveries)
            if not lead_time_data.empty:
                avg_lead_time = f"{lead_time_data['lead_time_days'].mean():.1f} days"
        
        # Display summary metrics
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Total POs", f"{total_pos:,}")
        
        with summary_col2:
            st.metric("Total Spend", f"${total_spend:,.2f}")
        
        with summary_col3:
            st.metric("Avg Order Value", f"${avg_order_value:,.2f}")
        
        with summary_col4:
            st.metric("Avg Cycle", avg_cycle_time)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**⏱️ PO Cycle Time**")
        if not st.session_state.invoices.empty:
            cycle_data, cycle_msg = calculate_purchase_order_cycle_time(po_df, st.session_state.deliveries)
            st.metric("PO Cycle", cycle_msg)
            if not cycle_data.empty:
                # Create more interpretable cycle time analysis
                # Group by department to show cycle time by department
                cycle_analysis = cycle_data.groupby('department').agg({
                    'cycle_time_days': ['mean', 'count', 'std']
                }).reset_index()
                cycle_analysis.columns = ['department', 'avg_cycle_time', 'po_count', 'cycle_std']
                cycle_analysis['avg_cycle_time'] = cycle_analysis['avg_cycle_time'].round(1)
                cycle_analysis['cycle_std'] = cycle_analysis['cycle_std'].round(1)
                
                # Sort by average cycle time for better visualization
                cycle_analysis = cycle_analysis.sort_values('avg_cycle_time', ascending=False)
                
                # Create bar chart for cycle time by department
                fig_cycle = px.bar(
                    cycle_analysis, 
                    x='department', 
                    y='avg_cycle_time',
                    title='Average PO Cycle Time by Department',
                    labels={'department': 'Department', 'avg_cycle_time': 'Average Cycle Time (days)'},
                    color='po_count',
                    color_continuous_scale='Reds'  # Red for longer cycle times
                )
                fig_cycle.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                st.plotly_chart(fig_cycle, use_container_width=True, key="po_cycle_time_chart")
                
                # Add insights
                if len(cycle_analysis) > 0:
                    slowest_dept = cycle_analysis.iloc[0]  # Already sorted by cycle time descending
                    avg_cycle = cycle_analysis['avg_cycle_time'].mean()
                    st.write("💡 Slowest: " + slowest_dept['department'] + " - " + f"{slowest_dept['avg_cycle_time']:.1f}" + " days | Avg: " + f"{avg_cycle:.1f}" + " days")
                
                # Show cycle time data table
                st.markdown("**📊 Cycle Time Data**")
                cycle_display = cycle_analysis.copy()
                cycle_display.columns = ['Department', 'Avg Cycle Time (days)', 'PO Count', 'Std Dev']
                display_dataframe_with_index_1(cycle_display)
        else:
            st.info("Add invoice data to see cycle time analysis")
    
    with col2:
        st.markdown("**🚚 Lead Time**")
        if not st.session_state.deliveries.empty:
            lead_time_data, lead_time_msg = calculate_procurement_lead_time(st.session_state.purchase_orders, st.session_state.deliveries)
            st.metric("Lead Time", lead_time_msg)
            if not lead_time_data.empty:
                # Create more interpretable lead time analysis
                # Group by supplier to show lead time by supplier
                lead_time_analysis = lead_time_data.groupby('supplier_id').agg({
                    'lead_time_days': ['mean', 'count', 'std']
                }).reset_index()
                lead_time_analysis.columns = ['supplier_id', 'avg_lead_time', 'order_count', 'lead_std']
                lead_time_analysis['avg_lead_time'] = lead_time_analysis['avg_lead_time'].round(1)
                lead_time_analysis['lead_std'] = lead_time_analysis['lead_std'].round(1)
                
                # Add supplier names if available
                if not st.session_state.suppliers.empty:
                    lead_time_analysis = lead_time_analysis.merge(
                        st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                        on='supplier_id', 
                        how='left'
                    )
                    x_axis_col = 'supplier_name'
                    x_axis_label = 'Supplier'
                else:
                    x_axis_col = 'supplier_id'
                    x_axis_label = 'Supplier ID'
                
                # Sort by average lead time for better visualization
                lead_time_analysis = lead_time_analysis.sort_values('avg_lead_time', ascending=False)
                
                # Create bar chart for lead time by supplier
                fig_lead = px.bar(
                    lead_time_analysis, 
                    x=x_axis_col, 
                    y='avg_lead_time',
                    title='Average Procurement Lead Time by Supplier',
                    labels={x_axis_col: x_axis_label, 'avg_lead_time': 'Average Lead Time (days)'},
                    color='order_count',
                    color_continuous_scale='Reds'  # Red for longer lead times
                )
                fig_lead.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                st.plotly_chart(fig_lead, use_container_width=True, key="process_lead_time_chart")
                
                # Add insights
                if len(lead_time_analysis) > 0:
                    slowest_supplier = lead_time_analysis.iloc[0]  # Already sorted by lead time descending
                    avg_lead = lead_time_analysis['avg_lead_time'].mean()
                    st.write("💡 Slowest: " + slowest_supplier[x_axis_col] + " - " + f"{slowest_supplier['avg_lead_time']:.1f}" + " days | Avg: " + f"{avg_lead:.1f}" + " days")
                
                # Show lead time data table
                st.markdown("**📊 Lead Time Data**")
                if 'supplier_name' in lead_time_analysis.columns:
                    lead_display = lead_time_analysis[['supplier_name', 'avg_lead_time', 'order_count', 'lead_std']].copy()
                    lead_display.columns = ['Supplier', 'Avg Lead Time (days)', 'Order Count', 'Std Dev']
                else:
                    lead_display = lead_time_analysis[['supplier_id', 'avg_lead_time', 'order_count', 'lead_std']].copy()
                    lead_display.columns = ['Supplier ID', 'Avg Lead Time (days)', 'Order Count', 'Std Dev']
                display_dataframe_with_index_1(lead_display)
        else:
            st.info("Add delivery data to see lead time analysis")
    
    with col3:
        st.markdown("**📊 Efficiency Score**")
        if not st.session_state.purchase_orders.empty:
            # Calculate process efficiency score by department
            po_analysis = st.session_state.purchase_orders.copy()
            po_analysis['total_spend'] = po_analysis['quantity'] * po_analysis['unit_price']
            
            # Calculate efficiency metrics by department
            dept_efficiency = po_analysis.groupby('department').agg({
                'po_id': 'count',
                'total_spend': 'sum',
                'quantity': 'sum'
            }).reset_index()
            dept_efficiency.columns = ['department', 'po_count', 'total_spend', 'total_quantity']
            
            # Calculate efficiency score (higher spend per PO = more efficient)
            dept_efficiency['efficiency_score'] = (dept_efficiency['total_spend'] / dept_efficiency['po_count']).round(2)
            dept_efficiency['avg_order_value'] = (dept_efficiency['total_spend'] / dept_efficiency['po_count']).round(2)
            
            # Sort by efficiency score for better visualization
            dept_efficiency = dept_efficiency.sort_values('efficiency_score', ascending=False)
            
            # Create bar chart for efficiency score by department
            fig_efficiency = px.bar(
                dept_efficiency, 
                x='department', 
                y='efficiency_score',
                title='Process Efficiency Score by Department',
                labels={'department': 'Department', 'efficiency_score': 'Efficiency Score ($/PO)'},
                color='po_count',
                color_continuous_scale='Greens'  # Green for higher efficiency
            )
            fig_efficiency.update_layout(
                xaxis_tickangle=-45,
                showlegend=True
            )
            st.plotly_chart(fig_efficiency, use_container_width=True, key="process_efficiency_chart")
            
            # Add insights
            if len(dept_efficiency) > 0:
                most_efficient = dept_efficiency.iloc[0]  # Already sorted by efficiency score descending
                avg_efficiency = dept_efficiency['efficiency_score'].mean()
                most_efficient_value = int(most_efficient['efficiency_score'])
                avg_efficiency_value = int(avg_efficiency)
                st.write("Most Efficient: " + most_efficient['department'] + " - $" + str(most_efficient_value) + "/PO")
                st.write("Average Efficiency: $" + str(avg_efficiency_value) + "/PO")
            
            # Show efficiency data table
            st.markdown("**📊 Efficiency Data**")
            efficiency_display = dept_efficiency.copy()
            efficiency_display.columns = ['Department', 'PO Count', 'Total Spend ($)', 'Total Quantity', 'Efficiency Score ($/PO)', 'Avg Order Value ($)']
            display_dataframe_with_index_1(efficiency_display)
        else:
            st.info("Add purchase order data to see efficiency analysis")
    


def show_compliance_risk():
    st.header("📋 Compliance & Risk Management")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="compliance_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="compliance_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary compliance metrics
    st.markdown("**📈 Compliance Summary Dashboard**")
    
    # Calculate overall compliance metrics
    total_pos = len(po_df)
    contract_compliance = "N/A"
    policy_compliance = "N/A"
    
    if not st.session_state.contracts.empty:
        contract_data, contract_msg = calculate_contract_compliance_rate(st.session_state.contracts, po_df)
        if not contract_data.empty:
            compliant_contracts = len(contract_data[contract_data['compliance_status'] == 'Compliant'])
            total_contracts = len(contract_data)
            contract_compliance = f"{compliant_contracts}/{total_contracts} ({compliant_contracts/total_contracts*100:.1f}%)"
    
    if not st.session_state.budgets.empty:
        policy_data, policy_msg = calculate_policy_compliance_rate(po_df)
        if not policy_data.empty:
            pos_with_budget = len(policy_data[policy_data['status'] == 'Compliant'])
            policy_compliance = f"{pos_with_budget}/{total_pos} ({pos_with_budget/total_pos*100:.1f}%)"
    
    # Display summary metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total POs", f"{total_pos:,}")
    
    with summary_col2:
        st.metric("Contract", contract_compliance)
    
    with summary_col3:
        st.metric("Policy", policy_compliance)
    
    with summary_col4:
        st.metric("Risk", "Medium")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("📄 Contract Compliance")
        if not st.session_state.contracts.empty:
            contract_data, contract_msg = calculate_contract_compliance_rate(st.session_state.contracts, po_df)
            st.metric("Contract", contract_msg)
            if not contract_data.empty:
                # Create more interpretable contract compliance analysis
                compliance_analysis = contract_data.groupby('compliance_status').size().reset_index(name='count')
                compliance_analysis['percentage'] = (compliance_analysis['count'] / compliance_analysis['count'].sum() * 100).round(1)
                
                # Create bar chart for compliance status
                fig_contract = px.bar(
                    compliance_analysis, 
                    x='compliance_status', 
                    y='count',
                    title='Contract Compliance Status',
                    labels={'compliance_status': 'Status', 'count': 'Number of Contracts'},
                    color='compliance_status',
                    color_discrete_map={'Compliant': 'green', 'Non-Compliant': 'red'}
                )
                fig_contract.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_contract, use_container_width=True, key="contract_compliance_chart")
                
                # Add insights
                if len(compliance_analysis) > 0:
                    compliant_count = compliance_analysis[compliance_analysis['compliance_status'] == 'Compliant']['count'].iloc[0] if len(compliance_analysis[compliance_analysis['compliance_status'] == 'Compliant']) > 0 else 0
                    total_contracts = compliance_analysis['count'].sum()
                    st.write("Compliant Contracts: " + str(compliant_count) + "/" + str(total_contracts))
                
                # Show compliance data table
                st.write("📊 Compliance Data")
                compliance_display = compliance_analysis.copy()
                compliance_display.columns = ['Status', 'Count', 'Percentage']
                display_dataframe_with_index_1(compliance_display)
        else:
            st.info("Add contract data to see compliance analysis")
    
    with col2:
        st.write("📋 Policy Compliance")
        if not st.session_state.budgets.empty:
            policy_data, policy_msg = calculate_policy_compliance_rate(po_df)
            st.metric("Policy", policy_msg)
            
            # Create more interpretable policy compliance analysis
            if not policy_data.empty:
                # Create pie chart for policy compliance status
                fig_policy = px.pie(
                    policy_data, 
                    values='count', 
                    names='status',
                    title='Policy Compliance Status',
                    color='status',
                    color_discrete_map={'Compliant': 'green', 'Non-Compliant': 'red'}
                )
                fig_policy.update_layout(
                    showlegend=True
                )
                st.plotly_chart(fig_policy, use_container_width=True, key="policy_compliance_chart")
                
                # Add insights
                if len(policy_data) > 0:
                    compliant_count = policy_data[policy_data['status'] == 'Compliant']['count'].iloc[0] if len(policy_data[policy_data['status'] == 'Compliant']) > 0 else 0
                    total_pos = policy_data['count'].sum()
                    st.write("Compliant POs: " + str(compliant_count) + "/" + str(total_pos))
                
                # Show policy compliance data table
                st.write("📊 Policy Data")
                policy_display = policy_data.copy()
                policy_display.columns = ['Status', 'Count']
                display_dataframe_with_index_1(policy_display)
        else:
            st.info("Add budget data to see policy compliance")
    
    with col3:
        st.write("⚠️ Risk Assessment")
        if not st.session_state.suppliers.empty:
            risk_data, risk_msg = calculate_supplier_risk_assessment(
                st.session_state.suppliers, 
                st.session_state.purchase_orders,
                st.session_state.deliveries if 'deliveries' in st.session_state else None,
                st.session_state.invoices if 'invoices' in st.session_state else None,
                st.session_state.contracts if 'contracts' in st.session_state else None
            )
            st.metric("Risk", risk_msg)
            
            if not risk_data.empty:
                # Create more interpretable risk assessment analysis
                risk_analysis = risk_data.groupby('risk_level').agg({
                    'supplier_name': 'count',
                    'spend_percentage': 'sum',
                    'total_risk_score': 'mean'
                }).reset_index()
                risk_analysis.columns = ['risk_level', 'supplier_count', 'total_spend_percentage', 'avg_risk_score']
                
                # Create bar chart for risk distribution
                fig_risk = px.bar(
                    risk_analysis, 
                    x='risk_level', 
                    y='supplier_count',
                    title='Supplier Risk Distribution',
                    labels={'risk_level': 'Risk Level', 'supplier_count': 'Number of Suppliers'},
                    color='avg_risk_score',
                    color_continuous_scale='Reds'  # Red for higher risk
                )
                fig_risk.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=True
                )
                st.plotly_chart(fig_risk, use_container_width=True, key="risk_assessment_chart")
                
                # Add insights
                if len(risk_analysis) > 0:
                    high_risk_count = risk_analysis[risk_analysis['risk_level'] == 'High']['supplier_count'].sum()
                    total_suppliers = risk_analysis['supplier_count'].sum()
                    st.write("High Risk Suppliers: " + str(high_risk_count) + "/" + str(total_suppliers))
                
                # Show risk assessment data table
                st.write("📊 Risk Data")
                risk_display = risk_data[['supplier_name', 'spend_percentage', 'total_risk_score', 'risk_level']].copy()
                risk_display.columns = ['Supplier', 'Spend %', 'Risk Score', 'Risk Level']
                display_dataframe_with_index_1(risk_display)
        else:
            st.info("Add supplier data to see risk assessment")
    

    
    # Comprehensive Risk Analysis Section
    st.markdown("---")
    st.markdown("## 🚨 Comprehensive Risk Analysis")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first to perform comprehensive risk analysis.")
    else:
        # Initialize risk analyzer
        risk_analyzer = ProcurementRiskAnalyzer(
            purchase_orders=st.session_state.purchase_orders,
            suppliers=st.session_state.suppliers,
            items_data=st.session_state.items_data,
            deliveries=st.session_state.deliveries,
            invoices=st.session_state.invoices,
            contracts=st.session_state.contracts,
            budgets=st.session_state.budgets,
            rfqs=st.session_state.rfqs
        )
        
        # Generate comprehensive risk report
        risk_report = risk_analyzer.generate_comprehensive_risk_report()
        
        # Display risk dashboard
        display_risk_dashboard(risk_report)

def show_inventory_management():
    st.header("📦 Inventory & Stock Management")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="inventory_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="inventory_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary inventory metrics
    st.markdown("**📈 Inventory Summary Dashboard**")
    
    # Calculate relevant inventory metrics
    total_items = len(po_df['item_id'].unique()) if not po_df.empty else 0
    total_quantity_ordered = po_df['quantity'].sum() if not po_df.empty else 0
    avg_order_quantity = total_quantity_ordered / len(po_df) if len(po_df) > 0 else 0
    
    # Calculate item frequency (how often each item is ordered)
    item_frequency = po_df['item_id'].value_counts()
    high_frequency_items = len(item_frequency[item_frequency > 1]) if len(item_frequency) > 0 else 0
    low_frequency_items = len(item_frequency[item_frequency == 1]) if len(item_frequency) > 0 else 0
    
    # Calculate average lead time if delivery data is available
    avg_lead_time = 0
    if not st.session_state.deliveries.empty and 'delivery_date' in st.session_state.deliveries.columns:
        try:
            # Calculate days between order and delivery
            merged_delivery = po_df.merge(
                st.session_state.deliveries[['po_id', 'delivery_date']], 
                on='po_id', 
                how='inner'
            )
            if not merged_delivery.empty and 'order_date' in merged_delivery.columns:
                merged_delivery['order_date'] = pd.to_datetime(merged_delivery['order_date'])
                merged_delivery['delivery_date'] = pd.to_datetime(merged_delivery['delivery_date'])
                merged_delivery['lead_time_days'] = (merged_delivery['delivery_date'] - merged_delivery['order_date']).dt.days
                avg_lead_time = merged_delivery['lead_time_days'].mean()
        except:
            avg_lead_time = 0
    
    # Display summary metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Unique Items", f"{total_items:,}")
    
    with summary_col2:
        st.metric("Total Quantity", f"{total_quantity_ordered:,}")
    
    with summary_col3:
        st.metric("High Frequency Items", f"{high_frequency_items}")
    
    with summary_col4:
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("🔄 Inventory Turnover")
        turnover_data, turnover_msg = calculate_inventory_turnover_rate(po_df, st.session_state.deliveries)
        st.metric("Turnover", turnover_msg)
        
        if not turnover_data.empty:
            # Create more interpretable inventory turnover analysis
            if not st.session_state.items_data.empty:
                # Analyze turnover by item category
                po_with_items = po_df.merge(
                    st.session_state.items_data[['item_id', 'category']], 
                    on='item_id', 
                    how='left'
                )
                po_with_items['total_spend'] = po_with_items['quantity'] * po_with_items['unit_price']
                
                category_turnover = po_with_items.groupby('category').agg({
                    'total_spend': 'sum',
                    'po_id': 'count'
                }).reset_index()
                category_turnover.columns = ['category', 'total_spend', 'po_count']
                category_turnover['avg_order_value'] = category_turnover['total_spend'] / category_turnover['po_count']
                category_turnover['turnover_rate'] = category_turnover['total_spend'] / 100000  # Assuming avg inventory value
                
                # Sort by turnover rate for better visualization
                category_turnover = category_turnover.sort_values('turnover_rate', ascending=False)
                
                # Create bar chart for turnover by category
                fig_turnover = px.bar(
                    category_turnover, 
                    x='category', 
                    y='turnover_rate',
                    title='Inventory Turnover by Category',
                    labels={'category': 'Category', 'turnover_rate': 'Turnover Rate'},
                    color='total_spend',
                    color_continuous_scale='Blues'
                )
                fig_turnover.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_turnover, use_container_width=True, key="inventory_turnover_chart")
                
                # Add insights
                if len(category_turnover) > 0:
                    best_category = category_turnover.iloc[0]  # Already sorted by turnover rate descending
                    avg_turnover = category_turnover['turnover_rate'].mean()
                    st.write("Best Category: " + best_category['category'] + " - " + f"{best_category['turnover_rate']:.2f}")
                    st.write("Average Turnover: " + f"{avg_turnover:.2f}")
                
                # Show turnover data table
                st.write("📊 Turnover Data")
                turnover_display = category_turnover.copy()
                turnover_display.columns = ['Category', 'Total Spend', 'PO Count', 'Avg Order Value', 'Turnover Rate']
                display_dataframe_with_index_1(turnover_display)
    
    with col2:
        st.write("❌ Stockout Analysis")
        if not st.session_state.deliveries.empty:
            stockout_data, stockout_msg = calculate_stockout_rate(st.session_state.deliveries)
            st.metric("Stockout", stockout_msg)
            
            if not stockout_data.empty:
                # Create more interpretable stockout analysis
                stockout_rate = stockout_data['value'].iloc[0] if 'value' in stockout_data.columns else 0
                stockout_analysis = pd.DataFrame({
                    'status': ['Stockout', 'Available'],
                    'count': [stockout_rate, 100 - stockout_rate]
                })
                
                # Create bar chart for stockout status
                fig_stockout = px.bar(
                    stockout_analysis, 
                    x='status', 
                    y='count',
                    title='Stockout Analysis',
                    labels={'status': 'Stockout Status', 'count': 'Percentage'},
                    color='status',
                    color_discrete_map={'Stockout': 'red', 'Available': 'green'}
                )
                fig_stockout.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_stockout, use_container_width=True, key="inventory_stockout_chart")
                
                # Add insights
                if len(stockout_analysis) > 0:
                    stockout_count = stockout_analysis[stockout_analysis['status'] == 'Stockout']['count'].iloc[0] if len(stockout_analysis[stockout_analysis['status'] == 'Stockout']) > 0 else 0
                    total_orders = stockout_analysis['count'].sum()
                    st.write("Stockout Rate: " + f"{stockout_count:.1f}%")
                
                # Show stockout data table
                st.write("📊 Stockout Data")
                stockout_display = stockout_analysis.copy()
                stockout_display.columns = ['Stockout Status', 'Count']
                display_dataframe_with_index_1(stockout_display)
        else:
            st.info("Add delivery data to see stockout analysis")
    
    with col3:
        st.write("📦 Item Performance")
        if not st.session_state.items_data.empty:
            # Create item performance analysis
            # Group by item name only to avoid duplicate items
            po_with_items = st.session_state.purchase_orders.merge(
                st.session_state.items_data[['item_id', 'item_name']], 
                on='item_id', 
                how='left'
            )
            po_with_items['total_spend'] = po_with_items['quantity'] * po_with_items['unit_price']
            
            item_performance = po_with_items.groupby('item_name').agg({
                'total_spend': 'sum',
                'quantity': 'sum',
                'po_id': 'count'
            }).reset_index()
            item_performance.columns = ['item_name', 'total_spend', 'total_quantity', 'po_count']
            item_performance['avg_unit_price'] = item_performance['total_spend'] / item_performance['total_quantity']
            
            # Get the correct category for each item from the items data
            if not st.session_state.items_data.empty:
                category_col = get_column_name(st.session_state.items_data, 'category')
                item_name_col = get_column_name(st.session_state.items_data, 'item_name')
                
                if category_col is not None and item_name_col is not None:
                    item_performance = item_performance.merge(
                        st.session_state.items_data[[item_name_col, category_col]], 
                        left_on='item_name', 
                        right_on=item_name_col,
                        how='left'
                    )
                    # Use the category from items data, not from merged data
                    item_performance['category'] = item_performance[category_col]
                    # Clean up duplicate columns
                    columns_to_drop = [category_col]
                    if f'{item_name_col}_y' in item_performance.columns:
                        columns_to_drop.append(f'{item_name_col}_y')
                    item_performance = item_performance.drop(columns=columns_to_drop)
                else:
                    item_performance['category'] = 'Unknown'
            else:
                item_performance['category'] = 'Unknown'
            
            # Ensure category column exists
            if 'category' not in item_performance.columns:
                item_performance['category'] = 'Unknown'
            
            # Sort by total spend for better visualization
            item_performance = item_performance.sort_values('total_spend', ascending=False).head(10)
            
            # Create bar chart for top items by spend
            fig_items = px.bar(
                item_performance, 
                x='item_name', 
                y='total_spend',
                title='Top Items by Spend',
                labels={'item_name': 'Item Name', 'total_spend': 'Total Spend ($)'},
                color_discrete_sequence=['#1f77b4']  # Single blue color for all bars
            )
            fig_items.update_layout(
                xaxis_tickangle=-45,
                showlegend=False
            )
            st.plotly_chart(fig_items, use_container_width=True, key="item_performance_chart")
            
            # Add insights
            if len(item_performance) > 0:
                top_item = item_performance.iloc[0]  # Already sorted by total spend descending
                total_item_spend = item_performance['total_spend'].sum()
                st.write("Top Item: " + top_item['item_name'] + " - $" + f"{top_item['total_spend']:,.0f}")
                st.write("Total Item Spend: $" + f"{total_item_spend:,.0f}")
            
            # Show item performance data table
            st.write("📊 Item Data")
            item_display = item_performance.copy()
            item_display.columns = ['Item Name', 'Category', 'Total Spend', 'Total Quantity', 'PO Count', 'Avg Unit Price']
            display_dataframe_with_index_1(item_display)
        else:
            st.info("Add item data to see performance analysis")
    
    st.markdown("---")
    
    # Add Inventory Tracking Section
    st.subheader("📦 Current Inventory Levels")
    
    if not st.session_state.items_data.empty and not po_df.empty:
        # Calculate current inventory levels based on orders and deliveries
        inventory_data = po_df.merge(
            st.session_state.items_data[['item_id', 'item_name']], 
            on='item_id', 
            how='left'
        )
        
        # Group by item to get total ordered quantities
        item_inventory = inventory_data.groupby('item_name').agg({
            'quantity': 'sum',
            'po_id': 'count',
            'unit_price': 'mean'
        }).reset_index()
        item_inventory.columns = ['Item Name', 'Total Ordered', 'Order Count', 'Avg Unit Price']
        
        # Calculate estimated current inventory (assuming some consumption)
        # This is a simplified model - in real scenarios, you'd have actual inventory data
        item_inventory['Estimated Current Stock'] = item_inventory['Total Ordered'] * 0.3  # Assume 30% remaining
        item_inventory['Inventory Value'] = item_inventory['Estimated Current Stock'] * item_inventory['Avg Unit Price']
        
        # Sort by inventory value for better visualization
        item_inventory = item_inventory.sort_values('Inventory Value', ascending=False).head(15)
        
        # Create inventory levels chart
        fig_inventory = px.bar(
            item_inventory,
            x='Item Name',
            y='Estimated Current Stock',
            title='Current Inventory Levels (Estimated)',
            labels={'Item Name': 'Item', 'Estimated Current Stock': 'Current Stock'},
            color_discrete_sequence=['#2ca02c']  # Green for inventory
        )
        fig_inventory.update_layout(
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_inventory, use_container_width=True)
        
        # Add inventory insights
        if len(item_inventory) > 0:
            total_inventory_value = item_inventory['Inventory Value'].sum()
            avg_stock_level = item_inventory['Estimated Current Stock'].mean()
            high_stock_items = len(item_inventory[item_inventory['Estimated Current Stock'] > avg_stock_level])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Inventory Value", f"${total_inventory_value:,.0f}")
            with col2:
                st.metric("Avg Stock Level", f"{avg_stock_level:.0f} units")
            with col3:
                st.metric("High Stock Items", f"{high_stock_items}")
        
        # Show inventory data table
        st.subheader("📊 Inventory Data")
        inventory_display = item_inventory.copy()
        inventory_display.columns = ['Item Name', 'Total Ordered', 'Order Count', 'Avg Unit Price', 'Current Stock', 'Inventory Value']
        inventory_display['Inventory Value'] = inventory_display['Inventory Value'].round(2)
        display_dataframe_with_index_1(inventory_display)
        
        # Add inventory alerts
        st.subheader("🚨 Inventory Alerts")
        
        # Identify potential issues
        low_stock_threshold = item_inventory['Estimated Current Stock'].quantile(0.25)  # Bottom 25%
        high_stock_threshold = item_inventory['Estimated Current Stock'].quantile(0.75)  # Top 25%
        
        low_stock_items = item_inventory[item_inventory['Estimated Current Stock'] <= low_stock_threshold]
        high_stock_items = item_inventory[item_inventory['Estimated Current Stock'] >= high_stock_threshold]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⚠️ Low Stock Items**")
            if not low_stock_items.empty:
                for _, item in low_stock_items.iterrows():
                    st.write(f"• {item['Item Name']}: {item['Estimated Current Stock']:.0f} units")
            else:
                st.write("No low stock items detected")
        
        with col2:
            st.markdown("**📦 High Stock Items**")
            if not high_stock_items.empty:
                for _, item in high_stock_items.iterrows():
                    st.write(f"• {item['Item Name']}: {item['Estimated Current Stock']:.0f} units")
            else:
                st.write("No high stock items detected")
    else:
        st.info("Add purchase order and items data to see inventory tracking")
    


def show_market_insights():
    st.header("🌍 Market & Price Analysis")
    
    # Add explanation of what this section provides
    with st.expander("ℹ️ About This Analysis", expanded=False):
        st.markdown("""
        **What This Section Provides:**
        - **Internal Price Analysis**: Analysis of price variations within your own procurement data
        - **Supplier Competition**: Assessment of supplier diversity and competition levels
        - **Price Efficiency**: Comparison of your current prices to your own minimum prices
        - **Market Positioning**: Your organization's pricing patterns relative to your supplier base
        
        **For True Market Benchmarking, You Would Need:**
        - External market price indices
        - Industry average pricing data
        - Competitor pricing information
        - Market research reports
        - Third-party benchmarking services
        """)
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="market_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="market_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary market metrics
    st.markdown("**📈 Market Summary Dashboard**")
    
    # Calculate overall market metrics
    total_items = len(po_df['item_id'].unique()) if not po_df.empty else 0
    total_spend = (po_df['quantity'] * po_df['unit_price']).sum() if not po_df.empty else 0
    avg_unit_price = po_df['unit_price'].mean() if not po_df.empty else 0
    
    # Calculate price volatility across all items
    price_volatility = 0
    if not po_df.empty:
        item_price_stats = po_df.groupby('item_id')['unit_price'].agg(['mean', 'std']).reset_index()
        item_price_stats['cv'] = item_price_stats['std'] / item_price_stats['mean']  # Coefficient of variation
        price_volatility = item_price_stats['cv'].mean() * 100  # Convert to percentage
    
    # Display summary metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Unique Items", f"{total_items:,}")
    
    with summary_col2:
        st.metric("Total Spend", f"${total_spend:,.0f}")
    
    with summary_col3:
        st.metric("Avg Unit Price", f"${avg_unit_price:.2f}")
    
    with summary_col4:
        st.metric("Price Volatility", f"{price_volatility:.1f}%")
    
    st.markdown("---")
    
    # Item-Level Price Analysis
    st.subheader("📊 Item-Level Price Analysis")
    
    if not st.session_state.items_data.empty and not po_df.empty:
        # Merge purchase orders with items data
        po_with_items = po_df.merge(
            st.session_state.items_data[['item_id', 'item_name']], 
            on='item_id', 
            how='left'
        )
        
        # Calculate comprehensive price statistics for each item
        item_price_analysis = po_with_items.groupby('item_name').agg({
            'unit_price': ['mean', 'std', 'min', 'max', 'count'],
            'quantity': 'sum',
            'po_id': 'nunique'
        }).reset_index()
        
        # Flatten column names
        item_price_analysis.columns = ['Item Name', 'Avg Price', 'Price Std', 'Min Price', 'Max Price', 'Order Count', 'Total Quantity', 'Supplier Count']
        
        # Calculate additional metrics
        item_price_analysis['Price Range'] = item_price_analysis['Max Price'] - item_price_analysis['Min Price']
        item_price_analysis['Price Volatility %'] = (item_price_analysis['Price Std'] / item_price_analysis['Avg Price'] * 100).round(2)
        item_price_analysis['Total Spend'] = item_price_analysis['Avg Price'] * item_price_analysis['Total Quantity']
        
        # Sort by total spend for better visualization
        item_price_analysis = item_price_analysis.sort_values('Total Spend', ascending=False)
        
        # Display top items by spend
        st.markdown("**💰 Top Items by Total Spend**")
        
        # Create price analysis chart
        fig_price_analysis = px.scatter(
            item_price_analysis.head(15),
            x='Avg Price',
            y='Price Volatility %',
            size='Total Spend',
            color='Supplier Count',
            hover_data=['Item Name', 'Total Quantity', 'Order Count'],
            title='Price Analysis: Average Price vs Volatility (Top 15 Items)',
            labels={'Avg Price': 'Average Price ($)', 'Price Volatility %': 'Price Volatility (%)', 'Total Spend': 'Total Spend ($)', 'Supplier Count': 'Number of Suppliers'},
            color_continuous_scale='Viridis'
        )
        fig_price_analysis.update_layout(
            showlegend=True
        )
        st.plotly_chart(fig_price_analysis, use_container_width=True)
        
        # Price summary table
        st.markdown("**📋 Detailed Price Summary**")
        price_summary_display = item_price_analysis.head(20).copy()
        price_summary_display = price_summary_display[['Item Name', 'Avg Price', 'Min Price', 'Max Price', 'Price Volatility %', 'Total Quantity', 'Order Count', 'Supplier Count', 'Total Spend']]
        price_summary_display.columns = ['Item Name', 'Avg Price ($)', 'Min Price ($)', 'Max Price ($)', 'Volatility (%)', 'Total Qty', 'Orders', 'Suppliers', 'Total Spend ($)']
        price_summary_display['Avg Price ($)'] = price_summary_display['Avg Price ($)'].round(2)
        price_summary_display['Min Price ($)'] = price_summary_display['Min Price ($)'].round(2)
        price_summary_display['Max Price ($)'] = price_summary_display['Max Price ($)'].round(2)
        price_summary_display['Total Spend ($)'] = price_summary_display['Total Spend ($)'].round(2)
        display_dataframe_with_index_1(price_summary_display)
        
        st.markdown("---")
        
        # Price Trend Analysis
        st.subheader("📈 Price Trend Analysis")
        
        # Calculate price trends over time for each item
        if 'order_date' in po_with_items.columns:
            po_with_items['order_date'] = pd.to_datetime(po_with_items['order_date'])
            po_with_items['month'] = po_with_items['order_date'].dt.to_period('M')
            
            # Get items with multiple orders for trend analysis
            items_with_trends = po_with_items.groupby('item_name').filter(lambda x: len(x) >= 3)
            
            if not items_with_trends.empty:
                # Calculate monthly average prices for trend items
                monthly_prices = items_with_trends.groupby(['item_name', 'month'])['unit_price'].mean().reset_index()
                monthly_prices['month'] = monthly_prices['month'].astype(str)
                
                # Get list of items with trends for selection
                available_items = sorted(items_with_trends['item_name'].unique())
                
                # Item selection interface
                st.markdown("**🔍 Select Item for Detailed Trend Analysis**")
                selected_item = st.selectbox(
                    "Choose an item to analyze:",
                    options=available_items,
                    index=0 if available_items else None,
                    key="trend_item_selector"
                )
                
                if selected_item:
                    # Filter data for selected item
                    item_trend_data = monthly_prices[monthly_prices['item_name'] == selected_item]
                    item_raw_data = po_with_items[po_with_items['item_name'] == selected_item]
                    
                    if not item_trend_data.empty:
                        # Create detailed trend chart for selected item
                        fig_item_trend = px.line(
                            item_trend_data,
                            x='month',
                            y='unit_price',
                            title=f'Price Trend for: {selected_item}',
                            labels={'month': 'Month', 'unit_price': 'Average Price ($)'},
                            markers=True
                        )
                        fig_item_trend.update_layout(
                            xaxis_tickangle=-45,
                            showlegend=False
                        )
                        st.plotly_chart(fig_item_trend, use_container_width=True)
                        
                        # Calculate detailed statistics for selected item
                        st.markdown("**📊 Detailed Trend Statistics**")
                        
                        # Basic trend stats
                        first_price = item_trend_data.iloc[0]['unit_price']
                        last_price = item_trend_data.iloc[-1]['unit_price']
                        price_change = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
                        trend_direction = "↗️ Increasing" if price_change > 0 else "↘️ Decreasing" if price_change < 0 else "→ Stable"
                        
                        # Calculate additional statistics
                        min_price = item_trend_data['unit_price'].min()
                        max_price = item_trend_data['unit_price'].max()
                        avg_price = item_trend_data['unit_price'].mean()
                        price_volatility = (item_trend_data['unit_price'].std() / avg_price * 100) if avg_price > 0 else 0
                        
                        # Display statistics in columns
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("First Price", f"${first_price:.2f}")
                        with col2:
                            st.metric("Last Price", f"${last_price:.2f}")
                        with col3:
                            st.metric("Price Change", f"{price_change:.1f}%", delta=f"{price_change:.1f}%")
                        with col4:
                            st.metric("Trend", trend_direction)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Min Price", f"${min_price:.2f}")
                        with col2:
                            st.metric("Max Price", f"${max_price:.2f}")
                        with col3:
                            st.metric("Avg Price", f"${avg_price:.2f}")
                        with col4:
                            st.metric("Volatility", f"{price_volatility:.1f}%")
                        
                        # Price range analysis
                        st.markdown("**📈 Price Range Analysis**")
                        price_range = max_price - min_price
                        price_range_percent = (price_range / avg_price * 100) if avg_price > 0 else 0
                        
                        if price_range_percent > 30:
                            st.warning(f"**High Price Variation**: Price range is ${price_range:.2f} ({price_range_percent:.1f}% of average) - Significant negotiation opportunity")
                        elif price_range_percent > 15:
                            st.info(f"**Moderate Price Variation**: Price range is ${price_range:.2f} ({price_range_percent:.1f}% of average) - Some optimization potential")
                        else:
                            st.success(f"**Low Price Variation**: Price range is ${price_range:.2f} ({price_range_percent:.1f}% of average) - Stable pricing")
                        
                        # Supplier analysis for this item
                        st.markdown("**🏢 Supplier Analysis for This Item**")
                        item_suppliers = item_raw_data.groupby('supplier_id').agg({
                            'unit_price': ['mean', 'count'],
                            'quantity': 'sum'
                        }).reset_index()
                        
                        # Flatten column names
                        item_suppliers.columns = ['supplier_id', 'avg_price', 'order_count', 'total_quantity']
                        
                        # Merge with supplier names
                        if not st.session_state.suppliers.empty:
                            item_suppliers = item_suppliers.merge(
                                st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                                on='supplier_id', 
                                how='left'
                            )
                            
                            # Calculate total spend per supplier
                            item_suppliers['total_spend'] = item_suppliers['avg_price'] * item_suppliers['total_quantity']
                            
                            # Sort by total spend
                            item_suppliers = item_suppliers.sort_values('total_spend', ascending=False)
                            
                            # Display supplier comparison
                            supplier_display = item_suppliers[['supplier_name', 'avg_price', 'order_count', 'total_quantity', 'total_spend']].copy()
                            supplier_display.columns = ['Supplier', 'Avg Price ($)', 'Orders', 'Total Qty', 'Total Spend ($)']
                            supplier_display['Avg Price ($)'] = supplier_display['Avg Price ($)'].round(2)
                            supplier_display['Total Spend ($)'] = supplier_display['Total Spend ($)'].round(2)
                            
                            st.write("**Supplier Comparison:**")
                            display_dataframe_with_index_1(supplier_display)
                            
                            # Identify best and worst suppliers
                            if len(supplier_display) > 1:
                                best_supplier = supplier_display.iloc[supplier_display['Avg Price ($)'].idxmin()]
                                worst_supplier = supplier_display.iloc[supplier_display['Avg Price ($)'].idxmax()]
                                
                                price_diff = worst_supplier['Avg Price ($)'] - best_supplier['Avg Price ($)']
                                savings_potential = price_diff * supplier_display['Total Qty'].sum()
                                
                                st.markdown("**💰 Optimization Insights**")
                                st.write(f"• **Best Price**: {best_supplier['Supplier']} at ${best_supplier['Avg Price ($)']:.2f}")
                                st.write(f"• **Highest Price**: {worst_supplier['Supplier']} at ${worst_supplier['Avg Price ($)']:.2f}")
                                st.write(f"• **Price Difference**: ${price_diff:.2f} per unit")
                                st.write(f"• **Potential Savings**: ${savings_potential:.2f} if all orders went to best supplier")
                        
                        # Monthly breakdown table
                        st.markdown("**📅 Monthly Price Breakdown**")
                        monthly_display = item_trend_data.copy()
                        monthly_display.columns = ['Item', 'Month', 'Avg Price ($)']
                        monthly_display['Avg Price ($)'] = monthly_display['Avg Price ($)'].round(2)
                        display_dataframe_with_index_1(monthly_display[['Month', 'Avg Price ($)']])
                        
                    else:
                        st.warning(f"No trend data available for {selected_item}")
                else:
                    st.info("Select an item to see detailed trend analysis")
            else:
                st.info("No items with sufficient order history (minimum 3 orders) for trend analysis")
        
        st.markdown("---")
        
        # Price Anomaly Detection
        st.subheader("🚨 Price Anomaly Detection")
        
        # Identify items with unusual price patterns
        high_volatility_items = item_price_analysis[item_price_analysis['Price Volatility %'] > 20].sort_values('Price Volatility %', ascending=False)
        high_price_range_items = item_price_analysis[item_price_analysis['Price Range'] > item_price_analysis['Avg Price']].sort_values('Price Range', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⚠️ High Price Volatility Items**")
            if not high_volatility_items.empty:
                volatility_display = high_volatility_items.head(10)[['Item Name', 'Price Volatility %', 'Avg Price', 'Supplier Count']]
                volatility_display.columns = ['Item', 'Volatility (%)', 'Avg Price ($)', 'Suppliers']
                volatility_display['Avg Price ($)'] = volatility_display['Avg Price ($)'].round(2)
                display_dataframe_with_index_1(volatility_display)
            else:
                st.write("No high volatility items detected")
        
        with col2:
            st.markdown("**💰 Large Price Range Items**")
            if not high_price_range_items.empty:
                range_display = high_price_range_items.head(10)[['Item Name', 'Price Range', 'Min Price', 'Max Price']]
                range_display.columns = ['Item', 'Price Range ($)', 'Min Price ($)', 'Max Price ($)']
                range_display['Price Range ($)'] = range_display['Price Range ($)'].round(2)
                range_display['Min Price ($)'] = range_display['Min Price ($)'].round(2)
                range_display['Max Price ($)'] = range_display['Max Price ($)'].round(2)
                display_dataframe_with_index_1(range_display)
            else:
                st.write("No large price range items detected")
        
            # Market Insights Summary
        st.markdown("---")
        st.subheader("💡 Market Insights Summary")
        
        # Generate insights based on the data
        insights = []
        
        # Price volatility insights
        avg_volatility = item_price_analysis['Price Volatility %'].mean()
        if avg_volatility > 15:
            insights.append(f"**High Internal Price Volatility**: Average price volatility is {avg_volatility:.1f}%, indicating significant price variations across your suppliers.")
        else:
            insights.append(f"**Stable Internal Pricing**: Average price volatility is {avg_volatility:.1f}%, showing consistent pricing across your supplier base.")
        
        # Supplier competition insights
        avg_suppliers = item_price_analysis['Supplier Count'].mean()
        if avg_suppliers > 2:
            insights.append(f"**Good Supplier Competition**: Average of {avg_suppliers:.1f} suppliers per item, providing competitive pricing opportunities.")
        else:
            insights.append(f"**Limited Competition**: Average of {avg_suppliers:.1f} suppliers per item, consider expanding supplier base.")
        
        # Price range insights
        avg_price_range = item_price_analysis['Price Range'].mean()
        if avg_price_range > item_price_analysis['Avg Price'].mean() * 0.5:
            insights.append(f"**Large Price Variations**: Average price range of ${avg_price_range:.2f} suggests significant negotiation opportunities.")
        else:
            insights.append(f"**Consistent Pricing**: Average price range of ${avg_price_range:.2f} indicates stable pricing conditions.")
        
        # Market positioning insights
        st.markdown("**🎯 Market Positioning Analysis**")
        
        # Calculate market positioning metrics
        if not po_df.empty:
            # Price efficiency analysis (comparing to internal benchmarks)
            price_efficiency = []
            for _, item in item_price_analysis.head(10).iterrows():
                item_name = item['Item Name']
                avg_price = item['Avg Price']
                min_price = item['Min Price']
                
                # Calculate efficiency as percentage above minimum
                efficiency = ((avg_price - min_price) / min_price * 100) if min_price > 0 else 0
                
                if efficiency > 20:
                    price_efficiency.append(f"**{item_name}**: {efficiency:.1f}% above minimum price - High negotiation potential")
                elif efficiency > 10:
                    price_efficiency.append(f"**{item_name}**: {efficiency:.1f}% above minimum price - Moderate optimization opportunity")
                else:
                    price_efficiency.append(f"**{item_name}**: {efficiency:.1f}% above minimum price - Well optimized")
            
            # Display price efficiency insights
            st.markdown("**💰 Price Efficiency Analysis**")
            for insight in price_efficiency[:5]:  # Show top 5
                st.write(f"• {insight}")
        
        # Supplier market share analysis
        if not st.session_state.suppliers.empty:
            st.markdown("**🏢 Supplier Market Share**")
            supplier_analysis = po_df.groupby('supplier_id').agg({
                'po_id': 'count',
                'quantity': 'sum',
                'unit_price': 'mean'
            }).reset_index()
            
            # Merge with supplier names
            supplier_analysis = supplier_analysis.merge(
                st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                on='supplier_id', 
                how='left'
            )
            
            supplier_analysis['total_spend'] = supplier_analysis['quantity'] * supplier_analysis['unit_price']
            total_market_spend = supplier_analysis['total_spend'].sum()
            supplier_analysis['market_share'] = (supplier_analysis['total_spend'] / total_market_spend * 100).round(2)
            
            # Sort by market share
            supplier_analysis = supplier_analysis.sort_values('market_share', ascending=False)
            
            # Display top suppliers
            st.write("**Top Suppliers by Spend:**")
            for _, supplier in supplier_analysis.head(3).iterrows():
                st.write(f"• **{supplier['supplier_name']}**: {supplier['market_share']:.1f}% of total spend")
        
        # Display general insights
        st.markdown("**📊 General Market Insights**")
        for insight in insights:
            st.info(insight)
    
    else:
        st.info("Add purchase order and items data to see market insights")
    


def show_contract_management():
    st.header("📄 Contract Management")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="contract_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="contract_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    # Summary contract metrics
    st.markdown("**📈 Contract Summary Dashboard**")
    
    # Calculate overall contract metrics
    total_contracts = len(st.session_state.contracts) if not st.session_state.contracts.empty else 0
    total_contract_value = st.session_state.contracts['contract_value'].sum() if not st.session_state.contracts.empty else 0
    
    # Get utilization and renewal data
    # utilization_data, utilization_msg = calculate_contract_utilization_analysis(st.session_state.contracts, po_df)
    utilization_data, utilization_msg = pd.DataFrame(), "No utilization data available"
    avg_utilization = utilization_data['utilization_rate'].mean() if not utilization_data.empty else 0
    
    renewal_data, renewal_msg = calculate_contract_renewal_analysis(st.session_state.contracts)
    expiring_count = 0
    if not st.session_state.contracts.empty:
        current_date = pd.Timestamp.now()
        contracts_with_dates = st.session_state.contracts.copy()
        contracts_with_dates['end_date'] = pd.to_datetime(contracts_with_dates['end_date'])
        expiring_contracts = contracts_with_dates[contracts_with_dates['end_date'] <= current_date + pd.Timedelta(days=30)]
        expiring_count = len(expiring_contracts)
    
    # Display summary metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total Contracts", f"{total_contracts:,}")
    
    with summary_col2:
        st.metric("Contract Value", f"${total_contract_value:,.0f}")
    
    with summary_col3:
        st.metric("Avg Utilization", f"{avg_utilization:.1f}%")
    
    with summary_col4:
        st.metric("Expiring Soon", f"{expiring_count}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("📈 Contract Utilization")
        if not st.session_state.contracts.empty:
            # utilization_data, utilization_msg = calculate_contract_utilization_analysis(st.session_state.contracts, st.session_state.purchase_orders)
            utilization_data, utilization_msg = pd.DataFrame(), "No utilization data available"
            st.metric("Utilization", utilization_msg)
            
            if not utilization_data.empty:
                # Create more interpretable contract utilization analysis
                if not st.session_state.suppliers.empty:
                    # Merge with supplier names for better analysis
                    utilization_with_suppliers = utilization_data.merge(
                        st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                        on='supplier_id', 
                        how='left'
                    )
                    
                    # Analyze utilization by supplier
                    supplier_utilization = utilization_with_suppliers.groupby('supplier_name').agg({
                        'utilization_rate': 'mean',
                        'contract_value': 'sum',
                        'total_spend': 'sum'
                    }).reset_index()
                    supplier_utilization.columns = ['supplier_name', 'avg_utilization', 'contract_value', 'actual_spend']
                    supplier_utilization['avg_utilization'] = supplier_utilization['avg_utilization'].round(2)
                    
                    # Sort by utilization rate for better visualization
                    supplier_utilization = supplier_utilization.sort_values('avg_utilization', ascending=False)
                    
                    # Create bar chart for utilization by supplier
                    fig_utilization = px.bar(
                        supplier_utilization, 
                        x='supplier_name', 
                        y='avg_utilization',
                        title='Contract Utilization by Supplier',
                        labels={'supplier_name': 'Supplier', 'avg_utilization': 'Utilization Rate (%)'},
                        color='contract_value',
                        color_continuous_scale='Blues'
                    )
                    fig_utilization.update_layout(
                        xaxis_tickangle=-45,
                        showlegend=False
                    )
                    st.plotly_chart(fig_utilization, use_container_width=True, key="contract_utilization_chart")
                    
                    # Add insights
                    if len(supplier_utilization) > 0:
                        best_utilization = supplier_utilization.iloc[0]  # Already sorted by utilization descending
                        avg_utilization = supplier_utilization['avg_utilization'].mean()
                        st.write("Best Utilization: " + best_utilization['supplier_name'] + " - " + str(best_utilization['avg_utilization']) + "%")
                        st.write("Average Utilization: " + str(avg_utilization) + "%")
                    
                    # Show utilization data table
                    st.write("📊 Utilization Data")
                    utilization_display = supplier_utilization.copy()
                    utilization_display.columns = ['Supplier', 'Avg Utilization (%)', 'Contract Value', 'Actual Spend']
                    display_dataframe_with_index_1(utilization_display)
        else:
            st.info("Add contract data to see utilization analysis")
    
    with col2:
        st.write("⏰ Contract Renewal")
        if not st.session_state.contracts.empty:
            renewal_data, renewal_msg = calculate_contract_renewal_analysis(st.session_state.contracts)
            st.metric("Renewal", renewal_msg)
            
            if not renewal_data.empty:
                # Create more interpretable contract renewal analysis
                # The renewal_data contains the analysis results, not the original contracts
                # We need to work with the original contracts data for detailed analysis
                if not st.session_state.contracts.empty:
                    contracts_with_dates = st.session_state.contracts.copy()
                    contracts_with_dates['end_date'] = pd.to_datetime(contracts_with_dates['end_date'])
                    current_date = pd.Timestamp.now()
                    
                    # Categorize contracts by expiration status
                    contracts_with_dates['days_to_expiry'] = (contracts_with_dates['end_date'] - current_date).dt.days
                    contracts_with_dates['expiry_status'] = pd.cut(
                        contracts_with_dates['days_to_expiry'],
                        bins=[-float('inf'), 0, 30, 90, float('inf')],
                        labels=['Expired', 'Expiring Soon', 'Expiring in 3 Months', 'Active']
                    )
                    
                    # Analyze by expiry status
                    expiry_analysis = contracts_with_dates.groupby('expiry_status').agg({
                        'contract_id': 'count',
                        'contract_value': 'sum'
                    }).reset_index()
                    expiry_analysis.columns = ['expiry_status', 'contract_count', 'total_value']
                    expiry_analysis['percentage'] = (expiry_analysis['contract_count'] / expiry_analysis['contract_count'].sum() * 100).round(1)
                else:
                    # Fallback to using the renewal_data if contracts are not available
                    expiry_analysis = renewal_data.copy()
                    expiry_analysis.columns = ['expiry_status', 'contract_count']
                    expiry_analysis['total_value'] = 0  # No value data available
                    expiry_analysis['percentage'] = (expiry_analysis['contract_count'] / expiry_analysis['contract_count'].sum() * 100).round(1)
                
                # Create bar chart for contract expiry status
                fig_renewal = px.bar(
                    expiry_analysis, 
                    x='expiry_status', 
                    y='contract_count',
                    title='Contract Expiry Status',
                    labels={'expiry_status': 'Status', 'contract_count': 'Number of Contracts'},
                    color='total_value',
                    color_continuous_scale='Reds'  # Red for urgency
                )
                fig_renewal.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_renewal, use_container_width=True, key="contract_renewal_chart")
                
                # Add insights
                if len(expiry_analysis) > 0:
                    expiring_soon = expiry_analysis[expiry_analysis['expiry_status'] == 'Expiring Soon']['contract_count'].iloc[0] if len(expiry_analysis[expiry_analysis['expiry_status'] == 'Expiring Soon']) > 0 else 0
                    total_contracts = expiry_analysis['contract_count'].sum()
                    st.write("Expiring Soon: " + str(expiring_soon) + "/" + str(total_contracts))
                
                # Show renewal data table
                st.write("📊 Renewal Data")
                renewal_display = expiry_analysis.copy()
                renewal_display.columns = ['Status', 'Contract Count', 'Total Value', 'Percentage']
                display_dataframe_with_index_1(renewal_display)
        else:
            st.info("Add contract data to see renewal tracking")
    
    with col3:
        st.write("📊 Contract Performance")
        if not st.session_state.contracts.empty:
            # Create contract performance analysis
            if not st.session_state.suppliers.empty:
                # Merge contracts with supplier data
                contracts_with_suppliers = st.session_state.contracts.merge(
                    st.session_state.suppliers[['supplier_id', 'supplier_name']], 
                    on='supplier_id', 
                    how='left'
                )
                
                # Calculate contract performance metrics
                contract_performance = contracts_with_suppliers.groupby('supplier_name').agg({
                    'contract_value': 'sum',
                    'contract_id': 'count',
                    'start_date': 'min',
                    'end_date': 'max'
                }).reset_index()
                contract_performance.columns = ['supplier_name', 'total_contract_value', 'contract_count', 'earliest_start', 'latest_end']
                
                # Calculate contract duration
                contract_performance['earliest_start'] = pd.to_datetime(contract_performance['earliest_start'])
                contract_performance['latest_end'] = pd.to_datetime(contract_performance['latest_end'])
                contract_performance['contract_duration_days'] = (contract_performance['latest_end'] - contract_performance['earliest_start']).dt.days
                contract_performance['avg_contract_value'] = contract_performance['total_contract_value'] / contract_performance['contract_count']
                
                # Sort by total contract value for better visualization
                contract_performance = contract_performance.sort_values('total_contract_value', ascending=False)
                
                # Create bar chart for contract value by supplier
                fig_performance = px.bar(
                    contract_performance, 
                    x='supplier_name', 
                    y='total_contract_value',
                    title='Contract Value by Supplier',
                    labels={'supplier_name': 'Supplier', 'total_contract_value': 'Total Contract Value ($)'},
                    color='contract_count',
                    color_continuous_scale='Greens'
                )
                fig_performance.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_performance, use_container_width=True, key="contract_performance_chart")
                
                # Add insights
                if len(contract_performance) > 0:
                    top_supplier = contract_performance.iloc[0]  # Already sorted by total contract value descending
                    total_value = contract_performance['total_contract_value'].sum()
                    st.write("Top Supplier: " + top_supplier['supplier_name'] + " - $" + f"{top_supplier['total_contract_value']:,.0f}")
                    st.write("Total Contract Value: $" + f"{total_value:,.0f}")
                
                # Show contract performance data table
                st.write("📊 Performance Data")
                performance_display = contract_performance.copy()
                performance_display.columns = ['Supplier', 'Total Value', 'Contract Count', 'Earliest Start', 'Latest End', 'Duration (Days)', 'Avg Value']
                display_dataframe_with_index_1(performance_display)
        else:
            st.info("Add supplier data to see contract performance")
    


def show_sustainability_csr():
    st.header("🌱 Sustainability & CSR")
    
    if st.session_state.purchase_orders.empty:
        st.warning("Please add purchase order data first in the Data Input section.")
        return
    
    # Add Year and Quarter Filter UI
    po_df = st.session_state.purchase_orders.copy()
    if not po_df.empty and 'order_date' in po_df.columns:
        po_df['order_date'] = pd.to_datetime(po_df['order_date'], errors='coerce')
        po_df = po_df.dropna(subset=['order_date'])
        po_df['year'] = po_df['order_date'].dt.year
        po_df['quarter'] = po_df['order_date'].dt.quarter
        years = sorted(po_df['year'].dropna().unique())
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        
        # Create filter UI in top-right
        filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
        with filter_col1:
            st.write("")  # Spacer
        with filter_col2:
            selected_year = st.selectbox('📅 Year', options=years, index=len(years)-1 if years else 0, key="sustainability_year_filter")
        with filter_col3:
            selected_quarter = st.selectbox('📊 Quarter', options=quarters, index=0, key="sustainability_quarter_filter")
        
        st.session_state.selected_year = selected_year
        st.session_state.selected_quarter = selected_quarter
    
    # Get filtered data
    po_df = get_filtered_po_df()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("♻️ Sustainable Procurement")
        if not st.session_state.items_data.empty:
            sustainability_data, sustainability_msg = calculate_sustainability_metrics(st.session_state.suppliers, st.session_state.items_data)
            st.metric("Sustainable Spend", sustainability_msg)
            if not sustainability_data.empty:
                # Create pie chart for sustainability metrics
                fig_sustainable = px.pie(
                    sustainability_data, 
                    names='metric', 
                    values='value',
                    title='Sustainability Metrics Distribution',
                    color_discrete_sequence=['#1A936F', '#88D498', '#C6DABF']
                )
                fig_sustainable.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    showlegend=True
                )
                st.plotly_chart(fig_sustainable, use_container_width=True, key="sustainable_procurement_chart")
                
                # Display sustainability data table
                st.write("📊 Sustainability Data")
                sustainability_display = sustainability_data.copy()
                sustainability_display.columns = ['Metric', 'Value']
                display_dataframe_with_index_1(sustainability_display)
        else:
            st.info("Add item data to see sustainability analysis")
    
    with col2:
        st.subheader("🤝 Diversity Spend Analysis")
        if not st.session_state.suppliers.empty:
            # diversity_data, diversity_msg = calculate_diversity_spend_analysis(po_df, st.session_state.suppliers)
            diversity_data, diversity_msg = pd.DataFrame(), "No diversity data available"
            st.metric("Diversity Spend", diversity_msg)
            if not diversity_data.empty:
                # Diversity chart would go here when diversity function is implemented
                st.info("Diversity analysis chart will be available when diversity function is implemented")
            else:
                st.info("No diversity data available")
        else:
            st.info("Add supplier data to see diversity analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🌍 Carbon Footprint Analysis")
        if not st.session_state.items_data.empty:
            carbon_data, carbon_msg = calculate_carbon_footprint_analysis(st.session_state.items_data, po_df)
            st.metric("Carbon Impact", carbon_msg)
            if not carbon_data.empty:
                # Create bar chart for carbon footprint metrics
                fig_carbon = px.bar(
                    carbon_data, 
                    x='metric', 
                    y='value',
                    title='Carbon Footprint Analysis',
                    labels={'metric': 'Metric', 'value': 'Value'},
                    color='value',
                    color_continuous_scale='Greens'
                )
                fig_carbon.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_carbon, use_container_width=True, key="carbon_footprint_chart")
                
                # Display carbon data table
                st.write("📊 Carbon Footprint Data")
                carbon_display = carbon_data.copy()
                carbon_display.columns = ['Metric', 'Value']
                display_dataframe_with_index_1(carbon_display)
        else:
            st.info("Add item data to see carbon footprint analysis")
    


if __name__ == "__main__":
    main() 
    


