import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

def format_ai_recommendations(recommendations_list):
    """
    Format AI recommendations with each bullet point on a separate line for better presentation.
    """
    formatted_recommendations = []
    
    for recommendation in recommendations_list:
        if recommendation.strip() == "":
            formatted_recommendations.append("")
        elif recommendation.startswith("   •"):
            # This is a bullet point - keep it as is
            formatted_recommendations.append(recommendation)
        elif recommendation.startswith("🤖") or recommendation.startswith("🎯") or recommendation.startswith("💰") or recommendation.startswith("💸") or recommendation.startswith("⚠️") or recommendation.startswith("👥") or recommendation.startswith("📦") or recommendation.startswith("🔍"):
            # This is a main heading - keep it as is
            formatted_recommendations.append(recommendation)
        elif recommendation.startswith("🟢") or recommendation.startswith("🟡") or recommendation.startswith("🟠") or recommendation.startswith("🔴") or recommendation.startswith("📈") or recommendation.startswith("📉"):
            # This is a sub-heading - keep it as is
            formatted_recommendations.append(recommendation)
        else:
            # This might be a bullet point without proper formatting - add bullet point
            if recommendation.strip() and not recommendation.startswith("**"):
                formatted_recommendations.append(f"   • {recommendation.strip()}")
            else:
                formatted_recommendations.append(recommendation)
    
    return "\n".join(formatted_recommendations)

