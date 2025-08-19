/**
 * SubtitlePlayer Module
 * Core learning interface logic that coordinates subtitle loading, navigation, and progress tracking
 */
class SubtitlePlayer {
    constructor(subLinkId, startIndex = 0) {
        this.subLinkId = subLinkId;
        this.currentIndex = startIndex;
        this.alignmentData = [];
        this.subtitleLines = {};
        this.totalAlignments = 0;
        this.batchSize = 50;
        
        // Playback control properties
        this.playbackState = {
            isPlaying: false,
            speed: 3000, // Default 3 seconds
            timer: null,
            startTime: null,
            pausedAt: null
        };
        
        // Initialize components
        this.dualDisplay = new DualSubtitleDisplay();
        
        // Initialize progress tracking (will be imported in template)
        this.progressTracker = null;
        if (typeof progressTracker !== 'undefined') {
            this.progressTracker = progressTracker;
        }
        
        // UI elements
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.progressTime = document.getElementById('progress-time');
        this.btnPrev = document.getElementById('btn-prev');
        this.btnNext = document.getElementById('btn-next');
        this.btnPlayPause = document.getElementById('btn-play-pause');
        this.speedSelector = document.getElementById('speed-selector');
        this.loadingContainer = document.getElementById('loading-container');
        this.errorContainer = document.getElementById('error-container');
        this.errorMessage = document.getElementById('error-message');
        
        // Override the dual display's alignment change callback
        this.dualDisplay.onAlignmentChange = (index) => {
            this.onAlignmentChanged(index);
        };
        
        // Set up event listeners
        this.initializeEventListeners();
        
        // Start loading data
        this.initialize();
    }
    
