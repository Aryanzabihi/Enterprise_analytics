import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Common color schemes and styling
COLOR_SCHEMES = {
    'primary': ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#ffecd2', '#a8edea'],
    'secondary': ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#ffecd2', '#a8edea'],
    'success': '#48bb78',
    'warning': '#ed8936',
    'error': '#f56565',
    'info': '#4299e1'
}

def load_shared_css():
    """Load shared CSS styling for all applications"""
    st.markdown("""
    <style>
    /* Shared Enterprise Styling */
    .main .block-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        max-width: 100%;
    }
    
    /* Card styling */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Metric display */
    .metric-display {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Button styling */
    .action-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-success { background-color: #48bb78; color: white; }
    .status-warning { background-color: #ed8936; color: white; }
    .status-error { background-color: #f56565; color: white; }
    .status-info { background-color: #4299e1; color: white; }
    
    /* Data table styling */
    .data-table {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, subtitle="", color="#667eea", icon="📊"):
    """Create a standardized metric card"""
    st.markdown(f"""
    <div class="metric-display">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <h3 style="color: {color}; margin: 10px 0;">{value}</h3>
        <h4 style="margin: 5px 0; color: #333;">{title}</h4>
        <p style="font-size: 12px; color: #666; margin: 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def create_info_card(title, content, icon="ℹ️"):
    """Create a standardized info card"""
    st.markdown(f"""
    <div class="info-card">
        <h3 style="color: #667eea; margin-bottom: 15px;">
            {icon} {title}
        </h3>
        <div style="color: #333; line-height: 1.6;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_status_badge(status, text):
    """Create a status badge with appropriate colors"""
    status_class = f"status-{status.lower()}"
    st.markdown(f"""
    <span class="status-badge {status_class}">{text}</span>
    """, unsafe_allow_html=True)

def display_dataframe_with_index_1(df, title="Data Overview", **kwargs):
    """Display dataframe with index starting from 1 and consistent styling"""
    if not df.empty:
        st.subheader(f"📊 {title}")
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        
        df_display = df.reset_index(drop=True)
        df_display.index = df_display.index + 1
        
        st.dataframe(df_display, **kwargs)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    else:
        st.warning("No data available to display")

def create_download_button(df, filename, sheet_name="Sheet1"):
    """Create a download button for Excel files"""
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.xlsx" class="action-button">📥 Download {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)

def create_chart_container(title, chart_func, *args, **kwargs):
    """Create a standardized chart container"""
    st.markdown(f"<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader(f"📈 {title}")
    
    try:
        chart = chart_func(*args, **kwargs)
        if hasattr(chart, 'update_layout'):
            chart.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=50, r=50, t=50, b=50)
            )
        st.plotly_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_upload_section(title="Data Upload", file_types=['xlsx', 'csv']):
    """Create a standardized file upload section"""
    st.markdown(f"<div class='info-card'>", unsafe_allow_html=True)
    st.subheader(f"📁 {title}")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=file_types,
        help=f"Supported formats: {', '.join(file_types).upper()}"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                st.error("Unsupported file format")
                return None
            
            st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
            st.info(f"Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            return df
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None
    
    st.markdown("</div>", unsafe_allow_html=True)
    return None

def create_navigation_menu(departments):
    """Create a navigation menu for switching between departments"""
    st.sidebar.title("🧭 Navigation")
    st.sidebar.markdown("---")
    
    for dept_key, dept_info in departments.items():
        if st.sidebar.button(f"{dept_info['icon']} {dept_info['name']}", key=f"nav_{dept_key}"):
            st.session_state.selected_department = dept_key
            st.success(f"Switched to: {dept_info['name']}")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Main Dashboard"):
        st.session_state.selected_department = None

def create_summary_metrics(df, title="Data Summary"):
    """Create summary metrics for a dataset"""
    if df is not None and not df.empty:
        st.subheader(f"📊 {title}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card("Total Records", len(df), "Rows in dataset", "#667eea", "📊")
        
        with col2:
            create_metric_card("Total Columns", len(df.columns), "Data fields", "#764ba2", "📋")
        
        with col3:
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            create_metric_card("Numeric Fields", numeric_cols, "Quantitative data", "#f093fb", "🔢")
        
        with col4:
            categorical_cols = len(df.select_dtypes(include=['object']).columns)
            create_metric_card("Text Fields", categorical_cols, "Qualitative data", "#4facfe", "📝")

def create_data_quality_report(df):
    """Create a data quality report"""
    if df is None or df.empty:
        st.warning("No data available for quality report")
        return
    
    st.subheader("🔍 Data Quality Report")
    
    # Missing values analysis
    missing_data = df.isnull().sum()
    missing_percentage = (missing_data / len(df)) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Missing Values by Column:**")
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Missing %': missing_percentage.values
        }).sort_values('Missing Count', ascending=False)
        
        st.dataframe(missing_df, use_container_width=True)
    
    with col2:
        st.markdown("**Data Types:**")
        dtype_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Data Type': df.dtypes.values
        })
        st.dataframe(dtype_df, use_container_width=True)
    
    # Data quality score
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    quality_score = ((total_cells - missing_cells) / total_cells) * 100
    
    st.metric("Data Quality Score", f"{quality_score:.1f}%")

def create_export_section(df, filename_prefix="data"):
    """Create an export section for data download"""
    if df is not None and not df.empty:
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export to Excel", key="export_excel"):
                create_download_button(df, f"{filename_prefix}_export", "Data")
        
        with col2:
            if st.button("📄 Export to CSV", key="export_csv"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename_prefix}_export.csv" class="action-button">📥 Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)

def create_error_boundary(func, *args, **kwargs):
    """Create an error boundary for functions"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def create_loading_spinner(text="Processing..."):
    """Create a loading spinner with custom text"""
    with st.spinner(text):
        return True

def create_success_message(message, duration=3):
    """Create a success message that auto-dismisses"""
    st.success(message)
    if duration > 0:
        st.empty()

def create_warning_message(message, duration=3):
    """Create a warning message that auto-dismisses"""
    st.warning(message)
    if duration > 0:
        st.empty()

def create_error_message(message, duration=3):
    """Create an error message that auto-dismisses"""
    st.error(message)
    if duration > 0:
        st.empty()

def create_info_message(message, duration=3):
    """Create an info message that auto-dismisses"""
    st.info(message)
    if duration > 0:
        st.empty()

# Common chart functions
def create_bar_chart(data, x_col, y_col, title="Bar Chart", color_col=None):
    """Create a standardized bar chart"""
    fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    return fig

def create_line_chart(data, x_col, y_col, title="Line Chart", color_col=None):
    """Create a standardized line chart"""
    fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title, markers=True)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    return fig

def create_pie_chart(data, names_col, values_col, title="Pie Chart"):
    """Create a standardized pie chart"""
    fig = px.pie(data, names=names_col, values=values_col, title=title)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    return fig

def create_scatter_chart(data, x_col, y_col, title="Scatter Plot", color_col=None, size_col=None):
    """Create a standardized scatter plot"""
    fig = px.scatter(data, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    return fig
