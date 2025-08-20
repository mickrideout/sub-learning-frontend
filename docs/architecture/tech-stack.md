# Tech Stack

## Modern React Architecture Stack

### Frontend Technologies

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.x | Type-safe React development | Enhanced developer experience, fewer runtime errors |
| Frontend Framework | React + Next.js | React 18.x, Next.js 14.x | Modern React with SSR/SSG capabilities | Industry standard, excellent performance, SEO benefits |
| UI Component Library | shadcn/ui | Latest | Pre-built accessible components | Modern design system, Tailwind-based, highly customizable |
| CSS Framework | Tailwind CSS | 3.x | Utility-first styling | Rapid development, consistent design, small bundle size |
| State Management - Global | Zustand | 4.x | Lightweight global state | Simple API, TypeScript support, no boilerplate |
| State Management - Server | React Query (TanStack Query) | 5.x | Server state management and caching | Powerful data fetching, caching, background updates |
| State Management - Forms | React Hook Form | 7.x | Form state and validation | Performant, minimal re-renders, great DX |
| Build Tool | Next.js (Webpack/Turbopack) | Built-in | Module bundling and optimization | Zero-config, optimized builds, code splitting |
| Package Manager | npm | Latest | Dependency management | Standard package manager, reliable ecosystem |
| Dev Server | Next.js Dev Server | Built-in | Development environment | Hot reload, fast refresh, excellent DX |

### Backend Technologies (Preserved)

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Backend Language | Python | 3.9+ | Server-side application logic | Stable ecosystem, Flask compatibility |
| Backend Framework | Flask | 2.3.x | Web application framework | Lightweight, proven REST API framework |
| API Style | REST | N/A | HTTP API endpoints | Simple, stateless, well-understood |
| Database | SQLite | 3.x | All data storage (users, subtitles, progress) | Single-file database, simple deployment |
| Cache | SQLite WAL mode | Built-in | Query performance optimization | Built-in SQLite feature, no additional dependencies |
| Authentication | Flask-Login + OAuth | Flask-Login 0.6.x | User sessions and social login | Session-based auth with social providers |
| Backend Testing | pytest | 7.x | Unit and integration testing | Python standard, comprehensive testing |

### Development & Deployment

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Testing | Jest + React Testing Library | Latest | Component and integration testing | React ecosystem standard, excellent testing utilities |
| E2E Testing | Playwright | Latest | End-to-end user flow testing | Modern, reliable, cross-browser testing |
| Code Quality | ESLint + Prettier | Latest | Code linting and formatting | Consistent code style, catch errors early |
| Type Checking | TypeScript | 5.x | Static type checking | Catch errors at compile time, better IDE support |
| Git Hooks | Husky + lint-staged | Latest | Pre-commit quality checks | Ensure code quality before commits |
| Deployment - Frontend | Vercel | N/A | Next.js optimized hosting | Zero-config deployment, edge optimization |
| Deployment - Backend | DigitalOcean Droplet | N/A | Flask application hosting | Cost-effective, reliable VPS hosting |
| File Storage | Local filesystem + CDN | N/A | Static assets delivery | Direct storage with CDN for performance |
| Monitoring | Vercel Analytics + Flask logging | Built-in | Application monitoring | Frontend performance + backend logging |
| Error Tracking | Sentry | Latest | Error monitoring and alerts | Comprehensive error tracking across stack |

## Key Architecture Decisions

### 1. Removal of Raspberry Pi Constraints

**Previous Constraint**: "Pi-optimized, no build complexity for Pi"
**New Approach**: Modern development toolchain with optimized deployment

**Rationale**: 
- Modern hosting platforms (Vercel, DigitalOcean) provide better performance and reliability
- Build tools enable significant performance optimizations
- Development experience improvements justify deployment complexity

### 2. React + Next.js Foundation

**Choice**: Next.js App Router with React Server Components
**Benefits**:
- Server-side rendering for improved SEO and initial load times
- Automatic code splitting and optimization
- Built-in TypeScript support
- Excellent developer experience with Fast Refresh

### 3. shadcn/ui Component Library

**Choice**: shadcn/ui over traditional libraries (Bootstrap, Material-UI)
**Benefits**:
- Copy-paste components for maximum customization
- Built on Radix UI primitives for accessibility
- Tailwind CSS integration for consistent styling
- Modern design system perfect for learning applications

### 4. State Management Strategy

**Global State**: Zustand for simplicity
**Server State**: React Query for robust data management
**Form State**: React Hook Form for performance
**Local State**: React hooks (useState, useReducer)

**Rationale**: Multi-layered approach addresses different state needs without over-engineering

### 5. TypeScript Adoption

**Decision**: Full TypeScript implementation
**Benefits**:
- Catch errors at compile time
- Better IDE support and autocomplete
- Self-documenting code through types
- Easier refactoring and maintenance

## Migration Considerations

### Development Workflow Changes

**Before**: Direct file editing → Upload to Pi
**After**: Modern dev workflow with:
- Local development server with hot reload
- Type checking and linting
- Automated testing
- Git-based deployment

### Performance Improvements

**Bundle Optimization**: Next.js automatically optimizes JavaScript bundles
**Image Optimization**: Built-in Next.js image optimization
**Caching Strategy**: React Query provides intelligent data caching
**Code Splitting**: Automatic route-based and component-based splitting

### Deployment Strategy

**Frontend**: Deployed to Vercel for optimal Next.js performance
**Backend**: Flask API remains on DigitalOcean droplet
**Database**: SQLite file-based database for simplicity
**Static Assets**: CDN distribution for improved global performance

This modernized tech stack provides a robust foundation for building a professional subtitle learning application while maintaining the simplicity of the backend architecture.