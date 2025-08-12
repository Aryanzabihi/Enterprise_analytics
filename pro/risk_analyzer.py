import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple

class ProcurementRiskAnalyzer:
    """Comprehensive risk analysis tool for procurement operations"""
    
    def __init__(self, purchase_orders, suppliers, items_data, deliveries, invoices, contracts, budgets, rfqs):
        self.purchase_orders = purchase_orders
        self.suppliers = suppliers
        self.items_data = items_data
        self.deliveries = deliveries
        self.invoices = invoices
        self.contracts = contracts
        self.budgets = budgets
        self.rfqs = rfqs
        
        # Risk scoring weights (can be customized)
        self.risk_weights = {
            'supplier_risk': 0.25,
            'contractual_risk': 0.20,
            'pricing_cost_risk': 0.15,
            'delivery_risk': 0.15,
            'fraud_manipulation_risk': 0.10,
            'market_risk': 0.05,
            'compliance_risk': 0.05,
            'process_risk': 0.05
        }
    
    def analyze_supplier_risk(self) -> Dict:
        """Analyze supplier-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        if self.suppliers.empty or self.purchase_orders.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['Insufficient supplier data'],
                'mitigation': ['Collect comprehensive supplier information']
            }
        
        # Supplier concentration risk
        supplier_spend = self.purchase_orders.merge(self.suppliers, on='supplier_id', how='left')
        supplier_spend['total_spend'] = supplier_spend['quantity'] * supplier_spend['unit_price']
        top_suppliers = supplier_spend.groupby('supplier_name')['total_spend'].sum().sort_values(ascending=False)
        
        if not top_suppliers.empty:
            top_supplier_pct = (top_suppliers.iloc[0] / top_suppliers.sum()) * 100
            
            if top_supplier_pct > 40:
                risk_score += 40
                risk_factors.append(f"High supplier concentration: {top_supplier_pct:.1f}% from top supplier")
            elif top_supplier_pct > 25:
                risk_score += 25
                risk_factors.append(f"Moderate supplier concentration: {top_supplier_pct:.1f}% from top supplier")
        
        # Supplier performance risk
        if not self.deliveries.empty:
            delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
            
            # Check if supplier_id exists in both dataframes before merging
            if 'supplier_id' in delivery_analysis.columns and 'supplier_id' in self.suppliers.columns:
                delivery_analysis = delivery_analysis.merge(self.suppliers, on='supplier_id', how='left')
                
                if 'delivery_date_actual' in delivery_analysis.columns and 'delivery_date' in delivery_analysis.columns:
                    delivery_analysis['on_time'] = pd.to_datetime(delivery_analysis['delivery_date_actual']) <= pd.to_datetime(delivery_analysis['delivery_date'])
                    otif_rate = delivery_analysis['on_time'].mean() * 100
                    
                    if otif_rate < 80:
                        risk_score += 30
                        risk_factors.append(f"Poor delivery performance: {otif_rate:.1f}% on-time rate")
                    elif otif_rate < 90:
                        risk_score += 15
                        risk_factors.append(f"Below-average delivery performance: {otif_rate:.1f}% on-time rate")
        
        # Supplier financial risk (if ESG scores available)
        if 'esg_score' in self.suppliers.columns:
            low_esg_suppliers = self.suppliers[self.suppliers['esg_score'] < 50]
            if not low_esg_suppliers.empty:
                risk_score += 20
                risk_factors.append(f"{len(low_esg_suppliers)} suppliers with low ESG scores")
        
        # Geographic concentration risk
        if 'country' in self.suppliers.columns:
            country_counts = self.suppliers['country'].value_counts()
            single_country_suppliers = country_counts[country_counts == 1]
            if len(single_country_suppliers) > 0:
                risk_score += 15
                risk_factors.append(f"{len(single_country_suppliers)} countries with single suppliers")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if top_supplier_pct > 25:
            mitigation.extend([
                "Develop supplier diversification strategy",
                "Identify and qualify backup suppliers",
                "Implement supplier relationship management program"
            ])
        
        # Check if otif_rate was calculated
        otif_rate = 0
        if not self.deliveries.empty:
            delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
            if 'supplier_id' in delivery_analysis.columns and 'supplier_id' in self.suppliers.columns:
                delivery_analysis = delivery_analysis.merge(self.suppliers, on='supplier_id', how='left')
                if 'delivery_date_actual' in delivery_analysis.columns and 'delivery_date' in delivery_analysis.columns:
                    delivery_analysis['on_time'] = pd.to_datetime(delivery_analysis['delivery_date_actual']) <= pd.to_datetime(delivery_analysis['delivery_date'])
                    otif_rate = delivery_analysis['on_time'].mean() * 100
        
        if otif_rate < 90:
            mitigation.extend([
                "Establish supplier performance improvement programs",
                "Implement delivery performance monitoring",
                "Develop supplier development initiatives"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring supplier performance")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_contractual_risk(self) -> Dict:
        """Analyze contract-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        if self.contracts.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['No contract data available'],
                'mitigation': ['Implement contract management system']
            }
        
        # Contract compliance risk
        active_contracts = self.contracts[
            (pd.to_datetime(self.contracts['end_date']) >= datetime.now()) &
            (self.contracts['compliance_status'] != 'Compliant')
        ]
        
        if not active_contracts.empty:
            risk_score += 35
            risk_factors.append(f"{len(active_contracts)} active contracts with compliance issues")
        
        # Contract expiration risk
        expiring_contracts = self.contracts[
            pd.to_datetime(self.contracts['end_date']) <= (datetime.now() + timedelta(days=90))
        ]
        
        if not expiring_contracts.empty:
            risk_score += 25
            total_value = expiring_contracts['contract_value'].sum()
            risk_factors.append(f"{len(expiring_contracts)} contracts expiring in 90 days (${total_value:,.0f})")
        
        # Contract value concentration
        if len(self.contracts) > 0:
            top_contract_pct = (self.contracts['contract_value'].max() / self.contracts['contract_value'].sum()) * 100
            if top_contract_pct > 50:
                risk_score += 20
                risk_factors.append(f"High contract value concentration: {top_contract_pct:.1f}% in single contract")
        
        # Contract term analysis
        if 'start_date' in self.contracts.columns and 'end_date' in self.contracts.columns:
            self.contracts['duration'] = (pd.to_datetime(self.contracts['end_date']) - 
                                        pd.to_datetime(self.contracts['start_date'])).dt.days
            short_contracts = self.contracts[self.contracts['duration'] < 30]
            if not short_contracts.empty:
                risk_score += 15
                risk_factors.append(f"{len(short_contracts)} contracts with very short terms (<30 days)")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if not active_contracts.empty:
            mitigation.extend([
                "Review and address compliance issues",
                "Implement contract compliance monitoring",
                "Establish corrective action plans"
            ])
        if not expiring_contracts.empty:
            mitigation.extend([
                "Develop contract renewal strategies",
                "Identify alternative suppliers for expiring contracts",
                "Implement contract lifecycle management"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring contract performance")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_pricing_cost_risk(self) -> Dict:
        """Analyze pricing and cost-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        # Initialize variables to avoid scope issues
        high_volatility = pd.DataFrame()
        high_price_items = pd.Series()
        over_budget = pd.DataFrame()
        
        if self.purchase_orders.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['No purchase order data available'],
                'mitigation': ['Implement cost monitoring system']
            }
        
        # Price volatility analysis
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            # Use unit_price from purchase_orders (primary source)
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            if unit_price_col in merged_data.columns:
                price_volatility = merged_data.groupby('item_name')[unit_price_col].agg(['mean', 'std']).reset_index()
                price_volatility['cv'] = price_volatility['std'] / price_volatility['mean']
                
                high_volatility = price_volatility[price_volatility['cv'] > 0.3]
                if not high_volatility.empty:
                    risk_score += 30
                    risk_factors.append(f"{len(high_volatility)} items with high price volatility (>30%)")
        
        # Abnormal pricing detection
        if not self.items_data.empty:
            # Identify items with prices significantly above average
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            if unit_price_col in merged_data.columns:
                item_avg_prices = merged_data.groupby('item_name')[unit_price_col].mean()
                overall_avg = item_avg_prices.mean()
                high_price_items = item_avg_prices[item_avg_prices > overall_avg * 2]
                
                if not high_price_items.empty:
                    risk_score += 25
                    risk_factors.append(f"{len(high_price_items)} items with abnormally high prices")
        
        # RFQ price variance analysis
        if not self.rfqs.empty:
            rfq_analysis = self.rfqs.groupby(['supplier_id', 'item_id'])['unit_price'].agg(['count', 'mean', 'std']).reset_index()
            rfq_analysis = rfq_analysis[rfq_analysis['count'] >= 3]  # Only items with multiple quotes
            
            if not rfq_analysis.empty:
                rfq_analysis['cv'] = rfq_analysis['std'] / rfq_analysis['mean']
                high_variance = rfq_analysis[rfq_analysis['cv'] > 0.5]
                
                if not high_variance.empty:
                    risk_score += 20
                    risk_factors.append(f"{len(high_variance)} items with high quote variance (>50%)")
        
        # Budget overrun risk
        if not self.budgets.empty:
            budget_analysis = self.purchase_orders.merge(self.budgets, on='budget_code', how='left')
            budget_analysis['total_spend'] = budget_analysis['quantity'] * budget_analysis['unit_price']
            budget_utilization = budget_analysis.groupby('budget_code').agg({
                'budget_amount': 'first',
                'total_spend': 'sum'
            }).reset_index()
            budget_utilization['utilization_rate'] = (budget_utilization['total_spend'] / budget_utilization['budget_amount']) * 100
            
            over_budget = budget_utilization[budget_utilization['utilization_rate'] > 100]
            if not over_budget.empty:
                risk_score += 25
                risk_factors.append(f"{len(over_budget)} budget codes exceeded 100% utilization")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if not high_volatility.empty:
            mitigation.extend([
                "Implement price monitoring and alerting",
                "Develop price hedging strategies",
                "Establish long-term supply agreements"
            ])
        if not high_price_items.empty:
            mitigation.extend([
                "Conduct market price analysis",
                "Negotiate better pricing terms",
                "Explore alternative suppliers"
            ])
        if not over_budget.empty:
            mitigation.extend([
                "Implement budget control measures",
                "Review budget allocation and forecasting",
                "Establish cost monitoring dashboards"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring pricing trends")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_delivery_risk(self) -> Dict:
        """Analyze delivery-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        if self.purchase_orders.empty or self.deliveries.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['Insufficient delivery data'],
                'mitigation': ['Implement delivery tracking system']
            }
        
        # On-time delivery risk
        delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
        otif_rate = 0  # Initialize otif_rate
        
        # Check if supplier_id exists in both dataframes before merging
        if 'supplier_id' in delivery_analysis.columns and 'supplier_id' in self.suppliers.columns:
            delivery_analysis = delivery_analysis.merge(self.suppliers, on='supplier_id', how='left')
        
        if 'delivery_date_actual' in delivery_analysis.columns and 'delivery_date' in delivery_analysis.columns:
            delivery_analysis['on_time'] = pd.to_datetime(delivery_analysis['delivery_date_actual']) <= pd.to_datetime(delivery_analysis['delivery_date'])
            otif_rate = delivery_analysis['on_time'].mean() * 100
            
            if otif_rate < 80:
                risk_score += 40
                risk_factors.append(f"Poor on-time delivery: {otif_rate:.1f}% rate")
            elif otif_rate < 90:
                risk_score += 25
                risk_factors.append(f"Below-average delivery: {otif_rate:.1f}% rate")
        
        # Lead time variability risk
        lead_time_std = 0
        avg_lead_time = 0
        if 'delivery_date_actual' in delivery_analysis.columns:
            delivery_analysis['lead_time'] = (pd.to_datetime(delivery_analysis['delivery_date_actual']) - 
                                            pd.to_datetime(delivery_analysis['order_date'])).dt.days
            
            lead_time_std = delivery_analysis['lead_time'].std()
            avg_lead_time = delivery_analysis['lead_time'].mean()
            
            if lead_time_std > avg_lead_time * 0.5:
                risk_score += 25
                risk_factors.append(f"High lead time variability: {lead_time_std:.1f} days std dev")
        
        # Quality risk
        total_defects = delivery_analysis['defect_flag'].sum()
        total_deliveries = len(delivery_analysis)
        defect_rate = (total_defects / total_deliveries) * 100 if total_deliveries > 0 else 0
        
        if defect_rate > 5:
            risk_score += 20
            risk_factors.append(f"High defect rate: {defect_rate:.1f}%")
        elif defect_rate > 2:
            risk_score += 10
            risk_factors.append(f"Moderate defect rate: {defect_rate:.1f}%")
        
        # Supplier-specific delivery issues
        if 'supplier_name' in delivery_analysis.columns and 'on_time' in delivery_analysis.columns:
            supplier_performance = delivery_analysis.groupby('supplier_name').agg({
                'on_time': 'mean',
                'po_id': 'count'
            }).reset_index()
            supplier_performance.columns = ['supplier_name', 'otif_rate', 'order_count']
            supplier_performance['otif_rate'] = supplier_performance['otif_rate'] * 100
            
            poor_performers = supplier_performance[
                (supplier_performance['otif_rate'] < 80) & 
                (supplier_performance['order_count'] >= 5)
            ]
            
            if not poor_performers.empty:
                risk_score += 15
                risk_factors.append(f"{len(poor_performers)} suppliers with poor delivery performance")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if otif_rate < 90:
            mitigation.extend([
                "Implement supplier performance improvement programs",
                "Establish delivery performance targets",
                "Develop supplier development initiatives"
            ])
        if lead_time_std > avg_lead_time * 0.5:
            mitigation.extend([
                "Standardize lead time requirements",
                "Implement supply chain optimization",
                "Establish buffer inventory strategies"
            ])
        if defect_rate > 2:
            mitigation.extend([
                "Implement quality control measures",
                "Establish supplier quality standards",
                "Develop quality improvement programs"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring delivery performance")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_fraud_manipulation_risk(self) -> Dict:
        """Analyze fraud and manipulation risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        # Initialize variables to avoid scope issues
        suspicious_rfqs = pd.DataFrame()
        high_price_suppliers = pd.DataFrame()
        single_bidder_rfqs = pd.Series()
        
        if self.purchase_orders.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['No purchase order data available'],
                'mitigation': ['Implement fraud detection systems']
            }
        
        # Bid rigging indicators
        if not self.rfqs.empty:
            # Analyze bidding patterns
            rfq_analysis = self.rfqs.groupby(['item_id', 'rfq_id'])['unit_price'].agg(['count', 'mean', 'std']).reset_index()
            
            # Check for suspicious bidding patterns
            suspicious_rfqs = rfq_analysis[
                (rfq_analysis['count'] >= 3) &  # Multiple bidders
                (rfq_analysis['std'] / rfq_analysis['mean'] < 0.05)  # Very low variance
            ]
            
            if not suspicious_rfqs.empty:
                risk_score += 35
                risk_factors.append(f"{len(suspicious_rfqs)} RFQs with suspicious bidding patterns")
        
        # Price manipulation indicators
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            
            # Check for unusual price patterns
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            if unit_price_col in merged_data.columns and 'supplier_id' in merged_data.columns:
                price_analysis = merged_data.groupby(['item_name', 'supplier_id'])[unit_price_col].agg(['mean', 'count']).reset_index()
                
                # Suppliers with consistently high prices
                high_price_suppliers = price_analysis[
                    (price_analysis['count'] >= 5) &  # Multiple orders
                    (price_analysis['mean'] > price_analysis['mean'].quantile(0.9))  # Top 10% prices
                ]
                
                if not high_price_suppliers.empty:
                    risk_score += 25
                    risk_factors.append(f"{len(high_price_suppliers)} supplier-item combinations with consistently high prices")
        
        # Bundle manipulation indicators
        if not self.items_data.empty:
            # Check for unusual item combinations
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            order_items = merged_data.groupby('po_id')['item_name'].count()
            large_orders = order_items[order_items > order_items.quantile(0.95)]
            
            if not large_orders.empty:
                risk_score += 20
                risk_factors.append(f"{len(large_orders)} orders with unusually large item counts")
        
        # Supplier collusion indicators
        if not self.suppliers.empty and not self.rfqs.empty:
            # Check for suppliers that never bid against each other
            supplier_bidding = self.rfqs.groupby(['rfq_id', 'supplier_id']).size().reset_index()
            rfq_supplier_counts = supplier_bidding.groupby('rfq_id')['supplier_id'].count()
            
            single_bidder_rfqs = rfq_supplier_counts[rfq_supplier_counts == 1]
            if not single_bidder_rfqs.empty:
                risk_score += 20
                risk_factors.append(f"{len(single_bidder_rfqs)} RFQs with only one bidder")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if not suspicious_rfqs.empty:
            mitigation.extend([
                "Implement enhanced bid analysis",
                "Establish bid evaluation committees",
                "Conduct supplier background checks"
            ])
        if not high_price_suppliers.empty:
            mitigation.extend([
                "Conduct market price analysis",
                "Implement price benchmarking",
                "Establish competitive bidding requirements"
            ])
        if not single_bidder_rfqs.empty:
            mitigation.extend([
                "Expand supplier base",
                "Implement mandatory competitive bidding",
                "Establish minimum bidder requirements"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring for suspicious patterns")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_market_risk(self) -> Dict:
        """Analyze market-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        # Initialize variables to avoid scope issues
        single_supplier_items = pd.DataFrame()
        high_volatility_items = pd.DataFrame()
        
        if self.suppliers.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['No supplier data available'],
                'mitigation': ['Implement market monitoring']
            }
        
        # Geographic concentration risk
        if 'country' in self.suppliers.columns:
            country_counts = self.suppliers['country'].value_counts()
            single_country_suppliers = country_counts[country_counts == 1]
            
            if len(single_country_suppliers) > 0:
                risk_score += 30
                risk_factors.append(f"{len(single_country_suppliers)} countries with single suppliers")
            
            # High concentration in specific regions
            top_country_pct = (country_counts.iloc[0] / len(self.suppliers)) * 100
            if top_country_pct > 60:
                risk_score += 25
                risk_factors.append(f"High geographic concentration: {top_country_pct:.1f}% from one country")
        
        # Supply market diversity
        if not self.items_data.empty:
            item_supplier_counts = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            if 'supplier_id' in item_supplier_counts.columns:
                item_supplier_counts = item_supplier_counts.groupby('item_name')['supplier_id'].nunique()
                
                single_supplier_items = item_supplier_counts[item_supplier_counts == 1]
                if not single_supplier_items.empty:
                    risk_score += 25
                    risk_factors.append(f"{len(single_supplier_items)} items with single suppliers")
        
        # Market volatility indicators
        if not self.purchase_orders.empty and not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            if unit_price_col in merged_data.columns:
                price_volatility = merged_data.groupby('item_name')[unit_price_col].agg(['mean', 'std']).reset_index()
                price_volatility['cv'] = price_volatility['std'] / price_volatility['mean']
                
                high_volatility_items = price_volatility[price_volatility['cv'] > 0.4]
                if not high_volatility_items.empty:
                    risk_score += 20
                    risk_factors.append(f"{len(high_volatility_items)} items with high market volatility")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if len(single_country_suppliers) > 0:
            mitigation.extend([
                "Diversify supplier geographic base",
                "Develop international supplier relationships",
                "Implement regional sourcing strategies"
            ])
        if not single_supplier_items.empty:
            mitigation.extend([
                "Identify alternative suppliers for critical items",
                "Develop strategic supplier partnerships",
                "Implement supplier development programs"
            ])
        if not high_volatility_items.empty:
            mitigation.extend([
                "Implement price hedging strategies",
                "Establish long-term supply agreements",
                "Develop inventory buffer strategies"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring market conditions")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_compliance_risk(self) -> Dict:
        """Analyze compliance-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        # Contract compliance risk
        if not self.contracts.empty:
            non_compliant_contracts = self.contracts[self.contracts['compliance_status'] != 'Compliant']
            if not non_compliant_contracts.empty:
                risk_score += 35
                risk_factors.append(f"{len(non_compliant_contracts)} contracts with compliance issues")
        
        # ESG compliance risk
        if not self.suppliers.empty and 'esg_score' in self.suppliers.columns:
            low_esg_suppliers = self.suppliers[self.suppliers['esg_score'] < 50]
            if not low_esg_suppliers.empty:
                risk_score += 25
                risk_factors.append(f"{len(low_esg_suppliers)} suppliers with low ESG scores")
        
        # Policy compliance risk
        if not self.purchase_orders.empty:
            # Check for orders without budget codes
            orders_without_budget = self.purchase_orders[self.purchase_orders['budget_code'].isna()]
            if not orders_without_budget.empty:
                risk_score += 20
                risk_factors.append(f"{len(orders_without_budget)} orders without budget codes")
        
        # Regulatory compliance indicators
        if not self.suppliers.empty:
            # Check for suppliers in high-risk categories
            if 'risk_category' in self.suppliers.columns:
                high_risk_suppliers = self.suppliers[self.suppliers['risk_category'] == 'High']
                if not high_risk_suppliers.empty:
                    risk_score += 20
                    risk_factors.append(f"{len(high_risk_suppliers)} suppliers in high-risk categories")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if not non_compliant_contracts.empty:
            mitigation.extend([
                "Review and address compliance issues",
                "Implement compliance monitoring system",
                "Establish corrective action plans"
            ])
        if not low_esg_suppliers.empty:
            mitigation.extend([
                "Implement ESG supplier development programs",
                "Establish ESG compliance requirements",
                "Conduct supplier ESG assessments"
            ])
        if not orders_without_budget.empty:
            mitigation.extend([
                "Implement mandatory budget code requirements",
                "Establish approval workflows",
                "Conduct policy compliance training"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring compliance status")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def analyze_process_risk(self) -> Dict:
        """Analyze process-related risks"""
        risk_score = 0
        risk_factors = []
        risk_level = "Low"
        
        if self.purchase_orders.empty:
            return {
                'score': 0,
                'level': 'Unknown',
                'factors': ['No purchase order data available'],
                'mitigation': ['Implement process monitoring']
            }
        
        # Process efficiency indicators
        # Small order analysis
        avg_order_value = (self.purchase_orders['quantity'] * self.purchase_orders['unit_price']).mean()
        small_orders = self.purchase_orders[
            (self.purchase_orders['quantity'] * self.purchase_orders['unit_price']) < avg_order_value * 0.1
        ]
        
        if not small_orders.empty:
            small_order_pct = (len(small_orders) / len(self.purchase_orders)) * 100
            if small_order_pct > 30:
                risk_score += 25
                risk_factors.append(f"High proportion of small orders: {small_order_pct:.1f}%")
        
        # Department efficiency analysis
        if 'department' in self.purchase_orders.columns:
            dept_efficiency = self.purchase_orders.groupby('department').agg({
                'po_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            dept_efficiency['avg_order_size'] = dept_efficiency['quantity'] / dept_efficiency['po_id']
            
            # Departments with many small orders
            small_order_depts = dept_efficiency[
                dept_efficiency['avg_order_size'] < dept_efficiency['avg_order_size'].quantile(0.25)
            ]
            
            if not small_order_depts.empty:
                risk_score += 20
                risk_factors.append(f"{len(small_order_depts)} departments with inefficient ordering patterns")
        
        # Process consistency indicators
        if 'order_date' in self.purchase_orders.columns:
            # Analyze ordering patterns
            self.purchase_orders['order_date'] = pd.to_datetime(self.purchase_orders['order_date'])
            daily_orders = self.purchase_orders.groupby(self.purchase_orders['order_date'].dt.date).size()
            
            # Check for unusual ordering patterns
            order_std = daily_orders.std()
            order_mean = daily_orders.mean()
            
            if order_std > order_mean * 2:
                risk_score += 20
                risk_factors.append("High variability in daily order volumes")
        
        # Documentation gaps
        missing_data = 0
        required_fields = ['po_id', 'supplier_id', 'item_id', 'quantity', 'unit_price']
        for field in required_fields:
            if field in self.purchase_orders.columns:
                missing_data += self.purchase_orders[field].isna().sum()
        
        if missing_data > 0:
            risk_score += 15
            risk_factors.append(f"{missing_data} missing data points in purchase orders")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Mitigation strategies
        mitigation = []
        if small_order_pct > 30:
            mitigation.extend([
                "Implement order consolidation strategies",
                "Establish minimum order value requirements",
                "Develop catalog purchasing programs"
            ])
        if not small_order_depts.empty:
            mitigation.extend([
                "Provide department-specific training",
                "Implement ordering guidelines",
                "Establish approval workflows"
            ])
        if missing_data > 0:
            mitigation.extend([
                "Implement data validation requirements",
                "Establish mandatory field requirements",
                "Conduct data quality audits"
            ])
        if not mitigation:
            mitigation.append("Continue monitoring process efficiency")
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'mitigation': mitigation
        }
    
    def generate_comprehensive_risk_report(self) -> Dict:
        """Generate comprehensive risk assessment report"""
        risk_categories = {
            'Supplier Risk': self.analyze_supplier_risk(),
            'Contractual Risk': self.analyze_contractual_risk(),
            'Pricing & Cost Risk': self.analyze_pricing_cost_risk(),
            'Delivery Risk': self.analyze_delivery_risk(),
            'Fraud/Manipulation Risk': self.analyze_fraud_manipulation_risk(),
            'Market Risk': self.analyze_market_risk(),
            'Compliance Risk': self.analyze_compliance_risk(),
            'Process Risk': self.analyze_process_risk()
        }
        
        # Calculate overall risk score
        overall_score = sum(
            risk_categories[category]['score'] * self.risk_weights[category.lower().replace(' & ', '_').replace('/', '_').replace(' ', '_')]
            for category in risk_categories.keys()
        )
        
        # Determine overall risk level
        if overall_score >= 60:
            overall_level = "High"
        elif overall_score >= 30:
            overall_level = "Medium"
        else:
            overall_level = "Low"
        
        # Identify top risks
        risk_scores = [(category, data['score']) for category, data in risk_categories.items()]
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        top_risks = risk_scores[:3]
        
        # Generate consolidated mitigation strategies
        all_mitigation = []
        for data in risk_categories.values():
            all_mitigation.extend(data['mitigation'])
        
        # Remove duplicates while preserving order
        unique_mitigation = []
        for strategy in all_mitigation:
            if strategy not in unique_mitigation:
                unique_mitigation.append(strategy)
        
        return {
            'overall_score': overall_score,
            'overall_level': overall_level,
            'risk_categories': risk_categories,
            'top_risks': top_risks,
            'consolidated_mitigation': unique_mitigation[:10]  # Top 10 strategies
        }

def display_risk_dashboard(risk_report: Dict):
    """Display comprehensive risk dashboard using Streamlit"""
    
    # Overall risk summary
    st.markdown("## 🚨 Procurement Risk Assessment Dashboard")
    
    # Risk level indicator
    risk_level = risk_report['overall_level']
    risk_score = risk_report['overall_score']
    
    if risk_level == "High":
        st.error(f"⚠️ **Overall Risk Level: {risk_level}** (Score: {risk_score:.1f})")
    elif risk_level == "Medium":
        st.warning(f"⚠️ **Overall Risk Level: {risk_level}** (Score: {risk_score:.1f})")
    else:
        st.success(f"✅ **Overall Risk Level: {risk_level}** (Score: {risk_score:.1f})")
    
    # Risk category breakdown
    st.markdown("### Risk Category Analysis")
    
    # Create DataFrame for risk categories
    risk_data = []
    for category, data in risk_report['risk_categories'].items():
        risk_data.append({
            'Risk Category': category,
            'Risk Level': data['level'],
            'Risk Score': data['score'],
            'Risk Factors': len(data['factors'])
        })
    
    df = pd.DataFrame(risk_data)
    
    # Display risk categories table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Risk Category": st.column_config.TextColumn("Risk Category", width="medium"),
            "Risk Level": st.column_config.SelectboxColumn(
                "Risk Level",
                width="small",
                options=["Low", "Medium", "High"],
                default="Low"
            ),
            "Risk Score": st.column_config.NumberColumn("Risk Score", width="small"),
            "Risk Factors": st.column_config.NumberColumn("Risk Factors", width="small")
        }
    )
    
    # Top risks section
    st.markdown("### 🔥 Top Risk Areas")
    for i, (category, score) in enumerate(risk_report['top_risks'], 1):
        risk_data = risk_report['risk_categories'][category]
        
        with st.expander(f"{i}. {category} - {risk_data['level']} Risk (Score: {score})"):
            st.markdown("**Risk Factors:**")
            for factor in risk_data['factors']:
                st.markdown(f"• {factor}")
            
            st.markdown("**Mitigation Strategies:**")
            for strategy in risk_data['mitigation']:
                st.markdown(f"• {strategy}")
    
    # Consolidated mitigation strategies
    st.markdown("### 🛡️ Recommended Mitigation Strategies")
    for i, strategy in enumerate(risk_report['consolidated_mitigation'], 1):
        st.markdown(f"{i}. {strategy}")
    
    # Risk trend analysis (placeholder for future enhancement)
    st.markdown("### 📊 Risk Trend Analysis")
    st.info("Risk trend analysis will be available in future versions with historical data.")
    
    # Risk heatmap visualization
    st.markdown("### 🗺️ Risk Heatmap")
    
    # Create a simple heatmap using risk scores
    heatmap_data = []
    for category, data in risk_report['risk_categories'].items():
        heatmap_data.append({
            'Category': category,
            'Risk Score': data['score'],
            'Risk Level': data['level']
        })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Display heatmap using st.bar_chart
    chart_data = heatmap_df.set_index('Category')['Risk Score']
    st.bar_chart(chart_data)
    
    # Risk summary metrics
    st.markdown("### 📈 Risk Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        high_risk_count = sum(1 for data in risk_report['risk_categories'].values() if data['level'] == 'High')
        st.metric("High Risk Categories", high_risk_count)
    
    with col2:
        medium_risk_count = sum(1 for data in risk_report['risk_categories'].values() if data['level'] == 'Medium')
        st.metric("Medium Risk Categories", medium_risk_count)
    
    with col3:
        low_risk_count = sum(1 for data in risk_report['risk_categories'].values() if data['level'] == 'Low')
        st.metric("Low Risk Categories", low_risk_count)
    
    with col4:
        total_factors = sum(len(data['factors']) for data in risk_report['risk_categories'].values())
        st.metric("Total Risk Factors", total_factors) 