# Tech Stack

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | JavaScript (ES6+) | Latest | Client-side interactivity | Native browser support, no build complexity for Pi |
| Frontend Framework | Vanilla JS + Bootstrap | Bootstrap 5.3 | Responsive UI without framework overhead | Lightweight, Pi-optimized, matches PRD requirements |
| UI Component Library | Bootstrap | 5.3.x | Pre-built responsive components | Minimal CSS/JS footprint, proven reliability |
| State Management | Browser SessionStorage/LocalStorage | Native | Client-side state persistence | Simple, no dependencies, works offline |
| Backend Language | Python | 3.9+ | Server-side application logic | Pi compatibility, Flask ecosystem, PRD requirement |
| Backend Framework | Flask | 2.3.x | Web application framework | Lightweight, Pi-suitable, PRD technical assumption |
| API Style | REST | N/A | HTTP API endpoints | Simple, stateless, efficient for Pi resources |
| Database | SQLite | 3.x | All data storage (users, subtitles, progress) | Single-file, Pi-optimized, no server overhead |
| Cache | SQLite WAL mode | Built-in | Query performance optimization | Built-in SQLite feature, no additional dependencies |
| File Storage | Local filesystem | N/A | Static assets (CSS, JS, images) | Direct Pi storage, no cloud dependencies |
| Authentication | Flask-Login + OAuth | Flask-Login 0.6.x | User sessions and social login | Lightweight session management for Pi |
| Frontend Testing | None (Manual) | N/A | UI validation | Resource conservation for Pi deployment |
| Backend Testing | pytest | 7.x | Unit and integration testing | Lightweight, Python standard |
| E2E Testing | Manual | N/A | User flow validation | Resource-efficient for Pi constraints |
| Build Tool | None | N/A | Direct file serving | Eliminates build complexity for Pi |
| Bundler | None | N/A | Static asset delivery | Direct serving from Pi filesystem |
| IaC Tool | None (Manual setup) | N/A | Pi configuration | Manual Pi setup and configuration |
| CI/CD | Git hooks (local) | N/A | Simple deployment automation | Local deployment to Pi |
| Monitoring | Flask logging | Built-in | Application monitoring | Built-in Python logging to files |
| Logging | Python logging | Built-in | Error tracking and debugging | Standard library, file-based logs |
| CSS Framework | Bootstrap + Custom CSS | 5.3.x | Responsive styling | Lightweight, customizable for subtitle reading |
