# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Instead, please report it via one of the following methods:

1. **Email**: Send details to the repository maintainer
2. **Private Security Advisory**: Use GitHub's private security advisory feature
3. **Direct Message**: Contact the maintainer through GitHub

### What to Include

When reporting a vulnerability, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response Time

We aim to respond to security reports within 48 hours and provide an initial assessment. We will keep you informed of our progress and work with you to address the issue.

### Security Best Practices

When using this project:

- **Never commit API keys**: Always use environment variables (`.env` file)
- **Keep dependencies updated**: Regularly update packages to get security patches
- **Use secure connections**: Always use HTTPS when making API calls
- **Review code changes**: Before deploying, review all code changes

## Security Considerations

This project uses external APIs (DeepSeek and Tavily). Please ensure:

- API keys are kept secure and never shared
- You understand the data privacy policies of these services
- You comply with all applicable data protection regulations

## Acknowledgments

We appreciate the security research community's efforts to help keep this project secure. Thank you for responsibly disclosing vulnerabilities!

