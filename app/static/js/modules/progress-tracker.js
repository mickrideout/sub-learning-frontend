/**
 * Progress Tracker Module for User Learning Progress Management
 * Handles automatic progress saving, session tracking, and offline queue management
 */

import { StorageHelper } from '../utils/storage-helper.js';

class ProgressTracker {
    constructor() {
        this.currentProgress = null;
        this.sessionStartTime = null;
        this.lastSaveTime = null;
        this.saveInterval = 5; // Save every 5 alignment advances
        this.offlineQueue = [];
        this.isOnline = navigator.onLine;
        this.retryTimeout = null;
        this.maxRetries = 3;
        
        // Bind event handlers
        this.handleOnline = this.handleOnline.bind(this);
        this.handleOffline = this.handleOffline.bind(this);
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
        
        this.initialize();
    }
    
    /**
     * Initialize the progress tracker with event listeners
     */
    initialize() {
        // Network status monitoring
        window.addEventListener('online', this.handleOnline);
        window.addEventListener('offline', this.handleOffline);
        
        // Save progress before page unload
        window.addEventListener('beforeunload', this.handleBeforeUnload);
        
        // Load offline queue from storage
        this.loadOfflineQueue();
        
        console.log('ProgressTracker initialized');
    }
    
    /**
     * Start a new learning session
     * @param {number} subLinkId - ID of the subtitle link
     */
    async startSession(subLinkId) {
        try {
            this.sessionStartTime = new Date();
            this.currentProgress = {
                sub_link_id: subLinkId,
                current_alignment_index: 0,
                session_duration_minutes: 0,
                unsaved_changes: false
            };
            
            // Try to restore existing progress from server
            await this.restoreProgress(subLinkId);
            
            console.log(`Learning session started for SubLink ${subLinkId}`);
            return this.currentProgress;
            
        } catch (error) {
            console.error('Error starting session:', error);
            // Continue with default progress if restoration fails
            return this.currentProgress;
        }
    }
    
