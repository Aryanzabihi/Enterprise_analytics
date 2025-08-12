import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

def calculate_benchmark_price_efficiency(purchase_orders: pd.DataFrame, items_data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Benchmark-Based Price Efficiency to detect overpayment per item or supplier.
    
    Purpose: Detect overpayment per item or supplier
    How: Compare current unit prices to internal median/average and historical lowest price
    Metrics: Price Efficiency Index = Actual Price / Benchmark Price
    Use: Flag suppliers with >110% deviation from benchmark
    """
    try:
        if purchase_orders.empty or items_data.empty:
            return pd.DataFrame(), "No data available for benchmark analysis"
        
        # Merge PO data with items data
        merged_data = purchase_orders.merge(items_data, on='item_id', how='left', suffixes=('', '_item'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching data found after merge"
        
        # Calculate benchmark prices for each item
        item_benchmarks = merged_data.groupby('item_id').agg({
            'unit_price': ['mean', 'median', 'min'],
            'item_name': 'first',
            'category': 'first'
        }).reset_index()
        
        # Flatten column names
        item_benchmarks.columns = ['item_id', 'avg_price', 'median_price', 'min_price', 'item_name', 'category']
        
        # Calculate price efficiency metrics
        efficiency_data = []
        
        for _, item in item_benchmarks.iterrows():
            item_pos = merged_data[merged_data['item_id'] == item['item_id']]
            
            # Calculate efficiency for each PO of this item
            for _, po in item_pos.iterrows():
                # Use median as primary benchmark, fallback to average
                benchmark_price = item['median_price'] if not pd.isna(item['median_price']) else item['avg_price']
                
                if benchmark_price and benchmark_price > 0:
                    efficiency_index = po['unit_price'] / benchmark_price
                    deviation_pct = (efficiency_index - 1) * 100
                    
                    efficiency_data.append({
                        'item_id': po['item_id'],
                        'item_name': po['item_name'],
                        'category': po['category'],
                        'supplier_id': po['supplier_id'],
                        'actual_price': po['unit_price'],
                        'benchmark_price': benchmark_price,
                        'efficiency_index': efficiency_index,
                        'deviation_pct': deviation_pct,
                        'is_overpriced': efficiency_index > 1.1,  # >110% of benchmark
                        'quantity': po['quantity'],
                        'total_spend': po['quantity'] * po['unit_price']
                    })
        
        if not efficiency_data:
            return pd.DataFrame(), "No efficiency data calculated"
        
        efficiency_df = pd.DataFrame(efficiency_data)
        
        # Calculate summary metrics
        overpriced_items = efficiency_df[efficiency_df['is_overpriced']]
        avg_efficiency = efficiency_df['efficiency_index'].mean()
        overpriced_spend = overpriced_items['total_spend'].sum()
        total_spend = efficiency_df['total_spend'].sum()
        
        summary_msg = f"Avg Efficiency: {avg_efficiency:.2f} | Overpriced Items: {len(overpriced_items)} | Overpriced Spend: ${overpriced_spend:,.0f} ({overpriced_spend/total_spend*100:.1f}% of total)"
        
        return efficiency_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating benchmark efficiency: {str(e)}"

def calculate_negotiation_opportunity_index(purchase_orders: pd.DataFrame, items_data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Negotiation Opportunity Index to identify suppliers or items with potential for renegotiation.
    
    Purpose: Identify suppliers or items with potential for renegotiation
    How: High volume, low price variation = negotiation leverage
    Items frequently purchased from multiple vendors = competition
    Score Formula: Opportunity Score = Volume Weight × (1 - Price StdDev / Mean)
    """
    try:
        if purchase_orders.empty or items_data.empty:
            return pd.DataFrame(), "No data available for negotiation opportunity analysis"
        
        # Merge PO data with items data
        merged_data = purchase_orders.merge(items_data, on='item_id', how='left', suffixes=('', '_item'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching data found after merge"
        
        # Calculate opportunity metrics by item-supplier combination
        opportunity_data = []
        
        # Group by item to find items with multiple suppliers
        item_supplier_analysis = merged_data.groupby(['item_id', 'supplier_id']).agg({
            'unit_price': ['mean', 'std', 'count'],
            'quantity': 'sum',
            'item_name': 'first',
            'category': 'first'
        }).reset_index()
        
        # Flatten column names
        item_supplier_analysis.columns = ['item_id', 'supplier_id', 'avg_price', 'price_std', 'po_count', 'total_quantity', 'item_name', 'category']
        
        # Calculate opportunity scores
        for _, row in item_supplier_analysis.iterrows():
            # Get all suppliers for this item
            item_suppliers = item_supplier_analysis[item_supplier_analysis['item_id'] == row['item_id']]
            
            # Volume weight (higher volume = more leverage)
            volume_weight = min(row['total_quantity'] / item_suppliers['total_quantity'].max(), 1.0)
            
            # Price variation (lower variation = more leverage)
            price_cv = row['price_std'] / row['avg_price'] if row['avg_price'] > 0 else 0
            price_variation_factor = max(0, 1 - price_cv)
            
            # Competition factor (more suppliers = more competition)
            competition_factor = min(len(item_suppliers) / 3, 1.0)  # Normalize to max 3 suppliers
            
            # Calculate opportunity score
            opportunity_score = volume_weight * price_variation_factor * competition_factor
            
            # Determine opportunity level
            if opportunity_score >= 0.7:
                opportunity_level = "High"
            elif opportunity_score >= 0.4:
                opportunity_level = "Medium"
            else:
                opportunity_level = "Low"
            
            opportunity_data.append({
                'item_id': row['item_id'],
                'item_name': row['item_name'],
                'category': row['category'],
                'supplier_id': row['supplier_id'],
                'avg_price': row['avg_price'],
                'price_std': row['price_std'],
                'po_count': row['po_count'],
                'total_quantity': row['total_quantity'],
                'volume_weight': volume_weight,
                'price_variation_factor': price_variation_factor,
                'competition_factor': competition_factor,
                'opportunity_score': opportunity_score,
                'opportunity_level': opportunity_level
            })
        
        if not opportunity_data:
            return pd.DataFrame(), "No opportunity data calculated"
        
        opportunity_df = pd.DataFrame(opportunity_data)
        
        # Calculate summary metrics
        high_opportunity = opportunity_df[opportunity_df['opportunity_level'] == 'High']
        avg_score = opportunity_df['opportunity_score'].mean()
        
        summary_msg = f"Avg Opportunity Score: {avg_score:.2f} | High Opportunity Items: {len(high_opportunity)}"
        
        return opportunity_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating negotiation opportunity: {str(e)}"

def calculate_tail_spend_optimization(purchase_orders: pd.DataFrame, suppliers: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Tail Spend Optimization to reduce admin cost and leakage from many small-value purchases.
    
    Purpose: Reduce admin cost and leakage from many small-value purchases
    How: Detect bottom 20% of suppliers that account for <5% of spend
    Suggest consolidation or catalog contracts
    Metric: Tail Spend % of Total Spend of Non-contracted Small Vendors
    """
    try:
        if purchase_orders.empty or suppliers.empty:
            return pd.DataFrame(), "No data available for tail spend analysis"
        
        # Calculate spend by supplier
        supplier_spend = purchase_orders.groupby('supplier_id').agg({
            'quantity': 'sum',
            'unit_price': lambda x: (x * purchase_orders.loc[x.index, 'quantity']).sum(),
            'po_id': 'count'
        }).reset_index()
        
        supplier_spend.columns = ['supplier_id', 'total_quantity', 'total_spend', 'po_count']
        
        # Add supplier names
        supplier_spend = supplier_spend.merge(suppliers[['supplier_id', 'supplier_name']], on='supplier_id', how='left')
        
        # Calculate total spend
        total_spend = supplier_spend['total_spend'].sum()
        
        # Calculate cumulative spend percentage
        supplier_spend = supplier_spend.sort_values('total_spend', ascending=False)
        supplier_spend['spend_pct'] = supplier_spend['total_spend'] / total_spend * 100
        supplier_spend['cumulative_spend_pct'] = supplier_spend['spend_pct'].cumsum()
        
        # Identify tail spend suppliers (bottom 20% by spend)
        tail_threshold = supplier_spend['cumulative_spend_pct'].quantile(0.8)  # 80th percentile
        tail_suppliers = supplier_spend[supplier_spend['cumulative_spend_pct'] > tail_threshold]
        
        # Calculate tail spend metrics
        tail_spend_total = tail_suppliers['total_spend'].sum()
        tail_spend_pct = tail_spend_total / total_spend * 100
        avg_po_value_tail = tail_suppliers['total_spend'].sum() / tail_suppliers['po_count'].sum() if tail_suppliers['po_count'].sum() > 0 else 0
        
        # Identify consolidation opportunities
        consolidation_data = []
        for _, supplier in tail_suppliers.iterrows():
            # Calculate potential savings from consolidation
            # Assume 15% savings from reducing transaction costs and better pricing
            potential_savings = supplier['total_spend'] * 0.15
            
            consolidation_data.append({
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'total_spend': supplier['total_spend'],
                'spend_pct': supplier['spend_pct'],
                'po_count': supplier['po_count'],
                'avg_po_value': supplier['total_spend'] / supplier['po_count'],
                'potential_savings': potential_savings,
                'consolidation_priority': 'High' if supplier['po_count'] > 5 else 'Medium'
            })
        
        consolidation_df = pd.DataFrame(consolidation_data)
        
        summary_msg = f"Tail Spend: ${tail_spend_total:,.0f} ({tail_spend_pct:.1f}% of total) | Tail Suppliers: {len(tail_suppliers)} | Avg PO Value: ${avg_po_value_tail:,.0f}"
        
        return consolidation_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating tail spend optimization: {str(e)}"

def calculate_unit_cost_trend_analysis(purchase_orders: pd.DataFrame, items_data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Unit Cost Trend Analysis to monitor inflation or procurement efficiency.
    
    Purpose: Monitor inflation or procurement efficiency
    How: Track unit price per SKU over time
    Flag sharp increases not justified by quantity or market
    """
    try:
        if purchase_orders.empty or items_data.empty:
            return pd.DataFrame(), "No data available for unit cost trend analysis"
        
        # Merge PO data with items data
        merged_data = purchase_orders.merge(items_data, on='item_id', how='left', suffixes=('', '_item'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching data found after merge"
        
        # Convert order_date to datetime if not already
        merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
        merged_data['month'] = merged_data['order_date'].dt.to_period('M')
        
        # Calculate monthly trends by item
        trend_data = []
        
        for item_id in merged_data['item_id'].unique():
            item_data = merged_data[merged_data['item_id'] == item_id]
            item_name = item_data['item_name'].iloc[0]
            category = item_data['category'].iloc[0]
            
            # Monthly aggregation
            monthly_data = item_data.groupby('month').agg({
                'unit_price': ['mean', 'std', 'count'],
                'quantity': 'sum'
            }).reset_index()
            
            monthly_data.columns = ['month', 'avg_price', 'price_std', 'po_count', 'total_quantity']
            
            # Calculate trend metrics
            if len(monthly_data) > 1:
                # Price trend (linear regression slope)
                x = np.arange(len(monthly_data))
                y = monthly_data['avg_price'].values
                slope = np.polyfit(x, y, 1)[0]
                
                # Price volatility
                price_volatility = monthly_data['price_std'].mean() / monthly_data['avg_price'].mean() if monthly_data['avg_price'].mean() > 0 else 0
                
                # Identify anomalies (prices > 2 std dev from mean)
                overall_mean = monthly_data['avg_price'].mean()
                overall_std = monthly_data['avg_price'].std()
                anomaly_threshold = overall_mean + 2 * overall_std
                
                anomalies = monthly_data[monthly_data['avg_price'] > anomaly_threshold]
                
                trend_data.append({
                    'item_id': item_id,
                    'item_name': item_name,
                    'category': category,
                    'trend_slope': slope,
                    'price_volatility': price_volatility,
                    'trend_direction': 'Increasing' if slope > 0 else 'Decreasing',
                    'anomaly_count': len(anomalies),
                    'avg_price': overall_mean,
                    'price_range': monthly_data['avg_price'].max() - monthly_data['avg_price'].min(),
                    'total_quantity': monthly_data['total_quantity'].sum(),
                    'po_count': monthly_data['po_count'].sum()
                })
        
        if not trend_data:
            return pd.DataFrame(), "No trend data calculated"
        
        trend_df = pd.DataFrame(trend_data)
        
        # Calculate summary metrics
        increasing_items = trend_df[trend_df['trend_direction'] == 'Increasing']
        avg_volatility = trend_df['price_volatility'].mean()
        total_anomalies = trend_df['anomaly_count'].sum()
        
        summary_msg = f"Increasing Price Items: {len(increasing_items)} | Avg Volatility: {avg_volatility:.2f} | Total Anomalies: {total_anomalies}"
        
        return trend_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating unit cost trends: {str(e)}"

def calculate_savings_realization_tracking(purchase_orders: pd.DataFrame, rfqs: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Savings Realization Tracking to compare forecast vs realized savings.
    
    Purpose: Compare forecast vs realized savings
    How: If strategic sourcing promised savings (e.g., 5% vs baseline), track whether actual prices reflect it
    You could compute: Savings Gap = Forecast Savings – Realized Savings
    """
    try:
        if purchase_orders.empty or rfqs.empty:
            return pd.DataFrame(), "No data available for savings realization tracking"
        
        # Merge RFQ and PO data to compare forecast vs actual
        merged_data = rfqs.merge(purchase_orders, on=['supplier_id', 'item_id'], how='inner', suffixes=('_rfq', '_po'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching RFQ-PO data found for savings tracking"
        
        # Calculate savings realization metrics
        realization_data = []
        
        for _, row in merged_data.iterrows():
            # Calculate actual savings
            actual_savings = row['rfq_cost'] - row['po_cost']
            actual_savings_pct = (actual_savings / row['rfq_cost']) * 100 if row['rfq_cost'] > 0 else 0
            
            # Assume target savings of 5% (this could be configurable)
            target_savings_pct = 5.0
            target_savings = row['rfq_cost'] * (target_savings_pct / 100)
            
            # Calculate savings gap
            savings_gap = target_savings - actual_savings
            savings_gap_pct = (savings_gap / row['rfq_cost']) * 100 if row['rfq_cost'] > 0 else 0
            
            # Determine realization status
            if actual_savings_pct >= target_savings_pct:
                realization_status = "Exceeded Target"
            elif actual_savings_pct >= target_savings_pct * 0.8:
                realization_status = "Near Target"
            else:
                realization_status = "Below Target"
            
            realization_data.append({
                'item_id': row['item_id'],
                'supplier_id': row['supplier_id'],
                'rfq_cost': row['rfq_cost'],
                'po_cost': row['po_cost'],
                'actual_savings': actual_savings,
                'actual_savings_pct': actual_savings_pct,
                'target_savings': target_savings,
                'target_savings_pct': target_savings_pct,
                'savings_gap': savings_gap,
                'savings_gap_pct': savings_gap_pct,
                'realization_status': realization_status,
                'quantity': row['quantity']
            })
        
        if not realization_data:
            return pd.DataFrame(), "No realization data calculated"
        
        realization_df = pd.DataFrame(realization_data)
        
        # Calculate summary metrics
        exceeded_target = realization_df[realization_df['realization_status'] == 'Exceeded Target']
        below_target = realization_df[realization_df['realization_status'] == 'Below Target']
        avg_realization = realization_df['actual_savings_pct'].mean()
        total_savings_gap = realization_df['savings_gap'].sum()
        
        summary_msg = f"Avg Realization: {avg_realization:.1f}% | Exceeded Target: {len(exceeded_target)} | Below Target: {len(below_target)} | Total Gap: ${total_savings_gap:,.0f}"
        
        return realization_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating savings realization: {str(e)}"

def calculate_spend_avoidance_detection(purchase_orders: pd.DataFrame, items_data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Spend Avoidance Detection to quantify avoided costs due to better sourcing, negotiation, or specification changes.
    
    Purpose: Quantify avoided costs due to better sourcing, negotiation, or specification changes
    Examples: Switching from Supplier A ($1.50) to B ($1.00)
    Using standard part instead of custom part
    """
    try:
        if purchase_orders.empty or items_data.empty:
            return pd.DataFrame(), "No data available for spend avoidance analysis"
        
        # Merge PO data with items data
        merged_data = purchase_orders.merge(items_data, on='item_id', how='left', suffixes=('', '_item'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching data found after merge"
        
        # Calculate spend avoidance opportunities
        avoidance_data = []
        
        # Group by item to find price variations
        item_analysis = merged_data.groupby('item_id').agg({
            'unit_price': ['mean', 'min', 'max', 'std'],
            'item_name': 'first',
            'category': 'first',
            'supplier_id': 'nunique'
        }).reset_index()
        
        # Flatten column names
        item_analysis.columns = ['item_id', 'avg_price', 'min_price', 'max_price', 'price_std', 'item_name', 'category', 'supplier_count']
        
        for _, item in item_analysis.iterrows():
            # Get all POs for this item
            item_pos = merged_data[merged_data['item_id'] == item['item_id']]
            
            # Calculate potential savings from switching to lowest price supplier
            if item['supplier_count'] > 1 and item['min_price'] < item['avg_price']:
                # Calculate current spend
                current_spend = (item_pos['quantity'] * item_pos['unit_price']).sum()
                
                # Calculate potential spend at minimum price
                potential_spend = (item_pos['quantity'] * item['min_price']).sum()
                
                # Calculate avoided cost
                avoided_cost = current_spend - potential_spend
                avoided_cost_pct = (avoided_cost / current_spend) * 100 if current_spend > 0 else 0
                
                # Determine avoidance type
                if item['price_std'] / item['avg_price'] > 0.2:  # High price variation
                    avoidance_type = "Supplier Switching"
                else:
                    avoidance_type = "Price Negotiation"
                
                avoidance_data.append({
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    'category': item['category'],
                    'current_avg_price': item['avg_price'],
                    'min_price': item['min_price'],
                    'price_variation_pct': ((item['max_price'] - item['min_price']) / item['avg_price']) * 100,
                    'supplier_count': item['supplier_count'],
                    'current_spend': current_spend,
                    'potential_spend': potential_spend,
                    'avoided_cost': avoided_cost,
                    'avoided_cost_pct': avoided_cost_pct,
                    'avoidance_type': avoidance_type,
                    'priority': 'High' if avoided_cost_pct > 10 else 'Medium'
                })
        
        if not avoidance_data:
            return pd.DataFrame(), "No avoidance opportunities found"
        
        avoidance_df = pd.DataFrame(avoidance_data)
        
        # Calculate summary metrics
        total_avoided_cost = avoidance_df['avoided_cost'].sum()
        high_priority_opportunities = avoidance_df[avoidance_df['priority'] == 'High']
        avg_avoidance_pct = avoidance_df['avoided_cost_pct'].mean()
        
        summary_msg = f"Total Avoided Cost: ${total_avoided_cost:,.0f} | High Priority: {len(high_priority_opportunities)} | Avg Avoidance: {avg_avoidance_pct:.1f}%"
        
        return avoidance_df, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating spend avoidance: {str(e)}"

def calculate_contract_leakage(purchase_orders: pd.DataFrame, contracts: pd.DataFrame, items_data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Calculate Contract Leakage to show % of spend going outside negotiated contracts.
    
    Purpose: Show % of spend going outside negotiated contracts
    How: Compare actual PO supplier vs contracted supplier for each item/category
    Metric: Leakage % = Off-Contract Spend / Total Spend on Contracted Items
    """
    try:
        if purchase_orders.empty or contracts.empty or items_data.empty:
            return pd.DataFrame(), "No data available for contract leakage analysis"
        
        # Merge PO data with items data
        merged_data = purchase_orders.merge(items_data, on='item_id', how='left', suffixes=('', '_item'))
        
        if merged_data.empty:
            return pd.DataFrame(), "No matching data found after merge"
        
        # Merge with contracts data
        # Note: This assumes contracts have item_id and supplier_id columns
        # If contracts structure is different, this needs to be adjusted
        contract_analysis = merged_data.merge(
            contracts[['contract_id', 'supplier_id', 'item_id', 'contract_value']], 
            on=['supplier_id', 'item_id'], 
            how='left', 
            suffixes=('', '_contract')
        )
        
        # Identify contracted vs non-contracted purchases
        contract_analysis['is_contracted'] = contract_analysis['contract_id'].notna()
        contract_analysis['total_spend'] = contract_analysis['quantity'] * contract_analysis['unit_price']
        
        # Calculate leakage metrics
        total_spend = contract_analysis['total_spend'].sum()
        contracted_spend = contract_analysis[contract_analysis['is_contracted']]['total_spend'].sum()
        off_contract_spend = total_spend - contracted_spend
        leakage_pct = (off_contract_spend / total_spend) * 100 if total_spend > 0 else 0
        
        # Analyze leakage by category
        leakage_by_category = contract_analysis.groupby('category').agg({
            'total_spend': 'sum',
            'is_contracted': lambda x: (x == True).sum(),
            'po_id': 'count'
        }).reset_index()
        
        leakage_by_category.columns = ['category', 'total_spend', 'contracted_pos', 'total_pos']
        leakage_by_category['contracted_spend'] = leakage_by_category['total_spend'] * (leakage_by_category['contracted_pos'] / leakage_by_category['total_pos'])
        leakage_by_category['off_contract_spend'] = leakage_by_category['total_spend'] - leakage_by_category['contracted_spend']
        leakage_by_category['leakage_pct'] = (leakage_by_category['off_contract_spend'] / leakage_by_category['total_spend']) * 100
        
        # Identify high leakage items
        high_leakage_items = contract_analysis[~contract_analysis['is_contracted']].groupby(['item_id', 'item_name', 'category']).agg({
            'total_spend': 'sum',
            'po_id': 'count'
        }).reset_index()
        
        high_leakage_items = high_leakage_items.sort_values('total_spend', ascending=False)
        
        summary_msg = f"Contract Leakage: {leakage_pct:.1f}% | Off-Contract Spend: ${off_contract_spend:,.0f} | Contracted Spend: ${contracted_spend:,.0f}"
        
        # Combine results
        result_data = {
            'summary': {
                'total_spend': total_spend,
                'contracted_spend': contracted_spend,
                'off_contract_spend': off_contract_spend,
                'leakage_pct': leakage_pct
            },
            'by_category': leakage_by_category,
            'high_leakage_items': high_leakage_items
        }
        
        return result_data, summary_msg
        
    except Exception as e:
        return pd.DataFrame(), f"Error calculating contract leakage: {str(e)}" 