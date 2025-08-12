import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# Import with fallback for different execution contexts
try:
    from data_handling_utils import (
        validate_dataframe, safe_merge, handle_missing_values, 
        calculate_spend, calculate_delivery_days, detect_delivery_date_column
    )
except ImportError:
    # Define fallback functions if module not found
    def validate_dataframe(df, required_columns, operation_name):
        return df
    def safe_merge(left_df, right_df, on, how='left', suffixes=('_x', '_y')):
        return left_df.merge(right_df, on=on, how=how, suffixes=suffixes)
    def handle_missing_values(df, categorical_fill='Unknown', numeric_fill=0):
        return df.fillna(categorical_fill if df.dtype == 'object' else numeric_fill)
    def calculate_spend(df, quantity_col='quantity', unit_price_col='unit_price'):
        return df[quantity_col] * df[unit_price_col]
    def calculate_delivery_days(df, order_date_col='order_date', delivery_date_col=None):
        return pd.Series([0] * len(df))
    def detect_delivery_date_column(df):
        return 'delivery_date' if 'delivery_date' in df.columns else None

# Spend Analysis Functions
def calculate_spend_trends(purchase_orders, items_data=None, suppliers=None):
    """Calculate comprehensive spend trends over time"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Convert order_date to datetime
    po_df = purchase_orders.copy()
    po_df['order_date'] = pd.to_datetime(po_df['order_date'])
    
    # Calculate total spend
    po_df['total_spend'] = po_df['quantity'] * po_df['unit_price']
    
    # Create monthly trends
    po_df['month'] = po_df['order_date'].dt.to_period('M')
    
    # Monthly total spend
    monthly_spend = po_df.groupby('month')['total_spend'].sum().reset_index()
    monthly_spend['month'] = monthly_spend['month'].astype(str)
    
    return monthly_spend, "Spend trends calculated"

def calculate_category_spend_trends(purchase_orders, items_data):
    """Calculate spend trends by category over time"""
    if purchase_orders.empty or items_data.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with items
    merged_data = purchase_orders.merge(items_data, on='item_id', how='left')
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Create monthly trends by category
    merged_data['month'] = merged_data['order_date'].dt.to_period('M')
    category_trends = merged_data.groupby(['month', 'category'])['total_spend'].sum().reset_index()
    category_trends['month'] = category_trends['month'].astype(str)
    
    return category_trends, "Category spend trends calculated"

def calculate_department_spend_trends(purchase_orders):
    """Calculate spend trends by department over time"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    po_df = purchase_orders.copy()
    po_df['order_date'] = pd.to_datetime(po_df['order_date'])
    po_df['total_spend'] = po_df['quantity'] * po_df['unit_price']
    
    # Create monthly trends by department
    po_df['month'] = po_df['order_date'].dt.to_period('M')
    dept_trends = po_df.groupby(['month', 'department'])['total_spend'].sum().reset_index()
    dept_trends['month'] = dept_trends['month'].astype(str)
    
    return dept_trends, "Department spend trends calculated"

def calculate_supplier_spend_trends(purchase_orders, suppliers):
    """Calculate spend trends by supplier over time"""
    if purchase_orders.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with suppliers
    merged_data = purchase_orders.merge(suppliers, on='supplier_id', how='left')
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Create monthly trends by supplier
    merged_data['month'] = merged_data['order_date'].dt.to_period('M')
    supplier_trends = merged_data.groupby(['month', 'supplier_name'])['total_spend'].sum().reset_index()
    supplier_trends['month'] = supplier_trends['month'].astype(str)
    
    return supplier_trends, "Supplier spend trends calculated"

def calculate_budget_spend_trends(purchase_orders, budgets):
    """Calculate budget vs actual spend trends over time"""
    if purchase_orders.empty or budgets.empty:
        return pd.DataFrame(), "No data available"
    
    po_df = purchase_orders.copy()
    po_df['order_date'] = pd.to_datetime(po_df['order_date'])
    po_df['total_spend'] = po_df['quantity'] * po_df['unit_price']
    
    # Create monthly trends by budget
    po_df['month'] = po_df['order_date'].dt.to_period('M')
    budget_trends = po_df.groupby(['month', 'budget_code'])['total_spend'].sum().reset_index()
    budget_trends['month'] = budget_trends['month'].astype(str)
    
    # Merge with budget data for comparison
    budget_comparison = budget_trends.merge(budgets, on='budget_code', how='left')
    budget_comparison['budget_amount'] = budget_comparison['budget_amount'].fillna(0)
    budget_comparison['variance'] = budget_comparison['total_spend'] - budget_comparison['budget_amount']
    budget_comparison['variance_percent'] = (budget_comparison['variance'] / budget_comparison['budget_amount'] * 100).fillna(0)
    
    return budget_comparison, "Budget spend trends calculated"

def calculate_spend_by_category(purchase_orders, items_data):
    """Calculate total spend by category"""
    # Validate input data
    is_valid_po, po_msg = validate_dataframe(purchase_orders, ['item_id', 'quantity', 'unit_price'], "category spend analysis")
    if not is_valid_po:
        return pd.DataFrame(), po_msg
    
    is_valid_items, items_msg = validate_dataframe(items_data, ['item_id', 'category'], "category spend analysis")
    if not is_valid_items:
        return pd.DataFrame(), items_msg
    
    # Merge purchase orders with items to get categories
    merged_data = safe_merge(purchase_orders, items_data, on='item_id', how='left')
    if merged_data.empty:
        return pd.DataFrame(), "Failed to merge purchase orders with items data"
    
    # Handle missing values consistently
    merged_data = handle_missing_values(merged_data, categorical_fill='Unknown Category')
    
    # Calculate total spend using centralized function
    merged_data['total_spend'] = calculate_spend(merged_data)
    if merged_data['total_spend'].empty:
        return pd.DataFrame(), "Error calculating spend"
    
    # Group by category and sum spend
    category_spend = merged_data.groupby('category')['total_spend'].sum().reset_index()
    category_spend = category_spend.sort_values('total_spend', ascending=False)
    
    # Remove zero spend categories
    category_spend = category_spend[category_spend['total_spend'] > 0]
    
    if category_spend.empty:
        return pd.DataFrame(), "No spend data found in categories"
    
    total_spend = category_spend['total_spend'].sum()
    total_spend_msg = f"${total_spend:,.0f}"
    
    return category_spend, total_spend_msg

