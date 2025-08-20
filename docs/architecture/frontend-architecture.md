# Frontend Architecture

## React + Next.js Architecture

### Project Structure
```
sublearning-frontend/
├── src/
│   ├── app/                      # Next.js 13+ App Router
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/
│   │   ├── movies/
│   │   │   ├── [id]/
│   │   │   └── search/
│   │   ├── learning/
│   │   │   └── [subLinkId]/
│   │   ├── layout.tsx            # Root layout with navigation
│   │   ├── page.tsx              # Landing page
│   │   └── globals.css           # Global styles + Tailwind
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── progress.tsx
│   │   │   └── ...
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── OAuthButtons.tsx
│   │   ├── learning/
│   │   │   ├── SubtitlePlayer.tsx     # Core learning interface
│   │   │   ├── DualSubtitleDisplay.tsx
│   │   │   ├── PlaybackControls.tsx
│   │   │   └── ProgressTracker.tsx
│   │   ├── movies/
│   │   │   ├── MovieCard.tsx
│   │   │   ├── MovieGrid.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── AlphabetNav.tsx
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── RecentActivity.tsx
│   │   │   └── ContinueLearning.tsx
│   │   └── common/
│   │       ├── Navigation.tsx
│   │       ├── LanguageSelector.tsx
│   │       └── LoadingSpinner.tsx
│   ├── lib/
│   │   ├── api.ts                # API client with React Query
│   │   ├── auth.ts               # Authentication utilities
│   │   ├── utils.ts              # Utility functions
│   │   └── validations.ts        # Form validation schemas
│   ├── hooks/
│   │   ├── useAuth.ts            # Authentication state
│   │   ├── useProgress.ts        # Progress tracking
│   │   ├── useSubtitles.ts       # Subtitle data management
│   │   └── useLocalStorage.ts    # Persistent state
│   ├── types/
│   │   ├── auth.ts
│   │   ├── movies.ts
│   │   ├── subtitles.ts
│   │   └── progress.ts
│   └── styles/
│       └── globals.css           # Tailwind + custom CSS
├── public/
│   ├── images/
│   │   └── flags/                # Language flag icons
│   └── fonts/                    # Custom fonts for subtitle readability
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── components.json               # shadcn/ui configuration
```

### React Component Examples

#### Core Learning Interface - SubtitlePlayer
```typescript
// components/learning/SubtitlePlayer.tsx
import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Play, Pause, SkipForward, SkipBack } from 'lucide-react'
import { api } from '@/lib/api'
import { useProgress } from '@/hooks/useProgress'
import type { SubtitleAlignment } from '@/types/subtitles'

interface SubtitlePlayerProps {
  subLinkId: string
  startIndex?: number
}

export function SubtitlePlayer({ subLinkId, startIndex = 0 }: SubtitlePlayerProps) {
  const [currentIndex, setCurrentIndex] = useState(startIndex)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(3000)
  
  // React Query for data fetching
  const { data: subtitleData, isLoading, error } = useQuery({
    queryKey: ['subtitles', subLinkId, currentIndex],
    queryFn: () => api.getSubtitles(subLinkId, currentIndex, 50),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
  
  // Custom hook for progress tracking
  const { updateProgress, progressData } = useProgress(subLinkId)
  
  // Auto-play functionality
  useEffect(() => {
    if (!isPlaying || !subtitleData) return
    
    const timer = setTimeout(() => {
      handleNext()
    }, playbackSpeed)
    
    return () => clearTimeout(timer)
  }, [isPlaying, currentIndex, playbackSpeed, subtitleData])
  
  const handleNext = () => {
    if (currentIndex < (subtitleData?.total_alignments ?? 0) - 1) {
      const newIndex = currentIndex + 1
      setCurrentIndex(newIndex)
      updateProgress({ alignmentIndex: newIndex })
    } else {
      setIsPlaying(false)
    }
  }
  
  const handlePrevious = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1
      setCurrentIndex(newIndex)
      updateProgress({ alignmentIndex: newIndex })
    }
  }
  
  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }
  
  const currentAlignment = subtitleData?.alignments[currentIndex]
  const progressPercentage = subtitleData?.total_alignments 
    ? (currentIndex / subtitleData.total_alignments) * 100 
    : 0
  
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  if (!currentAlignment) return <NoSubtitlesFound />
  
  return (
    <div className="space-y-6 max-w-6xl mx-auto p-6">
      {/* Progress Header */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">
              Line {currentIndex + 1} of {subtitleData?.total_alignments}
            </span>
            <span className="text-sm text-muted-foreground">
              {Math.round(progressPercentage)}% Complete
            </span>
          </div>
          <Progress value={progressPercentage} className="w-full" />
        </CardContent>
      </Card>
      
      {/* Dual Subtitle Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SubtitlePanel 
          title="Source Language"
          lines={currentAlignment.source_lines}
          className="border-l-4 border-l-blue-500"
        />
        <SubtitlePanel 
          title="Target Language"
          lines={currentAlignment.target_lines}
          className="border-l-4 border-l-green-500"
        />
      </div>
      
      {/* Playback Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-center space-x-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handlePrevious}
              disabled={currentIndex === 0}
            >
              <SkipBack className="h-4 w-4" />
            </Button>
            
            <Button 
              variant="default" 
              size="lg" 
              onClick={togglePlayback}
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </Button>
            
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleNext}
              disabled={currentIndex >= (subtitleData?.total_alignments ?? 0) - 1}
            >
              <SkipForward className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="mt-4 flex items-center justify-center space-x-2">
            <span className="text-sm text-muted-foreground">Speed:</span>
            <select 
              value={playbackSpeed} 
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="text-sm border rounded px-2 py-1"
            >
              <option value={2000}>Fast (2s)</option>
              <option value={3000}>Normal (3s)</option>
              <option value={5000}>Slow (5s)</option>
            </select>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Sub-component for subtitle panels
function SubtitlePanel({ title, lines, className }: {
  title: string
  lines: Array<{ id: string; content: string }>
  className?: string
}) {
  return (
    <Card className={className}>
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="space-y-3">
          {lines.map((line) => (
            <p 
              key={line.id}
              className="text-lg leading-relaxed p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              {line.content}
            </p>
          ))}
        </div>
      </CardContent>
    </Card>
  )
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
