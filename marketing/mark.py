import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import datetime
import io
import base64
import os
from datetime import datetime

# Set Plotly template
pio.templates.default = "plotly_white"
CONTINUOUS_COLOR_SCALE = "Turbo"
CATEGORICAL_COLOR_SEQUENCE = px.colors.qualitative.Pastel

# Import marketing metric calculation functions
from marketing_metrics_calculator import *

def apply_common_layout(fig):
    """Apply common layout settings to Plotly figures"""
    fig.update_layout(
        font=dict(family="Arial", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, t=50, b=50),
        height=500
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

def create_template_for_download():
    """Create an Excel template with all required marketing data schema and make it downloadable"""
    
    # Create empty DataFrames with the correct marketing schema
    campaigns_template = pd.DataFrame(columns=[
        'campaign_id', 'campaign_name', 'start_date', 'end_date', 'budget', 
        'channel', 'campaign_type', 'target_audience', 'status', 'objective'
    ])
    
    customers_template = pd.DataFrame(columns=[
        'customer_id', 'customer_name', 'email', 'phone', 'age', 'gender', 
        'location', 'acquisition_source', 'acquisition_date', 'customer_segment',
        'lifetime_value', 'last_purchase_date', 'total_purchases', 'status'
    ])
    
    website_traffic_template = pd.DataFrame(columns=[
        'session_id', 'customer_id', 'visit_date', 'page_url', 'time_on_page',
        'bounce_rate', 'traffic_source', 'device_type', 'conversion_flag'
    ])
    
    social_media_template = pd.DataFrame(columns=[
        'post_id', 'platform', 'post_date', 'content_type', 'impressions',
        'clicks', 'likes', 'shares', 'comments', 'reach', 'engagement_rate'
    ])
    
    email_campaigns_template = pd.DataFrame(columns=[
        'email_id', 'campaign_id', 'send_date', 'subject_line', 'recipients',
        'opens', 'clicks', 'unsubscribes', 'bounces', 'conversions'
    ])
    
    content_marketing_template = pd.DataFrame(columns=[
        'content_id', 'content_type', 'publish_date', 'title', 'views',
        'time_on_page', 'shares', 'comments', 'leads_generated', 'conversions'
    ])
    
    leads_template = pd.DataFrame(columns=[
        'lead_id', 'lead_name', 'email', 'company', 'source', 'created_date',
        'status', 'assigned_to', 'value', 'conversion_date'
    ])
    
    conversions_template = pd.DataFrame(columns=[
        'conversion_id', 'customer_id', 'campaign_id', 'conversion_date',
        'conversion_type', 'revenue', 'attribution_source', 'touchpoint_count'
    ])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each template to a separate sheet
        campaigns_template.to_excel(writer, sheet_name='Campaigns', index=False)
        customers_template.to_excel(writer, sheet_name='Customers', index=False)
        website_traffic_template.to_excel(writer, sheet_name='Website_Traffic', index=False)
        social_media_template.to_excel(writer, sheet_name='Social_Media', index=False)
        email_campaigns_template.to_excel(writer, sheet_name='Email_Campaigns', index=False)
        content_marketing_template.to_excel(writer, sheet_name='Content_Marketing', index=False)
        leads_template.to_excel(writer, sheet_name='Leads', index=False)
        conversions_template.to_excel(writer, sheet_name='Conversions', index=False)
        
        # Get the workbook for formatting
        workbook = writer.book
        
        # Add instructions sheet
        instructions_data = {
            'Sheet Name': ['Campaigns', 'Customers', 'Website_Traffic', 'Social_Media', 'Email_Campaigns', 'Content_Marketing', 'Leads', 'Conversions'],
            'Required Fields': [
                'campaign_id, campaign_name, start_date, end_date, budget, channel, campaign_type, target_audience, status, objective',
                'customer_id, customer_name, email, phone, age, gender, location, acquisition_source, acquisition_date, customer_segment, lifetime_value, last_purchase_date, total_purchases, status',
                'session_id, customer_id, visit_date, page_url, time_on_page, bounce_rate, traffic_source, device_type, conversion_flag',
                'post_id, platform, post_date, content_type, impressions, clicks, likes, shares, comments, reach, engagement_rate',
                'email_id, campaign_id, send_date, subject_line, recipients, opens, clicks, unsubscribes, bounces, conversions',
                'content_id, content_type, publish_date, title, views, time_on_page, shares, comments, leads_generated, conversions',
                'lead_id, lead_name, email, company, source, created_date, status, assigned_to, value, conversion_date',
                'conversion_id, customer_id, campaign_id, conversion_date, conversion_type, revenue, attribution_source, touchpoint_count'
            ],
            'Data Types': [
                'Text, Text, Date, Date, Number, Text, Text, Text, Text, Text',
                'Text, Text, Text, Text, Number, Text, Text, Text, Date, Text, Number, Date, Number, Text',
                'Text, Text, Date, Text, Number, Number, Text, Text, Boolean',
                'Text, Text, Date, Text, Number, Number, Number, Number, Number, Number, Number',
                'Text, Text, Date, Text, Number, Number, Number, Number, Number, Number',
                'Text, Text, Date, Text, Number, Number, Number, Number, Number, Number',
                'Text, Text, Text, Text, Text, Date, Text, Text, Number, Date',
                'Text, Text, Text, Date, Text, Number, Text, Number'
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
    """Export all loaded data to Excel file"""
    if 'campaigns_data' not in st.session_state or st.session_state.campaigns_data.empty:
        st.warning("No data loaded to export.")
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Export each dataset to separate sheets
        if 'campaigns_data' in st.session_state and not st.session_state.campaigns_data.empty:
            st.session_state.campaigns_data.to_excel(writer, sheet_name='Campaigns', index=False)
        
        if 'customers_data' in st.session_state and not st.session_state.customers_data.empty:
            st.session_state.customers_data.to_excel(writer, sheet_name='Customers', index=False)
        
        if 'website_traffic_data' in st.session_state and not st.session_state.website_traffic_data.empty:
            st.session_state.website_traffic_data.to_excel(writer, sheet_name='Website_Traffic', index=False)
        
        if 'social_media_data' in st.session_state and not st.session_state.social_media_data.empty:
            st.session_state.social_media_data.to_excel(writer, sheet_name='Social_Media', index=False)
        
        if 'email_campaigns_data' in st.session_state and not st.session_state.email_campaigns_data.empty:
            st.session_state.email_campaigns_data.to_excel(writer, sheet_name='Email_Campaigns', index=False)
        
        if 'content_marketing_data' in st.session_state and not st.session_state.content_marketing_data.empty:
            st.session_state.content_marketing_data.to_excel(writer, sheet_name='Content_Marketing', index=False)
        
        if 'leads_data' in st.session_state and not st.session_state.leads_data.empty:
            st.session_state.leads_data.to_excel(writer, sheet_name='Leads', index=False)
        
        if 'conversions_data' in st.session_state and not st.session_state.conversions_data.empty:
            st.session_state.conversions_data.to_excel(writer, sheet_name='Conversions', index=False)
    
    output.seek(0)
    return output

def show_home():
    st.markdown("""
    ## Welcome to the Marketing Analytics Dashboard
    
    This comprehensive tool helps you calculate and analyze key marketing metrics across multiple categories:
    
    ### 📊 Available Marketing Analytics Categories:
    
    **1. 📈 Campaign Performance Analysis**
    - Return on Investment (ROI)
    - Cost Per Acquisition (CPA)
    - Click-Through Rate (CTR)
    - Conversion Rate
    - Engagement Rate
    - Ad Spend Effectiveness
    
    **2. 👥 Customer Analysis**
    - Customer Lifetime Value (CLV)
    - Customer Churn Rate
    - Customer Segmentation
    - Acquisition Source Analysis
    - Repeat Customer Rate
    
    **3. 🌍 Market Analysis**
    - Market Share Analysis
    - Competitor Benchmarking
    - Demand Analysis
    - Geographical Performance
    
    **4. 📝 Content Marketing Analysis**
    - Content Engagement Metrics
    - Time on Page Analysis
    - Top-Performing Content
    - Bounce Rate
    - Lead Generation by Content
    
    **5. 🌐 Digital Marketing & Web Analytics**
    - Website Traffic Analysis
    - SEO Performance
    - Pay-Per-Click (PPC) Metrics
    - Email Campaign Metrics
    - Social Media Engagement
    
    **6. 🏷️ Brand Awareness & Perception**
    - Brand Recognition Metrics
    - Sentiment Analysis
    - Net Promoter Score (NPS)
    - Share of Voice (SOV)
    - Public Relations Impact
    
    **7. 📦 Product Marketing Analysis**
    - Product Sales Performance
    - Product Launch Analysis
    - Pricing Strategy Effectiveness
    - Feature Adoption Metrics
    
    **8. 🛤️ Customer Journey Analysis**
    - Attribution Modeling
    - Path to Purchase Analysis
    - Cart Abandonment Rate
    - Retention Funnel Analysis
    
    **9. 🔮 Marketing Forecasting**
    - Lead Forecasting
    - Revenue Forecasting
    - Campaign Budget Forecasting
    
    **10. 📱 Channel-Specific Analysis**
    - Social Media Analysis
    - Email Marketing Analysis
    - Influencer Marketing ROI
    - Affiliate Marketing Performance
    
    **11. 🎯 Specialized Marketing Metrics**
    - Seasonal Trends
    - Customer Advocacy Metrics
    - Mobile Marketing Metrics
    - Event Marketing Metrics
    
    ### 🚀 Getting Started:
    
    1. **Data Input**: Start by entering your marketing data in the "Data Input" tab
    2. **Calculate Metrics**: Use the main tabs to view specific metric categories
    3. **Real-time Analysis**: All metrics update automatically based on your data
    
    ### 📈 Data Schema:
    
    The application supports the following marketing data tables:
    - Campaigns (campaign details, budget, channels, objectives)
    - Customers (demographics, segments, acquisition, lifetime value)
    - Website Traffic (sessions, page views, traffic sources, conversions)
    - Social Media (posts, engagement, platform performance)
    - Email Campaigns (sends, opens, clicks, conversions)
    - Content Marketing (content pieces, engagement, lead generation)
    - Leads (prospects, sources, status, conversion)
    - Conversions (revenue, attribution, touchpoints)
    
    ---
    
    **Note**: All calculations are performed automatically based on your input data. Make sure to enter complete and accurate data for the most reliable metrics.
    """)

def show_data_input():
    """Show data input forms and file upload options"""
    st.markdown("## 📝 Data Input")
    
    # Create tabs for different data input methods
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Download Template", "📤 Upload Data", "📝 Data Entry", "📊 Sample Dataset"
    ])
    
    with tab1:
        st.markdown("### 📥 Download Data Template")
        st.markdown("Download the Excel template with all required marketing data schema, fill it with your data, and upload it back.")
        
        # Create template for download
        template_data = create_template_for_download()
        st.download_button(
            label="📥 Download Marketing Data Template",
            data=template_data.getvalue(),
            file_name="marketing_data_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Add some spacing for visual balance
        st.markdown("")
        st.markdown("**Template includes:**")
        st.markdown("• 8 Marketing data tables in separate sheets")
        st.markdown("• Instructions sheet with field descriptions")
        st.markdown("• Proper column headers and data types")
        
        st.markdown("### 📋 Template Structure")
        st.markdown("The template contains the following sheets:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📊 Campaigns**")
            st.markdown("• Campaign details, budgets, channels")
            st.markdown("**👥 Customers**")
            st.markdown("• Customer profiles and segments")
            st.markdown("**🌐 Website Traffic**")
            st.markdown("• Session data and user behavior")
            st.markdown("**📱 Social Media**")
            st.markdown("• Post performance metrics")
        
        with col2:
            st.markdown("**📧 Email Campaigns**")
            st.markdown("• Email performance and metrics")
            st.markdown("**📝 Content Marketing**")
            st.markdown("• Content engagement data")
            st.markdown("**🎯 Leads**")
            st.markdown("• Lead information and status")
            st.markdown("**💰 Conversions**")
            st.markdown("• Conversion tracking and revenue")
    
    with tab2:
        st.markdown("### 📤 Upload Your Data")
        st.markdown("Upload your filled Excel template:")
        
        # File upload for Excel template
        uploaded_file = st.file_uploader(
            "Upload Excel file with all marketing tables", 
            type=['xlsx', 'xls'],
            help="Upload the filled Excel template with all 8 marketing tables in separate sheets"
        )
        
        # Add helpful information
        st.markdown("")
        st.markdown("**Upload features:**")
        st.markdown("• Automatic validation of all sheets")
        st.markdown("• Import all 8 marketing tables at once")
        st.markdown("• Error checking and feedback")
        
        if uploaded_file is not None:
            try:
                # Read all sheets from the Excel file
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                
                # Check if all required sheets are present
                required_sheets = ['Campaigns', 'Customers', 'Website_Traffic', 'Social_Media', 'Email_Campaigns', 'Content_Marketing', 'Leads', 'Conversions']
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data.keys()]
                
                if missing_sheets:
                    st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                    st.info("Please ensure your Excel file contains all 8 required marketing sheets.")
                else:
                    # Load data into session state
                    st.session_state.campaigns_data = excel_data['Campaigns']
                    st.session_state.customers_data = excel_data['Customers']
                    st.session_state.website_traffic_data = excel_data['Website_Traffic']
                    st.session_state.social_media_data = excel_data['Social_Media']
                    st.session_state.email_campaigns_data = excel_data['Email_Campaigns']
                    st.session_state.content_marketing_data = excel_data['Content_Marketing']
                    st.session_state.leads_data = excel_data['Leads']
                    st.session_state.conversions_data = excel_data['Conversions']
                    
                    st.success("✅ All marketing data loaded successfully from Excel file!")
                    st.info(f"📊 Loaded {len(st.session_state.campaigns_data)} campaigns, {len(st.session_state.customers_data)} customers, {len(st.session_state.conversions_data)} conversions, and more...")
                    
                    # Show data summary
                    st.markdown("### 📊 Data Summary")
                    summary_data = {
                        'Data Type': ['Campaigns', 'Customers', 'Website Traffic', 'Social Media', 'Email Campaigns', 'Content Marketing', 'Leads', 'Conversions'],
                        'Records': [
                            len(st.session_state.campaigns_data),
                            len(st.session_state.customers_data),
                            len(st.session_state.website_traffic_data),
                            len(st.session_state.social_media_data),
                            len(st.session_state.email_campaigns_data),
                            len(st.session_state.content_marketing_data),
                            len(st.session_state.leads_data),
                            len(st.session_state.conversions_data)
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.info("Please ensure the file is a valid Excel file with the correct format.")
    
    with tab3:
        st.markdown("### 📝 Manual Data Entry")
        st.markdown("Add data manually using the forms below:")
        
        # Tabs for different data types
        data_tab1, data_tab2, data_tab3, data_tab4, data_tab5, data_tab6, data_tab7, data_tab8 = st.tabs([
            "Campaigns", "Customers", "Website Traffic", "Social Media", 
            "Email Campaigns", "Content Marketing", "Leads", "Conversions"
        ])
        
        with data_tab1:
            st.subheader("Campaigns")
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_id = st.text_input("Campaign ID", key="campaign_id_input")
                campaign_name = st.text_input("Campaign Name", key="campaign_name_input")
                start_date = st.date_input("Start Date", key="campaign_start_input")
                end_date = st.date_input("End Date", key="campaign_end_input")
                budget = st.number_input("Budget ($)", min_value=0, key="campaign_budget_input")
                channel = st.selectbox("Channel", ["Facebook", "Instagram", "Google Ads", "LinkedIn", "Twitter", "YouTube", "Email"], key="campaign_channel_input")
            
            with col2:
                campaign_type = st.selectbox("Campaign Type", ["Social Media", "Email", "PPC", "Content Marketing", "Influencer", "Affiliate"], key="campaign_type_input")
                target_audience = st.text_input("Target Audience", key="campaign_audience_input")
                status = st.selectbox("Status", ["Active", "Completed", "Paused"], key="campaign_status_input")
                objective = st.selectbox("Objective", ["Brand Awareness", "Lead Generation", "Sales", "Engagement", "Traffic"], key="campaign_objective_input")
            
            if st.button("Add Campaign", key="add_campaign_btn"):
                if campaign_id and campaign_name:
                    new_campaign = {
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'budget': budget,
                        'channel': channel,
                        'campaign_type': campaign_type,
                        'target_audience': target_audience,
                        'status': status,
                        'objective': objective
                    }
                    
                    if st.session_state.campaigns_data.empty:
                        st.session_state.campaigns_data = pd.DataFrame([new_campaign])
                    else:
                        st.session_state.campaigns_data = pd.concat([st.session_state.campaigns_data, pd.DataFrame([new_campaign])], ignore_index=True)
                    
                    st.success(f"✅ Campaign '{campaign_name}' added successfully!")
                else:
                    st.error("❌ Please fill in all required fields (Campaign ID and Name)")
            
            # Display existing data
            if not st.session_state.campaigns_data.empty:
                st.subheader("Existing Campaigns")
                display_dataframe_with_index_1(st.session_state.campaigns_data)
        
        with data_tab2:
            st.subheader("Customers")
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID", key="customer_id_input")
                customer_name = st.text_input("Customer Name", key="customer_name_input")
                email = st.text_input("Email", key="customer_email_input")
                phone = st.text_input("Phone", key="customer_phone_input")
                age = st.number_input("Age", min_value=0, max_value=120, key="customer_age_input")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="customer_gender_input")
            
            with col2:
                location = st.text_input("Location", key="customer_location_input")
                acquisition_source = st.selectbox("Acquisition Source", ["Organic Search", "Social Media", "Email", "Referral", "Paid Ads", "Direct"], key="customer_source_input")
                acquisition_date = st.date_input("Acquisition Date", key="customer_acq_date_input")
                customer_segment = st.selectbox("Customer Segment", ["High Value", "Medium Value", "Low Value", "New Customer", "Loyal Customer"], key="customer_segment_input")
                lifetime_value = st.number_input("Lifetime Value ($)", min_value=0, key="customer_clv_input")
                total_purchases = st.number_input("Total Purchases", min_value=0, key="customer_purchases_input")
            
            if st.button("Add Customer", key="add_customer_btn"):
                if customer_id and customer_name:
                    new_customer = {
                        'customer_id': customer_id,
                        'customer_name': customer_name,
                        'email': email,
                        'phone': phone,
                        'age': age,
                        'gender': gender,
                        'location': location,
                        'acquisition_source': acquisition_source,
                        'acquisition_date': acquisition_date,
                        'customer_segment': customer_segment,
                        'lifetime_value': lifetime_value,
                        'last_purchase_date': datetime.now().date(),
                        'total_purchases': total_purchases,
                        'status': 'Active'
                    }
                    
                    if st.session_state.customers_data.empty:
                        st.session_state.customers_data = pd.DataFrame([new_customer])
                    else:
                        st.session_state.customers_data = pd.concat([st.session_state.customers_data, pd.DataFrame([new_customer])], ignore_index=True)
                    
                    st.success(f"✅ Customer '{customer_name}' added successfully!")
                else:
                    st.error("❌ Please fill in all required fields (Customer ID and Name)")
            
            # Display existing data
            if not st.session_state.customers_data.empty:
                st.subheader("Existing Customers")
                display_dataframe_with_index_1(st.session_state.customers_data)
        
        with data_tab3:
            st.subheader("Website Traffic")
            col1, col2 = st.columns(2)
            
            with col1:
                session_id = st.text_input("Session ID", key="session_id_input")
                customer_id = st.text_input("Customer ID", key="traffic_customer_id_input")
                visit_date = st.date_input("Visit Date", key="visit_date_input")
                page_url = st.text_input("Page URL", key="page_url_input")
                time_on_page = st.number_input("Time on Page (seconds)", min_value=0, key="time_on_page_input")
            
            with col2:
                bounce_rate = st.slider("Bounce Rate", 0.0, 1.0, 0.5, key="bounce_rate_input")
                traffic_source = st.selectbox("Traffic Source", ["Organic", "Direct", "Referral", "Paid", "Social"], key="traffic_source_input")
                device_type = st.selectbox("Device Type", ["Desktop", "Mobile", "Tablet"], key="device_type_input")
                conversion_flag = st.checkbox("Conversion", key="conversion_flag_input")
            
            if st.button("Add Website Session", key="add_session_btn"):
                if session_id:
                    new_session = {
                        'session_id': session_id,
                        'customer_id': customer_id,
                        'visit_date': visit_date,
                        'page_url': page_url,
                        'time_on_page': time_on_page,
                        'bounce_rate': bounce_rate,
                        'traffic_source': traffic_source,
                        'device_type': device_type,
                        'conversion_flag': conversion_flag
                    }
                    
                    if st.session_state.website_traffic_data.empty:
                        st.session_state.website_traffic_data = pd.DataFrame([new_session])
                    else:
                        st.session_state.website_traffic_data = pd.concat([st.session_state.website_traffic_data, pd.DataFrame([new_session])], ignore_index=True)
                    
                    st.success(f"✅ Website session '{session_id}' added successfully!")
                else:
                    st.error("❌ Please fill in Session ID")
            
            # Display existing data
            if not st.session_state.website_traffic_data.empty:
                st.subheader("Existing Website Sessions")
                display_dataframe_with_index_1(st.session_state.website_traffic_data)
        
        with data_tab4:
            st.subheader("Social Media")
            col1, col2 = st.columns(2)
            
            with col1:
                post_id = st.text_input("Post ID", key="post_id_input")
                platform = st.selectbox("Platform", ["Facebook", "Instagram", "Twitter", "LinkedIn", "YouTube"], key="platform_input")
                post_date = st.date_input("Post Date", key="post_date_input")
                content_type = st.selectbox("Content Type", ["Image", "Video", "Text", "Story", "Reel"], key="social_media_content_type_input")
                impressions = st.number_input("Impressions", min_value=0, key="impressions_input")
            
            with col2:
                clicks = st.number_input("Clicks", min_value=0, key="social_media_clicks_input")
                likes = st.number_input("Likes", min_value=0, key="likes_input")
                shares = st.number_input("Shares", min_value=0, key="social_media_shares_input")
                comments = st.number_input("Comments", min_value=0, key="social_media_comments_input")
                reach = st.number_input("Reach", min_value=0, key="reach_input")
            
            if st.button("Add Social Media Post", key="add_post_btn"):
                if post_id:
                    engagement_rate = (likes + shares + comments) / max(reach, 1) if reach > 0 else 0
                    new_post = {
                        'post_id': post_id,
                        'platform': platform,
                        'post_date': post_date,
                        'content_type': content_type,
                        'impressions': impressions,
                        'clicks': clicks,
                        'likes': likes,
                        'shares': shares,
                        'comments': comments,
                        'reach': reach,
                        'engagement_rate': engagement_rate
                    }
                    
                    if st.session_state.social_media_data.empty:
                        st.session_state.social_media_data = pd.DataFrame([new_post])
                    else:
                        st.session_state.social_media_data = pd.concat([st.session_state.social_media_data, pd.DataFrame([new_post])], ignore_index=True)
                    
                    st.success(f"✅ Social media post '{post_id}' added successfully!")
                else:
                    st.error("❌ Please fill in Post ID")
            
            # Display existing data
            if not st.session_state.social_media_data.empty:
                st.subheader("Existing Social Media Posts")
                display_dataframe_with_index_1(st.session_state.social_media_data)
        
        with data_tab5:
            st.subheader("Email Campaigns")
            col1, col2 = st.columns(2)
            
            with col1:
                email_id = st.text_input("Email ID", key="email_id_input")
                campaign_id = st.text_input("Campaign ID", key="email_campaign_id_input")
                send_date = st.date_input("Send Date", key="email_send_date_input")
                subject_line = st.text_input("Subject Line", key="subject_line_input")
                recipients = st.number_input("Recipients", min_value=0, key="recipients_input")
            
            with col2:
                opens = st.number_input("Opens", min_value=0, key="opens_input")
                clicks = st.number_input("Clicks", min_value=0, key="email_clicks_input")
                unsubscribes = st.number_input("Unsubscribes", min_value=0, key="unsubscribes_input")
                bounces = st.number_input("Bounces", min_value=0, key="bounces_input")
                conversions = st.number_input("Conversions", min_value=0, key="email_conversions_input")
            
            if st.button("Add Email Campaign", key="add_email_btn"):
                if email_id:
                    new_email = {
                        'email_id': email_id,
                        'campaign_id': campaign_id,
                        'send_date': send_date,
                        'subject_line': subject_line,
                        'recipients': recipients,
                        'opens': opens,
                        'clicks': clicks,
                        'unsubscribes': unsubscribes,
                        'bounces': bounces,
                        'conversions': conversions
                    }
                    
                    if st.session_state.email_campaigns_data.empty:
                        st.session_state.email_campaigns_data = pd.DataFrame([new_email])
                    else:
                        st.session_state.email_campaigns_data = pd.concat([st.session_state.email_campaigns_data, pd.DataFrame([new_email])], ignore_index=True)
                    
                    st.success(f"✅ Email campaign '{email_id}' added successfully!")
                else:
                    st.error("❌ Please fill in Email ID")
            
            # Display existing data
            if not st.session_state.email_campaigns_data.empty:
                st.subheader("Existing Email Campaigns")
                display_dataframe_with_index_1(st.session_state.email_campaigns_data)
        
        with data_tab6:
            st.subheader("Content Marketing")
            col1, col2 = st.columns(2)
            
            with col1:
                content_id = st.text_input("Content ID", key="content_id_input")
                content_type = st.selectbox("Content Type", ["Blog Post", "Video", "Infographic", "Whitepaper", "Case Study", "Webinar"], key="content_marketing_content_type_input")
                publish_date = st.date_input("Publish Date", key="content_publish_date_input")
                title = st.text_input("Title", key="content_title_input")
                views = st.number_input("Views", min_value=0, key="content_views_input")
            
            with col2:
                time_on_page = st.number_input("Time on Page (seconds)", min_value=0, key="content_time_input")
                shares = st.number_input("Shares", min_value=0, key="content_shares_input")
                comments = st.number_input("Comments", min_value=0, key="content_comments_input")
                leads_generated = st.number_input("Leads Generated", min_value=0, key="leads_generated_input")
                conversions = st.number_input("Conversions", min_value=0, key="content_conversions_input")
            
            if st.button("Add Content", key="add_content_btn"):
                if content_id:
                    new_content = {
                        'content_id': content_id,
                        'content_type': content_type,
                        'publish_date': publish_date,
                        'title': title,
                        'views': views,
                        'time_on_page': time_on_page,
                        'shares': shares,
                        'comments': comments,
                        'leads_generated': leads_generated,
                        'conversions': conversions
                    }
                    
                    if st.session_state.content_marketing_data.empty:
                        st.session_state.content_marketing_data = pd.DataFrame([new_content])
                    else:
                        st.session_state.content_marketing_data = pd.concat([st.session_state.content_marketing_data, pd.DataFrame([new_content])], ignore_index=True)
                    
                    st.success(f"✅ Content '{title}' added successfully!")
                else:
                    st.error("❌ Please fill in Content ID")
            
            # Display existing data
            if not st.session_state.content_marketing_data.empty:
                st.subheader("Existing Content")
                display_dataframe_with_index_1(st.session_state.content_marketing_data)
        
        with data_tab7:
            st.subheader("Leads")
            col1, col2 = st.columns(2)
            
            with col1:
                lead_id = st.text_input("Lead ID", key="lead_id_input")
                lead_name = st.text_input("Lead Name", key="lead_name_input")
                email = st.text_input("Email", key="lead_email_input")
                company = st.text_input("Company", key="company_input")
                source = st.selectbox("Source", ["Website", "Social Media", "Email", "Referral", "Paid Ads", "Trade Show"], key="lead_source_input")
            
            with col2:
                created_date = st.date_input("Created Date", key="lead_created_date_input")
                status = st.selectbox("Status", ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"], key="lead_status_input")
                assigned_to = st.text_input("Assigned To", key="assigned_to_input")
                value = st.number_input("Value ($)", min_value=0, key="lead_value_input")
                conversion_date = st.date_input("Conversion Date", key="lead_conversion_date_input")
            
            if st.button("Add Lead", key="add_lead_btn"):
                if lead_id and lead_name:
                    new_lead = {
                        'lead_id': lead_id,
                        'lead_name': lead_name,
                        'email': email,
                        'company': company,
                        'source': source,
                        'created_date': created_date,
                        'status': status,
                        'assigned_to': assigned_to,
                        'value': value,
                        'conversion_date': conversion_date
                    }
                    
                    if st.session_state.leads_data.empty:
                        st.session_state.leads_data = pd.DataFrame([new_lead])
                    else:
                        st.session_state.leads_data = pd.concat([st.session_state.leads_data, pd.DataFrame([new_lead])], ignore_index=True)
                    
                    st.success(f"✅ Lead '{lead_name}' added successfully!")
                else:
                    st.error("❌ Please fill in all required fields (Lead ID and Name)")
            
            # Display existing data
            if not st.session_state.leads_data.empty:
                st.subheader("Existing Leads")
                display_dataframe_with_index_1(st.session_state.leads_data)
        
        with data_tab8:
            st.subheader("Conversions")
            col1, col2 = st.columns(2)
            
            with col1:
                conversion_id = st.text_input("Conversion ID", key="conversion_id_input")
                customer_id = st.text_input("Customer ID", key="conversion_customer_id_input")
                campaign_id = st.text_input("Campaign ID", key="conversion_campaign_id_input")
                conversion_date = st.date_input("Conversion Date", key="conversion_date_input")
                conversion_type = st.selectbox("Conversion Type", ["Purchase", "Sign-up", "Download", "Contact", "Demo Request"], key="conversion_type_input")
            
            with col2:
                revenue = st.number_input("Revenue ($)", min_value=0, key="revenue_input")
                attribution_source = st.selectbox("Attribution Source", ["First Touch", "Last Touch", "Multi-touch", "Time Decay"], key="attribution_source_input")
                touchpoint_count = st.number_input("Touchpoint Count", min_value=1, key="touchpoint_count_input")
            
            if st.button("Add Conversion", key="add_conversion_btn"):
                if conversion_id:
                    new_conversion = {
                        'conversion_id': conversion_id,
                        'customer_id': customer_id,
                        'campaign_id': campaign_id,
                        'conversion_date': conversion_date,
                        'conversion_type': conversion_type,
                        'revenue': revenue,
                        'attribution_source': attribution_source,
                        'touchpoint_count': touchpoint_count
                    }
                    
                    if st.session_state.conversions_data.empty:
                        st.session_state.conversions_data = pd.DataFrame([new_conversion])
                    else:
                        st.session_state.conversions_data = pd.concat([st.session_state.conversions_data, pd.DataFrame([new_conversion])], ignore_index=True)
                    
                    st.success(f"✅ Conversion '{conversion_id}' added successfully!")
                else:
                    st.error("❌ Please fill in Conversion ID")
            
            # Display existing data
            if not st.session_state.conversions_data.empty:
                st.subheader("Existing Conversions")
                display_dataframe_with_index_1(st.session_state.conversions_data)
    
    with tab4:
        st.markdown("### 📊 Sample Dataset")
        st.markdown("Load sample marketing data to explore the dashboard features:")
        
        if st.button("🚀 Load Sample Marketing Dataset", key="load_sample_btn", use_container_width=True):
            # Generate comprehensive sample data
            sample_campaigns = pd.DataFrame({
                'campaign_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008'],
                'campaign_name': ['Summer Sale 2024', 'Brand Awareness Q1', 'Lead Generation Campaign', 'Holiday Promotion', 'Product Launch', 'Email Newsletter Q1', 'Content Marketing Series', 'Social Media Boost'],
                'start_date': ['2024-06-01', '2024-01-01', '2024-03-01', '2024-11-01', '2024-09-01', '2024-01-01', '2024-02-01', '2024-04-01'],
                'end_date': ['2024-08-31', '2024-03-31', '2024-05-31', '2024-12-31', '2024-10-31', '2024-03-31', '2024-05-31', '2024-06-30'],
                'budget': [50000, 30000, 25000, 40000, 60000, 15000, 20000, 18000],
                'channel': ['Facebook', 'Google Ads', 'LinkedIn', 'Email', 'Instagram', 'Email', 'Content Hub', 'Social Media'],
                'campaign_type': ['Social Media', 'PPC', 'B2B', 'Email', 'Social Media', 'Email', 'Content Marketing', 'Social Media'],
                'target_audience': ['General', 'B2B', 'Professionals', 'Existing Customers', 'Young Adults', 'Subscribers', 'Professionals', 'General'],
                'status': ['Active', 'Completed', 'Completed', 'Active', 'Active', 'Completed', 'Completed', 'Active'],
                'objective': ['Sales', 'Brand Awareness', 'Lead Generation', 'Sales', 'Brand Awareness', 'Engagement', 'Thought Leadership', 'Brand Awareness']
            })
            
            sample_customers = pd.DataFrame({
                'customer_id': ['CU001', 'CU002', 'CU003', 'CU004', 'CU005', 'CU006', 'CU007', 'CU008', 'CU009', 'CU010'],
                'customer_name': ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson', 'David Brown', 'Emma Taylor', 'Alex Chen', 'Maria Garcia', 'Tom Wilson', 'Anna Lee'],
                'email': ['john@email.com', 'sarah@email.com', 'mike@email.com', 'lisa@email.com', 'david@email.com', 'emma@email.com', 'alex@email.com', 'maria@email.com', 'tom@email.com', 'anna@email.com'],
                'phone': ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105', '555-0106', '555-0107', '555-0108', '555-0109', '555-0110'],
                'age': [35, 28, 42, 31, 39, 26, 45, 33, 29, 37],
                'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
                'location': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Seattle', 'Boston', 'Miami', 'Denver', 'Austin'],
                'acquisition_source': ['Organic Search', 'Social Media', 'Email', 'Paid Ads', 'Referral', 'Content Marketing', 'LinkedIn', 'Facebook', 'Google Ads', 'Email'],
                'acquisition_date': ['2024-01-15', '2024-02-20', '2024-01-10', '2024-03-05', '2024-02-15', '2024-02-01', '2024-01-25', '2024-03-10', '2024-02-28', '2024-01-20'],
                'customer_segment': ['High Value', 'Medium Value', 'High Value', 'Low Value', 'Medium Value', 'Medium Value', 'High Value', 'Low Value', 'Medium Value', 'High Value'],
                'lifetime_value': [2500, 1200, 3000, 800, 1500, 1800, 2800, 950, 1300, 2200],
                'last_purchase_date': ['2024-05-20', '2024-04-15', '2024-05-10', '2024-03-20', '2024-04-25', '2024-05-05', '2024-05-15', '2024-04-10', '2024-05-01', '2024-05-18'],
                'total_purchases': [8, 4, 12, 2, 6, 5, 10, 3, 7, 9],
                'status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active']
            })
            
            # Generate conversions data (CRITICAL for analysis)
            sample_conversions = pd.DataFrame({
                'conversion_id': ['CONV001', 'CONV002', 'CONV003', 'CONV004', 'CONV005', 'CONV006', 'CONV007', 'CONV008', 'CONV009', 'CONV010'],
                'customer_id': ['CU001', 'CU002', 'CU003', 'CU004', 'CU005', 'CU006', 'CU007', 'CU008', 'CU009', 'CU010'],
                'campaign_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C001', 'C002', 'C003', 'C004', 'C005'],
                'conversion_date': ['2024-06-15', '2024-02-15', '2024-04-20', '2024-11-15', '2024-09-20', '2024-06-20', '2024-02-25', '2024-04-25', '2024-11-20', '2024-09-25'],
                'conversion_type': ['Purchase', 'Sign-up', 'Download', 'Purchase', 'Sign-up', 'Purchase', 'Sign-up', 'Download', 'Purchase', 'Sign-up'],
                'revenue': [150, 0, 0, 200, 0, 175, 0, 0, 225, 0],
                'attribution_source': ['First Touch', 'Last Touch', 'Multi-touch', 'First Touch', 'Last Touch', 'Multi-touch', 'First Touch', 'Last Touch', 'Multi-touch', 'First Touch'],
                'touchpoint_count': [3, 2, 4, 2, 3, 4, 2, 5, 3, 2]
            })
            
            # Generate leads data (required for forecasting)
            sample_leads = pd.DataFrame({
                'lead_id': ['L001', 'L002', 'L003', 'L004', 'L005', 'L006', 'L007', 'L008', 'L009', 'L010'],
                'lead_name': ['Tech Startup Inc', 'Marketing Agency XYZ', 'E-commerce Store', 'Consulting Firm', 'Healthcare Provider', 'Financial Services', 'Education Institute', 'Manufacturing Co', 'Retail Chain', 'Software Company'],
                'email': ['contact@techstartup.com', 'info@marketingagency.com', 'sales@ecommerce.com', 'hello@consulting.com', 'info@healthcare.com', 'contact@financial.com', 'admissions@education.com', 'sales@manufacturing.com', 'info@retail.com', 'hello@software.com'],
                'company': ['Tech Startup Inc', 'Marketing Agency XYZ', 'E-commerce Store', 'Consulting Firm', 'Healthcare Provider', 'Financial Services', 'Education Institute', 'Manufacturing Co', 'Retail Chain', 'Software Company'],
                'source': ['Website', 'LinkedIn', 'Google Ads', 'Referral', 'Content Marketing', 'Social Media', 'Email', 'Trade Show', 'Organic Search', 'PPC'],
                'created_date': ['2024-01-10', '2024-02-05', '2024-01-20', '2024-02-15', '2024-01-30', '2024-02-10', '2024-01-25', '2024-02-20', '2024-02-01', '2024-01-15'],
                'status': ['Qualified', 'New', 'Qualified', 'New', 'Qualified', 'New', 'Qualified', 'New', 'Qualified', 'New'],
                'assigned_to': ['Sales Team A', 'Sales Team B', 'Sales Team A', 'Sales Team B', 'Sales Team A', 'Sales Team B', 'Sales Team A', 'Sales Team B', 'Sales Team A', 'Sales Team B'],
                'value': [5000, 3000, 8000, 6000, 4000, 7000, 3500, 9000, 2500, 12000],
                'conversion_date': ['2024-02-15', '2024-03-20', '2024-02-25', '2024-03-25', '2024-02-28', '2024-03-30', '2024-03-05', '2024-04-05', '2024-03-10', '2024-02-20']
            })
            
            # Generate content marketing data (required for content analysis)
            sample_content_marketing = pd.DataFrame({
                'content_id': ['CONT001', 'CONT002', 'CONT003', 'CONT004', 'CONT005', 'CONT006', 'CONT007', 'CONT008'],
                'title': ['Ultimate Guide to Digital Marketing', '10 SEO Tips for 2024', 'Social Media Strategy Guide', 'Email Marketing Best Practices', 'Content Marketing ROI', 'Brand Building Strategies', 'Customer Journey Mapping', 'Marketing Analytics Guide'],
                'content_type': ['Blog Post', 'Infographic', 'Video', 'Whitepaper', 'Case Study', 'Blog Post', 'E-book', 'Webinar'],
                'publish_date': ['2024-01-15', '2024-02-01', '2024-02-15', '2024-03-01', '2024-03-15', '2024-04-01', '2024-04-15', '2024-05-01'],
                'channel': ['Website', 'Social Media', 'YouTube', 'Website', 'Website', 'Website', 'Website', 'Zoom'],
                'views': [2500, 1800, 3200, 1200, 900, 2100, 1500, 800],
                'shares': [180, 120, 250, 80, 60, 150, 100, 45],
                'comments': [45, 32, 68, 18, 25, 38, 42, 35],
                'leads_generated': [25, 18, 35, 12, 8, 22, 15, 10],
                'engagement_rate': [0.08, 0.12, 0.15, 0.06, 0.10, 0.09, 0.11, 0.18],
                'conversions': [45, 32, 68, 18, 25, 38, 42, 35],
                'time_on_page': [180, 120, 240, 90, 75, 150, 110, 60],
                'author': ['Marketing Team', 'SEO Specialist', 'Content Creator', 'Marketing Manager', 'Analytics Team', 'Brand Manager', 'UX Team', 'Marketing Director']
            })
            
            # Generate social media data
            sample_social_media = pd.DataFrame({
                'post_id': ['SOC001', 'SOC002', 'SOC003', 'SOC004', 'SOC005', 'SOC006', 'SOC007', 'SOC008'],
                'platform': ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'Facebook', 'Instagram', 'LinkedIn', 'Twitter'],
                'post_type': ['Image', 'Video', 'Article', 'Text', 'Carousel', 'Story', 'Poll', 'Text'],
                'publish_date': ['2024-01-15', '2024-01-20', '2024-01-25', '2024-02-01', '2024-02-05', '2024-02-10', '2024-02-15', '2024-02-20'],
                'content_type': ['Product Promotion', 'Brand Awareness', 'Thought Leadership', 'Customer Service', 'Product Demo', 'Behind the Scenes', 'Industry News', 'Customer Testimonial'],
                'impressions': [5000, 6500, 3500, 2500, 5500, 4500, 3000, 2000],
                'clicks': [150, 200, 80, 45, 180, 120, 95, 60],
                'shares': [25, 35, 15, 8, 30, 20, 12, 10],
                'comments': [18, 28, 12, 6, 22, 15, 8, 7],
                'likes': [120, 180, 65, 35, 150, 100, 75, 45],
                'reach': [2500, 3200, 1800, 1200, 2800, 2400, 1600, 1000],
                'engagement_rate': [0.072, 0.089, 0.089, 0.075, 0.075, 0.073, 0.094, 0.112]
            })
            
            # Generate email campaign data
            sample_email_campaigns = pd.DataFrame({
                'email_id': ['EMAIL001', 'EMAIL002', 'EMAIL003', 'EMAIL004', 'EMAIL005', 'EMAIL006'],
                'campaign_name': ['Weekly Newsletter', 'Product Launch', 'Holiday Sale', 'Customer Onboarding', 'Abandoned Cart', 'Welcome Series'],
                'subject_line': ['This Week in Marketing', 'New Product Launch!', 'Holiday Special Offers', 'Welcome to Our Platform', 'Complete Your Purchase', 'Welcome to the Family'],
                'send_date': ['2024-01-15', '2024-02-01', '2024-03-01', '2024-01-20', '2024-02-15', '2024-01-25'],
                'recipients': [5000, 3000, 8000, 1200, 2500, 2000],
                'opens': [1250, 900, 2000, 360, 500, 600],
                'clicks': [375, 270, 600, 108, 150, 180],
                'conversions': [75, 54, 120, 22, 30, 36],
                'unsubscribes': [25, 9, 40, 4, 10, 6],
                'bounces': [100, 45, 200, 12, 50, 30],
                'bounce_rate': [0.02, 0.015, 0.025, 0.01, 0.02, 0.015]
            })
            
            # Generate website traffic data
            sample_website_traffic = pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', '2024-01-07', '2024-01-08'],
                'customer_id': ['CU001', 'CU002', 'CU003', 'CU004', 'CU005', 'CU006', 'CU007', 'CU008'],
                'page_views': [1200, 1350, 1100, 1400, 1250, 1300, 1150, 1450],
                'unique_visitors': [800, 900, 750, 950, 850, 900, 800, 1000],
                'bounce_rate': [0.35, 0.32, 0.38, 0.30, 0.33, 0.31, 0.36, 0.29],
                'avg_session_duration': [180, 195, 165, 210, 185, 200, 170, 220],
                'conversion_rate': [0.025, 0.028, 0.022, 0.030, 0.026, 0.029, 0.024, 0.032],
                'traffic_source': ['Organic Search', 'Direct', 'Social Media', 'Paid Ads', 'Referral', 'Email', 'Organic Search', 'Direct'],
                'conversion_flag': [1, 1, 0, 1, 0, 1, 0, 1],
                'session_id': ['SESS001', 'SESS002', 'SESS003', 'SESS004', 'SESS005', 'SESS006', 'SESS007', 'SESS008'],
                'time_on_page': [180, 195, 165, 210, 185, 200, 170, 220],
                'device_type': ['Mobile', 'Desktop', 'Mobile', 'Desktop', 'Mobile', 'Desktop', 'Mobile', 'Desktop']
            })
            
            # Load all sample data into session state
            st.session_state.campaigns_data = sample_campaigns
            st.session_state.customers_data = sample_customers
            st.session_state.conversions_data = sample_conversions
            st.session_state.leads_data = sample_leads
            st.session_state.content_marketing_data = sample_content_marketing
            st.session_state.social_media_data = sample_social_media
            st.session_state.email_campaigns_data = sample_email_campaigns
            st.session_state.website_traffic_data = sample_website_traffic
            
            st.success("✅ Comprehensive sample marketing dataset loaded successfully!")
            st.info("📊 Sample data now includes: 8 campaigns, 10 customers, 10 conversions, 10 leads, 8 content pieces, 8 social posts, 6 email campaigns, and 8 website traffic records. All analysis sections are now fully functional!")
            
            # Show comprehensive data preview
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sample Campaigns & Conversions")
                st.dataframe(sample_campaigns, use_container_width=True)
                st.dataframe(sample_conversions, use_container_width=True)
            
            with col2:
                st.subheader("Sample Customers & Leads")
                st.dataframe(sample_customers, use_container_width=True)
                st.dataframe(sample_leads, use_container_width=True)
        
        st.markdown("### 📈 What You Can Do With Sample Data")
        st.markdown("• **Campaign Performance Analysis** - Analyze campaign metrics, ROI, and conversion tracking")
        st.markdown("• **Customer Analysis** - Understand customer segments, behavior, and lifetime value")
        st.markdown("• **Market Analysis** - Analyze market trends, customer acquisition, and competitive insights")
        st.markdown("• **Content Marketing Analysis** - Measure content performance, engagement, and ROI")
        st.markdown("• **Digital Marketing Analytics** - Track social media, email, and website performance")
        st.markdown("• **Brand Awareness Metrics** - Measure brand visibility, reach, and engagement")
        st.markdown("• **Product Marketing Analysis** - Analyze product performance and customer journey")
        st.markdown("• **Customer Journey Mapping** - Track touchpoints and conversion paths")
        st.markdown("• **Marketing Forecasting** - Test predictive analytics with comprehensive data")
        st.markdown("• **Channel Analysis** - Compare performance across all marketing channels")
        
        st.markdown("### 🔄 Reset Data")
        if st.button("🗑️ Clear All Data", key="clear_data_btn", use_container_width=True):
            st.session_state.campaigns_data = pd.DataFrame()
            st.session_state.customers_data = pd.DataFrame()
            st.session_state.website_traffic_data = pd.DataFrame()
            st.session_state.social_media_data = pd.DataFrame()
            st.session_state.email_campaigns_data = pd.DataFrame()
            st.session_state.content_marketing_data = pd.DataFrame()
            st.session_state.leads_data = pd.DataFrame()
            st.session_state.conversions_data = pd.DataFrame()
            st.success("✅ All data cleared successfully!")

