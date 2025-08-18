# Frontend Architecture

## Component Architecture

### Component Organization
```
static/
├── css/
│   ├── bootstrap.min.css          # CDN fallback
│   ├── custom.css                 # SubLearning-specific styles
│   └── learning-session.css       # Subtitle display optimizations
├── js/
│   ├── modules/
│   │   ├── auth.js               # Authentication handling
│   │   ├── subtitle-player.js    # Core learning interface
│   │   ├── progress-tracker.js   # Progress management
│   │   ├── bookmark-manager.js   # Bookmark functionality
│   │   └── movie-discovery.js    # Search and browsing
│   ├── components/
│   │   ├── dual-subtitle-display.js  # Side-by-side subtitle rendering
│   │   ├── language-selector.js      # Language pair selection
│   │   ├── progress-indicator.js     # Visual progress components
│   │   └── modal-manager.js          # Bootstrap modal handling
│   ├── utils/
│   │   ├── api-client.js         # Centralized API communication
│   │   ├── storage-helper.js     # LocalStorage management
│   │   └── error-handler.js      # Error display and recovery
│   └── app.js                    # Application initialization
└── assets/
    ├── images/
    │   └── flags/                # Language flag icons
    └── fonts/                    # Custom fonts for subtitle readability
```

### Component Template
```typescript
// Example: subtitle-player.js - Core learning component
class SubtitlePlayer {
    constructor(subLinkId, startIndex = 0) {
        this.subLinkId = subLinkId;
        this.currentIndex = startIndex;
        this.alignments = [];
        this.isPlaying = false;
        this.playbackSpeed = 3000; // 3 seconds per alignment
        
        this.initializeElements();
        this.loadAlignments();
        this.bindEvents();
    }
    
    initializeElements() {
        this.sourcePanel = document.getElementById('source-subtitles');
        this.targetPanel = document.getElementById('target-subtitles');
        this.progressBar = document.getElementById('progress-bar');
        this.playButton = document.getElementById('play-pause-btn');
        this.nextButton = document.getElementById('next-btn');
        this.prevButton = document.getElementById('prev-btn');
    }
    
    async loadAlignments(startIndex = 0, limit = 50) {
        try {
            const response = await ApiClient.get(`/subtitles/${this.subLinkId}`, {
                start_index: startIndex,
                limit: limit
            });
            this.alignments = response.alignments;
            this.totalAlignments = response.total_alignments;
            this.renderCurrentAlignment();
        } catch (error) {
            ErrorHandler.display('Failed to load subtitles', error);
        }
    }
    
    renderCurrentAlignment() {
        const alignment = this.alignments[this.currentIndex];
        if (!alignment) return;
        
        // Render source language lines
        this.sourcePanel.innerHTML = alignment.source_lines
            .map(line => `<p class="subtitle-line" data-line-id="${line.id}">${line.content}</p>`)
            .join('');
            
        // Render target language lines
        this.targetPanel.innerHTML = alignment.target_lines
            .map(line => `<p class="subtitle-line" data-line-id="${line.id}">${line.content}</p>`)
            .join('');
            
        this.updateProgress();
    }
    
    // Additional methods for navigation, progress tracking, etc.
}
```

## State Management Architecture

### State Structure
```typescript
// Browser storage-based state management
const AppState = {
    // User session state
    user: {
        id: null,
        email: null,
        nativeLanguageId: null,
        targetLanguageId: null,
        isAuthenticated: false
    },
    
    // Current learning session
    currentSession: {
        subLinkId: null,
        alignmentIndex: 0,
        startTime: null,
        duration: 0,
        isPlaying: false,
        playbackSpeed: 3000
    },
    
    // Movie discovery state
    discovery: {
        searchQuery: '',
        selectedLetter: '',
        availableMovies: [],
        filteredMovies: []
    },
    
    // Progress tracking
    progress: {
        currentMovie: null,
        completedAlignments: 0,
        totalAlignments: 0,
        sessionDuration: 0
    },
    
    // UI state
    ui: {
        currentPage: 'dashboard',
        modalOpen: null,
        errorMessage: null,
        loadingStates: new Set()
    }
};
```

