# SubLearning Product Requirements Document (PRD)

## Goals and Background Context

### Goals
Based on the Project Brief, here are the desired outcomes this PRD will deliver:

• Create a web-based dual-language subtitle learning platform that transforms passive movie watching into active language acquisition
• Enable busy professionals to combine entertainment with measurable language learning progress in 15-30 minute sessions
• Implement cognitive bridging technology that connects native and target languages through relatable movie content
• Build foundational MVP with user authentication, language pair selection, movie catalog, and synchronized subtitle display
• Establish sustainable user engagement with 70% weekly retention and 3 learning sessions per week average
• Validate market demand for movie-based language learning approach with 1,000 active users within 6 months

### Background Context

SubLearning addresses a fundamental gap in language learning where traditional materials fail to create authentic cognitive connections between textbook knowledge and real-world application. Current language learning solutions rely on artificial, scripted conversations that lack the cultural context and emotional engagement necessary for effective retention.

The platform leverages the inherent relatability of movies to create **cognitive bridges** - neurological connections between existing experience and new language concepts. By presenting dual-language subtitles side-by-side with interactive elements, SubLearning transforms entertainment consumption into structured learning opportunities that respect users' time constraints while delivering authentic cultural context and natural speech patterns that traditional methods cannot provide.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-08-18 | 1.0 | Initial PRD creation based on comprehensive Project Brief | John (PM Agent) |

## Requirements

### Functional

**FR1:** The system shall provide user registration and authentication via email/password and OAuth integration for Facebook, Google, and Apple IDs, maintaining personalized learning progress across sessions.

**FR2:** The system shall enable users to select two languages from available options stored in the languages database table to create their native and target language pair.

**FR3:** The system shall provide a searchable movie catalog where users can find movies by text title search or browse alphabetically by clicking first letter groups (e.g., clicking "H" shows all movies starting with H like "Happy Gilmore").

**FR4:** The system shall display synchronized dual-language subtitles side-by-side in text format without movie playback functionality.

**FR5:** The system shall track and persist user learning progress including lines completed, time spent, movies viewed, and session history across login sessions.

**FR6:** The system shall provide subtitle file storage and retrieval capabilities supporting efficient search and streaming of subtitle content for selected movies.

**FR8:** The system shall allow users to bookmark specific subtitle lines or scenes for later review and practice.

### Non Functional

**NFR1:** The system shall achieve initial page load times under 3 seconds and subtitle synchronization response times under 1 second to maintain user engagement.

**NFR2:** The system shall support 100+ concurrent users during peak usage without performance degradation or subtitle timing drift.

**NFR3:** The system shall maintain 99.5% uptime availability to ensure consistent access for daily learning routines.

**NFR4:** The system shall implement secure session management, input sanitization, and HTTPS enforcement to protect user data and privacy.

**NFR5:** The system shall provide responsive web design compatible with modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) and optimal for desktop/laptop usage.

**NFR6:** The system shall follow GDPR-compliant user data handling practices including data portability and deletion capabilities.

**NFR7:** The system shall implement graceful error handling and user-friendly error messages to minimize learning session interruptions.

**NFR8:** The system shall support database migration from SQLite to PostgreSQL as user base scales beyond single-server capacity.

## User Interface Design Goals

### Overall UX Vision
Clean, distraction-free learning environment that prioritizes readability and focus. The interface should feel more like a professional learning tool than entertainment software, with intuitive navigation that doesn't interrupt the cognitive bridging process. Emphasis on text clarity, comfortable reading layouts, and seamless transitions between movie selection and subtitle study sessions.

### Key Interaction Paradigms
- **Progressive disclosure:** Start with simple movie selection, gradually reveal subtitle controls and progress tracking
- **Keyboard-first navigation:** Arrow keys for subtitle progression, spacebar for pause/play timing, tab navigation for accessibility
- **Visual feedback system:** Subtle progress indicators and completion states without overwhelming the reading experience
- **Responsive text scaling:** User-controlled font sizing for optimal reading comfort across different screen sizes and lighting conditions

