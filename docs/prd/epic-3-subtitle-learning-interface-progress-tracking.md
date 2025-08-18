# Epic 3: Subtitle Learning Interface & Progress Tracking

**Epic Goal:** Create the core learning experience with dual-language subtitle display, user progress persistence, bookmarking functionality, and learning session management, delivering the complete SubLearning value proposition for cognitive bridging through movie-based language learning.

## Story 3.1: Basic Subtitle Reading Interface

As a language learner,
I want to view movie subtitles in both my native and target languages side-by-side,
so that I can study language connections through authentic movie content.

### Acceptance Criteria
1. Split-screen layout displaying subtitles in two columns (native language | target language)
2. Subtitle lines synchronized between both languages showing corresponding translations
3. Adjustable column widths allowing users to customize reading layout preferences
4. Clear visual separation between language columns with appropriate spacing
5. Font size controls for optimal reading comfort across different screen sizes
6. Navigation controls to move between subtitle lines (previous/next buttons)
7. Current subtitle line highlighted or emphasized for reading focus
8. Responsive design ensuring readability on desktop and mobile devices

## Story 3.2: Subtitle Navigation and Playback Controls

As a language learner,
I want to control the pace of subtitle progression,
so that I can study at my optimal learning speed.

### Acceptance Criteria
1. Play/pause functionality for automatic subtitle progression with configurable timing
2. Manual navigation controls (previous line, next line) for self-paced study
3. Speed adjustment controls for automatic progression (slow, normal, fast)
4. Jump to beginning/end of subtitle file functionality
5. Keyboard shortcuts for navigation (arrow keys, spacebar) for hands-free operation
6. Current position indicator showing progress through subtitle file
7. Smooth transitions between subtitle lines without jarring interface changes
8. Pause state preservation when user navigates away and returns

## Story 3.3: User Progress Tracking System

As a language learner,
I want my learning progress automatically saved,
so that I can resume study sessions where I left off and track my advancement.

### Acceptance Criteria
1. Progress table storing user_id, movie_id, current_line_number, last_accessed timestamp
2. Automatic progress saving as user advances through subtitle lines
3. Resume functionality returning user to last studied line when reopening movie
4. Session duration tracking for learning analytics
5. Lines completed counter for each movie and overall totals
6. Progress percentage display for current movie completion status
7. Recently studied movies list on user dashboard for quick access
8. Progress data persisted across browser sessions and devices

## Story 3.4: Bookmark Functionality

As a language learner,
I want to bookmark specific subtitle lines,
so that I can return to challenging or interesting phrases for focused review.

### Acceptance Criteria
1. Bookmark button on each subtitle line for easy marking during study
2. Bookmarks table storing user_id, movie_id, line_number, bookmark_timestamp, optional_note
3. Visual indicator showing which lines are already bookmarked
4. Bookmarks management page listing all saved lines with movie titles and content preview
5. Quick navigation to bookmarked lines from bookmarks management interface
6. Remove bookmark functionality from both reading interface and management page
7. Bookmark export capability for external study tools (optional text format)
8. Search functionality within bookmarked content for specific phrases or words

## Story 3.5: Learning Dashboard and Session Management

As a language learner,
I want to view my overall learning progress and manage my study sessions,
so that I can track advancement and maintain motivation for continued learning.

### Acceptance Criteria
1. Dashboard displaying total study time, movies completed, and lines studied
2. Recent activity showing last studied movies with resume options
3. Learning streak counter tracking consecutive days of study activity
4. Weekly/monthly progress charts showing study consistency and advancement
5. Personal learning statistics including average session duration and completion rates
6. Quick access to bookmarked content and favorite movies from dashboard
7. Learning goals setting and progress tracking toward user-defined targets
8. Session history with detailed breakdown of time spent per movie and language pair