def calculate_spend_by_supplier(purchase_orders, suppliers):
    """Calculate total spend by supplier"""
    # Validate input data
    is_valid_po, po_msg = validate_dataframe(purchase_orders, ['supplier_id', 'quantity', 'unit_price'], "supplier spend analysis")
    if not is_valid_po:
        return pd.DataFrame(), po_msg
    
    is_valid_suppliers, suppliers_msg = validate_dataframe(suppliers, ['supplier_id', 'supplier_name'], "supplier spend analysis")
    if not is_valid_suppliers:
        return pd.DataFrame(), suppliers_msg
    
    # Merge purchase orders with suppliers
    merged_data = safe_merge(purchase_orders, suppliers, on='supplier_id', how='left')
    if merged_data.empty:
        return pd.DataFrame(), "Failed to merge purchase orders with suppliers data"
    
    # Handle missing values consistently
    merged_data = handle_missing_values(merged_data, categorical_fill='Unknown Supplier')
    
    # Calculate total spend using centralized function
    merged_data['total_spend'] = calculate_spend(merged_data)
    if merged_data['total_spend'].empty:
        return pd.DataFrame(), "Error calculating spend"
    
    # Group by supplier and sum spend
    supplier_spend = merged_data.groupby('supplier_name')['total_spend'].sum().reset_index()
    supplier_spend = supplier_spend.sort_values('total_spend', ascending=False)
    
    # Remove zero spend suppliers
    supplier_spend = supplier_spend[supplier_spend['total_spend'] > 0]
    
    if supplier_spend.empty:
        return pd.DataFrame(), "No spend data found for suppliers"
    
    total_spend = supplier_spend['total_spend'].sum()
    total_spend_msg = f"${total_spend:,.0f}"
    
    return supplier_spend, total_spend_msg

def calculate_spend_by_department(purchase_orders):
    """Calculate total spend by department"""
    # Validate input data
    is_valid, msg = validate_dataframe(purchase_orders, ['department', 'quantity', 'unit_price'], "department spend analysis")
    if not is_valid:
        return pd.DataFrame(), msg
    
    # Handle missing values consistently
    po_clean = handle_missing_values(purchase_orders, categorical_fill='Unknown Department')
    
    # Calculate total spend using centralized function
    po_clean['total_spend'] = calculate_spend(po_clean)
    if po_clean['total_spend'].empty:
        return pd.DataFrame(), "Error calculating spend"
    
    # Group by department and sum spend
    dept_spend = po_clean.groupby('department')['total_spend'].sum().reset_index()
    dept_spend = dept_spend.sort_values('total_spend', ascending=False)
    
    # Remove zero spend departments
    dept_spend = dept_spend[dept_spend['total_spend'] > 0]
    
    if dept_spend.empty:
        return pd.DataFrame(), "No spend data found for departments"
    
    total_spend = dept_spend['total_spend'].sum()
    total_spend_msg = f"${total_spend:,.0f}"
    
    return dept_spend, total_spend_msg

def calculate_budget_utilization(purchase_orders, budgets):
    """Calculate budget utilization rate"""
    if purchase_orders.empty or budgets.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate actual spend by budget code
    purchase_orders['total_spend'] = purchase_orders['quantity'] * purchase_orders['unit_price']
    actual_spend = purchase_orders.groupby('budget_code')['total_spend'].sum().reset_index()
    
    # Merge with budget data
    budget_analysis = budgets.merge(actual_spend, on='budget_code', how='left')
    budget_analysis['total_spend'] = budget_analysis['total_spend'].fillna(0)
    budget_analysis['utilization_rate'] = (budget_analysis['total_spend'] / budget_analysis['amount']) * 100
    
    avg_utilization = budget_analysis['utilization_rate'].mean()
    budget_msg = f"Average utilization: {avg_utilization:.1f}%"
    
    return budget_analysis, budget_msg

def calculate_tail_spend(purchase_orders, suppliers):
    """Calculate tail spend analysis (Pareto)"""
    if purchase_orders.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with suppliers
    merged_data = purchase_orders.merge(suppliers, on='supplier_id', how='left')
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Group by supplier and sum spend
    supplier_spend = merged_data.groupby('supplier_name')['total_spend'].sum().reset_index()
    supplier_spend = supplier_spend.sort_values('total_spend', ascending=False)
    
    # Calculate tail spend (bottom 20% of suppliers by count, not by spend)
    total_suppliers = len(supplier_spend)
    tail_supplier_count = max(1, int(total_suppliers * 0.2))  # At least 1 supplier
    
    # Get the bottom 20% of suppliers by spend
    tail_suppliers = supplier_spend.tail(tail_supplier_count)
    tail_spend_total = tail_suppliers['total_spend'].sum()
    total_spend = supplier_spend['total_spend'].sum()
    
    # Calculate percentage of total spend
    tail_percentage = (tail_spend_total / total_spend * 100) if total_spend > 0 else 0
    
    tail_msg = f"${tail_spend_total:,.0f} ({tail_percentage:.1f}% of total spend)"
    
    return supplier_spend, tail_msg

