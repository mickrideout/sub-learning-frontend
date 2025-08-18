# Coding Standards

## Critical Fullstack Rules

- **Database Connection Management:** Always use SQLAlchemy context managers or Flask-SQLAlchemy's db.session, never create raw SQLite connections that could cause database locks on Pi
- **Subtitle Alignment Processing:** Always validate JSON structure in link_data before parsing, and handle missing subtitle lines gracefully with placeholder content
- **Progress Tracking Atomicity:** Use database transactions for progress updates to prevent corruption during Pi power interruptions or unexpected shutdowns  
- **Memory-Conscious Queries:** Never load all alignments at once - always use pagination with max 100 alignments per request to prevent Pi memory exhaustion
- **OAuth State Management:** Always validate OAuth state parameter and store callback URLs in session to prevent CSRF attacks in Pi's simplified security environment
- **Error Response Consistency:** All API endpoints must return JSON errors with consistent structure: `{"error": "message", "code": "error_type"}` for frontend error handling
- **Session Security:** Never store sensitive data in client-side storage - use Flask sessions for authentication state and temporary user preferences only
- **Subtitle Caching Keys:** Cache subtitle content using sub_link_id as key prefix to prevent cross-user data leakage in Pi's shared memory environment
- **Pi Resource Monitoring:** All long-running operations must check available memory/disk space before execution to prevent Pi system crashes
- **Input Sanitization:** Always escape user content in Jinja2 templates and validate all API inputs with WTForms to prevent XSS in subtitle notes and bookmarks

## Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| API Endpoints | REST style | snake_case | `/api/subtitles/123`, `/api/user_progress` |
| JavaScript Functions | camelCase | - | `loadSubtitleAlignments()`, `updateProgress()` |
| CSS Classes | kebab-case | - | `.subtitle-display`, `.learning-progress` |
| Python Functions | - | snake_case | `get_alignment_data()`, `validate_user_access()` |
| Database Tables | - | snake_case | `user_progress`, `sub_link_lines` |
| Flask Blueprints | - | snake_case | `auth_bp`, `subtitle_api_bp` |
| Environment Variables | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `GOOGLE_CLIENT_ID`, `DATABASE_URL` |
| SQLAlchemy Models | - | PascalCase | `UserProgress`, `SubLinkLine` |