    /**
     * Initialize event listeners for navigation controls
     */
    initializeEventListeners() {
        if (this.btnPrev) {
            this.btnPrev.addEventListener('click', () => this.previousAlignment());
        }
        
        if (this.btnNext) {
            this.btnNext.addEventListener('click', () => this.nextAlignment());
        }
        
        // Playback control listeners
        if (this.btnPlayPause) {
            this.btnPlayPause.addEventListener('click', () => this.togglePlayback());
        }
        
        if (this.speedSelector) {
            this.speedSelector.addEventListener('change', (e) => {
                this.setPlaybackSpeed(parseInt(e.target.value));
            });
        }
        
        // Progress tracking - update every 5 alignments or 30 seconds
        this.progressUpdateCounter = 0;
        this.lastProgressUpdate = Date.now();
        
        // Auto-save progress periodically
        setInterval(() => {
            this.autoSaveProgress();
        }, 30000); // 30 seconds
        
        // Handle browser visibility changes to pause auto-play
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.playbackState.isPlaying) {
                this.pauseAutoPlay();
            }
        });
        
        // Handle beforeunload to save state
        window.addEventListener('beforeunload', () => {
            this.savePlaybackState();
        });
    }
    
    /**
     * Initialize the subtitle player by loading user progress and alignment data
     */
    async initialize() {
        try {
            this.showLoading(true);
            
            // Start progress tracking session
            if (this.progressTracker) {
                const restoredProgress = await this.progressTracker.startSession(this.subLinkId);
                if (restoredProgress && restoredProgress.current_alignment_index) {
                    this.currentIndex = restoredProgress.current_alignment_index;
                }
            } else {
                // Fallback to legacy progress loading
                const progress = await this.loadUserProgress();
                if (progress && progress.current_alignment_index) {
                    this.currentIndex = progress.current_alignment_index;
                }
            }
            
            // Load initial batch of alignment data
            await this.loadAlignmentData(this.currentIndex);
            
            // Set up the display
            this.updateDisplay();
            
            // Restore playback state
            this.restorePlaybackState();
            
            this.showLoading(false);
            
        } catch (error) {
            console.error('Failed to initialize subtitle player:', error);
            this.showError('Failed to load subtitle data. Please refresh the page.');
        }
    }
    
    /**
     * Load user progress for the current subtitle pair
     */
    async loadUserProgress() {
        try {
            const response = await fetch(`/api/progress/${this.subLinkId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                if (response.status === 404) {
                    return null; // No progress exists yet
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.warn('Failed to load user progress:', error);
            return null;
        }
    }
    
    /**
     * Load alignment data from the API
     */
    async loadAlignmentData(startIndex = 0) {
        try {
            // Validate parameters
            if (startIndex < 0) {
                throw new Error('Start index cannot be negative');
            }
            
            const url = `/api/subtitles/${this.subLinkId}?start_index=${startIndex}&limit=${this.batchSize}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            // Validate response structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            // Store alignment data and subtitle lines
            this.alignmentData = Array.isArray(data.alignments) ? data.alignments : [];
            this.subtitleLines = data.subtitle_lines || {};
            this.totalAlignments = data.pagination?.total_alignments || 0;
            
            // Set language titles if we have subtitle data
            if (this.alignmentData.length > 0) {
                this.setLanguageTitles();
            }
            
            return data;
            
        } catch (error) {
            console.error('Failed to load alignment data:', error);
            throw error;
        }
    }
    
    /**
     * Set language titles based on subtitle data
     */
    setLanguageTitles() {
        // This would be enhanced with actual language names from the API
        this.dualDisplay.setLanguageTitles('Source Language', 'Target Language');
    }
    
    /**
     * Update the display with current alignment data
     */
    updateDisplay() {
        if (this.alignmentData.length === 0) {
            this.dualDisplay.showPlaceholder('No subtitle alignments available');
            return;
        }
        
        // Render alignments in the dual display
        this.dualDisplay.renderAlignments(this.alignmentData, this.subtitleLines, this.subtitleLines);
        
        // Update current index to be relative to loaded data
        const relativeIndex = Math.max(0, this.currentIndex - (this.alignmentData[0]?.index || 0));
        this.dualDisplay.highlightAlignment(relativeIndex, this.playbackState.isPlaying);
        
        // Update progress display
        this.updateProgressDisplay();
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    /**
     * Update progress bar and text with enhanced details
     */
    updateProgressDisplay() {
        if (this.progressBar && this.progressText) {
            const progress = this.totalAlignments > 0 ? (this.currentIndex / this.totalAlignments) * 100 : 0;
            this.progressBar.style.width = `${progress}%`;
            this.progressBar.setAttribute('aria-valuenow', progress);
            this.progressText.textContent = `${this.currentIndex + 1} / ${this.totalAlignments}`;
            
            // Update percentage display
            if (this.progressPercentage) {
                this.progressPercentage.textContent = `${Math.round(progress)}%`;
            }
            
            // Update estimated time remaining
            if (this.progressTime) {
                this.updateTimeEstimate();
            }
        }
    }
    
    /**
     * Update estimated time remaining
     */
    updateTimeEstimate() {
        if (!this.progressTime || !this.playbackState.isPlaying) {
            if (this.progressTime) {
                this.progressTime.textContent = 'Estimated time: --';
            }
            return;
        }
        
        const remainingAlignments = this.totalAlignments - this.currentIndex - 1;
        const estimatedSeconds = Math.ceil((remainingAlignments * this.playbackState.speed) / 1000);
        
        if (estimatedSeconds <= 0) {
            this.progressTime.textContent = 'Complete!';
            return;
        }
        
        const minutes = Math.floor(estimatedSeconds / 60);
        const seconds = estimatedSeconds % 60;
        
        if (minutes > 0) {
            this.progressTime.textContent = `Estimated time: ${minutes}m ${seconds}s`;
        } else {
            this.progressTime.textContent = `Estimated time: ${seconds}s`;
        }
    }
    
    /**
     * Update navigation button states with boundary indicators
     */
    updateNavigationButtons() {
        const atStart = this.currentIndex <= 0;
        const atEnd = this.currentIndex >= this.totalAlignments - 1;
        
        if (this.btnPrev) {
            this.btnPrev.disabled = atStart;
            if (atStart) {
                this.btnPrev.classList.add('at-boundary');
            } else {
                this.btnPrev.classList.remove('at-boundary');
            }
        }
        
        if (this.btnNext) {
            this.btnNext.disabled = atEnd;
            if (atEnd) {
                this.btnNext.classList.add('at-boundary');
            } else {
                this.btnNext.classList.remove('at-boundary');
            }
        }
        
        // Update first/last buttons if they exist
        const btnFirst = document.getElementById('btn-first');
        const btnLast = document.getElementById('btn-last');
        
        if (btnFirst) {
            btnFirst.disabled = atStart;
            btnFirst.classList.toggle('at-boundary', atStart);
        }
        
        if (btnLast) {
            btnLast.disabled = atEnd;
            btnLast.classList.toggle('at-boundary', atEnd);
        }
        
        // Auto-pause if at end during playback
        if (atEnd && this.playbackState.isPlaying) {
            this.pauseAutoPlay();
        }
    }
    
    /**
     * Navigate to previous alignment
     */
    async previousAlignment() {
        if (this.currentIndex <= 0) return;
        
        this.currentIndex--;
        
        // Check if we need to load previous batch
        const firstLoadedIndex = this.alignmentData[0]?.index || 0;
        if (this.currentIndex < firstLoadedIndex) {
            const newStartIndex = Math.max(0, this.currentIndex - Math.floor(this.batchSize / 2));
            await this.loadAlignmentData(newStartIndex);
            this.updateDisplay();
        } else {
            const relativeIndex = this.currentIndex - firstLoadedIndex;
            this.dualDisplay.highlightAlignment(relativeIndex, false);
            this.updateProgressDisplay();
            this.updateNavigationButtons();
        }
        
        this.onAlignmentChanged(this.currentIndex);
    }
    
    /**
     * Navigate to next alignment
     */
    async nextAlignment() {
        if (this.currentIndex >= this.totalAlignments - 1) return;
        
        this.currentIndex++;
        
        // Check if we need to load next batch
        const lastLoadedIndex = this.alignmentData[this.alignmentData.length - 1]?.index || 0;
        if (this.currentIndex > lastLoadedIndex) {
            await this.loadAlignmentData(this.currentIndex);
            this.updateDisplay();
        } else {
            const firstLoadedIndex = this.alignmentData[0]?.index || 0;
            const relativeIndex = this.currentIndex - firstLoadedIndex;
            this.dualDisplay.highlightAlignment(relativeIndex, this.playbackState.isPlaying);
            this.updateProgressDisplay();
            this.updateNavigationButtons();
        }
        
        this.onAlignmentChanged(this.currentIndex);
    }
    
    /**
     * Handle alignment change events
     */
    onAlignmentChanged(index) {
        this.currentIndex = index;
        this.updateProgressDisplay();
        this.updateNavigationButtons();
        
        // Update progress tracker with new position
        if (this.progressTracker) {
            this.progressTracker.updateProgress(index);
        } else {
            // Fallback to legacy progress tracking
            this.progressUpdateCounter++;
            if (this.progressUpdateCounter >= 5 || Date.now() - this.lastProgressUpdate > 30000) {
                this.saveProgress();
            }
        }
    }
    
    /**
     * Save current progress to the server
     */
    async saveProgress() {
        try {
            const response = await fetch(`/api/progress/${this.subLinkId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    current_alignment_index: this.currentIndex
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            this.progressUpdateCounter = 0;
            this.lastProgressUpdate = Date.now();
            
        } catch (error) {
            console.warn('Failed to save progress:', error);
        }
    }
    
    /**
     * Auto-save progress periodically
     */
    autoSaveProgress() {
        if (this.progressUpdateCounter > 0) {
            this.saveProgress();
        }
    }
    
    /**
     * Jump to a specific alignment index
     */
    async jumpToAlignment(index) {
        if (index < 0 || index >= this.totalAlignments) return;
        
        this.currentIndex = index;
        
        // Check if the target index is in currently loaded data
        const firstLoaded = this.alignmentData[0]?.index || 0;
        const lastLoaded = this.alignmentData[this.alignmentData.length - 1]?.index || 0;
        
        if (index < firstLoaded || index > lastLoaded) {
            // Need to load new batch centered around target index
            const newStartIndex = Math.max(0, index - Math.floor(this.batchSize / 2));
            await this.loadAlignmentData(newStartIndex);
            this.updateDisplay();
        } else {
            const relativeIndex = index - firstLoaded;
            this.dualDisplay.highlightAlignment(relativeIndex, false);
            this.updateProgressDisplay();
            this.updateNavigationButtons();
        }
        
        this.onAlignmentChanged(index);
    }
    
    /**
     * Show or hide loading indicator
     */
    showLoading(show) {
        if (this.loadingContainer) {
            this.loadingContainer.style.display = show ? 'block' : 'none';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showLoading(false);
        
        if (this.errorMessage) {
            this.errorMessage.textContent = message;
        }
        
        if (this.errorContainer) {
            this.errorContainer.style.display = 'block';
        }
    }
    
    /**
     * Hide error message
     */
    hideError() {
        if (this.errorContainer) {
            this.errorContainer.style.display = 'none';
        }
    }
    
    /**
     * Get current alignment data
     */
    getCurrentAlignment() {
        const firstLoadedIndex = this.alignmentData[0]?.index || 0;
        const relativeIndex = this.currentIndex - firstLoadedIndex;
        
        if (relativeIndex >= 0 && relativeIndex < this.alignmentData.length) {
            return this.alignmentData[relativeIndex];
        }
        
        return null;
    }
    
    /**
     * Get total number of alignments
     */
    getTotalAlignments() {
        return this.totalAlignments;
    }
    
    /**
     * Get current index
     */
    getCurrentIndex() {
        return this.currentIndex;
    }
    
    /**
     * Toggle playback state between playing and paused
     */
    togglePlayback() {
        if (this.playbackState.isPlaying) {
            this.pauseAutoPlay();
        } else {
            this.startAutoPlay();
        }
    }
    
    /**
     * Start automatic playback progression
     */
    startAutoPlay() {
        if (this.playbackState.isPlaying) {
            return; // Already playing
        }
        
        // Can't start if at the end
        if (this.currentIndex >= this.totalAlignments - 1) {
            return;
        }
        
        this.playbackState.isPlaying = true;
        this.playbackState.startTime = Date.now();
        this.playbackState.pausedAt = null;
        
        // Update UI
        this.updatePlaybackUI();
        
        // Start the timer
        this.restartPlaybackTimer();
        
        // Save state
        this.savePlaybackState();
    }
    
    /**
     * Pause automatic playback progression
     */
    pauseAutoPlay() {
        if (!this.playbackState.isPlaying) {
            return; // Already paused
        }
        
        this.playbackState.isPlaying = false;
        this.playbackState.pausedAt = this.currentIndex;
        
        // Clear timer
        if (this.playbackState.timer) {
            clearInterval(this.playbackState.timer);
            this.playbackState.timer = null;
        }
        
        // Update UI
        this.updatePlaybackUI();
        
        // Save state
        this.savePlaybackState();
    }
    
    /**
     * Set playback speed in milliseconds
     */
    setPlaybackSpeed(speed) {
        // Validate speed (1-5 seconds)
        const validSpeed = Math.max(1000, Math.min(5000, speed));
        
        // Only update if speed actually changed to avoid unnecessary work
        if (this.playbackState.speed === validSpeed) {
            return;
        }
        
        this.playbackState.speed = validSpeed;
        
        // Update UI
        if (this.speedSelector) {
            this.speedSelector.value = validSpeed;
        }
        
        // Restart timer if currently playing
        if (this.playbackState.isPlaying) {
            this.restartPlaybackTimer();
        }
        
        // Save state
        this.savePlaybackState();
    }
    
    /**
     * Restart playback timer with current speed
     */
    restartPlaybackTimer() {
        if (this.playbackState.timer) {
            clearInterval(this.playbackState.timer);
        }
        this.playbackState.timer = setInterval(() => {
            this.autoAdvance();
        }, this.playbackState.speed);
    }

    /**
     * Automatically advance to next alignment
     */
    async autoAdvance() {
        if (this.currentIndex >= this.totalAlignments - 1) {
            // Reached the end, pause playback
            this.pauseAutoPlay();
            return;
        }
        
        // Move to next alignment
        await this.nextAlignment();
    }
    
    /**
     * Update playback control UI elements
     */
    updatePlaybackUI() {
        if (this.btnPlayPause) {
            const icon = this.btnPlayPause.querySelector('i');
            const text = this.btnPlayPause.querySelector('.btn-text');
            
            if (this.playbackState.isPlaying) {
                if (icon) icon.className = 'fas fa-pause';
                if (text) text.textContent = 'Pause';
                this.btnPlayPause.classList.remove('btn-success');
                this.btnPlayPause.classList.add('btn-warning');
                
                // Show playback indicator on current alignment
                this.dualDisplay.showPlaybackIndicator(true);
            } else {
                if (icon) icon.className = 'fas fa-play';
                if (text) text.textContent = 'Play';
                this.btnPlayPause.classList.remove('btn-warning');
                this.btnPlayPause.classList.add('btn-success');
                
                // Hide playback indicator
                this.dualDisplay.showPlaybackIndicator(false);
            }
        }
        
        // Update progress time estimate
        this.updateTimeEstimate();
        
        // Update navigation button states to show boundary conditions
        this.updateNavigationButtons();
    }
    
    /**
     * Save playback state to localStorage
     */
    savePlaybackState() {
        if (typeof storageHelper !== 'undefined') {
            const sessionData = {
                currentIndex: this.currentIndex,
                isPlaying: this.playbackState.isPlaying,
                playbackSpeed: this.playbackState.speed,
                lastUpdated: Date.now()
            };
            
            storageHelper.savePlaybackSession(this.subLinkId, sessionData);
            
            // Also save preferences
            const preferences = {
                isAutoPlaying: this.playbackState.isPlaying,
                playbackSpeed: this.playbackState.speed,
                lastPlaybackState: this.playbackState.isPlaying ? 'playing' : 'paused',
                preferredSpeed: storageHelper.getPreferenceFromSpeed(this.playbackState.speed)
            };
            
            storageHelper.savePlaybackPreferences(preferences);
        }
    }
    
    /**
     * Restore playback state from localStorage
     */
    restorePlaybackState() {
        if (typeof storageHelper === 'undefined') {
            return;
        }
        
        // Load session data
        const sessionData = storageHelper.loadPlaybackSession(this.subLinkId);
        if (sessionData && sessionData.lastUpdated) {
            // Only restore if session is recent (within 24 hours)
            const timeDiff = Date.now() - sessionData.lastUpdated;
            if (timeDiff < 24 * 60 * 60 * 1000) {
                this.playbackState.speed = sessionData.playbackSpeed || 3000;
                
                // Update speed selector
                if (this.speedSelector) {
                    this.speedSelector.value = this.playbackState.speed;
                }
            }
        }
        
        // Load general preferences
        const preferences = storageHelper.loadPlaybackPreferences();
        if (preferences) {
            this.playbackState.speed = preferences.playbackSpeed || 3000;
            
            // Update UI
            if (this.speedSelector) {
                this.speedSelector.value = this.playbackState.speed;
            }
        }
        
        // Update UI state
        this.updatePlaybackUI();
    }
    
    /**
     * Jump to beginning of subtitle file
     */
    async jumpToBeginning() {
        if (this.playbackState.isPlaying) {
            this.pauseAutoPlay();
        }
        await this.jumpToAlignment(0);
    }
    
    /**
     * Jump to end of subtitle file
     */
    async jumpToEnd() {
        if (this.playbackState.isPlaying) {
            this.pauseAutoPlay();
        }
        await this.jumpToAlignment(this.totalAlignments - 1);
    }
    
    /**
     * Clean up resources
     */
    destroy() {
        // Pause playback and clear timers
        this.pauseAutoPlay();
        
        // End progress tracking session
        if (this.progressTracker) {
            this.progressTracker.endSession();
        } else {
            // Fallback to legacy progress saving
            this.saveProgress();
        }
        
        this.savePlaybackState();
        
        // Clean up event listeners if needed
        // This would be called when navigating away from the page
    }
}