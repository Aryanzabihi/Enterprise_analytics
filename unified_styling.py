import streamlit as st

def load_unified_styling():
    """Load unified styling for all applications"""
    st.markdown("""
    <style>
    /* Unified Enterprise Analytics Styling */
    
    /* Main container styling */
    .main .block-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        max-width: 100%;
        min-height: 100vh;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        padding: 20px 12px;
        width: 280px;
        min-width: 280px;
        box-shadow: 2px 0 20px rgba(0,0,0,0.15);
    }
    
    .css-1lcbmhc {
        width: 280px;
        min-width: 280px;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .app-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(45deg, #5a67d8, #6b46c1);
    }
    
    .secondary-button {
        background: rgba(255, 255, 255, 0.9);
        color: #2d3748;
        border: 2px solid #667eea;
        border-radius: 25px;
        padding: 10px 25px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px;
    }
    
    .secondary-button:hover {
        background: #667eea;
        color: white;
        transform: translateY(-1px);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success { 
        background: linear-gradient(45deg, #48bb78, #38a169);
        color: white;
        box-shadow: 0 2px 10px rgba(72, 187, 120, 0.3);
    }
    
    .status-warning { 
        background: linear-gradient(45deg, #ed8936, #dd6b20);
        color: white;
        box-shadow: 0 2px 10px rgba(237, 137, 54, 0.3);
    }
    
    .status-error { 
        background: linear-gradient(45deg, #f56565, #e53e3e);
        color: white;
        box-shadow: 0 2px 10px rgba(245, 101, 101, 0.3);
    }
    
    .status-info { 
        background: linear-gradient(45deg, #4299e1, #3182ce);
        color: white;
        box-shadow: 0 2px 10px rgba(66, 153, 225, 0.3);
    }
    
    /* Data table styling */
    .data-table {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Navigation styling */
    .nav-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.9);
        color: #2d3748;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px 0;
        width: 100%;
        text-align: left;
    }
    
    .nav-button:hover {
        background: #667eea;
        color: white;
        transform: translateX(5px);
    }
    
    /* Form styling */
    .form-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
        color: #2d3748;
    }
    
    .form-input {
        width: 100%;
        padding: 12px;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        transition: border-color 0.3s ease;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Alert styling */
    .alert {
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: rgba(72, 187, 120, 0.1);
        border-color: #48bb78;
        color: #22543d;
    }
    
    .alert-warning {
        background: rgba(237, 137, 54, 0.1);
        border-color: #ed8936;
        color: #744210;
    }
    
    .alert-error {
        background: rgba(245, 101, 101, 0.1);
        border-color: #f56565;
        color: #742a2a;
    }
    
    .alert-info {
        background: rgba(66, 153, 225, 0.1);
        border-color: #4299e1;
        color: #2a4365;
    }
    
    /* Progress bar styling */
    .progress-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background: #2d3748;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Responsive grid */
    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 30px;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 50px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 15px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in-left {
        animation: slideInLeft 0.5s ease-out;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .slide-in-right {
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Print styles */
    @media print {
        .main .block-container {
            background: white !important;
        }
        
        .info-card, .metric-card, .data-table, .chart-container {
            background: white !important;
            box-shadow: none !important;
            border: 1px solid #ddd !important;
        }
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 10px;
        }
        
        .app-header {
            padding: 20px;
        }
        
        .app-header h1 {
            font-size: 2rem;
        }
        
        .responsive-grid {
            grid-template-columns: 1fr;
        }
        
        .css-1d391kg {
            width: 100%;
            min-width: 100%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_header(title, subtitle="", icon="🏢"):
    """Create a standardized header for applications"""
    st.markdown(f"""
    <div class="app-header">
        <h1>{icon} {title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_metric_row(metrics_data):
    """Create a row of metric cards"""
    cols = st.columns(len(metrics_data))
    
    for i, (title, value, subtitle, color, icon) in enumerate(metrics_data):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
                <h3 style="color: {color}; margin: 10px 0; font-size: 1.8rem;">{value}</h3>
                <h4 style="margin: 5px 0; color: #333; font-size: 1rem;">{title}</h4>
                <p style="font-size: 12px; color: #666; margin: 0;">{subtitle}</p>
            </div>
            """, unsafe_allow_html=True)

def create_info_section(title, content, icon="ℹ️"):
    """Create a standardized info section"""
    st.markdown(f"""
    <div class="info-card">
        <h3 style="color: #667eea; margin-bottom: 15px; display: flex; align-items: center;">
            <span style="margin-right: 10px; font-size: 1.5rem;">{icon}</span>
            {title}
        </h3>
        <div style="color: #333; line-height: 1.6;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_navigation_section(title, buttons_data):
    """Create a navigation section with buttons"""
    st.markdown(f"""
    <div class="nav-section">
        <h4 style="margin-bottom: 15px; color: white;">{title}</h4>
    """, unsafe_allow_html=True)
    
    for button_text, button_icon in buttons_data:
        if st.button(f"{button_icon} {button_text}", key=f"nav_{button_text}"):
            st.session_state.nav_action = button_text
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_form_section(title, fields_data):
    """Create a standardized form section"""
    st.markdown(f"""
    <div class="form-container">
        <h3 style="color: #667eea; margin-bottom: 20px;">{title}</h3>
    """, unsafe_allow_html=True)
    
    form_data = {}
    for field_name, field_type, field_label, field_placeholder in fields_data:
        if field_type == "text":
            form_data[field_name] = st.text_input(field_label, placeholder=field_placeholder)
        elif field_type == "number":
            form_data[field_name] = st.number_input(field_label)
        elif field_type == "select":
            form_data[field_name] = st.selectbox(field_label, field_placeholder)
        elif field_type == "textarea":
            form_data[field_name] = st.text_area(field_label, placeholder=field_placeholder)
    
    st.markdown("</div>", unsafe_allow_html=True)
    return form_data

def create_alert(message, alert_type="info", icon="ℹ️"):
    """Create a standardized alert message"""
    alert_classes = {
        "success": "alert-success",
        "warning": "alert-warning", 
        "error": "alert-error",
        "info": "alert-info"
    }
    
    alert_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    alert_class = alert_classes.get(alert_type, "alert-info")
    alert_icon = alert_icons.get(alert_type, "ℹ️")
    
    st.markdown(f"""
    <div class="alert {alert_class}">
        <strong>{alert_icon} {alert_type.title()}:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def create_progress_section(title, current_value, max_value, description=""):
    """Create a progress section"""
    percentage = (current_value / max_value) * 100 if max_value > 0 else 0
    
    st.markdown(f"""
    <div class="progress-container">
        <h4 style="margin-bottom: 15px; color: #2d3748;">{title}</h4>
        {f'<p style="margin-bottom: 15px; color: #666;">{description}</p>' if description else ''}
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%"></div>
        </div>
        <p style="margin-top: 10px; text-align: center; font-weight: 600; color: #667eea;">
            {current_value} / {max_value} ({percentage:.1f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_tooltip(text, tooltip_text):
    """Create a tooltip element"""
    st.markdown(f"""
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """, unsafe_allow_html=True)

def create_loading_section(text="Processing..."):
    """Create a loading section"""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px;">
        <div class="loading-spinner"></div>
        <p style="margin-top: 15px; color: #667eea; font-weight: 600;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def create_footer():
    """Create a standardized footer"""
    st.markdown("""
    <div class="footer">
        <p>Enterprise Analytics Platform | Built with Streamlit | All Rights Reserved</p>
        <p style="font-size: 12px; margin-top: 10px;">Powered by Advanced Analytics & AI Insights</p>
    </div>
    """, unsafe_allow_html=True)
