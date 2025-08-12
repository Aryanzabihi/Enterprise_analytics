# 📊 Procurement Analytics Dashboard

A comprehensive Streamlit-based analytics dashboard for procurement professionals to measure, analyze, and optimize procurement performance across multiple key areas.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This application provides real-time analytics and insights for procurement operations, helping organizations optimize costs, improve supplier relationships, enhance compliance, and drive strategic procurement decisions.

## 🚀 Features

### 📈 **9 Core Analytics Categories:**

1. **💰 Spend Analysis**
   - Total spend by category, supplier, and department
   - Budget utilization tracking
   - Tail spend analysis (Pareto charts)
   - Spend trends and patterns

2. **🏭 Supplier Performance & Management**
   - On-time delivery rate analysis
   - Supplier defect rate monitoring
   - Lead time analysis by supplier
   - Supplier risk assessment

3. **💵 Cost & Savings Analysis**
   - Cost savings from negotiation
   - Procurement cost per purchase order
   - Total Cost of Ownership (TCO)
   - Unit cost trends
   - Savings from supplier consolidation

4. **⚡ Process Efficiency**
   - Purchase order cycle time
   - Procurement lead time
   - Requisition-to-payment cycle
   - Procurement automation metrics
   - Workload distribution

5. **📋 Compliance & Risk Management**
   - Contract compliance rate
   - Policy compliance monitoring
   - Procurement fraud analysis
   - Ethical sourcing compliance
   - Regulatory compliance trends

6. **📦 Inventory Management**
   - Inventory turnover rate
   - Stockout rate analysis
   - Excess inventory identification
   - Just-in-Time procurement efficiency

7. **🌍 Market Insights**
   - Market price benchmarking
   - Supplier market share analysis
   - Vendor location risk assessment
   - Industry procurement trends
   - Sourcing opportunities analysis

8. **📄 Contract Management**
   - Contract value analysis
   - Contract performance metrics
   - Contract renewal analysis
   - Contract compliance monitoring
   - Contract risk assessment

9. **🌱 Sustainability & CSR**
   - Sustainability metrics
   - CSR impact analysis
   - Green procurement metrics
   - Carbon footprint analysis
   - Sustainable supplier development

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- pip package manager

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/procurement-analytics.git
   cd procurement-analytics/pro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_simple.txt
   ```

3. **Run the application**
   ```bash
   streamlit run pro.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to access the dashboard

### **Data Setup**
- The application comes with sample data (`pro.xlsx`)
- You can upload your own data through the Data Input section
- Supported formats: Excel (.xlsx, .xls), CSV

## 🎨 **Professional UI Features:**

- **Vibrant Professional Color Scheme**: Deep navy blues, vibrant reds, bright oranges, professional teals, and forest greens
- **Interactive Dashboards**: Real-time metrics with color-coded performance indicators
- **Enhanced Visualizations**: Professional charts with business-appropriate color palettes
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Data Export**: Excel export functionality for all analytics

## 📊 **Data Schema**

The application works with 8 core data tables:

### **1. Suppliers** (`suppliers`)
- `supplier_id`, `supplier_name`, `country`, `region`
- `registration_date`, `diversity_flag`, `esg_score`, `certifications`

### **2. Items** (`items_data`)
- `item_id`, `item_name`, `category`, `unit`
- `recyclable_flag`, `carbon_score`

### **3. Purchase Orders** (`purchase_orders`)
- `po_id`, `order_date`, `department`, `supplier_id`, `item_id`
- `quantity`, `unit_price`, `delivery_date`, `currency`, `budget_code`

### **4. Contracts** (`contracts`)
- `contract_id`, `supplier_id`, `start_date`, `end_date`
- `contract_value`, `volume_commitment`, `dispute_count`, `compliance_status`

### **5. Deliveries** (`deliveries`)
- `delivery_id`, `po_id`, `delivery_date`, `delivered_quantity`
- `defect_flag`, `defect_notes`

### **6. Invoices** (`invoices`)
- `invoice_id`, `po_id`, `invoice_date`, `payment_date`, `invoice_amount`

### **7. Budgets** (`budgets`)
- `budget_code`, `department`, `category`, `fiscal_year`, `budget_amount`

### **8. RFQs** (`rfqs`)
- `rfq_id`, `supplier_id`, `item_id`, `unit_price`, `response_date`

