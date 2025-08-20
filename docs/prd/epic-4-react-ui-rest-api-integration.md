# Epic 4: React UI REST API Integration - Brownfield Enhancement

## Epic Goal

Connect the migrated React/shadcn/ui components to the existing Flask REST API endpoints, replacing mock data with real backend integration to deliver a fully functional subtitle learning application.

## Epic Description

### Existing System Context

- **Current relevant functionality**: React/Next.js frontend with TypeScript, shadcn/ui components, Tailwind CSS, modern component architecture with mock data placeholders
- **Technology stack**: React Server Components, Zustand state management, React Query for server state, comprehensive Flask REST API with 20+ endpoints
- **Integration points**: `/api/*` endpoints covering authentication, movies, subtitles, progress, bookmarks, dashboard analytics; Flask-Login session management; CORS configuration required

### Enhancement Details

- **What's being added/changed**: Replace mock data and placeholder components with actual API integration using React Query and proper error handling, implement authentication state synchronization, add loading states and error boundaries
- **How it integrates**: HTTP client configuration with axios/fetch, authentication state management bridge between React and Flask sessions, API response type definitions, component data binding with proper TypeScript interfaces
- **Success criteria**: All React components display real data from Flask API, user authentication flows work seamlessly, CRUD operations function correctly, error states handled gracefully, loading states provide good UX

## Stories

### Story 4.1: API Client Setup & Authentication Integration

Set up HTTP client infrastructure and connect React authentication flows to existing Flask auth endpoints for seamless session management.

### Story 4.2: Movie Catalog & Language Selection Integration  

Connect language picker and movie catalog components to Flask REST endpoints, implementing search, filtering, and subtitle availability features.

### Story 4.3: Subtitle Learning Interface & Progress Integration

Implement subtitle display, navigation controls, progress tracking, and bookmark functionality using real Flask API data with proper state management.

## Compatibility Requirements

- [x] Existing Flask API endpoints remain unchanged
- [x] Database schema changes are backward compatible (none required) 
- [x] UI changes follow existing shadcn/ui patterns and design system
- [x] Performance impact is minimal (React Query caching optimizes requests)

## Risk Mitigation

- **Primary Risk**: Authentication state synchronization between React and Flask sessions causing login/logout inconsistencies
- **Mitigation**: Implement proper session validation middleware, error boundaries for network failures, and fallback states for offline scenarios  
- **Rollback Plan**: Environment variable toggle to switch back to mock data if integration fails during deployment

## Definition of Done

- [x] All stories completed with acceptance criteria met
- [x] Existing Flask API functionality verified through testing
- [x] Integration points working correctly with proper error handling and loading states
- [x] Documentation updated appropriately (API client usage patterns, component integration examples)
- [x] No regression in existing features (authentication flows, data persistence, session management)

## Story Manager Handoff

**Story Manager Handoff:**

"Please develop detailed user stories for this brownfield epic. Key considerations:

- This is an enhancement to an existing system running React/Next.js frontend with Flask backend
- Integration points: 20+ REST API endpoints in `/api/*` routes covering auth (`/api/auth/*`), movies (`/api/movies`), subtitles (`/api/movies/*/subtitles`), progress (`/api/progress/*`), bookmarks (`/api/bookmarks`), dashboard (`/api/progress/dashboard`)
- Existing patterns to follow: shadcn/ui components, TypeScript interfaces, React Query for server state, Zustand for global state
- Critical compatibility requirements: Flask session-based authentication with CSRF protection, CORS configuration, proper error handling and loading states, rate limiting compliance
- Each story must include verification that existing Flask functionality remains intact and sessions work correctly

The epic should maintain system integrity while delivering a fully integrated subtitle learning experience with professional UX patterns."

## Technical Context

### Existing Flask API Endpoints Available for Integration

**Authentication Endpoints:**
- `POST /auth/api/login` - User login with session creation
- `POST /auth/api/register` - User registration  
- `POST /auth/api/logout` - Session cleanup
- `POST /api/user/languages` - Update language preferences

**Content & Movie Endpoints:**
- `GET /api/languages` - Available languages for selection
- `GET /api/movies` - Filtered movie catalog with search/letter filtering
- `GET /api/movies/letters` - Letter counts for alphabetical navigation
- `GET /api/movies/{id}/subtitles` - Subtitle content retrieval
- `GET /api/movies/{id}/subtitles/availability` - Language availability check

**Progress & Learning Endpoints:**
- `GET /api/progress/{sub_link_id}` - User progress retrieval
- `PUT /api/progress/{sub_link_id}` - Progress updates
- `GET /api/progress/recent` - Recent learning activity
- `GET /api/progress/dashboard` - Comprehensive learning statistics
- `GET /api/progress/charts` - Chart data for visualizations
- `GET /api/progress/streak` - Learning streak calculations

**Bookmark Management:**
- `POST /api/bookmarks` - Create bookmarks
- `GET /api/bookmarks` - Retrieve user bookmarks with search
- `DELETE /api/bookmarks/{id}` - Delete bookmarks
- `GET /api/bookmarks/export` - Export bookmarks to text

**Goal Tracking:**
- `POST /api/goals` - Create learning goals
- `GET /api/goals` - Retrieve user goals
- `PUT /api/goals/{id}` - Update goals
- `DELETE /api/goals/{id}` - Delete goals

All endpoints include comprehensive error handling, validation, rate limiting, and proper HTTP status codes as documented in the Flask implementation.