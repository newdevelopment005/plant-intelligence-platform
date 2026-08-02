# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

The Plant Intelligence Platform takes security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities.
2. Email security reports to: **security@pip-platform.org** (or your designated security contact)
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Assessment**: Within 5 business days
- **Resolution**: Critical vulnerabilities within 30 days
- **Disclosure**: Coordinated disclosure after fix is released

## Security Measures

### Authentication & Authorization

- **JWT Tokens**: Short-lived access tokens (30 min) with refresh tokens (7 days)
- **RBAC**: Role-based access control with 5 permission levels
- **Password Hashing**: bcrypt with work factor 12
- **Rate Limiting**: API rate limits (100 req/min general, 30 req/min for AI endpoints)

### Data Protection

- **Encryption at Rest**: Database volumes encrypted via cloud provider
- **Encryption in Transit**: TLS/HTTPS for all production deployments
- **Secrets Management**: Environment variables, never committed to repository
- **Input Validation**: Pydantic schemas validate all API inputs
- **SQL Injection**: SQLAlchemy ORM prevents raw SQL injection

### Infrastructure

- **Docker**: Non-root containers where possible
- **Network Isolation**: Services communicate via dedicated Docker network
- **Database Access**: Restricted to application services only
- **CORS**: Configurable allowed origins

### API Security

- **Rate Limiting**: Nginx-based rate limiting per IP
- **Request Size Limits**: 100MB for API, 50MB for AI service
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Error Handling**: No sensitive data leaked in error responses

## Security Checklist for Deployment

- [ ] Change all default passwords in `.env`
- [ ] Generate unique `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure CORS origins for your domain
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set `DEBUG=false` in production
- [ ] Restrict database ports to internal network
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular dependency updates (`pip audit`, `npm audit`)
- [ ] Database backup encryption

## Dependencies

We regularly audit dependencies for known vulnerabilities:

- **Python**: `pip-audit` in CI pipeline
- **Node.js**: `npm audit` in CI pipeline
- **Docker**: Base image updates monthly

## Contact

For security-related questions or concerns, contact:
- Email: security@pip-platform.org
- GitHub Security Advisories: Use the "Security" tab in the repository
