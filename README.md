# 🏢 AzIntelligence - Enterprise Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AzIntelligence** is a comprehensive, integrated analytics platform that consolidates all business department applications into a single, unified dashboard. Built with Streamlit, it provides seamless navigation between different business functions while maintaining the individual capabilities of each department's specialized analytics tools.

## ✨ Features

### 🎯 **Unified Dashboard**
- **Single Entry Point**: One main dashboard to access all departments
- **Consistent UI/UX**: Unified styling and navigation across all applications
- **Cross-Department Navigation**: Easy switching between business functions
- **Modern Design**: Professional, enterprise-ready interface

### 📊 **Integrated Departments**
- **📦 Procurement & Supply Chain** - Supplier management, cost optimization, risk assessment
- **🎧 Customer Support** - Ticket management, customer satisfaction, agent performance
- **💰 Finance & Accounting** - Financial analysis, budgeting, forecasting, risk management
- **👥 Human Resources** - Employee analytics, performance management, workforce planning
- **💻 Information Technology** - IT infrastructure, system performance, cybersecurity
- **📊 Marketing & Analytics** - Campaign performance, customer acquisition, ROI analysis
- **🔬 Research & Development** - Innovation metrics, project tracking, patent analysis
- **📈 Sales & Revenue** - Sales performance, pipeline analysis, forecasting

### 🚀 **Key Capabilities**
- **Dynamic Module Loading**: Seamlessly loads department applications
- **Session State Management**: Maintains user context across navigation
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live data refresh and monitoring
- **Export Functionality**: Download data in Excel and CSV formats
- **AI-Powered Insights**: Intelligent recommendations and analytics

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryanzabihi/azintelligence.git
   cd azintelligence
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run main_dashboard.py
   ```

4. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`

### Alternative Installation (Windows)
- Double-click `run_integrated_dashboard.bat`

## 📁 Project Structure

```
azintelligence/
├── main_dashboard.py              # Main entry point and dashboard
├── department_router.py           # Department routing and integration
├── shared_components.py           # Reusable UI components
├── unified_styling.py            # Centralized styling system
├── requirements.txt               # Python dependencies
├── run_integrated_dashboard.bat  # Windows launcher script
├── README.md                     # This documentation
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore file
├── pro/                          # Procurement application
├── cs/                           # Customer Support application
├── fin/                          # Finance application
├── hr/                           # HR application
├── IT/                           # IT application
├── marketing/                    # Marketing application
├── RD/                           # R&D application
└── sale/                         # Sales application
```

## 🎮 Usage

### 🏠 **Main Dashboard**
1. **Launch the Application**: Run `main_dashboard.py`
2. **View Overview**: See enterprise-wide metrics and status
3. **Navigate Departments**: Use sidebar or department cards
4. **Quick Actions**: Access common functions and tools

### 🚀 **Department Applications**
1. **Select Department**: Click on any department card or sidebar button
2. **Launch Application**: The department app will load automatically
3. **Use Features**: Access all department-specific analytics and tools
4. **Return to Main**: Use the "Back to Main Dashboard" button

## 🔧 Configuration

### Environment Setup
- **Virtual Environment**: Recommended to use `.venv/`
- **Python Path**: Department directories are automatically added to `sys.path`
- **Streamlit Config**: Uses `.streamlit/` directory for configuration

### Customization Options
- **Styling**: Modify `unified_styling.py` for custom themes
- **Components**: Extend `shared_components.py` for new UI elements
- **Routing**: Update `department_router.py` for new departments
- **Branding**: Change company name and colors in main dashboard

## 📊 Data Sources

### Supported Formats
- **Excel Files** (.xlsx, .xls)
- **CSV Files** (.csv)
- **Data Templates**: Pre-configured templates for each department

### Data Management
- **Upload Interface**: Drag-and-drop file upload
- **Validation**: Automatic data format checking
- **Storage**: Session-based data management
- **Export**: Download processed data and reports

## 🌟 Advanced Features

### 🔍 **Cross-Department Analytics**
- **Unified Data View**: Access data from multiple departments
- **Comparative Analysis**: Compare metrics across business functions
- **Integrated Reporting**: Generate comprehensive enterprise reports

### 🤖 **AI and Machine Learning**
- **Predictive Analytics**: Forecast trends and outcomes
- **Intelligent Insights**: Automated recommendations
- **Pattern Recognition**: Identify business opportunities and risks

### 📱 **Mobile and Responsive**
- **Mobile Optimization**: Touch-friendly interface
- **Responsive Design**: Adapts to different screen sizes
- **Cross-Platform**: Works on all modern browsers

## 🔒 Security

### Data Protection
- **Local Processing**: Data stays on your system
- **No External Sharing**: All analytics run locally
- **Session Management**: Secure user session handling

### Access Control
- **Department Isolation**: Separate data access per department
- **User Permissions**: Configurable access levels
- **Audit Trail**: Track user actions and data access

## 🚀 Deployment

### Local Development
```bash
# Development mode
streamlit run main_dashboard.py --server.port 8501
```

### Production Deployment
```bash
# Production mode
streamlit run main_dashboard.py --server.headless true
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**Department Not Loading**
- Check if department file exists in correct directory
- Verify Python dependencies are installed
- Check console for error messages

**Navigation Issues**
- Clear browser cache and cookies
- Restart the Streamlit application
- Check session state in Streamlit

**Styling Problems**
- Ensure all CSS files are properly loaded
- Check browser compatibility
- Verify file paths are correct

### Performance Optimization
- **Large Datasets**: Use data sampling for initial analysis
- **Memory Management**: Close unused department applications
- **Browser Performance**: Use modern browsers for best experience

## 🔮 Roadmap

### Planned Features
- **User Authentication**: Multi-user login system
- **Database Integration**: Connect to external databases
- **Real-time Data**: Live data streaming and updates
- **Advanced Analytics**: More sophisticated ML models
- **API Integration**: Connect to external business systems

### Extensibility
- **Plugin System**: Add new departments easily
- **Custom Themes**: User-defined styling options
- **Workflow Automation**: Automated data processing pipelines
- **Third-party Integrations**: Connect to popular business tools

## 📞 Support

### Getting Help
- **Documentation**: Refer to this README first
- **Code Comments**: Check inline documentation in source files
- **Error Messages**: Review console output for debugging
- **Issues**: Create an issue on GitHub for bugs or feature requests

### Community
- **Discussions**: Join our [GitHub Discussions](https://github.com/aryanzabihi/azintelligence/discussions)
- **Wiki**: Check our [Wiki](https://github.com/aryanzabihi/azintelligence/wiki) for detailed guides

## 🙏 Acknowledgments

- **Streamlit Team** for the amazing framework
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation
- **Open Source Community** for inspiration and support

---

## 👨‍💻 Developer

**Developed with ❤️ by [Aryan Zabihi](https://github.com/aryanzabihi)**

- **GitHub**: [@aryanzabihi](https://github.com/aryanzabihi)
- **LinkedIn**: [Aryan Zabihi](https://linkedin.com/in/aryanzabihi)

---

**AzIntelligence** - Where Business Intelligence Meets Innovation

*Built with ❤️ using Streamlit and Python*
