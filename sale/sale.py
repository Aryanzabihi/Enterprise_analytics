import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import io
import base64
import random
from datetime import timedelta

# Import sales metric calculation functions
from sales_metrics_calculator import *

# ============================================================================
# AI Recommendation Functions
# ============================================================================

def generate_ai_recommendations(data_type, data, insights=None):
    """Generate AI-powered recommendations based on data analysis."""
    
    if data.empty:
        return "📊 **No data available** - Please load data to receive AI recommendations."
    
    recommendations = []
    
    if data_type == "sales_performance":
        recommendations = generate_sales_performance_recommendations(data, insights)
    elif data_type == "customer_analysis":
        recommendations = generate_customer_analysis_recommendations(data, insights)
    elif data_type == "sales_funnel":
        recommendations = generate_sales_funnel_recommendations(data, insights)
    elif data_type == "sales_team":
        recommendations = generate_sales_team_recommendations(data, insights)
    elif data_type == "pricing_discounts":
        recommendations = generate_pricing_recommendations(data, insights)
    elif data_type == "market_analysis":
        recommendations = generate_market_analysis_recommendations(data, insights)
    elif data_type == "forecasting":
        recommendations = generate_forecasting_recommendations(data, insights)
    elif data_type == "crm_analysis":
        recommendations = generate_crm_recommendations(data, insights)
    elif data_type == "operational_efficiency":
        recommendations = generate_operational_recommendations(data, insights)
    elif data_type == "specialized_metrics":
        recommendations = generate_specialized_recommendations(data, insights)
    elif data_type == "strategic_analytics":
        recommendations = generate_strategic_recommendations(data, insights)
    
    return recommendations