### Core Screens and Views
- **Authentication Screen:** OAuth provider buttons prominently displayed above traditional email/password form
- **Language Pair Selection:** Visual language picker with flag icons and clear native/target language designation
- **Movie Catalog Browser:** List view with alphabetical navigation sidebar and search bar for title lookup
- **Subtitle Reading Interface:** Split-screen layout with adjustable column widths, progress tracker, and bookmark functionality
- **User Progress Dashboard:** Learning statistics, bookmarked lines, and recently viewed movies

### Accessibility: WCAG AA
Compliance with WCAG AA standards including keyboard navigation, screen reader compatibility, sufficient color contrast ratios (4.5:1 minimum), and alternative text for all interface elements. Focus indicators, skip navigation links, and semantic HTML structure throughout.

### Branding
Minimalist design aesthetic emphasizing clarity and professionalism. Color palette focused on high-contrast text readability with subtle accent colors for interactive elements. Typography choices prioritize legibility for extended reading sessions, avoiding decorative fonts that could impede learning focus.

### Target Device and Platforms: Web Responsive
Optimized for desktop/laptop primary usage (13-inch screens and larger) with responsive design ensuring usability on tablets and mobile devices. Desktop-first approach recognizes that extended subtitle reading is more comfortable on larger screens, while maintaining mobile compatibility for quick progress checking and light browsing.

## Technical Assumptions

### Repository Structure: Monorepo
Single repository containing Flask backend, static frontend assets, templates, and data files. Structure follows `/app` (Flask application), `/static` (CSS/JS/assets), `/templates` (Jinja2 templates), `/migrations` (database schemas), `/data` (subtitle files) organization for straightforward development and deployment.

### Service Architecture
Monolithic Flask application with modular blueprints for authentication, content management, user progress, and subtitle delivery APIs. Single-server deployment initially with migration path to microservices as user base scales beyond SQLite limitations.

### Testing Requirements
Unit testing for core business logic (authentication, subtitle processing, progress tracking) using pytest framework. Integration testing for API endpoints and database operations. Manual testing for UI workflows and cross-browser compatibility. Automated testing focused on backend reliability with manual validation for frontend user experience.

### Additional Technical Assumptions and Requests

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

## Epic List

**Epic 1: Foundation & Authentication Infrastructure**
Establish core project setup with user authentication via email/password and OAuth providers, basic database schema, and essential application security foundations.

**Epic 2: Language & Content Management System**
Implement dynamic language selection from database, movie catalog with search and alphabetical browsing capabilities, and subtitle file storage and retrieval system.

**Epic 3: Subtitle Learning Interface & Progress Tracking**
Create the core learning experience with dual-language subtitle display, user progress persistence, bookmarking functionality, and learning session management.

## Epic 1: Foundation & Authentication Infrastructure

**Epic Goal:** Establish project setup, authentication system with email/password and OAuth integration, database foundations, and essential security infrastructure while delivering a functional user registration and login system that demonstrates core platform capabilities.

### Story 1.1: Project Setup and Basic Flask Application

As a developer,
I want to establish the basic Flask project structure with essential configurations,
so that I have a solid foundation for building all subsequent features.

#### Acceptance Criteria
1. Flask application initialized with proper project structure (`/app`, `/static`, `/templates`, `/migrations`, `/data`)
2. Basic routing configured with health check endpoint returning system status
3. Development environment configuration with environment variables for database and secret keys
4. Version control initialized with appropriate `.gitignore` for Python/Flask projects
5. Requirements.txt file established with core dependencies (Flask, SQLAlchemy, etc.)
6. Basic error handling middleware configured for graceful error responses
7. Application successfully runs locally with `flask run` command

### Story 1.2: Database Setup and User Model

As a system administrator,
I want the database schema and user model established,
so that user data can be stored securely and efficiently.

#### Acceptance Criteria
1. SQLite database configuration with Flask-SQLAlchemy integration
2. User model defined with fields: id, email, password_hash, oauth_provider, oauth_id, created_at, updated_at
3. Database migration system configured using Flask-Migrate
4. Initial migration created and tested for user table creation
5. Database initialization script created for development setup
6. Basic database connection testing endpoint available
7. Password hashing implemented using secure algorithms (bcrypt/werkzeug)