class ProcurementInsights:
    """Auto insights generator for procurement analytics"""
    
    def __init__(self, purchase_orders, suppliers, items_data, deliveries, invoices, contracts, budgets, rfqs):
        self.purchase_orders = purchase_orders
        self.suppliers = suppliers
        self.items_data = items_data
        self.deliveries = deliveries
        self.invoices = invoices
        self.contracts = contracts
        self.budgets = budgets
        self.rfqs = rfqs
        
    def generate_spend_insights(self):
        """Generate insights for spend analysis"""
        if self.purchase_orders.empty:
            return "No purchase order data available for spend analysis."
        
        insights = []
        
        # Calculate basic metrics using purchase_orders unit_price
        total_spend = self.purchase_orders['quantity'].mul(self.purchase_orders['unit_price']).sum()
        total_orders = len(self.purchase_orders)
        avg_order_value = total_spend / total_orders if total_orders > 0 else 0
        
        # Key metrics
        insights.append(f"**Total Spend**: ${total_spend:,.0f}")
        insights.append(f"**Total Orders**: {total_orders:,}")
        insights.append(f"**Average Order Value**: ${avg_order_value:,.0f}")
        insights.append("")
        
        # Spend concentration analysis
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
            category_spend = merged_data.groupby('category')['total_spend'].sum().sort_values(ascending=False)
            
            if not category_spend.empty:
                top_category = category_spend.index[0]
                top_category_pct = (category_spend.iloc[0] / total_spend) * 100
                
                insights.append(f"**Top Spend Category**: {top_category} ({top_category_pct:.1f}%)")
                
                if top_category_pct > 50:
                    insights.append("**Risk Level**: High concentration - diversification recommended")
                elif top_category_pct > 30:
                    insights.append("**Risk Level**: Moderate concentration - monitor closely")
                else:
                    insights.append("**Risk Level**: Well-diversified spend")
        
        # Supplier concentration
        if not self.suppliers.empty:
            supplier_spend = self.purchase_orders.merge(self.suppliers, on='supplier_id', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in supplier_spend.columns else 'unit_price_x'
            supplier_spend['total_spend'] = supplier_spend['quantity'] * supplier_spend[unit_price_col]
            top_suppliers = supplier_spend.groupby('supplier_name')['total_spend'].sum().sort_values(ascending=False)
            
            if not top_suppliers.empty:
                top_supplier = top_suppliers.index[0]
                top_supplier_pct = (top_suppliers.iloc[0] / total_spend) * 100
                
                insights.append(f"**Top Supplier**: {top_supplier} ({top_supplier_pct:.1f}%)")
                
                if top_supplier_pct > 40:
                    insights.append("**Supplier Risk**: High dependence - develop alternatives")
                elif top_supplier_pct > 25:
                    insights.append("**Supplier Risk**: Moderate concentration - strategic sourcing needed")
        
        # Budget analysis
        if not self.budgets.empty:
            budget_analysis = self.purchase_orders.merge(self.budgets, on='budget_code', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in budget_analysis.columns else 'unit_price_x'
            budget_analysis['total_spend'] = budget_analysis['quantity'] * budget_analysis[unit_price_col]
            budget_utilization = budget_analysis.groupby('budget_code').agg({
                'amount': 'first',  # Use 'amount' instead of 'budget_amount' based on the schema
                'total_spend': 'sum'
            }).reset_index()
            budget_utilization['utilization_rate'] = (budget_utilization['total_spend'] / budget_utilization['amount']) * 100
            
            over_budget = budget_utilization[budget_utilization['utilization_rate'] > 100]
            under_budget = budget_utilization[budget_utilization['utilization_rate'] < 80]
            
            if not over_budget.empty:
                insights.append(f"**Budget Issues**: {len(over_budget)} codes exceeded budget")
            if not under_budget.empty:
                insights.append(f"**Budget Opportunities**: {len(under_budget)} codes under-utilized")
        
        # Add strategic recommendations
        insights.append("")
        insights.append("Strategic Actions:")
        
        # Initialize variables for recommendations
        top_category_pct = 0
        top_supplier_pct = 0
        
        # Calculate category percentage for recommendations
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
            category_spend = merged_data.groupby('category')['total_spend'].sum().sort_values(ascending=False)
            if not category_spend.empty:
                top_category_pct = (category_spend.iloc[0] / total_spend) * 100
        
        # Calculate supplier percentage for recommendations
        if not self.suppliers.empty:
            supplier_spend = self.purchase_orders.merge(self.suppliers, on='supplier_id', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in supplier_spend.columns else 'unit_price_x'
            supplier_spend['total_spend'] = supplier_spend['quantity'] * supplier_spend[unit_price_col]
            top_suppliers = supplier_spend.groupby('supplier_name')['total_spend'].sum().sort_values(ascending=False)
            if not top_suppliers.empty:
                top_supplier_pct = (top_suppliers.iloc[0] / total_spend) * 100
        
        if top_category_pct > 50:
            insights.append("• Implement category diversification strategy")
            insights.append("• Develop alternative supplier relationships")
            insights.append("• Establish risk mitigation protocols")
        elif top_category_pct > 30:
            insights.append("• Develop category management strategies")
            insights.append("• Explore volume consolidation opportunities")
            insights.append("• Implement strategic sourcing initiatives")
        
        if top_supplier_pct > 40:
            insights.append("• Develop backup supplier relationships")
            insights.append("• Implement supplier diversification program")
            insights.append("• Negotiate better terms and conditions")
        elif top_supplier_pct > 25:
            insights.append("• Monitor supplier concentration closely")
            insights.append("• Develop strategic supplier partnerships")
            insights.append("• Implement supplier performance management")
        
        return "\n".join(insights) if insights else "No significant spend insights identified."
    
    def generate_supplier_performance_insights(self):
        """Generate insights for supplier performance"""
        if self.purchase_orders.empty or self.deliveries.empty:
            return "Insufficient data for supplier performance analysis."
        
        insights = []
        
        # On-time delivery analysis
        delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
        delivery_analysis = delivery_analysis.merge(self.suppliers, on='supplier_id', how='left')
        
        # Calculate on-time delivery rate
        if 'delivery_date_actual' in delivery_analysis.columns and 'delivery_date' in delivery_analysis.columns:
            delivery_analysis['on_time'] = pd.to_datetime(delivery_analysis['delivery_date_actual']) <= pd.to_datetime(delivery_analysis['delivery_date'])
        else:
            delivery_analysis['on_time'] = True
        
        otif_rate = delivery_analysis['on_time'].mean() * 100 if not delivery_analysis.empty else 0
        
        # Key performance metrics
        insights.append(f"{otif_rate:.1f}%")
        
        if otif_rate < 85:
            insights.append("**Performance Status**: Below industry standard")
        elif otif_rate < 95:
            insights.append("**Performance Status**: Good, with room for improvement")
        else:
            insights.append("**Performance Status**: Excellent performance")
        
        # Quality metrics
        total_defects = delivery_analysis['defect_flag'].sum()
        total_deliveries = len(delivery_analysis)
        defect_rate = (total_defects / total_deliveries) * 100 if total_deliveries > 0 else 0
        
        insights.append(f"{defect_rate:.1f}% ({total_defects} defects)")
        
        if defect_rate > 5:
            insights.append("**Quality Alert**: Above acceptable threshold")
        
        # Supplier-specific analysis
        supplier_performance = delivery_analysis.groupby('supplier_name').agg({
            'on_time': 'mean',
            'defect_flag': 'sum',
            'po_id': 'count'
        }).reset_index()
        supplier_performance.columns = ['supplier_name', 'otif_rate', 'defect_count', 'order_count']
        supplier_performance['otif_rate'] = supplier_performance['otif_rate'] * 100
        
        # Identify problematic suppliers
        poor_performers = supplier_performance[
            (supplier_performance['otif_rate'] < 80) & 
            (supplier_performance['order_count'] >= 5)
        ]
        
        if not poor_performers.empty:
            worst_supplier = poor_performers.loc[poor_performers['otif_rate'].idxmin()]
            insights.append(f"**Performance Alert**: {worst_supplier['supplier_name']} ({worst_supplier['otif_rate']:.1f}% on-time)")
        
        # Add strategic recommendations
        insights.append("")
        insights.append("Strategic Actions:")
        
        if otif_rate < 85:
            insights.append("• Implement supplier performance improvement program")
            insights.append("• Establish delivery performance targets")
            insights.append("• Develop supplier development initiatives")
        elif otif_rate < 95:
            insights.append("• Monitor supplier performance closely")
            insights.append("• Implement continuous improvement programs")
            insights.append("• Establish performance incentives")
        
        if defect_rate > 5:
            insights.append("• Implement quality control measures")
            insights.append("• Establish supplier quality standards")
            insights.append("• Develop quality improvement programs")
        
        if not poor_performers.empty:
            insights.append("• Address underperforming suppliers")
            insights.append("• Implement corrective action plans")
            insights.append("• Consider supplier replacement strategies")
        
        return "\n".join(insights) if insights else "No significant supplier performance insights identified."
    
    def generate_cost_savings_insights(self):
        """Generate insights for cost savings opportunities"""
        if self.purchase_orders.empty:
            return "No purchase order data available for cost savings analysis."
        
        insights = []
        
        # Unit cost analysis
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            # Handle potential column renaming after merge
            unit_price_col = 'unit_price' if 'unit_price' in merged_data.columns else 'unit_price_x'
            merged_data['total_spend'] = merged_data['quantity'] * merged_data[unit_price_col]
            
            # Identify high-cost items
            item_costs = merged_data.groupby(['item_name', 'category']).agg({
                unit_price_col: 'mean',
                'total_spend': 'sum',
                'quantity': 'sum'
            }).reset_index()
            
            # Find items with highest unit costs
            high_cost_items = item_costs.nlargest(5, unit_price_col)
            if not high_cost_items.empty:
                top_cost_item = high_cost_items.iloc[0]
                insights.append(f"💸 **High-Cost Item**: {top_cost_item['item_name']} has average unit cost of ${top_cost_item[unit_price_col]:.2f}")
                insights.append(f"📊 **Spend Impact**: ${top_cost_item['total_spend']:,.0f} spent on this item")
        
        # RFQ analysis for negotiation opportunities
        if not self.rfqs.empty:
            rfq_analysis = self.rfqs.groupby(['supplier_id', 'item_id'])['unit_price'].agg(['count', 'mean', 'std']).reset_index()
            rfq_analysis = rfq_analysis.merge(self.suppliers, on='supplier_id', how='left')
            rfq_analysis = rfq_analysis.merge(self.items_data, on='item_id', how='left')
            
            # Items with multiple quotes
            competitive_items = rfq_analysis[rfq_analysis['count'] >= 3]
            if not competitive_items.empty:
                price_variance = competitive_items['std'] / competitive_items['mean']
                high_variance = competitive_items[price_variance > 0.2]
                
                if not high_variance.empty:
                    insights.append(f"💡 **Negotiation Opportunity**: {len(high_variance)} items show >20% price variance across suppliers")
                    insights.append("🎯 **Action**: Leverage competitive quotes for better pricing")
        
        # Volume consolidation opportunities
        supplier_volume = self.purchase_orders.groupby('supplier_id').agg({
            'quantity': 'sum',
            'unit_price': 'mean'
        }).reset_index()
        supplier_volume = supplier_volume.merge(self.suppliers, on='supplier_id', how='left')
        
        # Identify suppliers with high volume but high prices
        high_volume_high_cost = supplier_volume[
            (supplier_volume['quantity'] > supplier_volume['quantity'].quantile(0.75)) &
            (supplier_volume['unit_price'] > supplier_volume['unit_price'].quantile(0.75))
        ]
        
        if not high_volume_high_cost.empty:
            insights.append(f"📈 **Volume Leverage**: {len(high_volume_high_cost)} suppliers with high volume and high costs")
            insights.append("💼 **Strategy**: Negotiate volume discounts or explore alternative suppliers")
        
        return "\n\n".join(insights) if insights else "No significant cost savings opportunities identified."
    
    def generate_process_efficiency_insights(self):
        """Generate insights for process efficiency"""
        if self.purchase_orders.empty or self.deliveries.empty:
            return "Insufficient data for process efficiency analysis."
        
        insights = []
        
        # Lead time analysis
        delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
        if 'delivery_date_actual' in delivery_analysis.columns:
            delivery_analysis['lead_time'] = (pd.to_datetime(delivery_analysis['delivery_date_actual']) - 
                                            pd.to_datetime(delivery_analysis['order_date'])).dt.days
        else:
            delivery_analysis['lead_time'] = 0  # Default if we can't calculate
        
        avg_lead_time = delivery_analysis['lead_time'].mean()
        lead_time_std = delivery_analysis['lead_time'].std()
        
        insights.append(f"⏱️ **Average Lead Time**: {avg_lead_time:.1f} days")
        insights.append(f"📊 **Lead Time Variability**: {lead_time_std:.1f} days standard deviation")
        
        if lead_time_std > avg_lead_time * 0.5:
            insights.append("🔄 **Process Inconsistency**: High lead time variability indicates process inefficiencies")
        
        # Cycle time analysis
        if not self.invoices.empty:
            invoice_analysis = self.purchase_orders.merge(self.invoices, on='po_id', how='left')
            invoice_analysis['payment_cycle'] = (pd.to_datetime(invoice_analysis['payment_date']) - 
                                               pd.to_datetime(invoice_analysis['invoice_date'])).dt.days
            
            avg_payment_cycle = invoice_analysis['payment_cycle'].mean()
            insights.append(f"💳 **Payment Cycle**: {avg_payment_cycle:.1f} days average")
            
            if avg_payment_cycle > 30:
                insights.append("💰 **Cash Flow Impact**: Extended payment cycles affecting working capital")
        
        # Department efficiency
        if 'department' in self.purchase_orders.columns and 'quantity' in self.purchase_orders.columns:
            try:
                dept_efficiency = self.purchase_orders.groupby('department').agg({
                    'po_id': 'count',
                    'quantity': 'sum'
                }).reset_index()
                dept_efficiency['avg_order_size'] = dept_efficiency['quantity'] / dept_efficiency['po_id']
                
                # Identify departments with many small orders
                small_order_depts = dept_efficiency[dept_efficiency['avg_order_size'] < dept_efficiency['avg_order_size'].quantile(0.25)]
                if not small_order_depts.empty:
                    insights.append(f"📋 **Process Optimization**: {len(small_order_depts)} departments with small average order sizes")
                    insights.append("🎯 **Recommendation**: Consider order consolidation to reduce processing overhead")
            except Exception as e:
                insights.append(f"⚠️ **Data Issue**: Unable to analyze department efficiency: {str(e)}")
        
        return "\n\n".join(insights) if insights else "No significant process efficiency insights identified."
    
    def generate_compliance_risk_insights(self):
        """Generate insights for compliance and risk management"""
        insights = []
        
        # Contract compliance
        if not self.contracts.empty:
            active_contracts = self.contracts[
                (pd.to_datetime(self.contracts['end_date']) >= datetime.now()) &
                (self.contracts['compliance_status'] != 'Compliant')
            ]
            
            if not active_contracts.empty:
                insights.append(f"⚠️ **Contract Compliance**: {len(active_contracts)} active contracts with compliance issues")
            
            # Contract renewal analysis
            expiring_contracts = self.contracts[
                pd.to_datetime(self.contracts['end_date']) <= (datetime.now() + timedelta(days=90))
            ]
            
            if not expiring_contracts.empty:
                total_value = expiring_contracts['contract_value'].sum()
                insights.append(f"📅 **Contract Renewals**: {len(expiring_contracts)} contracts expiring in 90 days")
                insights.append(f"💰 **Value at Risk**: ${total_value:,.0f} in expiring contracts")
        
        # Supplier risk assessment
        if not self.suppliers.empty:
            # Geographic risk
            country_counts = self.suppliers['country'].value_counts()
            single_country_suppliers = country_counts[country_counts == 1]
            
            if len(single_country_suppliers) > 0:
                insights.append(f"🌍 **Geographic Risk**: {len(single_country_suppliers)} countries with single suppliers")
            
            # ESG risk
            if 'esg_score' in self.suppliers.columns:
                low_esg_suppliers = self.suppliers[self.suppliers['esg_score'] < 50]
                if not low_esg_suppliers.empty:
                    insights.append(f"🌱 **ESG Risk**: {len(low_esg_suppliers)} suppliers with ESG scores below 50")
        
        # Policy compliance
        if not self.purchase_orders.empty:
            # Check for orders without budget codes
            orders_without_budget = self.purchase_orders[self.purchase_orders['budget_code'].isna()]
            if not orders_without_budget.empty:
                insights.append(f"📋 **Policy Violation**: {len(orders_without_budget)} orders without budget codes")
        
        return "\n\n".join(insights) if insights else "No significant compliance or risk issues identified."
    
    def generate_sustainability_insights(self):
        """Generate insights for sustainability and CSR"""
        insights = []
        
        if self.suppliers.empty or self.items_data.empty:
            return "Insufficient data for sustainability analysis."
        
        # ESG performance
        if 'esg_score' in self.suppliers.columns:
            avg_esg_score = self.suppliers['esg_score'].mean()
            insights.append(f"🌱 **Average ESG Score**: {avg_esg_score:.1f}/100")
            
            if avg_esg_score < 60:
                insights.append("🟡 **Sustainability Opportunity**: Below-average ESG performance - consider supplier development programs")
        
        # Green procurement
        if 'recyclable_flag' in self.items_data.columns:
            recyclable_items = self.items_data[self.items_data['recyclable_flag'] == 'Yes']
            recyclable_pct = (len(recyclable_items) / len(self.items_data)) * 100
            
            insights.append(f"♻️ **Green Procurement**: {recyclable_pct:.1f}% of items are recyclable")
            
            if recyclable_pct < 30:
                insights.append("🌿 **Sustainability Goal**: Increase recyclable item procurement to meet sustainability targets")
        
        # Carbon footprint
        if 'carbon_score' in self.items_data.columns:
            carbon_analysis = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            carbon_analysis['total_carbon'] = carbon_analysis['quantity'] * carbon_analysis['carbon_score']
            total_carbon = carbon_analysis['total_carbon'].sum()
            
            insights.append(f"🌍 **Carbon Footprint**: {total_carbon:,.0f} total carbon units")
            
            # Identify high-carbon items
            high_carbon_items = carbon_analysis.groupby('item_name')['total_carbon'].sum().nlargest(3)
            if not high_carbon_items.empty:
                insights.append(f"🔥 **High Carbon Items**: Top 3 items contribute {high_carbon_items.sum():,.0f} carbon units")
        
        # Diversity suppliers
        if 'diversity_flag' in self.suppliers.columns:
            diverse_suppliers = self.suppliers[self.suppliers['diversity_flag'] == 'Yes']
            diverse_pct = (len(diverse_suppliers) / len(self.suppliers)) * 100
            
            insights.append(f"🤝 **Supplier Diversity**: {diverse_pct:.1f}% of suppliers are diverse-owned")
            
            if diverse_pct < 20:
                insights.append("📈 **Diversity Goal**: Increase diverse supplier representation to meet inclusion targets")
        
        return "\n\n".join(insights) if insights else "No significant sustainability insights identified."
    
    def generate_executive_summary(self):
        """Generate a comprehensive executive summary with clean formatting"""
        if self.purchase_orders.empty:
            return "Insufficient data for executive summary."
        
        # Calculate key metrics
        total_spend = self.purchase_orders['quantity'].mul(self.purchase_orders['unit_price']).sum()
        total_orders = len(self.purchase_orders)
        avg_order_value = total_spend / total_orders if total_orders > 0 else 0
        
        # Build structured summary
        summary = []
        
        # 1. Executive Overview
        summary.append("## Executive Overview")
        summary.append(f"**Total Spend**: ${total_spend:,.0f}")
        summary.append(f"**Total Orders**: {total_orders:,}")
        summary.append(f"**Average Order Value**: ${avg_order_value:,.0f}")
        summary.append("")
        
        # 2. Key Performance Indicators
        summary.append("## Key Performance Indicators")
        
        # Spend concentration
        if not self.items_data.empty:
            merged_data = self.purchase_orders.merge(self.items_data, on='item_id', how='left')
            # Use unit_price from purchase_orders, fallback to items_data if needed
            if 'unit_price' in merged_data.columns:
                merged_data['total_spend'] = merged_data['quantity'] * merged_data['unit_price']
            else:
                merged_data['total_spend'] = merged_data['quantity'] * merged_data.get('unit_price_y', 0)
            category_spend = merged_data.groupby('category')['total_spend'].sum().sort_values(ascending=False)
            
            if not category_spend.empty:
                top_category = category_spend.index[0]
                top_category_pct = (category_spend.iloc[0] / total_spend) * 100
                summary.append(f"**Top Spend Category**: {top_category} ({top_category_pct:.1f}%)")
        
        # Initialize variables
        otif_rate = 0
        avg_utilization = 0
        top_category_pct = 0
        top_supplier_pct = 0
        
        # Supplier performance
        if not self.deliveries.empty:
            delivery_analysis = self.purchase_orders.merge(self.deliveries, on='po_id', how='left')
            if 'delivery_date_actual' in delivery_analysis.columns and 'delivery_date' in delivery_analysis.columns:
                delivery_analysis['on_time'] = pd.to_datetime(delivery_analysis['delivery_date_actual']) <= pd.to_datetime(delivery_analysis['delivery_date'])
                otif_rate = delivery_analysis['on_time'].mean() * 100
                summary.append(f"**On-Time Delivery Rate**: {otif_rate:.1f}%")
        
        # Budget utilization
        if not self.budgets.empty:
            budget_analysis = self.purchase_orders.merge(self.budgets, on='budget_code', how='left')
            # Use unit_price from purchase_orders
            budget_analysis['total_spend'] = budget_analysis['quantity'] * budget_analysis['unit_price']
            budget_utilization = budget_analysis.groupby('budget_code').agg({
                'amount': 'first',
                'total_spend': 'sum'
            }).reset_index()
            budget_utilization['utilization_rate'] = (budget_utilization['total_spend'] / budget_utilization['amount']) * 100
            avg_utilization = budget_utilization['utilization_rate'].mean()
            summary.append(f"**Average Budget Utilization**: {avg_utilization:.1f}%")
        
        summary.append("")
        
        # 3. Risk Assessment
        summary.append("## Risk Assessment")
        
        # High spend concentration risk
        if not self.items_data.empty:
            if top_category_pct > 50:
                summary.append("**High Risk**: Spend concentration in single category")
            elif top_category_pct > 30:
                summary.append("**Medium Risk**: Moderate spend concentration")
            else:
                summary.append("**Low Risk**: Well-diversified spend")
        
        # Supplier concentration risk
        if not self.suppliers.empty:
            supplier_spend = self.purchase_orders.merge(self.suppliers, on='supplier_id', how='left')
            # Use unit_price from purchase_orders
            supplier_spend['total_spend'] = supplier_spend['quantity'] * supplier_spend['unit_price']
            top_suppliers = supplier_spend.groupby('supplier_name')['total_spend'].sum().sort_values(ascending=False)
            
            if not top_suppliers.empty:
                top_supplier_pct = (top_suppliers.iloc[0] / total_spend) * 100
                if top_supplier_pct > 40:
                    summary.append("**High Risk**: Over-dependence on single supplier")
                elif top_supplier_pct > 25:
                    summary.append("**Medium Risk**: Significant supplier concentration")
        
        # Contract compliance risk
        if not self.contracts.empty:
            active_contracts = self.contracts[
                (pd.to_datetime(self.contracts['end_date']) >= datetime.now()) &
                (self.contracts['compliance_status'] != 'Compliant')
            ]
            if not active_contracts.empty:
                summary.append(f"**Compliance Risk**: {len(active_contracts)} contracts with issues")
        
        summary.append("")
        
        # 4. Strategic Recommendations
        summary.append("## Strategic Recommendations")
        
        recommendations = []
        
        # Spend optimization
        if top_category_pct > 30:
            recommendations.append("Develop category strategies for high-spend areas")
            recommendations.append("Implement strategic sourcing initiatives")
            recommendations.append("Explore volume consolidation opportunities")
        
        # Supplier optimization
        if top_supplier_pct > 25:
            recommendations.append("Implement supplier diversification strategy")
            recommendations.append("Develop backup supplier relationships")
            recommendations.append("Negotiate better terms with key suppliers")
        
        # Process improvement
        if otif_rate < 95:
            recommendations.append("Improve supplier delivery performance")
            recommendations.append("Implement supplier scorecard system")
            recommendations.append("Establish performance improvement programs")
        
        # Budget management
        if avg_utilization > 90:
            recommendations.append("Review budget allocation and forecasting")
            recommendations.append("Implement budget optimization strategies")
            recommendations.append("Develop cost control measures")
        
        # Additional strategic actions
        if not self.contracts.empty:
            recommendations.append("Review and optimize contract terms")
            recommendations.append("Implement contract lifecycle management")
        
        if not self.items_data.empty:
            recommendations.append("Standardize procurement categories")
            recommendations.append("Implement e-procurement solutions")
        
        # Always include these strategic actions
        recommendations.append("Establish procurement analytics dashboard")
        recommendations.append("Implement automated spend analysis")
        recommendations.append("Develop supplier relationship management program")
        
        if recommendations:
            formatted_recommendations = format_ai_recommendations(recommendations)
            summary.append(formatted_recommendations)
        else:
            summary.append("No immediate actions required - procurement operations are well-optimized")
        
        return "\n".join(summary)

def display_insights_section(insights_text, title, icon="💡"):
    """Display insights in a clean, professional table format matching HR system"""
    import pandas as pd
    import streamlit as st
    
    # For executive summary, use special formatting
    if "## Executive Overview" in insights_text:
        display_executive_summary(insights_text, title, icon)
    else:
        # Convert insights to table format using Streamlit components
        display_insights_table(insights_text, title, icon)

def display_insights_table(insights_text, title, icon):
    """Display insights using professional table format matching HR system"""
    import pandas as pd
    import streamlit as st
    
    # Parse the insights text
    lines = insights_text.split('\n')
    insights_data = []
    strategic_actions = []
    in_strategic_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if we're entering strategic actions section
        if line.lower() == "strategic actions:":
            in_strategic_section = True
            continue
            
        # Handle strategic actions
        if in_strategic_section and line.startswith('•'):
            strategic_actions.append(line[1:].strip())
            continue
        elif in_strategic_section:
            in_strategic_section = False
            
        # Remove ** formatting but keep the content
        line = line.replace('**', '')
        
        # Extract metric and value
        if ':' in line:
            parts = line.split(':', 1)
            metric = parts[0].strip()
            value = parts[1].strip()
            
            # Determine status/alert based on content
            status = "Normal"
            if any(word in line.lower() for word in ['risk', 'alert', 'issue', 'high', 'above', 'critical', 'concerning']):
                status = "Alert"
            elif any(word in line.lower() for word in ['opportunity', 'good', 'excellent', 'low']):
                status = "Opportunity"
            elif any(word in line.lower() for word in ['moderate', 'medium']):
                status = "Monitor"
            elif any(word in line.lower() for word in ['data not available', 'error', 'unknown']):
                status = "No Data"
            
            insights_data.append({
                'metric': metric,
                'value': value,
                'status': status
            })
    
    if not insights_data:
        st.info(f"No insights available for {title}")
        return
    
    # Create professional styled container matching HR system
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; 
                padding: 24px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h3 style="color: #1f2937; margin: 0 0 20px 0; font-size: 1.25rem; font-weight: 600; 
                   border-bottom: 2px solid #667eea; padding-bottom: 8px;">
            {icon} {title}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create DataFrame for table display
    df_data = []
    for insight in insights_data:
        df_data.append({
            'Metric': insight['metric'],
            'Value': insight['value'],
            'Status': insight['status']
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table with custom styling matching HR system
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="medium"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                width="small",
                options=["Normal", "Alert", "Monitor", "Opportunity", "No Data"],
                default="Normal"
            )
        }
    )
    
    # Display strategic actions if available
    if strategic_actions:
        st.markdown("### Strategic Actions")
        for action in strategic_actions:
            st.markdown(f"• {action}")

def display_executive_summary(insights_text, title, icon):
    """Display executive summary with professional table format matching HR system"""
    import pandas as pd
    import streamlit as st
    
    # Create professional styled container matching HR system
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; 
                padding: 24px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h3 style="color: #1f2937; margin: 0 0 20px 0; font-size: 1.25rem; font-weight: 600; 
                   border-bottom: 2px solid #667eea; padding-bottom: 8px;">
            {icon} {title}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Parse the insights text
    lines = insights_text.split('\n')
    insights_data = []
    strategic_actions = []
    in_strategic_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if we're entering strategic actions section
        if line.lower() == "strategic actions:":
            in_strategic_section = True
            continue
            
        # Handle strategic actions
        if in_strategic_section and line.startswith('•'):
            strategic_actions.append(line[1:].strip())
            continue
        elif in_strategic_section:
            in_strategic_section = False
            
        # Remove ** formatting but keep the content
        line = line.replace('**', '')
        
        # Extract metric and value
        if ':' in line:
            parts = line.split(':', 1)
            metric = parts[0].strip()
            value = parts[1].strip()
            
            # Determine status/alert based on content
            status = "Normal"
            if any(word in line.lower() for word in ['risk', 'alert', 'issue', 'high', 'above', 'critical', 'concerning']):
                status = "Alert"
            elif any(word in line.lower() for word in ['opportunity', 'good', 'excellent', 'low']):
                status = "Opportunity"
            elif any(word in line.lower() for word in ['moderate', 'medium']):
                status = "Monitor"
            elif any(word in line.lower() for word in ['data not available', 'error', 'unknown']):
                status = "No Data"
            
            insights_data.append({
                'metric': metric,
                'value': value,
                'status': status
            })
    
    if not insights_data:
        st.info(f"No executive summary data available")
        return
    
    # Create DataFrame for table display
    df_data = []
    for insight in insights_data:
        df_data.append({
            'Metric': insight['metric'],
            'Value': insight['value'],
            'Status': insight['status']
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table with custom styling matching HR system
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="medium"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                width="small",
                options=["Normal", "Alert", "Monitor", "Opportunity", "No Data"],
                default="Normal"
            )
        }
    )
    
    # Display strategic actions if available
    if strategic_actions:
        st.markdown("### Strategic Actions")
        for action in strategic_actions:
            st.markdown(f"• {action}")

def get_section_icon(section_title):
    """Get appropriate icon for section title"""
    section_lower = section_title.lower()
    
    if 'spend' in section_lower:
        return "💰"
    elif 'supplier' in section_lower:
        return "🏭"
    elif 'cost' in section_lower:
        return "💡"
    elif 'process' in section_lower:
        return "⚡"
    elif 'risk' in section_lower or 'compliance' in section_lower:
        return "⚠️"
    elif 'sustainability' in section_lower or 'csr' in section_lower:
        return "🌱"
    else:
        return "📊"

def clean_insights_text(text):
    """Clean and format insights text for display"""
    # Remove extra whitespace and normalize line breaks
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines) 