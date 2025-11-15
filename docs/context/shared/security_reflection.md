# Security Reflection

## Threats Considered

This security sweep addressed several key threats from the OWASP Top 10 and common web application vulnerabilities:

### 1. Injection Attacks (A03:2021)
**Threat:** SQL injection through user input in search queries or form fields.  
**Mitigation:** All database queries use SQLAlchemy ORM with parameterized queries. No string concatenation in SQL. DAL layer enforces this pattern. Existing negative test confirms protection.

### 2. Broken Authentication (A07:2021)
**Threat:** Brute force attacks on login endpoint, session hijacking, weak session management.  
**Mitigation:** 
- Rate limiting on login (5 attempts per minute per IP)
- Secure session cookies (`HttpOnly`, `SameSite=Lax`, `Secure` in production)
- Password hashing with bcrypt
- CSRF protection on all form submissions

### 3. Cross-Site Scripting (XSS) (A03:2021)
**Threat:** Stored or reflected XSS through user-generated content (messages, reviews, resource descriptions).  
**Mitigation:**
- Content Security Policy (CSP) headers restrict inline script execution
- Input sanitization in DAL layer for messages and reviews
- HTML escaping in Jinja2 templates (default behavior)
- CSP allows `'unsafe-inline'` for styles (Bootstrap requirement) but restricts scripts

### 4. Cross-Site Request Forgery (CSRF) (A01:2021)
**Threat:** Unauthorized actions performed via forged requests from malicious sites.  
**Mitigation:**
- Flask-WTF CSRF protection enabled on all forms
- CSRF tokens required for POST requests
- `SameSite=Lax` cookie attribute provides additional protection
- JSON API endpoints exempted but protected by `@login_required`

### 5. Sensitive Data Exposure (A02:2021)
**Threat:** Session cookies, passwords, or user data exposed in transit or storage.  
**Mitigation:**
- Session cookies marked `HttpOnly` (prevents JavaScript access)
- `Secure` flag set in production (HTTPS only)
- Passwords hashed with bcrypt (never stored in plaintext)
- PII redaction in AI prompts

### 6. Broken Access Control (A01:2021)
**Threat:** Unauthorized access to admin functions, other users' bookings, or private message threads.  
**Mitigation:**
- Server-side authorization checks: `require_admin()`, `require_staff_or_admin()`
- Participant verification for messaging (`can_access_booking()`)
- Role-based access control enforced at controller level
- Admin routes protected by `@admin_bp.before_request` decorator

### 7. Security Misconfiguration (A05:2021)
**Threat:** Missing security headers, default credentials, exposed debug information.  
**Mitigation:**
- Security headers on all responses (CSP, X-Frame-Options, etc.)
- `DEBUG=False` in production config
- Secure defaults in `BaseConfig` with production overrides

### 8. Rate Limiting & DoS
**Threat:** Denial of service via rapid requests, resource exhaustion.  
**Mitigation:**
- Rate limiting on login (5/min), write endpoints (10/min)
- In-memory token bucket implementation
- Per-user/IP rate limiting keys

## Implementation Details

### Security Headers
All responses include:
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `Content-Security-Policy` - Restricts resource loading and script execution
- `Referrer-Policy: strict-origin-when-cross-origin` - Limits referrer information leakage
- `Permissions-Policy` - Disables geolocation, microphone, camera

### Rate Limiting
Implemented using in-memory token bucket algorithm:
- Login: 5 attempts per minute per IP
- Write endpoints (bookings, messages, resources): 10 requests per minute per user/IP
- AI endpoints: Already protected by service-layer rate limiting (5 seconds cooldown)

### Input Validation
- Pagination parameters validated and sanitized (`validate_pagination()`)
- Booking datetime validation at controller layer (defense in depth)
- Email validation with `email-validator`
- File upload validation (extension, size, double-extension blocking)

### Authorization Checks
- Admin routes: `@admin_bp.before_request` enforces admin role
- Messaging: `can_access_booking()` verifies participant or admin
- Resource management: `require_staff_or_admin()` for create/edit
- Reviews: Eligibility check (completed booking required)

## Known Limitations

1. **In-Memory Rate Limiting:** Current implementation uses `defaultdict` in memory. This means:
   - Rate limits reset on server restart
   - Not shared across multiple server instances (not suitable for load-balanced deployments)
   - No persistence across restarts

2. **CSP `'unsafe-inline'` for Styles:** Bootstrap 5 and custom CSS require inline styles. This is a common trade-off but reduces XSS protection slightly. Future work could use nonces or hashes.

3. **No Password Reset Flow:** Current implementation lacks password reset functionality. This should be added with secure token generation and expiration.

4. **No 2FA:** Two-factor authentication is not implemented. Consider adding for admin accounts in production.

5. **Session Management:** Sessions don't expire automatically. Consider adding session timeout configuration.

6. **Rate Limiting Granularity:** Current implementation uses IP + user ID, but could be more sophisticated (e.g., per-endpoint limits).

## Future Work

1. **Redis-Based Rate Limiting:** Move rate limiting to Redis for distributed systems and persistence
2. **Stricter CSP:** Implement CSP nonces for inline scripts/styles to remove `'unsafe-inline'`
3. **Password Reset:** Add secure password reset flow with time-limited tokens
4. **Two-Factor Authentication:** Implement 2FA for admin accounts
5. **Session Timeout:** Add configurable session expiration
6. **Security Monitoring:** Add logging and alerting for failed login attempts, CSRF failures
7. **HTTPS Enforcement:** Add middleware to redirect HTTP to HTTPS in production
8. **Security Headers Middleware:** Consider using Flask-Talisman for comprehensive header management
9. **Input Validation Library:** Consider using Marshmallow or Pydantic for schema-based validation
10. **Security Audit Logging:** Enhanced logging of security events (failed auth, privilege escalations)

## Configuration

Production deployment requires:
- `SESSION_COOKIE_SECURE=true` (set in environment)
- `REMEMBER_COOKIE_SECURE=true` (set in environment)
- `SECRET_KEY` set to strong random value
- `SQLALCHEMY_DATABASE_URI` configured securely
- HTTPS enabled (reverse proxy or Flask with SSL)

See `.env.example` for required environment variables.