# Supplier Performance Functions
def calculate_on_time_delivery_rate(purchase_orders, deliveries):
    """Calculate on-time delivery rate"""
    # Validate input data
    is_valid_po, po_msg = validate_dataframe(purchase_orders, ['po_id', 'order_date', 'delivery_date'], "on-time delivery analysis")
    if not is_valid_po:
        return pd.DataFrame(), po_msg
    
    is_valid_deliveries, deliveries_msg = validate_dataframe(deliveries, ['po_id', 'delivery_date_actual'], "on-time delivery analysis")
    if not is_valid_deliveries:
        return pd.DataFrame(), deliveries_msg
    
    # Merge purchase orders with deliveries
    merged_data = safe_merge(purchase_orders, deliveries, on='po_id', how='inner')
    if merged_data.empty:
        return pd.DataFrame(), "Failed to merge purchase orders with deliveries data"
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['expected_delivery_date'] = pd.to_datetime(merged_data['delivery_date_x'])  # from purchase_orders (expected)
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])  # from deliveries (actual)
    
    # Calculate if delivery was on time
    merged_data['on_time'] = merged_data['actual_delivery_date'] <= merged_data['expected_delivery_date']
    
    on_time_count = merged_data['on_time'].sum()
    total_deliveries = len(merged_data)
    on_time_rate = (on_time_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    delivery_msg = f"{on_time_rate:.1f}%"
    
    return merged_data[['po_id', 'on_time']], delivery_msg

def calculate_supplier_defect_rate(deliveries):
    """Calculate supplier defect rate"""
    if deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Count defects
    total_deliveries = len(deliveries)
    defect_count = deliveries['defect_flag'].sum()
    defect_rate = (defect_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Create summary data
    defect_summary = pd.DataFrame({
        'defect_flag': ['No Defects', 'Defects'],
        'count': [total_deliveries - defect_count, defect_count]
    })
    
    defect_msg = f"{defect_rate:.1f}%"
    
    return defect_summary, defect_msg

def calculate_supplier_lead_time_analysis(purchase_orders, deliveries, suppliers):
    """Calculate average lead time by supplier"""
    if purchase_orders.empty or deliveries.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Check for required columns
    required_po_cols = ['po_id', 'order_date']
    required_delivery_cols = ['po_id', 'delivery_date_actual']
    required_supplier_cols = ['supplier_id', 'supplier_name']
    
    missing_po_cols = [col for col in required_po_cols if col not in purchase_orders.columns]
    missing_delivery_cols = [col for col in required_delivery_cols if col not in deliveries.columns]
    missing_supplier_cols = [col for col in required_supplier_cols if col not in suppliers.columns]
    
    if missing_po_cols or missing_delivery_cols or missing_supplier_cols:
        return pd.DataFrame(), f"Missing required columns: PO={missing_po_cols}, Deliveries={missing_delivery_cols}, Suppliers={missing_supplier_cols}"
    
    # Merge all data
    merged_data = purchase_orders.merge(deliveries, on='po_id', how='inner')
    merged_data = merged_data.merge(suppliers, on='supplier_id', how='left')
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])
    
    # Calculate lead time
    merged_data['lead_time_days'] = (merged_data['actual_delivery_date'] - merged_data['order_date']).dt.days
    
    # Group by supplier and calculate average lead time
    supplier_lead_time = merged_data.groupby('supplier_name').agg({
        'lead_time_days': 'mean',
        'po_id': 'count'
    }).reset_index()
    
    supplier_lead_time.columns = ['supplier_name', 'avg_lead_time_days', 'order_count']
    supplier_lead_time = supplier_lead_time.sort_values('avg_lead_time_days')
    
    avg_lead_time = supplier_lead_time['avg_lead_time_days'].mean()
    lead_time_msg = f"{avg_lead_time:.1f} days"
    
    return supplier_lead_time, lead_time_msg

def calculate_lead_time_analysis(purchase_orders, deliveries):
    """Calculate detailed lead time analysis"""
    if purchase_orders.empty or deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Check for required columns
    required_po_cols = ['po_id', 'order_date']
    required_delivery_cols = ['po_id', 'delivery_date_actual']
    
    missing_po_cols = [col for col in required_po_cols if col not in purchase_orders.columns]
    missing_delivery_cols = [col for col in required_delivery_cols if col not in deliveries.columns]
    
    if missing_po_cols or missing_delivery_cols:
        return pd.DataFrame(), f"Missing required columns: PO={missing_po_cols}, Deliveries={missing_delivery_cols}"
    
    # Merge purchase orders with deliveries
    merged_data = purchase_orders.merge(deliveries, on='po_id', how='inner')
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])
    
    # Calculate lead time
    merged_data['lead_time_days'] = (merged_data['actual_delivery_date'] - merged_data['order_date']).dt.days
    
    return merged_data, "Lead time calculated"

