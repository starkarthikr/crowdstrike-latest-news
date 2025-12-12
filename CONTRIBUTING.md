# Contributing to CrowdStrike Monitor

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR-USERNAME/crowdstrike-monitor.git
   cd crowdstrike-monitor
   ```
3. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs
- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include detailed steps to reproduce
- Provide environment information
- Check if the issue already exists

### Suggesting Features
- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the use case clearly
- Consider if it aligns with project goals

### Improving Documentation
- Fix typos or clarify existing docs
- Add examples or use cases
- Update outdated information

## Development Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pylint black flake8 safety bandit
```

### Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Never commit .env file!
```

## Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Maximum line length: 100 characters

### Code Quality Tools
```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Check with Pylint
pylint **/*.py

# Security scan
bandit -r .
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** under [Unreleased]
5. **Create pull request** with clear description
6. **Link related issues** in PR description

### PR Requirements
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented complex sections
- [ ] Updated documentation
- [ ] Added/updated tests
- [ ] All tests passing
- [ ] No merge conflicts
- [ ] CHANGELOG.md updated
- [ ] No sensitive data included

### Commit Messages
Follow conventional commits format:
```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(monitor): add support for CrowdStrike threat reports
fix(parser): handle missing RSS feed items gracefully
docs(readme): update installation instructions
```

## Review Process

1. Maintainers review PRs within 3-5 business days
2. Address review comments
3. Request re-review after changes
4. PR merged after approval

## Questions?

Feel free to:
- Open an issue for discussion
- Contact maintainers at starkarthikr@gmail.com
- Join project discussions

Thank you for contributing! 🎉
