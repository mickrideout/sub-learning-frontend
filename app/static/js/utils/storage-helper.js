/**
 * Storage Helper Utility
 * Handles localStorage operations for playback preferences and session state
 */
class StorageHelper {
    constructor() {
        this.keyPrefix = 'learning_';
    }

    /**
     * Save playback preferences to localStorage
     */
    savePlaybackPreferences(preferences) {
        try {
            const validPreferences = this.validatePlaybackPreferences(preferences);
            if (!validPreferences) {
                console.warn('Invalid playback preferences:', preferences);
                return false;
            }
            
            localStorage.setItem(
                `${this.keyPrefix}playbackPreferences`, 
                JSON.stringify(validPreferences)
            );
            return true;
        } catch (error) {
            console.error('Failed to save playback preferences:', error);
            return false;
        }
    }

    /**
     * Load playback preferences from localStorage
     */
    loadPlaybackPreferences() {
        try {
            const stored = localStorage.getItem(`${this.keyPrefix}playbackPreferences`);
            if (!stored) {
                return this.getDefaultPlaybackPreferences();
            }

            const preferences = JSON.parse(stored);
            return this.validatePlaybackPreferences(preferences) || this.getDefaultPlaybackPreferences();
        } catch (error) {
            console.warn('Failed to load playback preferences, using defaults:', error);
            return this.getDefaultPlaybackPreferences();
        }
    }

    /**
     * Get default playback preferences
     */
    getDefaultPlaybackPreferences() {
        return {
            isAutoPlaying: false,
            playbackSpeed: 3000, // 3 seconds in milliseconds
            lastPlaybackState: 'paused',
            preferredSpeed: 'normal'
        };
    }

    /**
     * Validate playback preferences structure
     */
    validatePlaybackPreferences(preferences) {
        if (!preferences || typeof preferences !== 'object') {
            return null;
        }

        const validSpeeds = ['slow', 'normal', 'fast'];
        const validStates = ['playing', 'paused'];

        // Validate and sanitize each field
        const validated = {
            isAutoPlaying: Boolean(preferences.isAutoPlaying),
            playbackSpeed: this.validateSpeed(preferences.playbackSpeed),
            lastPlaybackState: validStates.includes(preferences.lastPlaybackState) 
                ? preferences.lastPlaybackState 
                : 'paused',
            preferredSpeed: validSpeeds.includes(preferences.preferredSpeed) 
                ? preferences.preferredSpeed 
                : 'normal'
        };

        return validated;
    }

    /**
     * Validate playback speed value
     */
    validateSpeed(speed) {
        const numSpeed = Number(speed);
        
        // Valid range: 1000ms (1 second) to 5000ms (5 seconds)
        if (isNaN(numSpeed) || numSpeed < 1000 || numSpeed > 5000) {
            return 3000; // Default to 3 seconds
        }
        
        return Math.round(numSpeed);
    }

    /**
     * Save current playback session state
     */
    savePlaybackSession(subLinkId, sessionData) {
        try {
            const validatedSession = this.validateSessionData(sessionData);
            if (!validatedSession) {
                console.warn('Invalid session data:', sessionData);
                return false;
            }

            const key = `${this.keyPrefix}session_${subLinkId}`;
            localStorage.setItem(key, JSON.stringify(validatedSession));
            return true;
        } catch (error) {
            console.error('Failed to save playback session:', error);
            return false;
        }
    }

    /**
     * Load playback session state
     */
    loadPlaybackSession(subLinkId) {
        try {
            const key = `${this.keyPrefix}session_${subLinkId}`;
            const stored = localStorage.getItem(key);
            
            if (!stored) {
                return null;
            }

            const sessionData = JSON.parse(stored);
            return this.validateSessionData(sessionData);
        } catch (error) {
            console.warn('Failed to load playback session:', error);
            return null;
        }
    }

    /**
     * Validate session data structure
     */
    validateSessionData(sessionData) {
        if (!sessionData || typeof sessionData !== 'object') {
            return null;
        }

        return {
            currentIndex: Math.max(0, parseInt(sessionData.currentIndex) || 0),
            isPlaying: Boolean(sessionData.isPlaying),
            playbackSpeed: this.validateSpeed(sessionData.playbackSpeed),
            lastUpdated: sessionData.lastUpdated || Date.now()
        };
    }

    /**
     * Clear playback session for specific subtitle link
     */
    clearPlaybackSession(subLinkId) {
        try {
            const key = `${this.keyPrefix}session_${subLinkId}`;
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to clear playback session:', error);
            return false;
        }
    }

    /**
     * Save general user preference
     */
    savePreference(key, value) {
        try {
            if (!key || typeof key !== 'string') {
                console.warn('Invalid preference key:', key);
                return false;
            }

            if (value === null || value === undefined) {
                console.warn('Invalid preference value for key:', key);
                return false;
            }

            localStorage.setItem(`${this.keyPrefix}${key}`, String(value));
            return true;
        } catch (error) {
            console.warn('Failed to save preference:', error);
            return false;
        }
    }

    /**
     * Load general user preference
     */
    loadPreference(key, defaultValue) {
        try {
            const value = localStorage.getItem(`${this.keyPrefix}${key}`);
            return value !== null ? value : defaultValue;
        } catch (error) {
            console.warn('Failed to load preference:', error);
            return defaultValue;
        }
    }

    /**
     * Get playback speed in milliseconds from preference string
     */
    getSpeedFromPreference(speedPreference) {
        switch (speedPreference) {
            case 'slow':
                return 5000; // 5 seconds
            case 'normal':
                return 3000; // 3 seconds
            case 'fast':
                return 1000; // 1 second
            default:
                return 3000; // Default to normal
        }
    }

    /**
     * Get speed preference from milliseconds
     */
    getPreferenceFromSpeed(milliseconds) {
        switch (milliseconds) {
            case 1000:
                return 'fast';
            case 3000:
                return 'normal';
            case 5000:
                return 'slow';
            default:
                return 'normal';
        }
    }

    /**
     * Check if localStorage is available and functional
     */
    isStorageAvailable() {
        try {
            const testKey = `${this.keyPrefix}test`;
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Clear all learning-related localStorage data
     */
    clearAllData() {
        try {
            // Use a more efficient approach to clear prefixed keys
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith(this.keyPrefix)) {
                    keysToRemove.push(key);
                }
            }
            
            keysToRemove.forEach(key => {
                localStorage.removeItem(key);
            });
            return true;
        } catch (error) {
            console.error('Failed to clear all data:', error);
            return false;
        }
    }
}

// Create and export singleton instance
const storageHelper = new StorageHelper();