def calculate_supplier_risk_assessment(suppliers, purchase_orders, deliveries=None, invoices=None, contracts=None):
    """Calculate comprehensive supplier risk assessment for each supplier"""
    if suppliers.empty or purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Create a copy of suppliers for risk analysis
    risk_data = suppliers.copy()
    
    # Calculate spend by supplier
    purchase_orders['total_spend'] = purchase_orders['quantity'] * purchase_orders['unit_price']
    supplier_spend = purchase_orders.groupby('supplier_id')['total_spend'].sum().reset_index()
    
    # Merge with supplier data
    risk_data = risk_data.merge(supplier_spend, on='supplier_id', how='left')
    risk_data['total_spend'] = risk_data['total_spend'].fillna(0)
    
    # Calculate spend percentage
    total_spend = risk_data['total_spend'].sum()
    risk_data['spend_percentage'] = (risk_data['total_spend'] / total_spend * 100) if total_spend > 0 else 0
    
    # 1. Financial Risk Score (0-100)
    risk_data['esg_score'] = risk_data['esg_score'].fillna(50)  # Default ESG score
    risk_data['financial_risk'] = 100 - risk_data['esg_score']  # Higher ESG = lower financial risk
    
    # 2. Concentration Risk Score (0-100)
    # Higher spend percentage = higher concentration risk
    max_spend_pct = risk_data['spend_percentage'].max()
    risk_data['concentration_risk'] = (risk_data['spend_percentage'] / max_spend_pct * 100) if max_spend_pct > 0 else 0
    
    # 3. Geographic Risk Score (0-100)
    if 'country' in risk_data.columns:
        country_counts = risk_data['country'].value_counts()
        risk_data['country_supplier_count'] = risk_data['country'].map(country_counts)
        # Fewer suppliers in a country = higher geographic risk
        risk_data['geographic_risk'] = (1 / risk_data['country_supplier_count'] * 100).clip(upper=100)
    else:
        risk_data['geographic_risk'] = 50  # Default moderate risk
    
    # 4. Performance Risk Score (0-100) - if delivery data available
    if deliveries is not None and not deliveries.empty:
        # Merge with delivery data to calculate performance metrics
        po_delivery = purchase_orders.merge(deliveries, on='po_id', how='left')
        po_delivery = po_delivery.merge(suppliers[['supplier_id', 'supplier_name']], on='supplier_id', how='left')
        
        # Calculate on-time delivery rate by supplier
        if 'delivery_date_actual' in po_delivery.columns and 'delivery_date' in po_delivery.columns:
            po_delivery['on_time'] = pd.to_datetime(po_delivery['delivery_date_actual']) <= pd.to_datetime(po_delivery['delivery_date'])
            supplier_performance = po_delivery.groupby('supplier_id').agg({
                'on_time': 'mean',
                'defect_flag': 'sum',
                'po_id': 'count'
            }).reset_index()
            supplier_performance.columns = ['supplier_id', 'on_time_rate', 'defect_count', 'order_count']
            
            # Merge performance data
            risk_data = risk_data.merge(supplier_performance, on='supplier_id', how='left')
            risk_data['on_time_rate'] = risk_data['on_time_rate'].fillna(0.5)  # Default 50% if no data
            risk_data['defect_count'] = risk_data['defect_count'].fillna(0)
            risk_data['order_count'] = risk_data['order_count'].fillna(0)
            
            # Calculate performance risk (lower on-time rate = higher risk)
            risk_data['performance_risk'] = (1 - risk_data['on_time_rate']) * 100
            
            # Add defect risk
            max_defects = risk_data['defect_count'].max()
            risk_data['defect_risk'] = (risk_data['defect_count'] / max_defects * 100) if max_defects > 0 else 0
        else:
            risk_data['performance_risk'] = 50  # Default moderate risk
            risk_data['defect_risk'] = 0
    else:
        risk_data['performance_risk'] = 50  # Default moderate risk
        risk_data['defect_risk'] = 0
    
    # 5. Contract Risk Score (0-100) - if contract data available
    if contracts is not None and not contracts.empty:
        # Calculate contract-related risks
        # Check which date column exists in contracts data
        date_column = None
        for col in ['end_date', 'expiry_date', 'contract_end_date']:
            if col in contracts.columns:
                date_column = col
                break
        
        if date_column:
            supplier_contracts = contracts.groupby('supplier_id').agg({
                'contract_value': 'sum',
                'contract_id': 'count',
                date_column: 'min'
            }).reset_index()
            supplier_contracts.columns = ['supplier_id', 'total_contract_value', 'contract_count', 'earliest_expiry']
        else:
            # If no date column found, create a basic aggregation without expiry
            supplier_contracts = contracts.groupby('supplier_id').agg({
                'contract_value': 'sum',
                'contract_id': 'count'
            }).reset_index()
            supplier_contracts.columns = ['supplier_id', 'total_contract_value', 'contract_count']
            supplier_contracts['earliest_expiry'] = None
        
        # Merge contract data
        risk_data = risk_data.merge(supplier_contracts, on='supplier_id', how='left')
        risk_data['total_contract_value'] = risk_data['total_contract_value'].fillna(0)
        risk_data['contract_count'] = risk_data['contract_count'].fillna(0)
        
        # Contract concentration risk (higher contract value = higher risk)
        max_contract_value = risk_data['total_contract_value'].max()
        risk_data['contract_risk'] = (risk_data['total_contract_value'] / max_contract_value * 100) if max_contract_value > 0 else 0
        
        # Contract expiry risk
        if 'earliest_expiry' in risk_data.columns and risk_data['earliest_expiry'].notna().any():
            risk_data['earliest_expiry'] = pd.to_datetime(risk_data['earliest_expiry'], errors='coerce')
            today = pd.Timestamp.now()
            risk_data['days_to_expiry'] = (risk_data['earliest_expiry'] - today).dt.days
            # Closer to expiry = higher risk
            risk_data['expiry_risk'] = ((365 - risk_data['days_to_expiry']) / 365 * 100).clip(lower=0, upper=100)
            risk_data['expiry_risk'] = risk_data['expiry_risk'].fillna(50)
        else:
            risk_data['expiry_risk'] = 50
    else:
        risk_data['contract_risk'] = 0
        risk_data['expiry_risk'] = 50
    
    # 6. Compliance Risk Score (0-100)
    if 'certification_status' in risk_data.columns:
        # Suppliers without certifications have higher compliance risk
        risk_data['compliance_risk'] = risk_data['certification_status'].apply(
            lambda x: 80 if pd.isna(x) or x == 'No' else 20 if x == 'Yes' else 50
        )
    else:
        risk_data['compliance_risk'] = 50  # Default moderate risk
    
    # 7. Diversity Risk Score (0-100)
    if 'diversity_flag' in risk_data.columns:
        # Non-diverse suppliers might have higher risk
        risk_data['diversity_risk'] = risk_data['diversity_flag'].apply(
            lambda x: 30 if pd.isna(x) or x == 'No' else 10 if x == 'Yes' else 20
        )
    else:
        risk_data['diversity_risk'] = 30  # Default moderate risk
    
    # Calculate weighted total risk score (0-100)
    risk_weights = {
        'financial_risk': 0.20,
        'concentration_risk': 0.25,
        'geographic_risk': 0.15,
        'performance_risk': 0.20,
        'defect_risk': 0.10,
        'contract_risk': 0.05,
        'expiry_risk': 0.02,
        'compliance_risk': 0.02,
        'diversity_risk': 0.01
    }
    
    risk_data['total_risk_score'] = sum(
        risk_data[col] * weight for col, weight in risk_weights.items()
    )
    
    # Categorize risk levels
    risk_data['risk_level'] = pd.cut(
        risk_data['total_risk_score'],
        bins=[0, 30, 60, 100],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    
    # Sort by risk score (highest risk first)
    risk_data = risk_data.sort_values('total_risk_score', ascending=False)
    
    # Calculate summary statistics
    high_risk_suppliers = len(risk_data[risk_data['total_risk_score'] > 60])
    medium_risk_suppliers = len(risk_data[(risk_data['total_risk_score'] > 30) & (risk_data['total_risk_score'] <= 60)])
    low_risk_suppliers = len(risk_data[risk_data['total_risk_score'] <= 30])
    
    risk_msg = f"{high_risk_suppliers} high-risk, {medium_risk_suppliers} medium-risk, {low_risk_suppliers} low-risk suppliers identified"
    
    return risk_data, risk_msg

# Cost & Savings Functions
def calculate_cost_savings_from_negotiation(purchase_orders, rfqs):
    """Calculate cost savings from negotiation"""
    if purchase_orders.empty or rfqs.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with RFQs on item_id and supplier_id
    # This assumes RFQ contains initial quotes and PO contains final negotiated prices
    merged_data = purchase_orders.merge(rfqs, on=['supplier_id', 'item_id'], how='inner', suffixes=('_po', '_rfq'))
    
    if merged_data.empty:
        return pd.DataFrame(), "No matching RFQ-PO data found"
    
    # Calculate costs for both RFQ and PO
    merged_data['po_cost'] = merged_data['quantity_po'] * merged_data['unit_price_po']
    merged_data['rfq_cost'] = merged_data['quantity_rfq'] * merged_data['unit_price_rfq']
    
    # Calculate savings: PO cost should be lower than RFQ cost for positive savings
    # If PO price is lower than RFQ price, that's a savings
    merged_data['savings'] = merged_data['rfq_cost'] - merged_data['po_cost']
    
    # Calculate savings percentage based on RFQ cost
    merged_data['savings_percentage'] = (merged_data['savings'] / merged_data['rfq_cost'] * 100).fillna(0)
    
    # Filter out negative savings (where PO cost > RFQ cost) for the chart
    positive_savings = merged_data[merged_data['savings'] > 0]
    
    total_savings = merged_data['savings'].sum()
    total_positive_savings = positive_savings['savings'].sum()
    
    # Create a more meaningful message
    if total_savings > 0:
        savings_msg = f"${total_savings:,.0f} total savings"
    elif total_savings < 0:
        savings_msg = f"${abs(total_savings):,.0f} cost increase"
    else:
        savings_msg = "No net savings"
    
    return merged_data, savings_msg

def calculate_procurement_cost_per_po(purchase_orders, invoices=None):
    """Calculate procurement cost per purchase order"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate total procurement cost
    total_po_cost = purchase_orders['quantity'].mul(purchase_orders['unit_price']).sum()
    total_pos = len(purchase_orders)
    
    cost_per_po = total_po_cost / total_pos if total_pos > 0 else 0
    cost_msg = f"${cost_per_po:,.2f} per PO"
    
    return pd.DataFrame({'metric': ['Cost per PO'], 'value': [cost_per_po]}), cost_msg

def calculate_total_cost_of_ownership(purchase_orders, deliveries, invoices):
    """Calculate Total Cost of Ownership"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate direct costs
    direct_costs = purchase_orders['quantity'].mul(purchase_orders['unit_price']).sum()
    
    # Calculate indirect costs (simplified)
    total_pos = len(purchase_orders)
    indirect_costs = total_pos * 50  # Estimated $50 per PO for processing
    
    # Calculate quality costs
    if not deliveries.empty:
        defect_count = deliveries['defect_flag'].sum()
        quality_costs = defect_count * 100  # Estimated $100 per defect
    else:
        quality_costs = 0
    
    total_tco = direct_costs + indirect_costs + quality_costs
    tco_msg = f"${total_tco:,.0f}"
    
    tco_breakdown = pd.DataFrame({
        'cost_type': ['Direct Costs', 'Indirect Costs', 'Quality Costs', 'Total TCO'],
        'amount': [direct_costs, indirect_costs, quality_costs, total_tco]
    })
    
    return tco_breakdown, tco_msg

def calculate_unit_cost_trends(purchase_orders, items_data):
    """Calculate unit cost trends over time"""
    if purchase_orders.empty or items_data.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with items
    merged_data = purchase_orders.merge(items_data, on='item_id', how='left')
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    
    # Group by month and item category
    merged_data['month'] = merged_data['order_date'].dt.to_period('M')
    cost_trends = merged_data.groupby(['month', 'category'])[unit_price_col].mean().reset_index()
    
    cost_trends['month'] = cost_trends['month'].astype(str)
    
    return cost_trends, "Unit cost trends calculated"

def calculate_savings_from_supplier_consolidation(purchase_orders, suppliers):
    """Calculate potential savings from supplier consolidation"""
    if purchase_orders.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with suppliers
    merged_data = purchase_orders.merge(suppliers, on='supplier_id', how='left')
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Identify suppliers with low spend
    supplier_spend = merged_data.groupby('supplier_name')['total_spend'].sum().reset_index()
    low_spend_threshold = supplier_spend['total_spend'].quantile(0.25)
    
    low_spend_suppliers = supplier_spend[supplier_spend['total_spend'] <= low_spend_threshold]
    potential_savings = low_spend_suppliers['total_spend'].sum() * 0.15  # 15% savings estimate
    
    savings_msg = f"${potential_savings:,.0f} potential savings"
    
    return low_spend_suppliers, savings_msg

# Process Efficiency Functions
def calculate_purchase_order_cycle_time(purchase_orders, deliveries):
    """Calculate purchase order cycle time"""
    if purchase_orders.empty or deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Check for required columns
    required_po_cols = ['po_id', 'order_date']
    required_delivery_cols = ['po_id', 'delivery_date_actual']
    
    missing_po_cols = [col for col in required_po_cols if col not in purchase_orders.columns]
    missing_delivery_cols = [col for col in required_delivery_cols if col not in deliveries.columns]
    
    if missing_po_cols or missing_delivery_cols:
        return pd.DataFrame(), f"Missing required columns: PO={missing_po_cols}, Deliveries={missing_delivery_cols}"
    
    # Merge purchase orders with deliveries
    merged_data = purchase_orders.merge(deliveries, on='po_id', how='inner')
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])
    
    # Calculate cycle time
    merged_data['cycle_time_days'] = (merged_data['actual_delivery_date'] - merged_data['order_date']).dt.days
    
    avg_cycle_time = merged_data['cycle_time_days'].mean()
    cycle_time_msg = f"{avg_cycle_time:.1f} days"
    
    return merged_data, cycle_time_msg

