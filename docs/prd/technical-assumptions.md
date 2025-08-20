# Technical Assumptions

## Repository Structure: Full-Stack Monorepo
Single repository containing separate Flask backend API and React frontend application. Structure follows modern separation of concerns:
- `/backend` - Flask REST API server
- `/frontend` - Next.js React application 
- `/shared` - Common TypeScript types and utilities
- `/docs` - Project documentation and specifications

This enables independent development and deployment of frontend and backend components while maintaining shared documentation and types.

## Service Architecture
**Backend**: Lightweight Flask REST API server with modular blueprints for authentication, content management, user progress, and subtitle delivery endpoints. Stateless API design enabling flexible frontend deployment.

**Frontend**: React single-page application (SPA) built with Next.js, providing server-side rendering capabilities and optimal performance. Communicates with Flask backend via REST API.

**Deployment**: Decoupled architecture allowing independent scaling - Next.js frontend deployed to Vercel/Netlify, Flask backend on DigitalOcean/Heroku. Migration path to microservices remains viable as user base grows.

## Testing Requirements
**Backend Testing**: Unit testing for core business logic (authentication, subtitle processing, progress tracking) using pytest framework. Integration testing for REST API endpoints and database operations.

**Frontend Testing**: Component testing using Jest and React Testing Library for UI components. Integration testing for user workflows and API integration. End-to-end testing using Playwright for critical user paths.

**Cross-Browser Compatibility**: Automated testing across modern browsers (Chrome, Firefox, Safari, Edge). Responsive design testing for mobile and tablet viewports.

**API Testing**: Automated REST API testing using pytest for backend endpoints. Frontend API integration testing using Mock Service Worker (MSW) for reliable test environments.

## Additional Technical Assumptions and Requests

**Frontend Technology Stack:**
- React 18+ with Next.js 14+ for modern component-based architecture
- TypeScript for type-safe development and enhanced developer experience
- shadcn/ui component library built on Radix UI primitives for accessibility
- Tailwind CSS for utility-first styling and consistent design system
- React Query (TanStack Query) for server state management and caching
- Zustand for lightweight global state management
- React Hook Form for performant form handling and validation

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
- **Frontend**: Vercel deployment optimized for Next.js with global CDN and edge computing
- **Backend**: DigitalOcean Droplet or Heroku for Flask API server
- **Static Assets**: CDN integration (Vercel Edge Network + Cloudflare) for subtitle file delivery optimization
- **SSL/TLS**: Automatic HTTPS enforcement across all services
- **Environment Separation**: Development, staging, and production environments with proper secrets management

**Security and Compliance:**
- Input sanitization for all user-generated content
- GDPR-compliant user data handling with data portability features
- Secure OAuth token handling and session management
