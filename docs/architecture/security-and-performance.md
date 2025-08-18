# Security and Performance

## Security Requirements

**Frontend Security:**
- CSP Headers: `default-src 'self'; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; script-src 'self' cdn.jsdelivr.net; img-src 'self' data: https:; connect-src 'self'; font-src 'self' fonts.googleapis.com fonts.gstatic.com`
- XSS Prevention: Content Security Policy enforcement, input sanitization on all user-generated content (bookmarks, notes), HTML escaping in Jinja2 templates
- Secure Storage: Session data in secure HTTP-only cookies, sensitive user preferences in server-side sessions, no sensitive data in localStorage

**Backend Security:**
- Input Validation: WTForms validation for all form inputs, SQLAlchemy parameterized queries prevent SQL injection, JSON schema validation for API endpoints
- Rate Limiting: 5 login attempts per minute per IP, 100 API requests per hour per user, 200 subtitle requests per hour per session
- CORS Policy: `Access-Control-Allow-Origin: https://your-domain.duckdns.org` (production), same-origin policy for API endpoints, credentials included only for authenticated requests

**Authentication Security:**
- Token Storage: Session cookies with secure, HttpOnly, SameSite=Lax flags, OAuth tokens stored server-side only, session timeout after 2 hours of inactivity
- Session Management: Flask-Login session management with CSRF protection, secure session key rotation, automatic logout on browser close
- Password Policy: Minimum 8 characters with complexity requirements, bcrypt hashing with cost factor 12, account lockout after 5 failed attempts

## Performance Optimization

**Frontend Performance:**
- Bundle Size Target: < 500KB total JavaScript (achieved through vanilla JS approach), < 200KB custom CSS excluding Bootstrap CDN, lazy loading for non-critical subtitle content
- Loading Strategy: Critical CSS inlined in base template, progressive enhancement with JavaScript modules, Bootstrap loaded from CDN with local fallback
- Caching Strategy: Service worker for offline subtitle access, localStorage for user preferences and progress backup, 1-year cache headers for static assets

**Backend Performance:**
- Response Time Target: < 500ms for subtitle API endpoints (Pi hardware consideration), < 200ms for authentication endpoints, < 1 second for movie discovery queries
- Database Optimization: SQLite WAL mode for concurrent reads, strategic indexing on user_id and sub_link_id, query result caching for subtitle content
- Caching Strategy: In-memory subtitle alignment caching (LRU with 1000 item limit), Flask session-based user state caching, nginx static file caching with gzip compression