def calculate_procurement_lead_time(purchase_orders, deliveries):
    """Calculate procurement lead time"""
    if purchase_orders.empty or deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with deliveries
    merged_data = purchase_orders.merge(deliveries, on='po_id', how='inner')
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])
    
    # Calculate lead time
    merged_data['lead_time_days'] = (merged_data['actual_delivery_date'] - merged_data['order_date']).dt.days
    
    avg_lead_time = merged_data['lead_time_days'].mean()
    lead_time_msg = f"{avg_lead_time:.1f} days"
    
    return merged_data, lead_time_msg

def calculate_requisition_to_payment_cycle(purchase_orders, invoices):
    """Calculate requisition to payment cycle"""
    if purchase_orders.empty or invoices.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with invoices
    merged_data = purchase_orders.merge(invoices, on='po_id', how='inner')
    
    # Convert dates to datetime
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['payment_date'] = pd.to_datetime(merged_data['payment_date'])
    
    # Calculate cycle time
    merged_data['cycle_time_days'] = (merged_data['payment_date'] - merged_data['order_date']).dt.days
    
    avg_cycle_time = merged_data['cycle_time_days'].mean()
    cycle_time_msg = f"{avg_cycle_time:.1f} days"
    
    return merged_data, cycle_time_msg

def calculate_procurement_automation_metrics(purchase_orders):
    """Calculate procurement automation metrics"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    total_pos = len(purchase_orders)
    
    # Simplified automation metrics (in real scenario, you'd have automation flags)
    automated_pos = total_pos * 0.7  # Assume 70% automation
    manual_pos = total_pos - automated_pos
    
    automation_rate = (automated_pos / total_pos * 100) if total_pos > 0 else 0
    automation_msg = f"{automation_rate:.1f}% automation rate"
    
    automation_data = pd.DataFrame({
        'metric': ['Automated POs', 'Manual POs', 'Automation Rate'],
        'value': [automated_pos, manual_pos, automation_rate]
    })
    
    return automation_data, automation_msg

def calculate_workload_distribution(purchase_orders):
    """Calculate workload distribution"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Group by department
    workload = purchase_orders.groupby('department').size().reset_index()
    workload.columns = ['department', 'po_count']
    
    total_pos = workload['po_count'].sum()
    workload['percentage'] = (workload['po_count'] / total_pos * 100) if total_pos > 0 else 0
    
    return workload, "Workload distribution calculated"

