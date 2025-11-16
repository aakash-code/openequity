# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of OpenEquity seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability in public forums, chat rooms, or social media

### Please DO:

1. **Email us directly** at security@openequity.org (coming soon)
   - Or create a [Security Advisory](https://github.com/yourusername/openequity/security/advisories/new) on GitHub

2. **Include the following information:**
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability and how an attacker might exploit it

3. **Allow us time to respond:**
   - We will acknowledge your email within 48 hours
   - We will send a more detailed response within 7 days
   - We will work with you to understand and resolve the issue
   - We will keep you informed of our progress

### What to expect:

- We will confirm receipt of your vulnerability report
- We will investigate and validate the vulnerability
- We will work on a fix and coordinate disclosure
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Disclosure Policy

- We will publish security advisories for confirmed vulnerabilities
- We follow responsible disclosure practices
- We aim to patch critical vulnerabilities within 30 days
- We will coordinate public disclosure with the reporter

## Security Best Practices

If you're using OpenEquity, please follow these best practices:

### For Users:
- Use strong, unique passwords
- Enable two-factor authentication when available
- Keep your software up to date
- Don't share API keys or credentials
- Review permission requests carefully

### For Developers:
- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Keep dependencies up to date
- Follow OWASP security guidelines
- Run security scans regularly
- Validate all user inputs
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Use HTTPS in production
- Implement rate limiting
- Log security-relevant events

## Security Features

OpenEquity implements the following security features:

- **Authentication:** OAuth 2.0 + JWT tokens
- **Authorization:** Role-based access control (RBAC)
- **Encryption:** HTTPS/TLS for data in transit
- **Password Security:** bcrypt hashing
- **API Security:** Rate limiting, input validation
- **Database Security:** Parameterized queries, prepared statements
- **XSS Protection:** Content Security Policy headers
- **CSRF Protection:** CSRF tokens for state-changing operations
- **Audit Logging:** Security-relevant events logged
- **Dependency Scanning:** Automated vulnerability checks

## Security Updates

We use automated tools to monitor dependencies for vulnerabilities:

- **Dependabot:** Automated dependency updates
- **Snyk:** Vulnerability scanning
- **CodeQL:** Static code analysis
- **GitHub Security Advisories:** Alerts for known vulnerabilities

## Compliance

OpenEquity is working towards:

- GDPR compliance
- SOC 2 Type II compliance pathway
- OWASP Top 10 coverage
- WCAG 2.1 AA accessibility

## Hall of Fame

We appreciate security researchers who help us keep OpenEquity secure. Contributors who responsibly disclose vulnerabilities will be recognized here (with their permission):

<!-- Hall of Fame will be updated as researchers contribute -->

## Contact

- **Security Issues:** security@openequity.org (coming soon)
- **General Inquiries:** contact@openequity.org (coming soon)
- **GitHub Security Advisories:** [Link](https://github.com/yourusername/openequity/security/advisories)

---

Thank you for helping keep OpenEquity and our users safe!
