# Unified Project Structure

```plaintext
sub-learning/
├── .github/                        # GitHub integration (optional)
│   └── workflows/
│       └── pi-deploy.yml           # Simple deployment script
├── app/                            # Flask application core
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Environment-based configuration
│   ├── models/                     # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py                 # User authentication model
│   │   ├── subtitle.py             # Existing subtitle schema models
│   │   ├── progress.py             # Learning progress tracking
│   │   └── bookmark.py             # User bookmark management
│   ├── blueprints/                 # Flask blueprints organization
│   │   ├── __init__.py
│   │   ├── auth/                   # Authentication routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Login, register, OAuth handlers
│   │   │   ├── forms.py            # WTForms validation
│   │   │   └── oauth_handlers.py   # Google, Facebook, Apple OAuth
│   │   ├── api/                    # REST API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── movies.py           # Movie discovery API
│   │   │   ├── subtitles.py        # Subtitle content delivery
│   │   │   ├── progress.py         # Progress tracking API
│   │   │   └── bookmarks.py        # Bookmark management API
│   │   ├── main/                   # Main application routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Dashboard, learning interface
│   │   │   └── errors.py           # Error page handlers
│   │   └── admin/                  # Content management (future)
│   │       ├── __init__.py
│   │       └── routes.py           # Subtitle data administration
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Authentication business logic
│   │   ├── subtitle_service.py     # Subtitle processing and delivery
│   │   ├── progress_service.py     # Progress calculation and tracking
│   │   ├── content_service.py      # Movie discovery and filtering
│   │   └── bookmark_service.py     # Bookmark management logic
│   ├── utils/                      # Shared utilities
│   │   ├── __init__.py
│   │   ├── database.py             # Database connection and utilities
│   │   ├── cache.py                # SQLite optimization helpers
│   │   ├── validators.py           # Input validation functions
│   │   ├── decorators.py           # Custom Flask decorators
│   │   └── error_handlers.py       # Centralized error handling
│   ├── static/                     # Frontend assets
│   │   ├── css/
│   │   │   ├── bootstrap.min.css   # Bootstrap framework (CDN fallback)
│   │   │   ├── main.css            # Base application styles
│   │   │   ├── learning.css        # Subtitle learning interface styles
│   │   │   └── responsive.css      # Mobile/tablet optimizations
│   │   ├── js/
│   │   │   ├── vendor/
│   │   │   │   └── bootstrap.bundle.min.js  # Bootstrap JavaScript
│   │   │   ├── modules/
│   │   │   │   ├── auth.js          # Authentication handling
│   │   │   │   ├── subtitle-player.js  # Core learning interface
│   │   │   │   ├── movie-discovery.js  # Search and browsing
│   │   │   │   ├── progress-tracker.js # Progress management
│   │   │   │   └── bookmark-manager.js # Bookmark functionality
│   │   │   ├── components/
│   │   │   │   ├── dual-subtitle-display.js # Side-by-side rendering
│   │   │   │   ├── language-selector.js     # Language pair selection
│   │   │   │   ├── progress-indicator.js    # Visual progress components
│   │   │   │   └── modal-manager.js         # Bootstrap modal handling
│   │   │   ├── utils/
│   │   │   │   ├── api-client.js    # Centralized API communication
│   │   │   │   ├── storage-helper.js # LocalStorage management
│   │   │   │   ├── error-handler.js  # Error display and recovery
│   │   │   │   └── state-manager.js  # Client-side state management
│   │   │   └── app.js               # Application initialization
│   │   ├── images/
│   │   │   ├── logo/               # SubLearning branding assets
│   │   │   ├── flags/              # Language flag icons
│   │   │   └── icons/              # UI icons and graphics
│   │   └── fonts/                  # Custom fonts for subtitle readability
│   └── templates/                  # Jinja2 template files
│       ├── base.html               # Base template with navigation
│       ├── auth/
│       │   ├── login.html          # Login page with OAuth options
│       │   ├── register.html       # Registration form
│       │   └── language-selection.html # Initial language pair setup
│       ├── main/
│       │   ├── dashboard.html      # User dashboard and progress
│       │   ├── movies.html         # Movie catalog and search
│       │   ├── learning.html       # Subtitle learning interface
│       │   └── settings.html       # User preferences
│       ├── components/             # Reusable template components
│       │   ├── navbar.html         # Navigation component
│       │   ├── footer.html         # Footer component
│       │   ├── progress-card.html  # Progress display component
│       │   └── movie-card.html     # Movie listing component
│       └── errors/
│           ├── 404.html            # Not found page
│           ├── 500.html            # Server error page
│           └── offline.html        # Network error fallback
├── migrations/                     # Database migration files
│   ├── versions/                   # SQLAlchemy migration versions
│   └── alembic.ini                 # Migration configuration
├── instance/                       # Instance-specific files (Pi-local)
│   ├── config.py                   # Pi-specific configuration overrides
│   ├── subtitle_database.db        # SQLite database file
│   └── logs/                       # Application log files
├── scripts/                        # Deployment and maintenance scripts
│   ├── setup_pi.sh                 # Initial Pi configuration script
│   ├── deploy.sh                   # Deployment automation
│   ├── backup_db.sh                # Database backup script
│   ├── import_subtitles.py         # Subtitle data import utility
│   └── health_check.py             # Pi health monitoring
├── tests/                          # Test suite (lightweight for Pi)
│   ├── __init__.py
│   ├── conftest.py                 # pytest configuration
│   ├── test_auth.py                # Authentication tests
│   ├── test_subtitle_service.py    # Subtitle functionality tests
│   ├── test_progress.py            # Progress tracking tests
│   └── test_api.py                 # API endpoint tests
├── docs/                           # Project documentation
│   ├── prd.md                      # Product Requirements Document
│   ├── front-end-spec.md           # UI/UX Specification
│   ├── architecture.md             # This architecture document
│   ├── pi-setup.md                 # Raspberry Pi setup guide
│   └── api-documentation.md        # API endpoint documentation
├── .env.example                    # Environment variables template
├── .gitignore                      # Git exclusions (exclude .env, instance/, logs/)
├── requirements.txt                # Python dependencies
├── wsgi.py                         # WSGI entry point for production
├── run.py                          # Development server entry point
└── README.md                       # Project overview and setup instructions
```