### Story 1.3: Email/Password Authentication System

As a new user,
I want to register and login with email and password,
so that I can access the platform and maintain my learning progress.

#### Acceptance Criteria
1. User registration form with email validation and password strength requirements
2. Registration endpoint creates new user with hashed password storage
3. Login form with email/password input and remember-me option
4. Login endpoint validates credentials and establishes secure session
5. Session management configured with Flask-Login for user state persistence
6. Logout functionality clears session and redirects appropriately
7. Basic user profile page displaying logged-in user information
8. Password reset functionality via email (basic implementation)

### Story 1.4: OAuth Integration for Social Login

As a busy professional,
I want to login using my Google, Facebook, or Apple account,
so that I can quickly access the platform without managing another password.

#### Acceptance Criteria
1. OAuth client configuration for Google, Facebook, and Apple providers
2. OAuth login buttons prominently displayed on authentication pages
3. OAuth callback handling for successful authentication flow
4. User account creation for first-time OAuth users
5. Account linking for existing users who choose to add OAuth
6. OAuth token secure storage and session management
7. Fallback error handling for OAuth failures with clear user messaging
8. User profile indicates OAuth authentication method used

## Epic 2: Language & Content Management System

**Epic Goal:** Implement language selection interface, movie catalog with search and alphabetical browsing capabilities, and subtitle file retrieval system, enabling users to discover and select learning content from pre-populated language and movie databases.

### Story 2.1: Language Selection Interface

As a language learner,
I want to select my native and target languages from available options,
so that I can access appropriate learning content for my language pair.

#### Acceptance Criteria
1. Language pair selection page with visual language picker using flag icons from pre-populated languages table
2. Clear designation of native language vs target language selection
3. User profile updated to store selected language pair preferences
4. Language pair validation prevents selecting same language for both native and target
5. Language selection persisted across user sessions
6. Dropdown or grid interface displays all available languages with flag icons
7. Form validation ensures both languages are selected before proceeding

### Story 2.2: Movie Catalog Display

As a language learner,
I want to browse available movies with subtitle content,
so that I can choose interesting content for my learning sessions.

#### Acceptance Criteria
1. Movie catalog page displaying movies as a simple list of titles from pre-populated database
2. Movie titles displayed as clickable links or buttons for selection
3. Movies filtered to show only those with subtitles available for user's selected language pair
4. Movies without subtitles for user's language pair are excluded from the list
5. Movie selection redirects to subtitle reading interface (placeholder for Epic 3)
6. Clean, readable list layout optimized for scanning through titles
7. List items have hover states and clear selection indicators

### Story 2.3: Movie Search Functionality

As a language learner,
I want to search for movies by title,
so that I can quickly find specific content I want to study.

#### Acceptance Criteria
1. Search bar prominently displayed on movie catalog page
2. Real-time search implementation with AJAX for responsive user experience
3. Search functionality matches partial titles (case-insensitive)
4. Search results update dynamically as user types (debounced input)
5. Search results highlight matching text within movie titles
6. Empty search state shows all available movies for user's language pair
7. No results state displays helpful message and suggestions
8. Search query preserved in URL for bookmarking and sharing

### Story 2.4: Alphabetical Movie Browsing

As a language learner,
I want to browse movies alphabetically by first letter,
so that I can explore available content systematically.

