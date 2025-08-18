# Components

## AuthenticationService

**Responsibility:** Handle user registration, login, OAuth integration, and session management across email/password and social authentication flows

**Key Interfaces:**
- POST /api/auth/register - User registration with email validation
- POST /api/auth/login - Email/password authentication  
- GET /api/auth/oauth/{provider} - OAuth provider redirects
- POST /api/auth/logout - Session termination

**Dependencies:** Flask-Login for session management, OAuth provider APIs (Google, Facebook, Apple), User model, Language model for initial language pair selection

**Technology Stack:** Flask blueprint with Flask-Login integration, OAuth2 libraries (Authlib), SQLite user storage, session-based authentication using secure cookies

## ContentDiscoveryService

**Responsibility:** Enable movie catalog browsing, search functionality, and language pair filtering based on available subtitle links

**Key Interfaces:**
- GET /api/movies - Filtered movie catalog with search and alphabetical browsing
- GET /api/languages - Available language options
- Movie title search with real-time filtering
- Alphabetical navigation (A-Z filtering)

**Dependencies:** SubTitle, SubLink, SubLinkLine models for determining available content, Language model for filtering, User model for language pair preferences

**Technology Stack:** Flask blueprint with SQLite queries, JSON API responses, Bootstrap frontend components for search and navigation UI

## SubtitleLearningService

**Responsibility:** Core learning experience delivering synchronized dual-language subtitle content with navigation controls and timing management

**Key Interfaces:**
- GET /api/subtitles/{sub_link_id} - Paginated alignment data retrieval
- Subtitle alignment rendering with source/target language display
- Navigation controls (previous/next alignment, jump to position)
- Session timing and auto-progression functionality

**Dependencies:** SubLine, SubLinkLine models for content retrieval, UserProgress for current position tracking, Language model for display formatting

**Technology Stack:** Flask blueprint with complex SQLite JOIN queries, JavaScript frontend for interactive navigation, Bootstrap responsive layout for dual-language display

## ProgressTrackingService

**Responsibility:** Monitor and persist user learning advancement through subtitle alignments, session duration, and completion statistics

**Key Interfaces:**
- GET /api/progress/{sub_link_id} - Specific movie progress retrieval
- PUT /api/progress/{sub_link_id} - Progress updates during learning sessions
- GET /api/progress - Overall learning statistics and dashboard data
- Real-time progress saving during subtitle navigation

**Dependencies:** UserProgress model for persistence, User model for ownership, SubLink model for content association, automatic session tracking

**Technology Stack:** Flask blueprint with optimized SQLite updates, JavaScript for client-side progress tracking, periodic AJAX updates to maintain progress state

## BookmarkManagementService

**Responsibility:** User-driven content marking system for review and focused study of specific subtitle alignments

**Key Interfaces:**
- GET /api/bookmarks - User bookmark retrieval with content preview
- POST /api/bookmarks - New bookmark creation with optional notes
- DELETE /api/bookmarks/{bookmark_id} - Bookmark removal
- Bookmark navigation within learning interface

**Dependencies:** Bookmark model for storage, SubLinkLine for alignment association, User model for ownership, SubLine for content preview

**Technology Stack:** Flask blueprint with SQLite bookmark storage, JavaScript for in-session bookmark creation, Bootstrap modal/form components for bookmark management

## UserDashboardService

**Responsibility:** Consolidated view of learning progress, recent activity, bookmark access, and quick continuation of study sessions

**Key Interfaces:**
- Dashboard page rendering with progress summaries
- Recent activity feed with continue learning options
- Quick access to bookmarked content and favorite movies
- Learning statistics visualization and goal tracking

**Dependencies:** UserProgress for statistics calculation, Bookmark for quick access, SubLink for recently studied content, User for personalization

**Technology Stack:** Flask blueprint with Jinja2 template rendering, SQLite aggregation queries for statistics, Bootstrap dashboard layout with responsive cards
