# Monitoring and Observability

## Monitoring Stack

- **Frontend Monitoring:** Browser console logging with local storage persistence, client-side error tracking via custom JavaScript handlers, performance timing using Navigation Timing API, user session recording in local storage for debugging
- **Backend Monitoring:** Python logging framework with rotating file handlers, Flask request logging with response times, SQLite query performance monitoring, Pi resource usage tracking via psutil
- **Error Tracking:** File-based error logging with structured JSON format, automatic log rotation to prevent disk exhaustion, email alerts for critical errors (optional Pi email setup)
- **Performance Monitoring:** Built-in Flask request timing, SQLite query duration logging, memory usage monitoring with automatic cache clearing, disk usage tracking with early warning system

## Key Metrics

**Frontend Metrics:**
- Core Web Vitals (First Contentful Paint, Largest Contentful Paint, Cumulative Layout Shift)
- JavaScript errors and exception counts per session
- API response times from browser perspective (subtitle loading, progress updates)
- User interactions (subtitle navigation clicks, bookmark creation, session duration)

**Backend Metrics:**
- Request rate (requests per minute, peak concurrent users)
- Error rate (4xx/5xx responses as percentage of total requests)
- Response time (95th percentile response times for API endpoints)
- Database query performance (subtitle alignment queries, progress updates, authentication queries)

**Pi-Specific Infrastructure Metrics:**
- Memory usage percentage (with 90% alert threshold)
- Disk usage percentage (with 85% warning, 95% critical thresholds)
- CPU temperature (Pi thermal throttling detection)
- Network connectivity status and OAuth provider reachability
- SQLite database lock frequency and duration
- Service uptime and automatic restart count
