# React Component Architecture Specifications

## Component Design Principles

### 1. Component Composition Strategy
- **Atomic Design**: Build components from smallest to largest (atoms → molecules → organisms → templates → pages)
- **Single Responsibility**: Each component has one clear purpose
- **Props Interface**: Well-defined TypeScript interfaces for all props
- **Accessibility First**: WCAG AA compliance built into every component

### 2. shadcn/ui Integration Pattern
- Use shadcn/ui primitives as foundation (MCP server available)
- Customize with Tailwind classes for SubLearning-specific styling
- Extend components through composition, not modification
- Maintain consistent design tokens across all components

## Core Component Library

### UI Foundation (shadcn/ui + Custom)

#### Button Components
```typescript
// components/ui/button.tsx (shadcn/ui base)
// Extended for SubLearning-specific variants

interface SubLearningButtonProps extends ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' | 'learning'
  size?: 'default' | 'sm' | 'lg' | 'icon' | 'subtitle-control'
}

// Usage examples:
<Button variant="learning" size="subtitle-control">
  <Play className="h-4 w-4" />
</Button>
```

#### Card Components
```typescript
// Learning-optimized card variants
interface LearningCardProps extends CardProps {
  variant?: 'default' | 'subtitle-panel' | 'progress-card' | 'movie-card'
  borderAccent?: 'source' | 'target' | 'neutral'
}

// Subtitle panel with language-specific styling
<Card variant="subtitle-panel" borderAccent="source">
  <CardHeader>
    <CardTitle>Source Language</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Subtitle content */}
  </CardContent>
</Card>
```

### Authentication Components

#### LoginForm Component
```typescript
// components/auth/LoginForm.tsx
interface LoginFormProps {
  onSuccess?: (user: UserData) => void
  redirectTo?: string
  showSocialAuth?: boolean
}

export function LoginForm({ onSuccess, redirectTo = '/dashboard', showSocialAuth = true }: LoginFormProps) {
  const form = useForm<LoginSchema>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' }
  })
  
  const { login, isLoggingIn } = useAuth()
  
  // Implementation with React Hook Form + shadcn/ui form components
}
```

#### OAuthButtons Component
```typescript
// components/auth/OAuthButtons.tsx
interface OAuthButtonsProps {
  providers: OAuthProvider[]
  onSuccess?: (user: UserData) => void
  orientation?: 'horizontal' | 'vertical'
}

// Renders provider-specific buttons with icons and proper styling
```

### Movie Discovery Components

#### MovieCard Component
```typescript
// components/movies/MovieCard.tsx
interface MovieCardProps {
  movie: Movie
  variant?: 'grid' | 'list' | 'continue-learning'
  onSelect: (movie: Movie) => void
  showProgress?: boolean
  className?: string
}

export function MovieCard({ movie, variant = 'grid', onSelect, showProgress = false }: MovieCardProps) {
  return (
    <Card className={cn('cursor-pointer transition-all hover:shadow-md', className)}>
      <CardContent className="p-4">
        {variant === 'continue-learning' && showProgress && (
          <Progress value={movie.progress?.percentage || 0} className="mb-2" />
        )}
        <h3 className="font-semibold">{movie.title}</h3>
        <p className="text-sm text-muted-foreground">{movie.year}</p>
        {movie.language_pair && (
          <Badge variant="secondary">
            {movie.language_pair.source} → {movie.language_pair.target}
          </Badge>
        )}
      </CardContent>
    </Card>
  )
}
```

#### SearchBar Component
```typescript
// components/movies/SearchBar.tsx
interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  debounceMs?: number
  showFilters?: boolean
}

// Implements debounced search with optional filter toggles
```

#### AlphabetNav Component
```typescript
// components/movies/AlphabetNav.tsx
interface AlphabetNavProps {
  selectedLetter?: string
  onLetterSelect: (letter: string) => void
  availableLetters: string[]
  orientation?: 'horizontal' | 'vertical'
}

// Renders A-Z navigation with active states and availability indicators
```

### Learning Interface Components