    /**
     * Restore user progress from server
     * @param {number} subLinkId - ID of the subtitle link
     */
    async restoreProgress(subLinkId) {
        try {
            const response = await fetch(`/api/progress/${subLinkId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.currentProgress = {
                    ...this.currentProgress,
                    current_alignment_index: data.progress.current_alignment_index,
                    total_alignments_completed: data.progress.total_alignments_completed,
                    completion_percentage: data.progress.completion_percentage,
                    total_alignments: data.progress.total_alignments
                };
                console.log('Progress restored from server:', this.currentProgress);
            } else if (response.status === 404) {
                // No existing progress - starting fresh
                console.log('No existing progress found - starting fresh session');
            } else {
                throw new Error(`Server error: ${response.status}`);
            }
            
        } catch (error) {
            console.warn('Could not restore progress from server:', error);
            // Continue with local progress if server is unavailable
        }
    }
    
    /**
     * Update progress position
     * @param {number} alignmentIndex - Current alignment position
     * @param {boolean} force - Force immediate save regardless of interval
     */
    updateProgress(alignmentIndex, force = false) {
        if (!this.currentProgress) {
            console.warn('No active session - cannot update progress');
            return;
        }
        
        const previousIndex = this.currentProgress.current_alignment_index;
        this.currentProgress.current_alignment_index = alignmentIndex;
        this.currentProgress.unsaved_changes = true;
        
        // Update session duration
        this.updateSessionDuration();
        
        // Check if we should auto-save
        const indexDifference = Math.abs(alignmentIndex - (this.lastSaveTime || 0));
        if (force || indexDifference >= this.saveInterval) {
            this.saveProgress();
        }
        
        // Dispatch progress update event
        this.dispatchProgressEvent('progress-updated', {
            current_index: alignmentIndex,
            previous_index: previousIndex,
            completion_percentage: this.calculateCompletionPercentage()
        });
    }
    
    /**
     * Save progress to server (with offline queue fallback)
     */
    async saveProgress() {
        if (!this.currentProgress || !this.currentProgress.unsaved_changes) {
            return;
        }
        
        try {
            const progressData = {
                current_alignment_index: this.currentProgress.current_alignment_index,
                session_duration_minutes: this.currentProgress.session_duration_minutes
            };
            
            if (this.isOnline) {
                await this.saveToServer(progressData);
                this.lastSaveTime = this.currentProgress.current_alignment_index;
                this.currentProgress.unsaved_changes = false;
            } else {
                // Queue for offline saving
                this.queueForOfflineSave(progressData);
            }
            
        } catch (error) {
            console.error('Error saving progress:', error);
            // Queue for retry if save fails
            this.queueForOfflineSave({
                current_alignment_index: this.currentProgress.current_alignment_index,
                session_duration_minutes: this.currentProgress.session_duration_minutes
            });
        }
    }
    
    /**
     * Save progress data to server
     * @param {Object} progressData - Progress data to save
     */
    async saveToServer(progressData) {
        const response = await fetch(`/api/progress/${this.currentProgress.sub_link_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(progressData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Update local progress with server response
        if (result.progress) {
            this.currentProgress.completion_percentage = result.progress.completion_percentage;
            this.currentProgress.total_alignments = result.progress.total_alignments;
            this.currentProgress.total_alignments_completed = result.progress.total_alignments_completed;
        }
        
        console.log('Progress saved to server:', result);
    }
    
    /**
     * Queue progress data for offline saving
     * @param {Object} progressData - Progress data to queue
     */
    queueForOfflineSave(progressData) {
        const queueItem = {
            sub_link_id: this.currentProgress.sub_link_id,
            data: progressData,
            timestamp: new Date().toISOString(),
            retry_count: 0
        };
        
        this.offlineQueue.push(queueItem);
        this.saveOfflineQueue();
        
        console.log('Progress queued for offline save:', queueItem);
    }
    
    /**
     * Process offline queue when connection is restored
     */
    async processOfflineQueue() {
        if (!this.isOnline || this.offlineQueue.length === 0) {
            return;
        }
        
        console.log(`Processing ${this.offlineQueue.length} queued progress updates`);
        
        const itemsToRemove = [];
        
        for (const item of this.offlineQueue) {
            try {
                const response = await fetch(`/api/progress/${item.sub_link_id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(item.data)
                });
                
                if (response.ok) {
                    itemsToRemove.push(item);
                    console.log('Queued progress successfully saved:', item);
                } else {
                    item.retry_count++;
                    if (item.retry_count >= this.maxRetries) {
                        itemsToRemove.push(item);
                        console.warn('Max retries reached, removing item:', item);
                    }
                }
                
            } catch (error) {
                console.error('Error processing queued item:', error);
                item.retry_count++;
                if (item.retry_count >= this.maxRetries) {
                    itemsToRemove.push(item);
                }
            }
        }
        
        // Remove successfully saved or max-retry items
        this.offlineQueue = this.offlineQueue.filter(item => !itemsToRemove.includes(item));
        this.saveOfflineQueue();
    }
    
    /**
     * Update session duration based on elapsed time
     */
    updateSessionDuration() {
        if (this.sessionStartTime && this.currentProgress) {
            const elapsed = new Date() - this.sessionStartTime;
            this.currentProgress.session_duration_minutes = Math.floor(elapsed / (1000 * 60));
        }
    }
    
    /**
     * Calculate completion percentage
     */
    calculateCompletionPercentage() {
        if (!this.currentProgress || !this.currentProgress.total_alignments) {
            return 0;
        }
        
        const percentage = (this.currentProgress.current_alignment_index / this.currentProgress.total_alignments) * 100;
        return Math.min(100, Math.max(0, Math.round(percentage * 100) / 100));
    }
    
    /**
     * Get current progress data
     */
    getCurrentProgress() {
        if (!this.currentProgress) {
            return null;
        }
        
        return {
            ...this.currentProgress,
            completion_percentage: this.calculateCompletionPercentage()
        };
    }
    
    /**
     * End the current learning session
     */
    async endSession() {
        if (this.currentProgress) {
            // Final save before ending session
            await this.saveProgress();
            
            // Dispatch session end event
            this.dispatchProgressEvent('session-ended', {
                session_duration: this.currentProgress.session_duration_minutes,
                final_index: this.currentProgress.current_alignment_index
            });
            
            console.log('Learning session ended');
        }
        
        this.currentProgress = null;
        this.sessionStartTime = null;
        this.lastSaveTime = null;
    }
    
    /**
     * Handle online event
     */
    handleOnline() {
        this.isOnline = true;
        console.log('Connection restored - processing offline queue');
        this.processOfflineQueue();
    }
    
    /**
     * Handle offline event
     */
    handleOffline() {
        this.isOnline = false;
        console.log('Connection lost - enabling offline mode');
    }
    
    /**
     * Handle before unload event
     */
    handleBeforeUnload(event) {
        if (this.currentProgress && this.currentProgress.unsaved_changes) {
            // Force save before page unload
            this.saveProgress();
            
            // Show warning for unsaved changes
            const message = 'You have unsaved progress. Are you sure you want to leave?';
            event.returnValue = message;
            return message;
        }
    }
    
    /**
     * Load offline queue from storage
     */
    loadOfflineQueue() {
        try {
            const saved = StorageHelper.get('progress_offline_queue');
            if (saved && Array.isArray(saved)) {
                this.offlineQueue = saved;
                console.log(`Loaded ${this.offlineQueue.length} queued progress items`);
            }
        } catch (error) {
            console.warn('Could not load offline queue:', error);
            this.offlineQueue = [];
        }
    }
    
    /**
     * Save offline queue to storage
     */
    saveOfflineQueue() {
        try {
            StorageHelper.set('progress_offline_queue', this.offlineQueue);
        } catch (error) {
            console.error('Could not save offline queue:', error);
        }
    }
    
    /**
     * Dispatch custom progress events
     * @param {string} eventType - Type of event
     * @param {Object} detail - Event detail data
     */
    dispatchProgressEvent(eventType, detail) {
        const event = new CustomEvent(eventType, { detail });
        document.dispatchEvent(event);
    }
    
    /**
     * Clean up event listeners
     */
    destroy() {
        window.removeEventListener('online', this.handleOnline);
        window.removeEventListener('offline', this.handleOffline);
        window.removeEventListener('beforeunload', this.handleBeforeUnload);
        
        if (this.retryTimeout) {
            clearTimeout(this.retryTimeout);
        }
        
        console.log('ProgressTracker destroyed');
    }
}

// Export singleton instance
export const progressTracker = new ProgressTracker();
export default progressTracker;