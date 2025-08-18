# Technical Assumptions

## Repository Structure: Monorepo
Single repository containing Flask backend, static frontend assets, templates, and data files. Structure follows `/app` (Flask application), `/static` (CSS/JS/assets), `/templates` (Jinja2 templates), `/migrations` (database schemas), `/data` (subtitle files) organization for straightforward development and deployment.

## Service Architecture
Monolithic Flask application with modular blueprints for authentication, content management, user progress, and subtitle delivery APIs. Single-server deployment initially with migration path to microservices as user base scales beyond SQLite limitations.

## Testing Requirements
Unit testing for core business logic (authentication, subtitle processing, progress tracking) using pytest framework. Integration testing for API endpoints and database operations. Manual testing for UI workflows and cross-browser compatibility. Automated testing focused on backend reliability with manual validation for frontend user experience.

## Additional Technical Assumptions and Requests

**Frontend Technology Stack:**
- HTML5/CSS3/JavaScript with Bootstrap 5 for responsive design
- jQuery for DOM manipulation and AJAX requests
- Modern ES6+ JavaScript features for cleaner code organization

**Backend Technology Stack:**
- Python 3.9+ with Flask framework
- Flask-SQLAlchemy for database ORM and query optimization
- Flask-Login for session management and authentication
- Flask-Migrate for database schema version control
- OAuth integration libraries for social authentication

**Database and Storage:**
- SQLite for development and initial production deployment
- Migration strategy to PostgreSQL when concurrent user load exceeds SQLite capacity
- Subtitle files stored as static assets with efficient indexing for search functionality

**Hosting and Infrastructure:**
- Initial deployment on Heroku or DigitalOcean App Platform for simplicity
- CDN integration (Cloudflare) for subtitle file delivery optimization
- HTTPS enforcement and secure session configuration

**Security and Compliance:**
- Input sanitization for all user-generated content
- GDPR-compliant user data handling with data portability features
- Secure OAuth token handling and session management