## 🤝 **Contributing**

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### **Development Setup**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Built with [Streamlit](https://streamlit.io/)
- Data visualization powered by [Plotly](https://plotly.com/)
- Analytics powered by [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)

4. **Access the dashboard:**
   - Open your browser to `http://localhost:8501`
   - The application will load with sample data

## 📋 **Getting Started**

### **1. Data Input**
- **Download Template**: Use the "Download Template" button to get an Excel file with the correct schema
- **Upload Data**: Upload your procurement data using the "Upload Data" feature
- **Manual Entry**: Enter data manually through the data input forms

### **2. Sample Data**
- The application includes `procurement_sample_dataset.xlsx` with realistic sample data
- Use this to explore all features and understand the data structure

### **3. Analytics Navigation**
- Use the tab navigation to explore different analytics categories
- Each section provides detailed metrics, visualizations, and insights
- Export data and charts for reporting

## 🎨 **Professional Color Scheme**

The application uses a sophisticated, business-appropriate color palette:

- **Primary Blue**: `#1e3c72` to `#2a5298` (Trust, professionalism)
- **Vibrant Red**: `#E63946` to `#A8DADC` (Energy, attention)
- **Bright Orange**: `#FF6B35` to `#F7931E` (Creativity, enthusiasm)
- **Professional Teal**: `#2E86AB` to `#A23B72` (Sophistication, reliability)
- **Forest Green**: `#1A936F` to `#88D498` (Growth, success)

## 📊 **Key Metrics Explained**

### **Spend Analysis Metrics:**
- **Total Spend**: Overall procurement expenditure
- **Spend by Category**: Distribution across product/service categories
- **Budget Utilization**: Actual vs. budgeted spend comparison
- **Tail Spend**: Analysis of low-value, high-volume transactions

### **Supplier Performance Metrics:**
- **On-Time Delivery Rate**: Percentage of deliveries meeting deadlines
- **Defect Rate**: Quality issues in delivered goods/services
- **Lead Time**: Time from order to delivery
- **Risk Score**: Supplier risk assessment based on multiple factors

### **Cost & Savings Metrics:**
- **Cost Savings**: Negotiated savings vs. initial quotes
- **TCO**: Total cost including acquisition, operation, and disposal
- **Unit Cost Trends**: Price movement over time
- **Consolidation Savings**: Potential savings from supplier consolidation

## 🔧 **Customization Options**

### **Adding New Metrics:**
1. Add calculation functions to `metrics_calculator.py`
2. Update the main application in `pro_app.py`
3. Add corresponding data schema if needed

### **Modifying Visualizations:**
- Update chart colors in the professional color palette
- Modify chart types and layouts
- Add new interactive features

### **Data Integration:**
- Connect to external databases
- Integrate with ERP systems
- Add real-time data feeds

## 📈 **Use Cases**

### **For Procurement Managers:**
- Monitor spend patterns and identify cost-saving opportunities
- Track supplier performance and manage relationships
- Ensure compliance with procurement policies
- Optimize inventory levels and reduce stockouts

### **For Finance Teams:**
- Track budget utilization and variance analysis
- Monitor procurement costs and savings
- Analyze total cost of ownership
- Support financial planning and forecasting

### **For Operations Teams:**
- Monitor delivery performance and lead times
- Track quality metrics and defect rates
- Optimize procurement processes
- Manage supplier relationships

### **For Compliance Teams:**
- Monitor policy compliance rates
- Track regulatory requirements
- Identify potential fraud or risks
- Ensure ethical sourcing practices

## 🔒 **Data Privacy & Security**

- All data is processed locally on your machine
- No data is transmitted to external servers
- Excel files are stored locally
- Session data is cleared when the application is closed

## 🤝 **Contributing**

### **Guidelines:**
1. Follow the existing code structure and naming conventions
2. Add comprehensive documentation for new features
3. Test thoroughly before submitting changes
4. Maintain the professional color scheme and UI standards

### **Areas for Enhancement:**
- Additional analytics categories
- Advanced visualization options
- Integration with external systems
- Real-time data processing
- Mobile optimization

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

### **Common Issues:**
- **Data Import Errors**: Ensure your Excel file matches the required schema
- **Chart Display Issues**: Check that all required columns are present
- **Performance Issues**: Large datasets may require optimization

### **Getting Help:**
- Check the data schema requirements
- Verify your data format matches the template
- Review the sample data for reference

## 📊 **Version History**

### **v1.0.0** (Current)
- Initial release with 9 core analytics categories
- Professional UI with vibrant color scheme
- Complete data schema and sample data
- Excel import/export functionality
- Interactive dashboards and visualizations

---

**🎯 Transform your procurement operations with data-driven insights and professional analytics!** 