### State Management Patterns
- **Centralized Updates:** All state changes go through StateManager.update() method
- **Persistence Strategy:** Critical state (progress, user preferences) saved to localStorage
- **Session Recovery:** Automatic restoration of learning session on page reload
- **Optimistic Updates:** UI updates immediately, with rollback on API failure
- **Event-Driven Updates:** Components subscribe to state changes via custom events

## Routing Architecture

### Route Organization
```
Frontend Routes (SPA-style with hash routing):
#/                          → Dashboard view
#/movies                    → Movie discovery and search
#/movies/search/{query}     → Search results
#/movies/letter/{letter}    → Alphabetical browsing
#/learning/{sub_link_id}    → Subtitle learning interface
#/progress                  → Progress dashboard
#/bookmarks                 → Bookmark management
#/settings                  → User preferences
#/auth/login               → Authentication forms
#/auth/register            → Registration flow
```

### Protected Route Pattern
```typescript
// Route protection for authenticated-only pages
class Router {
    static init() {
        window.addEventListener('hashchange', this.handleRoute.bind(this));
        this.handleRoute(); // Handle initial route
    }
    
    static handleRoute() {
        const hash = window.location.hash.slice(1) || '/';
        const route = this.parseRoute(hash);
        
        // Check authentication for protected routes
        if (this.isProtectedRoute(route.path) && !AppState.user.isAuthenticated) {
            this.redirect('/auth/login');
            return;
        }
        
        this.renderRoute(route);
    }
    
    static isProtectedRoute(path) {
        const protectedPaths = ['/learning', '/progress', '/bookmarks', '/settings'];
        return protectedPaths.some(protected => path.startsWith(protected));
    }
    
    static redirect(path) {
        window.location.hash = path;
    }
}
```

## Frontend Services Layer

### API Client Setup
```typescript
// Centralized API communication with error handling and retry logic
class ApiClient {
    static baseURL = '/api';
    static defaultHeaders = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };
    
    static async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method,
            headers: { ...this.defaultHeaders, ...options.headers },
            credentials: 'same-origin' // Include session cookies
        };
        
        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            config.body = JSON.stringify(data);
        } else if (data && method === 'GET') {
            const params = new URLSearchParams(data);
            url += `?${params.toString()}`;
        }
        
        try {
            LoadingManager.start(endpoint);
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new ApiError(response.status, await response.text());
            }
            
            return await response.json();
        } catch (error) {
            ErrorHandler.handle(error, { endpoint, method, data });
            throw error;
        } finally {
            LoadingManager.stop(endpoint);
        }
    }
    
    static get(endpoint, params) {
        return this.request('GET', endpoint, params);
    }
    
    static post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }
    
    static put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }
    
    static delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
}
```

### Service Example
```typescript
// Progress tracking service with automatic persistence
class ProgressService {
    static async updateProgress(subLinkId, alignmentIndex, sessionDuration) {
        const progressData = {
            current_alignment_index: alignmentIndex,
            session_duration_minutes: Math.floor(sessionDuration / 60000)
        };
        
        try {
            // Optimistic update
            StateManager.update('progress', {
                currentAlignmentIndex: alignmentIndex,
                sessionDuration: sessionDuration
            });
            
            // Persist to server
            const result = await ApiClient.put(`/progress/${subLinkId}`, progressData);
            
            // Update with server response
            StateManager.update('progress', result);
            
            return result;
        } catch (error) {
            // Rollback on failure, queue for retry
            this.queueProgressUpdate(subLinkId, progressData);
            throw error;
        }
    }
    
    static queueProgressUpdate(subLinkId, data) {
        const queue = StorageHelper.get('progress_queue', []);
        queue.push({ subLinkId, data, timestamp: Date.now() });
        StorageHelper.set('progress_queue', queue);
    }
    
    static async retryQueuedUpdates() {
        const queue = StorageHelper.get('progress_queue', []);
        for (const item of queue) {
            try {
                await ApiClient.put(`/progress/${item.subLinkId}`, item.data);
            } catch (error) {
                console.warn('Retry failed for progress update:', error);
            }
        }
        StorageHelper.remove('progress_queue');
    }
}
```