#### SubtitlePlayer Component (Core)
```typescript
// components/learning/SubtitlePlayer.tsx
interface SubtitlePlayerProps {
  subLinkId: string
  startIndex?: number
  autoPlay?: boolean
  onProgress?: (index: number) => void
  onComplete?: () => void
}

// Main learning interface orchestrating all subtitle components
```

#### DualSubtitleDisplay Component
```typescript
// components/learning/DualSubtitleDisplay.tsx
interface DualSubtitleDisplayProps {
  sourceLines: SubtitleLine[]
  targetLines: SubtitleLine[]
  layout?: 'side-by-side' | 'stacked'
  fontSize?: 'sm' | 'base' | 'lg' | 'xl'
  highlightActive?: boolean
  onLineClick?: (lineId: string, type: 'source' | 'target') => void
}

export function DualSubtitleDisplay({ 
  sourceLines, 
  targetLines, 
  layout = 'side-by-side',
  fontSize = 'base',
  highlightActive = true 
}: DualSubtitleDisplayProps) {
  return (
    <div className={cn(
      'grid gap-6',
      layout === 'side-by-side' ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'
    )}>
      <SubtitlePanel 
        title="Source Language"
        lines={sourceLines}
        type="source"
        fontSize={fontSize}
        highlightActive={highlightActive}
      />
      <SubtitlePanel 
        title="Target Language"
        lines={targetLines}
        type="target"
        fontSize={fontSize}
        highlightActive={highlightActive}
      />
    </div>
  )
}
```

#### PlaybackControls Component
```typescript
// components/learning/PlaybackControls.tsx
interface PlaybackControlsProps {
  isPlaying: boolean
  canGoNext: boolean
  canGoPrevious: boolean
  playbackSpeed: number
  onPlayPause: () => void
  onNext: () => void
  onPrevious: () => void
  onSpeedChange: (speed: number) => void
  onJumpTo?: (index: number) => void
}

// Comprehensive playback controls with keyboard shortcuts
```

#### ProgressTracker Component
```typescript
// components/learning/ProgressTracker.tsx
interface ProgressTrackerProps {
  currentIndex: number
  totalCount: number
  sessionDuration: number
  completionPercentage: number
  onBookmark?: () => void
  onPause?: () => void
  showSessionStats?: boolean
}

// Visual progress indicator with session statistics
```

### Dashboard Components

#### StatsCard Component
```typescript
// components/dashboard/StatsCard.tsx
interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ComponentType<{ className?: string }>
  trend?: {
    value: number
    label: string
    isPositive: boolean
  }
  className?: string
}

// Reusable statistics card for dashboard metrics
```

#### RecentActivity Component
```typescript
// components/dashboard/RecentActivity.tsx
interface RecentActivityProps {
  activities: Activity[]
  maxItems?: number
  showViewAll?: boolean
  onActivityClick?: (activity: Activity) => void
}

// Recent learning activity feed with proper relative time formatting
```

#### ContinueLearning Component
```typescript
// components/dashboard/ContinueLearning.tsx
interface ContinueLearningProps {
  sessions: InProgressSession[]
  onContinue: (session: InProgressSession) => void
  onStartNew: () => void
  maxSessions?: number
}

// Quick access to resume learning sessions
```

### Common/Utility Components

#### Navigation Component
```typescript
// components/common/Navigation.tsx
interface NavigationProps {
  user?: User | null
  variant?: 'header' | 'sidebar' | 'mobile'
  onLanguageChange?: (source: string, target: string) => void
}

// Main site navigation with responsive behavior
```

#### LanguageSelector Component
```typescript
// components/common/LanguageSelector.tsx
interface LanguageSelectorProps {
  sourceLanguage?: string
  targetLanguage?: string
  availableLanguages: Language[]
  onSelectionChange: (source: string, target: string) => void
  variant?: 'dropdown' | 'modal' | 'inline'
  showFlags?: boolean
}

// Language pair selection with flag icons and search
```

#### LoadingSpinner Component
```typescript
// components/common/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  className?: string
}

// Consistent loading states across the application
```

