# Contributing to AI Video Creator

Thank you for your interest in contributing to AI Video Creator! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone your fork of the repository:
   ```bash
   git clone https://github.com/yourusername/ai-video-creator.git
   cd ai-video-creator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. Create a `.env` file with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Running Tests

Run the test suite:
```bash
python test.py
```

## Code Style

Please follow these style guidelines:

- Use 4 spaces for indentation
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep lines under 100 characters when possible

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the version number in setup.py following semantic versioning
3. The PR will be merged once it has been reviewed and approved

## Feature Requests

If you have a feature request, please open an issue and describe:

- What you want to achieve
- Why this feature would be useful
- Any implementation ideas you have

## Bug Reports

When reporting bugs, please include:

- A clear description of the bug
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, etc.)

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.