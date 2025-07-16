# 🤝 Contributing to LifafaV0

Thank you for your interest in contributing to LifafaV0! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- MongoDB (local or cloud)
- Required API keys (OpenAI, Mem0, Google OAuth)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/LifafaV0.git
   cd LifafaV0
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/original-owner/LifafaV0.git
   ```

## 🔧 Development Setup

### 1. Environment Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # if available
```

### 2. Environment Configuration

```bash
# Copy environment template
cp backend/env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY, MEM0_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
```

### 3. Database Setup

```bash
# Start MongoDB (if using local)
brew services start mongodb/brew/mongodb-community  # macOS
sudo systemctl start mongod  # Ubuntu

# Or use Docker
docker run -d --name mongodb -p 27017:27017 mongo:7.0
```

### 4. Run Development Server

```bash
# Start the development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the Makefile
make dev
```

## 📝 Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications:

- **Line Length**: 120 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped and sorted
- **Docstrings**: Google style docstrings

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black app/ --line-length 120
isort app/ --profile black

# Check code style
flake8 app/ --max-line-length=120 --ignore=E501,W503
```

### Type Hints

- Use type hints for all function parameters and return values
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]`, etc. for collections

Example:
```python
from typing import Optional, List, Dict, Any

def process_emails(
    user_id: str,
    email_ids: List[str],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a list of emails for a user."""
    pass
```

### Documentation

- All public functions must have docstrings
- Use Google style docstrings
- Include type information in docstrings

Example:
```python
def extract_financial_data(email_content: str) -> Dict[str, Any]:
    """Extract financial transaction data from email content.
    
    Args:
        email_content: The raw email content to analyze.
        
    Returns:
        A dictionary containing extracted financial data including:
        - amount: Transaction amount
        - merchant: Merchant name
        - category: Transaction category
        - confidence: Extraction confidence score
        
    Raises:
        ValueError: If email content is empty or invalid.
    """
    pass
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_gmail_service.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

Example:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.gmail_service import GmailService

class TestGmailService:
    @pytest.mark.asyncio
    async def test_fetch_emails_success(self):
        # Arrange
        mock_gmail_client = Mock()
        mock_gmail_client.messages().list().execute.return_value = {
            'messages': [{'id': 'test_id'}]
        }
        
        # Act
        with patch('app.services.gmail_service.build') as mock_build:
            mock_build.return_value = mock_gmail_client
            service = GmailService()
            result = await service.fetch_emails('user_id')
            
        # Assert
        assert result is not None
        assert len(result) > 0
```

### Test Coverage

- Aim for at least 80% code coverage
- Focus on critical business logic
- Test both success and error scenarios

## 🔄 Pull Request Process

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-description
```

### 2. Make Your Changes

- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Test your changes thoroughly

### 3. Commit Guidelines

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(gmail): add batch email processing
fix(auth): resolve OAuth token refresh issue
docs(api): update endpoint documentation
```

### 4. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR on GitHub
```

### 5. Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is adequate
- [ ] Documentation is updated
- [ ] No sensitive data is included
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes

### 6. Review Process

- All PRs require at least one review
- Address review comments promptly
- Maintainers may request changes
- PRs are merged after approval

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - OS and version
   - Python version
   - Package versions
   - Browser (if applicable)
5. **Error messages** and stack traces
6. **Screenshots** (if applicable)

### Issue Template

```markdown
## Bug Description
Brief description of the issue.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.11.0]
- Package versions: [if relevant]

## Additional Information
Any other context, logs, or screenshots.
```

## 💡 Feature Requests

### Feature Request Guidelines

- Describe the feature clearly
- Explain the use case and benefits
- Consider implementation complexity
- Check if similar features exist

### Feature Request Template

```markdown
## Feature Description
Clear description of the requested feature.

## Use Case
How this feature would be used and why it's needed.

## Proposed Implementation
Optional: Suggestions for implementation approach.

## Alternatives Considered
Optional: Other approaches that were considered.

## Additional Context
Any other relevant information.
```

## 📚 Documentation

### Documentation Guidelines

- Keep documentation up to date
- Use clear, concise language
- Include code examples
- Update API documentation for new endpoints

### Documentation Types

1. **Code Documentation**: Docstrings and comments
2. **API Documentation**: OpenAPI/Swagger specs
3. **User Documentation**: README, guides, tutorials
4. **Developer Documentation**: Architecture, setup guides

### Updating Documentation

- Update relevant docs when adding features
- Include examples for new functionality
- Review existing docs for accuracy
- Use consistent formatting and style

## 🏗️ Project Structure

Understanding the project structure helps with contributions:

```
LifafaV0/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── config/         # Configuration
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── workers/        # Background tasks
│   ├── tests/              # Test files
│   └── requirements.txt    # Dependencies
├── frontend/               # Web interface
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🆘 Getting Help

### Resources

- [Project README](README.md)
- [Backend Documentation](backend/readme.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Issues](https://github.com/original-owner/LifafaV0/issues)

### Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and general discussion
- Be respectful and constructive in all communications

## 🙏 Recognition

Contributors will be recognized in:

- Project README
- Release notes
- GitHub contributors page
- Documentation acknowledgments

Thank you for contributing to LifafaV0! 🚀 