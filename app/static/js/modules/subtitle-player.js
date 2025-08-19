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
        
        // Initialize components
        this.dualDisplay = new DualSubtitleDisplay();
        
        // UI elements
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.btnPrev = document.getElementById('btn-prev');
        this.btnNext = document.getElementById('btn-next');
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
        
        // Progress tracking - update every 5 alignments or 30 seconds
        this.progressUpdateCounter = 0;
        this.lastProgressUpdate = Date.now();
        
        // Auto-save progress periodically
        setInterval(() => {
            this.autoSaveProgress();
        }, 30000); // 30 seconds
    }
    
    /**
     * Initialize the subtitle player by loading user progress and alignment data
     */
    async initialize() {
        try {
            this.showLoading(true);
            
            // Load user progress first
            const progress = await this.loadUserProgress();
            if (progress && progress.current_alignment_index) {
                this.currentIndex = progress.current_alignment_index;
            }
            
            // Load initial batch of alignment data
            await this.loadAlignmentData(this.currentIndex);
            
            // Set up the display
            this.updateDisplay();
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
            const url = `/api/subtitles/${this.subLinkId}?start_index=${startIndex}&limit=${this.batchSize}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Store alignment data and subtitle lines
            this.alignmentData = data.alignments || [];
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
        this.dualDisplay.highlightAlignment(relativeIndex);
        
        // Update progress display
        this.updateProgressDisplay();
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    /**
     * Update progress bar and text
     */
    updateProgressDisplay() {
        if (this.progressBar && this.progressText) {
            const progress = this.totalAlignments > 0 ? (this.currentIndex / this.totalAlignments) * 100 : 0;
            this.progressBar.style.width = `${progress}%`;
            this.progressBar.setAttribute('aria-valuenow', progress);
            this.progressText.textContent = `${this.currentIndex + 1} / ${this.totalAlignments}`;
        }
    }
    
    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        if (this.btnPrev) {
            this.btnPrev.disabled = this.currentIndex <= 0;
        }
        
        if (this.btnNext) {
            this.btnNext.disabled = this.currentIndex >= this.totalAlignments - 1;
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
            this.dualDisplay.highlightAlignment(relativeIndex);
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
            this.dualDisplay.highlightAlignment(relativeIndex);
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
        
        // Track progress updates
        this.progressUpdateCounter++;
        if (this.progressUpdateCounter >= 5 || Date.now() - this.lastProgressUpdate > 30000) {
            this.saveProgress();
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
            this.dualDisplay.highlightAlignment(relativeIndex);
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
     * Clean up resources
     */
    destroy() {
        // Save final progress
        this.saveProgress();
        
        // Clean up event listeners if needed
        // This would be called when navigating away from the page
    }
}