## Component Patterns

### 1. Compound Components Pattern
```typescript
// For complex components like SubtitlePlayer
<SubtitlePlayer subLinkId="123">
  <SubtitlePlayer.Header />
  <SubtitlePlayer.Display layout="side-by-side" />
  <SubtitlePlayer.Controls />
  <SubtitlePlayer.Progress />
</SubtitlePlayer>
```

### 2. Render Props Pattern
```typescript
// For sharing stateful logic
<ProgressProvider subLinkId="123">
  {({ progress, updateProgress, isLoading }) => (
    <div>
      {/* Components using progress state */}
    </div>
  )}
</ProgressProvider>
```

### 3. Custom Hooks Pattern
```typescript
// Extracting component logic into reusable hooks
function useSubtitlePlayer(subLinkId: string) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  
  // Complex subtitle player logic
  
  return {
    currentIndex,
    isPlaying,
    handleNext,
    handlePrevious,
    togglePlayback,
  }
}
```

## Styling Conventions

### 1. Tailwind CSS Classes
```typescript
// Consistent spacing and sizing
const spacing = {
  xs: 'p-1',
  sm: 'p-2', 
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8'
}

// Learning-specific styles
const learningStyles = {
  subtitleText: 'text-lg leading-relaxed font-medium',
  sourcePanel: 'border-l-4 border-l-blue-500',
  targetPanel: 'border-l-4 border-l-green-500',
  activeSubtitle: 'bg-blue-50 border-blue-200',
}
```

### 2. CSS Custom Properties
```css
/* globals.css - Learning-optimized CSS variables */
:root {
  --subtitle-font-size: 1.125rem;
  --subtitle-line-height: 1.75;
  --subtitle-spacing: 0.75rem;
  --learning-accent-source: theme('colors.blue.500');
  --learning-accent-target: theme('colors.green.500');
}
```

### 3. Responsive Design Patterns
```typescript
// Mobile-first responsive components
const ResponsiveSubtitleDisplay = () => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
    {/* Stacked on mobile, side-by-side on desktop */}
  </div>
)
```

## Error Handling Patterns

### 1. Error Boundary Components
```typescript
// components/common/ErrorBoundary.tsx
interface ErrorBoundaryProps {
  fallback?: React.ComponentType<{ error: Error }>
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  children: React.ReactNode
}

// Wrap components that might fail
<ErrorBoundary fallback={SubtitleErrorFallback}>
  <SubtitlePlayer subLinkId="123" />
</ErrorBoundary>
```

### 2. Loading and Error States
```typescript
// Consistent patterns for async states
function MovieList() {
  const { data: movies, isLoading, error } = useMovies()
  
  if (isLoading) return <LoadingSpinner text="Loading movies..." />
  if (error) return <ErrorMessage error={error} retry={() => refetch()} />
  if (!movies?.length) return <EmptyState message="No movies found" />
  
  return <MovieGrid movies={movies} />
}
```

## Testing Strategy

### 1. Component Testing with React Testing Library
```typescript
// __tests__/components/MovieCard.test.tsx
test('MovieCard displays movie information correctly', () => {
  const mockMovie = { id: '1', title: 'Test Movie', year: 2024 }
  
  render(<MovieCard movie={mockMovie} onSelect={jest.fn()} />)
  
  expect(screen.getByText('Test Movie')).toBeInTheDocument()
  expect(screen.getByText('2024')).toBeInTheDocument()
})
```

### 2. Integration Testing
```typescript
// Test component interactions
test('SubtitlePlayer advances to next subtitle on next button click', async () => {
  render(<SubtitlePlayer subLinkId="123" />)
  
  await waitFor(() => {
    expect(screen.getByText('Subtitle 1')).toBeInTheDocument()
  })
  
  fireEvent.click(screen.getByLabelText('Next subtitle'))
  
  await waitFor(() => {
    expect(screen.getByText('Subtitle 2')).toBeInTheDocument()
  })
})
```

This component architecture provides a solid foundation for building the SubLearning React application with modern patterns, excellent user experience, and maintainable code structure.