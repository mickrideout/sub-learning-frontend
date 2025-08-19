/**
 * Progress Indicator Component for Visual Progress Feedback
 * Displays completion percentage, milestone achievements, and progress statistics
 */

class ProgressIndicator {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            showPercentage: true,
            showMilestones: true,
            showStats: true,
            animateProgress: true,
            milestones: [25, 50, 75, 100],
            ...options
        };
        
        this.currentProgress = 0;
        this.totalAlignments = 0;
        this.currentIndex = 0;
        
        this.init();
    }
    
    /**
     * Initialize the progress indicator
     */
    init() {
        if (!this.container) {
            console.error('ProgressIndicator: Container not found');
            return;
        }
        
        this.render();
        this.bindEvents();
        
        console.log('ProgressIndicator initialized');
    }
    
    /**
     * Render the progress indicator HTML
     */
    render() {
        this.container.innerHTML = `
            <div class="progress-indicator">
                <div class="progress-header">
                    <h4 class="progress-title">Learning Progress</h4>
                    ${this.options.showPercentage ? '<span class="progress-percentage">0%</span>' : ''}
                </div>
                
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                        ${this.renderMilestones()}
                    </div>
                </div>
                
                ${this.options.showStats ? this.renderStats() : ''}
                
                <div class="progress-achievements hidden">
                    <div class="achievement-message"></div>
                </div>
            </div>
        `;
        
        this.cacheElements();
        this.addStyles();
    }
    
    /**
     * Render milestone markers
     */
    renderMilestones() {
        if (!this.options.showMilestones) return '';
        
        return this.options.milestones.map(milestone => `
            <div class="milestone-marker" data-milestone="${milestone}" style="left: ${milestone}%">
                <div class="milestone-dot"></div>
                <div class="milestone-label">${milestone}%</div>
            </div>
        `).join('');
    }
    
    /**
     * Render statistics section
     */
    renderStats() {
        return `
            <div class="progress-stats">
                <div class="stat-item">
                    <span class="stat-label">Current Position:</span>
                    <span class="stat-value current-position">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Alignments:</span>
                    <span class="stat-value total-alignments">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Completed:</span>
                    <span class="stat-value completed-count">0</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        this.elements = {
            percentage: this.container.querySelector('.progress-percentage'),
            progressFill: this.container.querySelector('.progress-fill'),
            milestones: this.container.querySelectorAll('.milestone-marker'),
            achievements: this.container.querySelector('.progress-achievements'),
            achievementMessage: this.container.querySelector('.achievement-message'),
            currentPosition: this.container.querySelector('.current-position'),
            totalAlignments: this.container.querySelector('.total-alignments'),
            completedCount: this.container.querySelector('.completed-count')
        };
    }
    
    /**
     * Update progress display
     * @param {Object} progressData - Progress data from tracker
     */
    updateProgress(progressData) {
        const {
            current_alignment_index = 0,
            total_alignments = 0,
            completion_percentage = 0,
            total_alignments_completed = 0
        } = progressData;
        
        const previousProgress = this.currentProgress;
        this.currentProgress = completion_percentage;
        this.totalAlignments = total_alignments;
        this.currentIndex = current_alignment_index;
        
        // Update percentage display
        if (this.elements.percentage) {
            this.elements.percentage.textContent = `${Math.round(completion_percentage)}%`;
        }
        
        // Update progress bar
        if (this.elements.progressFill) {
            if (this.options.animateProgress) {
                this.animateProgressBar(this.currentProgress);
            } else {
                this.elements.progressFill.style.width = `${this.currentProgress}%`;
            }
        }
        
        // Update statistics
        this.updateStats(current_alignment_index, total_alignments, total_alignments_completed);
        
        // Check for milestone achievements
        this.checkMilestoneAchievements(previousProgress, this.currentProgress);
        
        // Update milestone markers
        this.updateMilestoneMarkers();
        
        console.log(`Progress updated: ${this.currentProgress}%`);
    }
    
    /**
     * Animate progress bar to new value
     * @param {number} targetProgress - Target progress percentage
     */
    animateProgressBar(targetProgress) {
        if (!this.elements.progressFill) return;
        
        const currentWidth = parseFloat(this.elements.progressFill.style.width) || 0;
        const duration = Math.abs(targetProgress - currentWidth) * 10; // 10ms per percentage point
        
        this.elements.progressFill.style.transition = `width ${Math.min(duration, 1000)}ms ease-out`;
        this.elements.progressFill.style.width = `${targetProgress}%`;
    }
    
    /**
     * Update statistics display
     */
    updateStats(currentPosition, totalAlignments, completedCount) {
        if (this.elements.currentPosition) {
            this.elements.currentPosition.textContent = currentPosition.toLocaleString();
        }
        if (this.elements.totalAlignments) {
            this.elements.totalAlignments.textContent = totalAlignments.toLocaleString();
        }
        if (this.elements.completedCount) {
            this.elements.completedCount.textContent = completedCount.toLocaleString();
        }
    }
    
    /**
     * Check for milestone achievements
     */
    checkMilestoneAchievements(previousProgress, currentProgress) {
        if (!this.options.showMilestones) return;
        
        const newMilestones = this.options.milestones.filter(milestone => 
            previousProgress < milestone && currentProgress >= milestone
        );
        
        newMilestones.forEach(milestone => {
            this.showAchievement(`🎉 ${milestone}% Complete!`, milestone);
        });
        
        // Special achievement for 100% completion
        if (previousProgress < 100 && currentProgress >= 100) {
            this.showAchievement('🏆 Congratulations! You completed this subtitle!', 100);
        }
    }
    
    /**
     * Show achievement notification
     * @param {string} message - Achievement message
     * @param {number} milestone - Milestone percentage
     */
    showAchievement(message, milestone) {
        if (!this.elements.achievements || !this.elements.achievementMessage) return;
        
        this.elements.achievementMessage.textContent = message;
        this.elements.achievements.classList.remove('hidden');
        this.elements.achievements.classList.add('show');
        
        // Hide after 3 seconds
        setTimeout(() => {
            this.elements.achievements.classList.remove('show');
            this.elements.achievements.classList.add('hidden');
        }, 3000);
        
        // Dispatch achievement event
        const event = new CustomEvent('milestone-achieved', {
            detail: { milestone, message }
        });
        document.dispatchEvent(event);
        
        console.log(`Achievement unlocked: ${message}`);
    }
    
    /**
     * Update milestone marker states
     */
    updateMilestoneMarkers() {
        this.elements.milestones.forEach(marker => {
            const milestone = parseInt(marker.dataset.milestone);
            if (this.currentProgress >= milestone) {
                marker.classList.add('achieved');
            } else {
                marker.classList.remove('achieved');
            }
        });
    }
    
    /**
     * Reset progress to zero
     */
    resetProgress() {
        this.updateProgress({
            current_alignment_index: 0,
            total_alignments: 0,
            completion_percentage: 0,
            total_alignments_completed: 0
        });
    }
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        // Listen for progress updates from tracker
        document.addEventListener('progress-updated', (event) => {
            if (event.detail) {
                this.updateProgress({
                    current_alignment_index: event.detail.current_index,
                    completion_percentage: event.detail.completion_percentage
                });
            }
        });
        
        // Listen for session end
        document.addEventListener('session-ended', () => {
            this.resetProgress();
        });
    }
    
    /**
     * Add CSS styles for the progress indicator
     */
    addStyles() {
        if (document.querySelector('#progress-indicator-styles')) return;
        
        const styles = `
            <style id="progress-indicator-styles">
                .progress-indicator {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 16px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .progress-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                
                .progress-title {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                    color: #333;
                }
                
                .progress-percentage {
                    font-size: 18px;
                    font-weight: bold;
                    color: #007bff;
                }
                
                .progress-bar-container {
                    position: relative;
                    margin-bottom: 16px;
                }
                
                .progress-bar {
                    width: 100%;
                    height: 12px;
                    background-color: #e9ecef;
                    border-radius: 6px;
                    overflow: hidden;
                    position: relative;
                }
                
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #007bff, #28a745);
                    transition: width 300ms ease-out;
                }
                
                .milestone-marker {
                    position: absolute;
                    top: -8px;
                    transform: translateX(-50%);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                
                .milestone-dot {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #6c757d;
                    border: 2px solid white;
                    transition: all 300ms ease;
                }
                
                .milestone-marker.achieved .milestone-dot {
                    background: #28a745;
                    transform: scale(1.2);
                }
                
                .milestone-label {
                    font-size: 10px;
                    color: #6c757d;
                    margin-top: 4px;
                    white-space: nowrap;
                }
                
                .milestone-marker.achieved .milestone-label {
                    color: #28a745;
                    font-weight: bold;
                }
                
                .progress-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 12px;
                    margin-top: 12px;
                }
                
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px;
                    background: white;
                    border-radius: 4px;
                    border: 1px solid #dee2e6;
                }
                
                .stat-label {
                    font-size: 12px;
                    color: #6c757d;
                }
                
                .stat-value {
                    font-weight: bold;
                    color: #333;
                }
                
                .progress-achievements {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 6px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    z-index: 1000;
                    transform: translateX(100%);
                    transition: transform 300ms ease;
                }
                
                .progress-achievements.show {
                    transform: translateX(0);
                }
                
                .progress-achievements.hidden {
                    display: none;
                }
                
                .achievement-message {
                    font-weight: bold;
                    font-size: 14px;
                }
                
                @media (max-width: 768px) {
                    .progress-indicator {
                        padding: 12px;
                        margin: 8px 0;
                    }
                    
                    .progress-stats {
                        grid-template-columns: 1fr;
                    }
                    
                    .progress-achievements {
                        left: 10px;
                        right: 10px;
                        top: 10px;
                        transform: translateY(-100%);
                    }
                    
                    .progress-achievements.show {
                        transform: translateY(0);
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    /**
     * Destroy the progress indicator
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        document.removeEventListener('progress-updated', this.boundProgressHandler);
        document.removeEventListener('session-ended', this.boundSessionEndHandler);
    }
}

export default ProgressIndicator;