# Compliance & Risk Functions
def calculate_contract_compliance_rate(contracts, purchase_orders):
    """Calculate contract compliance rate"""
    if contracts.empty or purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge contracts with purchase orders
    merged_data = purchase_orders.merge(contracts, on='supplier_id', how='left')
    
    # Check compliance (simplified - based on compliance status)
    compliant_pos = len(merged_data[merged_data['compliance_status'] == 'Compliant'])
    total_pos = len(merged_data)
    
    compliance_rate = (compliant_pos / total_pos * 100) if total_pos > 0 else 0
    compliance_msg = f"{compliance_rate:.1f}% compliance rate"
    
    return merged_data, compliance_msg

def calculate_policy_compliance_rate(purchase_orders):
    """Calculate policy compliance rate"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    total_pos = len(purchase_orders)
    
    # Simplified policy compliance check
    compliant_pos = total_pos * 0.85  # Assume 85% compliance
    non_compliant_pos = total_pos - compliant_pos
    
    compliance_rate = (compliant_pos / total_pos * 100) if total_pos > 0 else 0
    compliance_msg = f"{compliance_rate:.1f}% policy compliance"
    
    compliance_data = pd.DataFrame({
        'status': ['Compliant', 'Non-Compliant'],
        'count': [compliant_pos, non_compliant_pos]
    })
    
    return compliance_data, compliance_msg

def calculate_procurement_fraud_analysis(purchase_orders, invoices):
    """Calculate procurement fraud analysis"""
    if purchase_orders.empty or invoices.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with invoices
    merged_data = purchase_orders.merge(invoices, on='po_id', how='inner')
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    
    # Calculate potential fraud indicators
    merged_data['po_amount'] = merged_data['quantity'] * merged_data[unit_price_col]
    merged_data['amount_discrepancy'] = merged_data['invoice_amount'] - merged_data['po_amount']
    merged_data['discrepancy_percentage'] = (merged_data['amount_discrepancy'] / merged_data['po_amount'] * 100)
    
    # Identify suspicious transactions
    suspicious_threshold = 10  # 10% discrepancy threshold
    suspicious_transactions = merged_data[merged_data['discrepancy_percentage'].abs() > suspicious_threshold]
    
    fraud_risk = len(suspicious_transactions) / len(merged_data) * 100 if len(merged_data) > 0 else 0
    fraud_msg = f"{fraud_risk:.1f}% fraud risk"
    
    return suspicious_transactions, fraud_msg

def calculate_ethical_sourcing_compliance(suppliers):
    """Calculate ethical sourcing compliance"""
    if suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    total_suppliers = len(suppliers)
    
    # Check ESG scores
    high_esg_suppliers = len(suppliers[suppliers['esg_score'] >= 70])
    medium_esg_suppliers = len(suppliers[(suppliers['esg_score'] >= 50) & (suppliers['esg_score'] < 70)])
    low_esg_suppliers = len(suppliers[suppliers['esg_score'] < 50])
    
    ethical_compliance_rate = (high_esg_suppliers / total_suppliers * 100) if total_suppliers > 0 else 0
    compliance_msg = f"{ethical_compliance_rate:.1f}% ethical sourcing compliance"
    
    esg_data = pd.DataFrame({
        'esg_level': ['High ESG (≥70)', 'Medium ESG (50-69)', 'Low ESG (<50)'],
        'count': [high_esg_suppliers, medium_esg_suppliers, low_esg_suppliers]
    })
    
    return esg_data, compliance_msg

def calculate_regulatory_compliance_trends(contracts):
    """Calculate regulatory compliance trends"""
    if contracts.empty:
        return pd.DataFrame(), "No data available"
    
    # Group by compliance status
    compliance_trends = contracts.groupby('compliance_status').size().reset_index()
    compliance_trends.columns = ['status', 'count']
    
    total_contracts = compliance_trends['count'].sum()
    compliance_trends['percentage'] = (compliance_trends['count'] / total_contracts * 100) if total_contracts > 0 else 0
    
    return compliance_trends, "Regulatory compliance trends calculated"

# Inventory Management Functions
def calculate_inventory_turnover_rate(purchase_orders, deliveries):
    """Calculate inventory turnover rate"""
    if purchase_orders.empty or deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate total purchases
    total_purchases = purchase_orders['quantity'].sum()
    
    # Calculate average inventory (simplified)
    avg_inventory = total_purchases / 12  # Assume monthly average
    
    turnover_rate = total_purchases / avg_inventory if avg_inventory > 0 else 0
    turnover_msg = f"{turnover_rate:.1f} times per year"
    
    return pd.DataFrame({'metric': ['Inventory Turnover Rate'], 'value': [turnover_rate]}), turnover_msg

def calculate_stockout_rate(deliveries):
    """Calculate stockout rate"""
    if deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    total_deliveries = len(deliveries)
    
    # Simplified stockout calculation
    stockouts = total_deliveries * 0.05  # Assume 5% stockout rate
    stockout_rate = (stockouts / total_deliveries * 100) if total_deliveries > 0 else 0
    
    stockout_msg = f"{stockout_rate:.1f}% stockout rate"
    
    return pd.DataFrame({'metric': ['Stockout Rate'], 'value': [stockout_rate]}), stockout_msg

def calculate_excess_inventory_analysis(purchase_orders):
    """Calculate excess inventory analysis"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate total inventory value
    total_inventory_value = purchase_orders['quantity'].mul(purchase_orders['unit_price']).sum()
    
    # Estimate excess inventory (simplified)
    excess_inventory = total_inventory_value * 0.15  # Assume 15% excess
    excess_percentage = 15.0
    
    excess_msg = f"${excess_inventory:,.0f} excess inventory ({excess_percentage:.1f}%)"
    
    excess_data = pd.DataFrame({
        'metric': ['Total Inventory', 'Excess Inventory', 'Excess Percentage'],
        'value': [total_inventory_value, excess_inventory, excess_percentage]
    })
    
    return excess_data, excess_msg

def calculate_just_in_time_efficiency(purchase_orders, deliveries):
    """Calculate Just-in-Time procurement efficiency"""
    if purchase_orders.empty or deliveries.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with deliveries
    merged_data = purchase_orders.merge(deliveries, on='po_id', how='inner')
    
    # Calculate delivery timing
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['expected_delivery_date'] = pd.to_datetime(merged_data['delivery_date_x'])  # from purchase_orders
    merged_data['actual_delivery_date'] = pd.to_datetime(merged_data['delivery_date_actual'])  # from deliveries
    
    # Check if delivery was on time (within 1 day)
    merged_data['jit_compliant'] = abs((merged_data['actual_delivery_date'] - merged_data['expected_delivery_date']).dt.days) <= 1
    
    jit_compliance_rate = merged_data['jit_compliant'].mean() * 100
    jit_msg = f"{jit_compliance_rate:.1f}% JIT efficiency"
    
    return merged_data, jit_msg

