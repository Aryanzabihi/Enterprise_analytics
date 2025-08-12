import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Tuple, Dict, Any, Optional

# Standard column name mappings
COLUMN_MAPPINGS = {
    'purchase_orders': {
        'po_id': 'po_id',
        'order_date': 'order_date', 
        'department': 'department',
        'supplier_id': 'supplier_id',
        'item_id': 'item_id',
        'quantity': 'quantity',
        'unit_price': 'unit_price',
        'delivery_date': 'delivery_date',
        'currency': 'currency',
        'budget_code': 'budget_code'
    },
    'suppliers': {
        'supplier_id': 'supplier_id',
        'supplier_name': 'supplier_name',
        'country': 'country',
        'region': 'region',
        'registration_date': 'registration_date',
        'diversity_flag': 'diversity_flag',
        'esg_score': 'esg_score',
        'certifications': 'certifications'
    },
    'items': {
        'item_id': 'item_id',
        'item_name': 'item_name',
        'category': 'category',
        'unit': 'unit',
        'recyclable_flag': 'recyclable_flag',
        'carbon_score': 'carbon_score'
    },
    'contracts': {
        'contract_id': 'contract_id',
        'supplier_id': 'supplier_id',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'contract_value': 'contract_value',
        'volume_commitment': 'volume_commitment',
        'dispute_count': 'dispute_count',
        'compliance_status': 'compliance_status'
    },
    'deliveries': {
        'delivery_id': 'delivery_id',
        'po_id': 'po_id',
        'delivery_date': 'delivery_date_actual',
        'delivered_quantity': 'delivered_quantity',
        'defect_flag': 'defect_flag',
        'defect_notes': 'defect_notes'
    },
    'invoices': {
        'invoice_id': 'invoice_id',
        'po_id': 'po_id',
        'invoice_date': 'invoice_date',
        'payment_date': 'payment_date',
        'invoice_amount': 'invoice_amount'
    },
    'budgets': {
        'budget_code': 'budget_code',
        'department': 'department',
        'category': 'category',
        'fiscal_year': 'fiscal_year',
        'budget_amount': 'budget_amount'
    },
    'rfqs': {
        'rfq_id': 'rfq_id',
        'supplier_id': 'supplier_id',
        'item_id': 'item_id',
        'unit_price': 'unit_price',
        'response_date': 'response_date'
    }
}

def safe_dataframe_operation(df: pd.DataFrame, operation: str, **kwargs) -> pd.DataFrame:
    """Safely perform DataFrame operations with error handling"""
    if df.empty:
        return pd.DataFrame()
    
    try:
        if operation == 'merge':
            return df.merge(**kwargs)
        elif operation == 'groupby':
            return df.groupby(**kwargs)
        elif operation == 'sort_values':
            return df.sort_values(**kwargs)
        elif operation == 'head':
            return df.head(**kwargs)
        elif operation == 'tail':
            return df.tail(**kwargs)
        else:
            return df
    except Exception as e:
        st.error(f"Error in DataFrame operation: {e}")
        return pd.DataFrame()

def calculate_total_spend(df: pd.DataFrame) -> float:
    """Calculate total spend from purchase orders DataFrame"""
    if df.empty or 'quantity' not in df.columns or 'unit_price' not in df.columns:
        return 0.0
    return (df['quantity'] * df['unit_price']).sum()

