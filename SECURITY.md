# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

## Reporting a Vulnerability

We take the security of crowdstrike-latest-news seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: starkarthikr@gmail.com
- **Subject**: [SECURITY] Vulnerability in crowdstrike-latest-news

### What to Include in Your Report

Please include the following information:
- Type of vulnerability (e.g., XSS, SQL injection, credential exposure)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability and how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed of the progress toward resolving the vulnerability
- **Timeline**: We aim to resolve critical vulnerabilities within 7 days
- **Credit**: We will credit you in our security advisories (unless you prefer to remain anonymous)

### Security Update Process

1. Vulnerability reported and confirmed
2. Security patch developed and tested
3. Security advisory published
4. Patch released and deployed
5. Public disclosure after fix is deployed

## Security Best Practices

When using this project:
- Never commit API keys, passwords, or other secrets to the repository
- Always use GitHub Secrets for sensitive credentials
- Keep dependencies up to date (we use Dependabot for this)
- Review security advisories regularly
- Enable branch protection on your forks

## Security Features

This repository includes:
- Dependabot security updates
- CodeQL security scanning
- Hardened GitHub Actions workflows
- Dependency review on pull requests
- Regular security audits

## Contact

- **Security Issues**: starkarthikr@gmail.com
- **General Issues**: [GitHub Issues](https://github.com/starkarthikr/crowdstrike-latest-news/issues)

---

**Last Updated**: February 10, 2026