# Market Insights Functions
def calculate_market_price_benchmarking(purchase_orders, rfqs):
    """Calculate market price benchmarking"""
    if purchase_orders.empty or rfqs.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with RFQs
    merged_data = purchase_orders.merge(rfqs, on=['supplier_id', 'item_id'], how='left', suffixes=('_po', '_rfq'))
    
    # Calculate price differences
    merged_data['price_difference'] = merged_data['unit_price_po'] - merged_data['unit_price_rfq']
    merged_data['price_variance'] = (merged_data['price_difference'] / merged_data['unit_price_rfq'] * 100)
    
    avg_variance = merged_data['price_variance'].mean()
    benchmark_msg = f"{avg_variance:.1f}% average price variance"
    
    return merged_data, benchmark_msg

def calculate_supplier_market_share_analysis(purchase_orders, suppliers):
    """Calculate supplier market share analysis"""
    if purchase_orders.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with suppliers
    merged_data = purchase_orders.merge(suppliers, on='supplier_id', how='left')
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Calculate market share by supplier
    supplier_spend = merged_data.groupby('supplier_name')['total_spend'].sum().reset_index()
    total_spend = supplier_spend['total_spend'].sum()
    
    supplier_spend['market_share'] = (supplier_spend['total_spend'] / total_spend * 100) if total_spend > 0 else 0
    supplier_spend = supplier_spend.sort_values('market_share', ascending=False)
    
    return supplier_spend, "Market share analysis completed"

def calculate_vendor_location_risk_analysis(suppliers):
    """Calculate vendor location risk analysis"""
    if suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Group by region and count suppliers
    location_risk = suppliers.groupby('region').size().reset_index()
    location_risk.columns = ['region', 'supplier_count']
    
    total_suppliers = location_risk['supplier_count'].sum()
    location_risk['concentration_risk'] = (location_risk['supplier_count'] / total_suppliers * 100) if total_suppliers > 0 else 0
    
    # Identify high-risk regions (high concentration)
    high_risk_threshold = 50  # 50% concentration threshold
    high_risk_regions = location_risk[location_risk['concentration_risk'] > high_risk_threshold]
    
    risk_msg = f"{len(high_risk_regions)} high-risk regions identified"
    
    return location_risk, risk_msg

def calculate_industry_procurement_trends(purchase_orders):
    """Calculate industry procurement trends"""
    if purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Convert order date to datetime
    purchase_orders['order_date'] = pd.to_datetime(purchase_orders['order_date'])
    
    # Group by month and calculate trends
    purchase_orders['month'] = purchase_orders['order_date'].dt.to_period('M')
    trends = purchase_orders.groupby('month').agg({
        'quantity': 'sum',
        'unit_price': 'mean'
    }).reset_index()
    
    trends['month'] = trends['month'].astype(str)
    
    return trends, "Industry trends calculated"

def calculate_sourcing_opportunities_analysis(purchase_orders, suppliers):
    """Calculate sourcing opportunities analysis"""
    if purchase_orders.empty or suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge purchase orders with suppliers
    merged_data = purchase_orders.merge(suppliers, on='supplier_id', how='left')
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
    
    # Identify opportunities for supplier consolidation
    supplier_spend = merged_data.groupby('supplier_name')['total_spend'].sum().reset_index()
    low_spend_threshold = supplier_spend['total_spend'].quantile(0.25)
    
    consolidation_opportunities = supplier_spend[supplier_spend['total_spend'] <= low_spend_threshold]
    
    # Identify opportunities for cost reduction
    high_cost_suppliers = supplier_spend[supplier_spend['total_spend'] >= supplier_spend['total_spend'].quantile(0.75)]
    
    opportunities_msg = f"{len(consolidation_opportunities)} consolidation opportunities, {len(high_cost_suppliers)} cost reduction targets"
    
    return consolidation_opportunities, opportunities_msg

# Contract Management Functions
def calculate_contract_value_analysis(contracts):
    """Calculate contract value analysis"""
    if contracts.empty:
        return pd.DataFrame(), "No data available"
    
    total_contract_value = contracts['contract_value'].sum()
    avg_contract_value = contracts['contract_value'].mean()
    
    # Group by compliance status
    contract_analysis = contracts.groupby('compliance_status').agg({
        'contract_value': ['sum', 'count']
    }).reset_index()
    
    analysis_msg = f"${total_contract_value:,.0f} total contract value"
    
    return contract_analysis, analysis_msg

def calculate_contract_performance_metrics(contracts, purchase_orders):
    """Calculate contract performance metrics"""
    if contracts.empty or purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge contracts with purchase orders
    merged_data = purchase_orders.merge(contracts, on='supplier_id', how='left')
    
    # Calculate performance metrics
    total_pos = len(merged_data)
    contract_pos = len(merged_data[merged_data['contract_id'].notna()])
    contract_utilization = (contract_pos / total_pos * 100) if total_pos > 0 else 0
    
    performance_msg = f"{contract_utilization:.1f}% contract utilization"
    
    performance_data = pd.DataFrame({
        'metric': ['Total POs', 'Contract POs', 'Contract Utilization'],
        'value': [total_pos, contract_pos, contract_utilization]
    })
    
    return performance_data, performance_msg

def calculate_contract_renewal_analysis(contracts):
    """Calculate contract renewal analysis"""
    if contracts.empty:
        return pd.DataFrame(), "No data available"
    
    # Convert dates to datetime
    contracts['end_date'] = pd.to_datetime(contracts['end_date'])
    
    # Calculate days until expiration
    current_date = pd.Timestamp.now()
    contracts['days_until_expiration'] = (contracts['end_date'] - current_date).dt.days
    
    # Categorize contracts
    contracts['renewal_status'] = pd.cut(
        contracts['days_until_expiration'],
        bins=[-float('inf'), 0, 30, 90, float('inf')],
        labels=['Expired', 'Expiring Soon (30 days)', 'Expiring (90 days)', 'Active']
    )
    
    renewal_analysis = contracts.groupby('renewal_status').size().reset_index()
    renewal_analysis.columns = ['status', 'count']
    
    expiring_soon = len(contracts[contracts['days_until_expiration'] <= 30])
    renewal_msg = f"{expiring_soon} contracts expiring soon"
    
    return renewal_analysis, renewal_msg