def show_campaign_performance():
    """Display campaign performance analysis"""
    st.header("📈 Campaign Performance Analysis")
    
    if st.session_state.campaigns_data.empty or st.session_state.conversions_data.empty:
        st.warning("Please add campaign and conversion data first in the Data Input section.")
        return
    
    # Calculate campaign performance summary
    campaign_performance = calculate_campaign_performance_summary(
        st.session_state.campaigns_data, 
        st.session_state.conversions_data
    )
    
    # Summary Dashboard with professional styling
    total_revenue = campaign_performance['revenue'].sum()
    total_budget = campaign_performance['budget'].sum()
    total_conversions = campaign_performance['conversions'].sum()
    avg_roi = campaign_performance['roi'].mean()
    avg_cpa = campaign_performance['cpa'].mean()
    
    st.markdown("""
    <div class="summary-dashboard">
        <h3 style="color: white; margin: 0; text-align: center;">📈 Campaign Performance Summary Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced summary metrics with color coding
    summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
    
    with summary_col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Revenue</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${total_revenue:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown(f"""
        <div class="metric-card-red">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Budget</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${total_budget:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown(f"""
        <div class="metric-card-orange">
            <h4 style="color: white; margin: 0; font-size: 14px;">Total Conversions</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{total_conversions:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown(f"""
        <div class="metric-card-teal">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg ROI</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">{avg_roi:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col5:
        st.markdown(f"""
        <div class="metric-card-green">
            <h4 style="color: white; margin: 0; font-size: 14px;">Avg CPA</h4>
            <h2 style="color: white; margin: 5px 0; font-size: 24px;">${avg_cpa:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 ROI by Campaign Type")
        roi_by_type = campaign_performance.groupby('campaign_type')['roi'].mean().reset_index()
        if not roi_by_type.empty:
            # Enhanced metric with color coding
            avg_roi_value = roi_by_type['roi'].mean()
            color = "🟢" if avg_roi_value >= 20 else "🟡" if avg_roi_value >= 10 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3c72; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Average ROI: {avg_roi_value:.1f}%</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced bar chart with professional colors
            fig_roi = px.bar(
                roi_by_type, 
                x='campaign_type', 
                y='roi', 
                title='ROI by Campaign Type',
                color='roi',
                color_continuous_scale='Blues',
                text='roi'
            )
            fig_roi.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_tickangle=-45,
                showlegend=False
            )
            fig_roi.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            st.plotly_chart(fig_roi, use_container_width=True, key="roi_campaign_chart")
            
            with st.expander("📊 ROI Data"):
                display_dataframe_with_index_1(roi_by_type)
    
    with col2:
        st.subheader("💰 CPA by Campaign Type")
        cpa_by_type = campaign_performance.groupby('campaign_type')['cpa'].mean().reset_index()
        if not cpa_by_type.empty:
            # Enhanced metric with color coding
            avg_cpa_value = cpa_by_type['cpa'].mean()
            color = "🟢" if avg_cpa_value <= 50 else "🟡" if avg_cpa_value <= 100 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #E63946; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Average CPA: ${avg_cpa_value:.0f}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced bar chart with professional colors
            fig_cpa = px.bar(
                cpa_by_type, 
                x='campaign_type', 
                y='cpa', 
                title='Cost Per Acquisition by Campaign Type',
                color='cpa',
                color_continuous_scale='Reds',
                text='cpa'
            )
            fig_cpa.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_tickangle=-45,
                showlegend=False
            )
            fig_cpa.update_traces(
                texttemplate='$%{text:.0f}',
                textposition='outside'
            )
            st.plotly_chart(fig_cpa, use_container_width=True, key="cpa_campaign_chart")
            
            with st.expander("📊 CPA Data"):
                display_dataframe_with_index_1(cpa_by_type)
    
    # Top performing campaigns
    st.subheader("🏆 Top Performing Campaigns")
    
    if not campaign_performance.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 campaigns by ROI
            top_roi_campaigns = campaign_performance.nlargest(10, 'roi')[['campaign_name', 'roi', 'revenue', 'budget', 'conversions']]
            st.markdown("**Top 10 Campaigns by ROI:**")
            
            # Enhanced metric with color coding
            best_roi = top_roi_campaigns['roi'].iloc[0] if not top_roi_campaigns.empty else 0
            color = "🟢" if best_roi >= 50 else "🟡" if best_roi >= 20 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1A936F; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Best ROI: {best_roi:.1f}%</h3>
            </div>
            """, unsafe_allow_html=True)
            
            display_dataframe_with_index_1(top_roi_campaigns)
        
        with col2:
            # Top 10 campaigns by revenue
            top_revenue_campaigns = campaign_performance.nlargest(10, 'revenue')[['campaign_name', 'revenue', 'roi', 'budget', 'conversions']]
            st.markdown("**Top 10 Campaigns by Revenue:**")
            
            # Enhanced metric with color coding
            best_revenue = top_revenue_campaigns['revenue'].iloc[0] if not top_revenue_campaigns.empty else 0
            color = "🟢" if best_revenue >= 100000 else "🟡" if best_revenue >= 50000 else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #FF6B35; margin: 10px 0;">
                <h3 style="margin: 0; color: #333;">{color} Best Revenue: ${best_revenue:,.0f}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            display_dataframe_with_index_1(top_revenue_campaigns)
    
    # Campaign efficiency analysis
    st.subheader("⚡ Campaign Efficiency Analysis")
    
    if not campaign_performance.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget vs Revenue scatter plot
            fig_scatter = px.scatter(
                campaign_performance,
                x='budget',
                y='revenue',
                size='conversions',
                color='campaign_type',
                hover_data=['campaign_name'],
                title="Budget vs Revenue by Campaign Type",
                color_discrete_sequence=['#FF6B35', '#004E89', '#1A936F', '#C6DABF', '#2E86AB', '#E63946', '#457B9D']
            )
            fig_scatter.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_title="Budget ($)",
                yaxis_title="Revenue ($)",
                showlegend=True,
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            st.plotly_chart(fig_scatter, use_container_width=True, key="budget_revenue_scatter")
        
        with col2:
            # Conversion rate by channel
            if 'channel' in campaign_performance.columns:
                channel_performance = campaign_performance.groupby('channel').agg({
                    'conversions': 'sum',
                    'budget': 'sum',
                    'revenue': 'sum'
                }).reset_index()
                
                channel_performance['conversion_rate'] = (channel_performance['conversions'] / channel_performance['budget']) * 100
                
                # Enhanced metric with color coding
                best_conversion_rate = channel_performance['conversion_rate'].max() if not channel_performance.empty else 0
                color = "🟢" if best_conversion_rate >= 5 else "🟡" if best_conversion_rate >= 2 else "🔴"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2E86AB; margin: 10px 0;">
                    <h3 style="margin: 0; color: #333;">{color} Best Conversion Rate: {best_conversion_rate:.2f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                fig_channel = px.bar(
                    channel_performance,
                    x='channel',
                    y='conversion_rate',
                    title="Conversion Rate by Channel",
                    color='conversion_rate',
                    color_continuous_scale='Blues',
                    text='conversion_rate'
                )
                fig_channel.update_layout(
                    title_font_size=18,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                fig_channel.update_traces(
                    texttemplate='%{text:.2f}%',
                    textposition='outside'
                )
                st.plotly_chart(fig_channel, use_container_width=True, key="channel_conversion_chart")
                
                with st.expander("📊 Channel Performance Data"):
                    display_dataframe_with_index_1(channel_performance)
    
    # Detailed campaign table
    st.subheader("📋 Campaign Performance Details")
    
    if not campaign_performance.empty:
        # Add calculated metrics
        display_columns = ['campaign_name', 'campaign_type', 'channel', 'budget', 'revenue', 'roi', 'cpa', 'conversions']
        display_df = campaign_performance[display_columns].copy()
        display_df['roi'] = display_df['roi'].round(1)
        display_df['cpa'] = display_df['cpa'].round(0)
        
        # Enhanced metric with color coding
        total_campaigns = len(display_df)
        profitable_campaigns = len(display_df[display_df['roi'] > 0])
        success_rate = (profitable_campaigns / total_campaigns) * 100 if total_campaigns > 0 else 0
        color = "🟢" if success_rate >= 70 else "🟡" if success_rate >= 50 else "🔴"
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3c72; margin: 10px 0;">
            <h3 style="margin: 0; color: #333;">{color} Campaign Success Rate: {success_rate:.1f}% ({profitable_campaigns}/{total_campaigns} campaigns profitable)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        display_dataframe_with_index_1(display_df)

def show_customer_analysis():
    """Display customer analysis"""
    st.title("👥 Customer Analysis")
    st.markdown("---")
    
    if st.session_state.customers_data.empty:
        st.warning("⚠️ Customer data required for this analysis.")
        return
    
    # Customer segmentation analysis
    st.subheader("🎯 Customer Segmentation")
    
    if 'customer_segment' in st.session_state.customers_data.columns:
        segment_analysis = segment_customers(st.session_state.customers_data, 'customer_segment')
        
        if not segment_analysis.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer count by segment
                fig_segments = px.pie(
                    values=segment_analysis['customer_count'],
                    names=segment_analysis.index,
                    title="Customer Distribution by Segment"
                )
                st.plotly_chart(fig_segments, use_container_width=True)
            
            with col2:
                # Average CLV by segment
                fig_clv = px.bar(
                    segment_analysis.reset_index(),
                    x='customer_segment',
                    y='lifetime_value',
                    title="Average Customer Lifetime Value by Segment",
                    labels={'lifetime_value': 'Average CLV ($)', 'customer_segment': 'Customer Segment'}
                )
                st.plotly_chart(fig_clv, use_container_width=True)
    
    # Customer acquisition analysis
    st.subheader("📈 Customer Acquisition Analysis")
    
    if 'acquisition_source' in st.session_state.customers_data.columns:
        acquisition_analysis = calculate_acquisition_source_analysis(st.session_state.customers_data)
        
        if not acquisition_analysis.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Customers by acquisition source
                fig_source = px.bar(
                    acquisition_analysis.reset_index(),
                    x='acquisition_source',
                    y='new_customers',
                    title="New Customers by Acquisition Source",
                    labels={'new_customers': 'New Customers', 'acquisition_source': 'Acquisition Source'}
                )
                st.plotly_chart(fig_source, use_container_width=True)
            
            with col2:
                # CLV by acquisition source
                fig_source_clv = px.bar(
                    acquisition_analysis.reset_index(),
                    x='acquisition_source',
                    y='lifetime_value',
                    title="Average CLV by Acquisition Source",
                    labels={'lifetime_value': 'Average CLV ($)', 'acquisition_source': 'Acquisition Source'}
                )
                st.plotly_chart(fig_source_clv, use_container_width=True)
    
    # Customer demographics
    st.subheader("👤 Customer Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'age' in st.session_state.customers_data.columns:
            fig_age = px.histogram(
                st.session_state.customers_data,
                x='age',
                nbins=20,
                title="Customer Age Distribution",
                labels={'age': 'Age', 'count': 'Number of Customers'}
            )
            st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        if 'gender' in st.session_state.customers_data.columns:
            gender_counts = st.session_state.customers_data['gender'].value_counts()
            fig_gender = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Customer Gender Distribution"
            )
            st.plotly_chart(fig_gender, use_container_width=True)
    
    # Customer lifetime value analysis
    st.subheader("💰 Customer Lifetime Value Analysis")
    
    if 'lifetime_value' in st.session_state.customers_data.columns:
        # CLV distribution
        fig_clv_dist = px.histogram(
            st.session_state.customers_data,
            x='lifetime_value',
            nbins=20,
            title="Customer Lifetime Value Distribution",
            labels={'lifetime_value': 'CLV ($)', 'count': 'Number of Customers'}
        )
        st.plotly_chart(fig_clv_dist, use_container_width=True)
        
        # CLV statistics
        clv_stats = st.session_state.customers_data['lifetime_value'].describe()
        st.markdown("**CLV Statistics:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean CLV", f"${clv_stats['mean']:.0f}")
        with col2:
            st.metric("Median CLV", f"${clv_stats['50%']:.0f}")
        with col3:
            st.metric("Max CLV", f"${clv_stats['max']:.0f}")
        with col4:
            st.metric("Min CLV", f"${clv_stats['min']:.0f}")
    
    # Repeat customer analysis
    st.subheader("🔄 Repeat Customer Analysis")
    
    if 'total_purchases' in st.session_state.customers_data.columns:
        repeat_rate = calculate_repeat_customer_rate(st.session_state.customers_data)
        st.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")
        
        # Purchase frequency distribution
        fig_purchases = px.histogram(
            st.session_state.customers_data,
            x='total_purchases',
            nbins=15,
            title="Customer Purchase Frequency Distribution",
            labels={'total_purchases': 'Number of Purchases', 'count': 'Number of Customers'}
        )
        st.plotly_chart(fig_purchases, use_container_width=True)

def show_market_analysis():
    """Display market analysis"""
    st.title("🌍 Market Analysis")
    st.markdown("---")
    
    if st.session_state.conversions_data.empty or st.session_state.customers_data.empty:
        st.warning("⚠️ Conversion and customer data required for market analysis.")
        return
    
    # Market share analysis
    st.subheader("📊 Market Share Analysis")
    
    company_revenue = st.session_state.conversions_data['revenue'].sum()
    total_customers = len(st.session_state.customers_data)
    
    # For demonstration, assume total market size
    total_market_size = company_revenue * 10  # Example: company has 10% market share
    market_share = calculate_market_share(company_revenue, total_market_size)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Company Revenue", f"${company_revenue:,.0f}")
    with col2:
        st.metric("Estimated Market Size", f"${total_market_size:,.0f}")
    with col3:
        st.metric("Market Share", f"{market_share:.1f}%")
    with col4:
        st.metric("Total Customers", f"{total_customers:,}")
    
    # Revenue trend analysis
    st.subheader("📈 Revenue Trend Analysis")
    
    if not st.session_state.conversions_data.empty:
        conversions_data = st.session_state.conversions_data.copy()
        conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
        conversions_data['month'] = conversions_data['conversion_date'].dt.to_period('M')
        
        monthly_revenue = conversions_data.groupby('month')['revenue'].sum().reset_index()
        monthly_revenue['month'] = monthly_revenue['month'].astype(str)
        
        fig_revenue_trend = px.line(
            monthly_revenue,
            x='month',
            y='revenue',
            title="Monthly Revenue Trend",
            labels={'revenue': 'Revenue ($)', 'month': 'Month'}
        )
        st.plotly_chart(fig_revenue_trend, use_container_width=True)
    
    # Geographical performance
    st.subheader("🗺️ Geographical Performance")
    
    if 'location' in st.session_state.customers_data.columns:
        geo_performance = st.session_state.customers_data.groupby('location').agg({
            'customer_id': 'count',
            'lifetime_value': 'sum'
        }).rename(columns={'customer_id': 'customers', 'lifetime_value': 'total_revenue'})
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_geo_customers = px.bar(
                geo_performance.reset_index(),
                x='location',
                y='customers',
                title="Customers by Location",
                labels={'customers': 'Number of Customers', 'location': 'Location'}
            )
            st.plotly_chart(fig_geo_customers, use_container_width=True)
        
        with col2:
            fig_geo_revenue = px.bar(
                geo_performance.reset_index(),
                x='location',
                y='total_revenue',
                title="Revenue by Location",
                labels={'total_revenue': 'Total Revenue ($)', 'location': 'Location'}
            )
            st.plotly_chart(fig_geo_revenue, use_container_width=True)
    
    # Market penetration analysis
    st.subheader("🎯 Market Penetration Analysis")
    
    if not st.session_state.customers_data.empty:
        # Calculate market penetration by segment
        segment_penetration = st.session_state.customers_data.groupby('customer_segment').agg({
            'customer_id': 'count',
            'lifetime_value': 'mean'
        }).rename(columns={'customer_id': 'customer_count', 'lifetime_value': 'avg_lifetime_value'})
        
        fig_segment_penetration = px.bar(
            segment_penetration.reset_index(),
            x='customer_segment',
            y='customer_count',
            title="Market Penetration by Customer Segment",
            labels={'customer_count': 'Number of Customers', 'customer_segment': 'Customer Segment'}
        )
        st.plotly_chart(fig_segment_penetration, use_container_width=True)
    
    # Competitive analysis framework
    st.subheader("🏆 Competitive Analysis Framework")
    
    # Example competitive metrics
    competitive_data = {
        'Metric': ['Market Share', 'Customer Acquisition Cost', 'Customer Lifetime Value', 'Conversion Rate'],
        'Your Company': [market_share, 150, st.session_state.customers_data['lifetime_value'].mean(), 2.5],
        'Competitor A': [market_share * 0.8, 180, st.session_state.customers_data['lifetime_value'].mean() * 0.9, 2.0],
        'Competitor B': [market_share * 1.2, 120, st.session_state.customers_data['lifetime_value'].mean() * 1.1, 3.0]
    }
    competitive_df = pd.DataFrame(competitive_data)
    
    st.markdown("**Competitive Benchmarking:**")
    display_dataframe_with_index_1(competitive_df)
    
    # Market opportunity analysis
    st.subheader("💡 Market Opportunity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Addressable Market", f"${total_market_size:,.0f}")
        st.metric("Current Market Share", f"{market_share:.1f}%")
        st.metric("Growth Potential", f"{(100 - market_share):.1f}%")
    
    with col2:
        st.metric("Customer Acquisition Rate", f"{len(st.session_state.customers_data) / 12:.0f}/month")
        st.metric("Average Customer Value", f"${st.session_state.customers_data['lifetime_value'].mean():.0f}")
        st.metric("Market Growth Rate", "5.2%")

def show_content_marketing():
    """Display content marketing analysis"""
    st.title("📝 Content Marketing Analysis")
    st.markdown("---")
    
    if st.session_state.content_marketing_data.empty:
        st.warning("⚠️ Content marketing data required for this analysis.")
        return
    
    # Content engagement overview
    st.subheader("📊 Content Engagement Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_views = st.session_state.content_marketing_data['views'].sum()
        st.metric("Total Views", f"{total_views:,}")
    
    with col2:
        total_shares = st.session_state.content_marketing_data['shares'].sum()
        st.metric("Total Shares", f"{total_shares:,}")
    
    with col3:
        total_leads = st.session_state.content_marketing_data['leads_generated'].sum()
        st.metric("Leads Generated", f"{total_leads:,}")
    
    with col4:
        total_conversions = st.session_state.content_marketing_data['conversions'].sum()
        st.metric("Conversions", f"{total_conversions:,}")
    
    # Content performance by type
    st.subheader("📈 Content Performance by Type")
    
    content_performance = st.session_state.content_marketing_data.groupby('content_type').agg({
        'views': 'sum',
        'shares': 'sum',
        'comments': 'sum',
        'leads_generated': 'sum',
        'conversions': 'sum',
        'time_on_page': 'mean'
    }).reset_index()
    
    # Calculate engagement rate
    content_performance['engagement_rate'] = (
        (content_performance['shares'] + content_performance['comments']) / content_performance['views']
    ) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_content_views = px.bar(
            content_performance,
            x='content_type',
            y='views',
            title="Total Views by Content Type",
            labels={'views': 'Total Views', 'content_type': 'Content Type'}
        )
        st.plotly_chart(fig_content_views, use_container_width=True)
    
    with col2:
        fig_content_engagement = px.bar(
            content_performance,
            x='content_type',
            y='engagement_rate',
            title="Engagement Rate by Content Type",
            labels={'engagement_rate': 'Engagement Rate (%)', 'content_type': 'Content Type'}
        )
        st.plotly_chart(fig_content_engagement, use_container_width=True)
    
    # Top performing content
    st.subheader("🏆 Top Performing Content")
    
    # Top content by views
    top_views = st.session_state.content_marketing_data.nlargest(10, 'views')[
        ['title', 'content_type', 'views', 'shares', 'leads_generated', 'conversions']
    ]
    st.markdown("**Top 10 Content by Views:**")
    display_dataframe_with_index_1(top_views)
    
    # Top content by leads generated
    top_leads = st.session_state.content_marketing_data.nlargest(10, 'leads_generated')[
        ['title', 'content_type', 'leads_generated', 'views', 'conversions']
    ]
    st.markdown("**Top 10 Content by Leads Generated:**")
    display_dataframe_with_index_1(top_leads)
    
    # Content engagement trends
    st.subheader("📈 Content Engagement Trends")
    
    if 'publish_date' in st.session_state.content_marketing_data.columns:
        # Convert publish_date to datetime if it's not already
        content_data = st.session_state.content_marketing_data.copy()
        content_data['publish_date'] = pd.to_datetime(content_data['publish_date'])
        content_data['month'] = content_data['publish_date'].dt.to_period('M')
        
        monthly_performance = content_data.groupby('month').agg({
            'views': 'sum',
            'shares': 'sum',
            'leads_generated': 'sum'
        }).reset_index()
        monthly_performance['month'] = monthly_performance['month'].astype(str)
        
        fig_trends = px.line(
            monthly_performance,
            x='month',
            y=['views', 'shares', 'leads_generated'],
            title="Monthly Content Performance Trends",
            labels={'value': 'Count', 'variable': 'Metric', 'month': 'Month'}
        )
        st.plotly_chart(fig_trends, use_container_width=True)

def show_digital_marketing():
    """Display digital marketing analysis"""
    st.title("🌐 Digital Marketing & Web Analytics")
    st.markdown("---")
    
    # Website traffic analysis
    if not st.session_state.website_traffic_data.empty:
        st.subheader("🌐 Website Traffic Analysis")
        
        # Traffic overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sessions = len(st.session_state.website_traffic_data)
            st.metric("Total Sessions", f"{total_sessions:,}")
        
        with col2:
            unique_visitors = st.session_state.website_traffic_data['customer_id'].nunique()
            st.metric("Unique Visitors", f"{unique_visitors:,}")
        
        with col3:
            conversions = st.session_state.website_traffic_data['conversion_flag'].sum()
            st.metric("Conversions", f"{conversions:,}")
        
        with col4:
            conversion_rate = calculate_conversion_rate(conversions, total_sessions)
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        # Traffic sources analysis
        if 'traffic_source' in st.session_state.website_traffic_data.columns:
            traffic_analysis = analyze_traffic_sources(st.session_state.website_traffic_data)
            
            if not traffic_analysis.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_traffic_sources = px.pie(
                        values=traffic_analysis['visits'],
                        names=traffic_analysis.index,
                        title="Traffic Distribution by Source"
                    )
                    st.plotly_chart(fig_traffic_sources, use_container_width=True)
                
                with col2:
                    fig_traffic_conversion = px.bar(
                        traffic_analysis.reset_index(),
                        x='traffic_source',
                        y='conversion_rate',
                        title="Conversion Rate by Traffic Source",
                        labels={'conversion_rate': 'Conversion Rate (%)', 'traffic_source': 'Traffic Source'}
                    )
                    st.plotly_chart(fig_traffic_conversion, use_container_width=True)
    
    # Social media analysis
    if not st.session_state.social_media_data.empty:
        st.subheader("📱 Social Media Analysis")
        
        social_performance = analyze_social_media_performance(st.session_state.social_media_data)
        
        if not social_performance.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_social_engagement = px.bar(
                    social_performance.reset_index(),
                    x='platform',
                    y='engagement_rate',
                    title="Engagement Rate by Platform",
                    labels={'engagement_rate': 'Engagement Rate (%)', 'platform': 'Platform'}
                )
                st.plotly_chart(fig_social_engagement, use_container_width=True)
            
            with col2:
                fig_social_ctr = px.bar(
                    social_performance.reset_index(),
                    x='platform',
                    y='ctr',
                    title="Click-Through Rate by Platform",
                    labels={'ctr': 'CTR (%)', 'platform': 'Platform'}
                )
                st.plotly_chart(fig_social_ctr, use_container_width=True)
    
    # Email marketing analysis
    if not st.session_state.email_campaigns_data.empty:
        st.subheader("📧 Email Marketing Analysis")
        
        email_metrics = calculate_email_metrics(st.session_state.email_campaigns_data)
        
        if not email_metrics.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Open Rate", f"{email_metrics['open_rate']:.1f}%")
            with col2:
                st.metric("Click Rate", f"{email_metrics['click_rate']:.1f}%")
            with col3:
                st.metric("Unsubscribe Rate", f"{email_metrics['unsubscribe_rate']:.1f}%")
            with col4:
                st.metric("Conversion Rate", f"{email_metrics['conversion_rate']:.1f}%")

def show_brand_awareness():
    """Display brand awareness analysis"""
    st.title("🏷️ Brand Awareness & Perception")
    st.markdown("---")
    
    if st.session_state.customers_data.empty and st.session_state.social_media_data.empty:
        st.warning("⚠️ Customer and social media data required for brand awareness analysis.")
        return
    
    # Brand recognition metrics
    st.subheader("📊 Brand Recognition Metrics")
    
    if not st.session_state.customers_data.empty:
        # Calculate brand recognition based on customer data
        total_customers = len(st.session_state.customers_data)
        repeat_customers = len(st.session_state.customers_data[st.session_state.customers_data['total_purchases'] > 1])
        high_value_customers = len(st.session_state.customers_data[st.session_state.customers_data['customer_segment'] == 'High Value'])
        
        brand_recognition = (total_customers / (total_customers * 1.5)) * 100  # Simulated
        brand_loyalty = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
        brand_preference = (high_value_customers / total_customers) * 100 if total_customers > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Brand Recognition", f"{brand_recognition:.1f}%")
        with col2:
            st.metric("Brand Loyalty", f"{brand_loyalty:.1f}%")
        with col3:
            st.metric("Brand Preference", f"{brand_preference:.1f}%")
        with col4:
            st.metric("Total Customers", f"{total_customers:,}")
    
    # Social media sentiment analysis
    st.subheader("😊 Social Media Sentiment Analysis")
    
    if not st.session_state.social_media_data.empty:
        # Calculate engagement-based sentiment
        total_engagement = st.session_state.social_media_data['likes'].sum() + st.session_state.social_media_data['shares'].sum() + st.session_state.social_media_data['comments'].sum()
        total_impressions = st.session_state.social_media_data['impressions'].sum()
        
        positive_engagement = total_engagement * 0.7  # Simulated positive engagement
        neutral_engagement = total_engagement * 0.2
        negative_engagement = total_engagement * 0.1
        
        sentiment_data = {
            'Sentiment': ['Positive', 'Neutral', 'Negative'],
            'Count': [positive_engagement, neutral_engagement, negative_engagement],
            'Percentage': [70, 20, 10]
        }
        sentiment_df = pd.DataFrame(sentiment_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sentiment = px.pie(
                sentiment_df,
                values='Count',
                names='Sentiment',
                title="Social Media Sentiment Distribution"
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            fig_sentiment_bar = px.bar(
                sentiment_df,
                x='Sentiment',
                y='Percentage',
                title="Sentiment Percentages",
                labels={'Percentage': 'Percentage (%)', 'Sentiment': 'Sentiment'}
            )
            st.plotly_chart(fig_sentiment_bar, use_container_width=True)
    
    # Net Promoter Score (NPS) analysis
    st.subheader("⭐ Net Promoter Score (NPS)")
    
    if not st.session_state.customers_data.empty:
        # Simulate NPS calculation
        promoters = len(st.session_state.customers_data[st.session_state.customers_data['lifetime_value'] > st.session_state.customers_data['lifetime_value'].mean()])
        detractors = len(st.session_state.customers_data[st.session_state.customers_data['lifetime_value'] < st.session_state.customers_data['lifetime_value'].quantile(0.3)])
        total_customers = len(st.session_state.customers_data)
        
        promoters_pct = (promoters / total_customers) * 100 if total_customers > 0 else 0
        detractors_pct = (detractors / total_customers) * 100 if total_customers > 0 else 0
        nps_score = promoters_pct - detractors_pct
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Promoters", f"{promoters_pct:.1f}%")
        with col2:
            st.metric("Detractors", f"{detractors_pct:.1f}%")
        with col3:
            st.metric("NPS Score", f"{nps_score:.0f}")
        
        # NPS interpretation
        if nps_score >= 50:
            st.success("🎉 Excellent NPS Score! Your customers are highly likely to recommend your brand.")
        elif nps_score >= 30:
            st.info("👍 Good NPS Score. There's room for improvement in customer satisfaction.")
        else:
            st.warning("⚠️ NPS Score needs improvement. Focus on customer satisfaction and experience.")
    
    # Share of Voice analysis
    st.subheader("📢 Share of Voice Analysis")
    
    if not st.session_state.social_media_data.empty:
        # Calculate share of voice by platform
        platform_voice = st.session_state.social_media_data.groupby('platform').agg({
            'impressions': 'sum',
            'engagement_rate': 'mean'
        }).reset_index()
        
        total_impressions = platform_voice['impressions'].sum()
        platform_voice['share_of_voice'] = (platform_voice['impressions'] / total_impressions) * 100
        
        fig_voice = px.bar(
            platform_voice,
            x='platform',
            y='share_of_voice',
            title="Share of Voice by Platform",
            labels={'share_of_voice': 'Share of Voice (%)', 'platform': 'Platform'}
        )
        st.plotly_chart(fig_voice, use_container_width=True)
    
    # Brand awareness trends
    st.subheader("📈 Brand Awareness Trends")
    
    if not st.session_state.social_media_data.empty:
        # Analyze brand awareness trends over time
        social_data = st.session_state.social_media_data.copy()
        social_data['publish_date'] = pd.to_datetime(social_data['publish_date'])
        social_data['month'] = social_data['publish_date'].dt.to_period('M')
        
        monthly_awareness = social_data.groupby('month').agg({
            'impressions': 'sum',
            'engagement_rate': 'mean'
        }).reset_index()
        monthly_awareness['month'] = monthly_awareness['month'].astype(str)
        
        fig_awareness_trend = px.line(
            monthly_awareness,
            x='month',
            y=['impressions', 'engagement_rate'],
            title="Brand Awareness Trends Over Time",
            labels={'value': 'Count/Rate', 'variable': 'Metric', 'month': 'Month'}
        )
        st.plotly_chart(fig_awareness_trend, use_container_width=True)

def show_product_marketing():
    """Display product marketing analysis"""
    st.title("📦 Product Marketing Analysis")
    st.markdown("---")
    
    if st.session_state.conversions_data.empty:
        st.warning("⚠️ Conversion data required for product marketing analysis.")
        return
    
    # Product performance analysis
    st.subheader("📊 Product Performance Analysis")
    
    if not st.session_state.conversions_data.empty:
        # Analyze conversions by type (assuming different conversion types represent different products)
        product_performance = st.session_state.conversions_data.groupby('conversion_type').agg({
            'conversion_id': 'count',
            'revenue': 'sum'
        }).rename(columns={'conversion_id': 'conversions'})
        product_performance['avg_revenue'] = product_performance['revenue'] / product_performance['conversions']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_product_conversions = px.bar(
                product_performance.reset_index(),
                x='conversion_type',
                y='conversions',
                title="Conversions by Product Type",
                labels={'conversions': 'Number of Conversions', 'conversion_type': 'Product Type'}
            )
            st.plotly_chart(fig_product_conversions, use_container_width=True)
        
        with col2:
            fig_product_revenue = px.bar(
                product_performance.reset_index(),
                x='conversion_type',
                y='revenue',
                title="Revenue by Product Type",
                labels={'revenue': 'Total Revenue ($)', 'conversion_type': 'Product Type'}
            )
            st.plotly_chart(fig_product_revenue, use_container_width=True)
    
    # Product launch analysis
    st.subheader("🚀 Product Launch Analysis")
    
    if not st.session_state.conversions_data.empty:
        # Analyze conversion trends over time to simulate product launch performance
        conversions_data = st.session_state.conversions_data.copy()
        conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
        conversions_data['month'] = conversions_data['conversion_date'].dt.to_period('M')
        
        launch_performance = conversions_data.groupby(['month', 'conversion_type']).agg({
            'conversion_id': 'count',
            'revenue': 'sum'
        }).reset_index()
        launch_performance['month'] = launch_performance['month'].astype(str)
        
        fig_launch_trend = px.line(
            launch_performance,
            x='month',
            y='conversion_id',
            color='conversion_type',
            title="Product Launch Performance Over Time",
            labels={'conversion_id': 'Conversions', 'month': 'Month', 'conversion_type': 'Product Type'}
        )
        st.plotly_chart(fig_launch_trend, use_container_width=True)
    
    # Pricing effectiveness analysis
    st.subheader("💰 Pricing Effectiveness Analysis")
    
    if not st.session_state.conversions_data.empty:
        # Analyze revenue distribution to understand pricing effectiveness
        revenue_stats = st.session_state.conversions_data['revenue'].describe()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Revenue", f"${revenue_stats['mean']:.0f}")
        with col2:
            st.metric("Median Revenue", f"${revenue_stats['50%']:.0f}")
        with col3:
            st.metric("Max Revenue", f"${revenue_stats['max']:.0f}")
        with col4:
            st.metric("Revenue Range", f"${revenue_stats['max'] - revenue_stats['min']:.0f}")
        
        # Revenue distribution histogram
        fig_revenue_dist = px.histogram(
            st.session_state.conversions_data,
            x='revenue',
            nbins=20,
            title="Revenue Distribution",
            labels={'revenue': 'Revenue ($)', 'count': 'Frequency'}
        )
        st.plotly_chart(fig_revenue_dist, use_container_width=True)
    
    # Feature adoption analysis (simulated)
    st.subheader("🔧 Feature Adoption Analysis")
    
    # Simulate feature adoption data based on conversion patterns
    if not st.session_state.conversions_data.empty:
        # Use touchpoint count as a proxy for feature adoption
        feature_adoption = st.session_state.conversions_data.groupby('touchpoint_count').agg({
            'conversion_id': 'count',
            'revenue': 'mean'
        }).reset_index()
        
        fig_feature_adoption = px.scatter(
            feature_adoption,
            x='touchpoint_count',
            y='conversion_id',
            size='revenue',
            title="Feature Adoption vs Touchpoints",
            labels={'touchpoint_count': 'Number of Touchpoints', 'conversion_id': 'Conversions', 'revenue': 'Average Revenue'}
        )
        st.plotly_chart(fig_feature_adoption, use_container_width=True)
    
    # Product marketing ROI
    st.subheader("📈 Product Marketing ROI")
    
    if not st.session_state.campaigns_data.empty and not st.session_state.conversions_data.empty:
        # Calculate ROI for different product types
        campaign_budgets = st.session_state.campaigns_data.groupby('campaign_type')['budget'].sum()
        product_revenues = st.session_state.conversions_data.groupby('conversion_type')['revenue'].sum()
        
        # Match campaign types to conversion types (simplified)
        roi_data = []
        for conv_type in product_revenues.index:
            revenue = product_revenues[conv_type]
            # Find matching campaign budget (simplified matching)
            budget = campaign_budgets.sum() / len(product_revenues)  # Distribute budget equally
            roi = ((revenue - budget) / budget) * 100 if budget > 0 else 0
            roi_data.append({
                'Product Type': conv_type,
                'Revenue': revenue,
                'Budget': budget,
                'ROI': roi
            })
        
        roi_df = pd.DataFrame(roi_data)
        
        fig_roi = px.bar(
            roi_df,
            x='Product Type',
            y='ROI',
            title="Product Marketing ROI by Type",
            labels={'ROI': 'ROI (%)', 'Product Type': 'Product Type'}
        )
        st.plotly_chart(fig_roi, use_container_width=True)
        
        st.markdown("**Product Marketing ROI Summary:**")
        display_dataframe_with_index_1(roi_df)

def show_customer_journey():
    """Display customer journey analysis"""
    st.title("🛤️ Customer Journey Analysis")
    st.markdown("---")
    
    if st.session_state.conversions_data.empty:
        st.warning("⚠️ Conversion data required for customer journey analysis.")
        return
    
    # Attribution modeling
    st.subheader("🎯 Attribution Modeling")
    
    if not st.session_state.conversions_data.empty:
        # Analyze attribution sources
        attribution_analysis = st.session_state.conversions_data.groupby('attribution_source').agg({
            'conversion_id': 'count',
            'revenue': 'sum',
            'touchpoint_count': 'mean'
        }).reset_index()
        
        attribution_analysis['conversion_rate'] = (attribution_analysis['conversion_id'] / attribution_analysis['conversion_id'].sum()) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_attribution = px.bar(
                attribution_analysis,
                x='attribution_source',
                y='conversion_id',
                title="Conversions by Attribution Source",
                labels={'conversion_id': 'Number of Conversions', 'attribution_source': 'Attribution Source'}
            )
            st.plotly_chart(fig_attribution, use_container_width=True)
        
        with col2:
            fig_attribution_revenue = px.bar(
                attribution_analysis,
                x='attribution_source',
                y='revenue',
                title="Revenue by Attribution Source",
                labels={'revenue': 'Total Revenue ($)', 'attribution_source': 'Attribution Source'}
            )
            st.plotly_chart(fig_attribution_revenue, use_container_width=True)
    
    # Path to purchase analysis
    st.subheader("🛒 Path to Purchase Analysis")
    
    if not st.session_state.conversions_data.empty:
        # Analyze touchpoint patterns
        touchpoint_analysis = st.session_state.conversions_data.groupby('touchpoint_count').agg({
            'conversion_id': 'count',
            'revenue': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_touchpoints = px.bar(
                touchpoint_analysis,
                x='touchpoint_count',
                y='conversion_id',
                title="Conversions by Number of Touchpoints",
                labels={'conversion_id': 'Number of Conversions', 'touchpoint_count': 'Number of Touchpoints'}
            )
            st.plotly_chart(fig_touchpoints, use_container_width=True)
        
        with col2:
            fig_touchpoint_revenue = px.scatter(
                touchpoint_analysis,
                x='touchpoint_count',
                y='revenue',
                size='conversion_id',
                title="Revenue vs Touchpoints",
                labels={'revenue': 'Average Revenue ($)', 'touchpoint_count': 'Number of Touchpoints', 'conversion_id': 'Conversions'}
            )
            st.plotly_chart(fig_touchpoint_revenue, use_container_width=True)
    
    # Customer journey funnel
    st.subheader("🔄 Customer Journey Funnel")
    
    if not st.session_state.leads_data.empty and not st.session_state.conversions_data.empty:
        # Create a simple funnel from leads to conversions
        total_leads = len(st.session_state.leads_data)
        qualified_leads = len(st.session_state.leads_data[st.session_state.leads_data['status'].isin(['Qualified', 'Proposal', 'Negotiation'])])
        total_conversions = len(st.session_state.conversions_data)
        
        funnel_data = {
            'Stage': ['Leads', 'Qualified Leads', 'Conversions'],
            'Count': [total_leads, qualified_leads, total_conversions],
            'Conversion Rate': [100, (qualified_leads/total_leads)*100 if total_leads > 0 else 0, (total_conversions/total_leads)*100 if total_leads > 0 else 0]
        }
        funnel_df = pd.DataFrame(funnel_data)
        
        fig_funnel = px.funnel(
            funnel_df,
            x='Count',
            y='Stage',
            title="Customer Journey Funnel"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # Funnel metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lead to Qualified Rate", f"{funnel_data['Conversion Rate'][1]:.1f}%")
        with col2:
            st.metric("Qualified to Conversion Rate", f"{(funnel_data['Conversion Rate'][2]/funnel_data['Conversion Rate'][1])*100:.1f}%" if funnel_data['Conversion Rate'][1] > 0 else "0%")
        with col3:
            st.metric("Overall Conversion Rate", f"{funnel_data['Conversion Rate'][2]:.1f}%")
    
    # Customer retention analysis
    st.subheader("🔄 Customer Retention Analysis")
    
    if not st.session_state.customers_data.empty:
        # Analyze customer retention based on purchase frequency
        repeat_customers = len(st.session_state.customers_data[st.session_state.customers_data['total_purchases'] > 1])
        total_customers = len(st.session_state.customers_data)
        retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers", f"{total_customers:,}")
        with col2:
            st.metric("Repeat Customers", f"{repeat_customers:,}")
        with col3:
            st.metric("Retention Rate", f"{retention_rate:.1f}%")
        
        # Customer lifetime value by segment
        if 'customer_segment' in st.session_state.customers_data.columns:
            segment_retention = st.session_state.customers_data.groupby('customer_segment').agg({
                'customer_id': 'count',
                'lifetime_value': 'mean',
                'total_purchases': 'mean'
            }).reset_index()
            
            fig_segment_retention = px.bar(
                segment_retention,
                x='customer_segment',
                y='lifetime_value',
                title="Customer Lifetime Value by Segment",
                labels={'lifetime_value': 'Average Lifetime Value ($)', 'customer_segment': 'Customer Segment'}
            )
            st.plotly_chart(fig_segment_retention, use_container_width=True)
    
    # Journey optimization insights
    st.subheader("💡 Journey Optimization Insights")
    
    if not st.session_state.conversions_data.empty:
        # Identify best performing attribution sources
        best_sources = st.session_state.conversions_data.groupby('attribution_source')['revenue'].sum().sort_values(ascending=False)
        
        st.markdown("**Top Performing Attribution Sources:**")
        for i, (source, revenue) in enumerate(best_sources.head(3).items(), 1):
            st.markdown(f"{i}. **{source}**: ${revenue:,.0f}")
        
        # Optimal touchpoint count
        optimal_touchpoints = st.session_state.conversions_data.groupby('touchpoint_count')['revenue'].mean().idxmax()
        st.markdown(f"**Optimal Touchpoint Count**: {optimal_touchpoints} touchpoints")
        
        # Conversion time analysis (if date data is available)
        if 'conversion_date' in st.session_state.conversions_data.columns:
            conversions_data = st.session_state.conversions_data.copy()
            conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
            conversions_data['day_of_week'] = conversions_data['conversion_date'].dt.day_name()
            
            day_performance = conversions_data.groupby('day_of_week')['revenue'].sum().reset_index()
            
            fig_day_performance = px.bar(
                day_performance,
                x='day_of_week',
                y='revenue',
                title="Revenue by Day of Week",
                labels={'revenue': 'Total Revenue ($)', 'day_of_week': 'Day of Week'}
            )
            st.plotly_chart(fig_day_performance, use_container_width=True)

def show_marketing_forecasting():
    """Display marketing forecasting"""
    st.title("🔮 Marketing Forecasting")
    st.markdown("---")
    
    if st.session_state.conversions_data.empty and st.session_state.leads_data.empty:
        st.warning("⚠️ Conversion and lead data required for marketing forecasting.")
        return
    
    # Revenue forecasting
    st.subheader("💰 Revenue Forecasting")
    
    if not st.session_state.conversions_data.empty:
        # Analyze revenue trends
        conversions_data = st.session_state.conversions_data.copy()
        conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
        conversions_data['month'] = conversions_data['conversion_date'].dt.to_period('M')
        
        monthly_revenue = conversions_data.groupby('month')['revenue'].sum().reset_index()
        monthly_revenue['month'] = monthly_revenue['month'].astype(str)
        
        # Calculate growth rate
        if len(monthly_revenue) > 1:
            growth_rate = ((monthly_revenue['revenue'].iloc[-1] - monthly_revenue['revenue'].iloc[-2]) / monthly_revenue['revenue'].iloc[-2]) * 100
        else:
            growth_rate = 5  # Default 5% growth
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Monthly Revenue", f"${monthly_revenue['revenue'].iloc[-1]:,.0f}")
        with col2:
            st.metric("Average Monthly Revenue", f"${monthly_revenue['revenue'].mean():,.0f}")
        with col3:
            st.metric("Growth Rate", f"{growth_rate:.1f}%")
        
        # Revenue trend chart
        fig_forecast = px.line(
            monthly_revenue,
            x='month',
            y='revenue',
            title="Revenue Trend Analysis",
            labels={'revenue': 'Revenue ($)', 'month': 'Month'}
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Simple forecast (next 3 months)
        if len(monthly_revenue) > 1:
            last_revenue = monthly_revenue['revenue'].iloc[-1]
            forecast_data = []
            for i in range(1, 4):
                forecast_month = f"Forecast {i}"
                forecast_revenue = last_revenue * (1 + (growth_rate/100)) ** i
                forecast_data.append({
                    'Month': forecast_month,
                    'Revenue': forecast_revenue,
                    'Type': 'Forecast'
                })
            
            forecast_df = pd.DataFrame(forecast_data)
            
            # Combine historical and forecast data
            historical_data = monthly_revenue[['month', 'revenue']].rename(columns={'month': 'Month', 'revenue': 'Revenue'})
            historical_data['Type'] = 'Historical'
            
            combined_data = pd.concat([historical_data, forecast_df])
            
            fig_combined = px.line(
                combined_data,
                x='Month',
                y='Revenue',
                color='Type',
                title="Revenue Forecast (Next 3 Months)",
                labels={'Revenue': 'Revenue ($)', 'Month': 'Month'}
            )
            st.plotly_chart(fig_combined, use_container_width=True)
    
    # Lead forecasting
    st.subheader("🎯 Lead Forecasting")
    
    if not st.session_state.leads_data.empty:
        # Analyze lead generation trends
        leads_data = st.session_state.leads_data.copy()
        leads_data['created_date'] = pd.to_datetime(leads_data['created_date'])
        leads_data['month'] = leads_data['created_date'].dt.to_period('M')
        
        monthly_leads = leads_data.groupby('month')['lead_id'].count().reset_index()
        monthly_leads['month'] = monthly_leads['month'].astype(str)
        monthly_leads = monthly_leads.rename(columns={'lead_id': 'leads'})
        
        # Calculate lead growth rate
        if len(monthly_leads) > 1:
            lead_growth_rate = ((monthly_leads['leads'].iloc[-1] - monthly_leads['leads'].iloc[-2]) / monthly_leads['leads'].iloc[-2]) * 100
        else:
            lead_growth_rate = 5  # Default 5% growth
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Monthly Leads", f"{monthly_leads['leads'].iloc[-1]:,}")
        with col2:
            st.metric("Average Monthly Leads", f"{monthly_leads['leads'].mean():.0f}")
        with col3:
            st.metric("Lead Growth Rate", f"{lead_growth_rate:.1f}%")
        
        # Lead trend chart
        fig_lead_trend = px.line(
            monthly_leads,
            x='month',
            y='leads',
            title="Lead Generation Trend",
            labels={'leads': 'Number of Leads', 'month': 'Month'}
        )
        st.plotly_chart(fig_lead_trend, use_container_width=True)
        
        # Lead source analysis for forecasting
        lead_source_analysis = leads_data.groupby('source')['lead_id'].count().sort_values(ascending=False)
        
        fig_lead_sources = px.bar(
            lead_source_analysis.reset_index(),
            x='source',
            y='lead_id',
            title="Lead Generation by Source",
            labels={'lead_id': 'Number of Leads', 'source': 'Lead Source'}
        )
        st.plotly_chart(fig_lead_sources, use_container_width=True)
    
    # Campaign budget forecasting
    st.subheader("💰 Campaign Budget Forecasting")
    
    if not st.session_state.campaigns_data.empty and not st.session_state.conversions_data.empty:
        # Analyze campaign performance for budget allocation
        campaign_performance = st.session_state.campaigns_data.groupby('campaign_type').agg({
            'budget': 'sum',
            'campaign_id': 'count'
        }).reset_index()
        
        # Calculate ROI for each campaign type
        campaign_roi = []
        for _, campaign in campaign_performance.iterrows():
            campaign_type = campaign['campaign_type']
            budget = campaign['budget']
            
            # Find matching conversions (simplified)
            if not st.session_state.conversions_data.empty:
                # Assume conversions are distributed across campaign types
                total_revenue = st.session_state.conversions_data['revenue'].sum()
                campaign_revenue = total_revenue / len(campaign_performance)  # Simplified distribution
                roi = ((campaign_revenue - budget) / budget) * 100 if budget > 0 else 0
            else:
                roi = 0
            
            campaign_roi.append({
                'Campaign Type': campaign_type,
                'Budget': budget,
                'Revenue': campaign_revenue if 'campaign_revenue' in locals() else 0,
                'ROI': roi
            })
        
        roi_df = pd.DataFrame(campaign_roi)
        
        # Budget allocation recommendations
        st.markdown("**Budget Allocation Recommendations:**")
        
        # Allocate budget based on ROI performance
        total_budget = roi_df['Budget'].sum()
        roi_df['Recommended Budget'] = roi_df['ROI'].apply(lambda x: total_budget * (x / roi_df['ROI'].sum()) if roi_df['ROI'].sum() > 0 else total_budget / len(roi_df))
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_budget_current = px.pie(
                roi_df,
                values='Budget',
                names='Campaign Type',
                title="Current Budget Allocation"
            )
            st.plotly_chart(fig_budget_current, use_container_width=True)
        
        with col2:
            fig_budget_recommended = px.pie(
                roi_df,
                values='Recommended Budget',
                names='Campaign Type',
                title="Recommended Budget Allocation"
            )
            st.plotly_chart(fig_budget_recommended, use_container_width=True)
        
        st.markdown("**Campaign Performance Summary:**")
        display_dataframe_with_index_1(roi_df[['Campaign Type', 'Budget', 'Revenue', 'ROI', 'Recommended Budget']])
    
    # Seasonal trend analysis
    st.subheader("📅 Seasonal Trend Analysis")
    
    if not st.session_state.conversions_data.empty:
        # Analyze seasonal patterns
        conversions_data = st.session_state.conversions_data.copy()
        conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
        conversions_data['month_name'] = conversions_data['conversion_date'].dt.month_name()
        conversions_data['quarter'] = conversions_data['conversion_date'].dt.quarter
        
        # Monthly seasonal analysis
        monthly_seasonal = conversions_data.groupby('month_name')['revenue'].sum().reset_index()
        
        # Reorder months
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_seasonal['month_name'] = pd.Categorical(monthly_seasonal['month_name'], categories=month_order, ordered=True)
        monthly_seasonal = monthly_seasonal.sort_values('month_name')
        
        fig_seasonal = px.bar(
            monthly_seasonal,
            x='month_name',
            y='revenue',
            title="Seasonal Revenue Patterns",
            labels={'revenue': 'Revenue ($)', 'month_name': 'Month'}
        )
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        # Quarterly analysis
        quarterly_seasonal = conversions_data.groupby('quarter')['revenue'].sum().reset_index()
        
        fig_quarterly = px.bar(
            quarterly_seasonal,
            x='quarter',
            y='revenue',
            title="Quarterly Revenue Patterns",
            labels={'revenue': 'Revenue ($)', 'quarter': 'Quarter'}
        )
        st.plotly_chart(fig_quarterly, use_container_width=True)

def show_channel_analysis():
    """Display channel-specific analysis"""
    st.title("📱 Channel-Specific Analysis")
    st.markdown("---")
    
    # Social media analysis
    if not st.session_state.social_media_data.empty:
        st.subheader("📱 Social Media Channel Analysis")
        
        social_performance = analyze_social_media_performance(st.session_state.social_media_data)
        
        if not social_performance.empty:
            # Platform comparison
            fig_platform_comparison = px.bar(
                social_performance.reset_index(),
                x='platform',
                y=['impressions', 'clicks', 'total_engagement'],
                title="Social Media Platform Performance",
                labels={'value': 'Count', 'variable': 'Metric', 'platform': 'Platform'},
                barmode='group'
            )
            st.plotly_chart(fig_platform_comparison, use_container_width=True)
    
    # Email marketing analysis
    if not st.session_state.email_campaigns_data.empty:
        st.subheader("📧 Email Marketing Channel Analysis")
        
        email_performance = st.session_state.email_campaigns_data.groupby('campaign_name').agg({
            'recipients': 'sum',
            'opens': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        email_performance['open_rate'] = (email_performance['opens'] / email_performance['recipients']) * 100
        email_performance['click_rate'] = (email_performance['clicks'] / email_performance['recipients']) * 100
        email_performance['conversion_rate'] = (email_performance['conversions'] / email_performance['recipients']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_email_rates = px.bar(
                email_performance,
                x='campaign_name',
                y=['open_rate', 'click_rate', 'conversion_rate'],
                title="Email Campaign Performance Rates",
                labels={'value': 'Rate (%)', 'variable': 'Metric', 'campaign_name': 'Campaign Name'},
                barmode='group'
            )
            st.plotly_chart(fig_email_rates, use_container_width=True)
        
        with col2:
            fig_email_volume = px.bar(
                email_performance,
                x='campaign_name',
                y=['recipients', 'opens', 'clicks', 'conversions'],
                title="Email Campaign Volume Metrics",
                labels={'value': 'Count', 'variable': 'Metric', 'campaign_name': 'Campaign Name'},
                barmode='group'
            )
            st.plotly_chart(fig_email_volume, use_container_width=True)

def show_specialized_metrics():
    """Display specialized marketing metrics"""
    st.title("🎯 Specialized Marketing Metrics")
    st.markdown("---")
    
    st.info("💡 Specialized metrics provide deeper insights into specific marketing areas.")
    
    # Seasonal trends analysis
    st.subheader("📅 Seasonal Trends Analysis")
    
    if not st.session_state.conversions_data.empty:
        try:
            conversions_data = st.session_state.conversions_data.copy()
            conversions_data['conversion_date'] = pd.to_datetime(conversions_data['conversion_date'])
            conversions_data['month'] = conversions_data['conversion_date'].dt.month_name()
            conversions_data['month_num'] = conversions_data['conversion_date'].dt.month
            
            # Group by month and aggregate
            seasonal_performance = conversions_data.groupby('month').agg({
                'revenue': 'sum',
                'conversion_id': 'count'
            }).rename(columns={'conversion_id': 'conversions'})
            
            # Add month number for proper ordering
            seasonal_performance['month_num'] = seasonal_performance.index.map({
                'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
            })
            
            # Sort by month number and reset index
            seasonal_performance = seasonal_performance.sort_values('month_num').reset_index()
            
            # Create the seasonal trends chart
            fig_seasonal = px.line(
                seasonal_performance,
                x='month',
                y=['revenue', 'conversions'],
                title="Seasonal Revenue and Conversion Trends",
                labels={'value': 'Count/Amount', 'variable': 'Metric', 'month': 'Month'},
                color_discrete_sequence=['#667eea', '#f97316']
            )
            
            # Apply common layout and styling
            fig_seasonal = apply_common_layout(fig_seasonal)
            fig_seasonal.update_traces(line=dict(width=3))
            fig_seasonal.update_layout(
                title_font_size=18,
                title_font_color='#1e3c72',
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                legend_title_font_size=14,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_seasonal, use_container_width=True)
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${seasonal_performance['revenue'].sum():,.0f}")
            with col2:
                st.metric("Total Conversions", f"{seasonal_performance['conversions'].sum():,}")
            with col3:
                avg_revenue = seasonal_performance['revenue'].mean()
                st.metric("Avg Monthly Revenue", f"${avg_revenue:,.0f}")
                
        except Exception as e:
            st.error(f"Error processing seasonal trends data: {str(e)}")
            st.info("Please ensure conversions data contains valid dates and revenue information.")
    else:
        st.warning("⚠️ No conversion data available. Please load sample data or upload your own data first.")
    
    # Mobile vs Desktop analysis
    if not st.session_state.website_traffic_data.empty and 'device_type' in st.session_state.website_traffic_data.columns:
        st.subheader("📱 Mobile vs Desktop Analysis")
        
        try:
            device_analysis = st.session_state.website_traffic_data.groupby('device_type').agg({
                'session_id': 'count',
                'conversion_flag': 'sum',
                'time_on_page': 'mean'
            }).rename(columns={'session_id': 'sessions', 'conversion_flag': 'conversions'})
            
            device_analysis['conversion_rate'] = (device_analysis['conversions'] / device_analysis['sessions']) * 100
            
            # Display device performance metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_sessions = device_analysis['sessions'].sum()
                st.metric("Total Sessions", f"{total_sessions:,}")
            with col2:
                total_conversions = device_analysis['conversions'].sum()
                st.metric("Total Conversions", f"{total_conversions:,}")
            with col3:
                overall_conversion_rate = (total_conversions / total_sessions) * 100
                st.metric("Overall Conversion Rate", f"{overall_conversion_rate:.1f}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_device_sessions = px.pie(
                    values=device_analysis['sessions'],
                    names=device_analysis.index,
                    title="Traffic Distribution by Device Type",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_device_sessions = apply_common_layout(fig_device_sessions)
                fig_device_sessions.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_device_sessions, use_container_width=True)
            
            with col2:
                fig_device_conversion = px.bar(
                    device_analysis.reset_index(),
                    x='device_type',
                    y='conversion_rate',
                    title="Conversion Rate by Device Type",
                    labels={'conversion_rate': 'Conversion Rate (%)', 'device_type': 'Device Type'},
                    color='conversion_rate',
                    color_continuous_scale='Viridis'
                )
                fig_device_conversion = apply_common_layout(fig_device_conversion)
                fig_device_conversion.update_layout(
                    title_font_size=16,
                    title_font_color='#1e3c72'
                )
                st.plotly_chart(fig_device_conversion, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error processing device analysis data: {str(e)}")
            st.info("Please ensure website traffic data contains valid device type and session information.")
    else:
        st.warning("⚠️ No website traffic data available or missing 'device_type' column. Please load sample data or upload your own data first.")
    
    # Customer Lifetime Value Analysis
    if not st.session_state.customers_data.empty and not st.session_state.conversions_data.empty:
        st.subheader("💰 Customer Lifetime Value Analysis")
        
        try:
            # Merge customers with conversions to calculate CLV
            customers_clv = st.session_state.customers_data.copy()
            conversions_summary = st.session_state.conversions_data.groupby('customer_id')['revenue'].sum().reset_index()
            customers_clv = customers_clv.merge(conversions_summary, on='customer_id', how='left')
            customers_clv['revenue'] = customers_clv['revenue'].fillna(0)
            
            # Calculate CLV by customer segment
            clv_by_segment = customers_clv.groupby('customer_segment')['revenue'].agg(['mean', 'sum', 'count']).round(2)
            clv_by_segment.columns = ['Avg CLV', 'Total Revenue', 'Customer Count']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_clv_segment = px.bar(
                    clv_by_segment.reset_index(),
                    x='customer_segment',
                    y='Avg CLV',
                    title="Average CLV by Customer Segment",
                    color='Avg CLV',
                    color_continuous_scale='Viridis'
                )
                fig_clv_segment = apply_common_layout(fig_clv_segment)
                fig_clv_segment.update_layout(
                    title_font_size=16,
                    title_font_color='#1e3c72'
                )
                st.plotly_chart(fig_clv_segment, use_container_width=True)
            
            with col2:
                fig_clv_distribution = px.histogram(
                    customers_clv,
                    x='revenue',
                    nbins=10,
                    title="Customer Lifetime Value Distribution",
                    labels={'revenue': 'CLV ($)', 'count': 'Number of Customers'}
                )
                fig_clv_distribution = apply_common_layout(fig_clv_distribution)
                fig_clv_distribution.update_layout(
                    title_font_size=16,
                    title_font_color='#1e3c72'
                )
                st.plotly_chart(fig_clv_distribution, use_container_width=True)
            
            # Display CLV metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_clv = customers_clv['revenue'].mean()
                st.metric("Average CLV", f"${avg_clv:.2f}")
            with col2:
                total_clv = customers_clv['revenue'].sum()
                st.metric("Total Customer Value", f"${total_clv:,.0f}")
            with col3:
                high_value_customers = len(customers_clv[customers_clv['revenue'] > avg_clv])
                st.metric("High-Value Customers", f"{high_value_customers}")
                
        except Exception as e:
            st.error(f"Error processing CLV analysis: {str(e)}")
            st.info("Please ensure both customer and conversion data are available.")
    
    # Content Performance Analysis
    if not st.session_state.content_marketing_data.empty:
        st.subheader("📝 Content Performance Analysis")
        
        try:
            content_data = st.session_state.content_marketing_data.copy()
            
            # Top performing content by engagement
            top_content = content_data.nlargest(5, 'engagement_rate')[['title', 'content_type', 'views', 'shares', 'engagement_rate']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_content_engagement = px.bar(
                    top_content,
                    x='title',
                    y='engagement_rate',
                    title="Top Content by Engagement Rate",
                    color='content_type',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_content_engagement = apply_common_layout(fig_content_engagement)
                fig_content_engagement.update_layout(
                    title_font_size=16,
                    title_font_color='#1e3c72',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_content_engagement, use_container_width=True)
            
            with col2:
                fig_content_views = px.scatter(
                    content_data,
                    x='views',
                    y='shares',
                    size='leads_generated',
                    color='content_type',
                    title="Content Views vs Shares (Size = Leads Generated)",
                    labels={'views': 'Views', 'shares': 'Shares', 'leads_generated': 'Leads Generated'}
                )
                fig_content_views = apply_common_layout(fig_content_views)
                fig_content_views.update_layout(
                    title_font_size=16,
                    title_font_color='#1e3c72'
                )
                st.plotly_chart(fig_content_views, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error processing content performance analysis: {str(e)}")
            st.info("Please ensure content marketing data is available.")

def main():
    # Configure page for wide layout
    st.set_page_config(
        page_title="Marketing Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
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
    
    /* Additional marketing-specific styling */
    .formula-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
        padding: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    .summary-dashboard {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: white;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 Marketing Analytics Dashboard</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Comprehensive Marketing Analytics & Insights Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'campaigns_data' not in st.session_state:
        st.session_state.campaigns_data = pd.DataFrame()
    if 'customers_data' not in st.session_state:
        st.session_state.customers_data = pd.DataFrame()
    if 'website_traffic_data' not in st.session_state:
        st.session_state.website_traffic_data = pd.DataFrame()
    if 'social_media_data' not in st.session_state:
        st.session_state.social_media_data = pd.DataFrame()
    if 'email_campaigns_data' not in st.session_state:
        st.session_state.email_campaigns_data = pd.DataFrame()
    if 'content_marketing_data' not in st.session_state:
        st.session_state.content_marketing_data = pd.DataFrame()
    if 'leads_data' not in st.session_state:
        st.session_state.leads_data = pd.DataFrame()
    if 'conversions_data' not in st.session_state:
        st.session_state.conversions_data = pd.DataFrame()
    
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
        
        if st.button("📈 Campaign Performance", key="nav_campaign_performance", use_container_width=True):
            st.session_state.current_page = "📈 Campaign Performance"
        
        if st.button("👥 Customer Analysis", key="nav_customer_analysis", use_container_width=True):
            st.session_state.current_page = "👥 Customer Analysis"
        
        if st.button("🌍 Market Analysis", key="nav_market_analysis", use_container_width=True):
            st.session_state.current_page = "🌍 Market Analysis"
        
        if st.button("📝 Content Marketing", key="nav_content_marketing", use_container_width=True):
            st.session_state.current_page = "📝 Content Marketing"
        
        if st.button("🌐 Digital Marketing", key="nav_digital_marketing", use_container_width=True):
            st.session_state.current_page = "🌐 Digital Marketing"
        
        if st.button("🏷️ Brand Awareness", key="nav_brand_awareness", use_container_width=True):
            st.session_state.current_page = "🏷️ Brand Awareness"
        
        if st.button("📦 Product Marketing", key="nav_product_marketing", use_container_width=True):
            st.session_state.current_page = "📦 Product Marketing"
        
        if st.button("🛤️ Customer Journey", key="nav_customer_journey", use_container_width=True):
            st.session_state.current_page = "🛤️ Customer Journey"
        
        if st.button("🔮 Marketing Forecasting", key="nav_marketing_forecasting", use_container_width=True):
            st.session_state.current_page = "🔮 Marketing Forecasting"
        
        if st.button("📱 Channel Analysis", key="nav_channel_analysis", use_container_width=True):
            st.session_state.current_page = "📱 Channel Analysis"
        
        if st.button("🎯 Specialized Metrics", key="nav_specialized_metrics", use_container_width=True):
            st.session_state.current_page = "🎯 Specialized Metrics"
        
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
    
    elif page == "📈 Campaign Performance":
        show_campaign_performance()
    
    elif page == "👥 Customer Analysis":
        show_customer_analysis()
    
    elif page == "🌍 Market Analysis":
        show_market_analysis()
    
    elif page == "📝 Content Marketing":
        show_content_marketing()
    
    elif page == "🌐 Digital Marketing":
        show_digital_marketing()
    
    elif page == "🏷️ Brand Awareness":
        show_brand_awareness()
    
    elif page == "📦 Product Marketing":
        show_product_marketing()
    
    elif page == "🛤️ Customer Journey":
        show_customer_journey()
    
    elif page == "🔮 Marketing Forecasting":
        show_marketing_forecasting()
    
    elif page == "📱 Channel Analysis":
        show_channel_analysis()
    
    elif page == "🎯 Specialized Metrics":
        show_specialized_metrics()

if __name__ == "__main__":
    main()
