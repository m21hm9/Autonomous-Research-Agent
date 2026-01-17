# Contributing to DeepSeek Research Agent

Thank you for your interest in contributing! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

We'd love to hear your ideas! Open an issue with:
- A clear description of the feature
- Use cases and examples
- Potential implementation approach (if you have one)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the coding style and add tests if applicable
4. **Commit your changes**: Use clear, descriptive commit messages
5. **Push to your fork**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**: Provide a clear description of your changes

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/Autonomous-Research-Agent.git
   cd Autonomous-Research-Agent/my-deepseek-researcher
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up your `.env` file with API keys (see README.md)

4. Test your changes:
   ```bash
   streamlit run app.py
   ```

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

## Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Be specific about what changed
- Reference issue numbers if applicable

Examples:
- `Add error handling for API rate limits`
- `Fix typo in README.md`
- `Update dependencies to latest versions`

## Questions?

Feel free to open an issue for any questions or discussions. We're here to help!

Thank you for contributing! 🎉

