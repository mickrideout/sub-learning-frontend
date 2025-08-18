# Deployment Architecture

## Deployment Strategy

**Frontend Deployment:**
- **Platform:** Raspberry Pi local filesystem serving
- **Build Command:** No build process required (vanilla JS + Bootstrap)
- **Output Directory:** app/static/ (served directly by Flask/nginx)
- **CDN/Edge:** Bootstrap CSS/JS from CDN with local fallback, static assets served directly from Pi

**Backend Deployment:**
- **Platform:** Raspberry Pi with systemd service management
- **Build Command:** No compilation required (Python Flask application)
- **Deployment Method:** Git pull + service restart with database migration

## CI/CD Pipeline

```yaml