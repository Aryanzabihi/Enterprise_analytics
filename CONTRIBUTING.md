# Contributing to AzIntelligence

Thank you for your interest in contributing to AzIntelligence! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions from the community! There are many ways to contribute:

- **Bug Reports**: Report bugs or issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with code improvements
- **Documentation**: Help improve documentation and examples
- **Testing**: Test the application and report issues
- **Community Support**: Help other users in discussions

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of Streamlit, Python, and web development

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/azintelligence.git
   cd azintelligence
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main_dashboard.py
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, readable code
- Follow the existing code style
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes
- Test the application locally
- Ensure all functionality works as expected
- Check for any console errors

### 4. Commit Your Changes
```bash
git add .
git commit -m "Add: brief description of your changes"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with a clear description of your changes.

## 🎨 Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add type hints where appropriate
- Maximum line length: 88 characters (Black formatter)

### Streamlit Best Practices
- Use descriptive keys for all Streamlit components
- Organize code into logical sections
- Use session state for data persistence
- Implement proper error handling

### File Organization
- Keep related functionality together
- Use descriptive file names
- Separate concerns (UI, logic, data)
- Follow the existing project structure

## 🧪 Testing Guidelines

### Manual Testing
- Test all major functionality
- Test on different browsers
- Test responsive design on mobile
- Verify error handling works correctly

### Code Quality
- Ensure no syntax errors
- Check for unused imports
- Verify consistent formatting
- Test edge cases

## 📚 Documentation Standards

### Code Comments
- Add docstrings to functions and classes
- Explain complex logic with inline comments
- Keep comments up-to-date with code changes

### README Updates
- Update README.md if adding new features
- Include installation steps for new dependencies
- Update usage examples if needed

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, browser)
5. **Screenshots** if applicable
6. **Error messages** from console

## 💡 Feature Requests

When suggesting features:

1. **Clear description** of the feature
2. **Use case** and benefits
3. **Implementation suggestions** if you have ideas
4. **Priority level** (low, medium, high)

## 🔄 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No console errors
- [ ] Feature is tested thoroughly

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested locally
- [ ] All functionality works
- [ ] No console errors

## Screenshots (if applicable)
Add screenshots here

## Additional Notes
Any additional information
```

## 📋 Code Review Process

1. **Automated Checks**: GitHub Actions will run basic checks
2. **Review**: Maintainers will review your code
3. **Feedback**: You may receive feedback and requested changes
4. **Approval**: Once approved, your PR will be merged

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 🆘 Getting Help

If you need help with your contribution:

1. **Check existing issues** for similar problems
2. **Search discussions** for solutions
3. **Create a new issue** with your question
4. **Join our community** discussions

## 📄 License

By contributing to AzIntelligence, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor hall of fame

---

Thank you for contributing to AzIntelligence! Your help makes this project better for everyone. 🚀