def create_standard_chart(data: pd.DataFrame, chart_type: str, **kwargs) -> Any:
    """Create standardized charts with consistent styling"""
    if data.empty:
        return None
    
    try:
        if chart_type == 'bar':
            fig = px.bar(data, **kwargs)
        elif chart_type == 'pie':
            fig = px.pie(data, **kwargs)
        elif chart_type == 'line':
            fig = px.line(data, **kwargs)
        elif chart_type == 'scatter':
            fig = px.scatter(data, **kwargs)
        elif chart_type == 'histogram':
            fig = px.histogram(data, **kwargs)
        else:
            return None
        
        # Apply standard styling
        fig.update_layout(
            title_font_size=18,
            title_font_color='#1e3c72',
            showlegend=True,
            legend=dict(bgcolor='rgba(255,255,255,0.8)'),
            xaxis_tickangle=-45
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None

def display_metric_card(title: str, value: str, color: str = "blue") -> None:
    """Display standardized metric cards"""
    color_classes = {
        "blue": "metric-card-blue",
        "red": "metric-card-red", 
        "orange": "metric-card-orange",
        "teal": "metric-card-teal",
        "green": "metric-card-green"
    }
    
    css_class = color_classes.get(color, "metric-card-blue")
    
    st.markdown(f"""
    <div class="{css_class}">
        <h4 style="color: white; margin: 0; font-size: 14px;">{title}</h4>
        <h2 style="color: white; margin: 5px 0; font-size: 24px;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

def display_dataframe_with_index(df: pd.DataFrame, **kwargs) -> None:
    """Display dataframe with standardized formatting"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        st.dataframe(df_display, **kwargs)
    else:
        st.dataframe(df, **kwargs)

def validate_dataframe_columns(df: pd.DataFrame, required_columns: list, table_name: str) -> bool:
    """Validate DataFrame has required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns in {table_name}: {', '.join(missing_columns)}")
        return False
    return True

def get_summary_metrics(purchase_orders: pd.DataFrame, suppliers: pd.DataFrame, 
                       items: pd.DataFrame, deliveries: pd.DataFrame) -> Dict[str, Any]:
    """Calculate standardized summary metrics"""
    metrics = {}
    
    # Basic metrics
    metrics['total_pos'] = len(purchase_orders) if not purchase_orders.empty else 0
    metrics['total_spend'] = calculate_total_spend(purchase_orders)
    metrics['avg_order_value'] = metrics['total_spend'] / metrics['total_pos'] if metrics['total_pos'] > 0 else 0
    metrics['unique_suppliers'] = purchase_orders['supplier_id'].nunique() if not purchase_orders.empty else 0
    metrics['unique_categories'] = purchase_orders['item_id'].nunique() if not purchase_orders.empty else 0
    
    # Supplier metrics
    metrics['total_suppliers'] = len(suppliers) if not suppliers.empty else 0
    metrics['total_deliveries'] = len(deliveries) if not deliveries.empty else 0
    
    # Quality metrics
    if not deliveries.empty:
        defect_count = deliveries['defect_flag'].sum() if 'defect_flag' in deliveries.columns else 0
        metrics['defect_count'] = defect_count
        metrics['defect_rate'] = (defect_count / metrics['total_deliveries'] * 100) if metrics['total_deliveries'] > 0 else 0
        metrics['quality_score'] = 100 - metrics['defect_rate']
    else:
        metrics['defect_count'] = 0
        metrics['defect_rate'] = 0
        metrics['quality_score'] = 0
    
    return metrics

def format_currency(amount: float) -> str:
    """Format currency values consistently"""
    return f"${amount:,.0f}"

def format_percentage(value: float) -> str:
    """Format percentage values consistently"""
    return f"{value:.1f}%"

def safe_iloc_access(df: pd.DataFrame, index: int, column: str, default_value: Any = None) -> Any:
    """Safely access DataFrame values with error handling"""
    try:
        if not df.empty and index < len(df) and column in df.columns:
            return df.iloc[index][column]
        return default_value
    except Exception:
        return default_value

def create_insight_message(metric_name: str, value: Any, comparison: str = "", threshold: Any = None) -> str:
    """Create standardized insight messages"""
    if threshold is not None:
        if isinstance(threshold, (int, float)):
            if value > threshold:
                status = "🟢"
            elif value == threshold:
                status = "🟡"
            else:
                status = "🔴"
        else:
            status = "💡"
    else:
        status = "💡"
    
    return f"{status} **{metric_name}**: {value} {comparison}".strip() 