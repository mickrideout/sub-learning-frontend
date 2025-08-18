# Backend Architecture

## Service Architecture

### Controller/Route Organization
```
app/
├── __init__.py                    # Flask app factory
├── config.py                      # Configuration management
├── models/
│   ├── __init__.py
│   ├── user.py                    # User model with authentication
│   ├── subtitle.py                # Subtitle schema models
│   ├── progress.py                # Progress tracking models
│   └── bookmark.py                # Bookmark management models
├── blueprints/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py              # Authentication endpoints
│   │   ├── oauth_handlers.py      # OAuth provider integration
│   │   └── forms.py               # WTForms validation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── movies.py              # Movie discovery API
│   │   ├── subtitles.py           # Subtitle content API
│   │   ├── progress.py            # Progress tracking API
│   │   └── bookmarks.py           # Bookmark management API
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py              # Main application routes
│   │   └── views.py               # Template rendering
│   └── admin/
│       ├── __init__.py
│       └── routes.py              # Content management
├── services/
│   ├── __init__.py
│   ├── subtitle_service.py        # Subtitle processing logic
│   ├── progress_service.py        # Progress calculation
│   ├── auth_service.py            # Authentication business logic
│   └── content_service.py         # Content discovery logic
├── utils/
│   ├── __init__.py
│   ├── database.py                # Database utilities
│   ├── cache.py                   # SQLite optimization
│   ├── validators.py              # Input validation
│   └── error_handlers.py          # Error processing
└── static/                        # Frontend assets
└── templates/                     # Jinja2 templates
```

### Controller Template
```python