#### Acceptance Criteria
1. Alphabetical navigation sidebar with letter buttons (A-Z, #)
2. Clicking letter filters movies to show only titles starting with that letter
3. Active letter highlighted in navigation to show current filter state
4. Letter navigation works in combination with search functionality
5. Letters with no available movies displayed as disabled/grayed out
6. Movie count indicator for each letter group
7. "All" option to display complete movie catalog for user's language pair
8. Smooth scrolling and responsive behavior on different screen sizes

### Story 2.5: Subtitle File Retrieval System

As a system administrator,
I want subtitle files efficiently retrieved from pre-populated storage,
so that users can access synchronized subtitle content for their selected movies.

#### Acceptance Criteria
1. Subtitle retrieval API endpoint accepting movie ID and language parameters
2. Subtitle file parsing capability for common formats from existing file storage
3. Subtitle content cached in memory for performance optimization
4. Error handling for missing or corrupted subtitle files with user-friendly messages
5. API response includes subtitle lines with timing and text content in JSON format
6. Subtitle file validation ensuring proper formatting during retrieval
7. Database references to subtitle files validated during movie catalog display
8. Performance optimization for concurrent subtitle file access

## Epic 3: Subtitle Learning Interface & Progress Tracking

**Epic Goal:** Create the core learning experience with dual-language subtitle display, user progress persistence, bookmarking functionality, and learning session management, delivering the complete SubLearning value proposition for cognitive bridging through movie-based language learning.

### Story 3.1: Basic Subtitle Reading Interface

As a language learner,
I want to view movie subtitles in both my native and target languages side-by-side,
so that I can study language connections through authentic movie content.

#### Acceptance Criteria
1. Split-screen layout displaying subtitles in two columns (native language | target language)
2. Subtitle lines synchronized between both languages showing corresponding translations
3. Adjustable column widths allowing users to customize reading layout preferences
4. Clear visual separation between language columns with appropriate spacing
5. Font size controls for optimal reading comfort across different screen sizes
6. Navigation controls to move between subtitle lines (previous/next buttons)
7. Current subtitle line highlighted or emphasized for reading focus
8. Responsive design ensuring readability on desktop and mobile devices

### Story 3.2: Subtitle Navigation and Playback Controls

As a language learner,
I want to control the pace of subtitle progression,
so that I can study at my optimal learning speed.

#### Acceptance Criteria
1. Play/pause functionality for automatic subtitle progression with configurable timing
2. Manual navigation controls (previous line, next line) for self-paced study
3. Speed adjustment controls for automatic progression (slow, normal, fast)
4. Jump to beginning/end of subtitle file functionality
5. Keyboard shortcuts for navigation (arrow keys, spacebar) for hands-free operation
6. Current position indicator showing progress through subtitle file
7. Smooth transitions between subtitle lines without jarring interface changes
8. Pause state preservation when user navigates away and returns

### Story 3.3: User Progress Tracking System

As a language learner,
I want my learning progress automatically saved,
so that I can resume study sessions where I left off and track my advancement.

#### Acceptance Criteria
1. Progress table storing user_id, movie_id, current_line_number, last_accessed timestamp
2. Automatic progress saving as user advances through subtitle lines
3. Resume functionality returning user to last studied line when reopening movie
4. Session duration tracking for learning analytics
5. Lines completed counter for each movie and overall totals
6. Progress percentage display for current movie completion status
7. Recently studied movies list on user dashboard for quick access
8. Progress data persisted across browser sessions and devices

### Story 3.4: Bookmark Functionality

As a language learner,
I want to bookmark specific subtitle lines,
so that I can return to challenging or interesting phrases for focused review.

#### Acceptance Criteria
1. Bookmark button on each subtitle line for easy marking during study
2. Bookmarks table storing user_id, movie_id, line_number, bookmark_timestamp, optional_note
3. Visual indicator showing which lines are already bookmarked
4. Bookmarks management page listing all saved lines with movie titles and content preview
5. Quick navigation to bookmarked lines from bookmarks management interface
6. Remove bookmark functionality from both reading interface and management page
7. Bookmark export capability for external study tools (optional text format)
8. Search functionality within bookmarked content for specific phrases or words

### Story 3.5: Learning Dashboard and Session Management

As a language learner,
I want to view my overall learning progress and manage my study sessions,
so that I can track advancement and maintain motivation for continued learning.

#### Acceptance Criteria
1. Dashboard displaying total study time, movies completed, and lines studied
2. Recent activity showing last studied movies with resume options
3. Learning streak counter tracking consecutive days of study activity
4. Weekly/monthly progress charts showing study consistency and advancement
5. Personal learning statistics including average session duration and completion rates
6. Quick access to bookmarked content and favorite movies from dashboard
7. Learning goals setting and progress tracking toward user-defined targets
8. Session history with detailed breakdown of time spent per movie and language pair