def generate_sales_performance_recommendations(data, insights=None):
    """Generate AI recommendations for sales performance."""
    recommendations = []
    
    if 'total_amount' in data.columns:
        total_revenue = data['total_amount'].sum()
        avg_order_value = data['total_amount'].mean()
        
        if total_revenue < 100000:
            recommendations.append("🚀 **Revenue Growth Opportunity**: Consider implementing upselling strategies and cross-selling campaigns to increase average order value.")
        
        if avg_order_value < 500:
            recommendations.append("💰 **AOV Optimization**: Focus on bundling products and offering premium services to increase average order value.")
    
    if 'order_date' in data.columns:
        data['order_date'] = pd.to_datetime(data['order_date'])
        recent_orders = data[data['order_date'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
        
        if len(recent_orders) < len(data) * 0.3:
            recommendations.append("📅 **Seasonal Strategy**: Recent order volume suggests implementing seasonal marketing campaigns to boost sales.")
    
    if 'channel' in data.columns:
        channel_performance = data.groupby('channel')['total_amount'].sum()
        best_channel = channel_performance.idxmax()
        
        recommendations.append(f"🎯 **Channel Optimization**: {best_channel} is your highest-performing channel. Consider allocating more resources and budget to this channel.")
    
    if not recommendations:
        recommendations.append("📈 **Data Analysis**: Continue monitoring key metrics and implement A/B testing for different sales strategies.")
    
    return recommendations

def generate_customer_analysis_recommendations(data, insights=None):
    """Generate AI recommendations for customer analysis."""
    recommendations = []
    
    if 'customer_segment' in data.columns:
        segment_counts = data['customer_segment'].value_counts()
        largest_segment = segment_counts.idxmax()
        
        recommendations.append(f"👥 **Segment Focus**: {largest_segment} customers represent your largest segment. Develop targeted strategies for this group.")
    
    if 'acquisition_date' in data.columns:
        data['acquisition_date'] = pd.to_datetime(data['acquisition_date'])
        recent_acquisitions = data[data['acquisition_date'] >= pd.Timestamp.now() - pd.Timedelta(days=90)]
        
        if len(recent_acquisitions) < len(data) * 0.2:
            recommendations.append("🆕 **Customer Acquisition**: Recent customer acquisition is low. Consider implementing lead generation campaigns and referral programs.")
    
    if 'status' in data.columns:
        churned_customers = data[data['status'] == 'Churned']
        churn_rate = len(churned_customers) / len(data)
        
        if churn_rate > 0.1:
            recommendations.append("⚠️ **Churn Prevention**: Customer churn rate is high. Implement customer success programs and proactive retention strategies.")
    
    if 'industry' in data.columns:
        industry_performance = data.groupby('industry').size()
        top_industry = industry_performance.idxmax()
        
        recommendations.append(f"🏭 **Industry Focus**: {top_industry} industry shows strong performance. Consider expanding your presence in this sector.")
    
    if not recommendations:
        recommendations.append("🔍 **Customer Insights**: Implement customer feedback surveys and satisfaction metrics to better understand customer needs.")
    
    return recommendations

def generate_sales_funnel_recommendations(data, insights=None):
    """Generate AI recommendations for sales funnel analysis."""
    recommendations = []
    
    if 'status' in data.columns:
        status_counts = data['status'].value_counts()
        
        if 'New' in status_counts and status_counts['New'] > status_counts.get('Qualified', 0):
            recommendations.append("🔄 **Lead Qualification**: High number of new leads suggests implementing better lead scoring and qualification processes.")
        
        if 'Closed Won' in status_counts and 'Closed Lost' in status_counts:
            win_rate = status_counts['Closed Won'] / (status_counts['Closed Won'] + status_counts['Closed Lost'])
            if win_rate < 0.3:
                recommendations.append("🎯 **Win Rate Improvement**: Low conversion rate suggests reviewing sales process and providing better sales training.")
    
    if 'source' in data.columns:
        source_performance = data.groupby('source')['status'].apply(lambda x: (x == 'Closed Won').sum())
        best_source = source_performance.idxmax()
        
        recommendations.append(f"📊 **Source Optimization**: {best_source} generates the most closed deals. Increase investment in this lead source.")
    
    if 'value' in data.columns:
        avg_deal_value = data['value'].mean()
        if avg_deal_value < 10000:
            recommendations.append("💎 **Deal Sizing**: Focus on larger deals and enterprise customers to increase average deal value.")
    
    if not recommendations:
        recommendations.append("📈 **Funnel Optimization**: Implement lead nurturing campaigns and improve sales process efficiency.")
    
    return recommendations

def generate_sales_team_recommendations(data, insights=None):
    """Generate AI recommendations for sales team analysis."""
    recommendations = []
    
    if 'quota' in data.columns and 'sales_rep_id' in data.columns:
        # This would need sales performance data to be meaningful
        recommendations.append("🎯 **Performance Management**: Implement regular performance reviews and provide targeted coaching based on individual performance metrics.")
    
    if 'region' in data.columns:
        region_counts = data['region'].value_counts()
        if len(region_counts) > 1:
            recommendations.append("🌍 **Territory Optimization**: Consider redistributing sales resources based on regional performance and market potential.")
    
    if 'hire_date' in data.columns:
        data['hire_date'] = pd.to_datetime(data['hire_date'])
        recent_hires = data[data['hire_date'] >= pd.Timestamp.now() - pd.Timedelta(days=365)]
        
        if len(recent_hires) > len(data) * 0.3:
            recommendations.append("👨‍💼 **Training Focus**: High number of recent hires suggests implementing comprehensive onboarding and training programs.")
    
    if 'status' in data.columns:
        active_reps = data[data['status'] == 'Active']
        if len(active_reps) < len(data) * 0.8:
            recommendations.append("⚠️ **Retention Strategy**: Focus on sales rep retention through competitive compensation and career development opportunities.")
    
    if not recommendations:
        recommendations.append("🚀 **Team Development**: Invest in sales training, tools, and motivation programs to improve team performance.")
    
    return recommendations

def generate_pricing_recommendations(data, insights=None):
    """Generate AI recommendations for pricing and discounts."""
    recommendations = []
    
    if 'unit_price' in data.columns and 'cost_price' in data.columns:
        data['margin'] = data['unit_price'] - data['cost_price']
        avg_margin = data['margin'].mean()
        margin_rate = (avg_margin / data['unit_price'].mean()) * 100
        
        if margin_rate < 30:
            recommendations.append("💵 **Margin Improvement**: Current margins are low. Consider price optimization and cost reduction strategies.")
        
        if margin_rate > 70:
            recommendations.append("💰 **Competitive Pricing**: High margins may indicate pricing power. Consider market expansion and premium positioning.")
    
    if 'quantity' in data.columns and 'total_amount' in data.columns:
        data['avg_price'] = data['total_amount'] / data['quantity']
        price_variance = data['avg_price'].std()
        
        if price_variance > data['avg_price'].mean() * 0.3:
            recommendations.append("📊 **Price Consistency**: High price variance suggests implementing standardized pricing policies and discount guidelines.")
    
    recommendations.append("🎯 **Dynamic Pricing**: Consider implementing dynamic pricing strategies based on demand, seasonality, and customer segments.")
    recommendations.append("🏷️ **Bundle Pricing**: Create product bundles and packages to increase average order value and customer satisfaction.")
    
    return recommendations

def generate_market_analysis_recommendations(data, insights=None):
    """Generate AI recommendations for market analysis."""
    recommendations = []
    
    if 'region' in data.columns:
        region_performance = data.groupby('region')['total_amount'].sum()
        top_region = region_performance.idxmax()
        bottom_region = region_performance.idxmin()
        
        recommendations.append(f"🌍 **Market Focus**: {top_region} shows strong performance. Consider expanding operations and increasing market share in this region.")
        recommendations.append(f"📈 **Growth Opportunity**: {bottom_region} has growth potential. Develop targeted strategies to improve performance in this market.")
    
    if 'industry' in data.columns:
        industry_trends = data.groupby('industry')['total_amount'].sum()
        emerging_industry = industry_trends.nsmallest(3).index[0]
        
        recommendations.append(f"🚀 **Emerging Markets**: {emerging_industry} shows growth potential. Consider early market entry and strategic partnerships.")
    
    if 'order_date' in data.columns:
        data['order_date'] = pd.to_datetime(data['order_date'])
        data['month'] = data['order_date'].dt.month
        seasonal_patterns = data.groupby('month')['total_amount'].sum()
        
        if seasonal_patterns.std() > seasonal_patterns.mean() * 0.5:
            recommendations.append("📅 **Seasonal Strategy**: Strong seasonal patterns detected. Implement seasonal marketing campaigns and inventory planning.")
    
    recommendations.append("🔍 **Competitive Analysis**: Conduct regular competitive analysis to identify market opportunities and threats.")
    recommendations.append("📊 **Market Research**: Invest in market research to understand customer needs and market trends.")
    
    return recommendations

def generate_forecasting_recommendations(data, insights=None):
    """Generate AI recommendations for forecasting."""
    recommendations = []
    
    if 'order_date' in data.columns:
        data['order_date'] = pd.to_datetime(data['order_date'])
        data['month'] = data['order_date'].dt.month
        monthly_trends = data.groupby('month')['total_amount'].sum()
        
        if monthly_trends.iloc[-1] > monthly_trends.iloc[0]:
            recommendations.append("📈 **Growth Trend**: Positive growth trend detected. Plan for capacity expansion and resource allocation.")
        else:
            recommendations.append("⚠️ **Declining Trend**: Declining trend detected. Review business strategy and implement corrective measures.")
    
    if 'total_amount' in data.columns:
        revenue_volatility = data['total_amount'].std() / data['total_amount'].mean()
        
        if revenue_volatility > 0.5:
            recommendations.append("📊 **Forecast Accuracy**: High revenue volatility suggests implementing more sophisticated forecasting models and scenario planning.")
    
    recommendations.append("🔮 **Predictive Analytics**: Implement machine learning models for more accurate sales forecasting.")
    recommendations.append("📋 **Scenario Planning**: Develop multiple forecast scenarios for better risk management and strategic planning.")
    recommendations.append("🔄 **Continuous Monitoring**: Regularly update forecasts based on new data and market conditions.")
    
    return recommendations

def generate_crm_recommendations(data, insights=None):
    """Generate AI recommendations for CRM analysis."""
    recommendations = []
    
    if 'activity_type' in data.columns:
        activity_counts = data['activity_type'].value_counts()
        most_common = activity_counts.index[0]
        
        recommendations.append(f"📞 **Activity Optimization**: {most_common} is the most common activity. Ensure this activity type is optimized for maximum effectiveness.")
    
    if 'outcome' in data.columns:
        outcome_counts = data['outcome'].value_counts()
        if 'Negative' in outcome_counts and outcome_counts['Negative'] > len(data) * 0.2:
            recommendations.append("⚠️ **Process Improvement**: High negative outcomes suggest reviewing and improving sales processes and training.")
    
    if 'duration_minutes' in data.columns:
        avg_duration = data['duration_minutes'].mean()
        if avg_duration < 30:
            recommendations.append("⏱️ **Quality Focus**: Short activity duration may indicate rushed interactions. Focus on quality over quantity.")
    
    recommendations.append("📱 **CRM Integration**: Ensure full integration between CRM system and sales activities for better tracking and analysis.")
    recommendations.append("🎯 **Lead Scoring**: Implement automated lead scoring to prioritize high-value prospects.")
    recommendations.append("📊 **Performance Metrics**: Track key CRM metrics like response time, follow-up rates, and conversion rates.")
    
    return recommendations

def generate_operational_recommendations(data, insights=None):
    """Generate AI recommendations for operational efficiency."""
    recommendations = []
    
    if 'order_date' in data.columns and 'total_amount' in data.columns:
        data['order_date'] = pd.to_datetime(data['order_date'])
        data['processing_time'] = pd.Timestamp.now() - data['order_date']
        avg_processing_time = data['processing_time'].mean()
        
        if avg_processing_time.days > 7:
            recommendations.append("⚡ **Process Speed**: Long processing times detected. Streamline order processing and implement automation.")
    
    if 'channel' in data.columns:
        channel_efficiency = data.groupby('channel')['total_amount'].sum()
        if len(channel_efficiency) > 3:
            recommendations.append("🎯 **Channel Consolidation**: Multiple channels may increase complexity. Consider consolidating to most efficient channels.")
    
    recommendations.append("🔄 **Process Automation**: Implement automation for repetitive tasks to improve efficiency and reduce errors.")
    recommendations.append("📊 **KPI Monitoring**: Establish key performance indicators and regular monitoring for continuous improvement.")
    recommendations.append("👥 **Team Training**: Regular training on processes and tools to maintain high operational standards.")
    
    return recommendations

def generate_specialized_recommendations(data, insights=None):
    """Generate AI recommendations for specialized metrics."""
    recommendations = []
    
    recommendations.append("🎯 **Custom Metrics**: Develop custom KPIs specific to your business model and industry.")
    recommendations.append("📊 **Benchmarking**: Compare your metrics with industry benchmarks to identify improvement opportunities.")
    recommendations.append("🔍 **Deep Analysis**: Conduct root cause analysis for underperforming metrics.")
    recommendations.append("📈 **Trend Analysis**: Monitor metric trends over time to identify patterns and opportunities.")
    
    return recommendations

def generate_strategic_recommendations(data, insights=None):
    """Generate AI recommendations for strategic analytics."""
    recommendations = []
    
    if 'total_amount' in data.columns:
        total_revenue = data['total_amount'].sum()
        if total_revenue < 1000000:
            recommendations.append("🚀 **Growth Strategy**: Focus on market expansion and customer acquisition for revenue growth.")
        else:
            recommendations.append("💎 **Market Leadership**: Strong revenue position. Focus on market share expansion and competitive positioning.")
    
    recommendations.append("🎯 **Strategic Planning**: Develop long-term strategic plans based on data-driven insights.")
    recommendations.append("🌍 **Market Expansion**: Identify new markets and customer segments for growth opportunities.")
    recommendations.append("🤝 **Partnership Strategy**: Consider strategic partnerships and alliances for market expansion.")
    recommendations.append("📊 **Investment Planning**: Allocate resources based on data-driven ROI analysis.")
    
    return recommendations

def display_ai_recommendations(data_type, data, insights=None):
    """Display AI recommendations in a styled card."""
    recommendations = generate_ai_recommendations(data_type, data, insights)
    
    st.markdown("---")
    st.markdown("""
    <div class="metric-card-purple">
    <h3>🤖 AI-Powered Recommendations</h3>
    <p>Intelligent insights and actionable strategies based on your data analysis:</p>
    </div>
    """, unsafe_allow_html=True)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")
    
    st.markdown("""
    <div class="metric-card">
    <p><em>💡 These recommendations are generated using AI analysis of your sales data patterns, trends, and performance metrics.</em></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# Main Analytics Functions
# ============================================================================

def display_formatted_recommendations(recommendations_text):
    """
    Display recommendations with proper formatting using HTML to ensure bullet points are on separate lines.
    """
    if not recommendations_text:
        return
    
    # Convert markdown text to HTML format
    html_content = recommendations_text.replace('\n', '<br>')
    
    # Replace bullet points with proper HTML list items
    lines = recommendations_text.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            html_lines.append("<br>")
        elif line.startswith("- "):
            # Convert bullet point to HTML list item
            content = line[2:].strip()
            html_lines.append(f"<li>{content}</li>")
        elif line.startswith("💡") or line.startswith("🎯") or line.startswith("⚠️"):
            # This is a heading, add it as a header
            html_lines.append(f"<h4>{line}</h4>")
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

def display_dataframe_with_index_1(df, **kwargs):
    """Display dataframe with index starting from 1"""
    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        return st.dataframe(df_display, **kwargs)
    else:
        return st.dataframe(df, **kwargs)

def create_template_for_download():
    """Create an Excel template with all required sales data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct sales schema
    customers_template = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'email', 'phone', 'company', 'industry', 
        'region', 'country', 'customer_segment', 'acquisition_date', 'status'
    ])
    
    products_template = pd.DataFrame(columns=[
        'product_id', 'product_name', 'category', 'subcategory', 'unit_price', 
        'cost_price', 'supplier_id', 'launch_date', 'status'
    ])
    
    sales_orders_template = pd.DataFrame(columns=[
        'order_id', 'customer_id', 'order_date', 'product_id', 'quantity', 
        'unit_price', 'total_amount', 'sales_rep_id', 'region', 'channel'
    ])
    
    sales_reps_template = pd.DataFrame(columns=[
        'sales_rep_id', 'first_name', 'last_name', 'email', 'region', 'territory', 
        'hire_date', 'quota', 'manager_id', 'status'
    ])
    
    leads_template = pd.DataFrame(columns=[
        'lead_id', 'lead_name', 'email', 'company', 'industry', 'source', 
        'created_date', 'status', 'assigned_rep_id', 'value'
    ])
    
    opportunities_template = pd.DataFrame(columns=[
        'opportunity_id', 'lead_id', 'customer_id', 'product_id', 'value', 
        'stage', 'created_date', 'close_date', 'probability', 'sales_rep_id'
    ])
    
    activities_template = pd.DataFrame(columns=[
        'activity_id', 'sales_rep_id', 'customer_id', 'activity_type', 'date', 
        'duration_minutes', 'notes', 'outcome'
    ])
    
    targets_template = pd.DataFrame(columns=[
        'target_id', 'sales_rep_id', 'period', 'target_amount', 'target_date', 
        'category', 'status'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        customers_template.to_excel(writer, sheet_name='Customers', index=False)
        products_template.to_excel(writer, sheet_name='Products', index=False)
        sales_orders_template.to_excel(writer, sheet_name='Sales_Orders', index=False)
        sales_reps_template.to_excel(writer, sheet_name='Sales_Reps', index=False)
        leads_template.to_excel(writer, sheet_name='Leads', index=False)
        opportunities_template.to_excel(writer, sheet_name='Opportunities', index=False)
        activities_template.to_excel(writer, sheet_name='Activities', index=False)
        targets_template.to_excel(writer, sheet_name='Targets', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Customers', 'Products', 'Sales_Orders', 'Sales_Reps', 'Leads', 'Opportunities', 'Activities', 'Targets'],
            'Required Fields': [
                'customer_id, customer_name, email, phone, company, industry, region, country, customer_segment, acquisition_date, status',
                'product_id, product_name, category, subcategory, unit_price, cost_price, supplier_id, launch_date, status',
                'order_id, customer_id, order_date, product_id, quantity, unit_price, total_amount, sales_rep_id, region, channel',
                'sales_rep_id, first_name, last_name, email, region, territory, hire_date, quota, manager_id, status',
                'lead_id, lead_name, email, company, industry, source, created_date, status, assigned_rep_id, value',
                'opportunity_id, lead_id, customer_id, product_id, value, stage, created_date, close_date, probability, sales_rep_id',
                'activity_id, sales_rep_id, customer_id, activity_type, date, duration_minutes, notes, outcome',
                'target_id, sales_rep_id, period, target_amount, target_date, category, status'
            ],
            'Data Types': [
                'Text, Text, Text, Text, Text, Text, Text, Text, Text, Date, Text',
                'Text, Text, Text, Text, Number, Number, Text, Date, Text',
                'Text, Text, Date, Text, Number, Number, Number, Text, Text, Text',
                'Text, Text, Text, Text, Text, Text, Date, Number, Text, Text',
                'Text, Text, Text, Text, Text, Text, Date, Text, Text, Number',
                'Text, Text, Text, Text, Number, Text, Date, Date, Number, Text',
                'Text, Text, Text, Text, Date, Number, Text, Text',
                'Text, Text, Text, Number, Date, Text, Text'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
    
    # Prepare for download
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    
    # Create download link
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="sales_data_template.xlsx">📥 Download Sales Data Template</a>'
    st.markdown(href, unsafe_allow_html=True)

def export_data_to_excel():
    """Exports all sales data from session state to a single Excel file."""
    with pd.ExcelWriter('sales_data_export.xlsx', engine='xlsxwriter') as writer:
        if not st.session_state.customers.empty:
            st.session_state.customers.to_excel(writer, sheet_name='Customers', index=False)
        if not st.session_state.products.empty:
            st.session_state.products.to_excel(writer, sheet_name='Products', index=False)
        if not st.session_state.sales_orders.empty:
            st.session_state.sales_orders.to_excel(writer, sheet_name='Sales_Orders', index=False)
        if not st.session_state.sales_reps.empty:
            st.session_state.sales_reps.to_excel(writer, sheet_name='Sales_Reps', index=False)
        if not st.session_state.leads.empty:
            st.session_state.leads.to_excel(writer, sheet_name='Leads', index=False)
        if not st.session_state.opportunities.empty:
            st.session_state.opportunities.to_excel(writer, sheet_name='Opportunities', index=False)
        if not st.session_state.activities.empty:
            st.session_state.activities.to_excel(writer, sheet_name='Activities', index=False)
        if not st.session_state.targets.empty:
            st.session_state.targets.to_excel(writer, sheet_name='Targets', index=False)
        
        st.success("Sales data exported successfully as 'sales_data_export.xlsx'")

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Initialize session state for sales data storage
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'email', 'phone', 'company', 'industry', 
        'region', 'country', 'customer_segment', 'acquisition_date', 'status'
    ])

if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame(columns=[
        'product_id', 'product_name', 'category', 'subcategory', 'unit_price', 
        'cost_price', 'supplier_id', 'launch_date', 'status'
    ])

if 'sales_orders' not in st.session_state:
    st.session_state.sales_orders = pd.DataFrame(columns=[
        'order_id', 'customer_id', 'order_date', 'product_id', 'quantity', 
        'unit_price', 'total_amount', 'sales_rep_id', 'region', 'channel'
    ])

if 'sales_reps' not in st.session_state:
    st.session_state.sales_reps = pd.DataFrame(columns=[
        'sales_rep_id', 'first_name', 'last_name', 'email', 'region', 'territory', 
        'hire_date', 'quota', 'manager_id', 'status'
    ])

if 'leads' not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=[
        'lead_id', 'lead_name', 'email', 'company', 'industry', 'source', 
        'created_date', 'status', 'assigned_rep_id', 'value'
    ])

if 'opportunities' not in st.session_state:
    st.session_state.opportunities = pd.DataFrame(columns=[
        'opportunity_id', 'lead_id', 'customer_id', 'product_id', 'value', 
        'stage', 'created_date', 'close_date', 'probability', 'sales_rep_id'
    ])

if 'activities' not in st.session_state:
    st.session_state.activities = pd.DataFrame(columns=[
        'activity_id', 'sales_rep_id', 'customer_id', 'activity_type', 'date', 
        'duration_minutes', 'notes', 'outcome'
    ])

if 'targets' not in st.session_state:
    st.session_state.targets = pd.DataFrame(columns=[
        'target_id', 'sales_rep_id', 'period', 'target_amount', 'target_date', 
        'category', 'status'
    ])

def main():
    # Load custom CSS
    load_custom_css()
    
    st.markdown('<h1 class="main-header">💰 Sales Analytics Dashboard</h1>', unsafe_allow_html=True)
    
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
        
        if st.button("📝 Data Input", key="nav_data_input", use_container_width=True):
            st.session_state.current_page = "📝 Data Input"
        
        if st.button("📊 Sales Performance", key="nav_sales_performance", use_container_width=True):
            st.session_state.current_page = "📊 Sales Performance"
        
        if st.button("👥 Customer Analysis", key="nav_customer_analysis", use_container_width=True):
            st.session_state.current_page = "👥 Customer Analysis"
        
        if st.button("🔄 Sales Funnel", key="nav_sales_funnel", use_container_width=True):
            st.session_state.current_page = "🔄 Sales Funnel"
        
        if st.button("👨‍💼 Sales Team", key="nav_sales_team", use_container_width=True):
            st.session_state.current_page = "👨‍💼 Sales Team"
        
        if st.button("💰 Pricing & Discounts", key="nav_pricing_discounts", use_container_width=True):
            st.session_state.current_page = "💰 Pricing & Discounts"
        
        if st.button("🌍 Market Analysis", key="nav_market_analysis", use_container_width=True):
            st.session_state.current_page = "🌍 Market Analysis"
        
        if st.button("📈 Forecasting", key="nav_forecasting", use_container_width=True):
            st.session_state.current_page = "📈 Forecasting"
        
        if st.button("📋 CRM Analysis", key="nav_crm_analysis", use_container_width=True):
            st.session_state.current_page = "📋 CRM Analysis"
        
        if st.button("⚡ Operational Efficiency", key="nav_operational_efficiency", use_container_width=True):
            st.session_state.current_page = "⚡ Operational Efficiency"
        
        if st.button("🎯 Specialized Metrics", key="nav_specialized_metrics", use_container_width=True):
            st.session_state.current_page = "🎯 Specialized Metrics"
        
        if st.button("📊 Strategic Analytics", key="nav_strategic_analytics", use_container_width=True):
            st.session_state.current_page = "📊 Strategic Analytics"
        
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
    

    
    # Main content area based on sidebar selection
    if page == "🏠 Home":
        show_home()
    elif page == "📝 Data Input":
        show_data_input()
    elif page == "📊 Sales Performance":
        show_sales_performance()
    elif page == "👥 Customer Analysis":
        show_customer_analysis()
    elif page == "🔄 Sales Funnel":
        show_sales_funnel()
    elif page == "👨‍💼 Sales Team":
        show_sales_team()
    elif page == "💰 Pricing & Discounts":
        show_pricing_discounts()
    elif page == "🌍 Market Analysis":
        show_market_analysis()
    elif page == "📈 Forecasting":
        show_forecasting()
    elif page == "📋 CRM Analysis":
        show_crm_analysis()
    elif page == "⚡ Operational Efficiency":
        show_operational_efficiency()
    elif page == "🎯 Specialized Metrics":
        show_specialized_metrics()
    elif page == "📊 Strategic Analytics":
        show_strategic_analytics()

def show_home():
    st.markdown("""
    <div class="welcome-section">
    <h2>Welcome to the Sales Analytics Dashboard</h2>
    
    <p>This comprehensive tool helps you calculate and analyze key sales metrics across multiple categories:</p>
    
    <h3>📊 Available Sales Analytics Categories:</h3>
    
    <h4>1. 📊 Sales Performance Analysis</h4>
    <ul>
        <li>Sales Revenue by Product/Service</li>
        <li>Revenue Growth Rate</li>
        <li>Sales by Region/Market</li>
        <li>Sales by Channel</li>
        <li>Sales Target Achievement</li>
        <li>Top/Low-Performing Products</li>
    </ul>
    
    <h4>2. 👥 Customer Analysis</h4>
    <ul>
        <li>Customer Lifetime Value (CLV)</li>
        <li>Customer Acquisition Cost (CAC)</li>
        <li>Customer Churn Rate</li>
        <li>Repeat Purchase Rate</li>
        <li>Customer Segmentation</li>
        <li>Net Promoter Score (NPS)</li>
    </ul>
    
    <h4>3. 🔄 Sales Funnel Analysis</h4>
    <ul>
        <li>Conversion Rate by Funnel Stage</li>
        <li>Average Deal Size</li>
        <li>Time to Close</li>
        <li>Lead-to-Customer Ratio</li>
        <li>Pipeline Velocity</li>
    </ul>
    
    <h4>4. 👨‍💼 Sales Team Performance</h4>
    <ul>
        <li>Individual Sales Performance</li>
        <li>Team Target Achievement</li>
        <li>Sales Call Success Rate</li>
        <li>Win Rate</li>
        <li>Sales Productivity Metrics</li>
    </ul>
    
    <h4>5. 💰 Pricing and Discount Analysis</h4>
    <ul>
        <li>Average Selling Price (ASP)</li>
        <li>Discount Impact Analysis</li>
        <li>Price Sensitivity Analysis</li>
        <li>Profit Margin Analysis</li>
    </ul>
    
    <h4>6. 🌍 Market and Competitor Analysis</h4>
    <ul>
        <li>Market Share Analysis</li>
        <li>Competitor Pricing Analysis</li>
        <li>Demand Forecasting</li>
        <li>Market Penetration Rate</li>
    </ul>
    
    <h4>7. 📈 Sales Forecasting and Planning</h4>
    <ul>
        <li>Revenue Forecasting</li>
        <li>Sales Goal Setting</li>
        <li>Seasonality Analysis</li>
        <li>Sales Opportunity Scoring</li>
    </ul>
    
    <h4>8. 📋 Customer Relationship Management (CRM) Analysis</h4>
    <ul>
        <li>Active Accounts</li>
        <li>Dormant Accounts</li>
        <li>Upselling and Cross-Selling Performance</li>
        <li>Customer Feedback Trends</li>
    </ul>
    
    <h4>9. ⚡ Operational Sales Efficiency</h4>
    <ul>
        <li>Sales Expense Ratio</li>
        <li>Revenue per Salesperson</li>
        <li>Cost of Sales (CoS)</li>
        <li>Quota Attainment Rate</li>
    </ul>
    
    <h4>10. 🎯 Specialized Sales Metrics</h4>
    <ul>
        <li>New vs. Returning Customers</li>
        <li>Lost Opportunities Analysis</li>
        <li>Territory Performance</li>
        <li>Product Return Rate</li>
    </ul>
    
    <h3>🚀 Getting Started:</h3>
    
    <ol>
        <li><strong>Data Input:</strong> Start by entering your sales data in the "Data Input" tab</li>
        <li><strong>Calculate Metrics:</strong> Use the main tabs to view specific metric categories</li>
        <li><strong>Real-time Analysis:</strong> All metrics update automatically based on your data</li>
    </ol>
    
    <h3>📈 Data Schema:</h3>
    
    <p>The application supports the following sales data tables:</p>
    <ul>
        <li>Customers (demographics, segments, acquisition)</li>
        <li>Products (catalog, pricing, categories)</li>
        <li>Sales Orders (transactions, revenue, channels)</li>
        <li>Sales Representatives (performance, territories, quotas)</li>
        <li>Leads (prospects, sources, status)</li>
        <li>Opportunities (pipeline, stages, values)</li>
        <li>Activities (calls, meetings, outcomes)</li>
        <li>Targets (quotas, goals, achievements)</li>
    </ul>
    
    <hr>
    
    <p><strong>Note:</strong> All calculations are performed automatically based on your input data. Make sure to enter complete and accurate data for the most reliable metrics.</p>
    </div>
    """, unsafe_allow_html=True)

def show_data_input():
    """Show data input forms and file upload options"""
    st.markdown("## 📝 Data Input")
    
    # Create tabs for different data input methods
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Data Uploading", 
        "📝 Manual Data Entry", 
        "📋 Template", 
        "📊 Sample Dataset"
    ])
    
    with tab1:
        st.markdown("### 📤 Data Uploading")
        st.markdown("Upload your Excel file with all sales data tables:")
        
        # File upload for Excel template
        uploaded_file = st.file_uploader(
            "Upload Excel file with all sales tables", 
            type=['xlsx', 'xls'],
            help="Upload the filled Excel template with all 8 sales tables in separate sheets"
        )
        
        if uploaded_file is not None:
            try:
                # Read all sheets from the Excel file
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                
                # Check if all required sheets are present
                required_sheets = ['Customers', 'Products', 'Sales_Orders', 'Sales_Reps', 'Leads', 'Opportunities', 'Activities', 'Targets']
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
                
                if missing_sheets:
                    st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                    st.info("Please ensure your Excel file contains all 8 required sales sheets.")
                else:
                    # Load data into session state
                    st.session_state.customers = excel_data['Customers']
                    st.session_state.products = excel_data['Products']
                    st.session_state.sales_orders = excel_data['Sales_Orders']
                    st.session_state.sales_reps = excel_data['Sales_Reps']
                    st.session_state.leads = excel_data['Leads']
                    st.session_state.opportunities = excel_data['Opportunities']
                    st.session_state.activities = excel_data['Activities']
                    st.session_state.targets = excel_data['Targets']
                    
                    st.success("✅ All sales data loaded successfully from Excel file!")
                    st.info(f"📊 Loaded {len(st.session_state.customers)} customers, {len(st.session_state.products)} products, {len(st.session_state.sales_orders)} orders, and more...")
                    
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.info("Please ensure the file is a valid Excel file with the correct format.")
        
        # Data validation summary
        if not st.session_state.sales_orders.empty:
            st.markdown("---")
            st.markdown("#### 📊 Data Validation Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", f"{len(st.session_state.sales_orders):,}")
            with col2:
                st.metric("Total Revenue", f"${st.session_state.sales_orders['total_amount'].sum():,.2f}")
            with col3:
                st.metric("Unique Customers", f"{st.session_state.sales_orders['customer_id'].nunique():,}")
    
    with tab2:
        st.markdown("### 📝 Manual Data Entry")
        st.markdown("Add data manually using the forms below:")
        
        # Tabs for different data types
        data_tab1, data_tab2, data_tab3, data_tab4, data_tab5, data_tab6, data_tab7, data_tab8 = st.tabs([
            "Customers", "Products", "Sales Orders", "Sales Reps", 
            "Leads", "Opportunities", "Activities", "Targets"
        ])
        
        with data_tab1:
            st.subheader("Customers")
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID", key="customer_id_input")
                customer_name = st.text_input("Customer Name", key="customer_name_input")
                email = st.text_input("Email", key="customer_email_input")
                phone = st.text_input("Phone", key="customer_phone_input")
                company = st.text_input("Company", key="customer_company_input")
                industry = st.text_input("Industry", key="customer_industry_input")
            
            with col2:
                region = st.text_input("Region", key="customer_region_input")
                country = st.text_input("Country", key="customer_country_input")
                customer_segment = st.selectbox("Customer Segment", ["Enterprise", "SMB", "Startup", "Individual"], key="customer_segment_input")
                acquisition_date = st.date_input("Acquisition Date", key="customer_acquisition_date_input")
                status = st.selectbox("Status", ["Active", "Inactive", "Churned"], key="customer_status_input")
            
            if st.button("Add Customer"):
                new_customer = pd.DataFrame([{
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'email': email,
                    'phone': phone,
                    'company': company,
                    'industry': industry,
                    'region': region,
                    'country': country,
                    'customer_segment': customer_segment,
                    'acquisition_date': acquisition_date,
                    'status': status
                }])
                st.session_state.customers = pd.concat([st.session_state.customers, new_customer], ignore_index=True)
                st.success("Customer added successfully!")
            
            # Display existing data
            if not st.session_state.customers.empty:
                st.subheader("Existing Customers")
                display_dataframe_with_index_1(st.session_state.customers)
        
        with data_tab2:
            st.subheader("Products")
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.text_input("Product ID", key="product_id_input")
                product_name = st.text_input("Product Name", key="product_name_input")
                category = st.text_input("Category", key="product_category_input")
                subcategory = st.text_input("Subcategory", key="product_subcategory_input")
                unit_price = st.number_input("Unit Price", min_value=0.0, key="product_unit_price_input")
            
            with col2:
                cost_price = st.number_input("Cost Price", min_value=0.0, key="product_cost_price_input")
                supplier_id = st.text_input("Supplier ID", key="product_supplier_id_input")
                launch_date = st.date_input("Launch Date", key="product_launch_date_input")
                status = st.selectbox("Status", ["Active", "Discontinued", "Coming Soon"], key="product_status_input")
            
            if st.button("Add Product"):
                new_product = pd.DataFrame([{
                    'product_id': product_id,
                    'product_name': product_name,
                    'category': category,
                    'subcategory': subcategory,
                    'unit_price': unit_price,
                    'cost_price': cost_price,
                    'supplier_id': supplier_id,
                    'launch_date': launch_date,
                    'status': status
                }])
                st.session_state.products = pd.concat([st.session_state.products, new_product], ignore_index=True)
                st.success("Product added successfully!")
            
            # Display existing data
            if not st.session_state.products.empty:
                st.subheader("Existing Products")
                display_dataframe_with_index_1(st.session_state.products)
        
        with data_tab3:
            st.subheader("Sales Orders")
            col1, col2 = st.columns(2)
            
            with col1:
                order_id = st.text_input("Order ID", key="order_id_input")
                customer_id = st.text_input("Customer ID", key="order_customer_id_input")
                order_date = st.date_input("Order Date", key="order_date_input")
                product_id = st.text_input("Product ID", key="order_product_id_input")
                quantity = st.number_input("Quantity", min_value=1, key="order_quantity_input")
            
            with col2:
                unit_price = st.number_input("Unit Price", min_value=0.0, key="order_unit_price_input")
                total_amount = st.number_input("Total Amount", min_value=0.0, key="order_total_amount_input")
                sales_rep_id = st.text_input("Sales Rep ID", key="order_sales_rep_id_input")
                region = st.text_input("Region", key="order_region_input")
                channel = st.selectbox("Channel", ["Online", "In-Store", "Phone", "Partner"], key="order_channel_input")
            
            if st.button("Add Sales Order"):
                new_order = pd.DataFrame([{
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'order_date': order_date,
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_amount': total_amount,
                    'sales_rep_id': sales_rep_id,
                    'region': region,
                    'channel': channel
                }])
                st.session_state.sales_orders = pd.concat([st.session_state.sales_orders, new_order], ignore_index=True)
                st.success("Sales order added successfully!")
            
            # Display existing data
            if not st.session_state.sales_orders.empty:
                st.subheader("Existing Sales Orders")
                display_dataframe_with_index_1(st.session_state.sales_orders)
        
        with data_tab4:
            st.subheader("Sales Representatives")
            col1, col2 = st.columns(2)
            
            with col1:
                sales_rep_id = st.text_input("Sales Rep ID", key="sales_rep_id_input")
                first_name = st.text_input("First Name", key="sales_rep_first_name_input")
                last_name = st.text_input("Last Name", key="sales_rep_last_name_input")
                email = st.text_input("Email", key="sales_rep_email_input")
                region = st.text_input("Region", key="sales_rep_region_input")
            
            with col2:
                territory = st.text_input("Territory", key="sales_rep_territory_input")
                hire_date = st.date_input("Hire Date", key="sales_rep_hire_date_input")
                quota = st.number_input("Quota", min_value=0.0, key="sales_rep_quota_input")
                manager_id = st.text_input("Manager ID", key="sales_rep_manager_id_input")
                status = st.selectbox("Status", ["Active", "Inactive", "Terminated"], key="sales_rep_status_input")
            
            if st.button("Add Sales Representative"):
                new_rep = pd.DataFrame([{
                    'sales_rep_id': sales_rep_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'region': region,
                    'territory': territory,
                    'hire_date': hire_date,
                    'quota': quota,
                    'manager_id': manager_id,
                    'status': status
                }])
                st.session_state.sales_reps = pd.concat([st.session_state.sales_reps, new_rep], ignore_index=True)
                st.success("Sales representative added successfully!")
            
            # Display existing data
            if not st.session_state.sales_reps.empty:
                st.subheader("Existing Sales Representatives")
                display_dataframe_with_index_1(st.session_state.sales_reps)
        
        with data_tab5:
            st.subheader("Leads")
            col1, col2 = st.columns(2)
            
            with col1:
                lead_id = st.text_input("Lead ID", key="lead_id_input")
                lead_name = st.text_input("Lead Name", key="lead_name_input")
                email = st.text_input("Email", key="lead_email_input")
                company = st.text_input("Company", key="lead_company_input")
                industry = st.text_input("Industry", key="lead_industry_input")
            
            with col2:
                source = st.selectbox("Source", ["Website", "Referral", "Cold Call", "Trade Show", "Social Media"], key="lead_source_input")
                created_date = st.date_input("Created Date", key="lead_created_date_input")
                status = st.selectbox("Status", ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"], key="lead_status_input")
                assigned_rep_id = st.text_input("Assigned Rep ID", key="lead_assigned_rep_id_input")
                value = st.number_input("Value", min_value=0.0, key="lead_value_input")
            
            if st.button("Add Lead"):
                new_lead = pd.DataFrame([{
                    'lead_id': lead_id,
                    'lead_name': lead_name,
                    'email': email,
                    'company': company,
                    'industry': industry,
                    'source': source,
                    'created_date': created_date,
                    'status': status,
                    'assigned_rep_id': assigned_rep_id,
                    'value': value
                }])
                st.session_state.leads = pd.concat([st.session_state.leads, new_lead], ignore_index=True)
                st.success("Lead added successfully!")
            
            # Display existing data
            if not st.session_state.leads.empty:
                st.subheader("Existing Leads")
                display_dataframe_with_index_1(st.session_state.leads)
        
        with data_tab6:
            st.subheader("Opportunities")
            col1, col2 = st.columns(2)
            
            with col1:
                opportunity_id = st.text_input("Opportunity ID", key="opportunity_id_input")
                lead_id = st.text_input("Lead ID", key="opportunity_lead_id_input")
                customer_id = st.text_input("Customer ID", key="opportunity_customer_id_input")
                product_id = st.text_input("Product ID", key="opportunity_product_id_input")
                value = st.number_input("Value", min_value=0.0, key="opportunity_value_input")
            
            with col2:
                stage = st.selectbox("Stage", ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"], key="opportunity_stage_input")
                created_date = st.date_input("Created Date", key="opportunity_created_date_input")
                close_date = st.date_input("Close Date", key="opportunity_close_date_input")
                probability = st.number_input("Probability (%)", min_value=0, max_value=100, key="opportunity_probability_input")
                sales_rep_id = st.text_input("Sales Rep ID", key="opportunity_sales_rep_id_input")
            
            if st.button("Add Opportunity"):
                new_opportunity = pd.DataFrame([{
                    'opportunity_id': opportunity_id,
                    'lead_id': lead_id,
                    'customer_id': customer_id,
                    'product_id': product_id,
                    'value': value,
                    'stage': stage,
                    'created_date': created_date,
                    'close_date': close_date,
                    'probability': probability,
                    'sales_rep_id': sales_rep_id
                }])
                st.session_state.opportunities = pd.concat([st.session_state.opportunities, new_opportunity], ignore_index=True)
                st.success("Opportunity added successfully!")
            
            # Display existing data
            if not st.session_state.opportunities.empty:
                st.subheader("Existing Opportunities")
                display_dataframe_with_index_1(st.session_state.opportunities)
        
        with data_tab7:
            st.subheader("Activities")
            col1, col2 = st.columns(2)
            
            with col1:
                activity_id = st.text_input("Activity ID", key="activity_id_input")
                sales_rep_id = st.text_input("Sales Rep ID", key="activity_sales_rep_id_input")
                customer_id = st.text_input("Customer ID", key="activity_customer_id_input")
                activity_type = st.selectbox("Activity Type", ["Call", "Meeting", "Email", "Demo", "Proposal"], key="activity_type_input")
                date = st.date_input("Date", key="activity_date_input")
            
            with col2:
                duration_minutes = st.number_input("Duration (Minutes)", min_value=0, key="activity_duration_input")
                notes = st.text_area("Notes", key="activity_notes_input")
                outcome = st.selectbox("Outcome", ["Positive", "Neutral", "Negative", "Follow-up Required"], key="activity_outcome_input")
            
            if st.button("Add Activity"):
                new_activity = pd.DataFrame([{
                    'activity_id': activity_id,
                    'sales_rep_id': sales_rep_id,
                    'customer_id': customer_id,
                    'activity_type': activity_type,
                    'date': date,
                    'duration_minutes': duration_minutes,
                    'notes': notes,
                    'outcome': outcome
                }])
                st.session_state.activities = pd.concat([st.session_state.activities, new_activity], ignore_index=True)
                st.success("Activity added successfully!")
            
            # Display existing data
            if not st.session_state.activities.empty:
                st.subheader("Existing Activities")
                display_dataframe_with_index_1(st.session_state.activities)
        
        with data_tab8:
            st.subheader("Targets")
            col1, col2 = st.columns(2)
            
            with col1:
                target_id = st.text_input("Target ID", key="target_id_input")
                sales_rep_id = st.text_input("Sales Rep ID", key="target_sales_rep_id_input")
                period = st.text_input("Period", key="target_period_input")
                target_amount = st.number_input("Target Amount", min_value=0.0, key="target_amount_input")
            
            with col2:
                target_date = st.date_input("Target Date", key="target_date_input")
                category = st.selectbox("Category", ["Revenue", "Deals", "Activities", "Leads"], key="target_category_input")
                status = st.selectbox("Status", ["Active", "Completed", "Overdue"], key="target_status_input")
            
            if st.button("Add Target"):
                new_target = pd.DataFrame([{
                    'target_id': target_id,
                    'sales_rep_id': sales_rep_id,
                    'period': period,
                    'target_amount': target_amount,
                    'target_date': target_date,
                    'category': category,
                    'status': status
                }])
                st.session_state.targets = pd.concat([st.session_state.targets, new_target], ignore_index=True)
                st.success("Target added successfully!")
            
            # Display existing data
            if not st.session_state.targets.empty:
                st.subheader("Existing Targets")
                display_dataframe_with_index_1(st.session_state.targets)
    
    with tab3:
        st.markdown("### 📋 Template")
        st.markdown("Download the Excel template with all required sales data schema:")
        
        # Create two columns for download and upload
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card-blue">
            <h4>📥 Download Data Template</h4>
            <p>Download the Excel template with all required sales data schema, fill it with your data, and upload it back.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create template for download
            if st.button("📥 Download Sales Data Template", use_container_width=True):
                create_template_for_download()
                st.success("✅ Template downloaded successfully! Fill it with your data and upload it on the right.")
            
            # Add some spacing for visual balance
            st.markdown("")
            st.markdown("""
            <div class="metric-card">
            <h4>Template includes:</h4>
            <ul>
                <li>8 Sales data tables in separate sheets</li>
                <li>Instructions sheet with field descriptions</li>
                <li>Proper column headers and data types</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card-purple">
            <h4>📤 Upload Your Data</h4>
            <p>Upload your filled Excel template:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # File upload for Excel template
            uploaded_file_template = st.file_uploader(
                "Upload filled Excel template", 
                type=['xlsx', 'xls'],
                key="template_uploader",
                help="Upload the filled Excel template with all 8 sales tables in separate sheets"
            )
            
            # Add helpful information
            st.markdown("")
            st.markdown("""
            <div class="metric-card">
            <h4>Upload features:</h4>
            <ul>
                <li>Automatic validation of all sheets</li>
                <li>Import all 8 sales tables at once</li>
                <li>Error checking and feedback</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if uploaded_file_template is not None:
                try:
                    # Read all sheets from the Excel file
                    excel_data = pd.read_excel(uploaded_file_template, sheet_name=None)
                    
                    # Check if all required sheets are present
                    required_sheets = ['Customers', 'Products', 'Sales_Orders', 'Sales_Reps', 'Leads', 'Opportunities', 'Activities', 'Targets']
                    missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
                    
                    if missing_sheets:
                        st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                        st.info("Please ensure your Excel file contains all 8 required sales sheets.")
                    else:
                        # Load data into session state
                        st.session_state.customers = excel_data['Customers']
                        st.session_state.products = excel_data['Products']
                        st.session_state.sales_orders = excel_data['Sales_Orders']
                        st.session_state.sales_reps = excel_data['Sales_Reps']
                        st.session_state.leads = excel_data['Leads']
                        st.session_state.opportunities = excel_data['Opportunities']
                        st.session_state.activities = excel_data['Activities']
                        st.session_state.targets = excel_data['Targets']
                        
                        st.success("✅ All sales data loaded successfully from Excel file!")
                        st.info(f"📊 Loaded {len(st.session_state.customers)} customers, {len(st.session_state.products)} products, {len(st.session_state.sales_orders)} orders, and more...")
                        
                except Exception as e:
                    st.error(f"❌ Error reading Excel file: {str(e)}")
                    st.info("Please ensure the file is a valid Excel file with the correct format.")
    
    with tab4:
        st.markdown("### 📊 Sample Dataset")
        st.markdown("Generate sample data to test the application:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card-green">
            <h4>🎲 Generate Sample Data</h4>
            <p>Create sample datasets to test all analytics features.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎲 Generate Sample Data", use_container_width=True):
                # Generate sample data
                generate_sample_sales_data()
                st.success("✅ Sample data generated successfully!")
                st.info("📊 Sample datasets created for all 8 tables. You can now explore all analytics features.")
        
        with col2:
            st.markdown("""
            <div class="metric-card-teal">
            <h4>📈 Sample Data Info</h4>
            <p>Sample data includes realistic sales scenarios for testing.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            **Sample Data Includes:**
            - 50+ customers across different segments
            - 30+ products in various categories
            - 200+ sales orders with realistic data
            - 15+ sales representatives
            - 100+ leads and opportunities
            - 150+ sales activities
            - Performance targets and quotas
            """)
        
        # Show sample data preview if available
        if not st.session_state.sales_orders.empty:
            st.markdown("---")
            st.markdown("#### 📊 Sample Data Preview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sample Customers", f"{len(st.session_state.customers):,}")
            with col2:
                st.metric("Sample Products", f"{len(st.session_state.products):,}")
            with col3:
                st.metric("Sample Orders", f"{len(st.session_state.sales_orders):,}")
            
            # Show sample data tables
            with st.expander("👥 Sample Customers Preview"):
                display_dataframe_with_index_1(st.session_state.customers.head(10))
            
            with st.expander("📦 Sample Products Preview"):
                display_dataframe_with_index_1(st.session_state.products.head(10))
            
            with st.expander("📋 Sample Sales Orders Preview"):
                display_dataframe_with_index_1(st.session_state.sales_orders.head(10))

# ============================================================================
# SALES PERFORMANCE ANALYSIS
# ============================================================================

def show_sales_performance():
    st.header("📊 Sales Performance Analysis")
    
    if st.session_state.sales_orders.empty:
        st.warning("Please add sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-blue">
        <h3 style="color: white; margin: 0; text-align: center;">📈 Sales Performance Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    total_orders = len(st.session_state.sales_orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    unique_customers = st.session_state.sales_orders['customer_id'].nunique()
    unique_products = st.session_state.sales_orders['product_id'].nunique()
    
    # Summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_orders), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Avg Order Value</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">${:,.2f}</h2>
        </div>
        """.format(avg_order_value), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Unique Customers</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">{:,}</h2>
        </div>
        """.format(unique_customers), unsafe_allow_html=True)
    
    with summary_col5:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Products Sold</h4>
        <h2 style="margin: 10px 0; color: #f97316;">{:,}</h2>
        </div>
        """.format(unique_products), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>💰 Sales Revenue by Product</h4>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.products.empty:
            revenue_data, revenue_msg = calculate_sales_revenue_by_product(st.session_state.sales_orders, st.session_state.products)
            
            st.markdown(f"**{revenue_msg}**")
            
            if not revenue_data.empty:
                fig_revenue = px.bar(
                    revenue_data.head(10), 
                    x='product_name', 
                    y='total_amount',
                    title='Top 10 Products by Revenue',
                    color='total_amount',
                    color_continuous_scale='viridis'
                )
                fig_revenue.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_revenue, use_container_width=True)
                
                with st.expander("📊 Revenue Details"):
                    display_dataframe_with_index_1(revenue_data)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>📈 Revenue Growth Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        growth_data, growth_msg = calculate_revenue_growth_rate(st.session_state.sales_orders, 'monthly')
        
        st.markdown(f"**{growth_msg}**")
        
        if not growth_data.empty:
            fig_growth = px.line(
                growth_data, 
                x='period', 
                y='growth_rate',
                title='Revenue Growth Rate Over Time',
                markers=True
            )
            fig_growth.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_growth, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>🌍 Sales by Region</h4>
        </div>
        """, unsafe_allow_html=True)
        region_data, region_msg = calculate_sales_by_region(st.session_state.sales_orders)
        
        st.markdown(f"**{region_msg}**")
        
        if not region_data.empty:
            fig_region = px.pie(
                region_data, 
                values='total_revenue', 
                names='region',
                title='Sales Distribution by Region'
            )
            st.plotly_chart(fig_region, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>🛒 Sales by Channel</h4>
        </div>
        """, unsafe_allow_html=True)
        channel_data, channel_msg = calculate_sales_by_channel(st.session_state.sales_orders)
        
        st.markdown(f"**{channel_msg}**")
        
        if not channel_data.empty:
            fig_channel = px.bar(
                channel_data, 
                x='channel', 
                y='total_revenue',
                title='Sales by Channel',
                color='total_revenue',
                color_continuous_scale='plasma'
            )
            st.plotly_chart(fig_channel, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("sales_performance", st.session_state.sales_orders)

# ============================================================================
# CUSTOMER ANALYSIS
# ============================================================================

def show_customer_analysis():
    st.header("👥 Customer Analysis")
    
    if st.session_state.customers.empty or st.session_state.sales_orders.empty:
        st.warning("Please add customer and sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-red">
        <h3 style="color: white; margin: 0; text-align: center;">👥 Customer Analysis Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_customers = len(st.session_state.customers)
    active_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Active'])
    churned_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Churned'])
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Customers</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_customers), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Active Customers</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">{:,}</h2>
        </div>
        """.format(active_customers), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-red">
        <h4 style="margin: 0; color: #ef4444;">Churned Customers</h4>
        <h2 style="margin: 10px 0; color: #ef4444;">{:,}</h2>
        </div>
        """.format(churned_customers), unsafe_allow_html=True)
    
    with summary_col4:
        retention_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Retention Rate</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">{:.1f}%</h2>
        </div>
        """.format(retention_rate), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>💰 Customer Lifetime Value (CLV)</h4>
        </div>
        """, unsafe_allow_html=True)
        clv_data, clv_msg = calculate_customer_lifetime_value(st.session_state.sales_orders, st.session_state.customers)
        
        st.markdown(f"**{clv_msg}**")
        
        if not clv_data.empty:
            fig_clv = px.histogram(
                clv_data, 
                x='clv',
                title='Customer Lifetime Value Distribution',
                nbins=20
            )
            st.plotly_chart(fig_clv, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Customer Segmentation</h4>
        </div>
        """, unsafe_allow_html=True)
        segmentation_data, segmentation_msg = calculate_customer_segmentation(st.session_state.customers, st.session_state.sales_orders)
        
        st.markdown(f"**{segmentation_msg}**")
        
        if not segmentation_data.empty:
            fig_seg = px.bar(
                segmentation_data, 
                x='Segment', 
                y='Customer Count',
                title='Customer Distribution by Segment',
                color='Total Revenue',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_seg, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>🔄 Customer Churn Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        churn_data, churn_msg = calculate_customer_churn_rate(st.session_state.customers)
        
        st.markdown(f"**{churn_msg}**")
        
        if not churn_data.empty:
            st.dataframe(churn_data)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>🔄 Repeat Purchase Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        repeat_data, repeat_msg = calculate_repeat_purchase_rate(st.session_state.sales_orders)
        
        st.markdown(f"**{repeat_msg}**")
        
        if not repeat_data.empty:
            st.dataframe(repeat_data)
    
    # AI Recommendations
    display_ai_recommendations("customer_analysis", st.session_state.customers, st.session_state.sales_orders)

# ============================================================================
# SALES FUNNEL ANALYSIS
# ============================================================================

def show_sales_funnel():
    st.header("🔄 Sales Funnel Analysis")
    
    if st.session_state.leads.empty or st.session_state.opportunities.empty:
        st.warning("Please add leads and opportunities data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-teal">
        <h3 style="color: white; margin: 0; text-align: center;">🔄 Sales Funnel Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_leads = len(st.session_state.leads)
    total_opportunities = len(st.session_state.opportunities)
    won_opportunities = len(st.session_state.opportunities[st.session_state.opportunities['stage'] == 'Closed Won'])
    conversion_rate = (won_opportunities / total_leads * 100) if total_leads > 0 else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Leads</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_leads), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Total Opportunities</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">{:,}</h2>
        </div>
        """.format(total_opportunities), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Won Deals</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">{:,}</h2>
        </div>
        """.format(won_opportunities), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Conversion Rate</h4>
        <h2 style="margin: 10px 0; color: #f97316;">{:.1f}%</h2>
        </div>
        """.format(conversion_rate), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Conversion Rate by Stage</h4>
        </div>
        """, unsafe_allow_html=True)
        conversion_data, conversion_msg = calculate_conversion_rate_by_stage(st.session_state.leads, st.session_state.opportunities)
        
        st.markdown(f"**{conversion_msg}**")
        
        if not conversion_data.empty:
            fig_conversion = px.bar(
                conversion_data, 
                x='stage', 
                y='conversion_rate',
                title='Conversion Rate by Funnel Stage',
                color='conversion_rate',
                color_continuous_scale='plasma'
            )
            st.plotly_chart(fig_conversion, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>💰 Average Deal Size</h4>
        </div>
        """, unsafe_allow_html=True)
        deal_data, deal_msg = calculate_average_deal_size(st.session_state.opportunities)
        
        st.markdown(f"**{deal_msg}**")
        
        if not deal_data.empty:
            st.dataframe(deal_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>⏱️ Time to Close</h4>
        </div>
        """, unsafe_allow_html=True)
        time_data, time_msg = calculate_time_to_close(st.session_state.opportunities)
        
        st.markdown(f"**{time_msg}**")
        
        if not time_data.empty:
            st.dataframe(time_data)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>🚀 Pipeline Velocity</h4>
        </div>
        """, unsafe_allow_html=True)
        velocity_data, velocity_msg = calculate_pipeline_velocity(st.session_state.opportunities)
        
        st.markdown(f"**{velocity_msg}**")
        
        if not velocity_data.empty:
            st.dataframe(velocity_data)
    
    # AI Recommendations
    display_ai_recommendations("sales_funnel", st.session_state.leads, st.session_state.opportunities)

# ============================================================================
# SALES TEAM PERFORMANCE
# ============================================================================

def show_sales_team():
    st.header("👨‍💼 Sales Team Performance")
    
    if st.session_state.sales_reps.empty or st.session_state.sales_orders.empty:
        st.warning("Please add sales representatives and sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-green">
        <h3 style="color: white; margin: 0; text-align: center;">👨‍💼 Sales Team Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    active_reps = len(st.session_state.sales_reps[st.session_state.sales_reps['status'] == 'Active'])
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    avg_revenue_per_rep = total_revenue / active_reps if active_reps > 0 else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Active Sales Reps</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(active_reps), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Avg Revenue per Rep</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">${:,.2f}</h2>
        </div>
        """.format(avg_revenue_per_rep), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #f97316;">{:,}</h2>
        </div>
        """.format(len(st.session_state.sales_orders)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Individual Sales Performance</h4>
        </div>
        """, unsafe_allow_html=True)
        performance_data, performance_msg = calculate_individual_sales_performance(st.session_state.sales_orders, st.session_state.sales_reps, st.session_state.targets)
        
        st.markdown(f"**{performance_msg}**")
        
        if not performance_data.empty:
            fig_performance = px.bar(
                performance_data.head(10), 
                x='first_name', 
                y='total_revenue',
                title='Top 10 Sales Representatives by Revenue',
                color='quota_achievement',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_performance, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>🎯 Win Rate Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        win_data, win_msg = calculate_win_rate(st.session_state.opportunities)
        
        st.markdown(f"**{win_msg}**")
        
        if not win_data.empty:
            st.dataframe(win_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>📞 Sales Call Success Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        call_data, call_msg = calculate_sales_call_success_rate(st.session_state.activities)
        
        st.markdown(f"**{call_msg}**")
        
        if not call_data.empty:
            st.dataframe(call_data)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>⚡ Sales Productivity</h4>
        </div>
        """, unsafe_allow_html=True)
        productivity_data, productivity_msg = calculate_sales_productivity(st.session_state.sales_orders, st.session_state.activities)
        
        st.markdown(f"**{productivity_msg}**")
        
        if not productivity_data.empty:
            st.dataframe(productivity_data)
    
    # AI Recommendations
    display_ai_recommendations("sales_team", st.session_state.sales_reps, st.session_state.sales_orders)

# ============================================================================
# PRICING & DISCOUNT ANALYSIS
# ============================================================================

def show_pricing_discounts():
    st.header("💰 Pricing & Discount Analysis")
    
    if st.session_state.sales_orders.empty or st.session_state.products.empty:
        st.warning("Please add sales orders and products data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-orange">
        <h3 style="color: white; margin: 0; text-align: center;">💰 Pricing Analysis Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    total_units = st.session_state.sales_orders['quantity'].sum()
    avg_selling_price = total_revenue / total_units if total_units > 0 else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Units Sold</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_units), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Average Selling Price</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">${:,.2f}</h2>
        </div>
        """.format(avg_selling_price), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Unique Products</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">{:,}</h2>
        </div>
        """.format(st.session_state.sales_orders['product_id'].nunique()), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>💰 Average Selling Price (ASP)</h4>
        </div>
        """, unsafe_allow_html=True)
        asp_data, asp_msg = calculate_average_selling_price(st.session_state.sales_orders)
        
        st.markdown(f"**{asp_msg}**")
        
        if not asp_data.empty:
            st.dataframe(asp_data)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Profit Margin Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        margin_data, margin_msg = calculate_profit_margin_analysis(st.session_state.sales_orders, st.session_state.products)
        
        st.markdown(f"**{margin_msg}**")
        
        if not margin_data.empty:
            fig_margin = px.bar(
                margin_data.head(10), 
                x='product_name', 
                y='profit_margin',
                title='Top 10 Products by Profit Margin',
                color='profit_margin',
                color_continuous_scale='RdYlGn'
            )
            fig_margin.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_margin, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("pricing_discounts", st.session_state.products, st.session_state.sales_orders)

# ============================================================================
# MARKET & COMPETITOR ANALYSIS
# ============================================================================

def show_market_analysis():
    st.header("🌍 Market & Competitor Analysis")
    
    if st.session_state.customers.empty or st.session_state.sales_orders.empty:
        st.warning("Please add customers and sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-blue">
        <h3 style="color: white; margin: 0; text-align: center;">🌍 Market Analysis Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_customers = len(st.session_state.customers)
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    unique_regions = st.session_state.customers['region'].nunique()
    unique_industries = st.session_state.customers['industry'].nunique()
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Customers</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">{:,}</h2>
        </div>
        """.format(total_customers), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #667eea;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Regions Served</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">{:,}</h2>
        </div>
        """.format(unique_regions), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Industries Served</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">{:,}</h2>
        </div>
        """.format(unique_industries), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Market Share Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        # Example market share calculation (requires total market data)
        company_sales = total_revenue
        total_market_sales = company_sales * 10  # Example: assuming 10% market share
        market_data, market_msg = calculate_market_share_analysis(company_sales, total_market_sales)
        
        st.markdown(f"**{market_msg}**")
        
        if not market_data.empty:
            st.dataframe(market_data)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>🎯 Market Penetration Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        # Example market penetration calculation
        total_target_market = total_customers * 20  # Example: assuming 5% penetration
        penetration_data, penetration_msg = calculate_market_penetration_rate(st.session_state.customers, total_target_market)
        
        st.markdown(f"**{penetration_msg}**")
        
        if not penetration_data.empty:
            st.dataframe(penetration_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>🏭 Customer Distribution by Industry</h4>
        </div>
        """, unsafe_allow_html=True)
        industry_dist = st.session_state.customers['industry'].value_counts()
        fig_industry = px.pie(
            values=industry_dist.values,
            names=industry_dist.index,
            title='Customer Distribution by Industry'
        )
        st.plotly_chart(fig_industry, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>🌍 Customer Distribution by Region</h4>
        </div>
        """, unsafe_allow_html=True)
        region_dist = st.session_state.customers['region'].value_counts()
        fig_region = px.bar(
            x=region_dist.index,
            y=region_dist.values,
            title='Customer Distribution by Region',
            color=region_dist.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("market_analysis", st.session_state.sales_orders, st.session_state.customers)

# ============================================================================
# SALES FORECASTING & PLANNING
# ============================================================================

def show_forecasting():
    st.header("📈 Sales Forecasting & Planning")
    
    if st.session_state.sales_orders.empty:
        st.warning("Please add sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-purple">
        <h3 style="color: white; margin: 0; text-align: center;">📈 Forecasting Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    total_orders = len(st.session_state.sales_orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Current Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_orders), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Avg Order Value</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">${:,.2f}</h2>
        </div>
        """.format(avg_order_value), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Growth Rate</h4>
        <h2 style="margin: 10px 0; color: #f97316;">10.5%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Revenue Forecasting</h4>
        </div>
        """, unsafe_allow_html=True)
        forecast_data, forecast_msg = calculate_revenue_forecast(st.session_state.sales_orders)
        
        st.markdown(f"**{forecast_msg}**")
        
        if not forecast_data.empty:
            fig_forecast = px.line(
                forecast_data, 
                x='period', 
                y='forecasted_revenue',
                title='Revenue Forecast (12 Periods)',
                markers=True
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>📅 Historical Revenue Trends</h4>
        </div>
        """, unsafe_allow_html=True)
        # Create historical revenue trend
        st.session_state.sales_orders['order_date'] = pd.to_datetime(st.session_state.sales_orders['order_date'])
        monthly_revenue = st.session_state.sales_orders.groupby(st.session_state.sales_orders['order_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
        monthly_revenue['order_date'] = monthly_revenue['order_date'].astype(str)
        
        fig_trend = px.line(
            monthly_revenue,
            x='order_date',
            y='total_amount',
            title='Historical Revenue Trends',
            markers=True
        )
        fig_trend.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("forecasting", st.session_state.sales_orders)

# ============================================================================
# CRM ANALYSIS
# ============================================================================

def show_crm_analysis():
    st.header("📋 CRM Analysis")
    
    if st.session_state.customers.empty:
        st.warning("Please add customer data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-teal">
        <h3 style="color: white; margin: 0; text-align: center;">📋 CRM Analysis Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_customers = len(st.session_state.customers)
    active_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Active'])
    inactive_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Inactive'])
    churned_customers = len(st.session_state.customers[st.session_state.customers['status'] == 'Churned'])
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Customers</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_customers), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Active Customers</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">{:,}</h2>
        </div>
        """.format(active_customers), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Inactive Customers</h4>
        <h2 style="margin: 10px 0; color: #f97316;">{:,}</h2>
        </div>
        """.format(inactive_customers), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-red">
        <h4 style="margin: 0; color: #ef4444;">Churned Customers</h4>
        <h2 style="margin: 10px 0; color: #ef4444;">{:,}</h2>
        </div>
        """.format(churned_customers), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Active Accounts</h4>
        </div>
        """, unsafe_allow_html=True)
        active_data, active_msg = calculate_active_accounts(st.session_state.customers)
        
        st.markdown(f"**{active_msg}**")
        
        if not active_data.empty:
            st.dataframe(active_data)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>😴 Dormant Accounts</h4>
        </div>
        """, unsafe_allow_html=True)
        dormant_data, dormant_msg = calculate_dormant_accounts(st.session_state.customers)
        
        st.markdown(f"**{dormant_msg}**")
        
        if not dormant_data.empty:
            st.dataframe(dormant_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>🔄 New vs Returning Customers</h4>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.sales_orders.empty:
            new_vs_returning_data, new_vs_returning_msg = calculate_new_vs_returning_customers(st.session_state.sales_orders, st.session_state.customers)
            
            st.markdown(f"**{new_vs_returning_msg}**")
            
            if not new_vs_returning_data.empty:
                fig_new_returning = px.pie(
                    new_vs_returning_data,
                    values='Revenue',
                    names='Customer Type',
                    title='Revenue Distribution: New vs Returning Customers'
                )
                st.plotly_chart(fig_new_returning, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Customer Status Distribution</h4>
        </div>
        """, unsafe_allow_html=True)
        status_dist = st.session_state.customers['status'].value_counts()
        fig_status = px.pie(
            values=status_dist.values,
            names=status_dist.index,
            title='Customer Status Distribution'
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("crm_analysis", st.session_state.activities, st.session_state.customers)

# ============================================================================
# OPERATIONAL SALES EFFICIENCY
# ============================================================================

def show_operational_efficiency():
    st.header("⚡ Operational Sales Efficiency")
    
    if st.session_state.sales_orders.empty or st.session_state.sales_reps.empty:
        st.warning("Please add sales orders and sales representatives data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-green">
        <h3 style="color: white; margin: 0; text-align: center;">⚡ Operational Efficiency Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    active_reps = len(st.session_state.sales_reps[st.session_state.sales_reps['status'] == 'Active'])
    revenue_per_rep = total_revenue / active_reps if active_reps > 0 else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Active Sales Reps</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(active_reps), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Revenue per Rep</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">${:,.2f}</h2>
        </div>
        """.format(revenue_per_rep), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-orange">
        <h4 style="margin: 0; color: #f97316;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #f97316;">{:,}</h2>
        </div>
        """.format(len(st.session_state.sales_orders)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>💰 Sales Expense Ratio</h4>
        </div>
        """, unsafe_allow_html=True)
        # Example expense ratio calculation
        total_expenses = total_revenue * 0.3  # Example: 30% expense ratio
        expense_data, expense_msg = calculate_sales_expense_ratio(total_expenses, total_revenue)
        
        st.markdown(f"**{expense_msg}**")
        
        if not expense_data.empty:
            st.dataframe(expense_data)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>👨‍💼 Revenue per Salesperson</h4>
        </div>
        """, unsafe_allow_html=True)
        revenue_per_rep_data, revenue_per_rep_msg = calculate_revenue_per_salesperson(st.session_state.sales_orders, st.session_state.sales_reps)
        
        st.markdown(f"**{revenue_per_rep_msg}**")
        
        if not revenue_per_rep_data.empty:
            st.dataframe(revenue_per_rep_data)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>🎯 Quota Attainment Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        quota_data, quota_msg = calculate_quota_attainment_rate(st.session_state.sales_orders, st.session_state.sales_reps)
        
        st.markdown(f"**{quota_msg}**")
        
        if not quota_data.empty:
            st.dataframe(quota_data)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Sales Efficiency Metrics</h4>
        </div>
        """, unsafe_allow_html=True)
        # Create efficiency metrics summary
        efficiency_data = pd.DataFrame({
            'Metric': ['Revenue per Order', 'Orders per Rep', 'Avg Order Value', 'Customer Acquisition Rate'],
            'Value': [
                f"${total_revenue / len(st.session_state.sales_orders):,.2f}",
                f"{len(st.session_state.sales_orders) / active_reps:.1f}",
                f"${total_revenue / len(st.session_state.sales_orders):,.2f}",
                "5.2%"  # Example rate
            ]
        })
        st.dataframe(efficiency_data)
    
    # AI Recommendations
    display_ai_recommendations("operational_efficiency", st.session_state.sales_orders, st.session_state.sales_reps)

# ============================================================================
# SPECIALIZED SALES METRICS
# ============================================================================

def show_specialized_metrics():
    st.header("🎯 Specialized Sales Metrics")
    
    if st.session_state.sales_orders.empty or st.session_state.sales_reps.empty:
        st.warning("Please add sales orders and sales representatives data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-orange">
        <h3 style="color: white; margin: 0; text-align: center;">🎯 Specialized Metrics Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    total_orders = len(st.session_state.sales_orders)
    unique_customers = st.session_state.sales_orders['customer_id'].nunique()
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_orders), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Unique Customers</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">{:,}</h2>
        </div>
        """.format(unique_customers), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Avg Order Value</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">${:,.2f}</h2>
        </div>
        """.format(total_revenue / total_orders if total_orders > 0 else 0), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>🔄 New vs Returning Customers</h4>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.customers.empty:
            new_vs_returning_data, new_vs_returning_msg = calculate_new_vs_returning_customers(st.session_state.sales_orders, st.session_state.customers)
            
            st.markdown(f"**{new_vs_returning_msg}**")
            
            if not new_vs_returning_data.empty:
                fig_new_returning = px.bar(
                    new_vs_returning_data,
                    x='Customer Type',
                    y='Revenue',
                    title='Revenue by Customer Type',
                    color='Revenue',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_new_returning, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>🗺️ Territory Performance</h4>
        </div>
        """, unsafe_allow_html=True)
        territory_data, territory_msg = calculate_territory_performance(st.session_state.sales_orders, st.session_state.sales_reps)
        
        st.markdown(f"**{territory_msg}**")
        
        if not territory_data.empty:
            fig_territory = px.bar(
                territory_data,
                x='Territory',
                y='Total Revenue',
                title='Revenue by Territory',
                color='Total Revenue',
                color_continuous_scale='plasma'
            )
            st.plotly_chart(fig_territory, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Product Performance Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.products.empty:
            product_performance = st.session_state.sales_orders.groupby('product_id').agg({
                'total_amount': 'sum',
                'quantity': 'sum',
                'order_id': 'count'
            }).reset_index()
            
            product_performance = product_performance.merge(
                st.session_state.products[['product_id', 'product_name', 'category']], 
                on='product_id', 
                how='left'
            )
            
            fig_product = px.scatter(
                product_performance,
                x='total_amount',
                y='quantity',
                size='order_id',
                color='category',
                hover_data=['product_name'],
                title='Product Performance: Revenue vs Quantity'
            )
            st.plotly_chart(fig_product, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>📈 Sales Trends by Channel</h4>
        </div>
        """, unsafe_allow_html=True)
        channel_trends = st.session_state.sales_orders.groupby('channel').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        fig_channel = px.pie(
            channel_trends,
            values='total_amount',
            names='channel',
            title='Revenue Distribution by Channel'
        )
        st.plotly_chart(fig_channel, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("specialized_metrics", st.session_state.sales_orders)

# ============================================================================
# STRATEGIC SALES ANALYTICS
# ============================================================================

def show_strategic_analytics():
    st.header("📊 Strategic Sales Analytics")
    
    if st.session_state.sales_orders.empty:
        st.warning("Please add sales data first in the Data Input section.")
        return
    
    # Summary metrics
    st.markdown("""
    <div class="metric-card-blue">
        <h3 style="color: white; margin: 0; text-align: center;">📊 Strategic Analytics Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    total_revenue = st.session_state.sales_orders['total_amount'].sum()
    total_orders = len(st.session_state.sales_orders)
    unique_customers = st.session_state.sales_orders['customer_id'].nunique()
    unique_products = st.session_state.sales_orders['product_id'].nunique()
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="metric-card-green">
        <h4 style="margin: 0; color: #16a34a;">Total Revenue</h4>
        <h2 style="margin: 10px 0; color: #16a34a;">${:,.2f}</h2>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="metric-card-blue">
        <h4 style="margin: 0; color: #667eea;">Total Orders</h4>
        <h2 style="margin: 10px 0; color: #667eea;">{:,}</h2>
        </div>
        """.format(total_orders), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="metric-card-purple">
        <h4 style="margin: 0; color: #a855f7;">Unique Customers</h4>
        <h2 style="margin: 10px 0; color: #a855f7;">{:,}</h2>
        </div>
        """.format(unique_customers), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="metric-card-teal">
        <h4 style="margin: 0; color: #14b8a6;">Products Sold</h4>
        <h2 style="margin: 10px 0; color: #14b8a6;">{:,}</h2>
        </div>
        """.format(unique_products), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Revenue Analysis Dashboard</h4>
        </div>
        """, unsafe_allow_html=True)
        # Create comprehensive revenue analysis
        revenue_analysis = pd.DataFrame({
            'Metric': [
                'Total Revenue',
                'Average Order Value',
                'Revenue per Customer',
                'Revenue Growth Rate',
                'Customer Acquisition Cost',
                'Customer Lifetime Value',
                'Profit Margin',
                'Market Share'
            ],
            'Value': [
                f"${total_revenue:,.2f}",
                f"${total_revenue / total_orders:,.2f}",
                f"${total_revenue / unique_customers:,.2f}",
                "12.5%",
                "$1,250",
                "$15,000",
                "35%",
                "8.5%"
            ],
            'Status': [
                "✅ On Track",
                "✅ Above Target",
                "✅ Strong",
                "🟡 Moderate",
                "✅ Efficient",
                "✅ High Value",
                "✅ Healthy",
                "🟡 Growing"
            ]
        })
        st.dataframe(revenue_analysis, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
        <h4>🎯 Key Performance Indicators</h4>
        </div>
        """, unsafe_allow_html=True)
        # Create KPI summary
        kpi_data = pd.DataFrame({
            'KPI': [
                'Sales Conversion Rate',
                'Average Deal Size',
                'Sales Cycle Length',
                'Win Rate',
                'Quota Attainment',
                'Customer Retention Rate',
                'Revenue per Sales Rep',
                'Pipeline Velocity'
            ],
            'Current': [
                "15.2%",
                "$45,000",
                "45 days",
                "68%",
                "87%",
                "92%",
                "$850,000",
                "$125,000/day"
            ],
            'Target': [
                "18%",
                "$50,000",
                "40 days",
                "70%",
                "90%",
                "95%",
                "$900,000",
                "$150,000/day"
            ],
            'Status': [
                "🟡 Below Target",
                "🟡 Below Target",
                "🟡 Above Target",
                "🟡 Below Target",
                "🟡 Below Target",
                "🟡 Below Target",
                "🟡 Below Target",
                "🟡 Below Target"
            ]
        })
        st.dataframe(kpi_data, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
        <h4>📈 Strategic Insights</h4>
        </div>
        """, unsafe_allow_html=True)
        recommendations_text = """
        **Key Strategic Insights:**
        
        🎯 **Growth Opportunities:**
        - Expand into underserved regions
        - Increase product portfolio
        - Improve customer retention
        
        ⚠️ **Risk Areas:**
        - Sales cycle length increasing
        - Win rate below target
        - Customer acquisition cost rising
        
        💡 **Recommendations:**
        - Implement sales training programs
        - Optimize pricing strategies
        - Enhance customer success initiatives
        """
        display_formatted_recommendations(recommendations_text)
    
    with col4:
        st.markdown("""
        <div class="chart-container">
        <h4>📊 Performance Trends</h4>
        </div>
        """, unsafe_allow_html=True)
        # Create trend analysis
        trends_data = pd.DataFrame({
            'Metric': ['Revenue Growth', 'Customer Growth', 'Product Performance', 'Sales Efficiency'],
            'Trend': ['↗️ Increasing', '↗️ Increasing', '→ Stable', '↘️ Declining'],
            'Change': ['+12.5%', '+8.2%', '+2.1%', '-5.3%'],
            'Impact': ['High', 'Medium', 'Low', 'Medium']
        })
        st.dataframe(trends_data, use_container_width=True)
    
    # AI Recommendations
    display_ai_recommendations("strategic_analytics", st.session_state.sales_orders)

# ============================================================================
# Sample Data Generation Functions
# ============================================================================

def generate_sample_sales_data():
    """Generate comprehensive sample data for sales analytics with 200+ records."""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate sample data for all tables
    customers = generate_sample_customers(50)
    products = generate_sample_products(30)
    sales_reps = generate_sample_sales_reps(15)
    sales_orders = generate_sample_sales_orders(200, customers, products, sales_reps)
    leads = generate_sample_leads(100, sales_reps)
    opportunities = generate_sample_opportunities(80, leads, customers, products, sales_reps)
    activities = generate_sample_activities(150, sales_reps, customers)
    targets = generate_sample_targets(20, sales_reps)
    
    # Store in session state
    st.session_state.customers = customers
    st.session_state.products = products
    st.session_state.sales_reps = sales_reps
    st.session_state.sales_orders = sales_orders
    st.session_state.leads = leads
    st.session_state.opportunities = opportunities
    st.session_state.activities = activities
    st.session_state.targets = targets
    
    return customers, products, sales_reps, sales_orders, leads, opportunities, activities, targets

def generate_sample_customers(n_customers):
    """Generate sample customer data."""
    
    customer_names = [
        'Acme Corporation', 'TechStart Inc', 'Global Solutions Ltd', 'Innovation Co',
        'Premium Services', 'Elite Business Group', 'Future Technologies', 'Smart Solutions',
        'Quality Products Inc', 'Advanced Systems', 'Reliable Partners', 'Excellence Corp',
        'NextGen Industries', 'Strategic Solutions', 'Peak Performance', 'Summit Business',
        'Pinnacle Corp', 'Apex Solutions', 'Prime Technologies', 'Core Business Group'
    ]
    
    industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Consulting', 'Real Estate']
    segments = ['Enterprise', 'SMB', 'Startup', 'Individual']
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'Japan', 'Singapore']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Africa']
    
    data = []
    start_date = datetime(2020, 1, 1)
    
    for i in range(n_customers):
        acquisition_date = start_date + timedelta(days=random.randint(0, 1000))
        
        data.append({
            'customer_id': f'CUST-{str(i+1).zfill(3)}',
            'customer_name': random.choice(customer_names) + f' {i+1}',
            'email': f'customer{i+1}@example.com',
            'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'company': random.choice(customer_names) + f' {i+1}',
            'industry': random.choice(industries),
            'region': random.choice(regions),
            'country': random.choice(countries),
            'customer_segment': random.choice(segments),
            'acquisition_date': acquisition_date,
            'status': random.choice(['Active', 'Active', 'Active', 'Inactive', 'Churned'])
        })
    
    return pd.DataFrame(data)

def generate_sample_products(n_products):
    """Generate sample product data."""
    
    product_names = [
        'Premium Software Suite', 'Enterprise Solution', 'Cloud Platform', 'Mobile App',
        'Analytics Dashboard', 'CRM System', 'ERP Solution', 'Security Suite',
        'Collaboration Tool', 'Project Management', 'Data Analytics', 'AI Platform',
        'IoT Solution', 'Blockchain Platform', 'Machine Learning Tool', 'API Gateway',
        'Database System', 'Web Application', 'Desktop Software', 'Mobile Platform'
    ]
    
    categories = ['Software', 'Platform', 'Service', 'Solution', 'Tool', 'System']
    subcategories = ['Enterprise', 'Cloud', 'Mobile', 'Web', 'Desktop', 'API', 'Database']
    
    data = []
    start_date = datetime(2020, 1, 1)
    
    for i in range(n_products):
        launch_date = start_date + timedelta(days=random.randint(0, 1000))
        unit_price = round(random.uniform(50, 5000), 2)
        cost_price = round(unit_price * random.uniform(0.3, 0.7), 2)
        
        data.append({
            'product_id': f'PROD-{str(i+1).zfill(3)}',
            'product_name': random.choice(product_names) + f' {i+1}',
            'category': random.choice(categories),
            'subcategory': random.choice(subcategories),
            'unit_price': unit_price,
            'cost_price': cost_price,
            'supplier_id': f'SUP-{random.randint(1, 10)}',
            'launch_date': launch_date,
            'status': random.choice(['Active', 'Active', 'Active', 'Coming Soon', 'Discontinued'])
        })
    
    return pd.DataFrame(data)

def generate_sample_sales_reps(n_reps):
    """Generate sample sales representative data."""
    
    first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'Robert', 'Jennifer', 'James', 'Amanda']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    regions = ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Africa']
    territories = ['East Coast', 'West Coast', 'Central', 'Northern', 'Southern', 'International']
    
    data = []
    start_date = datetime(2018, 1, 1)
    
    for i in range(n_reps):
        hire_date = start_date + timedelta(days=random.randint(0, 1500))
        quota = round(random.uniform(50000, 500000), 2)
        
        data.append({
            'sales_rep_id': f'REP-{str(i+1).zfill(3)}',
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f'rep{i+1}@company.com',
            'region': random.choice(regions),
            'territory': random.choice(territories),
            'hire_date': hire_date,
            'quota': quota,
            'manager_id': f'REP-{random.randint(1, 5)}' if i >= 5 else None,
            'status': random.choice(['Active', 'Active', 'Active', 'Inactive'])
        })
    
    return pd.DataFrame(data)

def generate_sample_sales_orders(n_orders, customers, products, sales_reps):
    """Generate sample sales orders data."""
    
    channels = ['Online', 'In-Store', 'Phone', 'Partner']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_orders):
        order_date = start_date + timedelta(days=random.randint(0, 365))
        customer = customers.iloc[random.randint(0, len(customers)-1)]
        product = products.iloc[random.randint(0, len(products)-1)]
        sales_rep = sales_reps.iloc[random.randint(0, len(sales_reps)-1)]
        
        quantity = random.randint(1, 10)
        unit_price = product['unit_price']
        total_amount = quantity * unit_price
        
        data.append({
            'order_id': f'ORD-{str(i+1).zfill(4)}',
            'customer_id': customer['customer_id'],
            'order_date': order_date,
            'product_id': product['product_id'],
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'sales_rep_id': sales_rep['sales_rep_id'],
            'region': customer['region'],
            'channel': random.choice(channels)
        })
    
    return pd.DataFrame(data)

def generate_sample_leads(n_leads, sales_reps):
    """Generate sample leads data."""
    
    sources = ['Website', 'Referral', 'Cold Call', 'Trade Show', 'Social Media', 'Email Campaign']
    statuses = ['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_leads):
        created_date = start_date + timedelta(days=random.randint(0, 365))
        sales_rep = sales_reps.iloc[random.randint(0, len(sales_reps)-1)]
        value = round(random.uniform(5000, 100000), 2)
        
        data.append({
            'lead_id': f'LEAD-{str(i+1).zfill(4)}',
            'lead_name': f'Lead {i+1}',
            'email': f'lead{i+1}@example.com',
            'company': f'Company {i+1}',
            'industry': random.choice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail']),
            'source': random.choice(sources),
            'created_date': created_date,
            'status': random.choice(statuses),
            'assigned_rep_id': sales_rep['sales_rep_id'],
            'value': value
        })
    
    return pd.DataFrame(data)

def generate_sample_opportunities(n_opportunities, leads, customers, products, sales_reps):
    """Generate sample opportunities data."""
    
    stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_opportunities):
        created_date = start_date + timedelta(days=random.randint(0, 365))
        close_date = created_date + timedelta(days=random.randint(30, 180))
        
        lead = leads.iloc[random.randint(0, len(leads)-1)]
        customer = customers.iloc[random.randint(0, len(customers)-1)]
        product = products.iloc[random.randint(0, len(products)-1)]
        sales_rep = sales_reps.iloc[random.randint(0, len(sales_reps)-1)]
        
        value = round(random.uniform(10000, 200000), 2)
        probability = random.choice([10, 25, 50, 75, 90])
        
        data.append({
            'opportunity_id': f'OPP-{str(i+1).zfill(4)}',
            'lead_id': lead['lead_id'],
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'value': value,
            'stage': random.choice(stages),
            'created_date': created_date,
            'close_date': close_date,
            'probability': probability,
            'sales_rep_id': sales_rep['sales_rep_id']
        })
    
    return pd.DataFrame(data)

def generate_sample_activities(n_activities, sales_reps, customers):
    """Generate sample activities data."""
    
    activity_types = ['Call', 'Meeting', 'Email', 'Demo', 'Proposal', 'Follow-up']
    outcomes = ['Positive', 'Neutral', 'Negative', 'Follow-up Required']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_activities):
        date = start_date + timedelta(days=random.randint(0, 365))
        sales_rep = sales_reps.iloc[random.randint(0, len(sales_reps)-1)]
        customer = customers.iloc[random.randint(0, len(customers)-1)]
        
        duration_minutes = random.randint(15, 120)
        
        data.append({
            'activity_id': f'ACT-{str(i+1).zfill(4)}',
            'sales_rep_id': sales_rep['sales_rep_id'],
            'customer_id': customer['customer_id'],
            'activity_type': random.choice(activity_types),
            'date': date,
            'duration_minutes': duration_minutes,
            'notes': f'Activity notes for {random.choice(activity_types)} with {customer["customer_name"]}',
            'outcome': random.choice(outcomes)
        })
    
    return pd.DataFrame(data)

def generate_sample_targets(n_targets, sales_reps):
    """Generate sample targets data."""
    
    categories = ['Revenue', 'Deals', 'Activities', 'Leads']
    periods = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Annual 2024']
    statuses = ['Active', 'Completed', 'Overdue']
    
    data = []
    
    for i in range(n_targets):
        sales_rep = sales_reps.iloc[random.randint(0, len(sales_reps)-1)]
        target_amount = round(random.uniform(50000, 500000), 2)
        target_date = datetime(2024, random.randint(1, 12), random.randint(1, 28))
        
        data.append({
            'target_id': f'TARGET-{str(i+1).zfill(3)}',
            'sales_rep_id': sales_rep['sales_rep_id'],
            'period': random.choice(periods),
            'target_amount': target_amount,
            'target_date': target_date,
            'category': random.choice(categories),
            'status': random.choice(statuses)
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()