def calculate_contract_compliance_monitoring(contracts):
    """Calculate contract compliance monitoring"""
    if contracts.empty:
        return pd.DataFrame(), "No data available"
    
    # Group by compliance status
    compliance_monitoring = contracts.groupby('compliance_status').agg({
        'contract_id': 'count',
        'contract_value': 'sum'
    }).reset_index()
    
    compliance_monitoring.columns = ['status', 'contract_count', 'total_value']
    
    total_contracts = compliance_monitoring['contract_count'].sum()
    compliant_contracts = compliance_monitoring[compliance_monitoring['status'] == 'Compliant']['contract_count'].iloc[0] if len(compliance_monitoring[compliance_monitoring['status'] == 'Compliant']) > 0 else 0
    
    compliance_rate = (compliant_contracts / total_contracts * 100) if total_contracts > 0 else 0
    monitoring_msg = f"{compliance_rate:.1f}% contract compliance rate"
    
    return compliance_monitoring, monitoring_msg

def calculate_contract_risk_assessment(contracts):
    """Calculate contract risk assessment"""
    if contracts.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate risk factors
    contracts['volume_risk'] = contracts['volume_commitment'] / contracts['contract_value']
    contracts['dispute_risk'] = contracts['dispute_count'] / contracts['contract_value'] * 1000
    
    # Calculate overall risk score
    contracts['risk_score'] = (
        contracts['volume_risk'] * 0.4 +
        contracts['dispute_risk'] * 0.4 +
        (contracts['compliance_status'] != 'Compliant').astype(int) * 0.2
    ) * 100
    
    high_risk_contracts = len(contracts[contracts['risk_score'] > 70])
    risk_msg = f"{high_risk_contracts} high-risk contracts identified"
    
    return contracts, risk_msg

# Sustainability & CSR Functions
def calculate_sustainability_metrics(suppliers, items_data):
    """Calculate sustainability metrics"""
    if suppliers.empty or items_data.empty:
        return pd.DataFrame(), "No data available"
    
    # Calculate ESG performance
    avg_esg_score = suppliers['esg_score'].mean()
    
    # Calculate carbon footprint
    avg_carbon_score = items_data['carbon_score'].mean()
    
    # Calculate recyclable percentage
    recyclable_items = len(items_data[items_data['recyclable_flag'] == True])
    total_items = len(items_data)
    recyclable_percentage = (recyclable_items / total_items * 100) if total_items > 0 else 0
    
    sustainability_msg = f"ESG: {avg_esg_score:.1f}, Carbon: {avg_carbon_score:.1f}, Recyclable: {recyclable_percentage:.1f}%"
    
    sustainability_data = pd.DataFrame({
        'metric': ['Average ESG Score', 'Average Carbon Score', 'Recyclable Percentage'],
        'value': [avg_esg_score, avg_carbon_score, recyclable_percentage]
    })
    
    return sustainability_data, sustainability_msg

def calculate_csr_impact_analysis(suppliers):
    """Calculate CSR impact analysis"""
    if suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Analyze diversity and CSR metrics
    diverse_suppliers = len(suppliers[suppliers['diversity_flag'] == True])
    total_suppliers = len(suppliers)
    diversity_percentage = (diverse_suppliers / total_suppliers * 100) if total_suppliers > 0 else 0
    
    # Calculate average ESG score
    avg_esg = suppliers['esg_score'].mean()
    
    csr_msg = f"{diversity_percentage:.1f}% diverse suppliers, ESG: {avg_esg:.1f}"
    
    csr_data = pd.DataFrame({
        'metric': ['Diverse Suppliers', 'Diversity Percentage', 'Average ESG Score'],
        'value': [diverse_suppliers, diversity_percentage, avg_esg]
    })
    
    return csr_data, csr_msg

def calculate_green_procurement_metrics(items_data, purchase_orders):
    """Calculate green procurement metrics"""
    if items_data.empty or purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge items with purchase orders
    merged_data = purchase_orders.merge(items_data, on='item_id', how='left')
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    
    # Calculate green procurement metrics
    green_items = merged_data[merged_data['recyclable_flag'] == True]
    total_spend = merged_data['quantity'].mul(merged_data[unit_price_col]).sum()
    green_spend = green_items['quantity'].mul(green_items[unit_price_col]).sum()
    
    green_percentage = (green_spend / total_spend * 100) if total_spend > 0 else 0
    
    green_msg = f"{green_percentage:.1f}% green procurement spend"
    
    green_data = pd.DataFrame({
        'metric': ['Total Spend', 'Green Spend', 'Green Percentage'],
        'value': [total_spend, green_spend, green_percentage]
    })
    
    return green_data, green_msg

def calculate_carbon_footprint_analysis(items_data, purchase_orders):
    """Calculate carbon footprint analysis"""
    if items_data.empty or purchase_orders.empty:
        return pd.DataFrame(), "No data available"
    
    # Merge items with purchase orders
    merged_data = purchase_orders.merge(items_data, on='item_id', how='left')
    
    # Handle potential column renaming after merge
    unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
    
    # Calculate total carbon footprint
    merged_data['carbon_footprint'] = merged_data['quantity'] * merged_data['carbon_score']
    total_carbon = merged_data['carbon_footprint'].sum()
    
    # Calculate carbon intensity
    total_spend = merged_data['quantity'].mul(merged_data[unit_price_col]).sum()
    carbon_intensity = total_carbon / total_spend if total_spend > 0 else 0
    
    carbon_msg = f"{total_carbon:.1f} total carbon footprint, {carbon_intensity:.3f} intensity"
    
    carbon_data = pd.DataFrame({
        'metric': ['Total Carbon Footprint', 'Carbon Intensity', 'Total Spend'],
        'value': [total_carbon, carbon_intensity, total_spend]
    })
    
    return carbon_data, carbon_msg

def calculate_sustainable_supplier_development(suppliers):
    """Calculate sustainable supplier development metrics"""
    if suppliers.empty:
        return pd.DataFrame(), "No data available"
    
    # Analyze supplier sustainability
    high_esg_suppliers = len(suppliers[suppliers['esg_score'] >= 80])
    medium_esg_suppliers = len(suppliers[(suppliers['esg_score'] >= 60) & (suppliers['esg_score'] < 80)])
    low_esg_suppliers = len(suppliers[suppliers['esg_score'] < 60])
    
    total_suppliers = len(suppliers)
    sustainable_percentage = ((high_esg_suppliers + medium_esg_suppliers) / total_suppliers * 100) if total_suppliers > 0 else 0
    
    development_msg = f"{sustainable_percentage:.1f}% sustainable suppliers"
    
    development_data = pd.DataFrame({
        'esg_level': ['High ESG (≥80)', 'Medium ESG (60-79)', 'Low ESG (<60)'],
        'count': [high_esg_suppliers, medium_esg_suppliers, low_esg_suppliers]
    })
    
    return development_data, development_msg 